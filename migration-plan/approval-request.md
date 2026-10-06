# Approval request: bounded harness reproduction (ready for owner review)

Prepared 2026-10-06 by the research-designer role for `protocol.md` draft v2, which applies review
corrections C1 to C13 (`review-disposition.md`).

**Nothing has been approved.** This file describes the decision the owner would record with the
research CLI. The agent cannot record that decision or infer it. It is ready for review now. It can
only take effect at the commit where the pending engineering (below) is complete and the protocol
text is unchanged.

## The decision

> Approve `protocol.md` draft v2, unchanged, at the commit where scaffold tasks S1 to S10 are
> implemented, for exactly this bounded scope:
>
> **Executions**
> - **A.** One original analysis: the S1 Tier 1 driver (`study.json` `experiment.command`,
>   `configs/full.json`).
> - **B.** One clean reproduction: `make reproduce` from a clean checkout with fresh scratch, uv
>   cache and venv.
> - **P.** One paper build from whatever results exist after B. This is the manuscript mode that
>   reports any outcome: pass, partial, discrepancy or stopped.
> - Nothing else: no smoke run, no CI run, no third run, and no rerun after a stopping rule.
>
> **Compute**
> - Local CPU only, at most 4 threads (OMP, OpenBLAS, MKL and vecLib all set to 4).
> - No GPU and no paid services or cloud.
> - No SpliceAI or Pangolin inference (Tier 2 excluded). Specialist rows are a saved-score replay
>   only.
>
> **Time**
> - A: at most 2,700 s.
> - B: at most 3,600 s excluding the paper build, with its Tier 1 part also capped at 2,700 s.
> - P: at most 600 s, recorded separately.
> - Per-command caps as in protocol §9. The cumulative caps take precedence.
>
> **Disk**
> - At most 2 GB (2,048 MiB) of additional storage in aggregate across A, B and P, including the
>   Tectonic toolchain.
> - Preflight: at least 3 GiB free before each of A, B and P.
> - Stop before free space falls below 1 GiB.
>
> **Retries**
> - At most 2 attempts per command (one retry), only for network or transient failures, and always
>   within the time and disk caps.
> - A numeric mismatch is never retried.
>
> **Network**, limited to:
> - the pinned §4 data (about 132 MB: MFASS tables, rewire-benchmarks split and saved predictions,
>   GENCODE 44 GTF);
> - the hash-pinned `uv.lock` wheels from PyPI;
> - CPython 3.11 from `astral-sh/python-build-standalone`, only if no local 3.11 is present;
> - three live UCSC hg38 `check-variant` queries, reported as a live external check outside R1 to R8;
> - for P only, Tectonic and bundle v33 from relay.fullyjustified.net.
>
> **Fixed**
> - Seeds: bootstrap 20260914; registered tie order `default_rng(0)`.
> - Budgets 20, 25, 100 and 300 as listed in §6.2.
> - 2,000 draws (200 for the tutorial).
> - The baselines and the tiered numerical tolerances of protocol §8, which override the global
>   `abs_tolerance` and `rel_tolerance` in `study.json`.
>
> **Outcomes**
> - Every result is kept and reported with its §11 class, including failed, partial, discrepant and
>   stopped runs.
> - Discrepancies are never fixed by changing code, seeds, data, tolerances or commands without an
>   amendment.

This also accepts the `study.json` budget change in scaffold task S7:
- `experiment_seconds` 2700;
- `reproduction_seconds` 3600;
- `worker_seconds` at least 3600;
- `max_storage_mb` 2048;
- `max_attempts` 2.

## What it does not approve

- Tier 2 specialist inference.
- New budgets, seeds, draws, baselines, tolerances or analyses, including Monte Carlo error
  estimation.
- The operational smoke run (S2) or any CI execution (S10). Running CI is a separate owner decision.
- Any legal determination about MFASS-derived content, the companion licence or SpliceAI terms.

Publishing the repository publicly, with commits and pushes, was **already explicitly authorised by
the owner on 2026-10-06**. It is not requested again here. (The worker agents themselves still do not
commit or push.)

## Licence status, recorded transparently (not resolved by this approval)

| ID | Status | What this approval does with it |
|---|---|---|
| U-LIC-MFASS | MFASS declares no licence. The retained outputs zip contains the MFASS outcome label for all 8,324 held-out variants, plus gene names and GRCh38 positions | Nothing. Keeping the zip remains an owner decision. No permission is inferred from the public-repository authorisation |
| U-LIC-COMPANION | Companion code licence unset (`companion/NOTICE.md`) | Nothing. It is recorded as unset |
| U-LIC-SPLICEAI | Ambiguous terms (PolyForm Strict / CC BY-NC 4.0 vs PyPI GPLv3) | Relevant only to Tier 2, which is excluded |

## Other owner inputs (optional; none blocks approval or the computation)

1. Supply the IPO9 and COL1A2 variant IDs so that the case claims can be checked [U-CASE-IDS].
   Otherwise they stay "imported, unverified".
2. Decide whether the GTF is verified by the companion's MD5 alone or also by a SHA-256 recorded on
   first fetch (S3). Under the single-fetch-path rule, the companion's MD5 governs by default.

## Engineering still pending under the harness approval gate

None of this is done. It is listed so that the owner knows what the approved commit must contain.
Implementing it does not change the protocol. Any change to commands, tolerances, budgets, stopping
rules or scope would need an amendment and a new request.

1. **S10 first, or together with S1.** Change the CI trigger to `workflow_dispatch` only, so that no
   push runs Tier 1.
2. Static pre-run step (no experiment):
   - record the per-member SHA-256 of the outputs zip in `evidence/claims.json`;
   - confirm the `kmer_cons` member digest equals `2f3117c2…23eb` (protocol §6.1).

   The member names are already enumerated: 39 entries, 32 files and 7 directories (review §1).
3. S1 to S9: Tier 1 driver with disk preflight and free-disk floor, configs, data manifest under a
   git-ignored path, comparator, new `tests/`, Makefile targets (`paper-imported`, separate paper
   timing), and paper build modes. Remove seed 20261001 from the repository.
4. The owner reviews the final commit and records approval with the CLI.
5. The harness runs A, then B, then P, once each.
