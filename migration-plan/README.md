# Migration plan

This is a design-only package. It was prepared on 2026-10-06 and revised the same day to apply review
corrections C1 to C13. No experiment was run, and no approval is claimed. Nothing has been reproduced
or verified. The harness engineering (scaffold S1 to S10) is still pending.

| File | Purpose |
|---|---|
| `../protocol.md` | Reproduction protocol, draft v2 (UNAPPROVED). Covers scope, replay versus inference, data and licences, exact commands, tolerances, budgets, stopping rules and uncertainty |
| `review-disposition.md` | Maps corrections C1 to C13 to where they were applied, and lists the owner-scope deviations |
| `approval-request.md` | The bounded scope the owner would approve: one original analysis, one clean reproduction and one paper build, ready for review |
| `evidence-map.json` | Maps every imported number to its source, evidence type, manuscript location and reproduction check. Lists the unresolved evidence |
| `paper-outline.md` | LaTeX manuscript outline with separate imported and reproduced build modes |
| `blog-outline.md` | Outline for an accessible post of 1,000 to 1,500 words |
| `scaffold-replacement.md` | Engineering tasks that replace the synthetic π fixture |

Inputs read:
- `article/original.md`;
- `companion/` (README, NOTICE, pyproject, script and tests);
- `evidence/import-manifest.json`;
- `MIGRATION.md`;
- the original workspace's delivery report and archive clean-run receipt, for runtimes (summarised;
  no private logs or paths copied);
- `migration-review/review.md` and `migration-review/proposed-protocol-corrections.md`;
- `study.json`.

Source discovery and the original drafting pipeline were not repeated. The earlier designer pass
failed only its return contract. Its artifacts were kept and revised in place.
