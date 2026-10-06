# Independent review of the imported-evidence manuscript

- **Reviewer:** Claude Opus (model `claude-opus-5-5`), an independent instance that did not write the
  manuscript. Single agent, no sub-agents. Date: 2026-10-06.
- **Object reviewed:** `paper/main.tex`, `paper/references.bib`, `paper/generated/*.tex`, and
  `paper/build/main.pdf` (24 pages; SHA-256 `cb0ee469…2b71` per `build-receipt.json`).
- **Status of this review:** an automated AI review. It is not human scientific review, and it does not
  verify, approve or reproduce any result.

## Scope and what I did

**Files read in full or in the relevant parts:**
- `article/published-original.md`, and a `diff` against `article/original.md`, which differs only in local links;
- `paper/main.tex` (all 1,034 lines), `paper/references.bib`, all 16 files in `paper/generated/`, and `paper/build/main.bbl`, `main.log` and `warnings.txt`;
- under `evidence/paper-migration/`: `build-receipt.json`, `status.json`, `content-coverage.md`, `matched-study-contrasts.json` and `claims-ledger.json`. For the ledger I checked that every manuscript label it points to exists;
- `companion/README.md`, `companion/NOTICE.md`, and `companion/splice_shortlist.py` lines 381–430 and 505–534;
- `migration-review/review.md` §3 (the methods critique), the head of `protocol.md`, the relevant lines of `migration-plan/paper-outline.md` and `evidence-map.json`, `README.md`, `Makefile` and `.gitignore`.

**Archived metrics (read-only).** I printed values from `downloads/splice-shortlist-outputs.zip` with `unzip -p`, covering:
- `metrics.json` for `out`, `out-b25`, `out-b300`, `out-selected-b100` and `out-tutorial`;
- `runs/controls/receipt.json`;
- `out/decision-table.md` and `runs/evaluate-b100-P0.log`.

This was lookup and formatting only. I computed no statistics. The only arithmetic was sums and differences of archived point values, used for consistency checks.

**Matched-study transcription.** I checked the four newly transcribed values against the published
files. I read the files read-only with `git show 093fd1ae…:benchmarks/mfass/results/matched-annotation-v1/contrasts/{S1-S0,P1-P0,P0-S0}.json`
in the existing local checkout `../rewire-benchmarks`. No network was used.
- All three files and the README match the SHA-256 digests recorded in `matched-study-contrasts.json`.
- All nine intervals, including the four new ones, round correctly from the file values.

**Embedded supplement.** The PDF contains one attachment, `S1-published-original.md`. I extracted it
temporarily with `pdfdetach`, compared it and deleted it. It is byte-identical to `article/published-original.md`
(SHA-256 `5d47e526…57d6`).

**Pages viewed.** I rendered the PDF with `pdftoppm` into `/tmp/splicing-review/` and viewed the images with the Read tool:
- all 24 pages at 50 dpi;
- pages 10, 12 and 23 again at 110–130 dpi;
- higher-resolution crops of page 13 (the Figure 5 forest plot) and page 18 (the Appendix A command listing).

Rendering worked; nothing about it limits these findings.

**Not done:**
- no `make`, `uv`, companion command, build, inference, bootstrap or refit;
- no network fetch, so I re-retrieved no literature source.

## Overall assessment

The manuscript is a faithful and careful conversion, and in most respects it is in good shape.

**Numbers.** Every number I checked agrees with the original article and with the archived `metrics.json` and
`receipt.json`:
- the generated Tables 2–4 and 6–8, the appendix tables and the in-text values;
- signs, rounding and tie ranges;
- the 41-interval inventory;
- the derived counts (51/61, 57/65, 36/38, 43/45, 173/314, yields at 300, download sums).

The four transcribed matched-study values are correct against the published files at `093fd1a`. Their AUROC
point values also equal differences of the archived per-configuration AUROCs.

