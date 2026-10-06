# Splicing scores for a fixed minigene budget: computational reproduction protocol

Status: **UNAPPROVED** (draft v2, engineering status corrected 2026-10-06; prepared 2026-10-06 by the research-designer role, model
`claude-opus-5-5`). Draft v2 applies corrections C1 to C13 from
`migration-review/proposed-protocol-corrections.md`, which came from the methods review of draft v1
(`migration-review/review.md`, snapshot `108d850`). The mapping from each correction to where it was
applied is in `migration-plan/review-disposition.md`. All corrections were made before approval, so
none of them is a post hoc amendment.

No part of this protocol has been executed. The owner has not approved it. It does not claim that
any original result has been verified by the harness or reproduced independently. The harness code it
depends on (scaffold tasks S1 to S10) **has not been implemented yet** (§14).

This protocol migrates an existing study and adds no new experiment. Its scope is a **computational
reproduction** of the analyses behind the article "Choosing a Splicing Score for a Fixed Minigene
Budget: Baseline, SpliceAI and Pangolin on MFASS" (`article/original.md`, 2026-09-30). The runnable
companion is in `companion/`. Imported provenance is in `evidence/import-manifest.json` (source
`rewire-bio/rewire.it` at `a2ba98c1463162cc91a6376fcdfc71e0023f0703`, issue 339).

## 1. Research question (unchanged from the original)

Suppose you can afford k minigene splicing experiments on a list of human SNVs. Which scoring
configuration should rank the list? The candidates are a supervised baseline trained on assay labels,
or SpliceAI or Pangolin with masking off or on. The question is answered on the MFASS held-out arm,
within the original measured scope.

This protocol asks a narrower **reproduction question**: does a fresh, resource-bounded rerun of the
companion workflow reproduce the recorded measurements within the tolerances declared in §8?

## 2. Contribution and what this protocol does not add

- **Original contribution (imported, exploratory):** a budget-based comparison (P@k) of the
  historical MFASS-v2 k-mer baseline, a validation-selected variant and simple controls against four
  annotation-matched specialist configurations. All are evaluated on one common population of 8,297
  variants. The study reports tie-order ranges, whole-group paired bootstrap intervals, a
  junction-distance breakdown, a documented assembly-orientation exclusion class and a decision
  flowchart.
- **Migration contribution:** this reproduction protocol, with fixed commands, tolerances, budgets and
  stopping rules. It also includes an evidence map that ties every manuscript number to its source, a
  LaTeX manuscript outline, and an outline for an accessible blog post.
- **Not added:** new endpoints, budgets, comparators, datasets, seeds or hyperparameters; new
  specialist inference; any confirmatory scientific claim; any new statistical computation, including
  Monte Carlo error.

## 3. Hypotheses and estimands

### 3.1 Scientific estimands (imported; exploratory only, not re-tested here)

All of these were measured on the common population (N = 8,297; 314 disrupting; 460 groups):

- E1. P@k for every configuration at k in {25, 100, 300} and along the budget curve k in {10, 25, 50,
  100, 150, 200, 300, 400, 600, 800}. Each is reported as the expected value over tie orders, a
  [min, max] range over tie orders, and the value under the registered tie order.
- E2. AP (non-interpolated, `sklearn.metrics.average_precision_score`) and AUROC for every
  configuration.
- E3. Paired differences (candidate minus baseline) in P@k, AP and AUROC for S0, S1, P0 and P1:
  - against `kmer_cons` at k = 25, 100 and 300;
  - against `kmer_cons_selected` at k = 100.

  Each difference is reported as the observed value with a 95% percentile interval from 2,000
  whole-group bootstrap draws, seed 20260914.
- E4. The junction-distance band breakdown: hits in the top k, and AUROC within each band.
- E5. Population accounting: 8,324 held-out variants, 8,297 common, and 27 exclusions (23 assembly
  orientation, 4 outside the canonical transcript span).

**Status of E1 to E5:** exploratory and unadjusted. The held-out outcomes had been inspected in
earlier work. Only k = 100 was fixed in advance; k = 25 and k = 300 are **post hoc**. The rewire-benchmarks
protocol defines an improvement rule: a P@100 gain of at least 0.05 with a paired lower bound above 0.
That rule applies only to a future, prospectively registered cohort, so it is not applied here. This
protocol must not promote any E1 to E5 result to confirmatory status.

### 3.2 Reproduction hypotheses (confirmatory for the computation only)

Each hypothesis is fixed before execution. A pass means the computation reproduced. It does not mean
the science was validated.

- **R1 (inputs).** All 14 pinned files from `fetch` match their recorded SHA-256. The GENCODE 44 GTF
  matches MD5 `b182a9f3b134b9cc2da566a2b1692557`.
