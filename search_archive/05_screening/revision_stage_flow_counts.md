# Prospective revision-stage screening flow counts

This is a prospective repair and screening flow for the missing W2 record collection. It is not a reconstruction of the July historical search. The original W2 search log and screenshots remain unchanged; this flow counts only machine-readable records recovered during the 2026-09-30 repair.

| Stage | Count | Definition |
|---|---:|---|
| Database records exported | 740 | Repaired ScienceDirect and partial IEEE Xplore result rows captured as machine-readable metadata (490 ScienceDirect + 250 IEEE Xplore). |
| Duplicates removed | 7 | Exact normalized publisher accession duplicates across repaired query captures. |
| Unique records title/abstract screened | 733 | Unique repaired records. ScienceDirect abstract fields were blank; IEEE fields were limited to truncated result snippets where present. |
| Title/abstract exclusions: E1 | 0 | Promotional/commercial exclusion. |
| Title/abstract exclusions: E2 | 1 | Correction/version record excluded at title stage. |
| Title/abstract exclusions: E3 | 3 | Retracted record excluded at title stage. |
| Title/abstract exclusions: E4 | 153 | Clearly outside every stated evidence domain at title stage. |
| Full texts sought | 576 | All plausible records retained conservatively because the abstract was missing. |
| Full texts unavailable | 576 | No complete full text was obtained for the retained repaired batch; no substantive exclusion was inferred. |
| Full texts assessed | 0 | Complete texts assessed against E1-E4. |
| Full-text exclusions: E1 | 0 | None; full-text exclusions file is empty. |
| Full-text exclusions: E2 | 0 | None; full-text exclusions file is empty. |
| Full-text exclusions: E3 | 0 | None; full-text exclusions file is empty. |
| Full-text exclusions: E4 | 0 | None; full-text exclusions file is empty. |
| Final eligible repaired records | 0 | No repaired record reached substantive full-text eligibility assessment. |
| New eligible sources relative to old coded corpus | 2 | ref94 and ref95 are peer-reviewed revision-stage candidates documented outside the repaired database export; author approval is still required before any corpus change. |

## Access limitation

ScienceDirect reported 10,746 Q3 hits, but the repaired browser capture recovered only the first 200 result cards before subsequent offset requests returned an access error. IEEE Xplore contributed 100 Q1 records, 100 Q2 records, and all 50 Q3 records from its visible public result interface; the first two IEEE queries reported 1,148 and 855 hits, so those captures are partial. Hit counts are not treated as exported-record counts, and no inaccessible records were invented.

No inter-rater reliability was calculated. The screening is an AI-assisted audit workflow, not independent human validation; the authors remain responsible for final inclusion and classification decisions.

## Resolved pending decision groups

The six separately logged W4 reassessment rows (ref51, ref52, ref53, ref53-arxiv, ref94, and ref95) are outside the 733-record repaired-export denominator above. Their resolved decisions are: ref51 and ref52 excluded under E4; the preferred ref53 workshop version included and ref53-arxiv excluded under E2; and ref94 and ref95 included. These rows are recorded in `06_corpus_update/w4_pending_decision_table.csv` and in the completed screening log.
