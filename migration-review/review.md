# Methods review before approval: `protocol.md` draft v1 (UNAPPROVED)

- Reviewer role: methods-reviewer (Claude, model `claude-opus-5-5`, single agent, no child workers).
- Date: 2026-10-06. Snapshot: `108d85022498047b8431381bdb50f1786f6bcd38`.
- Scope: a critique only. No experiment, companion command, test, CI job or paper build was run.
  **This review does not approve the protocol or attest to it.** It does not verify any scientific
  result, and it grants no legal permission for any data or code.
- Inputs read: `protocol.md`, `migration-plan/{evidence-map.json, scaffold-replacement.md,
  approval-request.md, paper-outline.md, README.md}`, `companion/{README.md, NOTICE.md,
  splice_shortlist.py, test_splice_shortlist.py}`, `study.json`, `evidence/{import-manifest.json,
  claims.json, reviews.json}`, `data/manifest.json`, `configs/{smoke,full}.json`, `Makefile`,
  `.gitignore`, `.github/workflows/reproduce.yml`, `scripts/{experiment,analyse,data,build_paper}.py`,
  `paper/main.tex`, `MIGRATION.md`.
- Exact corrections are in `migration-review/proposed-protocol-corrections.md`.

## 0. Summary

The protocol is careful in most places that matter scientifically:
- it keeps E1 to E5 exploratory, and it labels k = 25 and k = 300 as post hoc;
- it keeps saved-score replay separate from specialist inference, and it excludes Tier 2;
- it records the unadjusted intervals, inspected outcomes, the 4-thread cap, budgets, stopping rules,
  and that no seeds may be chosen after seeing output.

It is **not ready for approval yet.** Eleven blocking findings (B1 to B11) concern:
- internal contradictions;
- an R7 file set that has not been fixed;
- gaps in the tolerance rules;
- stopping rules that would fire on downloads the protocol itself needs;
- stale scaffold and paper-mode assumptions;
- a `.gitignore` gap that could put MFASS tables into a public repository.

All of them can be fixed by editing the text or configuration. None needs new data, new seeds or
any experiment.

**Dependencies that keep the experiment blocked** are listed here and are not findings of this
review:
1. Owner approval through the research CLI (none recorded; none claimed here).
2. Scaffold tasks S1 to S9 implemented. Today `scripts/experiment.py` and `scripts/analyse.py` are
   `SystemExit` stubs, and `evidence/claims.json`, `data/manifest.json` and `evidence/reviews.json`
   are empty.
