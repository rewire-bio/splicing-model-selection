# Replacing the synthetic scaffold

The repository template contains a Monte Carlo π fixture. It has no scientific role in this study.
The fixture files are:
- `src/study/monte_carlo.py`;
- the `estimate_pi` path in `scripts/experiment.py`;
- `configs/{smoke,full}.json` (`study_kind` "unconfigured", seed 20261001, n 100000);
- `tests/test_numerics.py`;
- the π text in the previous `protocol.md`.

Its seeds, tolerances and budgets must not be carried into this study. The tasks below are for the
engineer. They are listed here as a plan only, and nothing has been implemented. Each code change
needs owner approval of `protocol.md` first. Changes to the commands, budgets or tolerances are
protocol amendments.

| # | File(s) | Replacement task | Acceptance check |
|---|---|---|---|
| S1 | `scripts/experiment.py`, `configs/full.json` | Replace the π fixture with a Tier 1 driver for `study_kind: "mfass_companion_replay"`. The driver will: copy the six companion files to `<output>/work/splice-shortlist/`, check them against `evidence/import-manifest.json`, export the 4-thread environment variables, run the protocol §6.2 commands in order with per-command timeouts, record exit code, wall time and peak RSS for each, and stop according to §10. It writes `results.json`, which collects the extracted metrics, the receipts and SHA-256 hashes of the outputs. It never writes into `companion/` | A dry-run lists the commands without executing them, and the config hash is recorded |
| S2 | `configs/smoke.json` | Replace with an operational smoke run: `uv sync`, `fetch`, `build`, `controls`, then `evaluate --tutorial --budget 20 --draws 200 --method P0` (about 75 s on M4). The run is labelled operational and is never evidence of reproduction | Smoke results are never compared as R6 |
| S3 | `data/manifest.json`, `scripts/data.py` | Add 15 entries: the 14 companion `PINNED` files plus the GTF. Each entry has an HTTPS URL, a git-ignored path, a licence string and provenance. `data.py` requires a SHA-256, but upstream gives only an MD5 for the GTF. Either record a SHA-256 computed on first fetch, which has to be reported as an amendment, or let the companion's own MD5 check govern and leave the GTF out of the manifest. **The owner decides.** Decide whether the harness fetches the data itself or relies on the companion's `fetch` command, to avoid downloading everything twice | Every digest matches `PINNED` |
| S4 | `scripts/analyse.py`, `evidence/claims.json` | Turn `evidence-map.json` into `evidence/claims.json` reference values. Compare `results.json` with them using the protocol §8 tolerances. Output a table with pass, fail or discrepancy for R1 to R8 and an outcome class (§11). For R7, enumerate the members of the outputs zip and compare SHA-256 hashes on macOS arm64 only | Every claim with `check` R1 to R8 is evaluated, and none is skipped silently |
| S5 | `tests/test_numerics.py` | Replace the π tests with unit tests for: the comparator (tolerance edges, the rounding-string rule), the platform rule, and the stop conditions. Run the companion `pytest` inside the working copy as R8 | `make test` runs without network |
| S6 | `src/study/` | Remove `monte_carlo.py`. Add only comparison and extraction helpers. Do not re-implement the science, because the companion is the implementation | |
| S7 | `study.json` | Set `budgets` to the protocol §9 values. The current values are too tight: `reproduction_seconds` 600 is under the 45-minute ceiling, and a full `evaluate` alone takes about 60 s against an `experiment_seconds` of 120. Set `max_storage_mb` to 2048 or less. Keep the global `abs_tolerance`/`rel_tolerance` only as a fallback, or point them to the tiered table in §8 | Approved together with the protocol |
| S8 | `Makefile` | `reproduce` runs data, then test, then experiment, then analysis, then paper. Add `paper-imported`, which builds the imported-evidence draft and needs no experiment | `make paper-imported` needs no network beyond the TeX toolchain |
| S9 | `scripts/build_paper.py`, `paper/main.tex`, `paper/references.bib` | Implement `paper-outline.md`: macro generation in both modes and the bibliography (13 entries) | The PDF shows the mode banner |
| S10 | `.github/workflows/reproduce.yml` | The runner is Linux x86_64, so R7 does not apply (§8.3). Set the 4-thread environment variables and raise `timeout-minutes` to about 45. Note that it downloads the MFASS tables on every push. Consider `workflow_dispatch` only | Owner approval: running CI is execution |
| S11 | `literature/sources.json` | Fill from the bibliography table, with URLs and the original review date (2026-09-30). Mark them "not re-retrieved in migration" | |
| S12 | `README.md` | Keep the status wording: "imported; reproduction pending". Link to `protocol.md` and this plan | |