- **R2 (cohort).** `build` prints:
  - 27,733 eligible, 1,050 disrupting, 2,198 exons;
  - 7,770 reverse-complemented legacy sequences;
  - train 19,409 / 735 / 1,127 groups and test 8,324 / 315 / 463 groups.

  The reference values are in the article text only (§4, evidence map C-BUILD).
- **R3 (control refit).** `runs/controls/kmer_cons.predictions.tsv` matches the published
  `baseline-kmer-position-v2.predictions.tsv` with max |Δ| < 1e-9, which is the companion test. It
  should also be byte-identical, with SHA-256
  `2f3117c225a8da9ea737abfa2d0f7e1dec97696ae4bacd263864bec9d7f923eb` (equal to the `PINNED` digest).
  Validation selection must choose (0.06, 15) for `kmer_assay` and (0.1, 15) for `kmer_cons`.
- **R4 (replay).** For S0, S1, P0 and P1, AP and AUROC equal the matched-study JSON values within
  absolute 1e-12. The registered-tie-order P@100 equals the study's `precision_at_capacity` exactly.
- **R5 (population).** {held_out 8324, common_scored 8297, positives 314, groups 460, excluded 27},
  with 23 orientation and 4 span exclusions.
- **R6 (metrics and intervals).** Every number in Tables 2 to 6 and Figures 4 and 5 of the article that
  is regenerated from `metrics.json` or `decision-table.md` matches within the §8 tolerances. R6
  excludes all time, RSS, download-size and environment fields (the Table 2 resource columns and
  T2-RES).
- **R7 (determinism, macOS arm64 only).** These 21 files are byte-identical (SHA-256) to the zip
  members with the same paths under `splice-shortlist/` in `downloads/splice-shortlist-outputs.zip`
  (zip SHA-256 `6d1f0de2f359a1984c89f60b402a66e906cb24bc1a4beb7a97336af0f17dbb33`):
  - `{out,out-b25,out-b300,out-selected-b100,out-tutorial}/{decision-table.md,shortlist.csv,excluded.csv}`
    (15 files);
  - `runs/controls/{prevalence,distance,kmer_assay,kmer_cons,kmer_assay_selected,kmer_cons_selected}.predictions.tsv`
    (6 files).

  These files are never compared byte for byte:
  - the 5 `metrics.json` files;
  - `runs/controls/receipt.json`;
  - the 5 `runs/evaluate-*.log` files.

  The archive has 39 entries (32 files and 7 directories). Before approval, the engineer records the
  SHA-256 of each member in `evidence/claims.json`. Comparisons extract only into a git-ignored
  scratch directory. Under the 4-thread cap R7 is a **new condition**, because the reference run used
  default threads (§8.3).
- **R8 (tests).** `pytest -q` in the populated companion working copy passes every collected test, with zero failures and zero skips. The historical suite contained 26 tests; added regression tests must also pass. R8
  re-checks R3 to R5 on the same outputs, so it is not independent evidence (§13).

**Not part of R1 to R8:** the three `check-variant` calls. They are a live external check (§6.2).

## 4. Data, provenance and licences

The repository does not redistribute MFASS source tables (`snv_data_clean.txt`,
`snv_func_annot.txt`), alleles or sequences, or any specialist model weights. Those inputs are fetched
at run time into a git-ignored scratch directory and checked against the pinned digests.

The repository **does retain** `downloads/splice-shortlist-outputs.zip`, which holds data derived
from MFASS:
- six `runs/controls/*.predictions.tsv` files containing the MFASS outcome label for all 8,324
  held-out variants, keyed by MFASS ID and group;
- five `shortlist.csv` files containing gene, chromosome, GRCh38 position and the retrospective MFASS
  outcome.

MFASS declares no licence. Keeping the zip is an owner decision (U-LIC-MFASS). This protocol makes no
claim about whether redistribution is legally permitted. The owner authorised a public repository on
2026-10-06. That authorisation is recorded as given. It is not read as a licence determination for
MFASS-derived content, and this protocol does not ask for it again.

