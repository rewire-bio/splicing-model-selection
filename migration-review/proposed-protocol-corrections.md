# Proposed corrections to make before replay approval

These are proposals from the methods review (`migration-review/review.md`). They are not applied:
inputs are frozen, and the designer or engineer must make the edits. Each one changes the draft
before approval, so none of them is a post hoc amendment. Each correction lists the finding (B#)
it fixes. Anything not listed here stays as it is.

## C1 (B1). §4, first sentence

Replace:
> The repository redistributes no data. All data are fetched at run time into a git-ignored scratch
> directory and checked against the pinned digests.

with:
> The repository does not redistribute MFASS source tables (`snv_data_clean.txt`,
> `snv_func_annot.txt`), alleles or sequences, or any specialist model weights. Those inputs are
> fetched at run time into a git-ignored scratch directory and checked against the pinned digests.
>
> The repository **does retain** `downloads/splice-shortlist-outputs.zip`, which holds data derived
> from MFASS:
> - six `runs/controls/*.predictions.tsv` files containing the MFASS outcome label for all 8,324
>   held-out variants, keyed by MFASS ID and group;
> - five `shortlist.csv` files containing gene, chromosome, GRCh38 position and the retrospective
>   MFASS outcome.
>
> MFASS declares no licence. Keeping the zip is an owner decision (U-LIC-MFASS). This protocol
> makes no claim about whether redistribution is legally permitted.

In the §4 table row "Imported reference outputs", change the contents cell to:
> Per-variant scores and MFASS outcome labels for all 8,324 held-out variants (control TSVs); gene
> names and GRCh38 positions (shortlists); no MFASS source tables, alleles or sequences

## C2 (B3.4). §3.2 R3

Replace "(SHA-256 prefix `2f3117c2`)" with:
> (SHA-256 `2f3117c225a8da9ea737abfa2d0f7e1dec97696ae4bacd263864bec9d7f923eb`, equal to the
> `PINNED` digest)

Add the following as a pre-run static check under §6.1. It inspects a frozen input and is not an
experiment:
> Confirm that zip member `splice-shortlist/runs/controls/kmer_cons.predictions.tsv` has this
> digest.

## C3 (B2). §3.2 R7: fixed file set

Replace R7 with:
> R7 (determinism, macOS arm64 only): these 21 files are byte-identical (SHA-256) to the zip
> members with the same paths under `splice-shortlist/` in `downloads/splice-shortlist-outputs.zip`
> (zip SHA-256 `6d1f0de2f359a1984c89f60b402a66e906cb24bc1a4beb7a97336af0f17dbb33`):
> - `{out,out-b25,out-b300,out-selected-b100,out-tutorial}/{decision-table.md,shortlist.csv,excluded.csv}`
>   (15 files);
> - `runs/controls/{prevalence,distance,kmer_assay,kmer_cons,kmer_assay_selected,kmer_cons_selected}.predictions.tsv`
>   (6 files).
>
> These files are never compared byte for byte:
> - the 5 `metrics.json`;
> - `runs/controls/receipt.json`;
> - the 5 `runs/evaluate-*.log`.
>
> The archive has 39 entries (32 files and 7 directories); the engineer records the per-member
> SHA-256 values in `evidence/claims.json` before approval. To compare, extract only into a
> git-ignored scratch directory.

## C4 (B3.2, B4). §8.3: replace the rank-change paragraph

> **Score-identity gate.** First compare the six control TSVs byte for byte with the reference.
> - **If all six are byte-identical:** every control-derived quantity (AP, AUROC, P@k, bootstrap
>   observed values and endpoints, share of zero-difference draws, within-band AUROC) must match
>   within abs 1e-9, and every count must match exactly.
> - **If any TSV differs, at any magnitude:** R3 is still judged at max |Δ| < 1e-9. All
>   control-derived quantities are then reported with their observed differences and judged by the
>   C5 and C6 rules. Any changed count, tie block, top-k membership or P@k value is a
>   **reproduction discrepancy**, even when |Δscore| < 1e-9.
> - **If R3 passes but R7 fails on the control TSVs:** the outcome is "Partial reproduction
>   (byte identity not preserved under the 4-thread cap)". The reference run used default threads,
>   so this is a new condition.
>
> Record in the receipt: thread environment variables, `os.cpu_count()`, CPU model, macOS version,
> and the uv, Python, numpy and scikit-learn versions.

## C5 (B3.1). §8.2: bootstrap endpoint row

Replace the tolerance cell "abs 1e-9 on macOS arm64; see 8.3 elsewhere" with:
> Specialist-versus-specialist and replay-only quantities: abs 1e-12 on any platform.
>
> Contrasts involving a control:
> - if the C4 gate passes: abs 1e-9 on any platform (the numpy 1.26.4 `default_rng` stream does not
>   depend on platform);
> - if the gate fails: there is no numeric tolerance. Report the observed endpoints next to the
>   reference values. Any difference larger than 1e-9 is a reproduction discrepancy, and a P@k
>   endpoint that shifts is listed with the step size 1/cap.

## C6 (B3.3, B3.6). §8.2: precedence of the display rule, and resource exclusion

Add below the table:
> **Precedence.** A value passes only if it is within its numeric tolerance **and** reproduces the
> imported displayed string. If it is within tolerance but rounds to a different string, it is
> labelled "display-boundary difference", listed, and counts as a tolerance failure for §11.
> Tolerances are never widened.
>
> R6 excludes every time, RSS, download-size and environment field (Table 2 resource columns and
> T2-RES).
>
> These tolerances override the global `abs_tolerance` and `rel_tolerance` in `study.json`, which
> are not used for R1 to R8.

## C7 (B5). §6.2, §9 and §10.5: permitted downloads and the uv cache

- In §6.2, replace "Each command uses a fresh uv cache under the scratch directory" with:
  > A single fresh uv cache (`UV_CACHE_DIR=<scratch>/uv-cache`) is created once for the run and
  > shared by all commands.
- In §9 Network, extend the list to:
  - PyPI wheels pinned by hash in `companion/uv.lock`, from pypi.org and files.pythonhosted.org;
  - a uv-managed CPython 3.11 from github.com (`astral-sh/python-build-standalone`), only if no
    local 3.11 is present. Record which source was used.
- Replace §10 item 5 with:
  > Any step needs a paid service, a GPU, more than 4 threads or specialist inference, or downloads
  > anything other than: the §4 data inputs, the uv.lock wheels, the CPython 3.11 build, and the
  > UCSC API queries of §6.2.
- State that the paper toolchain (Tectonic and bundle v33 from relay.fullyjustified.net) is
  **outside** Tier 1. It is excluded from the 45-minute and 2 GB accounting and recorded separately.

## C8 (B6). §6.2 order, and a new classification for `check-variant`

- Move the three `check-variant` commands to after `pytest`.
- Add:
  > `check-variant` depends on the live, unpinned UCSC API. It is a **live external check** and is
  > not part of R1 to R8.
  > - Expected exit code for all three calls: 0. (CYFIP1 prints "ref FAIL" and still exits 0.)
  > - Each call is reported as `match`, `mismatch` (with the lines that differ from the article's
  >   console blocks) or `unavailable`.
  > - Network failures after 2 attempts are recorded and do not trigger stopping rule 3.
- In the evidence map, change the C-CHECKVAR, C-BUILD and C-GTF sources to "article text only (not
  in outputs zip)".

