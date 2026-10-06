# Repository review, 6 October 2026

Reviewed source: main at `c193edb`. This review checks implementation and imported
evidence; it does not execute the proposed scientific reproduction.

## Findings and fixes

- [Issue 1](https://github.com/rewire-bio/splicing-model-selection/issues/1):
  prediction dictionaries silently overwrote duplicate IDs, accepted nonfinite
  scores and ignored labels/groups; common-population intersection could omit
  variants without an exclusion record. The maintained companion now rejects
  these inputs, incomplete control predictions and overlapping train/test groups
  before fitting or writing evaluation results.
- [Issue 2](https://github.com/rewire-bio/splicing-model-selection/issues/2):
  the root test target used a nonexistent unittest directory and changes had no
  automatic checks. It now runs locked companion pytest. Push/PR CI also checks
  the hash-verified archived metrics against the generated manuscript tables.
- [Issue 3](https://github.com/rewire-bio/splicing-model-selection/issues/3):
  the draft protocol incorrectly described the completed manuscript as a missing
  placeholder. Engineering status now reflects the implemented imported-evidence
  build. Reproduction requires all collected tests to pass without skips, rather
  than requiring the historical test count forever. The paper appendix preserves
  26 as the historical count and distinguishes the maintained regression suite.

## Review coverage and result impact

Examined cohort construction, assay orientation, feature construction, grouped
train/validation/test separation, hyperparameter selection, model fitting, score
joins, tie handling, paired bootstrap, reporting/export, fetch integrity, CLI,
locked dependencies, CI/harness status, manuscript claims and table extraction.

Validation selection uses only training groups. The published-settings and
validation-selected baselines remain separate. Bootstrap draws resample whole
groups, keep the review fraction, and disclose variable realised budgets. The
paper explicitly identifies prior test-outcome inspection, unadjusted exploratory
intervals, post hoc budgets, saved-score replay and unknown specialist training
overlap. The audit found no new basis for invalidating the historical conclusions.

Read-only integrity inspection of the six archived control TSVs and four original
specialist TSVs found that all pass the new score/cohort checks. Specialist files
and exclusion files were retrieved from their pinned URLs and verified against
the existing SHA-256 values; temporary copies were removed. Controls each contain
8,324 rows, specialists each contain 8,297 rows, their common set contains 8,297,
and all 27 excluded IDs match the documented exclusions exactly. No model fitting,
metric calculation or bootstrap rerun was performed during this inspection.

Historical article sources, figures and both download archives are unchanged.
Numerical manuscript tables are unchanged. No numerical blog correction follows
from these fixes. Future instructions should distinguish the maintained companion
from its historical downloadable snapshot.

## Validation and second review

- `make test`: 21 passed, 14 skipped. Skips require fetched/built/fitted scientific
  inputs and are explicitly not evidence of independent reproduction.
- `python3 scripts/paper_extract.py`: six archive members verified, 16 generated
  files, zero mismatches; generated table diff empty.
- `make paper-imported`: 25 pages, zero LaTeX/BibTeX warnings. The changed appendix
  page was rendered and visually inspected.
- Second review checked the new guards against both synthetic malformed inputs
  and original score files; tutorial filtering occurs after full held-out control
  coverage validation. Validation failures occur before output-directory creation.

Independent reproduction remains pending. The experiment/analysis drivers are
explicit disabled stubs, and the data/claim manifests for execution are unfilled.
The full engineering/execution protocol must be implemented and approved before
running that study; this review does not certify specialist inference or authorize
new scientific comparisons. The historical archived code remains available and
has not been rewritten to disguise its provenance.