| Input | Source (pinned) | Size | Integrity | Licence / terms | Redistribution |
|---|---|---:|---|---|---|
| `snv_data_clean.txt`, `snv_func_annot.txt` (MFASS) | KosuriLab/MFASS @ `9a8e4f27106be52aeb11acad27f95f5cded663a8`, `processed_data/snv/` | ~80 MB | SHA-256 in `PINNED` (`companion/splice_shortlist.py`) | **No licence declared** | Not redistributed; fetched only |
| `split-v2.tsv` | rewire-benchmarks @ `093fd1ae198c80ce34408d84d6543bca4fc538f2` | <2 MB in total with the next two rows | SHA-256 pinned | MIT (rewire-benchmarks) | Fetched |
| `baseline-kmer-position-v2.predictions.tsv` | as above | (incl.) | SHA-256 `2f3117c225a8da9ea737abfa2d0f7e1dec97696ae4bacd263864bec9d7f923eb` | MIT | Fetched |
| S0/S1/P0/P1 `*.predictions.tsv`, `*.json`; S0/P0 `*.unscored.tsv` | as above, `results/matched-annotation-v1/` | (incl.) | SHA-256 pinned | MIT for the files. They are model outputs; the model terms are noted below | Fetched |
| GENCODE 44 primary-assembly GTF | ftp.ebi.ac.uk, release_44 | ~50 MB | MD5 `b182a9f3b134b9cc2da566a2b1692557` | GENCODE/Ensembl open data | Fetched (`annotation` step) |
| GRCh38 windows for `check-variant` | api.genome.ucsc.edu (`hg38`) | negligible | none (live, unpinned API) | UCSC public API | Only the public GRCh38 base is printed |
| Imported reference outputs | `downloads/splice-shortlist-outputs.zip` (SHA-256 `6d1f0de2f359a1984c89f60b402a66e906cb24bc1a4beb7a97336af0f17dbb33`) | small | import manifest; per-member SHA-256 to be recorded | Per-variant scores and MFASS outcome labels for all 8,324 held-out variants (control TSVs); gene names and GRCh38 positions (shortlists); no MFASS source tables, alleles or sequences | Retained in the repository; owner decision U-LIC-MFASS, no legal determination made |

Tool licences matter only to the out-of-scope specialist route (§6.3):
- Pangolin `5cf94b8` is GPL-3.0. The per-gene mask patch is also GPL-3.0.
- SpliceAI terms are ambiguous. At `03f4243` the repository licenses code under PolyForm Strict 1.0.0
  and models under CC BY-NC 4.0 (changed July 2025). The PyPI 1.3.1 metadata says GPLv3.
- The licence for the companion code itself is **unset**: `companion/NOTICE.md` says "to be set at
  publication" (U-LIC-COMPANION).
- `companion/NOTICE.md` says the companion "contains no MFASS data". That is true of `companion/`
  only. It is not a statement about the repository.

Licence uncertainty is recorded here as it stands. Nothing in this protocol, the review or the
approval request grants or implies legal permission.

**Data manifest and fetch path.** Every fetched file is recorded in `data/manifest.json`, which the
engineer populates. Each entry has a stable URL, a git-ignored local path, the SHA-256 and the licence
string. MFASS entries use `"none declared; not redistributed"`. The run receipt records the retrieval
date.
- Data paths in `data/manifest.json` must sit under a git-ignored directory. Either use
  `results/full/work/...`, or add `data/*` and `!data/manifest.json` to `.gitignore` before S3 lands.
- There is exactly one fetch path. The harness relies on the companion's `fetch` and `annotation`
  commands and their digests. `scripts/data.py` only verifies the companion's receipt; it does not
  download a second copy.

## 5. Configurations, controls and baselines (fixed; identical to the original)

| Name | Role | Scores from |
|---|---|---|
| `prevalence` | Null control (no information) | Computed (training prevalence 0.038) |
| `distance` | Fixed-rule control (negative distance to the nearest construct junction) | Computed (no fitting) |
| `kmer_assay` | Supervised baseline without conservation; published settings (lr 0.06, 31 leaves) | Fitted on 19,409 training variants in 1,127 groups |
| `kmer_cons` | **Historical MFASS-v2 baseline; default contrast reference** | Fitted, published settings |
| `kmer_assay_selected`, `kmer_cons_selected` | Sensitivity baselines; grid lr {0.03, 0.06, 0.1} × leaves {15, 31} on a 25% group-held-out part of the training arm | Fitted |
| `S0`/`S1` | SpliceAI 1.3.1, GENCODE 44 canonical, mask 0/1, distance 50 | **Saved-score replay** |
| `P0`/`P1` | Pangolin `5cf94b8` + per-gene mask patch, GENCODE 44 canonical, mask False/True, distance 50 | **Saved-score replay** |

The protocol keeps three kinds of evidence separate throughout:
- **Computed or fitted here:** the reproduction regenerates the scores.
- **Saved-score replay:** the reproduction only re-evaluates the published per-variant predictions.
- **Specialist inference:** rerunning SpliceAI or Pangolin. It is not part of this protocol.

A replay that passes is not evidence that the specialist tools reproduce.

The validation grid selects on AP, but the decision endpoint is P@100. This is a pre-existing choice
and is not changed.

## 6. Procedure

### 6.0 Approved executions (the whole bounded scope)

After approval, the harness may perform exactly these executions, and no others:

| ID | What | Command | Time cap |
|---|---|---|---|
| **A. Original analysis** | One Tier 1 run through the S1 driver | `study.json` `experiment.command` with `configs/full.json` | 2,700 s cumulative |
| **B. Clean reproduction** | One run from a clean checkout with fresh scratch, uv cache and venv: data verification, tests, Tier 1, analysis | `make reproduce`, with the paper step timed separately | 3,600 s excluding the paper build. The Tier 1 part is also capped at 2,700 s |
| **P. Paper build** | Build the manuscript from whatever results exist after B (§6.4) | `make paper` (and `make paper-imported`) | 600 s, recorded separately |

