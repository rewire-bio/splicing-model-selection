# Replacing the synthetic scaffold

The repository template carried a Monte Carlo π fixture. It has no scientific role in this study, and
it has already been partly disabled. This is the fixture's state in snapshot
`78eb4628b6553aeba853f33634b7d85a62ac42dd` (correction C12):
- `scripts/experiment.py` and `scripts/analyse.py` are disabled `SystemExit` stubs;
- there is no `src/study/monte_carlo.py` and no `tests/` directory;
- `configs/{smoke,full}.json` have `study_kind "unconfigured"` and seed 20261001;
- `scripts/build_paper.py` requires `paper/figures/convergence.pdf`;
- `Makefile:test` runs `unittest discover -s tests`, which fails because there is no `tests/`
  directory. So `make smoke` and `make reproduce` fail before the experiment starts;
- `.github/workflows/reproduce.yml` runs `make reproduce` on every `push` and `pull_request`, with a
  20-minute timeout.

The fixture's seeds, tolerances and budgets must not be carried into this study.

The tasks below are for the engineer. This is a plan only; nothing has been implemented. Writing the
code is engineering under the harness approval gate. **Executing** any of it (A, B, P, smoke or CI)
requires recorded owner approval of `protocol.md`. Changes to the commands, budgets or tolerances
are protocol amendments.

**Order of work.** S10 must land **before or in the same change as** S1. Otherwise any push after S1
would run Tier 1 without approval.

| # | File(s) | Replacement task | Acceptance check |
|---|---|---|---|
| S10 | `.github/workflows/reproduce.yml` | Change the trigger to `workflow_dispatch` only. Set the 4-thread environment variables and set `timeout-minutes` to at least 45. The runner is Linux x86_64, so R7 does not apply (§8.3). Running CI stays a separate owner decision | No `push` or `pull_request` trigger remains. Lands before or with S1 |
| S1 | `scripts/experiment.py`, `configs/full.json` | Write a Tier 1 driver for `study_kind: "mfass_companion_replay"`. It must: (1) run the §6.1 disk preflight (≥ 3 GiB free; record the baseline); (2) copy the six companion files to `<output>/work/splice-shortlist/` and check them against `evidence/import-manifest.json`; (3) export the 4-thread variables and a single `UV_CACHE_DIR=<scratch>/uv-cache`; (4) run the §6.2 commands in order with per-command timeouts, the 2,700 s cumulative cap and at most 2 attempts for transient failures only; (5) monitor additional disk (stop at 2,048 MiB) and the 1 GiB free floor; (6) record exit code, wall time and peak RSS per command, plus the §8.3 receipt fields; (7) treat `check-variant` as a live check outside stopping rule 3; (8) stop according to §10; (9) write `results.json` even when stopped, and delete `data/`, the venv and the uv cache afterwards, keeping their digests. It never writes into `companion/` | A dry run lists the commands without executing them, and the config hash is recorded. Seed 20261001 does not appear anywhere in the repository after S1 and S2 |
| S2 | `configs/smoke.json` | Replace with an operational smoke config: `uv sync`, `fetch`, `build`, `controls`, then `evaluate --tutorial --budget 20 --draws 200 --method P0`. It is labelled operational and is never evidence of reproduction. It is **not** covered by the requested approval | Smoke results are never compared as R6. Seed 20261001 is gone |
| S3 | `data/manifest.json`, `scripts/data.py`, `.gitignore` | Add 15 entries: the 14 companion `PINNED` files plus the GTF. Each has an HTTPS URL, a licence string, provenance and a path under a git-ignored directory. Either use `results/full/work/...`, or add `data/*` and `!data/manifest.json` to `.gitignore` before this lands. There is a single fetch path: the companion's `fetch` and `annotation` commands download, and `data.py` only verifies the companion's receipt (no second download). Because `make reproduce` runs `data` before the experiment, `make data` must either be a non-downloading preflight or run its receipt check after the experiment. Either way it must not fetch. GTF: the companion MD5 governs unless the owner chooses otherwise | Every digest matches `PINNED`. `git check-ignore` covers every data path. No data are downloaded twice |
| S4 | `scripts/analyse.py`, `evidence/claims.json` | Convert `evidence-map.json` into `evidence/claims.json`. Each claim gets `evidence_class` (`historical_imported` or `tier1_reproduced`) and a `historical_source` (a zip member path or "article text only"). Record the per-member SHA-256 of the 32 zip files. Compare `results.json` using the §8 tiered tolerances, the §8.3 score-identity gate and the display-string precedence rule. Output R1 to R8 as pass, fail, discrepancy or not run, a live-check table, and the §11 class. For R7, compare the fixed 21-file set on macOS arm64 only, extracting into git-ignored scratch | Every claim with `check` R1 to R8 is evaluated, and none is skipped silently. Imported values are never overwritten |
| S5 | `tests/` (new) | Create `tests/`. Add unit tests for: the comparator (tolerance edges, the score-identity gate, the display-boundary rule), the platform rule, the stop conditions (time, disk, free-disk floor) and the network allowlist. The companion `pytest` runs inside the working copy as R8 | `make test` passes without network and without data |
| S6 | `src/study/` | Add only comparison, extraction and receipt helpers. Do not re-implement the science, because the companion is the implementation | |
| S7 | `study.json` | Set `budgets`: `experiment_seconds` 2700, `reproduction_seconds` 3600 (excluding the paper build), `worker_seconds` ≥ 3600, `max_storage_mb` 2048, `max_attempts` 2. Mark the global `abs_tolerance`/`rel_tolerance` as unused for R1 to R8 (protocol §8.2), or remove them if the harness allows | Approved together with the protocol |
| S8 | `Makefile` | `reproduce` runs data verification, then test, then experiment, then analysis. The paper step is timed and receipted separately against its own 600 s cap. Add `paper-imported`, which builds the imported-evidence draft and needs no experiment. Fix `test` once `tests/` exists | `make paper-imported` needs no network beyond the TeX toolchain. The paper time is recorded outside the 3,600 s cap |
| S9 | `scripts/build_paper.py`, `paper/main.tex`, `paper/references.bib` | Remove the `convergence.pdf` dependency. Implement `paper-outline.md`: macro generation in both modes, the reproduced mode for any outcome (§11 class banner; R1 to R8 table with pass, fail, discrepancy or not run; imported values shown next to reproduced values), and the bibliography (13 entries) | The PDF shows the mode banner. A stopped run still builds |
| S11 | `literature/sources.json` | Fill from the bibliography table, with URLs and the original review date (2026-09-30). Mark the entries "not re-retrieved in migration" | |
| S12 | `README.md` | Keep the status wording "imported; reproduction pending". Link to `protocol.md` and this plan | |
