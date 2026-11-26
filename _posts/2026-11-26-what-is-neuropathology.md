---
layout: post
title: "From the beginning: What is neuropathology and why does it matter?"
date: 2026-11-26
description: "An introduction to neuropathology, from brain donation to computational image analysis."
tags: [neuropathology, computational-neuropathology]
thumbnail: assets/img/blog/what-is-neuropathology/thumbnail.png
categories: [perspectives]
related_posts: false
---

## How I ended up in neuropathology

The brain fascinated me from the very beginning. My first approach to studying it was highly theoretical, as I studied cognitive science at the Department of Philosophy. I quickly realized, however, that the real stuff for me was happening in psychology and neurobiology.

I tried my hand at research in several different labs, developed my first (very bad) algorithm for pupil detection in videos of mice, and, thanks to an amazing internship in genomics, discovered the fascinating world of neurodegenerative diseases.

Why am I mentioning this? Because all these research experiences had one thing in common: machines collected data, and we analyzed them.

Imagine my surprise when I started my dream PhD and discovered that data collection involved looking at tissue sections and saying, “It looks moderate,” followed by “Hmm, this one looks worse, let's call it severe.”

What do you even mean by that? 😲 What are the criteria? (Shout-out to my great supervisor, Dr. Thal, who survived having me as a PhD student.)

It turns out that this educated judgment, a combination of experience, established criteria, and intuition, is remarkably difficult to reproduce computationally. Much of what we know about neurodegenerative diseases today comes from precisely this kind of assessment.

In my next post, I will explain why this approach works so well, despite its seemingly subjective nature. I will also argue that many aspects of neuropathology can be viewed as a highly sophisticated, **biology-driven object detection problem** — a perspective that could help us standardize and automate parts of the process. This is precisely why I joined Dr. Irwin's lab, where we share a vision of bringing traditional neuropathology and computational approaches together, not simply to automate existing methods, but to ask biological questions that were previously difficult or impossible to address.

By now, you have probably realized that I am not a neuropathologist. While I am not qualified to make formal neuropathological diagnoses, I am a neuroscientist and a self-proclaimed neuropathology enthusiast. This brings me to another point I would like to make throughout this blog: **neuropathology is much more than a diagnostic discipline**.

For those coming from other scientific backgrounds, neuropathology can seem like a rather mysterious world, with its own terminology, methods, and unwritten rules. Yet human brain tissue offers a unique opportunity to answer fundamental biological questions. I believe that making neuropathological research more accessible to scientists from different disciplines, while building on the expertise of neuropathologists, could bring new perspectives and methods to the field and open up entirely new avenues of research.

With this in mind, let us begin.

## What is neuropathology?

