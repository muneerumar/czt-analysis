# Frozen revision-stage reproducibility/update search protocol

**Paper:** *Cognitive Zero Trust: A Human-Centered Framework for Verifying Communication Requests in GenAI-Enabled Social Engineering*  
**Target journal:** *Computer Standards & Interfaces*  
**Phase:** W1  
**Protocol status:** Frozen for user review; execution is pending protocol approval.  
**Protocol freeze date:** 2026-09-30 (local time, Asia/Karachi)  
**Search date:** The actual local execution date must be entered in every search-log row. No planned date or historical date may be substituted.  
**Execution state at freeze:** No database searches have been executed in Phase W1.

## Purpose and scope

This protocol is a prospective revision-stage reproducibility and update search designed to address Reviewer 3's concern about retrieved, deduplicated, screened, excluded, and retained records. It defines the search, record handling, screening, and audit rules that will be used after user approval.

The original review remains a purposive, theory-building integrative review. Its historical search strings, hit counts, deduplication counts, and screening decisions were not logged. This protocol does not reconstruct or estimate those unavailable historical counts, and it does not create a retrospective PRISMA flow. Every count produced under this protocol will be labeled as a prospective revision-stage count.

The inclusion and exclusion criteria below are carried forward exactly from the current manuscript. They must not be changed to preserve the current 67-source corpus. Newly eligible sources identified by the prospective search will be retained and all affected analyses and outputs will be updated in a later phase.

The current coded corpus is a baseline for comparison only. It is not the expected result of the prospective search. See [CURRENT_CORPUS_BASELINE.txt](CURRENT_CORPUS_BASELINE.txt).

## Search execution and audit controls

1. Run each database query only after this protocol has been approved.
2. Use the exact Q1-Q3 text below, with the database wrapper or interface field specified below. Do not add synonyms, truncation, proximity operators, date limits, language limits, document-type filters, or other filters unless a later approved protocol amendment records the change before execution.
3. Record the actual local execution date, displayed hit count, whether that count is exact or approximate, records captured, export filename, screenshot filename, filters, and notes in `03_search_logs/search_log.csv`.
4. Preserve the original export and a screenshot of the results page or query state where the platform permits it. If a platform does not offer an export, save the inspected record metadata in the screening log and record that fact in `notes`.
5. Assign each captured record a stable `record_id`. A record is entered in `05_screening/screening_log.csv` before deduplication is finalized so that duplicates and their source records remain auditable.
6. Log backward and forward citation checking as additional discovery activities after the database searches. Use `database=citation_chaining`, `query_id=BACKWARD` or `FORWARD`, and describe the seed source and inspected citation set in `notes`.

## Exact Q1-Q3

The following query text is copied from the current manuscript's Table 4. The wording, spelling variants, quoted phrases, and Boolean structure are frozen for this phase.

**Q1 (zero trust × human communication)**

```text
("zero trust" OR "zero trust architecture") AND (phishing OR "social engineering" OR communication OR human)
```

**Q2 (GenAI deception)**

```text
("generative AI" OR LLM OR "large language model" OR deepfake OR "synthetic media") AND (phishing OR impersonation OR deception OR provenance)
```

**Q3 (human-centered verification)**

```text
("human-centered cybersecurity" OR "human-centred cybersecurity" OR "usable security" OR "organizational trust" OR "organisational trust") AND (verification OR escalation OR authority OR friction)
```

## Database-specific syntax and interface settings

The current manuscript expresses the database syntax with `Q` as a placeholder. During execution, replace `Q` with the complete literal Q1, Q2, or Q3 block above and record the expanded query in `exact_query`. The database field or interface setting is part of the syntax and must be recorded exactly as executed.

| Database | Frozen syntax or interface setting |
|---|---|
| Scopus | Advanced search: `TITLE-ABS-KEY(Q)`. Use straight ASCII quotation marks for phrases and the parentheses shown. |
| Web of Science Core Collection | Advanced search: `TS=(Q)`. `TS` is the Topic field. |
| IEEE Xplore | Command search with the `All Metadata` field selected: `(Q)`. Use the query exactly as displayed after submission. |
| ACM Digital Library | Advanced Search with Title, Abstract, and Author Keywords selected: `(Q)`. Do not silently broaden this to full text. |
| ScienceDirect | Advanced search field `Title, abstract or author-specified keywords`: enter `Q`. If the interface rejects the complete Boolean expression because of a connector limit, split only the OR groups into documented equivalent subqueries, preserve the AND relationship, run all resulting subqueries, and log every subquery. |
| SpringerLink | Advanced search: enter `Q` using the keyword/advanced-search fields corresponding to the manuscript's `with all/at least one of the words` instruction. Record the exact field values and Boolean expression shown by the interface. |
| Google Scholar | Search all fields using `Q`, with no date or document-type filter. Keep the default relevance order. Apply the stopping rule below. |
| Institutional repositories | Search each named institution's own site search and publication lists. Use the fixed topical targets `zero trust`, `AI risk`, `phishing`, `social engineering`, `synthetic media`, and `content provenance`; do not invent a total hit count when the site does not expose a reliable total. Record the site, search term or query, pages inspected, and items inspected. |

