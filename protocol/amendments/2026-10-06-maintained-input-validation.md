# Maintained-code integrity review before execution

The reproduction protocol remains unapproved and unexecuted. The owner requested
review, issue reporting and fixes across the series repositories on 6 October 2026.

The maintained companion now validates prediction identity, finite scores,
label/group agreement, complete control coverage, exclusion accounting and
train/test group disjointness. These are rejection guards; valid-input ranking,
model selection, bootstrap seeds, budgets and estimands are unchanged. Read-only
checks confirmed the original archived controls and pinned specialist files pass.

Nine added regression cases must pass in addition to the original 26 tests. R8
therefore requires every collected test to pass with no skips; offline CI alone
does not meet R8. No scientific reproduction has been run under this amendment.

`evidence/import-manifest.json` continues to describe the original imported bytes.
Historical code remains in `downloads/splice-shortlist.zip`. When implementing
execution, freeze and record the maintained code revision separately, and retain
historical digest checks for historical artifacts. Do not overwrite the import
manifest to make changed maintained files appear byte-identical to the import.
The pending driver must resolve that distinction and the current local TeX Live
paper build before approval. No execution approval is implied by these fixes.
