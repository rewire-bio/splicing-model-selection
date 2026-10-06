# Splicing scores for a fixed minigene budget: computational reproduction protocol

Status: UNAPPROVED (draft v1, prepared 2026-10-06 by the research-designer role, model `claude-opus-5-5`).
No part of this protocol has been executed. It has not been approved by the owner, and it does not
say that any original result has been harness-verified or independently reproduced.

This protocol migrates an existing study and adds no new experiment. Its scope is a **computational
reproduction** of the analyses behind the article "Choosing a Splicing Score for a Fixed Minigene
Budget: Baseline, SpliceAI and Pangolin on MFASS" (`article/original.md`, 2026-09-30). The runnable
companion is in `companion/`. Imported provenance is in `evidence/import-manifest.json` (source
`rewire-bio/rewire.it` at `a2ba98c1463162cc91a6376fcdfc71e0023f0703`, issue 339).

## 1. Research question (unchanged from the original)

Suppose you can afford k minigene splicing experiments on a list of human SNVs. Which scoring
configuration should rank the list? The candidates are a supervised baseline trained on assay
labels, or SpliceAI or Pangolin with masking off or on. The question is answered on the MFASS
held-out arm, within the original measured scope.

This protocol asks a narrower **reproduction question**: does a fresh, resource-bounded rerun of the
companion workflow reproduce the recorded measurements within the tolerances declared in section 8?

## 2. Contribution and what this protocol does not add

- **Original contribution (imported, exploratory):** a budget-based comparison (P@k) of the
  historical MFASS-v2 k-mer baseline, a validation-selected variant and simple controls against four
  annotation-matched specialist configurations, evaluated on one common population of 8,297
  variants. It reports tie-order ranges, whole-group paired bootstrap intervals, a junction-distance
  breakdown, a documented assembly-orientation exclusion class and a decision flowchart.
- **Migration contribution:** a reproduction protocol with fixed commands, tolerances, budgets and
  stopping rules; an evidence map that ties every manuscript number to its source file; a LaTeX
  manuscript outline; and an outline for an accessible blog post.
- **Not added:** new endpoints, budgets, comparators, datasets, seeds or hyperparameters, new
  specialist inference, and any confirmatory scientific claim.

## 3. Hypotheses and estimands

### 3.1 Scientific estimands (imported; exploratory only, not re-tested here)

All of these were measured on the common population (N = 8,297; 314 disrupting; 460 groups):

- E1. P@k (expected over tie orders, with [min, max] over tie orders, plus the registered-tie-order
  value) for every configuration at k in {25, 100, 300} and along the budget curve
  k in {10, 25, 50, 100, 150, 200, 300, 400, 600, 800}.
- E2. AP (non-interpolated, `sklearn.metrics.average_precision_score`) and AUROC for every
  configuration.
- E3. Paired differences (candidate minus baseline) in P@k, AP and AUROC for S0, S1, P0 and P1:
  - against `kmer_cons` at k = 25, 100 and 300;
  - against `kmer_cons_selected` at k = 100.

  Each difference is reported as the observed value with a 95% percentile interval from 2,000
  whole-group bootstrap draws, seed 20260914.
- E4. The junction-distance band breakdown: hits in the top k, and AUROC within each band.
- E5. Population accounting: 8,324 held-out variants, 8,297 common, 27 exclusions (23 assembly
  orientation, 4 outside the canonical transcript span).

**Status of E1 to E5:** exploratory and unadjusted. The held-out outcomes had been inspected in
earlier work. Only k = 100 was fixed in advance; k = 25 and k = 300 are **post hoc**. The improvement
rule in the rewire-benchmarks protocol (a P@100 gain ≥ 0.05 with a paired lower bound > 0) applies
only to a future, prospectively registered cohort, so it is not applied here. This protocol must not
promote any E1 to E5 result to confirmatory status.

### 3.2 Reproduction hypotheses (confirmatory for the computation only)

Each hypothesis is fixed before execution. A pass means the computation reproduced. It does not
mean the science was validated.

