# Accessible blog outline (target 1,000–1,500 words)

This is an outline only. The prose will be written later. The original detailed article stays in
`article/original.md` and is not replaced. Every number comes from `evidence-map.json`, with its ID
shown in brackets. Do not add numbers that are not in the map. Keep each caveat next to the claim it
qualifies.

**Working title:** "Picking a splicing score when you can only test 100 variants"
**Standfirst (about 40 words):** You have a list of variants and money for 100 minigene experiments.
Does a big splicing model choose better than a simple trained baseline? On one public assay, at 100,
we could not tell them apart. Whole-list ranking favoured Pangolin.

| # | Section | Words | Content |
|---|---|---:|---|
| 1 | The problem | 150 | A fixed assay budget means the useful number is how many real hits land in your first k picks (precision at k), not a score cut-off. A random 100 from this list would hold about 4 hits. Define "disrupting" in one sentence: the MFASS exon inclusion drops by at least 0.5 [L-MFASS]. |
| 2 | What was compared | 180 | Plain-language descriptions of three kinds of scorer: (a) a model trained on the assay's own labels (`kmer_cons`), (b) SpliceAI and (c) Pangolin, each with masking off and on. There are also two sanity checks (prevalence, distance to junction). State clearly that the SpliceAI and Pangolin scores are *replayed* from published predictions, not rerun [C-REPLAY, U-TIER2]. |
| 3 | Main finding | 220 | At 100 the baseline found 61 hits and the four specialist setups found 63 to 66 [T2]. No paired difference was established. The intervals allow about 7 fewer to 13 more hits per 100 [I-MAIN]. Explain "not established ≠ equal". Over the whole ranked list Pangolin's AP and AUROC were higher [T3]. At 300 its lead was clearer, but that budget was chosen after looking, so treat it as a lead to test [I-P300]. Suggested visual: the forest plot (Figure 5, `article/assets/05-paired-differences-forest.svg`). |
| 4 | Practical use | 220 | Three short "if you…" bullets, based on the article's at-a-glance table: (1) if you have same-design labels and test about 1% of the list, any of these is defensible, so choose on cost and coverage; (2) if you have no labels, start with a specialist after allele, strand and transcript checks; (3) if you test about 4% of the list, pilot Pangolin on outcomes nobody has seen. Fix a tie-break rule before testing. Budgets are fractions of *this* list, not universal thresholds. |
| 5 | One small example | 220 | A tie example, from [C-TIES]. SpliceAI gives two-decimal scores, so at a budget of 25 there were 23 variants tied at 0.99 competing for 18 slots. Depending on which 18 you take, 17 to 21 of 25 picks are real hits. Show a 3-line console snippet (`evaluate --budget 25 --method S1` printing "30 rows for budget 25; 23 tied at the cutoff"). Optional second mini-example: the CYFIP1 variant whose alleles are complemented relative to GRCh38, and why a pipeline should refuse it rather than flip it [C-CHECKVAR, C-EXCL]. Pick only one if over budget. |
| 6 | Limitations | 220 | Five bullets: (1) the endpoint is a minigene reporter in HEK293T cells, not patient RNA or pathogenicity [L-MFASS, L-CAGI5]; (2) the analysis is exploratory and unadjusted, the outcomes had been seen before, and two budgets were chosen post hoc; (3) it covers one list of 8,297 variants at 3.8% prevalence [C-POP]; (4) the specialist scores are replayed and the 27 exclusions include 23 records with a probable liftover defect that the authors have not confirmed [C-EXCL, U-MFASS-CONFIRM]; (5) review so far has been automated only, with no independent human scientific review [U-HUMAN-REVIEW]. |
| 7 | Reproduce it / read more | 120 | Links: the study repository [U-REPO-URL placeholder]; the LaTeX paper PDF [placeholder]; the companion code (`companion/`, `downloads/splice-shortlist.zip`); the detailed original article; rewire-benchmarks matched-annotation study at `093fd1a` (https://github.com/rewire-bio/rewire-benchmarks/tree/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass). Say plainly that the controls take about a minute per evaluation on a laptop CPU and that rerunning the specialists takes about 14 hours, which this work did not do [T2-RES]. |
| 8 | Disclosure | 50 | The study and code come from this site's benchmark project. AI agents ran the commands and drafted text. Licences differ: Pangolin is GPL-3.0, SpliceAI's terms are mixed, and MFASS has no licence. |

**Total planned:** about 1,380 words, leaving room within 1,000–1,500.

**Style rules:**
- Define P@k, AP and AUROC once, in plain words.
- Use no p-values and no "significant".
- Do not use "beats" or "wins" for any interval that includes zero.
- Name no single winner.
- Include no personal information and no private log paths.
- Put reproduction status in a single sentence: "imported results; harness reproduction pending".
  Update it after a protocol-approved run.