Both A and B use the same fixed commands, seeds (20260914; registered tie order `default_rng(0)`),
budgets, draws and tolerances. Each run is classified independently against the imported references
under §8 and §11. If A and B differ on any compared quantity, the difference is reported and judged
by the same §8 rules. No new quantity is computed.

These are not approved: a third run, a rerun after a stopping rule fires, the operational smoke
config (S2), CI runs (S10) and Tier 2. Any of them needs a separate decision or an amendment.

### 6.1 Pre-run checks (static; not experiments)

1. **Working copy.** `companion/` is a frozen input. The companion writes `data/`, `runs/` and
   `out*/` next to its own script. The harness must therefore copy the six companion files into a
   fresh, git-ignored working directory for each run, and never run the companion in place:

   ```
   results/full/work/splice-shortlist/   # copy of companion/{splice_shortlist.py,test_splice_shortlist.py,pyproject.toml,uv.lock,README.md,NOTICE.md}
   ```

   Verify that each copied file's SHA-256 matches `evidence/import-manifest.json`.
2. **Reference digest.** Confirm that zip member
   `splice-shortlist/runs/controls/kmer_cons.predictions.tsv` has SHA-256
   `2f3117c225a8da9ea737abfa2d0f7e1dec97696ae4bacd263864bec9d7f923eb`. Record the per-member SHA-256
   of all 32 files in `evidence/claims.json`. This step inspects a frozen input and is not an
   experiment.
3. **Disk preflight.** Before A, before B and before P, record the free space on the volume that
   holds the scratch directory, uv cache, venv and `.tools/`. Do not start unless at least 3 GiB
   (3,072 MiB) is free. Record the free space before A as the single baseline for the 2 GB aggregate
   storage accounting (§9). A failed preflight is recorded and is not counted as an attempt.

### 6.2 Tier 1 commands (used by A and B)

Environment:
- `OMP_NUM_THREADS=4`, `OPENBLAS_NUM_THREADS=4`, `MKL_NUM_THREADS=4`, `VECLIB_MAXIMUM_THREADS=4`;
- uv ≥ 0.8 (reference uv 0.8.2) and Python 3.11 from `uv.lock`;
- local CPU only.

A single fresh uv cache (`UV_CACHE_DIR=<scratch>/uv-cache`) is created once for the run and shared by
all commands. Each command is logged with its exit code, wall time and peak RSS. Run the commands in
this order from `results/full/work/splice-shortlist/`:

```bash
uv sync --frozen
uv run --frozen python splice_shortlist.py fetch
uv run --frozen python splice_shortlist.py build
uv run --frozen python splice_shortlist.py controls
uv run --frozen python splice_shortlist.py annotation
uv run --frozen python splice_shortlist.py evaluate --tutorial --budget 20 --draws 200 --method P0 --out out-tutorial
uv run --frozen python splice_shortlist.py evaluate --budget 100 --method P0 --out out
uv run --frozen python splice_shortlist.py evaluate --budget 300 --method kmer_cons --out out-b300
uv run --frozen python splice_shortlist.py evaluate --budget 25 --method S1 --out out-b25
uv run --frozen python splice_shortlist.py evaluate --budget 100 --baseline kmer_cons_selected --method kmer_cons_selected --out out-selected-b100
uv run --frozen pytest -q
# live external check (not part of R1 to R8)
uv run --frozen python splice_shortlist.py check-variant ENSE00000712808_003   # DDX1, PASS example
uv run --frozen python splice_shortlist.py check-variant ENSE00001321140_001   # CYFIP1, orientation exclusion
uv run --frozen python splice_shortlist.py check-variant ENSE00002361772_001   # ARHGEF3, span exclusion
```

**`check-variant` is a live external check.** It depends on the live, unpinned UCSC API, and it is not
part of R1 to R8.
- The expected exit code for all three calls is 0. CYFIP1 prints "ref FAIL" and still exits 0.
- Each call is reported as `match`, `mismatch` (listing the lines that differ from the article's
  console blocks) or `unavailable`.
- A network failure after 2 attempts is recorded and does not trigger stopping rule 3.

The original clean run made two more `check-variant` calls (IPO9 and COL1A2). Their IDs are not given
in the imported article or README, and the article does not show their console output. They are
**excluded** rather than guessed (U-CASE-IDS). The article's `evaluate --budget 60 --method P1`
command is marked "not executed" there and stays out of scope.

After the commands, the harness writes `results/full/results.json`. It is a structured extraction of:
- the five `metrics.json` files;
- the controls `receipt.json` and the fetch receipt;
- the per-command receipts;
- the SHA-256 of every output file.

