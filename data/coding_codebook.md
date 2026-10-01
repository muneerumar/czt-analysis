# Coding codebook: Cognitive Zero Trust literature corpus

Unit of analysis: one unique source in the final 66-source matrix; source keys and verified metadata are maintained in `references.bib` (revision-stage audit last updated 30 September 2026).
Each source is coded individually. The column `coding_justification` records the feature of the source that each non-zero code rests on.

## Bibliographic attributes

| Field | Values | Rule |
|---|---|---|
| `year` | publication year | Year of the version cited. |
| `source_type` | Journal article; Conference paper; Preprint; Standard/report; Book/chapter | Venue of the cited version. |
| `evidence_basis` | Peer-reviewed empirical; Peer-reviewed review; Peer-reviewed conceptual; Standard/guidance; Industry report; Preprint; Book/chapter | Light quality appraisal: the kind of evidence the source offers. Preprints and industry reports are used for threat description only, never as sole support for a construct. |
| `research_stream` | Zero trust architecture; Adaptive/cognitive zero trust; Human factors & social engineering; GenAI & synthetic deception; AI/LLM security & governance | One primary stream: the stream the source mainly contributes to. |
| `modalities` | Email/chat/web; Voice/video; LLM/AI application; Access/workflow; Not modality-specific | Multi-label: every modality the source substantively addresses. |

## Verification dimensions (ordinal 0/1/2)

**Scope.** These codes record how far each source covers the *related concepts* from which the CZT constructs were
derived. They are deliberately broader than the construct definitions in the article's construct dictionary (Table 7):
`feedback` includes logging and monitoring, `authority` includes authority used as a manipulation cue, and `friction`
includes warnings and the cost of security steps in general. Figure 4 therefore shows coverage of these related
concepts, not coverage of the exact CZT constructs.

| Code | Meaning |
|---|---|
| 0 | Absent or incidental mention. |
| 1 | Substantive discussion, but not operationalized as a control or measured. |
| 2 | Central theoretical treatment, an explicit control, or an evaluated mechanism. |

Ambiguous cases take the lower code.

| Dimension | Coded as present when the source treats… |
|---|---|
| `provenance` | the verifiable origin or authenticity of a message, document, or media item (sender authentication, signatures, content credentials, synthetic-media detection). Device or user identity alone is not provenance. |
| `context` | whether a request fits role, workflow, timing, or record; includes context-aware or risk-adaptive access policy. |
| `authority` | whether the requester is entitled to request the action (delegation, authorization scope, instruction authority), or authority as a manipulation cue. |
| `channel` | the integrity or appropriateness of the communication channel (managed vs. personal channels, channel switching, injection routes, secured transport). |
| `friction` | deliberate verification steps or costs (step-up, out-of-band confirmation, dual control, warnings, or the cost of security steps to users). |
| `challenge` | protected human challenge: permission and safety to pause, question, or escalate; blame culture; organizational support for users. |
| `feedback` | accountability feedback: logging, monitoring, incident or near-miss learning, continual improvement of policy. |

## Procedure

Codes were recorded in `literature_coding_matrix.csv`. The previously released matrix assigned codes by research stream; this revision replaces it with source-level codes. The authors' coding and verification procedure, number of coders, and agreement statistics are reported in Section 3.4 of the manuscript.
