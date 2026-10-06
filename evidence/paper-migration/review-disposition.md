# Disposition of the independent review (`review.md`)

Author: paper-author agent (Claude Opus, `claude-opus-5-5`, session `5b2a6d85-2616-43fe-bdde-40dd448ad762`).
Date: 2026-10-06. The review itself is unchanged in `review.md` (owned by the reviewer). All 19 findings were
accepted; none was rejected. After the fixes the manuscript was rebuilt with `make paper-imported`
(25 pages; 0 LaTeX warnings, 0 BibTeX warnings; extraction cross-check 0 mismatches) and the changed pages
(1, 15, 19, 23, 24) were re-rendered with `pdftoppm` at 50 dpi and inspected by the author.

| Finding | Severity | Disposition |
|---|---|---|
| F1 CAGI5/MFASS claim and novelty sentence in §2.4 | major | Fixed. §2.4 now states only what the original supports: MMSplice's per-tool-subset PR curves on MFASS (MMSplice, HAL, SPANR; SpliceAI and Pangolin absent) and the CAGI5 assessors' caution. The "assessed MFASS and Vex-seq" clause and the "Neither evaluated…" sentence were deleted. |
| F2 protocol review status | major | Fixed in the status box, §4.9 and `README.md`: "draft v2, unapproved, incorporates corrections from an automated AI methods review of draft v1; not reviewed, approved or executed itself". |
| F3 bands/overlap labelled post hoc | minor | Fixed. §3.8 now calls them descriptive outputs, not pre-specified, without intervals; Table 7 caption says the top-300 columns inherit the post hoc budget. |
| F4 masked SpliceAI AUROC interval | minor | Fixed in §4.2 and §4.3: "excludes zero only marginally (lower bound at or near zero; Monte Carlo error not quantified) among 41 unadjusted intervals". |
| F5 guidance weakened | minor | Fixed: (a) "do not complement a mismatched base…" added to §3.9; (b) `kmer_assay` needs no conservation, and the `kmer_cons` 30 s / labels-and-tracks point, added to §5.1; (c) Table 9 row relabelled to cover no-label lists at fractions other than 1.2% and labelled lists at other fractions; (d) Table 2 and Table 3 cross-references restored. |
| F6 Appendix A listing unsafe to paste | minor | Fixed. Trailing comments moved to prose, long commands split with backslashes so no token wraps, and the text now says "adapted from the original (unzip and cd joined; comments moved; one command continued)". |
| F7 cross-check scope overstated | minor | Fixed in §3.10 and Appendix F to name the evidence-map items actually cross-checked and say the rest are formatted from digest-checked members. |
| F8 bibliography additions | minor | Fixed: `pangolin_repo` author now the GitHub owner `tkzeng`; `uv` title reduced to "uv"; `{Splicing Subgroup}` braced. |
| F9 coverage count | minor | Fixed: 23 entries; empty cell on the control-resource row filled. |
| F10 flowchart legibility | minor | Partly addressed without altering the original figure: caption states the vector figure can be zoomed and Table 9 gives the same routes in readable form. Re-exporting with larger fonts would modify an original asset and is left as an owner decision. |
| F11 "GitHub, . URL" artefacts | nit | Fixed by `year = {n.d.}` on undated web/repository entries (no date is guessed); the 16 BibTeX empty-year warnings are gone. |
| F12 rotated header on landscape page | nit | Fixed with `\thispagestyle{empty}` on the landscape page; flowchart and caption now fit on one page. |
| F13 zero-share rounding | nit | Fixed: two decimals (exact multiples of 1/2000). |
| F14 PDF creation date | nit | Fixed: `SOURCE_DATE_EPOCH` now pinned to 2026-10-06 (migration date), recorded in `build-receipt.json`. |
| F15 tutorial intervals not counted | nit | Fixed: "41 substantive intervals"; the 12 tutorial intervals are stated to be a pipeline check, not counted or interpreted. |
| F16 realised depths near P@k intervals | nit | Fixed in the captions of Tables 3, 4 and 5. |
| F17 wording overreaches | nit | Fixed: "every command reported… other than one illustrative example marked as not executed"; contribution (iv) now historical with reproduction pending; (iii) now "would have scored without warning". |
| F18 §4.2 heading | nit | Fixed: "(exploratory, unadjusted)" added. |
| F19 disclosure tense and scope | nit | Fixed: past tense with reference to `review.md`; clause added that `protocol.md` and its methods review were AI-written; full path to the D2 source. |

No new experiment, inference, recomputation or network fetch was performed in addressing these findings.