- R1 (inputs): all 14 pinned files from `fetch` match their recorded SHA-256. The GENCODE 44 GTF
  matches MD5 `b182a9f3b134b9cc2da566a2b1692557`.
- R2 (cohort): `build` prints 27,733 eligible, 1,050 disrupting, 2,198 exons, 7,770 reverse-complemented
  legacy sequences, train 19,409 / 735 / 1,127 groups and test 8,324 / 315 / 463 groups.
- R3 (control refit): `runs/controls/kmer_cons.predictions.tsv` matches the published
  `baseline-kmer-position-v2.predictions.tsv` (max |Δ| < 1e-9, which is the companion test). It should
  also be byte-identical (SHA-256 prefix `2f3117c2`). Validation selection chooses (0.06, 15) for
  `kmer_assay` and (0.1, 15) for `kmer_cons`.
- R4 (replay): for S0, S1, P0 and P1, AP and AUROC equal the matched-study JSON values within
  absolute 1e-12, and the registered-tie-order P@100 equals the study's `precision_at_capacity`
  exactly.
- R5 (population): {held_out 8324, common_scored 8297, positives 314, groups 460, excluded 27}, with
  23 orientation and 4 span exclusions.
- R6 (metrics and intervals): every number in Tables 2 to 6 of the article, and in Figures 4 and 5,
  that is regenerated from `metrics.json` or `decision-table.md` matches within section 8 tolerances.
- R7 (determinism): `decision-table.md`, `shortlist.csv`, `excluded.csv` and the six control
  `*.predictions.tsv` files are byte-identical to the imported reference copies in
  `downloads/splice-shortlist-outputs.zip`. This applies on macOS arm64 only (section 8.3).
- R8 (tests): `pytest -q` in the companion working copy reports 26 passed and 0 failed.

## 4. Data, provenance and licences

The repository redistributes no data. All data are fetched at run time into a git-ignored scratch
directory and checked against the pinned digests.

| Input | Source (pinned) | Size | Integrity | Licence / terms | Redistribution |
|---|---|---:|---|---|---|
| `snv_data_clean.txt`, `snv_func_annot.txt` (MFASS) | KosuriLab/MFASS @ `9a8e4f27106be52aeb11acad27f95f5cded663a8`, `processed_data/snv/` | ~80 MB | SHA-256 in `PINNED` (`companion/splice_shortlist.py`) | **No licence declared** | Not redistributed; fetched only |
| `split-v2.tsv` | rewire-benchmarks @ `093fd1ae198c80ce34408d84d6543bca4fc538f2` | <2 MB total with the next three rows | SHA-256 pinned | MIT (rewire-benchmarks) | Fetched |
| `baseline-kmer-position-v2.predictions.tsv` | as above | (incl.) | SHA-256 `2f3117c2…` | MIT | Fetched |
| S0/S1/P0/P1 `*.predictions.tsv`, `*.json`; S0/P0 `*.unscored.tsv` | as above, `results/matched-annotation-v1/` | (incl.) | SHA-256 pinned | MIT for the files. They are model outputs; the model terms are noted below | Fetched |
| GENCODE 44 primary-assembly GTF | ftp.ebi.ac.uk, release_44 | ~50 MB | MD5 `b182a9f3…2557` | GENCODE/Ensembl open data | Fetched (optional `annotation` step) |
| GRCh38 windows for `check-variant` | api.genome.ucsc.edu (`hg38`) | negligible | none (live API) | UCSC public API | Only the public GRCh38 base is printed |
| Imported reference outputs | `downloads/splice-shortlist-outputs.zip` (SHA-256 `6d1f0de2…`) | small | import manifest | Contains per-variant scores, MFASS outcome labels, gene names and GRCh38 positions; no MFASS source tables, alleles or sequences | Already in repository (owner decision to retain) |

Tool licences matter only to the out-of-scope specialist route (section 6.3):
- Pangolin `5cf94b8` is GPL-3.0. The per-gene mask patch is also GPL-3.0.
- SpliceAI terms are ambiguous. At `03f4243` the repository licenses code under PolyForm Strict 1.0.0
  and models under CC BY-NC 4.0 (changed July 2025). The PyPI 1.3.1 metadata says GPLv3.