**Policy compliance:**
- The title-page status box states that these are existing results and that reproduction is pending.
- Post hoc budgets are marked throughout.
- Every negative or null result, limitation and licence statement in the original is present.
- The original is embedded unchanged.
- The bibliography follows the original's Sources list.
- There are no personal paths and no `??` references.

**What needs fixing.**
- One sentence in §2.4 adds a literature claim that is not in the original and that I believe is wrong (F1).
- The status box and §4.9 misstate which protocol draft was reviewed, and do not say on the title page that the review was automated (F2).

The remaining findings are minor or cosmetic.

**Counts:** 0 blocking, 2 major, 8 minor, 9 nits.

## Findings

### F1 (major): unsupported, probably incorrect literature claim about CAGI5, plus a new novelty claim

**Location:** `paper/main.tex` lines 207–210 (§2.4 "Other benchmarks", PDF p. 4).

**Evidence:**
- The manuscript says: "The CAGI5 splicing challenge~\citep{mount2019cagi5} assessed predictions of MFASS and Vex-seq outcomes".
- The original cites CAGI5 only for the quotation "cannot directly imply clinical significance". The evidence-map and ledger item L-CAGI5 covers only that quotation.
- As far as I know, the CAGI5 splicing challenges were Vex-seq and MaPSy, not MFASS. MFASS was published in 2019, after CAGI5. I did not re-retrieve the source to confirm this.
- The next sentence, "Neither evaluated SpliceAI or Pangolin at a fixed budget on a common scored population with paired intervals, which is the question here", is a new novelty claim. Neither the original nor the ledger supports it.

**Fix:**
- Limit §2.4 to what the original supports. MMSplice reported precision–recall curves on MFASS, each tool on its own scored subset (Figure 1 caption). The CAGI5 assessors caution that "predicting a splicing assay cannot directly imply clinical significance".
- Delete the "assessed predictions of MFASS and Vex-seq outcomes" clause and the "Neither evaluated…" sentence. Alternatively, verify both against the sources and add a ledger entry.

### F2 (major): the review status of the reproduction protocol is misstated, and on the title page it is unqualified

**Locations:**
- Status box, `main.tex` lines 80–81 (p. 1): "the reproduction protocol in the repository is a reviewed but unapproved draft".
- §4.9, lines 639–640 (p. 13): "`protocol.md`, draft v2) has been reviewed by an automated methods reviewer".

**Evidence:**
- `migration-review/review.md` line 1 says the review covered "`protocol.md` draft v1", at snapshot `108d850`.
- `protocol.md` lines 3–7 say that draft v2 applies corrections C1–C13 arising from that review. Draft v2 has not itself been reviewed.
- `evidence/reviews.json` has `"reviews": []`.
- On the title page, an unqualified "reviewed" can be read as human review, which the policy forbids implying.

**Fix:**
- Status box: "the reproduction protocol (`protocol.md`, draft v2, unapproved) incorporates corrections from an automated AI methods review of draft v1 and has not been executed".
- Mirror this wording in §4.9 and in `README.md` line 17.

### F3 (minor): the junction-distance bands and overlap counts are labelled "post hoc" without support

**Locations:** §3.8, `main.tex` lines 348–350; Table 7 caption, line 595 ("Descriptive and post hoc").

**Evidence:**
- The original marks only budgets 25 and 300 as post hoc, plus the `kmer_cons_selected` run as "a separate run after the analyses above".
- For the bands, the original says only that no band intervals were computed and that "`evaluate` prints this breakdown for every configuration". Nothing in the evidence says they were chosen after the outcomes were seen.
- The label is conservative, but it changes the analysis status the original reported.

**Fix:**
- Describe the bands and overlap as "descriptive, not pre-specified; no intervals". Keep "post hoc" only where the original uses it: budgets 25 and 300.
- The top-300 band columns can keep "post hoc" because they inherit it from the post hoc budget.

