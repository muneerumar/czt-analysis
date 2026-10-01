# Cognitive Zero Trust (CZT) — analysis code and data

Code and data for the article *Cognitive Zero Trust: A Human-Centered Framework for Verifying Communication
Requests in GenAI-Enabled Social Engineering* (submitted to *Computer Standards & Interfaces*).

The article is a conceptual framework. This repository supports three kinds of evidence in it, and nothing more:

| Evidence in the article | Files here | What it can and cannot show |
|---|---|---|
| Descriptive mapping of the 66-source literature corpus (Figs. 2, 4–7) | `data/literature_coding_matrix.csv`, `data/coding_codebook.md` | What the corpus covers; not prevalence or effect sizes |
| Analytical illustration of the decision model (Figs. 12–13) on 60 written vignettes | `data/scenario_vignettes.csv`, `data/scoring_rubric.csv`, `data/decision_parameters.csv`, `data/scenario_results.csv`, `data/sensitivity_summary.csv` | Internal consistency and parameter sensitivity of Eqs. (1)–(7); **not** detection accuracy or real-world effectiveness |
| Monte Carlo simulation study (Section 6.6, Fig. 14; global-sensitivity figure supplementary) | `sim/model.py`, `sim/parameters.json`, `sim/results/` | Relative behavior of CZT, zero trust alone, awareness training and a uniform callback policy under explicit, mostly assumed parameters; not real-world effectiveness |
| Analytical latency and overhead model (Figs. 15–17) | `data/analytical_assumptions.csv` | Order-of-magnitude feasibility under stated assumptions; not production benchmarks |

It also contains the documented-incident cross-check (`data/documented_incident_mapping.csv`), the TikZ sources of the
conceptual figures, and, for transparency, the logs of a partial revision-stage search rerun (`data/revision_stage_*`).
That rerun could capture records from only two of the seven databases and could not retrieve full texts, so it is not
reported as a screening flow in the article and did not change the corpus.

File names follow the figure order of an earlier draft. Article figure numbers: files 01–06 = Figs. 1–6; 08 = Fig. 7;
09–14 = Figs. 8–13; 18 = Fig. 14; 15–17 = Figs. 15–17. Files 07 (source types) and 19 (simulation global sensitivity)
are supplementary.

## Reproduce the numbers and figures
    pip install -r requirements.txt
    python tools/build_coding_matrix.py   # rebuilds the coded corpus from the authoritative input
    python generate_figures.py            # regenerates figures/ and data/derived_numbers.txt
    python sim/run_simulation.py          # Monte Carlo study: sim/results/ and figures/Figure_18-19 (about 15 s)
    python tools/reliability/agreement.py # second-coder agreement statistics (Section 3.4)
    python -m pytest -q                   # independent checks, full reproduction test, simulation tests

Conceptual figures (1, 3, 8, 9, 11) are compiled separately from `figure_sources/*.tex` (LaTeX standalone + TikZ).

`data/derived_numbers.txt` lists the corpus, scenario and timing numbers quoted in the article; `sim/results/simulation_numbers.txt` lists the simulation numbers. The test suite re-implements the decision rule
(Eq. 4, including the authority floor) and veto rules (V1–V4) independently and checks them against `data/scenario_results.csv`, then reruns the
whole pipeline and checks that it reproduces the released outputs exactly. Decision scores are rounded before
comparison so that boundary cases follow the declared inequalities on every platform.

## Monte Carlo simulation
`sim/model.py` generates organizational request streams (legitimate routine and high-consequence requests, and deceptive
requests from adversary classes A1–A5 of the threat model) and applies each defense configuration to the same stream
(common random numbers). CZT decides on noisy, incomplete and partly poisoned evidence with Eqs. (1)–(4), vetoes V1–V4, the authority floor,
and threshold recalibration on incident and interruption rates (Eq. 6; model-based proxies using class labels); ablations remove one construct at a time. `sim/parameters.json` gives each
uncertain parameter with its range and basis; most are assumptions and are varied jointly in a Latin-hypercube sensitivity
analysis. The simulated cost counts realized outcomes (executed deceptive requests and weighted interruption of legitimate
requests), not the routing surrogate of Eq. (7). The simulation encodes the logic it evaluates, so it shows behavior under
assumptions, not effectiveness.

Structural choices that are fixed rather than varied: the class-specific input distributions and the attack mix
(`generate`); consequence, urgency, secrecy, irreversibility and protected-action flags are observed without error
(only provenance, context, authority, channel and novelty are noisy, `observe`); only CZT has vetoes, the authority floor
and dual approval; and A5 is a request-attribute abstraction, not an agent-runtime or memory-propagation experiment.
The 95% intervals are Monte Carlo intervals under these fixed assumptions.

## Data dictionary (main files)
- `literature_coding_matrix.csv` — one row per source: bibliographic attributes, seven ordinal codes (0/1/2), the justification for each code, and audit traceability columns.
- `scenario_vignettes.csv` — 60 vignettes (10 per sector; 30 legitimate, 30 deceptive; 19 agent-mediated) with rubric scores and request flags. Ground truth and scores were set by the authors.
- `scoring_rubric.csv` — anchor text for every score level.
- `second_coder_codes.csv`, `second_coder_agreement_report.md`, `second_coder_resolution_log.csv` — independent second coding of a 21-source stratified sample (first vs. second coder), agreement statistics, and how the eight disagreements were resolved.
- `decision_parameters.csv` — weights, thresholds and analysis settings, with the basis for each value.
- `scenario_results.csv` — computed A(r), R(r), veto rule, decision, and weight-perturbation stability per vignette.
- `sensitivity_summary.csv` — misses, legitimate-request escalations and cost over the threshold grid.
- `second_coder_resolution_log.csv` also records a post-hoc rationale for each of the eight resolved disagreements, written during revision from the codebook and the source (not a contemporaneous coder note).

## Search archive and reliability tools
- `search_archive/` — protocol, raw captures, and search, deduplication and screening logs of the partial revision-stage rerun (see its README).
- `tools/reliability/` — `build_kit.py` (draws the stratified 21-source sample, seed 2026; keys in `sample_keys.csv`), `agreement.py` (recomputes the agreement statistics), and `analyze_reliability.py` (reads the coder and rater workbooks of the reliability kit).
- The source descriptions inside `data/second_coder_workbook.xlsx` are the coder's working copy and predate eight bibliographic corrections made later in `references.bib`.

## Limitations
The vignettes and their labels are author-constructed; agreement between the model and the labels demonstrates the
internal consistency of the decision rule, not its accuracy. All weights and thresholds are illustrative and are
examined in the sensitivity analysis. No empirical validation is claimed.

## AI assistance
AI tools (Claude by Anthropic; ChatGPT, ChatGPT Work, Codex and Prism by OpenAI) assisted with drafting code, data
files and documentation. The authors reviewed the outputs and are responsible for them; see the article's declaration.

## License
Code: MIT (`LICENSE`). Data and figures: CC BY 4.0 (`LICENSE-DATA.md`). Please cite using `CITATION.cff`.
