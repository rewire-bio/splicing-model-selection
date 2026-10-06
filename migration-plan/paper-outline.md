# LaTeX manuscript outline

Target: `paper/main.tex` and `paper/references.bib`, which the engineer and writer will implement.
This outline is a plan only. It contains no new results. Every number comes from an entry in
`migration-plan/evidence-map.json`, cited below by its ID in square brackets.

## Build modes (keep them separate)

| Mode | Numbers from | Label on every page or footnote | When allowed |
|---|---|---|---|
| `imported` | Imported reference values: the evidence map, converted to `evidence/claims.json` and then to `paper/generated/macros.tex` | "Values imported from the 2026-09-30 companion run; not reproduced under this repository's harness" | Now. Compiling is not verification |
| `reproduced` | `results/full/results.json` after the Tier 1 run approved by the protocol | "Reproduced on <platform>, <date>; outcome class: <protocol §11>" | Only after approval and a run. Each mismatch is shown, not hidden |

Generated macros replace hand-typed numbers. Tables are generated from JSON. In `reproduced` mode,
Figures 4 and 5 are regenerated from `metrics.json`; in `imported` mode, the imported SVGs are
converted.

## Title, authorship and disclosure

- Working title: *Choosing a splicing score for a fixed minigene budget: an exploratory comparison
  of a supervised baseline, SpliceAI and Pangolin on MFASS.*
- The author list is for the owner to decide. Do not add personal details beyond what the owner
  supplies.
- Disclosure paragraph, kept from the original:
  - the benchmark project's own study and code;
  - AI agents (Claude, Codex) ran commands and drafted text;
  - all review so far is automated;
  - there has been no independent human scientific review [U-HUMAN-REVIEW].

## Abstract (about 200 words)

- Problem: rank SNVs for a fixed number of minigene assays.
- Data: MFASS held-out arm. 8,297 common variants, 314 disrupting, 460 groups [C-POP].
- Result at k = 100: `kmer_cons` 0.61; specialists 0.63 to 0.657. No paired difference established
  (this is not equivalence) [T2, T3, I-MAIN].
- Whole-list result: Pangolin has higher AP and AUROC [T3]. At k = 300 its intervals exclude zero, but
  300 is a post hoc budget [I-P300].
- Status: exploratory and unadjusted. The specialists are a saved-score replay. The endpoint is
  minigene exon recognition only.

## 1. Introduction

- A budgeted assay calls for precision at k, not a score threshold. Thresholds vary between settings
  [L-THRESH, L-CLINGEN].
- Contribution: a P@k comparison on one common population, with tie ranges, whole-group paired
  intervals and a documented assembly-orientation failure mode. Also a reproducible companion.
- Scope statement. The comparison is between workflows, not architectures. The held-out outcomes had
  been inspected before.

## 2. Background

- 2.1 The MFASS assay and its disruption definition [L-MFASS]. Figure 1 is optional: Cheng et al.
  Fig. 2e, CC BY 4.0, embedded or cited [U-FIG-REUSE].
- 2.2 SpliceAI and Pangolin, and what the mask settings mean [L-MASKDEF]. Background masking and
  annotation effects [L-MASKFIG]; Figure 3 is optional.
- 2.3 Related benchmarks: Smith and Kitzman 2023, CAGI5 and MMSplice [L-THRESH, L-CAGI5].

## 3. Data

- 3.1 Cohort and split.
  - Build counts [C-BUILD].
  - `split-v2`: whole exon and gene groups; no gene crosses arms.
  - The legacy `sequence` column is reverse-complemented in 7,770 rows [C-BUILD].
- 3.2 Common population and exclusions.
  - Population [C-POP, C-EXCL]. The orientation defect also affects the cohort and training arm
    [C-EXCL-TRAIN].
  - Three worked QC examples [C-CHECKVAR].
  - Table: the population and its exclusions.
- 3.3 Provenance and licences. Pinned revisions and digests are listed as in protocol §4. MFASS has
  no licence, so its tables are not redistributed [U-LIC-MFASS].

## 4. Methods

- 4.1 Configurations, as in protocol §5. This section defines the three evidence types: computed or
  fitted, saved-score replay, and not-run inference.
- 4.2 Controls and baselines.
  - Features, published settings and the validation grid [C-HP-SEL].
  - The refit reproduces the published baseline exactly [C-KMER-BYTE].
- 4.3 Specialist replay. Annotation-matched conditions (GENCODE 44 canonical, distance 50) and the
  per-gene mask patch. The replay matches the study's metrics [C-REPLAY]. GTF canonical count
  [C-GTF].
- 4.4 Metrics.
  - P@k as the expected value over tie orders, its [min, max] range, and the registered tie order.
    Include `budget_precision` in the appendix.
  - AP (non-interpolated) and AUROC.
- 4.5 Statistics.
  - Paired whole-group bootstrap: 2,000 draws, seed 20260914, keeping the review fraction. Report the
    realised depths [C-DEPTH].
  - Interval inventory and the absence of multiplicity adjustment [C-COUNTS-INTERVALS].
  - "Excludes zero" is not "established improvement". The protocol's improvement rule is not applied.
- 4.6 Pre-specified versus post hoc. Only k = 100 was fixed in advance. k = 25 and k = 300 are post
  hoc, and so are the bands and the selected-baseline run.

## 5. Results

- 5.1 Budget 100 (Table `tab:b100`) [T2] and resources (`sec:resources`) [T2-RES].
- 5.2 Paired contrasts against the historical baseline (Table `tab:contrasts-hist`, Figure
  `fig:forest`) [T3].
