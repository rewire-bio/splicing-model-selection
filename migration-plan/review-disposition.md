# Review disposition: corrections C1 to C13

Prepared 2026-10-06 by the research-designer role (`claude-opus-5-5`, single agent, no child agents).
Snapshot: `78eb4628b6553aeba853f33634b7d85a62ac42dd`.

Inputs:
- `migration-review/proposed-protocol-corrections.md`;
- `migration-review/review.md`;
- `study.json`;
- `companion/README.md`.

All 13 corrections were applied to the unapproved draft, which produced `protocol.md` draft v2.
Nothing was executed. No code, input, `study.json` or harness record was changed, and no approval is
claimed. Because the edits come before approval, none is a post hoc amendment.

| C# | Finding | Applied at |
|---|---|---|
| C1 | B1 | `protocol.md` §4: the opening paragraphs replaced with the exact wording (what is and is not redistributed; MFASS-derived content of the retained zip); the "Imported reference outputs" row; note that the NOTICE covers `companion/` only. `evidence-map.json` A_outputs `mfass_derived_content` and U-LIC-MFASS |
| C2 | B3.4 | `protocol.md` §3.2 R3 (full SHA-256 `2f3117c2…23eb`, equal to `PINNED`); §4 table; §6.1 item 2 (static pre-run digest check). `evidence-map.json` C-KMER-BYTE |
| C3 | B2 | `protocol.md` §3.2 R7: the fixed 21-file set, the files excluded from byte comparison, 39 entries, per-member SHA-256 before approval, git-ignored extraction. `evidence-map.json` A_outputs and U-ZIP-MEMBERS |
| C4 | B3.2, B4 | `protocol.md` §8.3 score-identity gate (three cases, including "Partial reproduction (byte identity not preserved under the 4-thread cap)") and receipt fields; §11 outcome class. `evidence-map.json` U-PLATFORM |
| C5 | B3.1 | `protocol.md` §8.2 bootstrap-endpoint row (1e-12 for specialist/replay; 1e-9 if the gate passes; observed values with the 1/cap step if it fails); the other control rows are conditioned on the gate |
| C6 | B3.3, B3.6 | `protocol.md` §8.2 "Precedence" paragraph (display-boundary difference); R6 resource exclusion in §3.2 R6 and §8.2; override of the `study.json` global tolerances |
| C7 | B5 | `protocol.md` §6.2 (single shared `UV_CACHE_DIR`); §9 Network row (uv.lock wheels, CPython 3.11 with the source recorded); §10 rule 5 rewritten; §6.4 paper toolchain outside Tier 1. *Deviation:* see below |
| C8 | B6 | `protocol.md` §6.2: `check-variant` moved after `pytest` and classified as a live external check (exit 0 for all three; match, mismatch or unavailable; network failure outside rule 3); §3.2, §10 rule 3, §11, §12. `evidence-map.json` C-CHECKVAR, C-BUILD and C-GTF sources set to "article text only (not in outputs zip)" |
| C9 | B11 | `protocol.md` §9 precedence row (2,700 s overrides the per-command sum of 4,660 s) and the `study.json` values list. `scaffold-replacement.md` S7. `approval-request.md` |
| C10 | B7 | `protocol.md` §6.4: reproduced mode for any ended run (banner class; pass, fail, discrepancy or not run; imported values never overwritten); "not buildable yet" paragraph. `paper-outline.md` build-modes table and §5.8. `scaffold-replacement.md` S9 |
| C11 | B10 | `protocol.md` §4 "Data manifest and fetch path" (git-ignored data paths; single fetch path). `scaffold-replacement.md` S3 (adds the Makefile `data`-ordering consequence) |
| C12 | B8, B9 | `scaffold-replacement.md`: fixture inventory corrected to the snapshot; seed-20261001 acceptance check; S5 changed to "create `tests/`"; S10 set to `workflow_dispatch` with ≥ 45 min, placed before or with S1; CI stays a separate owner decision. `approval-request.md` pending-engineering step 2 marks the zip members as enumerated (39 entries) and keeps "record per-member SHA-256" |
| C13 | Review §3.4, §3.6 | `protocol.md` §11 (`evidence_class` and `historical_source`); §13 (three limitations, plus U-CASE-IDS and baseline fairness from review §3.2); §7 near-zero reporting rule. `evidence-map.json` `evidence_class_rule` and U-MC-ERROR. `paper-outline.md` §5.8 |

## Deviations and additions requested by the owner's scope (not from C1 to C13)

These come from the task brief, not from the review. They are listed so that the reviewer can check
them.

1. **Disk accounting for the paper toolchain (affects C7).** C7 excludes Tectonic from both the time
   and the 2 GB accounting. The owner's scope sets "≤ 2 GB aggregate additional storage across all
   stages". The paper toolchain is therefore **excluded from the time caps**, as C7 says, and capped
   separately at 600 s, but it is **included in the 2 GB disk aggregate**. That is the stricter
   reading.
2. **Two approved executions.** The scope was made concrete as A (one original analysis, ≤ 2,700 s),
   B (one clean reproduction, ≤ 3,600 s excluding the paper) and P (one paper build, ≤ 600 s),
   added in §6.0. Rules for whether B runs after A stops are in §10. No new quantity is computed: A
   and B use identical commands, seeds and tolerances.
3. **Disk preflight and floor.** At least 3 GiB free before each stage, and stop before free space
   falls below 1 GiB (§6.1 item 3, §9, §10 rule 4).
4. **Retries.** At most 2 attempts per command (one retry), only for transient or network failures,
   and within the caps (§9). This is consistent with `max_attempts` 2 in C9 and with C8.
5. **Publishing.** The owner authorised the public repository on 2026-10-06. The redundant request for
   permission to publish, push or go public was removed from `approval-request.md`. The licence
   uncertainty (U-LIC-MFASS, U-LIC-COMPANION, U-LIC-SPLICEAI) is still recorded openly, and no legal
   permission is inferred from the authorisation (§4, §14; `approval-request.md` licence table).
6. **Manuscript mode** reports discrepancies and stopped runs, not only successes (C10, reinforced in
   §6.4 and §11).

Not changed: the scientific scope, estimands E1 to E5, configurations, seeds, budgets, draws and
tolerance values. No analysis was added.

## Prior designer report

The earlier designer pass on draft v1 failed only its return contract. Its artifacts (`protocol.md`
v1, `evidence-map.json`, `paper-outline.md`, `blog-outline.md`, `scaffold-replacement.md` and
`approval-request.md`) were reviewed and kept. This revision edits them in place and does not replace
them.

## Still pending (future execution dependencies, not design blockers)

- Owner approval through the research CLI, recorded against the commit that contains the engineering
  work.
- Scaffold S1 to S10, with S10 landing before or with S1.
- Per-member zip SHA-256 values.
- Owner decisions on U-LIC-MFASS and U-LIC-COMPANION.
- Optional: U-CASE-IDS.

These are listed in `approval-request.md` and protocol §14.