`scripts/analyse.py` then compares `results.json` with the reference values in `evidence/claims.json`,
which the engineer converts from `migration-plan/evidence-map.json`. Comparisons with the imported
outputs zip follow §8.

### 6.3 Tier 2: full specialist inference (documented; not requested; outside budget)

The route is rewire-benchmarks `093fd1a`, `results/matched-annotation-v1/README.md#reproduction`:
- GENCODE 44 FASTA (845 MB) and GTF (50 MB);
- the patched Pangolin `5cf94b8`;
- SpliceAI 1.3.1 with TensorFlow 2.21.0;
- torch 2.2.2;
- `run_matched_study.sh MANIFEST ENV_FILE`.

The recorded scoring times on an Apple M4 were S0 6,921 s, S1 6,102 s, P0 19,153 s and P1 18,655 s.
That totals 50,831 s (about 14.1 h) of scoring at 5 or 6 threads, before cohort preparation. At a
4-thread cap, assume at least 14 h, perhaps 18 to 21 h. This figure is extrapolated, not measured.
Downloads alone come to about 1.4 GB before the environments are installed, so the 2 GB disk budget
would very likely be exceeded. The SpliceAI licence terms are also unresolved. **Tier 2 must not run
under this protocol.** Running it would need a separate protocol amendment, its own disk and time
budget, and owner approval.

### 6.4 Paper and blog builds (no experiment)

These builds only read existing results. The intended two modes are listed below; only the imported-evidence mode is implemented:
- **Imported-evidence draft.** Macros are generated from the imported reference values, and every
  number carries the label "imported, not reproduced".
- **Reproduced (manuscript mode for any outcome).** Macros are generated from
  `results/full/results.json`. This mode is enabled after any approved Tier 1 run ends, whether it
  completes or a stopping rule fires:
  - the banner shows the §11 outcome class;
  - the R1 to R8 table shows pass, fail, discrepancy or not run for each check;
  - the live-check table shows match, mismatch or unavailable;
  - imported values appear next to reproduced values and are never overwritten.

The imported-evidence manuscript is now implemented in `paper/main.tex`, with the
`make paper-imported` target and a local TeX Live builder. It formats hash-verified archived
metrics and compiles the paper without running experiments, fetching data or creating an environment.
This build is not scientific verification or independent reproduction. The reproduced-results paper
mode remains pending with the scientific harness implementation.

The current paper builder uses locally installed `pdflatex`, `bibtex` and `rsvg-convert`.
It does not use or download Tectonic; `scripts/bootstrap_tectonic.py` is a retained, unused scaffold.
Any future execution protocol must reconcile its paper-toolchain budget and commands with this
implemented builder before approval. No research execution is approved by this status correction.

## 7. Uncertainty

- **Sampling uncertainty.** 95% percentile intervals come from a paired whole-group bootstrap over 460
  exon/gene groups, with 2,000 draws and seed 20260914.
  - Each draw keeps the review fraction k/N, so realised depths vary: 21 to 31 at k = 25, 83 to 126 at
    k = 100, 250 to 378 at k = 300, and 15 to 26 for the tutorial at k = 20. The manuscript repeats
    this next to every P@k interval.
  - Draws with a single class are skipped and counted.
  - The intervals are unadjusted. The study reports 20 distinct baseline intervals against
    `kmer_cons`, 12 against `kmer_cons_selected`, and 9 specialist-versus-specialist intervals from
    the matched study.
- **Tie uncertainty.** P@k is reported as an expected value with a [min, max] range over tie orders.
  Observed contrasts use the registered label-independent order: `np.random.default_rng(0).permutation`
  combined with a lexsort on the score.
- **Monte Carlo error of the interval endpoints.** This was **not quantified** in the original. No new
  seeds or computations are allowed. The protocol records it as an open limitation.
- **Near-zero reporting rule (reporting only; no new computation).** Interval bounds within about
  0.005 of zero (for example, S1 AUROC, and masking P@100 lower bounds of 0.000) are described as "at
  or near zero; Monte Carlo error not quantified". They are not described as excluding zero.
- **Hyperparameter sensitivity.** Reported only through the `*_selected` rows.
- **Not quantified:**
  - overlap between MFASS and the specialists' training and pretraining data;
  - how the 67 training-arm orientation-defect records affect the baselines;
  - specialist peak memory.

## 8. Numerical tolerances (declared before any execution)

### 8.1 Exact match (any platform)

These must match exactly:
- all counts: R2 and R5, rows, positives, groups, exclusions and their reasons, tie block sizes, hits
  per band, top-k overlaps, realised depth min and max, and single-class skip counts;
- input digests (R1);
- the validation-selected hyperparameters;
- registered-tie-order P@k values (these are rationals, hits/k) and the [min, max] tie ranges;
- the pytest result: every collected test passes, with zero failures and zero skips; record the test count and source revision.

### 8.2 Floating point