- The licence for the companion code itself is **unset**: `companion/NOTICE.md` says "to be set at
  publication". This is listed as unresolved in `migration-plan/evidence-map.json`.

Record every fetched file in `data/manifest.json`, which the engineer populates. Each entry needs a
stable URL, a git-ignored local path, the SHA-256 and the licence string. MFASS entries use
`"none declared; not redistributed"`. Record the retrieval date in the run receipt.

## 5. Configurations, controls and baselines (fixed; identical to the original)

| Name | Role | Scores from |
|---|---|---|
| `prevalence` | Null control (no information) | Computed (training prevalence 0.038) |
| `distance` | Fixed-rule control (negative distance to nearest construct junction) | Computed (no fitting) |
| `kmer_assay` | Supervised baseline without conservation; published settings (lr 0.06, 31 leaves) | Fitted on 19,409 training variants / 1,127 groups |
| `kmer_cons` | **Historical MFASS-v2 baseline; default contrast reference** | Fitted, published settings |
| `kmer_assay_selected`, `kmer_cons_selected` | Sensitivity baselines; grid lr {0.03, 0.06, 0.1} × leaves {15, 31} on a 25% group-held-out training part | Fitted |
| `S0`/`S1` | SpliceAI 1.3.1, GENCODE 44 canonical, mask 0/1, distance 50 | **Saved-score replay** |
| `P0`/`P1` | Pangolin `5cf94b8` + per-gene mask patch, GENCODE 44 canonical, mask False/True, distance 50 | **Saved-score replay** |

The protocol keeps three kinds of evidence separate throughout. **Computed or fitted here** means
the reproduction regenerates the scores. **Saved-score replay** means the reproduction only
re-evaluates the published per-variant predictions. **Specialist inference** means rerunning
SpliceAI or Pangolin; it is not part of this protocol. A replay that passes is not evidence that the
specialist tools reproduce.

## 6. Procedure

### 6.1 Working-copy rule

`companion/` is a frozen input. The companion writes `data/`, `runs/` and `out*/` next to its own
script, so the harness must first copy the six companion files into a fresh, git-ignored working
directory. Do not run the companion in place:

```
results/full/work/splice-shortlist/   # copy of companion/{splice_shortlist.py,test_splice_shortlist.py,pyproject.toml,uv.lock,README.md,NOTICE.md}
```

Before running, verify that each copied file's SHA-256 matches `evidence/import-manifest.json`.

### 6.2 Tier 1: harness reproduction (the only tier this protocol asks to approve)

Environment: `OMP_NUM_THREADS=4`, `OPENBLAS_NUM_THREADS=4`, `MKL_NUM_THREADS=4`,
`VECLIB_MAXIMUM_THREADS=4`, uv ≥ 0.8 (reference uv 0.8.2) and Python 3.11 from `uv.lock`. Run on a
local CPU only.

Run these commands in order from `results/full/work/splice-shortlist/`. Each command uses a fresh
uv cache under the scratch directory, and each line is logged with its exit code, wall time and peak
RSS:

```bash
uv sync --frozen
uv run --frozen python splice_shortlist.py fetch
uv run --frozen python splice_shortlist.py build
uv run --frozen python splice_shortlist.py controls
uv run --frozen python splice_shortlist.py annotation
uv run --frozen python splice_shortlist.py check-variant ENSE00000712808_003   # DDX1, PASS example
uv run --frozen python splice_shortlist.py check-variant ENSE00001321140_001   # CYFIP1, orientation exclusion
uv run --frozen python splice_shortlist.py check-variant ENSE00002361772_001   # ARHGEF3, span exclusion
uv run --frozen python splice_shortlist.py evaluate --tutorial --budget 20 --draws 200 --method P0 --out out-tutorial
uv run --frozen python splice_shortlist.py evaluate --budget 100 --method P0 --out out
uv run --frozen python splice_shortlist.py evaluate --budget 300 --method kmer_cons --out out-b300
uv run --frozen python splice_shortlist.py evaluate --budget 25 --method S1 --out out-b25
uv run --frozen python splice_shortlist.py evaluate --budget 100 --baseline kmer_cons_selected --method kmer_cons_selected --out out-selected-b100
uv run --frozen pytest -q
```