The literal expanded forms for the command-style databases are therefore:

| Database | Q1 | Q2 | Q3 |
|---|---|---|---|
| Scopus | `TITLE-ABS-KEY(("zero trust" OR "zero trust architecture") AND (phishing OR "social engineering" OR communication OR human))` | `TITLE-ABS-KEY(("generative AI" OR LLM OR "large language model" OR deepfake OR "synthetic media") AND (phishing OR impersonation OR deception OR provenance))` | `TITLE-ABS-KEY(("human-centered cybersecurity" OR "human-centred cybersecurity" OR "usable security" OR "organizational trust" OR "organisational trust") AND (verification OR escalation OR authority OR friction))` |
| Web of Science Core Collection | `TS=(("zero trust" OR "zero trust architecture") AND (phishing OR "social engineering" OR communication OR human))` | `TS=(("generative AI" OR LLM OR "large language model" OR deepfake OR "synthetic media") AND (phishing OR impersonation OR deception OR provenance))` | `TS=(("human-centered cybersecurity" OR "human-centred cybersecurity" OR "usable security" OR "organizational trust" OR "organisational trust") AND (verification OR escalation OR authority OR friction))` |
| IEEE Xplore | `("zero trust" OR "zero trust architecture") AND (phishing OR "social engineering" OR communication OR human)` in All Metadata | `("generative AI" OR LLM OR "large language model" OR deepfake OR "synthetic media") AND (phishing OR impersonation OR deception OR provenance)` in All Metadata | `("human-centered cybersecurity" OR "human-centred cybersecurity" OR "usable security" OR "organizational trust" OR "organisational trust") AND (verification OR escalation OR authority OR friction)` in All Metadata |
| ACM Digital Library | Same literal Q1 in Title + Abstract + Author Keywords | Same literal Q2 in Title + Abstract + Author Keywords | Same literal Q3 in Title + Abstract + Author Keywords |
| ScienceDirect | Same literal Q1 in `Title, abstract or author-specified keywords` | Same literal Q2 in `Title, abstract or author-specified keywords` | Same literal Q3 in `Title, abstract or author-specified keywords` |
| SpringerLink | Same literal Q1 in the approved advanced-search fields | Same literal Q2 in the approved advanced-search fields | Same literal Q3 in the approved advanced-search fields |
| Google Scholar | Same literal Q1 in all fields | Same literal Q2 in all fields | Same literal Q3 in all fields |

The query syntax was checked against the current manuscript Table 4 and the platform help material available on 2026-09-30. Scopus documents `TITLE-ABS-KEY` as the combined title, abstract, and keyword field; Web of Science documents `TS` as Topic; IEEE Xplore documents Boolean and command-search support; Springer Nature documents Boolean and phrase matching in advanced-search fields; and Google Scholar documents relevance ordering, a 1,000-result display limit, approximate result-count limitations, and the absence of bulk export. The interface-specific rows above remain the controlling protocol because database interfaces can change.

## Google Scholar stopping rule - revision-stage audit only

**Proposed rule for user approval:** For each of Q1, Q2, and Q3, run the exact query in all fields with no date or document-type filter, retain the default relevance order, and inspect every displayed result sequentially. Stop after **100 consecutive displayed records** have been inspected without identifying a new potentially eligible unique source. Reset the 100-record counter whenever a new potentially eligible unique source is identified. If Google Scholar reaches its platform display ceiling of 1,000 results before the 100-record condition is met, stop at that ceiling and record `GS_CAP_1000` in `notes`.

A potentially eligible unique source is a record that passes the title/abstract rule below or is sufficiently uncertain that it must advance to full-text screening. A duplicate of a source already captured does not reset the counter. Record the first and last inspected result rank, every page inspected, the stopping event, and any platform count shown. This is a bounded, relevance-ordered audit sample. It is not an exhaustive Google Scholar search, and a displayed result total must not be interpreted as complete coverage.

This stopping rule is proposed explicitly for user review and must not be silently replaced during execution.

## Institutional-site counting rule

