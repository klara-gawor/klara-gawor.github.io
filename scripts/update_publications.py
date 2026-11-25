"""Synchronize ORCID journal articles and select recent first-author publications."""
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
N_SELECTED = 3
FIRST_AUTHOR_NAMES = {"gawor klara", "klara gawor", "gawor k", "k gawor"}
MONTHS = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)
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
    parser.bib_database.strings.update({month.lower(): month for month in MONTHS})
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


def is_first_author(entry):
    """Identify the first listed author from the BibTeX author field."""
    author = re.split(r"\s+and\s+", entry.get("author", ""), maxsplit=1, flags=re.I)[0]
    name = convert_to_unicode({"author": author})["author"].casefold()
    name = " ".join(re.findall(r"[^\W\d_]+", name))
    return name in FIRST_AUTHOR_NAMES


def publication_date(entry):
    """Rank articles by publication year, month and day, when available."""
    year = re.search(r"\b\d{4}\b", entry.get("year", ""))
    year = int(year.group()) if year else 0
    month = entry.get("month", "").strip().casefold().rstrip(".")
    aliases = {name.casefold(): index for index, name in enumerate(MONTHS, 1)}
    aliases.update({name[:3].casefold(): index for index, name in enumerate(MONTHS, 1)})
    aliases["sept"] = 9
    month = int(month) if month.isdigit() else aliases.get(month, 0)
    day = entry.get("day", "").strip()
    day = int(day) if day.isdigit() else 0
    date = re.fullmatch(r"(\d{4})(?:-(\d{2})(?:-(\d{2}))?)?", entry.get("date", "").strip())
    if date:
        year = int(date.group(1))
        month = int(date.group(2)) if date.group(2) else month
        day = int(date.group(3)) if date.group(3) else day
    return year, month if 1 <= month <= 12 else 0, day if 1 <= day <= 31 else 0


def select_publications(entries):
    """Return the newest first-author journal articles, with stable tie-breaking."""
    candidates = [
        entry for entry in entries
        if entry["ENTRYTYPE"].lower() == "article" and is_first_author(entry)
    ]
    candidates.sort(key=lambda entry: (publication_date(entry), entry["ID"]), reverse=True)
    return candidates[:N_SELECTED]


def serialize_entries(entries):
    """Serialize new entries without reformatting the existing bibliography."""
    database = BibDatabase()
    database.entries = entries
    writer = BibTexWriter()
    writer.indent = "  "
    writer.order_entries_by = None
    return bibtexparser.dumps(database, writer).rstrip() + "\n"


def update_selected_flags(text, entries):
    """Update selected flags only and verify that all other citation data is unchanged."""
    selected = select_publications(entries)
    selected_ids = {entry["ID"] for entry in selected}
    by_id = {entry["ID"]: entry for entry in entries}
    expected = {key: entry.copy() for key, entry in by_id.items()}
    if len(expected) != len(entries):
        raise ValueError("Duplicate bibliography keys; no changes made.")

    changes = {}
    for entry in entries:
        key = entry["ID"]
        flag = entry.get("selected")
        if key in selected_ids and flag != "true":
            changes[key] = "true"
        elif key not in selected_ids and flag is not None and flag.strip().lower() != "false":
            changes[key] = "false"
        if key in changes:
            expected[key]["selected"] = changes[key]

    if not changes:
        return text, selected

    # Modify individual entry blocks, leaving other fields and the YAML header intact.
    headers = list(re.finditer(r"(?im)^[ \t]*@[a-z]+\s*[{(]\s*([^,\r\n{}()]+),", text))
    field_pattern = (
        r'(?im)(^[ \t]*|(?<=,)[ \t\r\n]*)selected\s*=\s*'
        r'(?:\{[^{}]*\}|"[^"]*"|[^\s,})]+)'
    )
    for index in reversed(range(len(headers))):
        header = headers[index]
        key = header.group(1).strip()
        if key not in changes:
            continue
        end = headers[index + 1].start() if index + 1 < len(headers) else len(text)
        block = text[header.end():end]
        value = changes[key]
        if "selected" in by_id[key]:
            block, count = re.subn(field_pattern, rf"\g<1>selected = {{{value}}}", block, count=1)
            if count != 1:
                raise ValueError(f"Could not locate selected field in {key}; no changes made.")
        else:
            block = f"\n  selected = {{{value}}}," + block
        text = text[:header.end()] + block + text[end:]

    # A formatting edge case must never silently remove or change a publication.
    actual_entries = parse_bibtex(text)
    actual = {entry["ID"]: entry for entry in actual_entries}
    if len(actual_entries) != len(entries) or actual != expected:
        raise ValueError("Selected-publication update changed other metadata; no changes made.")
    return text, selected


def sync(path, dry_run=False):
    """Append missing citations and update the homepage selection."""
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

    updated = original
    if additions:
        updated = original.rstrip() + "\n\n" + serialize_entries(additions)
    all_entries = parse_bibtex(updated) if additions else existing
    actual_keys = {entry["ID"] for entry in all_entries}
    if len(all_entries) != len(existing) + len(additions) or actual_keys != used_keys:
        raise ValueError("Bibliography serialization lost entries; no changes made.")
    updated, selected = update_selected_flags(updated, all_entries)
    if updated != original and not dry_run:
        path.write_text(updated, encoding="utf-8", newline="\n")

    print(f"{'Would add' if dry_run else 'Added'} {len(additions)} publication(s).")
    print(f"{'Would select' if dry_run else 'Selected'} {len(selected)} first-author publication(s):")
    for entry in selected:
        print(f"  {entry.get('year', '')}: {entry['title']}")
    if skipped:
        print(f"Skipped {len(skipped)} DOI(s): {', '.join(skipped)}")


def test_selection():
    """Check ranking, author matching, flag replacement and idempotency."""
    sample = """---
---
@article{old, author={Gawor, Klara}, title={Old}, year={2020}, selected={true}}
@article{coauthor, author={Other, A and Gawor, Klara}, title={Coauthor}, year={2027},
  selected = {true}, code={https://example.com/code}}
@article{first, author={Gawor, Klara}, title={First}, year={2025}, month={July}}
@article{second, author={Klara Gawor}, title={Second}, year={2025}, month=sept}
@article{third, author={Gawor, K.}, title={Third}, year={2026}, selected={false}}
@article{fourth, author={Gawor, Klara}, title={Fourth}, year={2024}}
"""
    updated, selected = update_selected_flags(sample, parse_bibtex(sample))
    if [entry["ID"] for entry in selected] != ["third", "second", "first"]:
        raise RuntimeError("First-author selection self-test failed.")
    repeated, _ = update_selected_flags(updated, parse_bibtex(updated))
    if repeated != updated or not updated.startswith("---\n---\n"):
        raise RuntimeError("Selected-publication update is not idempotent.")
    print("First-author selection self-test passed.", flush=True)


def main():
    """Run the synchronization from the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing.")
    args = parser.parse_args()
    # Check all supported month spellings before contacting external services.
    aliases = {month.lower(): month for month in MONTHS}
    aliases.update({month[:3].lower(): month for month in MONTHS})
    aliases["sept"] = "September"
    for alias, expected in aliases.items():
        sample = parse_bibtex(f"@article{{month_test, title={{Test}}, month={alias}}}")
        if len(sample) != 1 or sample[0].get("month") != expected:
            raise RuntimeError(f"BibTeX month parsing self-test failed for {alias}.")
    print("BibTeX month parsing self-test passed (including july and sept).", flush=True)
    test_selection()
    sync(BIB_PATH, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