The original clean run also ran two more `check-variant` calls (IPO9 and COL1A2). Their IDs are not
given in the imported article or README, and the article does not show their console output.
They are **excluded** from Tier 1 rather than guessed. See the evidence map for the unresolved items.

The `evaluate --budget 60 --method P1` command in the article is marked "not executed" there. It
stays out of scope.

Next, the harness writes `results/full/results.json`. It is a structured extraction of the five
`metrics.json` files, the controls `receipt.json`, the fetch receipt, the per-command receipts and
the SHA-256 of every output file. `scripts/analyse.py` then compares `results.json` against the
reference values in `migration-plan/evidence-map.json`, which the engineer converts into
`evidence/claims.json`. The reference outputs in the imported outputs zip are compared under
section 8.

### 6.3 Tier 2: full specialist inference (documented; not requested; outside budget)

The route is rewire-benchmarks `093fd1a`, `results/matched-annotation-v1/README.md#reproduction`:
- GENCODE 44 FASTA (845 MB) and GTF (50 MB);
- the patched Pangolin `5cf94b8`;
- SpliceAI 1.3.1 with TensorFlow 2.21.0;
- torch 2.2.2;
- `run_matched_study.sh MANIFEST ENV_FILE`.

The recorded scoring times on an Apple M4 were S0 6,921 s, S1 6,102 s, P0 19,153 s and P1
18,655 s: 50,831 s (about 14.1 h) of summed scoring at 5 or 6 threads, before cohort preparation.
At a 4-thread cap, assume at least 14 h and perhaps around 18 to 21 h. This figure is extrapolated,
not measured. Downloads alone come to about 1.4 GB before installed environments, so the 2 GB
additional-disk budget would very likely be exceeded. The SpliceAI licence terms are also
unresolved. **Tier 2 must not run under this protocol.** Running it requires a separate protocol
amendment, a disk and time budget, and owner approval.

### 6.4 Paper and blog builds (no experiment)

These builds only read existing results. `make paper` compiles the manuscript in two modes:
- **imported-evidence draft:** macros are generated from the imported reference values, and every
  number carries the label "imported, not reproduced";
- **reproduced:** macros are generated from `results/full/results.json`. This mode is enabled only
  after Tier 1 passes.

Compiling the imported-evidence draft is not scientific verification.

## 7. Uncertainty

- **Sampling uncertainty:** 95% percentile intervals from a paired whole-group bootstrap over 460
  exon/gene groups, 2,000 draws, seed 20260914.
  - Each draw keeps the review fraction k/N, so realised depths vary: 21 to 31 at k = 25, 83 to 126 at
    k = 100, 250 to 378 at k = 300, and 15 to 26 for the tutorial at k = 20.
  - Draws with a single class are skipped and counted.
  - The intervals are unadjusted. The study reports 20 distinct baseline intervals against
    `kmer_cons`, 12 against `kmer_cons_selected` and 9 specialist-versus-specialist intervals from
    the matched study.
- **Tie uncertainty:** the expected P@k plus a [min, max] range over tie orders. Observed contrasts
  use the registered label-independent order: `np.random.default_rng(0).permutation`, combined with a
  lexsort on the score.
- **Monte Carlo error of the interval endpoints:** this was **not quantified** in the original. No new
  seeds are allowed. The protocol records it as an open limitation and does not estimate it.
- **Hyperparameter sensitivity:** reported only through the `*_selected` rows.
- **Not quantified:** training and pretraining overlap between MFASS and the specialists' training
  data; how the 67 training-arm orientation-defect records affect the baselines; and specialist peak
  memory.

## 8. Numerical tolerances (declared before any execution)

### 8.1 Exact match (any platform)

All counts must match exactly: R2 and R5, rows, positives, groups, exclusions and their reasons,
tie block sizes, hits per band, top-k overlaps, realised depth min and max, and single-class skip
counts. So must input digests (R1), the validation-selected hyperparameters, registered-tie-order
P@k values (these are rationals hits/k) and the [min, max] tie ranges. The pytest summary must be
exactly 26 passed.

