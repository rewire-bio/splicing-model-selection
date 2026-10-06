# Content coverage: original article to manuscript

Original: `article/published-original.md` (byte-identical published copy; SHA-256
`5d47e526d9f60353a947292caa4cf54ebafe20dd2460a441925846e0bdff57d6`), title *Choosing a Splicing Score
for a Fixed Minigene Budget: Baseline, SpliceAI and Pangolin on MFASS* (30 September 2026).
Manuscript: `paper/main.tex` → `paper/build/main.pdf`. The original is retained unchanged as
Supplement S1 (repository file and PDF attachment `S1-published-original.md`).

Numbers in manuscript tables are generated from the archived outputs zip by
`scripts/paper_extract.py`, which stops the build if any value differs from the article's value as
transcribed in `migration-plan/evidence-map.json` (T2, T3, T4, T5, T6, C-POP, C-OVERLAP, F4, M-STUDY).
Recorded result: 0 mismatches (`paper/generated/extraction-receipt.json`).

| Original section / element | Scientific content | Manuscript location | Notes |
|---|---|---|---|
| Front matter: title, excerpt | Headline counts (61 vs 63–66 of 100), no difference at 100, Pangolin whole-list exploratory | Title, status box, Abstract | Wording restructured; numbers identical |
| FAQ 1 (beat a simple baseline?) | 61 vs 63–66; intervals include zero; about 7 fewer to 13 more per 100; exploratory | Abstract; §4.1; §5.1 | |
| FAQ 2 (Pangolin better anywhere?) | AP +0.102 [+0.061, +0.142]; P@300 post hoc | Abstract; §4.2; §4.5; §5.1 | |
| FAQ 3 (were tools run?) | Saved-score replay; ~14 h recorded; controls computed locally | Abstract; §3.3, §3.5; §4.8; App. A | |
| FAQ 4 (27 missing) | 23 orientation + 4 ARHGEF3; not author-confirmed | §3.2; §3.9; Limitations | |
| FAQ 5 (100/300 as rule?) | 1.2% and 3.6% of 8,297 at 3.8% prevalence; needs own validation | §4.5; §5.2 and Table 9 | |
| FAQ 6 (pathogenic?) | MFASS is minigene exon recognition in HEK293T; no patient/pathogenicity claim | Abstract; Limitations (Reporter to patient); Table 9 last row | |
| Lead paragraphs | Configurations, population, P@100 values, paired difference for P0, range of intervals, exploratory, replay | Abstract; §1; §4.1 | |
| Disclosure paragraph | Own benchmark project; Claude ran commands and drafted; automated review; no human review | §8 (AI assistance, review and disclosure) | Extended with this manuscript's drafting/review |
| "At a glance" table | Five decision rows with evidence and caveats | Table 9 (`tab:glance`) | Two rows added from "Which configuration" bullets (all-variants coverage; patient RNA) |
| §"The decision is how many disrupting variants land in your first k" | MFASS design and SDV definition; 27,733 / 1,050 / 83%; P@k rationale; random 100 ≈ 4; AP/AUROC; thresholds (Smith & Kitzman; ClinGen; SpliceAI README); definition of "no difference established"; protocol improvement rule not applied | §2.1; §2.3; §3.6; §3.7 | |
| Figure 1 (Cheng et al. Fig. 2) | MFASS reporter schematic, CC BY 4.0 | Figure 1 | Embedded with original attribution |
| Figure 2 (Smith & Kitzman Fig. 5) | Threshold variability | Figure 3 | Embedded with attribution |
| §"The configurations see different inputs" + Table 1 | Workflows not architectures; inputs; labels; evidence type; hyperparameters (0.06/31; selected 15 leaves, 0.1 for kmer_cons); byte-identical refit; GENCODE 44 canonical; Pangolin patch (issue #29); mask semantics and defaults | Table 1; §3.3–3.5; §2.2 | Validation grid added as App. Table 14 from `runs/controls/receipt.json` (formatting only) |
| Figure 3 (Smith & Kitzman Fig. 6) | Masking/annotation background effects (11,795 / 8,719; 280 / 270) | Figure 2 | Embedded with attribution |
| §"The evaluation population is 8,297 of 8,324" | split-v2; 8,324/315/463; 8,297/314/460; exclusion causes; interval inventory (9 + 20 + 12); bootstrap 2,000, seed 20260914, fraction rule, realised depths; registered tie order; post hoc budgets | §3.1, §3.2, §3.7, §3.8; App. Table 16 | |
| §"One variant passes the scoring checks…" console blocks | DDX1 pass; CYFIP1 fail (135 vs 0 mismatches); ARHGEF3 outside span; 7,770 reverse-complemented; MFASS issue #1; do not complement mismatches | §3.9; App. C (verbatim console output); §3.1 | |
| Ties paragraph and budget-25 shortlist | SpliceAI 7 at 1.00 (3 disrupting), 23 at 0.99 (19) for 18 slots; P@25 0.68–0.84; registered order gives 17; P1 3 tied at 0.54 for 2 slots; 30-row shortlist | §4.6 | |
| `budget_precision` code | Verbatim function | §3.6 (equations); App. B (verbatim listing from `companion/splice_shortlist.py` lines 511–527) | |
| Overlap and case variants | kmer_cons/P0 share 61; S0/P0 88; IPO9 and COL1A2 ranks | §4.6; App. Table 13 (full overlap matrix from archive) | Case ranks flagged as article-text-only, not re-checked |
| §"At 100 experiments…" + Table 2 | P@100, tie ranges, AP, AUROC, time, data per configuration | Table 2 (metrics); Table 8 (resources); App. Table 10 (downloads); §4.8 | Resource columns split into separate table with exact archived values (30.81 s, 278.1 MB) |
| Control-resource paragraph; replay 1e-12; distance tie (171, 23) | Controls ~30 s, ~300 MB (build ~680 MB), 80 MB data; specialist times recorded by the study; replay matches study AP/AUROC to 1e-12; distance rule's 171-way top tie (23 disrupting) | §4.1; §4.8; §3.5 | |
| Table 3 | Paired differences vs kmer_cons at 25/100/300, AP, AUROC; tie-order sensitivity | Table 3 | |
| Paragraphs after Table 3 | −0.069 to +0.133; matched-study three contrasts; 22.5%/44.4% zero draws; P0−S0 +0.020 [−0.033, +0.083]; AP/AUROC; masking; S1 AUROC barely excludes zero | §4.1; §4.2; §4.4 and Table 5 | Table 5 completes the 9 matched-study intervals by transcription (see `matched-study-contrasts.json`); S1 AUROC phrased "at or near zero" per methods critique |
| Table 4 | Contrasts vs kmer_cons_selected | Table 4; §4.3 | |
| §"The answer depends on the budget" + Figure 4 | Budget curve; fractions 0.3/1.2/3.6%; SpliceAI 0.548 at 10 | Figure 4; §4.5; App. Table 11 (full curve values) | |
| Table 5 | P@25/100/300 with tie ranges | Table 6 | |
| Budget-25 and budget-300 paragraphs | Fragile point estimates; yields 100/105/110/137/145 with tie ranges; only Pangolin P@300 intervals exclude zero | §4.5 paragraphs | |
| Figure 5 | Forest plot | Figure 5 | |
| Table 6 + paragraph | Junction-distance bands | Table 7; §4.7; App. Table 12 (all configurations at 25/100/300) | |
| §"Which configuration to use, by situation" + Figure 6 | Recommendations by situation; flowchart | §5.2; Table 9; App. E (Figure 6, landscape) | |
| §"Reproduce the shortlist" | Companion contents; outputs zip contents; requirements; commands; expected build output; 2,198 vs 2,185 exons; controls/annotation outputs; tutorial subset; options; executed by Claude on M4 29–30 Sep 2026; clean-archive byte identity; specialist inference route and downloads | App. A; §3.10; §3.1; App. Table 10; App. Table 17 (tutorial) | Commands reproduced as recorded; not re-executed |
| §"Limits and failure cases" | Coverage; assembly; ties; exploratory/budgets; reporter to patient (13 of 19; CAGI5); labels and replay; review | §6 Limitations (all items retained) | Added: Monte Carlo error, overlap not audited, imported case values, platform (from evidence map / methods critique) |
| Licence paragraph | Pangolin GPL-3.0; SpliceAI PolyForm/CC BY-NC vs PyPI GPLv3; MFASS no licence | §7 | |
| §"What would change this recommendation" | Prospective registration; Pangolin vs SpliceAI; withdrawal condition; liftover correction | §5.3 | |
| §"Sources and artifacts" (13 entries) | Bibliography | `paper/references.bib` (23 entries; repository/licence/issue links split into separate entries) | No DOI added beyond the original; author initials as in original |

## Additions beyond the original article (all from archived evidence; no new computation)

- Table 5: four matched-study interval values not quoted in the article, transcribed from the
  published study files at `093fd1a` (resolves evidence-map item U-MSTUDY-MISSING).
- Appendix Tables 11–17: full budget curve, all-configuration bands, top-100 overlap matrix, validation
  grid, share of zero-difference draws, bootstrap design per run, tutorial-subset contrasts — formatted
  from archive members so that every archived output is accounted for.
- Recall at 100 and registered-order P@100 columns in Table 2.

## Not carried into the manuscript body (retained in Supplement S1)

- Reader-facing FAQ phrasing and blog front-matter fields (SEO title, tags). Their scientific content is
  covered above.
- Site-relative download links (`/downloads/...`); the manuscript names repository paths instead.