| Quantity | Tolerance | Rationale |
|---|---|---|
| Specialist AP and AUROC (pure replay of fixed inputs) | abs 1e-12 | Same check as the companion test |
| Specialist-only P@k expected values | abs 1e-12 | Pure arithmetic on fixed inputs |
| Control prediction scores vs reference TSVs | abs 1e-9 per variant (companion test threshold) | The HGB fit may differ in the last bits across BLAS, OpenMP, thread count and platform |
| Control-derived AP, AUROC, P@k expected | abs 1e-9 if the §8.3 gate passes; otherwise §8.3 | Follows from the line above only if the scores are byte-identical |
| Paired-bootstrap observed differences | abs 1e-9 if the gate passes; otherwise §8.3 | Deterministic given the scores |
| Bootstrap interval endpoints, share of zero-difference draws | Specialist-versus-specialist and replay-only quantities: abs 1e-12 on any platform. Contrasts that involve a control: if the §8.3 gate passes, abs 1e-9 on any platform, because the numpy 1.26.4 `default_rng` stream does not depend on platform. If the gate fails, there is no numeric tolerance: report the observed endpoints next to the reference values. Any difference larger than 1e-9 is a reproduction discrepancy, and a P@k endpoint that shifts is listed with its step size, 1/cap | P@k endpoints are percentiles of discrete values |
| Within-band AUROC | abs 1e-9 if the gate passes; otherwise §8.3 | |
| Article-displayed values (3 decimals, or 2 for tie ranges) | The reproduced value must round to the identical displayed string | This is what the manuscript prints |
| Timing, peak RSS, download sizes, environment fields | No tolerance; informational only | Hardware-dependent; never a pass criterion and excluded from R6 |

**Precedence.** A value passes only if it is within its numeric tolerance **and** reproduces the
imported displayed string. A value that is within tolerance but rounds to a different string is
labelled a "display-boundary difference". It is listed and counts as a tolerance failure for §11.
Tolerances are never widened.

R6 excludes every time, RSS, download-size and environment field (the Table 2 resource columns and
T2-RES).

These tolerances override the global `abs_tolerance` (1e-10) and `rel_tolerance` (1e-8) in
`study.json`. Those global values are not used for R1 to R8, and relative error is not used anywhere.

### 8.3 Score-identity gate and platform rule

**Score-identity gate.** First compare the six control TSVs byte for byte with the reference.
- **If all six are byte-identical:** every control-derived quantity must match within abs 1e-9. That
  covers AP, AUROC, P@k, bootstrap observed values and endpoints, the share of zero-difference draws,
  and within-band AUROC. Every count must match exactly.
- **If any TSV differs, at any magnitude:** R3 is still judged at max |Δ| < 1e-9. All
  control-derived quantities are then reported with their observed differences and judged by the §8.2
  rules. Any changed count, tie block, top-k membership or P@k value is a **reproduction
  discrepancy**, even when |Δscore| < 1e-9. (Controls are written with `{v:.10f}`, so a difference
  below 1e-9 can still create or break a tie.)
- **If R3 passes but R7 fails on the control TSVs:** the outcome is "Partial reproduction (byte
  identity not preserved under the 4-thread cap)". The reference run used default threads, so this is
  a new condition. It is declared now and is not reclassified afterwards.

**Platform rule.** Byte identity (R7) is required only on macOS arm64 with the locked environment,
which is the platform of the original runs. On any other platform:
- R7 is replaced by the §8.1 and §8.2 checks under the gate above;
- the outcome is labelled "cross-platform numeric reproduction".

`metrics.json`, `receipt.json` and the logs are never compared byte for byte.

**Receipt fields** (both A and B): the thread environment variables, `os.cpu_count()`, CPU model,
macOS version, and the uv, Python, numpy and scikit-learn versions. Also record which Python source
was used (§9), the free disk at each preflight, and the peak additional disk use.

## 9. Budgets