### F4 (minor): masked SpliceAI's AUROC interval is never stated to exclude zero

**Locations:** §4.2, lines 444–446; §4.3, lines 453–454 (pp. 9–10).

**Evidence:**
- The original says the interval +0.037 [+0.005, +0.070] "barely excludes zero among many unadjusted intervals".
- The manuscript follows the methods critique (`migration-review/review.md` lines 268–272) and writes "lower bound at or near zero… should not be read as an established difference". It never says that the interval as reported excludes zero.
- A reader who sees only the text cannot tell that this is the one non-Pangolin interval with both bounds above zero.

**Fix:** "excludes zero only marginally (lower bound +0.005, at or near zero; Monte Carlo error not quantified) among 41 unadjusted intervals, so it is not read as an established difference." Do the same for +0.003 in §4.3.

### F5 (minor): some practical guidance from the original is weakened or missing

**Evidence:**
- (a) The original says, after the CYFIP1 example: "Do not complement a mismatched base unless the mapping orientation and sequence context have been validated." It appears only inside the Appendix E flowchart node, not in §3.9 or §6.
- (b) The original bullet "`kmer_assay` (P@100 0.570) needs no conservation" is missing. §5.1, line 652, says "The supervised baseline needs same-design labels and conservation tracks", which is true only of `kmer_cons`.
- (c) Table 9, line 683, merges the original's row 5 into "Any other fraction". The original row explicitly covered "No labels at any fraction other than about 1.2%", which includes no-label lists at 0.3% and 3.6%. Every other row in Table 9 is labels-specific, so no-label users at 0.3% or 3.6% now have no clearly matching row.
- (d) Table 9 drops two cross-references the original had: Table 2 for the distance and specialist yields in row 2, and Table 3 for "No interval excludes zero" in row 4.

**Fix:**
- Add sentence (a) to §3.9.
- Add (b) to §5.1.
- Relabel the Table 9 row as "Labels at a fraction other than ≈0.3/1.2/3.6%, or no labels at a fraction other than ≈1.2%".
- Restore the two table references.

### F6 (minor): the Appendix A command listing is not safe to copy and is not exactly "as recorded"

**Location:** p. 18, `main.tex` lines 773–790.

