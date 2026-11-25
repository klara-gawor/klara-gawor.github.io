"""Append public ORCID journal articles to the al-folio bibliography."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase, UndefinedString
from bibtexparser.bparser import BibTexParser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.customization import convert_to_unicode
from pyparsing import ParseBaseException

ORCID = "0000-0001-7571-5420"
BIB_PATH = Path(__file__).resolve().parents[1] / "_bibliography" / "papers.bib"
WORK_TYPES = {"journal-article"}
EXCLUDED_DOIS = set()  # Add lowercase DOIs here to prevent their automatic import.
USER_AGENT = "AcademicPublicationSync/1.0 (https://klara-gawor.github.io/)"
DEMO_KEYS = {"einstein1920relativity", "einstein1956investigations", "PhysRev.47.777"}


def fetch(url, accept):
    """Retrieve public metadata, retrying temporary network and service errors."""
    request = Request(url, headers={"Accept": accept, "User-Agent": USER_AGENT})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                return response.read().decode("utf-8")
        except HTTPError as error:
            if error.code not in {429, 500, 502, 503, 504} or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** (attempt + 1))


def normalize_doi(value):
    """Return a lowercase DOI without its resolver prefix."""
    value = (value or "").strip().lower()
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value)
    return value if re.fullmatch(r"10\.\d{4,9}/\S+", value) else ""


def normalize_title(value):
    """Normalize titles for duplicate detection across punctuation and accents."""
    value = convert_to_unicode({"title": value or ""})["title"]
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in value if char.isalnum())


def parse_bibtex(text):
    """Parse bibliography entries without changing the original file."""
    text = re.sub(r"\A---\s*\n---\s*\n?", "", text, count=1)
    parser = BibTexParser(ignore_nonstandard_types=False, common_strings=True)
    # Some DOI providers use full, unquoted month names instead of BibTeX abbreviations.
    months = (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    )
    parser.bib_database.strings.update({month.lower(): month for month in months})
    parser.bib_database.strings["sept"] = "September"
    return bibtexparser.loads(text, parser=parser).entries


def get_orcid_works():
    """Collect self-identified DOIs for public journal articles in ORCID."""
    url = f"https://pub.orcid.org/v3.0/{ORCID}/works"
    record = json.loads(fetch(url, "application/vnd.orcid+json"))
    groups = record.get("group")
    if not isinstance(groups, list):
        raise ValueError("ORCID did not return a valid works list.")

    works = {}
    for group in groups:
        for summary in group.get("work-summary", []):
            if summary.get("type") not in WORK_TYPES:
                continue
            title = ((summary.get("title") or {}).get("title") or {}).get("value", "")
            identifiers = (summary.get("external-ids") or {}).get("external-id", [])
            for identifier in identifiers:
                if identifier.get("external-id-type", "").lower() != "doi":
                    continue
                if identifier.get("external-id-relationship") != "self":
                    continue
                doi = normalize_doi(identifier.get("external-id-value"))
                if doi and doi not in EXCLUDED_DOIS:
                    works.setdefault(doi, title)
    return works


def get_bibtex(doi):
    """Resolve a DOI to a complete journal article citation."""
    url = f"https://doi.org/{quote(doi, safe='/')}"
    try:
        text = fetch(url, "application/x-bibtex")
    except HTTPError as error:
        if error.code in {404, 406}:
            print(f"WARNING: DOI metadata unavailable for {doi} ({error.code}).")
            return None
        raise

    print(f"Reading DOI: {doi}", flush=True)
    try:
        entries = parse_bibtex(text)
    except (UndefinedString, ParseBaseException) as error:
        print(f"::warning::Could not parse DOI {doi}: {error}. Skipped; retry on next run.")
        return None

    if len(entries) != 1:
        print(f"WARNING: Unexpected BibTeX response for {doi}; skipped.")
        return None
    entry = entries[0]
    if entry["ENTRYTYPE"].lower() != "article":
        print(f"Skipping non-journal citation: {doi}")
        return None
    if not all(entry.get(field) for field in ("author", "title", "year", "journal")):
        print(f"WARNING: Incomplete citation for {doi}; skipped.")
        return None

    resolved_doi = normalize_doi(entry.get("doi"))
    if resolved_doi and resolved_doi != doi:
        print(f"WARNING: DOI mismatch for {doi}; skipped.")
        return None
    entry["doi"] = doi
    entry["html"] = f"https://doi.org/{quote(doi, safe='/')}"
    entry["bibtex_show"] = "true"
    entry.pop("abstract", None)
    return entry


def unique_key(entry, used_keys):
    """Generate a stable citation key without overwriting existing entries."""
    digest = hashlib.sha256(entry["doi"].encode()).hexdigest()[:12]
    year = re.sub(r"\D", "", entry["year"])[:4]
    base = f"gawor{year}_{digest}"
    key = base
    counter = 2
    while key in used_keys:
        key = f"{base}_{counter}"
        counter += 1
    return key


def sync(path, dry_run=False):
    """Append only missing citations, preserving all manually edited entries."""
    original = path.read_text(encoding="utf-8")
    existing = parse_bibtex(original)
    used_keys = {entry["ID"] for entry in existing}
    if used_keys & DEMO_KEYS:
        raise ValueError("Remove the al-folio demonstration bibliography before syncing.")
    if re.search(r"(?im)^\s*@(?:article|book|inproceedings)\s*[{(]", original) and not existing:
        raise ValueError("Existing bibliography could not be parsed; no changes made.")

    seen_dois = {normalize_doi(entry.get("doi")) for entry in existing} - {""}
    # Match titles as well, including manually added accepted papers without DOIs.
    seen_titles = {normalize_title(entry.get("title")) for entry in existing} - {""}
    works = get_orcid_works()
    if not works:
        print("WARNING: No public journal articles with DOIs found in ORCID.")

    additions = []
    skipped = []
    for doi, orcid_title in sorted(works.items()):
        if doi in seen_dois or normalize_title(orcid_title) in seen_titles:
            continue
        entry = get_bibtex(doi)
        if entry is None:
            skipped.append(doi)
            continue
        title = normalize_title(entry["title"])
        if title in seen_titles:
            continue
        entry["ID"] = unique_key(entry, used_keys)
        additions.append(entry)
        used_keys.add(entry["ID"])
        seen_dois.add(doi)
        seen_titles.add(title)
        print(f"Adding: {entry['title']} ({doi})")

    if additions and not dry_run:
        database = BibDatabase()
        database.entries = additions
        writer = BibTexWriter()
        writer.indent = "  "
        writer.order_entries_by = None
        appended = bibtexparser.dumps(database, writer).rstrip() + "\n"
        # Append rather than reserialize: preserve existing citations and formatting.
        with path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write("\n\n" + appended)
    print(f"{'Would add' if dry_run else 'Added'} {len(additions)} publication(s).")
    if skipped:
        print(f"Skipped {len(skipped)} DOI(s): {', '.join(skipped)}")


def main():
    """Run the synchronization from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    args = parser.parse_args()
    # Check all supported month spellings before contacting external services.
    months = (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    )
    aliases = {month.lower(): month for month in months}
    aliases.update({month[:3].lower(): month for month in months})
    aliases["sept"] = "September"
    for alias, expected in aliases.items():
        sample = parse_bibtex(f"@article{{month_test, title={{Test}}, month={alias}}}")
        if len(sample) != 1 or sample[0].get("month") != expected:
            raise RuntimeError(f"BibTeX month parsing self-test failed for {alias}.")
    print("BibTeX month parsing self-test passed (including july and sept).", flush=True)
    sync(BIB_PATH, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
