# C3 Deduplication Method

## Scope

This method creates the C3 master-record and conservative deduplication outputs from W2 machine-readable exports found under 02_search_exports/raw/. Scientific title/abstract or full-text inclusion and exclusion decisions are outside this phase.

The raw export directory is preserved byte-for-byte. Screenshot artifacts are inventoried and reconciled to 03_search_logs/search_log.csv, but screenshots are not treated as bibliographic exports and are not OCR-parsed into records.

## Source handling and master schema

Supported input formats for this phase are RIS, BibTeX/BibLaTeX, CSV/TSV, EndNote XML, NBIB, and JSON bibliographic exports. Each parsed row receives a deterministic record_id based on sorted source-file order and row order. Original source provenance is retained in:

- source_database: database named by the matching search-log row;
- query_ids: one or more matching query_id values;
- source_export_files: the workspace-relative export path or paths.

The master schema is:

record_id,title,authors,year,doi,journal_or_venue,abstract,keywords,url,source_database,query_ids,source_export_files

When multiple source manifestations are confirmed as the same work, fields are combined conservatively. Non-empty values are retained, source provenance is unioned, and no scientific eligibility decision is inferred.

## Normalization

Normalization is used only for matching:

- DOI: lowercase; remove https://doi.org/, http://doi.org/, and doi: prefixes; remove query strings, fragments, surrounding whitespace, and trailing punctuation.
- Title: Unicode normalization; lowercase; normalize quotation marks; remove punctuation; collapse whitespace; compare the resulting token string.
- Authors: normalize case and whitespace for comparison; use the family name of the first author where available.
- Year: parse a four-digit publication year where available. A missing or non-four-digit year remains blank.
- URLs and original citation text are preserved in the master record; URL normalization is not used to declare a duplicate.
- Source database names, query identifiers, and source export file paths are never discarded during deduplication.

## Matching hierarchy

Rules are evaluated in order:

1. Exact normalized DOI match is a confirmed duplicate with high confidence.
2. Exact normalized title plus compatible publication year is a duplicate candidate. Compatible years allow the same year or a documented version difference; this phase does not silently resolve versions from title and year alone.
3. Strong normalized title similarity with overlapping first author and compatible year is a duplicate candidate only.
4. A likely preprint and peer-reviewed version is a candidate pair. The peer-reviewed version can be retained and the preprint classified under E2 only after the protocol's version-resolution rule is verified in a later screening/adjudication phase.

Fuzzy title similarity alone never removes or merges a record. Pending candidates remain in master_unique_records.csv until reviewed. Confirmed duplicate rows are recorded in duplicate_groups_confirmed.csv; candidate pairs are recorded in duplicate_candidates_for_review.csv.

## Current W2 input condition

The W2 search log contains no exported records (records_exported=0 in all rows). The raw directory contains screenshot PNGs only and no supported machine-readable bibliographic export. Therefore no parser rows, duplicate groups, candidate pairs, or unique master records could be created in C3. This is a data-availability result, not a scientific inclusion or exclusion decision.