| Resource | Limit | Basis |
|---|---|---|
| CPU | Local CPU only, ≤ 4 threads (environment variables in §6.2). No GPU, **no paid services or paid compute**, no cloud | Owner constraint |
| Executions | Exactly one original analysis (A) and one clean reproduction (B), plus the paper build (P) | Owner constraint |
| Wall time, A | **Hard ceiling 2,700 s cumulative** for Tier 1. Expected about 6 to 12 min | Owner constraint |
| Wall time, B | **Hard ceiling 3,600 s** for data verification, tests, Tier 1 and analysis, excluding the paper build. The Tier 1 part is also capped at 2,700 s | Owner constraint |
| Wall time, P | **Hard ceiling 600 s**, recorded separately, including the Tectonic toolchain download | Owner constraint |
| Per command | `uv sync` 600 s, `fetch` 900 s, `build` 120 s, `controls` 300 s, `annotation` 600 s, `check-variant` 60 s each, `evaluate` (tutorial) 60 s, each full `evaluate` 400 s, `pytest` 300 s | About 5× the recorded M4 times, rounded up, with extra margin for network steps |
| Precedence | The 2,700 s cumulative ceiling overrides the per-command ceilings, which sum to 4,660 s. A retry counts against both the per-command and cumulative ceilings | |
| Additional disk | **≤ 2 GB (2,048 MiB) in aggregate across all stages (A, B and P)**, measured as the drop in free space since the baseline taken before A. This covers the scratch directories, uv caches, venvs, data, results and `.tools/` | Owner constraint. Estimate per Tier 1 run: about 0.6 to 0.9 GB at peak (fetch 82 MB, GTF 50 MB, intermediates of tens of MB, a venv with numpy, scipy, scikit-learn and pytest of about 0.3 to 0.5 GB, uv cache with Python 3.11 of about 0.1 to 0.2 GB, outputs < 20 MB). The Tectonic toolchain size has not been measured. All of these are estimates |
| Free-disk floor | Preflight requires at least 3 GiB free before A, B and P. **Stop before free space falls below 1 GiB** at any point | Owner constraint |
| Network | Only: the §4 data inputs (about 132 MB from raw.githubusercontent.com and ftp.ebi.ac.uk); PyPI wheels pinned by hash in `companion/uv.lock` (from pypi.org and files.pythonhosted.org); a uv-managed CPython 3.11 from github.com (`astral-sh/python-build-standalone`), only if no local 3.11 is present, with the source used recorded; the UCSC API queries of §6.2. The paper build P may also download Tectonic and bundle v33 from relay.fullyjustified.net | Companion README; review B5 |
| Attempts | At most 2 attempts per command (one retry), and only for network or transient failures, always within the time and disk caps. A numeric mismatch or count drift is never retried | |
| Retained storage | Keep receipts, logs, `results.json` and output tables (< 50 MB per run). After each run, delete its `data/`, venv and uv cache, keeping their digests. B starts from fresh scratch, cache and venv | Keeps the aggregate within 2 GB |

The wall-time estimate comes from the 2026-09-30 archive clean-run receipt on an Apple M4 (16 GB,
macOS 26.6.2, uv 0.8.2, with unpinned default threads): uv sync 4.4 s; fetch 34.9 s; build 2.3 s;
controls 29.0 s; annotation 17.0 s; check-variant 2.0 to 2.6 s each; tutorial evaluate 3.6 s; full
evaluates 59.5, 59.6, 59.8 and 60.6 s; pytest 11.6 s. The total is about 354 s, or about 6 min. The
4-thread cap mainly slows the `controls` HGB fits, perhaps by about 2×; that is an estimate, not a
measurement. The bootstrap in `evaluate` is mostly single-threaded. A cold uv cache and slower networks
add minutes. Peak RSS was at most 678 MB (`build`).

**`study.json` values.** The `study.json` budgets must be:
- `experiment_seconds` ≥ 2700 (the S1 driver runs all of Tier 1); proposed 2700;
- `reproduction_seconds` ≥ 2700 plus the data, test and analysis steps; proposed 3600, excluding the
  paper toolchain;
- `worker_seconds` ≥ 3600 if a worker drives a run;
- `max_storage_mb` ≤ 2048;
- `max_attempts` 2.

The current values (120, 600, 1800 and 1000) are too tight. The paper cap of 600 s has no `study.json`
field today, so S8 records it in the paper receipt. These values are part of the approval request.

## 10. Stopping rules

Stop the current execution immediately, keep all logs and partial outputs, and report if any of these
occur:
1. Any input SHA-256 or MD5 mismatches (R1), or a copied companion file mismatches the import manifest.
2. `build` count drift (the companion exits non-zero by design).
3. Any R1 to R8 command exits non-zero after its permitted attempts, or exceeds its per-command
   timeout. `check-variant` network failures are excluded (§6.2).
4. A wall-time cap in §9 is reached (2,700 s for Tier 1; 3,600 s for B excluding the paper; 600 s
   for P), the additional disk reaches 2,048 MiB, or free disk would fall below 1 GiB.
5. Any step needs a paid service, a GPU, more than 4 threads or specialist inference, or downloads
   anything other than the §4 data inputs, the uv.lock wheels, the CPython 3.11 build and the UCSC API
   queries of §6.2. For P, the Tectonic toolchain is also allowed.

If rule 1, 2, 3 or the time part of rule 4 fires during A, B still runs once as approved, provided
its preflight passes. This keeps the clean-reproduction evidence. If rule 5 or the disk part of rule
4 fires during A, B does not run until the owner decides. If any rule fires during B, there is no
rerun. A stopped run is never repeated under this approval.

The following do **not** stop the run. They are recorded, and the remaining steps continue, so that
the full picture of agreement and disagreement is kept:
- a tolerance failure or display-boundary difference in R3, R4, R6 or R7;
- a pytest failure;
- a `check-variant` mismatch or unavailability;
- a paper build failure.