### 8.2 Floating point

| Quantity | Tolerance | Rationale |
|---|---|---|
| Specialist AP and AUROC (pure replay of fixed inputs) | abs 1e-12 | Same check as the companion test |
| Specialist-only P@k expected values | abs 1e-12 | Pure arithmetic on fixed inputs |
| Control prediction scores vs reference TSVs | abs 1e-9 per variant (companion test threshold) | The HGB fit may differ in the last bits across BLAS, OpenMP and platform |
| Control-derived AP, AUROC, P@k expected | abs 1e-9 | Follows from the line above, provided no ranks change |
| Paired-bootstrap observed differences | abs 1e-9 | Deterministic given the scores |
| Bootstrap interval endpoints, share of zero-difference draws | abs 1e-9 on macOS arm64; see 8.3 elsewhere | The RNG stream (`numpy.random.default_rng`, numpy 1.26.4) is platform-independent |
| Within-band AUROC | abs 1e-9 | |
| Article-displayed values (3 decimals, or 2 for tie ranges) | The reproduced value must round to the identical displayed string | This is what the manuscript prints |
| Timing and peak RSS fields | No tolerance; informational only | Hardware-dependent; never a pass criterion |

### 8.3 Platform rule

Byte identity (R7) is required only on macOS arm64 with the locked environment, which is the
platform of the original runs. On any other platform, such as the Linux CI runner in
`.github/workflows/reproduce.yml`:
- R7 is replaced by the 8.1 and 8.2 checks;
- the outcome is labelled "cross-platform numeric reproduction".

If any control score differs by more than 1e-9 in a way that changes a rank and alters a P@k count,
record a **reproduction discrepancy**. Do not loosen the tolerance after the fact. The rounding rule
in 8.2 still applies.

`metrics.json` is never compared byte for byte. It contains the controls' timing and RSS fields.

## 9. Budgets

| Resource | Limit | Basis |
|---|---|---|
| CPU | Local CPU only, ≤ 4 threads (environment variables in 6.2); no GPU; **no paid compute**, no cloud | Owner constraint |
| Additional disk | ≤ 2 GB in total across the scratch directory, uv cache, venv, data and results | Owner constraint. Estimate about 0.6 to 0.9 GB: fetch 82 MB, GTF 50 MB, `cohort.tsv` and intermediates of tens of MB, venv with numpy, scipy, scikit-learn and pytest of about 0.3 to 0.5 GB, uv cache with Python 3.11 of about 0.1 to 0.2 GB, outputs < 20 MB. Measure the venv size; it is not recorded in the original |
| Network | About 132 MB of data plus Python wheels, from raw.githubusercontent.com, ftp.ebi.ac.uk, api.genome.ucsc.edu and pypi.org/files.pythonhosted.org | Companion README |
| Wall time, Tier 1 | **Expected about 6 to 12 min; hard ceiling 45 min** | See below |
| Per command | `uv sync` 600 s, `fetch` 900 s, `build` 120 s, `controls` 300 s, `annotation` 600 s, `check-variant` 60 s each, `evaluate` (tutorial) 60 s, each full `evaluate` 400 s, `pytest` 300 s | About 5× the recorded M4 times, rounded up, with extra margin for network steps |
| Attempts | At most 2 attempts per command, and only for network or transient failures. A numeric mismatch is never retried | |
| Retained storage | Keep receipts, logs, `results.json` and output tables (< 50 MB). Delete `data/`, the venv and the uv cache after the run, keeping their digests | |

The wall-time estimate comes from the 2026-09-30 archive clean-run receipt on an Apple M4 (16 GB,
macOS 26.6.2, uv 0.8.2, with unpinned default threads): uv sync 4.4 s; fetch 34.9 s; build 2.3 s;
controls 29.0 s; annotation 17.0 s; check-variant 2.0 to 2.6 s each; tutorial evaluate 3.6 s; full
evaluates 59.5, 59.6, 59.8 and 60.6 s; pytest 11.6 s. The total is about 354 s, or about 6 min.

