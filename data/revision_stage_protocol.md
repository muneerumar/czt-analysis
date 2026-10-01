# Revision-stage reproducibility protocol

**Paper:** *Cognitive Zero Trust: A Human-Centered Framework for Verifying Communication Requests in GenAI-Enabled Social Engineering*

**Rerun date:** 30 September 2026 (Asia/Karachi)

**Status:** Completed prospective revision-stage rerun and corpus integration record.

## Purpose and scope

The original review was a purposive, theory-building integrative review. Its historical database-level retrieval, export, deduplication, and screening logs were not retained, so historical July counts cannot be reconstructed reliably. This protocol documents a prospective revision-stage rerun and repair capture. Its counts describe the records captured and processed on 30 September 2026; they do not reconstruct the original search and do not claim exhaustive coverage or prevalence.

## Search sources and syntax

The rerun used the frozen database-specific protocol in search_archive/01_protocol/protocol_frozen.md across Scopus, Web of Science Core Collection, IEEE Xplore, ACM Digital Library, ScienceDirect, SpringerLink, Google Scholar, and the named institutional sites. The three concept queries were:

- Q1: ("zero trust" OR "zero trust architecture") AND (phishing OR "social engineering" OR communication OR human)
- Q2: ("generative AI" OR LLM OR "large language model" OR deepfake OR "synthetic media") AND (phishing OR impersonation OR deception OR provenance)
- Q3: ("human-centered cybersecurity" OR "human-centred cybersecurity" OR "usable security" OR "organizational trust" OR "organisational trust") AND (verification OR escalation OR authority OR friction)

Database-specific fields and wrappers were retained as recorded in the frozen protocol and the machine-readable search log. Access, export, and platform ceiling limitations were recorded rather than filled with estimates.

## Record handling and eligibility

The unit of analysis was one unique source after version resolution. DOI, database accession, exact bibliographic key, version comparison, and manual adjudication were applied in that order. Title/abstract screening used the frozen inclusion domains. Full-text exclusions used only E1 promotional material, E2 duplicate/version, E3 insufficient detail, and E4 AI-security work without a defensible link to deception, trust, communication, or organizational decision workflows. FT-NA records were kept administratively separate from substantive E1-E4 exclusions.

## Exact revision-stage counts

The repaired export denominator contains 740 records: 490 ScienceDirect and 250 IEEE Xplore. Seven exact publisher-accession duplicates were removed, leaving 733 unique records. Title/abstract screening excluded 157 records (E1=0, E2=1, E3=3, E4=153). The remaining 576 records were sought for full text; all 576 remained unavailable, so 0 were substantively assessed at full text and 0 repaired records were finally eligible. Six separately logged W4 reassessment/update rows were outside that repaired-export denominator. They resolved ref51 and ref52 as E4 exclusions, ref53 as the preferred workshop version with its arXiv manifestation E2, and ref94 as FT-NA because complete authoritative full text was unavailable, and ref95 as the newly eligible source.

The final coded corpus contains 66 sources: 26 journal articles, 15 conference papers, 2 preprints, 20 standards or reports, and 3 books or chapters. Five version replacements are one-for-one. Ref94 remains outside the coded corpus as FT-NA because complete authoritative full text was unavailable; ref95 is the one newly eligible retained source.

## Limitations and reporting

ScienceDirect Q3 reported 10,746 hits but only 200 result cards were captured before an access error. IEEE Q1 and Q2 were partial 100-record captures, while Q3 contributed 50 records. These records document the observed rerun and are not an exhaustive database census. No two-coder reliability statistic was calculated for the search screening in this rerun; AI-assisted processing was not treated as independent human validation. (Inter-coder reliability of the literature classification was assessed separately on 30 September 2026; see `second_coder_agreement_report.md`.) The search audit does not validate the scenario analysis or its results.

## Linked artifacts

- revision_stage_search_log.csv
- revision_stage_dedup_log.csv
- revision_stage_screening_log.csv
- revision_stage_full_text_exclusions.csv
- revision_stage_flow_counts.csv
- ../../06_corpus_update/revision_stage_flow_counts.json (historical C6 record)
- revision_stage_flow_counts.json (C8 final corrected record)
- updated literature_coding_matrix.csv
- coding_codebook.md (unchanged)
- 10_audit_logs/literature_coding_matrix_pre_C6_update_20260930.csv