Institutional sites are heterogeneous and may expose no reliable total hit count. When a site does not provide a stable, trustworthy total, enter `N/A` in both `hits_displayed` and `hits_exact_or_approx`; do not infer a number from pagination, a search-engine estimate, or the number of visible pages. Record the pages or publication-list sections actually inspected and the number of individual items actually inspected in `notes`. `records_exported` is the number of item records captured in the audit, not an estimate of the site's total holdings.

The named institutional sites are NIST, CISA, OMB, NSA, NCSC, ENISA, OWASP, MITRE, ISO, and C2PA. A site may be searched by its own search form and by its publication or resource lists. Each site, topical target, page range, and inspected-item count must be separately identifiable in the search log.

## Inclusion criteria

A source is included when it contributes directly to at least one of the following:

- zero trust architecture or deployment;
- phishing or social-engineering behavior;
- human-centered security;
- GenAI- or LLM-enabled deception;
- synthetic-media authenticity;
- organizational trust and decision-making;
- communication provenance; or
- AI and cybersecurity governance.

Peer-reviewed studies, recognized standards, and authoritative institutional guidance are eligible regardless of publication year. Preprints are eligible only when they address rapidly developing 2025-2026 threats not yet covered by peer-reviewed work.

## Exclusion criteria E1-E4

Sources are excluded when they are:

- **E1 — Promotional material.**
- **E2 — Duplicate versions of the same work, in which case the peer-reviewed version is kept.**
- **E3 — Lacking sufficient conceptual or methodological detail.**
- **E4 — AI-security work without a defensible link to deception, trust, communication, or organizational decision workflows.**

These are the exact E1-E4 criteria documented in the current manuscript. `FT-NA` and `AMB` are administrative audit statuses defined below; they are not new substantive exclusion criteria.

## Unit of analysis

The unit of analysis is **one unique source**. A source is a distinct scholarly work, standard, report, book/chapter, or eligible preprint after version resolution and deduplication. Database records, alternate URLs, and preprint/peer-reviewed manifestations are discovery records until the unique-source rule is applied.

## Deduplication rule hierarchy

Apply the following hierarchy in order before final title/abstract counts are reported:

1. **Normalized DOI.** Lowercase the DOI, remove `https://doi.org/`, `http://doi.org/`, `doi:`, query strings, fragments, surrounding whitespace, and trailing punctuation. Identical normalized DOIs are one work.
2. **Database accession or document identifier.** Identical accession/document identifiers within a database are one record manifestation. Preserve the source database and accession information in the evidence note.
3. **Exact bibliographic key.** Match a normalized title together with first-author family name and publication year. Normalize case, whitespace, punctuation, and Unicode quotation marks only for matching; preserve the original citation text in the log.
4. **Version resolution.** When records are probable versions of the same work, compare title, authors, abstract/content, venue, publisher record, DOI, and explicit links between versions. Do not merge on a title fragment alone.
5. **Manual adjudication.** Near matches that cannot be resolved by the first four rules are flagged `AMB` and reviewed by the lead reviewer with methodological review by the second author. A fuzzy match alone never silently removes a record.

All manifestations remain auditable in `screening_log.csv`. The non-canonical manifestation receives decision `duplicate` and exclusion code `E2`; the canonical source is the one carried forward. If the same work has a peer-reviewed version and a preprint, retain the peer-reviewed version and mark the preprint E2. If no peer-reviewed version exists at the execution date and the preprint satisfies the rapidly developing 2025-2026 condition, the preprint may be retained as the unique source.

## Title/abstract screening rule

After deduplication, screen the title and abstract, when available, against the inclusion list and E1-E4:

- advance the record to full text when the title/abstract directly addresses at least one inclusion domain;
- exclude at this stage only when the title/abstract clearly shows E1, E2, E3, or E4, or is clearly unrelated to every inclusion domain;
- do not require all three queries or an explicit `Cognitive Zero Trust` label;
- if the title/abstract is missing, sparse, or inconclusive, advance the record rather than excluding it solely for that reason; and
- record the decision, code, and short evidence note in `screening_log.csv`.

The title/abstract stage is a screening decision, not a source-quality judgment. Records advanced because of uncertainty must be marked for full-text review.

## Full-text screening rule

For every deduplicated record advanced to full text, check the complete accessible source against the exact inclusion list and E1-E4. Retain the unique source only when it contributes directly to at least one inclusion domain, belongs to an eligible source class, and is not excluded by E1-E4. Record the decisive passage, section, page, or metadata evidence in `evidence_note`.

Apply the current coding codebook after retention. Each retained source is coded individually. Ambiguous dimension codes use the lower code, as specified in the codebook; this lower-code rule does not change eligibility.