The outcome is then "reproduction discrepancy" (or the live-check status). It must not be fixed by
changing code, seeds, data, tolerances or commands. Any fix needs an amendment in
`protocol/amendments/` and renewed approval.

Never choose seeds, budgets, draws or baselines after seeing reproduction output.

## 11. Outcome classification and evidence records

Each of A and B is classified on its own:
- **Reproduced (same platform):** R1 to R8 all pass on macOS arm64.
- **Reproduced numerically (cross-platform):** R1 to R6 and R8 pass, and R7 is replaced as §8.3
  describes.
- **Partial reproduction (byte identity not preserved under the 4-thread cap):** R3 passes, R7 fails on
  the control TSVs, and the other checks are judged under the §8.3 gate.
- **Partial reproduction:** all steps ran, but at least one tolerance check failed or there was a
  display-boundary difference. Each one is listed.
- **Not reproduced / incomplete:** a stopping rule fired before all steps completed.

The live-check status (`match`, `mismatch` or `unavailable` per call) is reported next to the class
and does not change it.

Every outcome, including failed, partial and null outcomes, is reported in the manuscript and in
`evidence/`. Failed and stopped runs are kept, not deleted or overwritten. None of these outcomes
changes the exploratory status of E1 to E5.

Claims in `evidence/claims.json` carry `evidence_class`, set to `historical_imported` or
`tier1_reproduced`, plus a `historical_source` (a zip member path or "article text only"). Reproduced
values go in separate fields and never overwrite imported ones. The R1 to R8 table cites the
historical source for each comparison.

## 12. Exploratory versus confirmatory

- Confirmatory (prespecified here): only R1 to R8, which are claims about computation.
- Not confirmatory: the `check-variant` live external check.
- Exploratory (imported): every scientific comparison, E1 to E5. This explicitly covers:
  - both post hoc budgets (25 and 300);
  - the junction-distance bands;
  - the validation-selected sensitivity rows;
  - the case studies (DDX1, CYFIP1, ARHGEF3, IPO9, COL1A2).
- Any analysis that has not already been run is out of scope. That includes new budgets, new tie rules,
  Monte Carlo error estimation and other baselines. Such an analysis would need an amendment and would
  be labelled exploratory.

## 13. Limitations and failure interpretation

- A passing Tier 1 shows that the companion pipeline is deterministic and that the replay arithmetic
  is correct. It does not show that SpliceAI or Pangolin reproduce, because Tier 2 was not run.
- It does not confirm the assembly-orientation explanation either. That explanation is checked
  computationally only. The MFASS authors have not confirmed it (KosuriLab/MFASS issue 1).
- R7 under the 4-thread cap is a new condition. The reference run used default threads.
- `check-variant` depends on a live, unpinned API. Its results can change for reasons unrelated to
  the study.
- R8 re-checks R3 to R5 on the same outputs, so it is not independent evidence.
- The IPO9 and COL1A2 case values remain imported and unverified (U-CASE-IDS).
- The endpoint is MFASS minigene exon recognition in HEK293T cells. It is not patient RNA splicing,
  pathogenicity or diagnostic yield.
- The results apply to one population (8,297 variants at 3.8% prevalence). Budgets are fractions of
  that list, not thresholds for other lists.
- The comparison is between workflows, not architectures. Inputs, padding, masking semantics, ensemble
  size and training data all differ. The k-mer baselines are supervised on in-distribution MFASS
  training data, and the specialists' overlap with MFASS has not been audited.
- All prior review was automated (Claude and Codex agents). There has been no independent human
  scientific review.

## 14. Approval, pending engineering and amendments

The owner must explicitly approve this protocol through the research CLI before the harness runs
anything. The bounded scope to approve is set out in `migration-plan/approval-request.md`. No approval
is recorded, and none is claimed or implied here.

**Engineering still pending under the harness approval gate.** Today:
- `scripts/experiment.py` and `scripts/analyse.py` are disabled `SystemExit` stubs;
- `evidence/claims.json`, `data/manifest.json` and `evidence/reviews.json` are empty;
- `make test` runs the companion unit/regression tests; integration tests skip without scientific inputs;
- the imported-evidence paper builds from historical outputs using local TeX Live;
- push/PR CI runs offline tests and archived-table validation; the separate reproduction workflow remains manual and unimplemented.

Scaffold tasks S1 to S10 (`migration-plan/scaffold-replacement.md`) must land before A can run, with
S10 landing before or together with S1. Implementing them does not change this protocol. Any change to
the commands, tolerances, budgets, stopping rules or scope invalidates approval. Record the reason
and its effect in `protocol/amendments/`, and request approval again.

Neither of these counts as protocol approval: running the companion's standalone commands, or
compiling the imported-evidence paper draft. The public-repository authorisation of 2026-10-06 is a
separate, already-recorded owner decision. It is neither approval of this protocol nor a licence
determination.
