# Revision-stage search archive (30 September 2026)

Raw material of the partial search rerun documented in `data/revision_stage_*`. Paths such as
`01_protocol/...`, `02_search_exports/...`, `03_search_logs/...`, `04_dedup/...` and `05_screening/...` that appear in the
logs are relative to this folder.

- `01_protocol/protocol_frozen.md` — the protocol frozen before the rerun.
- `02_search_exports/` — raw result screenshots, access-error records and machine-readable exports (ScienceDirect and IEEE Xplore).
- `03_search_logs/`, `04_dedup/`, `05_screening/` — search, deduplication and screening logs.

Scope: records could be captured from two of the seven databases and full texts could not be retrieved, so the rerun
is not reported as a screening flow in the article and did not change the corpus. It does not reconstruct the original
(July 2026) search, whose database-level counts were not retained.

Correction: files in this archive that give the corpus reconciliation as "67 − 2 + 1 − 1 (ref94) = 66" are superseded
by `data/revision_stage_flow_counts.*`: ref94 was a candidate outside the 67-source baseline and was never added, so the
correct reconciliation is 67 − 2 + 1 = 66. The archive is otherwise kept unchanged.