The 4-thread cap mainly slows the `controls` HGB fits, perhaps by about 2× on the 10-core M4 (an
estimate, not measured). The bootstrap in `evaluate` is mostly single-threaded. A cold uv cache and
slower networks add minutes. Peak RSS was at most 678 MB (`build`).

**Mismatch with the scaffold budgets:** `study.json` currently allows `experiment_seconds` 120 and
`reproduction_seconds` 600. A full `evaluate` takes about 60 s, and Tier 1 takes about 6 min even
on the reference machine, so 600 s leaves no margin at 4 threads. The engineer must change the
`study.json` budgets to match this section. That is part of the approval request.

## 10. Stopping rules

Stop immediately, preserve all logs and partial outputs, and report if any of the following occur:
1. Any input SHA-256 or MD5 mismatches (R1), or a copied companion file mismatches the import manifest.
2. `build` count drift (the companion exits non-zero by design).
3. Any command exits non-zero after its permitted attempts, or exceeds its per-command timeout.
4. The cumulative wall time reaches 45 min, or the measured additional disk reaches 2 GB.
5. Any step needs a paid service, GPU, more than 4 threads, specialist inference, or a download not
   listed in section 4.

The following do **not** stop the run. They are recorded and the remaining steps continue, so that
the full picture of agreement and disagreement is preserved:
- a tolerance failure in R3, R4, R6 or R7;
- a pytest failure.

The outcome is then "reproduction discrepancy". It must not be fixed by changing code, seeds, data,
tolerances or commands. Any fix needs an amendment in `protocol/amendments/` and renewed approval.

Never select seeds, budgets, draws or baselines after seeing reproduction output.

## 11. Outcome classification

- **Reproduced (same platform):** R1 to R8 all pass on macOS arm64.
- **Reproduced numerically (cross-platform):** R1 to R6 and R8 pass, and R7 is replaced per 8.3.
- **Partial reproduction:** all steps ran, but at least one tolerance check failed. List each one.
- **Not reproduced / incomplete:** a stopping rule fired before all steps completed.

Every outcome, including failed, partial and null outcomes, is reported in the manuscript and in
`evidence/`. None of these outcomes changes the exploratory status of E1 to E5.

## 12. Exploratory versus confirmatory

- Confirmatory (prespecified here): only R1 to R8, which are claims about computation.
- Exploratory (imported): every scientific comparison, E1 to E5. This explicitly covers:
  - both post hoc budgets (25 and 300);
  - the junction-distance bands;
  - the validation-selected sensitivity rows;
  - the case studies (DDX1, CYFIP1, ARHGEF3, IPO9, COL1A2).
- Any new analysis that has not already been run, such as new budgets, new tie rules, Monte Carlo
  error estimation or other baselines, is out of scope. It would need an amendment, and it would be
  labelled exploratory.

## 13. Limitations and failure interpretation

- A passing Tier 1 shows that the companion pipeline is deterministic and that the replay
  arithmetic is correct. It does not show that SpliceAI or Pangolin reproduce, because Tier 2 was not
  run.
- It does not confirm the assembly-orientation explanation either. That explanation is checked
  computationally only, and the MFASS authors have not confirmed it in KosuriLab/MFASS issue 1.
- The endpoint is MFASS minigene exon recognition in HEK293T cells. It is not patient RNA splicing,
  pathogenicity or diagnostic yield.
- The results apply to one population (8,297 variants, 3.8% prevalence). Budgets are fractions of
  that list, not thresholds for other lists.
- The comparison is between workflows, not architectures: inputs, padding, masking semantics,
  ensemble size and training data all differ.
- All prior review was automated (Claude and Codex agents). There has been no independent human
  scientific review.

## 14. Approval and amendments

The owner must explicitly approve this protocol using the research CLI before the harness runs
anything. The smallest approval needed is set out in `migration-plan/approval-request.md`. Any
change to the commands, tolerances, budgets, stopping rules or scope invalidates approval. Record the
reason and its effect in `protocol/amendments/`, and request approval again. Running the companion's
standalone commands is not protocol approval, and neither is compiling the imported-evidence paper
draft.