## C9 (B11). §9: budget precedence and the `study.json` values

Add:
> The 2,700 s cumulative ceiling overrides the per-command ceilings, which sum to 4,660 s.

Replace the last paragraph of §9 with:
> The `study.json` budgets must be: `experiment_seconds` ≥ 2700 (the S1 driver runs all of
> Tier 1); `reproduction_seconds` ≥ 2700 plus the data, test and analysis steps (proposed 3600,
> excluding the paper toolchain); `worker_seconds` ≥ 3600 if a worker drives the run;
> `max_storage_mb` ≤ 2048; `max_attempts` 2. These values are part of the approval request.

## C10 (B7). §6.4: paper modes

Replace "This mode is enabled only after Tier 1 passes." with:
> This mode is enabled after any approved Tier 1 run ends, whether it completes or a stopping rule
> fires.
> - The banner shows the §11 outcome class.
> - The R1 to R8 table shows pass, fail, discrepancy or not run for each check.
> - Imported values appear next to reproduced values and are never overwritten.

Add:
> The imported-evidence draft is **not buildable yet**. `scripts/build_paper.py` still requires the
> π-fixture artefact `paper/figures/convergence.pdf`, `paper/main.tex` is a placeholder, and there
> is no `paper-imported` target. Until S8 and S9 are done, no paper-mode claim is made.

## C11 (B10). §4 last paragraph, and scaffold S3

Add:
> Data paths in `data/manifest.json` must sit under a git-ignored directory. Either use
> `results/full/work/...`, or add `data/*` and `!data/manifest.json` to `.gitignore` before S3
> lands.
>
> There is exactly one fetch path. The harness relies on the companion's `fetch` and `annotation`
> commands and their digests. `scripts/data.py` only verifies the companion's receipt; it does not
> download a second copy.

## C12 (B8, B9). Corrections to `scaffold-replacement.md` and `approval-request.md`

- **Fixture inventory.** Replace the list with what is actually in the snapshot:
  - `scripts/experiment.py` and `scripts/analyse.py` are disabled `SystemExit` stubs;
  - there is no `src/study/monte_carlo.py` and no `tests/` directory;
  - `configs/{smoke,full}.json` have `study_kind "unconfigured"` and seed 20261001;
  - `build_paper.py` requires `paper/figures/convergence.pdf`;
  - `Makefile:test` runs `unittest discover -s tests`, which fails with no `tests/` directory.
  
  The acceptance check adds: "seed 20261001 does not appear anywhere in the repository after S1
  and S2."
- **S5.** Change to "create `tests/`", not "replace the π tests".
- **S10 and the order of work.** Change the CI trigger to `workflow_dispatch` only, and raise
  `timeout-minutes` to at least 45. Do this **before or in the same change as** S1, because any
  push after S1 would otherwise run Tier 1 without approval. Running CI stays a separate owner
  decision.
- **approval-request.md, "Order of work" step 2.** Mark the zip member names as enumerated
  (39 entries; review §1). Keep "record the per-member SHA-256 values".

## C13 (§3.4 and §3.6 of the review). §11, §12 and §13

- In §11, add:
  > Claims in `evidence/claims.json` carry `evidence_class` set to `historical_imported` or
  > `tier1_reproduced`, plus a `historical_source` (a zip member path or "article text only").
- In §13, add three limitations:
  - R7 under the 4-thread cap is a new condition;
  - `check-variant` depends on a live API;
  - R8 re-checks R3 to R5 on the same outputs, so it is not independent evidence.
- In §7, add:
  > Interval bounds within about 0.005 of zero (S1 AUROC; masking P@100 lower bounds of 0.000) are
  > described as "at or near zero; Monte Carlo error not quantified", not as excluding zero.

  This is a reporting rule only and needs no new computation.