**Evidence:**
- With `breaklines=true`, long lines wrap inside tokens without a continuation character: `--out out-` / `b300`, `--method` / `P0 --out out-tutorial`, `scipy` / `1.17.1`, and `SHA-256` / `mismatch`.
- If the listing is pasted into a shell, these break the commands, or run the comment remnants (`mismatch`, `1.17.1`) as commands.
- The text says "The commands below are those recorded in the original article". The listing actually merges `unzip` and `cd` with `&&` and adds a `\` continuation that the original does not have.

**Fix:**
- Drop the trailing comments, or move them to prose.
- Use `\footnotesize` or a smaller font, or break lines manually with `\`, so that no token wraps.
- Say "adapted from the original (unzip and cd joined; one line continued)".

### F7 (minor): the cross-check scope is overstated

**Locations:** §3.10, lines 385–386 ("every generated value is cross-checked against the original article"); Appendix F, lines 1026–1027.

**Evidence:**
- Many generated values do not appear in the original, so they cannot be cross-checked against it. Examples: recall, the "Reg." column, curve values at budgets other than 10/25/100/300, Tables 12–17, and the validation grid.
- `extraction-receipt.json` limits the cross-check to evidence-map items T2–T6, C-POP, C-OVERLAP, F4 and M-STUDY.
- (I checked the remaining values against the archive myself and found no errors.)

**Fix:** "every generated value that also appears in the original article (evidence-map items T2–T6, C-POP, C-OVERLAP, F4, M-STUDY) is cross-checked; the remaining values are formatted directly from digest-checked archive members."

### F8 (minor): bibliography entries add details that are not in the original Sources list

**Locations:** `paper/references.bib`, entries `pangolin_repo` and `uv`; reference 8 as rendered.

**Evidence:**
- `pangolin_repo` gives `author = {Zeng, T.}`. The original names no author for the repository. The policy says no guessed authors.
- `uv` adds the subtitle "Python package and project manager". The original has only "Astral. uv."
- `unsrtnat` lowercases "Splicing Subgroup" in the Walker title to "splicing subgroup" (p. 17).

**Fix:**
- Use `author = {{tkzeng}}`, or omit the author for the repository, matching the GitHub owner in the URL.
- Reduce `uv` to "uv".
- Brace `{Splicing Subgroup}`.

### F9 (minor): content-coverage.md miscounts the bibliography

**Location:** `content-coverage.md` line 51: "`paper/references.bib` (24 entries…)".

**Evidence:** `references.bib` and `main.bbl` both contain 23 entries, all of which are cited. The other section, table and figure numbers in the coverage map match the PDF: §2.1–§8, Tables 1–17, Figures 1–6 and Appendices A–F.

**Fix:** Change 24 to 23. Also fill in the empty "Scientific content" cell on line 37.

### F10 (minor): the selection flowchart is barely legible at print size

**Location:** Appendix E, p. 23.

**Evidence:** At 120 dpi the node text is about 4–5 pt equivalent. It is readable only when zoomed in and would be illegible in print. Edge labels such as "about 0.3% (tested at 25, post hoc)" are smaller still.

**Fix:** Either re-export the SVG with larger fonts, which needs an owner decision because it is an original figure, or note in the caption that Table 9 gives the same routes in readable form. Table 9 is already referenced.

### F11 (nit): bibliography rendering artefacts

**Location:** references 11, 12, 14, 15, 16, 20 and 22 (pp. 16–17).

**Evidence:** These render as "GitHub, . URL". This comes from the empty-year `\natexlab` suffix. The 16 BibTeX "empty year" warnings in `warnings.txt` are otherwise benign.

**Fix:** Add `year = {n.d.}`, or use a style or `note` field that suppresses the stray separator.

### F12 (nit): the landscape page's running header is rotated

**Location:** p. 23.

**Evidence:** The `pdflscape` page keeps the portrait header and footer. In a viewer, the header runs vertically down the right edge and the page number sits on the left edge.

**Fix:** Use `\thispagestyle{empty}`, or the `fancyhdr`/`pdflscape` header-rotation idiom, on that page.

### F13 (nit): the zero-share percentages are rounded inconsistently

**Location:** Table 15 (p. 22), `paper_extract.py` line 178.

**Evidence:** Exact half values in the archive round in different directions because of float representation:
- 0.0785 → 7.8%, but 0.0805 → 8.1%;
- 0.0615 → 6.2% and 0.0625 → 6.2%;
- 0.0455 → 4.5%, but 0.0915 → 9.2%.

**Fix:** Print two decimals. Shares are multiples of 1/2000, so 7.85% is exact. Alternatively, print counts out of 2,000.

### F14 (nit): the PDF creation date disagrees with the title page

**Evidence:** `pdfinfo` reports CreationDate 2026-09-30, from `SOURCE_DATE_EPOCH=1790726400`. The title page says the manuscript was "compiled … October 2026".

**Fix:** Set the epoch to the build date, or say in `build-receipt.json` that the date is pinned to the original run date.

### F15 (nit): the interval count does not mention the tutorial intervals

**Location:** §3.7, lines 340–344; Table 17.

**Evidence:** The manuscript says it reports 41 intervals, but Table 17 prints 12 more (the tutorial subset, 200 draws).

**Fix:** Write "41 substantive intervals; Table 17's 12 tutorial intervals are a pipeline check and are not counted or interpreted".

### F16 (nit): realised depth is not stated next to the P@k intervals

**Location:** Table 3 and Table 4 captions.

**Evidence:** The methods critique (lines 264–267) asks for the realised review depth (83–126 at 100, and so on) to be repeated next to every P@k interval. It is stated in §3.7, Table 16 and the Figure 5 artwork, but not in these captions. The matched-study files also use the same fraction rule (realised depth 83–126), and Table 5's caption could say so.

**Fix:** Add "each draw keeps the fraction k/8,297 (realised depths in Table 16)" to the captions of Tables 3, 4 and 5.

### F17 (nit): small wording overreaches

**Evidence:**
- §3.10, line 375, says "Every companion command was executed". The original says "Every other command": the `--budget 60` example was not executed, as Appendix A correctly notes.
- Contribution (iv), line 132, says the companion "regenerates every control score and metric". This should be past-tense historical ("was reported to regenerate"), because reproduction is pending.
- Contribution (iii) says "silently corrupts scores". The original says it "would have scored them without warning".

**Fix:** Align the wording with the original.

### F18 (nit): no exploratory qualifier on the §4.2 heading

**Location:** §4.2 heading, "Whole-list metrics favour Pangolin".

**Evidence:** The original's excerpt frames this result as "exploratory and unadjusted". The heading has no qualifier, and the section body does not repeat it for Pangolin.

**Fix:** Rename the heading to "Whole-list metrics favour Pangolin (exploratory, unadjusted)".

### F19 (nit): the AI disclosure is written in the future tense and leaves out AI-produced documents

**Location:** §8, lines 757–759.

**Evidence:**
- "is to be reviewed by an independent AI reviewer instance" will be stale once this review exists.
- The disclosure does not say that the reproduction protocol and its methods review were also produced by AI agents (`protocol.md` line 3; `migration-review/review.md` line 3).
- The Figure 6 caption cites the D2 source as `06-selection-flowchart.d2` without its path, `article/assets/`.

**Fix:**
- After disposition, change the sentence to the past tense and cite `evidence/paper-migration/review.md`.
- Add one clause on the AI-authored protocol and methods review.
- Give the full path to the D2 source.

## Verified without findings

- **Abstract and §4.1 numbers:**
  - 61 versus 63–66 per 100;
  - +0.040 [−0.038, +0.120];
  - about 7 fewer to 13 more per 100;
  - +0.000 to +0.030 against the selected baseline;
  - AP +0.102 [+0.061, +0.142].
- **Generated tables against the archive:**
  - Table 2, including Reg., Tied and Recall;
  - Tables 3 and 4: every cell, plus the tie-order shifts at 300 (−0.017/+0.007, −0.007/+0.010);
  - Table 6 and Table 7;
  - Table 8: 30.81 s, 278.1 MB, 6,921/6,102/19,153/18,655 s;
  - Table 10, and the 1.13/1.14 GB download sums;
  - Tables 11–14, 16 and 17.
- **Matched-study contrasts:**
  - Table 5 matches `contrasts/*.json` at `093fd1a`;
  - the 22.5% and 44.4% zero shares are as quoted in the original;
  - lower bounds of exactly 0.000 are plausible, since fewer than 2.5% of draws are negative.
- **Methods details against the code:** the equation in §3.6 and the Appendix B listing match `budget_precision` (lines 511–527 verbatim). The model settings in §3.4 (300 iterations, L2 1.0, the grid, 3-mer frequencies in a 21 bp window) match `splice_shortlist.py`, and `splice_shortlist.py` is identical to the copy in `downloads/splice-shortlist.zip`.
- **Original content carried over:** every original limitation, the licence paragraph, the "what would change" paragraph, the three CC BY 4.0 figures with attribution, and the two original data figures.
- **Build:** 0 LaTeX warnings, no overfull boxes in `main.log`, no unresolved references, and 23 of 23 bibliography entries cited.
- **Privacy:** no personal paths or credentials in the tex, bib, generated files or the PDF text.

## Author disposition

_To be completed by the paper author._
