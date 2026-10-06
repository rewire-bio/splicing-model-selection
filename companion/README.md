# splice-shortlist

Choose a scoring configuration for a fixed number of minigene splicing experiments,
using the MFASS assay (Chong et al., Mol Cell 2018) as a worked example.

The script downloads pinned public inputs and checks each file's SHA-256. It then:
- builds the eligible MFASS cohort on the canonical held-out split;
- fits CPU controls on the training groups;
- compares them with the saved SpliceAI and Pangolin predictions from the
  [rewire-benchmarks matched-annotation study](https://github.com/rewire-bio/rewire-benchmarks/tree/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1);
- writes `shortlist.csv`, `excluded.csv`, `metrics.json` and `decision-table.md`.

**What this is not.**
- The specialist scores are a **saved-score replay**. Nothing in this directory runs
  SpliceAI or Pangolin (see "Full specialist inference" below).
- The endpoint is exon recognition in a minigene reporter, not splicing in patient RNA
  and not pathogenicity.
- The held-out outcomes had been inspected in earlier work, so every interval here is
  exploratory and unadjusted.

## Requirements

- [uv](https://docs.astral.sh/uv/) 0.8 or later. It installs Python 3.11 if needed.
- Downloads: about 82 MB for `fetch` (80 MB of MFASS tables plus 2 MB of split and
  predictions). The optional `annotation` step adds 50 MB (the GENCODE 44 GTF).
- Network access to raw.githubusercontent.com, ftp.ebi.ac.uk and api.genome.ucsc.edu.

## Run

```bash
cd splice-shortlist
uv sync --frozen                                        # numpy 1.26.4, scikit-learn 1.9.1 (uv.lock)
uv run --frozen python splice_shortlist.py fetch       # 14 files, SHA-256 checked
uv run --frozen python splice_shortlist.py build       # reconciles 27,733 / 1,050 / 2,198
uv run --frozen python splice_shortlist.py controls    # about 30 s on an Apple M4 CPU
uv run --frozen python splice_shortlist.py annotation  # optional: GENCODE 44 canonical transcripts
uv run --frozen python splice_shortlist.py check-variant ENSE00000712808_003
uv run --frozen python splice_shortlist.py evaluate --tutorial --budget 20 --draws 200 --method P0 --out out-tutorial
uv run --frozen python splice_shortlist.py evaluate --budget 100 --method P0 --out out
uv run --frozen pytest -q                               # all tests must pass; data tests need the steps above
```

- `--budget` is the number of constructs you can test. It must be between 1 and the number
  of commonly scored variants (8,297 on the full split).
- `--draws` is the number of bootstrap resamples. It must be at least 100; the default is
  2,000.
- `--method` chooses which configuration's shortlist to export. It does not change the
  comparison table.
- `--baseline` sets the reference for the paired contrasts. The default is `kmer_cons`, the
  historical MFASS-v2 baseline with its published settings.

| Name | Configuration | Inputs it needs |
|---|---|---|
| `prevalence` | training prevalence, the same score for every variant | nothing |
| `distance` | negative distance to the nearest junction in the construct (fixed rule, not fitted) | construct layout |
| `kmer_assay` | k-mers, position and alleles, gradient-boosted trees, published settings | construct sequence and layout, MFASS training labels |
| `kmer_cons` | `kmer_assay` plus phyloP and phastCons (the historical MFASS-v2 baseline) | as above plus conservation |
| `kmer_assay_selected`, `kmer_cons_selected` | as above, with hyperparameters chosen on held-aside training groups (see below) | as above |
| `S0` / `S1` | SpliceAI 1.3.1, GENCODE 44 canonical, mask 0 / 1, distance 50 | GRCh38 position, alleles, annotation |
| `P0` / `P1` | Pangolin 5cf94b8 with a per-gene mask patch, GENCODE 44 canonical, mask False / True, distance 50 | GRCh38 position, alleles, annotation |

**Historical and validation-selected baselines.** The `controls` step fits the published
MFASS-v2 settings (`learning_rate` 0.06, `max_leaf_nodes` 31). It also runs a small grid,
with learning rate in {0.03, 0.06, 0.1} and leaves in {15, 31}, on a 25% group-held-out
part of the training arm. The grid chooses (0.06, 15) for `kmer_assay` and (0.1, 15) for
`kmer_cons`. Both selected models are always exported as `*_selected`. Use them as the
contrast baseline with `--baseline kmer_cons_selected`. The published-settings rows remain
the default, for continuity with the historical results.

**Shortlists and ties.** `shortlist.csv` includes every variant tied with the score at the
cutoff, so it can have more rows than `--budget`. Its `rank` column is an arbitrary stable
order within equal scores. Treat a tied block as one group, not as ranked candidates.

**Bootstrap intervals.** The intervals resample whole exon/gene groups (2,000 draws, seed
20260914). A resampled list is shorter or longer than the original, so each draw keeps the
review *fraction* `budget / N` rather than exactly `budget` slots. `decision-table.md` and
`metrics.json` report the realised depth range: 83–126 for a nominal 100 on the full split.
The observed difference always uses exactly `budget`.

## Expected results

These were checked on 30 September 2026 with macOS arm64, Python 3.11 and `uv.lock`.

- `controls` reproduces the published `baseline-kmer-position-v2` predictions exactly: the
  file is byte-identical, with SHA-256 `2f3117c2…`.
- The replay reproduces the study's AP and AUROC for S0, S1, P0 and P1 to 1e-12. Under the
  registered tie order it also reproduces the study's P@100.
- The common scored population is 8,297 of 8,324 held-out variants: 314 disrupting, in 460
  groups. The 27 exclusions break down as:
  - 23 whose recorded alleles are the complement of GRCh38 after an inverted hg19-to-hg38
    mapping;
  - 4 outside the GENCODE 44 canonical transcript span.
- Results are deterministic for a given platform and library set.

## Full specialist inference (not re-executed here)

The saved predictions come from the study in rewire-benchmarks at commit
[`093fd1a`](https://github.com/rewire-bio/rewire-benchmarks/tree/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass).
Its frozen manifest records every command. To regenerate the predictions rather than
replay them, follow that commit's
[results README](https://github.com/rewire-bio/rewire-benchmarks/blob/093fd1ae198c80ce34408d84d6543bca4fc538f2/benchmarks/mfass/results/matched-annotation-v1/README.md#reproduction).
In outline:

1. Check out rewire-benchmarks at `093fd1ae198c80ce34408d84d6543bca4fc538f2`. Build the
   cohort with `mfass-build`, which uses the same two MFASS tables as `fetch`.
2. Download the GENCODE 44 GRCh38 primary-assembly FASTA (845 MB gzip) and the
   primary-assembly GTF (50 MB). Check both against the official `MD5SUMS`.
3. Clone Pangolin, apply `benchmarks/mfass/patches/pangolin-5cf94b8-mask-per-gene-1.patch`
   at `5cf94b8`, and install the patched tree without the editable flag. The patch is
   GPL-3.0; see `patches/README.md`.
4. Create two environments with the versions recorded in `manifest-v1.json`. The first has
   SpliceAI 1.3.1 and TensorFlow 2.21.0; the second has the patched Pangolin, torch 2.2.2 and
   gffutils 0.14.
5. Run `mfass.matched_annotation prepare` and `variants`, then `mfass.matched_study freeze`,
   then `benchmarks/mfass/scripts/run_matched_study.sh MANIFEST ENV_FILE`. Each condition
   uses distance 50 and one GENCODE 44 `Ensembl_canonical` transcript per gene. The mask is
   `0`/`1` for SpliceAI and `False`/`True` for Pangolin.

The study recorded about 14 h wall time on an Apple M4 CPU for all four conditions. The
per-condition scoring times were 6,921 s (S0), 6,102 s (S1), 19,153 s (P0) and 18,655 s
(P1). Peak memory was not recorded. **This route was not run for this article**: every
specialist number here comes from the published per-variant predictions.

Licences differ by tool and version. The current SpliceAI repository licenses its code
under PolyForm Strict 1.0.0 and its models under CC BY-NC 4.0; the PyPI 1.3.1 release
metadata lists GPLv3. Pangolin is GPL-3.0. Check the terms for your use before installing
either tool.

## Data terms

The MFASS repository declares no licence. This directory therefore downloads the tables
from the authors' repository and does not redistribute them. `shortlist.csv` and
`excluded.csv` contain no alleles or sequences. `check-variant` compares the recorded
alleles with GRCh38 but prints only the public GRCh38 base.

The feature code in `featurise` follows `run_baseline.py` in rewire-benchmarks (MIT).

## Maintained-code validation

From the repository root, `make test` runs offline unit and integrity regression tests.
Data-dependent tests skip on a fresh checkout; that is not a scientific reproduction.
Evaluation now rejects duplicate/nonfinite scores, label or group mismatches, incomplete
control predictions, unexplained exclusions and overlapping train/test groups before
writing metrics. The historical download archives retain their original bytes and code.