## Preprints and peer-reviewed duplicates

Preprints follow the exact eligibility rule above. A preprint is not retained merely because it is recent. It must address a rapidly developing 2025-2026 threat that is not yet covered by peer-reviewed work at the search date and must otherwise meet the inclusion rule.

When a peer-reviewed version of the same work is found, retain the peer-reviewed version and classify the preprint as E2. If the peer-reviewed version materially changes the work and is not the same source, resolve the case using the version hierarchy and document the decision. The decision must never be made solely to preserve the baseline 67-source corpus.

## Records with missing abstracts

Missing abstracts are not, by themselves, grounds for exclusion. Use the title, author keywords, database metadata, publisher or official record, and accessible full text. If the record remains potentially eligible, advance it to full-text screening and record `abstract_missing` in `evidence_note`. If the full text cannot be accessed after the access procedure below, record `full_text_status=inaccessible` and `exclusion_code=FT-NA`; do not claim that E1-E4 was established.

## Inaccessible full texts

For a record advanced to full text, check, in order, the publisher or official source page, an institutional repository or author manuscript, and an available library or subscribed access route. Record each route attempted. If no sufficient full text is available after these checks, set `full_text_status=inaccessible`, decision `not_assessed`, and exclusion code `FT-NA`. Such a record is reported separately as inaccessible full text and is not counted as an E1-E4 substantive exclusion. It is not retained because eligibility cannot be established from the available evidence.

If a later approved search phase obtains a sufficient full text before the phase is closed, replace `FT-NA` with the documented full-text decision and preserve the earlier access note.

## Ambiguous cases and review status

Flag uncertain eligibility, version identity, source type, or full-text interpretation as `AMB` in the audit note and pause the final decision. The lead reviewer makes the initial determination; the second author provides methodological review and validation for flagged cases. No formal inter-rater agreement statistic is claimed. Resolve the case by applying the exact inclusion/exclusion wording, the codebook, and the evidence in the source. If uncertainty remains after review, retain only when direct inclusion is supported and no exclusion criterion applies; otherwise record the documented reason for not retaining it. Use `review_status` to record `initial`, `author_review`, or `resolved`.

## Prospective counts and reporting

The prospective flow will be computed from the audit records as follows:

- **Retrieved:** records captured from the search results or inspected institutional/citation pages and entered in the screening log. `hits_displayed` is a platform display value and may be approximate; it is not substituted for captured records.
- **Deduplicated:** retrieved records after E2 duplicate manifestations are collapsed to one canonical unique source.
- **Title/abstract screened:** deduplicated records with a recorded title/abstract decision.
- **Full-text assessed:** deduplicated records for which full-text eligibility was assessed, including records with a missing abstract when full text is available.
- **Excluded:** deduplicated records not retained, reported separately by E1-E4, `FT-NA`, and any resolved administrative status. `FT-NA` is not presented as an E1-E4 reason.
- **Retained:** unique sources that pass full-text screening and have no applicable exclusion code.

The original 67-source count is a pre-existing coded-corpus baseline. Any prospective counts are revision-stage counts generated after execution of this protocol. They are not reconstructed historical counts and must never be described as the original review's retrieved, deduplicated, screened, excluded, or retained flow.

## Files and evidence register

- `03_search_logs/search_log.csv` — one row per executed query/site/citation-chaining activity.
- `05_screening/screening_log.csv` — one row per captured record manifestation, including duplicates.
- `05_screening/full_text_exclusions.csv` — one row per full-text-stage record not retained, with E1-E4 or administrative status.
- `10_audit_logs/phase_log.md` — dated decisions, execution status, amendments, and evidence files.
- `01_protocol/CURRENT_CORPUS_BASELINE.txt` — current 67-source baseline and source-type breakdown.

## Verification references consulted before freeze

- [Scopus advanced search and field codes](https://service.elsevier.com/app/answers/detail/a_id/11365/supporthub/scopus/~/how-can-i-best-use-the-advanced-search%3F/)
- [Web of Science Core Collection search field tags](https://webofscience.help.clarivate.com/en-us/Content/wos-core-collection/woscc-search-field-tags.htm)
- [IEEE Xplore searching and saving searches guide](https://ieeexplore.ieee.org/Xplorehelp/downloads/user-guides/IEEE_Xplore_Searching_and_Saving_Searches.pdf)
- [Springer Nature Link advanced search](https://support.springernature.com/en/support/solutions/articles/6000080445)
- [Google Scholar Search Help](https://scholar.google.com/intl/uk/scholar/help.html)