The word neuropathology combines the Greek roots *neuron* (nerve), *pathos* (suffering or disease), and *logos* (study). Interestingly, the term is thought to have been coined by Samuel Taylor Coleridge (1772–1834), an English poet and philosopher, although its meaning at the time was quite different from what we understand by neuropathology today. Coleridge himself had quite a personal relationship with medicine, suffering from chronic health problems and using opium to relieve his symptoms \[[1](#ref-1)\].

Today, neuropathology is a subspecialty of anatomical pathology that focuses on diseases of the brain, spinal cord, and peripheral nerves, but also extends to skeletal muscle and the eye \[[2](#ref-2)\]. The focus on disease distinguishes neuropathology from **neuroanatomy**, although the boundary between the two disciplines is rather thin. After all, recognizing what is abnormal requires a good understanding of what is normal.

Neuropathologists also differ from **neurologists**, who primarily work directly with living patients, whereas neuropathologists diagnose diseases by examining tissues and cells, often in combination with molecular analyses.

The brain, however, is a particularly difficult organ to study. Unlike many other organs, it is relatively inaccessible during life, and removing even a small piece of it can have serious consequences. As a result, much of what we know about the cellular and molecular changes occurring in the human brain during neurodegeneration comes from studying **postmortem tissue**.

The unique characteristics of the brain have also led neuropathology to develop its own methods, terminology, and lingo. One interesting example is the word *pathology* itself. Although it broadly refers to disease-related abnormalities, researchers studying neurodegeneration\* often use it to describe abnormal accumulations of proteins, such as tau, alpha-synuclein, or TDP-43. These protein aggregates are a hallmark of many neurodegenerative diseases, although their exact role in disease development and progression is still being investigated \[[3](#ref-3)\].

## Where does human brain tissue come from?

Much of human neuropathological research would not be possible without brain donation, and we are extremely grateful to every wonderful person who has made this decision, as well as to their families.

Brain donations are often arranged through programs established in collaboration with neurologists and other clinicians, who inform their patients about the possibility of donating their brains after death. Donations can also be arranged by family members, subject to the relevant consent requirements. In some cases tissue is obtained through collaborations with medical examiners and forensic pathologists \[[4](#ref-4), [5](#ref-5)\].

Donated brains are collected, processed, examined, preserved, and made available to researchers through institutions called **brain banks** \[[4](#ref-4), [5](#ref-5)\]. Because many brain banks are associated with specialized neurological clinics, their collections often contain a relatively high proportion of individuals with neurological diseases. Obtaining well-characterized control tissue can therefore be challenging.

Interestingly, a person who had no neurological symptoms during life may still have considerable pathological changes in their brain \[[3](#ref-3), [6](#ref-6)\]. This makes donations from individuals without neurological symptoms particularly valuable, not only for understanding normal aging but also for investigating why some people are more resilient to pathological changes than others.

## From brain donation to microscope slides

<figure>
  <img src="{{ '/assets/img/blog/what-is-neuropathology/figure1.png' | relative_url }}"
       class="img-fluid rounded"
       alt="Neuropathological pipeline"
       style="width: 100%; height: auto; display: block; margin: auto;">
  <figcaption>
    <strong>Figure 1.</strong> An overview of brain tissue preservation and the main steps in preparing microscope slides.
  </figcaption>
</figure>

Once collected, the brain is typically weighed, photographed, and macroscopically examined. Visible abnormalities, such as atrophy (a reduction in tissue volume), vascular changes, infarcts, hemorrhages, and unusual anatomical features, are documented \[[7](#ref-7)\].

A common approach is to preserve one cerebral hemisphere in a chemical **fixative**, usually formalin, and freeze the other hemisphere or selected parts of it. Fixed tissue is particularly useful for microscopic examination, while frozen tissue is valuable for many molecular and biochemical analyses \[[4](#ref-4), [5](#ref-5), [7](#ref-7)\].

Brain tissue is extremely precious, and decisions about how to process it need to be made before we even know what research questions it might help answer in the future. Each brain bank therefore has its own protocols, designed to make the tissue useful for as many types of research as possible.

The next step is to sample specific brain regions. The brain is far from uniform, and different neurodegenerative diseases preferentially affect different regions. For example, the hippocampus is particularly important in the assessment of Alzheimer's disease, while the substantia nigra is important in the assessment of Parkinson's disease \[[3](#ref-3), [6](#ref-6)\].

The cerebral hemispheres are commonly cut into coronal slabs approximately one centimeter thick. Within these slabs, key anatomical landmarks are identified, and smaller pieces of tissue containing specific brain regions, known as tissue **blocks**, are collected \[[7](#ref-7)\].

**In neuropathology, where something happens is often just as important as what happens.**

The fixed tissue blocks are then processed and embedded in a supporting medium, most commonly **paraffin wax** (relatively cheap and easy to use). Using an instrument called a microtome, the tissue is cut into very, very thin sections, only a few micrometers thick, and transferred onto glass microscope slides \[[8](#ref-8)\].

One of the great advantages of paraffin-embedded tissue is that it can be stored and remain useful for decades, although not all molecular targets are equally well preserved \[[9](#ref-9)\]. This allows us to study tissue collected many years ago using technologies that did not even exist at the time of collection!

Because these very thin sections are largely transparent (with a few interesting exceptions that deserve a separate discussion), they usually need to be stained.

Conventional **histological stains**, such as hematoxylin and eosin, use dyes to visualize different tissue structures, while **immunohistochemistry** (IHC) uses antibodies to detect specific targets, most commonly proteins. Depending on the staining method, we can visualize individual neurons, glial cells, blood vessels, or disease-associated protein aggregates \[[3](#ref-3), [8](#ref-8)\].

However, how the tissue was collected, preserved, processed, stored, and stained can influence what we ultimately see under the microscope. These sources of variability are among the reasons why obtaining reliable and comparable quantitative measurements from histological sections remains so challenging \[[9](#ref-9), [10](#ref-10)\].

## From microscope slides to digital images

Traditionally, stained tissue sections have been examined using **brightfield microscopy**. Neuropathologists describe the observed changes and often use **semiquantitative scoring systems** to assess their severity. For example, the amount of protein pathology in a particular brain region might be described as absent, mild, moderate, or severe \[[6](#ref-6), [10](#ref-10)\].

Alternatively, we can use fluorescence-based techniques, such as **immunofluorescence**. These techniques can facilitate quantitative measurements and allow us to visualize multiple proteins within the same tissue section, helping us investigate how different pathological changes and cell types relate to one another \[[11](#ref-11)\].

Increasingly, glass slides are scanned to generate high-resolution digital images, known as **whole-slide images (WSI)**. While quantitative approaches in neuropathology have existed for decades, slide scanning allows us to perform such analyses on a much larger scale \[[12](#ref-12)\].

Rather than simply describing how much pathology is present, we can ask more detailed questions. How many protein aggregates are there? Do they differ in size or shape? Are they more common in particular cortical layers? Are certain types of neurons more vulnerable than others?

This is where computational neuropathology comes into play, combining traditional neuropathological knowledge with image analysis, statistics, computer vision, and machine learning \[[12](#ref-12)\].

This approach, however, comes with its own set of challenges, which I will explore in later posts.

## Why does neuropathology matter?

<figure>
  <img src="{{ '/assets/img/blog/what-is-neuropathology/figure2.png' | relative_url }}"
       class="img-fluid rounded"
       alt="Research areas"
       style="width: 60%; height: auto; display: block; margin: auto;">
  <figcaption>
    <strong>Figure 2.</strong> Main areas of research involving neuropathological examination.
  </figcaption>
</figure>

By examining changes at the cellular and molecular levels, neuropathology helps us understand the biological processes underlying neurological diseases. It also teaches us about normal brain structure, how the brain ages, and how it differs between individuals.

Interestingly, two patients may present with very similar symptoms but have quite different underlying diseases. Conversely, two individuals with similar pathological changes in their brains may have experienced very different symptoms during life \[[3](#ref-3), [6](#ref-6)\].

Although we now have access to an increasing number of biomarkers that allow us to detect disease-related changes in living patients, postmortem neuropathological examination remains an important reference for establishing the underlying diagnosis. It helps us understand these seemingly contradictory observations, refine clinical diagnoses, and evaluate the biomarkers used during life \[[3](#ref-3), [4](#ref-4), [6](#ref-6), [12](#ref-12)\].

What I find particularly fascinating about neuropathology is that, despite more than a century of examining human brains under microscopes, there is still so much to discover. Even tissue collected decades ago can offer new insights when examined using new methods or approached with different questions.

In future posts, I would like to explore how we study the human brain, what our methods can and cannot tell us, and how computational approaches might help answer some of the questions that remain unresolved.

\* Although neuropathology covers a wide range of conditions, from brain tumors to infections and developmental abnormalities, I will focus here on neurodegenerative diseases, which are the subject of my own research.

## Words to use to impress a neuropathologist

- **Postmortem tissue**: tissue collected after death.
- **Brain bank**: an institution that collects, preserves, characterizes, and distributes human brain tissue for research.
- **Protein aggregates**: abnormal accumulations of proteins that can form within or outside cells (often informally referred to as “pathology”).
- **Atrophy**: a reduction in the size or volume of a tissue or organ.
- **Macroscopic examination**: examination of tissue structures and abnormalities visible without a microscope.
- **Fixation**: preservation of tissue, usually using chemicals, to prevent degradation and maintain its structure.
- **Coronal slab**: a relatively thick slice of the brain cut in a plane that separates its front and back.
- **Tissue block**: a small piece of tissue collected for further processing and examination.
- **Paraffin embedding**: the process of embedding tissue in wax to provide support for cutting thin sections.
- **Microtome**: an instrument used to cut very thin tissue sections.
- **Immunohistochemistry**: a technique that uses antibodies to visualize specific targets within tissue sections.
- **Immunofluorescence**: a technique that uses antibodies and fluorescent labels to visualize specific targets.
- **Semiquantitative scoring**: assessing the extent or severity of tissue changes using ordered categories rather than direct numerical measurements.
- **Whole-slide image**: a high-resolution digital image of the tissue on a microscope slide.
- **Computational neuropathology**: the application of computational methods to the detection, measurement, and interpretation of neuropathological features.

## References

1. <a id="ref-1"></a>Vickers N. (2004). [Coleridge and the Doctors: 1795–1806](https://academic.oup.com/book/5761). Oxford University Press.
2. <a id="ref-2"></a>College of American Pathologists. [Neuropathology](https://www.cap.org/education/pathology-subspecialties/neuropathology/).
3. <a id="ref-3"></a>Dugger BN, Dickson DW. (2017). [Pathology of neurodegenerative diseases](https://pubmed.ncbi.nlm.nih.gov/28062563/). *Cold Spring Harbor Perspectives in Biology*, 9(7), a028035.
4. <a id="ref-4"></a>Toledo JB, et al. (2014). [A platform for discovery: The University of Pennsylvania Integrated Neurodegenerative Disease Biobank](https://doi.org/10.1016/j.jalz.2013.06.003). *Alzheimer's & Dementia*, 10(4), 477–484.e1.
5. <a id="ref-5"></a>National Institutes of Health. [NeuroBioBank Best Practices](https://www.neurobiobank.nih.gov/about-best-practices/).
6. <a id="ref-6"></a>Montine TJ, et al. (2012). [National Institute on Aging–Alzheimer's Association guidelines for the neuropathologic assessment of Alzheimer's disease: A practical approach](https://pmc.ncbi.nlm.nih.gov/articles/PMC3268003/). *Acta Neuropathologica*, 123, 1–11.
7. <a id="ref-7"></a>Iwasaki Y. (2022). [Brain cutting and trimming](https://doi.org/10.1111/neup.12787). *Neuropathology*, 42(5), 343–352.
8. <a id="ref-8"></a>Hywood JD, Yin AH. (2025). [An introduction to anatomical pathology](https://doi.org/10.1093/postmj/qgae160). *Postgraduate Medical Journal*, 101(1194), 366–370.
9. <a id="ref-9"></a>Grillo F, et al. (2017). [Immunohistochemistry on old archival paraffin blocks: Is there an expiry date?](https://pubmed.ncbi.nlm.nih.gov/28596153/) *Journal of Clinical Pathology*, 70(11), 988–993.
10. <a id="ref-10"></a>Meyerholz DK, Beck AP. (2018). [Principles and approaches for reproducible scoring of tissue stains in research](https://doi.org/10.1038/s41374-018-0057-0). *Laboratory Investigation*, 98, 844–855.
11. <a id="ref-11"></a>Taube JM, et al. (2020). [The Society for Immunotherapy of Cancer statement on best practices for multiplex immunohistochemistry (IHC) and immunofluorescence (IF) staining and validation](https://jitc.bmj.com/content/8/1/e000155). *Journal for ImmunoTherapy of Cancer*, 8(1), e000155.
12. <a id="ref-12"></a>Rosado AM, et al. (2025). [Digital neuropathology of neurodegenerative disorders: Foundations, research advances, and future directions](https://doi.org/10.1002/alz.70775). *Alzheimer's & Dementia*, 21(11), e70775.

## Helpful resources for the curious

**[Brain cutting and trimming – Yasushi Iwasaki (2022)](https://onlinelibrary.wiley.com/doi/full/10.1111/neup.12787)**

A very good illustrated overview of brain examination, cutting, and the selection of tissue blocks for neuropathological assessment.

**[An Introduction to the Brain Autopsy – Vanessa Smith (2024)](https://www.youtube.com/watch?v=pCPxu-q0YjY)**

A step-by-step video from the American Association of Neuropathologists' Teaching Rounds showing brain cutting and tissue block preparation.

**[Neuropathology – Dimitri P. Agamanolis](https://neuropathology-web.org/)**

A comprehensive, freely accessible, illustrated compendium of neuropathology, covering much more than neurodegenerative diseases.

**[WebPath: Neuropathology – University of Utah](https://webpath.med.utah.edu/CNSHTML/CNSIDX.html)**

An extensive educational collection of macroscopic and microscopic images illustrating different diseases of the nervous system.



**The views expressed in this article are my own and do not represent those of my affiliated institutions.**