3. Owner decisions on: the companion licence, keeping the outputs zip (§4 records "owner decision to
   retain"), and how the GTF is digested (S3).

## 1. Zip members (historical evidence, enumerated without extraction)

How the list was made: I scanned the uncompressed local-file and central-directory headers of
`downloads/splice-shortlist-outputs.zip` with a read-only regex search (Grep). I did not extract,
decompress or execute anything. Every name appears twice (local header and central directory), which
fits a well-formed archive.

The archive has **39 entries: 7 directory entries and 32 files.** This matches the "39 files" in the
delivery report quoted by the evidence map, if directory entries are counted. All paths start with
`splice-shortlist/`.

- Directories: `out/`, `out-b25/`, `out-b300/`, `out-selected-b100/`, `out-tutorial/`, `runs/`,
  `runs/controls/`.
- In each of the five `out*/` directories: `metrics.json`, `excluded.csv`, `decision-table.md`,
  `shortlist.csv` (20 files).
- `runs/controls/`: `prevalence`, `distance`, `kmer_assay`, `kmer_cons`, `kmer_assay_selected`,
  `kmer_cons_selected` `.predictions.tsv` files, plus `receipt.json` (7 files).
- `runs/`: `evaluate-tutorial.log`, `evaluate-b100-P0.log`, `evaluate-b25.log`, `evaluate-b300.log`,
  `evaluate-selected-b100.log` (5 files).

What the archive does **not** contain:
- logs from `fetch`, `build`, `annotation` or `check-variant`, or `pytest` output;
- `data/fetch-receipt.json`;
- `data/cohort.tsv` or any MFASS source table.

Consequences:
- The historical reference values for R2 (C-BUILD), C-GTF (62,754), C-CHECKVAR and R8 (26 passed)
  exist **only as text in `article/original.md`**. They are not archived machine outputs. The evidence
  map lists sources such as "runs/ logs if present" and "not confirmed to contain it"; these should
  now say "article text only".
- U-ZIP-MEMBERS is resolved at the level of member names. Member digests still have to be computed
  by the engineer in a read-only step. I had no shell, so I computed none.

## 2. Blocking findings

### B1. "Redistributes no data" contradicts the retained outputs zip (§4)

- §4 opens with "The repository redistributes no data." The same table then lists the outputs zip as
  "Already in repository (owner decision to retain)".
- The member list shows what the zip holds:
  - the six `runs/controls/*.predictions.tsv` files have columns `id, group, label, score` for all
    8,324 held-out variants (`cmd_controls`, lines 486–489), so they carry the **complete held-out
    MFASS outcome label vector** keyed by MFASS IDs;
  - `shortlist.csv` adds gene, chromosome, `pos_hg38` and `mfass_outcome_retrospective`.
- The §4 row says the zip contains "MFASS outcome labels". It understates how much: every held-out
  label is there, not only those in the shortlists.
- `companion/NOTICE.md` ("contains no MFASS data") is accurate only for the `companion/` directory.
  It must not be read as a statement about the repository.

The user has authorised a public repository, and this review does not reopen that decision. It also
does not judge whether redistribution is legally permitted: MFASS declares no licence, and nothing
here should be read as permission. The fix is factual. State exactly what derived MFASS-linked data
the repository retains, and keep U-LIC-MFASS open as an owner decision.

### B2. The R7 byte-identity file set is ambiguous and must be fixed now

R7 names "`decision-table.md`, `shortlist.csv`, `excluded.csv` and the six control TSVs" without
saying which output directories. Five `out*/` directories exist. The fixed set should be the
**21 files** listed in correction C3:
- 15 = 3 files × 5 directories, including `out-tutorial/`;
- 6 control TSVs.

These should be excluded from byte comparison:
- every `metrics.json`, which contains timing, RSS and a platform string;
- `runs/controls/receipt.json`, which contains timing;
- the five `.log` files, whose capture method is not documented.

Feasibility, from reading the code:
- `decision-table.md` is built only from non-resource fields of `metrics.json`;
- `shortlist.csv` is ordered by `sorted(common, key=-score)` over sorted IDs;
- `excluded.csv` is sorted by ID.

So these three files are deterministic functions of the scores. Byte identity is feasible if the
control TSVs are byte-identical.

A static check should also run before approval. The zip member
`runs/controls/kmer_cons.predictions.tsv` should have the full SHA-256
`2f3117c225a8da9ea737abfa2d0f7e1dec97696ae4bacd263864bec9d7f923eb` (the `PINNED` digest of the
published baseline). This only inspects a frozen input. It is not an experiment.

### B3. Tolerance rules have gaps and precedence conflicts (§8)

1. **Off-platform bootstrap endpoints are undefined.** The §8.2 row says "see 8.3 elsewhere", but
   §8.3 gives no endpoint rule. P@k-difference endpoints are percentiles of discrete values
   (multiples of 1/cap). If one control score moves one rank in any of the 2,000 resamples, an
   endpoint can jump by about 1/cap. That is a discrete change, not a 1e-9 drift. The rule must be
   conditional and declared in advance (C5).
2. **Rank flips below 1e-9 are not covered.** Controls are written with `{v:.10f}` and read back by
   `evaluate`, so all downstream metrics use scores rounded to 1e-10. A difference smaller than 1e-9
   passes R3 but can still create or break a tie, or reorder near-ties. §8.3 handles only differences
   larger than 1e-9 that change a rank. The rule should key on whether the TSVs are byte-identical,
   not on a magnitude.
3. **The display-string rule conflicts with numeric tolerances.** A value inside 1e-12 can still round
   to a different 3-decimal string if it lies on a rounding boundary. The protocol must say which
   rule wins, and label the outcome (C6).
4. **R3 cites only a digest prefix** (`2f3117c2`). It should use the full 64-hex digest.
5. **`study.json` sets a global `abs_tolerance` of 1e-10 and `rel_tolerance` of 1e-8.** These are
   tighter than the 1e-9 tiers for controls, and they apply relative error, which the protocol never
   mentions. The protocol must declare that §8 overrides them, or the values must be removed
   (scaffold S7).
6. **R6 includes Table 2**, whose time and memory columns are informational under §8.2. R6 must
   explicitly exclude resource cells.

### B4. Thread cap differs from the reference run; R7 at 4 threads is untested

- The reference run used "unpinned default threads" on a 10-core M4. Tier 1 caps threads at 4.
- scikit-learn's `HistGradientBoostingClassifier` uses OpenMP. Its results are commonly
  deterministic across thread counts, but the protocol has no evidence of that for this fit
  (U-PLATFORM says as much).
- R7 under 4 threads is therefore a **new condition**, not a replay of the historical one. That is
  acceptable, but the outcome must be declared in advance for the case where R3 passes (≤ 1e-9) but
  R7 fails: "Partial reproduction (byte identity not preserved under 4-thread cap)". It must not be
  reclassified after the fact.
- The run receipt must also record the actual thread count, CPU model, macOS version, and the uv and
  Python versions.

### B5. The stopping rules forbid downloads the run needs (§9, §10.5)

Stopping rule 5 stops on "a download not listed in section 4". §4 lists data only. Three other
downloads are needed:
- `uv sync --frozen` with a fresh cache downloads PyPI wheels;
- if Python 3.11 is not already installed, uv downloads a CPython build from
  `github.com/astral-sh/python-build-standalone`;
- the `paper` step in `make reproduce` downloads Tectonic and the bundle from
  `relay.fullyjustified.net` (`scripts/build_paper.py`, `scripts/bootstrap_tectonic.py`).

Read literally, the rule fires at the first command.

Two smaller issues:
- §6.2 says "each command uses a fresh uv cache", which would re-download per command. It should be
  one fresh cache per run.
- The Tectonic toolchain falls outside the 2 GB disk accounting, and it is unclear whether it is
  part of the "reproduction".

### B6. `check-variant` depends on a live, unpinned API but is treated as a stopping step

- Commands 6 to 8 query `api.genome.ucsc.edu`, which has no digest. Under rule 3, an outage after two
  attempts stops the whole reproduction before `evaluate` runs. An external service then decides the
  R1 to R8 outcome, even though no R hypothesis covers `check-variant`.
- In the code, CYFIP1 prints "ref FAIL" but exits 0, and `check-variant` exits non-zero only for IDs
  outside the cohort. The expected exit codes are therefore 0, 0, 0. This should be stated.
- Fix: classify C-CHECKVAR as a separate, non-confirmatory "live external check", with outcomes
  pass, mismatch or unavailable. Exclude its failures from stopping rule 3, and run these commands
  after `pytest` (C8).

### B7. Paper modes contradict each other, and the build path is stale

- §6.4 enables `reproduced` mode "only after Tier 1 passes".
- §11 and `paper-outline.md` require every outcome, including partial and failed ones, to appear in
  the manuscript with its class.
- This is an internal contradiction. If reproduced mode is gated on a pass, failures cannot be
  reported.
- Fix: enable `reproduced` mode after any completed or stopped Tier 1 run, with the §11 class on the
  banner (C10).

The current build path also does not support either mode:
- `scripts/build_paper.py` still requires `paper/figures/convergence.pdf`, a π-fixture artefact;
- there is one mode and no `paper-imported` target;
- `paper/main.tex` is a placeholder;
- `Makefile:reproduce` always ends with `paper`.

Imported-mode paper status today is **pending, not buildable**. Compiling it would not be
verification in any case.

### B8. The scaffold plan's assertions about the synthetic fixture are stale

`scaffold-replacement.md` lists fixture files that are not in this snapshot:
- `src/study/monte_carlo.py`;
- `tests/test_numerics.py`, and there is no `tests/` directory at all;
- `configs/*.json` containing `n 100000`. The configs hold only `mode`, `study_kind: "unconfigured"`
  and `seed: 20261001`.
- "the π text in the previous `protocol.md`" refers to a file that has already been replaced.

The fixture has already been **disabled**: `scripts/experiment.py` and `scripts/analyse.py` raise
`SystemExit`. The remaining live leftovers are:
- the `convergence.pdf` requirement in `build_paper.py`;
- seed 20261001 in `configs/*.json`;
- `Makefile:test`, which runs `unittest discover -s tests` and fails with no `tests/` directory.
  That makes `make smoke` and `make reproduce` fail before the experiment starts.

S1, S5 and S6 should be rewritten to describe the actual state, so that the engineer does not
"remove" files that do not exist. The plan must also assert that seed 20261001 is not used anywhere.

### B9. CI would execute the experiment without approval once S1 lands

- `.github/workflows/reproduce.yml` runs `make reproduce` on every `push` and `pull_request`, with a
  20-minute timeout.
- When the S1 driver is merged, every push would run Tier 1 on Linux and download the MFASS tables.
  That is an execution the protocol says needs approval. The 20-minute timeout also conflicts with the
  45-minute ceiling.
- S10 is left to the owner, but the order of work must change: switch the trigger to
  `workflow_dispatch` only **before or together with** S1, not afterwards.

### B10. Data paths are not git-ignored

- `.gitignore` ignores `results/` but not `data/`.
- If S3 fills `data/manifest.json` with paths under `data/`, then `make data` (`scripts/data.py
  --fetch`) writes about 80 MB of MFASS source tables to a path that Git tracks. In a public
  repository this would redistribute the source tables, contradicting §4 and the companion README.
- The companion's own `data/` under `results/full/work/...` is already ignored.
- Correction C11 either moves the manifest paths under `results/` or ignores `data/*` with an
  exception for `!data/manifest.json`. It also chooses a single fetch path, which avoids
  downloading everything twice and wasting budget.

### B11. Budgets in `study.json` remain inconsistent beyond those §9 names

§9 and S7 cover `experiment_seconds` (120) and `reproduction_seconds` (600). They do not cover:
- `worker_seconds` 1800, which is below the 45-minute ceiling if a worker drives Tier 1;
- `max_storage_mb` 1000, below 2 GB;
- the S1 design, under which `scripts/experiment.py` runs all of Tier 1. `experiment_seconds` must
  therefore be at least 2,700, and `reproduction_seconds` must also cover data, test, analysis and
  paper.

The per-command ceilings sum to 4,660 s, which is more than the 2,700 s cumulative ceiling. That is
fine, but the protocol should say that the cumulative ceiling takes precedence.

## 3. Non-blocking methodological observations

### 3.1 Statistical validity and uncertainty

- **Bootstrap design.** The paired whole-group percentile bootstrap (460 groups, 2,000 draws) is
  appropriate for clustered variants. Keeping the review fraction means each interval mixes realised
  depths (83 to 126 at k = 100). This is disclosed, and the manuscript should repeat it next to every
  P@k interval.
- **Monte Carlo error.** The endpoints are unquantified (U-MC-ERROR). Several "excludes zero"
  statements rest on bounds of +0.003 to +0.005 (S1 AUROC against both baselines), and the masking
  lower bounds are exactly 0.000.
  - Recommendation: phrase these as "lower bound at or near zero; Monte Carlo error not quantified",
    not as excluding zero.
  - A Monte Carlo standard error computed from the *existing* draws would be a new analysis. It needs
    an amendment, and the protocol correctly forbids it now.
- **Multiplicity.** The study reports 41 unadjusted intervals: 20 against `kmer_cons`, 12 against
  `kmer_cons_selected`, and 9 from the matched study. These are correctly kept exploratory. I-P300
  calls 300 "a lead to test", which is appropriate.
- **Repeated test outcomes.** R8 (pytest) re-checks R3, R4 and R5 on the same outputs. It is not
  independent evidence and should not be counted as such.

### 3.2 Baseline fairness

- The k-mer baselines are supervised on the in-distribution MFASS training arm. The specialists are
  zero-shot on this assay but were pretrained on other data, and their overlap with MFASS has not been
  audited (U-OVERLAP).
- The comparison is therefore between workflows (§13 says so). Neither side's advantage is
  controlled.
- The validation grid selects on AP but the decision endpoint is P@100. This is a reasonable
  pre-existing choice, and it should be stated.
- The 67 training-arm orientation-defect records stay in the baseline training data (U-TRAIN-DEFECT).
- Neither of these is a reason to change the reproduction.

### 3.3 Leakage

- `select_on_validation` uses `GroupShuffleSplit` on training groups only. I confirmed by reading the
  code that the test arm is not read.
- The held-out arm was inspected in earlier work, which is disclosed.
- The `*_selected` contrast run happened after the main analyses, which is disclosed as post hoc.
- No new leakage is introduced by replay.

### 3.4 Historical evidence versus new reproduction

- `evidence/claims.json` should hold each reference value with `evidence_class: "historical_imported"`
  and its source:
  - a zip member, or
  - "article text only" (C-BUILD, C-GTF, C-CHECKVAR, the R8 count, C-CASES).
- Tier 1 values should go into a separate field with `evidence_class: "tier1_reproduced"`. They must
  never overwrite the imported values.
- The R1 to R8 table must cite the historical source for each comparison.

### 3.5 Citation support

- `companion/README.md` cites "Chong et al., Mol Cell 2018". `paper-outline.md` cites *Mol Cell*
  2019;73(1):183–194.e8. The companion is frozen, so the paper and blog should use one citation and
  note the online-versus-issue date if that explains the difference. I did not re-retrieve the source.
- Literature claims (L-*) were not re-retrieved during migration. The manuscript must say so, as
  planned.
- Transcribing the M-STUDY values (U-MSTUDY-MISSING) is an external lookup. It needs the URL at
  `093fd1a` and a retrieval date. It is citation evidence, not reproduction.

### 3.6 Limitations and other gaps

§13 is adequate. Add:
- R7 under the 4-thread cap is a new condition (B4);
- `check-variant` depends on a live API (B6);
- the article reports the IPO9 and COL1A2 case values, but they remain imported and unverified
  (U-CASE-IDS).

## 4. Validation performed

This was a read-only review; I made no changes to any input.
- Read all listed inputs.
- Zip member names were enumerated by a regex scan of the zip headers. Result: 39 entries
  (32 files and 7 directories), as listed in §1.
- Read `companion/test_splice_shortlist.py` and counted 17 plain test functions plus 3 parametrised
  functions with 3 cases each, giving 26 test cases. This is consistent with R8.
- `PINNED` has 14 entries, consistent with R1.
- Not done, because no shell was available and execution is out of scope:
  - SHA-256 of the files in `companion/` against the import manifest;
  - SHA-256 of the zip members;
  - any decompression;
  - any command run.
