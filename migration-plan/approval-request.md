# Smallest approval needed for harness reproduction

Nothing has been approved. This file describes the decision the owner would record with the research
CLI. The agent cannot record or infer it.

## The decision

> Approve `protocol.md` (draft v1, at the commit where the harness implementation is complete) for a
> **single Tier 1 computational reproduction**:
> - local CPU, at most 4 threads, no paid compute, no GPU;
> - at most 2 GB additional disk, at most 45 min wall time, at most 2 attempts per command;
> - network fetch of about 132 MB of pinned public data (MFASS tables, rewire-benchmarks split and
>   saved predictions, GENCODE 44 GTF) plus Python wheels, and live UCSC hg38 queries for three
>   `check-variant` calls;
> - comparison against the declared tolerances;
> - no SpliceAI or Pangolin inference (Tier 2 excluded).

This includes accepting the `study.json` budget change in scaffold task S7, from 600 s to 45 min and
to at most 2048 MB.

## What it does not approve

- Tier 2 specialist inference.
- New budgets, seeds, draws or analyses.
- Publishing, pushing or making the repository public.
- Running CI on every push. S10 is a separate decision.

## Decisions the owner should make before or alongside approval

None of these blocks the computation, but each blocks public release.

1. Companion code licence [U-LIC-COMPANION].
2. Whether to keep `downloads/splice-shortlist-outputs.zip` in a public repository, given that it
   contains MFASS outcome labels and MFASS declares no licence [U-LIC-MFASS].
3. Optionally, supply the IPO9 and COL1A2 variant IDs so the case claims can be checked
   [U-CASE-IDS]. Otherwise they stay "imported, unverified".
4. Whether the GTF is verified by the companion's MD5 or by a SHA-256 recorded on first fetch
   (scaffold task S3).

## Order of work

1. The engineer implements S1 to S9 without executing the experiment.
2. The engineer enumerates the zip members [U-ZIP-MEMBERS] and fixes the R7 file list.
3. The owner reviews the final `protocol.md` and approves it with the CLI.
4. The harness runs Tier 1 once.
5. The `reproduced` paper mode is built from the results.