- 5.3 Sensitivity analysis against the validation-selected baseline (Table `tab:contrasts-sel`) [T4].
- 5.4 Specialist-versus-specialist contrasts from the matched study (Table `tab:specialist-pairs`).
  These values are reported, not recomputed [M-STUDY]. Three cells are incomplete until the values
  are transcribed [U-MSTUDY-MISSING].
- 5.5 Budget dependence (Figure `fig:budget`, Table `tab:budgets`) [F4, T5].
- 5.6 Ties and shortlist overlap [C-TIES, C-OVERLAP]. Case variants [C-CASES] are presented only as
  "imported, unverified" until U-CASE-IDS is resolved.
- 5.7 Junction-distance bands (Table `tab:bands`) [T6]. No band intervals were computed.
- 5.8 Reproduction status. In `imported` mode this is a placeholder box: "Not yet reproduced under
  this repository's harness." In `reproduced` mode it shows the protocol §11 class and a table of
  R1 to R8 with pass, fail or discrepancy.

## 6. Discussion

- Decision guidance by label availability and budget fraction. The flowchart is Figure 6 (D2 source
  [A_fig_flow]). Each terminal cites a table, and untested fractions end at "not tested" [I-MAIN,
  I-P300].
- Budgets are fractions of this one list (1.2%, 3.6% and 0.3% of 8,297, at 3.8% prevalence). They are
  not thresholds for other lists.
- What would change the recommendation: a prospectively registered cohort, a Pangolin-versus-SpliceAI
  test without labels, or an author-confirmed liftover fix.

## 7. Limitations

These are carried over in full from the article's "Limits and failure cases":
- coverage;
- assembly [U-MFASS-CONFIRM, U-TRAIN-DEFECT];
- ties;
- exploratory status and post hoc budgets;
- reporter versus patient (13 of 19 confirmed; CAGI5) [L-MFASS, L-CAGI5];
- labels and replay;
- review.

Also include:
- overlap not audited [U-OVERLAP];
- Monte Carlo error not quantified [U-MC-ERROR];
- specialist inference not rerun [U-TIER2];
- platform scope [U-PLATFORM].

## 8. Data and code availability

- The repository URL is a placeholder [U-REPO-URL].
- The companion and the outputs zip have digests, and the outputs zip contents are described.
- The companion licence is pending [U-LIC-COMPANION]. Tool licences are listed [U-LIC-SPLICEAI].

## Appendix

- A. Exact Tier 1 commands (protocol §6.2), with the recorded runtimes from the 2026-09-30 receipt.
- B. Tier 2 route (not executed): the steps and recorded scoring times.
- C. The `budget_precision` code listing, verbatim from the companion.

## Bibliography (`references.bib`), preserving the original's 13 Sources entries

| Key | Work | Identifier |
|---|---|---|
| `chong2019mfass` | Chong R, Insigne KD, Yao D, et al. *Mol Cell* 2019;73(1):183–194.e8 | PMC6599603 |
| `kosurilab_mfass` | KosuriLab MFASS repository @ `9a8e4f2`; issue 1 | GitHub |
| `jaganathan2019spliceai` | Jaganathan K, et al. *Cell* 2019;176(3):535–548.e24 | doi:10.1016/j.cell.2018.12.015 |
| `spliceai_repo` | Illumina/SpliceAI @ `03f4243`, LICENSE, PyPI 1.3.1 metadata | GitHub/PyPI |
| `zeng2022pangolin` | Zeng T, Li YI. *Genome Biol* 2022;23:103 | PMC9022248 |
| `pangolin_repo` | tkzeng/Pangolin @ `5cf94b8`, LICENSE, issue 29 | GitHub |
| `smith2023benchmarking` | Smith C, Kitzman JO. *Genome Biol* 2023;24:294 | PMC10734170 |
| `cheng2019mmsplice` | Cheng J, Nguyen TYD, Cygan KJ, et al. *Genome Biol* 2019;20:48 | PMC6396468 |
| `mount2019cagi5` | Mount SM, Avsec Ž, Carmel L, et al. *Hum Mutat* 2019;40(9):1215–1224 | PMC6744318 |
| `walker2023clingen` | Walker LC, et al. *Am J Hum Genet* 2023;110(7):1046–1067 | PMC10357475 |
| `gencode44` | GENCODE Human release 44 (GRCh38.p14) | gencodegenes.org |
| `sklearn_ap` | scikit-learn `average_precision_score` (v1.9.1); Astral uv | scikit-learn.org; docs.astral.sh |
| `rewirebench_093fd1a` | rewire-benchmarks @ `093fd1a`: MFASS README, matched-study README, report, manifest, automated review | GitHub |
| `rewirebench_4be7a98` | rewire-benchmarks @ `4be7a98`: specialist comparison protocol, exclusions addendum | GitHub |

The URLs are exactly as in `article/original.md` "Sources and artifacts". The original's citation
review date is 2026-09-30, and the sources were not re-retrieved during migration. Record retrieval
dates in `literature/sources.json`.

## Scaffold items the manuscript build depends on (see `scaffold-replacement.md`)

These scaffold items must be in place before the build works:
- `scripts/build_paper.py` must generate macros and tables from JSON in both modes;
- `evidence/claims.json` must be populated from this map;
- `literature/sources.json` must be populated;
- `paper/references.bib` must be filled.
