# Migration plan

This is a design-only package, prepared on 2026-10-06. No experiment was run. No approval is
claimed, and nothing has been reproduced or verified.

| File | Purpose |
|---|---|
| `../protocol.md` | Reproduction protocol (UNAPPROVED). It covers scope, replay versus inference, data and licences, exact commands, tolerances, budgets, stopping rules and uncertainty |
| `evidence-map.json` | Maps every imported number to its source file, evidence type, manuscript location and reproduction check. It also lists the unresolved evidence |
| `paper-outline.md` | LaTeX manuscript outline with separate imported and reproduced build modes |
| `blog-outline.md` | Outline for an accessible post of 1,000–1,500 words |
| `scaffold-replacement.md` | Tasks that replace the synthetic π fixture |
| `approval-request.md` | The smallest owner approval needed for harness reproduction |

Inputs read:
- `article/original.md`;
- `companion/` (README, NOTICE, pyproject, script and tests);
- `evidence/import-manifest.json`;
- `MIGRATION.md`;
- the original workspace's delivery report and archive clean-run receipt, for runtimes. These are
  summarised here, and no private logs or paths are copied.

Source discovery and the original drafting pipeline were not repeated.
