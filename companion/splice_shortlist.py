#!/usr/bin/env python3
"""Choose a scoring configuration for a fixed budget of splicing experiments.

Worked example on the MFASS minigene assay (Chong et al., Mol Cell 2018), using
the canonical held-out split and the saved SpliceAI/Pangolin predictions from the
rewire-benchmarks matched-annotation study (commit 093fd1a).

Subcommands
  fetch          download pinned public inputs and verify SHA-256
  build          build the eligible cohort and join the canonical split
  annotation     (optional) extract GENCODE 44 Ensembl_canonical transcripts
  check-variant  assembly, strand and transcript checks for one variant
  controls       fit the CPU controls on training groups, score held-out rows
  evaluate       compare configurations at a budget; write shortlist and tables

Specialist scores are a SAVED-SCORE REPLAY: this script reads the published
per-variant predictions; it does not run SpliceAI or Pangolin. The endpoint is
exon recognition in a minigene reporter, not splicing in patient RNA.
"""
import argparse
import csv
import gzip
import hashlib
import itertools
import json
import pathlib
import platform
import resource
import sys
import time
import urllib.request

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit

HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
RUNS = HERE / "runs"

MFASS_REV = "9a8e4f27106be52aeb11acad27f95f5cded663a8"
BENCH_REV = "093fd1ae198c80ce34408d84d6543bca4fc538f2"
MFASS_RAW = f"https://raw.githubusercontent.com/KosuriLab/MFASS/{MFASS_REV}/processed_data/snv/"
BENCH_RAW = f"https://raw.githubusercontent.com/rewire-bio/rewire-benchmarks/{BENCH_REV}/benchmarks/mfass/"
MATCHED = "results/matched-annotation-v1/"

# (local name, url, sha256). Hashes are those published with the benchmark.
PINNED = [
    ("snv_data_clean.txt", MFASS_RAW + "snv_data_clean.txt",
     "a637ca0e307e66ff48811ec7efa22b9ce453bc7883b04f0cacb867f7283132d8"),
    ("snv_func_annot.txt", MFASS_RAW + "snv_func_annot.txt",
     "71a857fe647c4e68acbb41ca61e959c47e1176de89b1442bd6ca1772aa60d5a1"),
    ("split-v2.tsv", BENCH_RAW + "splits/split-v2.tsv",
     "999ebcb7e63a5c5eaa8780fa468e59ac1f934260ad50102814174c396317f052"),
    ("baseline-kmer-position-v2.predictions.tsv",
     BENCH_RAW + "results/baseline-kmer-position-v2.predictions.tsv",
     "2f3117c225a8da9ea737abfa2d0f7e1dec97696ae4bacd263864bec9d7f923eb"),
    ("S0.predictions.tsv", BENCH_RAW + MATCHED + "S0/spliceai-1.3.1-gencode44-canonical-mask0.predictions.tsv",
     "fa30a4dc6a05e6e762fbac9411e486869aec5b248cab80146aeab7a42c27320d"),
    ("S1.predictions.tsv", BENCH_RAW + MATCHED + "S1/spliceai-1.3.1-gencode44-canonical-mask1.predictions.tsv",
     "84f9d10c367ada32df5f27b49985c35fae68727f1d8e576352c98cfb27be9516"),
    ("P0.predictions.tsv", BENCH_RAW + MATCHED + "P0/pangolin-gencode44-canonical-maskFalse.predictions.tsv",
     "fbd8861a37c2d041038cfdfb0dd4e9d1f572d72b0eb7e41406739ef740eaf4a1"),
    ("P1.predictions.tsv", BENCH_RAW + MATCHED + "P1/pangolin-gencode44-canonical-maskTrue.predictions.tsv",
     "9fba694b636899feed60d955506849f68701fc6ecb9cec5c1fc6ba7f92728e1e"),
    ("S0.unscored.tsv", BENCH_RAW + MATCHED + "S0/spliceai-1.3.1-gencode44-canonical-mask0.unscored.tsv",
     "cd22dae59572ae7bfeee7d5843f487e093ba5706235cb149ee5fd3704c83efc7"),
    ("P0.unscored.tsv", BENCH_RAW + MATCHED + "P0/pangolin-gencode44-canonical-maskFalse.unscored.tsv",
     "f8f274522c28f428e97bf84458294e235979466b7c9433746a6ad1adef37fe5a"),
    ("S0.json", BENCH_RAW + MATCHED + "S0/spliceai-1.3.1-gencode44-canonical-mask0.json",
     "477554b7c10ea16600b487affcf562c1fdce987e787b06f34fb406ab2aed4810"),
    ("S1.json", BENCH_RAW + MATCHED + "S1/spliceai-1.3.1-gencode44-canonical-mask1.json",
     "e8f396107329ffe66ce2ae8bd7aeb74a1daedb3e86b6a1e1cd2cc3fd8af8b8d7"),
    ("P0.json", BENCH_RAW + MATCHED + "P0/pangolin-gencode44-canonical-maskFalse.json",
     "2b677f373d3a53f45d8bdf58630546edb508525886825b736f8bd4a5029d0660"),
    ("P1.json", BENCH_RAW + MATCHED + "P1/pangolin-gencode44-canonical-maskTrue.json",
     "4877e83894e59122c1cd8ebdc39e4d1f591e1adf2fd59290f6440863a57de742"),
]

GENCODE_URL = ("https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_44/"
               "gencode.v44.primary_assembly.annotation.gtf.gz")
GENCODE_MD5 = "b182a9f3b134b9cc2da566a2b1692557"  # official MD5SUMS, as in the study preflight
UCSC_SEQ = "https://api.genome.ucsc.edu/getData/sequence?genome=hg38;chrom={chrom};start={start};end={end}"

SPECIALISTS = {
    "S0": "SpliceAI 1.3.1, GENCODE 44 canonical, mask 0, distance 50",
    "S1": "SpliceAI 1.3.1, GENCODE 44 canonical, mask 1, distance 50",
    "P0": "Pangolin 5cf94b8 + per-gene mask patch, GENCODE 44 canonical, mask False, distance 50",
    "P1": "Pangolin 5cf94b8 + per-gene mask patch, GENCODE 44 canonical, mask True, distance 50",
}
CONTROLS = {
    "prevalence": "training prevalence, same score for every variant (no information)",
    "distance": "negative distance to the nearest exon/intron junction in the construct (no fitting)",
    "kmer_assay": "k-mer + position + allele, assay window only, gradient-boosted trees",
    "kmer_cons": "as kmer_assay plus phyloP and phastCons (the published MFASS-v2 baseline)",
}
# Sizes checked 2026-09-29 (PyPI JSON API, GitHub trees API, local file stat).
DOWNLOADS = {
    "GRCh38 primary assembly FASTA (GENCODE 44, gzip)": 844_691_642,
    "GENCODE 44 primary-assembly GTF (gzip)": 49_730_393,
    "spliceai 1.3.1 wheel (includes 5 models)": 16_676_295,
    "tensorflow 2.21.0 wheel (cp311 macOS arm64)": 223_405_849,
    "Pangolin repository models directory at 5cf94b8": 184_399_504,
    "torch 2.2.2 wheel (cp311 macOS arm64)": 59_714_938,
}
SELECTED = ["kmer_assay_selected", "kmer_cons_selected"]
SCORES_FROM = {
    "prevalence": "computed here (one training number)",
    "distance": "computed here (no fitting)",
    "kmer_assay_selected": "fitted here (validation-selected settings)",
    "kmer_cons_selected": "fitted here (validation-selected settings)",
    **{c: "saved-score replay (matched study)" for c in SPECIALISTS},
}
SEED = 20260914
N_TRAIN, N_TEST, POS_TRAIN, POS_TEST = 19409, 8324, 735, 315
COMPLEMENT = str.maketrans("ACGT", "TGCA")


# ----------------------------------------------------------------------------- io

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_tsv(path):
    with open(path, newline="") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def write_tsv(path, rows, fields, delimiter="\t"):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, delimiter=delimiter, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def download(url, dest):
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "splice-shortlist/0.1"})
    with urllib.request.urlopen(req, timeout=120) as r, open(tmp, "wb") as fh:
        while block := r.read(1 << 20):
            fh.write(block)
    tmp.rename(dest)


def cmd_fetch(args):
    DATA.mkdir(exist_ok=True)
    receipt = []
    for name, url, want in PINNED:
        dest = DATA / name
        if not dest.exists():
            print(f"downloading {name}")
            download(url, dest)
        got = sha256(dest)
        status = "ok" if got == want else "MISMATCH"
        receipt.append({"file": name, "url": url, "sha256": got, "status": status})
        print(f"{status:8s} {name}")
        if got != want:
            raise SystemExit(f"{name}: SHA-256 {got} != pinned {want}; refusing to continue")
    (DATA / "fetch-receipt.json").write_text(json.dumps(receipt, indent=2))


# -------------------------------------------------------------------------- cohort

def assay_pair(row):
    """Return assay-oriented reference/mutant sequences after checking the alleles.

    natural_seq/original_seq are in assay orientation with the variant at
    rel_position - 1. The legacy `sequence` column is reverse-complemented in
    7,770 eligible rows, so it must not be used to centre a window.
    """
    ref_seq, mut_seq = row["natural_seq"].upper(), row["original_seq"].upper()
    pos = int(row["rel_position"]) - 1
    diffs = [i for i, (a, b) in enumerate(zip(ref_seq, mut_seq)) if a != b]
    if len(ref_seq) != 170 or len(mut_seq) != 170 or diffs != [pos]:
        raise ValueError(f"{row['id']}: assay pair does not differ only at rel_position")
    ref, alt = row["ref_allele"].upper(), row["alt_allele"].upper()
    if row["strand"] == "-":
        ref, alt = ref.translate(COMPLEMENT), alt.translate(COMPLEMENT)
    if ref_seq[pos] != ref or mut_seq[pos] != alt:
        raise ValueError(f"{row['id']}: assay pair alleles disagree with the genomic alleles")
    legacy = row["sequence"].upper()
    orientation = ("assay" if legacy == mut_seq else
                   "reverse_complement" if legacy == mut_seq.translate(COMPLEMENT)[::-1] else None)
    if orientation is None:
        raise ValueError(f"{row['id']}: legacy sequence matches neither orientation")
    return ref_seq, mut_seq, orientation


def cmd_build(args):
    raw = read_tsv(DATA / "snv_data_clean.txt")
    annot = {r["id"]: r for r in read_tsv(DATA / "snv_func_annot.txt")}
    split = {r["id"]: r for r in read_tsv(DATA / "split-v2.tsv")}
    eligible = [r for r in raw if r["category"] == "mutant" and r["strong_lof"] != "NA"]
    n_sdv = sum(r["strong_lof"] == "TRUE" for r in eligible)
    exons = len({r["ensembl_id"] for r in raw if r["category"] == "mutant"})
    print(f"source rows {len(raw)}; eligible {len(eligible)} (paper 27,733); "
          f"disrupting {n_sdv} (paper 1,050); exons in mutant set {exons} (paper 2,198)")
    if (len(eligible), n_sdv, exons) != (27733, 1050, 2198):
        raise SystemExit("cohort does not reconcile with the published totals")
    if set(split) != {r["id"] for r in eligible}:
        raise SystemExit("split IDs differ from the eligible cohort")
    out, orient = [], {"assay": 0, "reverse_complement": 0}
    for r in eligible:
        ref_seq, mut_seq, o = assay_pair(r)
        orient[o] += 1
        a = annot.get(r["id"], {})
        out.append({
            "id": r["id"], "group": split[r["id"]]["group"], "split": split[r["id"]]["split"],
            "sdv": int(r["strong_lof"] == "TRUE"), "ensembl_id": r["ensembl_id"],
            "gene_id": a.get("ensembl_gene_id", "NA"), "symbol": a.get("symbol", "NA"),
            "chr": r["chr"], "strand": r["strand"],
            "pos_hg38": r["snp_position_hg38_1based"], "pos_hg19": r["snp_position"],
            "ref_allele": r["ref_allele"], "alt_allele": r["alt_allele"],
            "rel_position": r["rel_position"], "rel_position_scaled": r["rel_position_scaled"],
            "intron1_len": r["intron1_len"], "exon_len": r["exon_len"],
            "intron2_len": r["intron2_len"], "region": r["label"],
            "phylop_score": a.get("phylop_score", "NA"),
            "mean_phastCons_score": a.get("mean_phastCons_score", "NA"),
            "reference_sequence": ref_seq, "mutant_sequence": mut_seq,
            "legacy_orientation": o,
        })
    train = [r for r in out if r["split"] == "train"]
    test = [r for r in out if r["split"] == "test"]
    counts = (len(train), len(test), sum(r["sdv"] for r in train), sum(r["sdv"] for r in test))
    if counts != (N_TRAIN, N_TEST, POS_TRAIN, POS_TEST):
        raise SystemExit(f"split counts changed: {counts}")
    write_tsv(DATA / "cohort.tsv", out, list(out[0]))
    print(f"assay-pair checks passed for all {len(out)} variants; legacy sequence "
          f"reverse-complemented in {orient['reverse_complement']}")
    print(f"train {len(train)} variants ({counts[2]} disrupting) in "
          f"{len({r['group'] for r in train})} groups; test {len(test)} ({counts[3]} disrupting) "
          f"in {len({r['group'] for r in test})} groups")


def load_cohort():
    rows = read_tsv(DATA / "cohort.tsv")
    for r in rows:
        r["sdv"] = int(r["sdv"])
    return rows


# ------------------------------------------------------------------ variant check

def fetch_json(url, cache):
    if cache.exists():
        return json.loads(cache.read_text())
    req = urllib.request.Request(url, headers={"User-Agent": "splice-shortlist/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        payload = json.loads(r.read())
    payload["_retrieved_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    payload["_url"] = url
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(payload))
    return payload


def hg38_bases(chrom, start0, end0):
    cache = DATA / "ucsc" / f"{chrom}_{start0}_{end0}.json"
    return fetch_json(UCSC_SEQ.format(chrom=chrom, start=start0, end=end0), cache)["dna"].upper()


def cmd_annotation(args):
    gtf = DATA / "gencode.v44.primary_assembly.annotation.gtf.gz"
    if not gtf.exists():
        print("downloading GENCODE 44 primary-assembly GTF (about 50 MB)")
        download(GENCODE_URL, gtf)
    md5 = hashlib.md5(gtf.read_bytes(), usedforsecurity=False).hexdigest()
    if md5 != GENCODE_MD5:
        raise SystemExit(f"GENCODE GTF MD5 {md5} != {GENCODE_MD5}")
    tx, exons = {}, []
    with gzip.open(gtf, "rt") as fh:
        for line in fh:
            if line.startswith("#"):
                continue
            f = line.rstrip("\n").split("\t")
            if f[2] not in ("transcript", "exon") or 'tag "Ensembl_canonical"' not in f[8]:
                continue
            attrs = dict(kv.strip().split(" ", 1) for kv in f[8].strip(";").split("; ") if " " in kv.strip())
            tid, gname = attrs["transcript_id"].strip('"'), attrs.get("gene_name", '"NA"').strip('"')
            gid = attrs["gene_id"].strip('"')
            if f[2] == "transcript":
                tx[tid] = {"transcript_id": tid, "gene_id": gid, "gene_name": gname, "chrom": f[0],
                           "start": f[3], "end": f[4], "strand": f[6]}
            else:
                exons.append({"transcript_id": tid, "chrom": f[0], "start": f[3], "end": f[4]})
    write_tsv(DATA / "gencode44-canonical-transcripts.tsv", list(tx.values()),
              ["transcript_id", "gene_id", "gene_name", "chrom", "start", "end", "strand"])
    write_tsv(DATA / "gencode44-canonical-exons.tsv", exons,
              ["transcript_id", "chrom", "start", "end"])
    print(f"GTF MD5 ok; {len(tx)} Ensembl_canonical transcripts, {len(exons)} exons")


def canonical_context(chrom, pos):
    path = DATA / "gencode44-canonical-transcripts.tsv"
    if not path.exists():
        return None
    hits = [t for t in read_tsv(path) if t["chrom"] == chrom and int(t["start"]) <= pos <= int(t["end"])]
    ex = [e for e in read_tsv(DATA / "gencode44-canonical-exons.tsv")
          if e["chrom"] == chrom and e["transcript_id"] in {t["transcript_id"] for t in hits}]
    for t in hits:
        mine = [e for e in ex if e["transcript_id"] == t["transcript_id"]]
        t["nearest_exon_boundary_bp"] = min(
            (min(abs(pos - int(e["start"])), abs(pos - int(e["end"]))) for e in mine), default=None)
        t["in_exon"] = any(int(e["start"]) <= pos <= int(e["end"]) for e in mine)
    return hits


def cmd_check_variant(args):
    rows = {r["id"]: r for r in load_cohort()}
    r = rows.get(args.id)
    if r is None:
        raise SystemExit(f"{args.id} is not in the eligible cohort")
    pos = int(r["pos_hg38"])
    print(f"{r['id']}  gene {r['symbol']} ({r['gene_id']})  split {r['split']}  group {r['group']}")
    print(f"  hg38 {r['chr']}:{pos}  gene strand {r['strand']}  construct region {r['region']}  "
          f"assay position {r['rel_position']}/170")
    print(f"  1 assay pair: reference and mutant differ only at position {r['rel_position']}, "
          f"alleles consistent with strand: PASS (checked in build)")
    print(f"    legacy `sequence` column orientation: {r['legacy_orientation']}")
    # Assay reference window mapped onto GRCh38, in genomic orientation.
    rel = int(r["rel_position"]) - 1

    def window_mismatches(strand):
        window = r["reference_sequence"]
        if strand == "+":
            start0 = pos - 1 - rel
        else:
            start0 = pos - 1 - (169 - rel)
            window = window.translate(COMPLEMENT)[::-1]
        genome = hg38_bases(r["chr"], start0, start0 + 170)
        return sum(a != b for a, b in zip(window, genome)), start0, genome[pos - 1 - start0]

    mism, start0, base = window_mismatches(r["strand"])
    ref = r["ref_allele"].upper()
    # MFASS has no declared licence, so cohort alleles are compared but not printed.
    print(f"  2 GRCh38 base at {r['chr']}:{pos} is {base}; matches the recorded genomic ref "
          f"allele: {'PASS' if base == ref else 'FAIL'}")
    if base != ref and base == ref.translate(COMPLEMENT):
        print("    recorded alleles are the complement of the GRCh38 base")
    print(f"  3 170 bp assay reference window vs GRCh38 {r['chr']}:{start0 + 1}-{start0 + 170} "
          f"on recorded strand {r['strand']}: {mism} mismatching bases")
    if mism:
        flipped = "-" if r["strand"] == "+" else "+"
        m2, s2, _ = window_mismatches(flipped)
        print(f"    same window on the opposite strand ({flipped}), {r['chr']}:{s2 + 1}-{s2 + 170}: "
              f"{m2} mismatching bases")
        if m2 == 0:
            print("    -> the assay is intact; the hg19->hg38 mapping inverted this region but the "
                  "strand and alleles were not converted. Excluded, not repaired, in the study.")
    hits = canonical_context(r["chr"], pos)
    if hits is None:
        print("  4 transcript: run `annotation` first for the GENCODE 44 canonical check")
    elif not hits:
        print("  4 transcript: no GENCODE 44 Ensembl_canonical transcript spans this position -> "
              "unscored under the canonical-transcript protocol")
    else:
        for t in hits:
            print(f"  4 transcript: {t['transcript_id']} {t['gene_name']} {t['chrom']}:{t['start']}-{t['end']} "
                  f"({t['strand']}); in exon: {t['in_exon']}; distance to nearest canonical exon end "
                  f"{t['nearest_exon_boundary_bp']} bp")
    print("  5 saved scores (replay):")
    for cond in SPECIALISTS:
        p = {x["id"]: x for x in read_tsv(DATA / f"{cond}.predictions.tsv")}[args.id]
        print(f"    {cond}: {p['score'] or 'unscored'}")
    print(f"  MFASS outcome (large-effect disruption, retrospective): {r['sdv']}")


# ------------------------------------------------------------------------ controls

BASES, REGIONS = "ACGT", ["exon", "upstr_intron", "downstr_intron"]
KMERS = {"".join(p): i for i, p in enumerate(itertools.product(BASES, repeat=3))}


def featurise(rows, conservation=True, window=21):
    """Features of the published MFASS-v2 baseline (rewire-benchmarks run_baseline.py, MIT).

    Positions come from the construct; the 21 bp window is taken from the
    validated assay-oriented mutant sequence.
    """
    n_num = 8 + (2 if conservation else 0)
    X = np.zeros((len(rows), n_num + len(REGIONS) + 8 + len(KMERS)), dtype=np.float32)
    for i, r in enumerate(rows):
        pos, i1, ex = float(r["rel_position"]), float(r["intron1_len"]), float(r["exon_len"])
        acceptor, donor = i1, i1 + ex
        vals = [pos, float(r["rel_position_scaled"]), pos - acceptor, pos - donor,
                min(abs(pos - acceptor), abs(pos - donor)), ex, i1, float(r["intron2_len"])]
        if conservation:
            for col in ("phylop_score", "mean_phastCons_score"):
                v = r[col]
                vals.append(float(v) if v not in ("NA", "") else np.nan)
        vals += [1.0 if r["region"] == g else 0.0 for g in REGIONS]
        vals += [1.0 if r["ref_allele"] == b else 0.0 for b in BASES]
        vals += [1.0 if r["alt_allele"] == b else 0.0 for b in BASES]
        X[i, :len(vals)] = vals
        seq, p = r["mutant_sequence"], int(pos) - 1
        sub = seq[max(0, p - window // 2): p + window // 2 + 1]
        counts = np.zeros(len(KMERS), dtype=np.float32)
        for j in range(len(sub) - 2):
            if (k := KMERS.get(sub[j:j + 3])) is not None:
                counts[k] += 1
        X[i, len(vals):] = counts / max(counts.sum(), 1)
    return X


def junction_distance(r):
    """Bases to the nearest exon/intron junction; 0 = the base touching a junction."""
    pos, i1, ex = int(r["rel_position"]), int(r["intron1_len"]), int(r["exon_len"])
    return min(abs(pos - (i1 + 0.5)), abs(pos - (i1 + ex + 0.5))) - 0.5


BANDS = [("0-2", 0, 2), ("3-10", 3, 10), ("11-30", 11, 30), (">30", 31, 10_000)]

GRID = [{"learning_rate": lr, "max_leaf_nodes": leaves}
        for lr in (0.03, 0.06, 0.1) for leaves in (15, 31)]
PUBLISHED = {"learning_rate": 0.06, "max_leaf_nodes": 31}


def gbt(params):
    return HistGradientBoostingClassifier(max_iter=300, l2_regularization=1.0,
                                          random_state=SEED, **params)


def select_on_validation(train, conservation):
    """Pick hyperparameters on held-aside TRAINING groups only; the test arm is never read."""
    groups = np.array([r["group"] for r in train])
    y = np.array([r["sdv"] for r in train])
    X = featurise(train, conservation)
    inner, val = next(GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=SEED)
                      .split(X, y, groups))
    table = []
    for params in GRID:
        s = gbt(params).fit(X[inner], y[inner]).predict_proba(X[val])[:, 1]
        table.append({**params, "validation_ap": float(average_precision_score(y[val], s))})
    best = max(table, key=lambda t: t["validation_ap"])
    return {k: best[k] for k in PUBLISHED}, table, {
        "inner_variants": int(len(inner)), "validation_variants": int(len(val)),
        "validation_groups": int(len(set(groups[val]))), "validation_positives": int(y[val].sum())}


def peak_rss_mb():
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rss / (1 << 20) if sys.platform == "darwin" else rss / 1024


def cmd_controls(args):
    t_start = time.perf_counter()
    rows = load_cohort()
    train = [r for r in rows if r["split"] == "train"]
    test = [r for r in rows if r["split"] == "test"]
    ytr = np.array([r["sdv"] for r in train])
    out = RUNS / "controls"
    out.mkdir(parents=True, exist_ok=True)
    scores, receipt = {}, {"seed": SEED, "train_variants": len(train), "test_variants": len(test),
                           "train_groups": len({r["group"] for r in train}), "methods": {}}
    prevalence = float(ytr.mean())
    scores["prevalence"] = np.full(len(test), prevalence)
    receipt["methods"]["prevalence"] = {"fitted_on": "training labels (one number)", "value": prevalence}
    scores["distance"] = -np.array([junction_distance(r) for r in test])
    receipt["methods"]["distance"] = {"fitted_on": "nothing; fixed rule"}
    for name, cons in (("kmer_assay", False), ("kmer_cons", True)):
        t0 = time.perf_counter()
        chosen, table, sizes = select_on_validation(train, cons)
        t_sel = time.perf_counter() - t0
        t0 = time.perf_counter()
        model = gbt(PUBLISHED).fit(featurise(train, cons), ytr)
        s = model.predict_proba(featurise(test, cons))[:, 1]
        t_fit = time.perf_counter() - t0
        scores[name] = s
        receipt["methods"][name] = {
            "fitted_on": "training groups only", "params_used": PUBLISHED,
            "validation_selected": chosen, "selection_agrees_with_used": chosen == PUBLISHED,
            "validation_grid": table, "validation_split": sizes,
            "seconds_selection": round(t_sel, 2), "seconds_fit_and_score": round(t_fit, 2)}
        # Always export the validation-selected model under a stable name, even when
        # selection agrees with the historical settings (the files are then identical).
        alt = (s if chosen == PUBLISHED else
               gbt(chosen).fit(featurise(train, cons), ytr).predict_proba(featurise(test, cons))[:, 1])
        scores[name + "_selected"] = alt
    for name, s in scores.items():
        write_tsv(out / f"{name}.predictions.tsv",
                  [{"id": r["id"], "group": r["group"], "label": r["sdv"], "score": f"{v:.10f}"}
                   for r, v in zip(test, s)], ["id", "group", "label", "score"])
    receipt["seconds_end_to_end"] = round(time.perf_counter() - t_start, 2)
    receipt["peak_rss_mb"] = round(peak_rss_mb(), 1)
    receipt["environment"] = {"python": platform.python_version(), "machine": platform.machine(),
                              "platform": platform.platform(), "numpy": np.__version__,
                              "sklearn": __import__("sklearn").__version__}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2))
    for name, m in receipt["methods"].items():
        if "validation_selected" in m:
            print(f"{name}: validation-selected {m['validation_selected']} "
                  f"(published {PUBLISHED}; agree={m['selection_agrees_with_used']})")
    print(f"controls scored {len(test)} held-out variants in {receipt['seconds_end_to_end']} s, "
          f"peak RSS {receipt['peak_rss_mb']} MB")


# ------------------------------------------------------------------------ metrics

def check_budget(k, n):
    if not 1 <= k <= n:
        raise ValueError(f"budget must be between 1 and the {n} scored variants; got {k}")


def budget_precision(labels, scores, k):
    """Precision in the top k, with ties at the cutoff handled explicitly.

    Returns the expectation under a uniformly random order of the tied block,
    the worst and best achievable values, and the tie size at the cutoff.
    """
    labels, scores = np.asarray(labels), np.asarray(scores, dtype=float)
    check_budget(k, len(scores))
    cut = np.sort(scores)[::-1][k - 1]
    above, tied = scores > cut, scores == cut
    pa, na = int(labels[above].sum()), int(above.sum())
    pt, nt = int(labels[tied].sum()), int(tied.sum())
    slots = k - na
    return {"k": k, "expected": (pa + slots * pt / nt) / k,
            "min": (pa + max(0, slots - (nt - pt))) / k, "max": (pa + min(slots, pt)) / k,
            "tied_at_cutoff": nt, "slots_in_tied_block": slots,
            "positives_in_tied_block": pt}


def registered_precision(labels, scores, k):
    """The study's fixed label-independent tie order (rewirebench.metrics.precision_at_n)."""
    check_budget(k, len(scores))
    jitter = np.random.default_rng(0).permutation(len(scores))
    order = np.lexsort((jitter, -np.asarray(scores, dtype=float)))
    return float(np.asarray(labels)[order[:k]].sum() / k), order[:k]


def paired_bootstrap(labels, base, cand, groups, k, draws, seed):
    """Candidate minus baseline, resampling whole exon/gene groups (percentile 95%).

    Resampled lists differ in length, so each draw keeps the review FRACTION k/N
    rather than exactly k slots; the realised depths are returned.
    """
    rng = np.random.default_rng(seed)
    uniq = np.unique(groups)
    idx = {g: np.flatnonzero(groups == g) for g in uniq}
    fns = {"precision_at_budget": lambda y, s, c: registered_precision(y, s, c)[0],
           "average_precision": lambda y, s, c: average_precision_score(y, s),
           "auroc": lambda y, s, c: roc_auc_score(y, s)}
    obs = {m: f(labels, cand, k) - f(labels, base, k) for m, f in fns.items()}
    deltas = {m: [] for m in fns}
    skipped, caps = 0, []
    for _ in range(draws):
        rows = np.concatenate([idx[g] for g in rng.choice(uniq, size=len(uniq))])
        y = labels[rows]
        if y.min() == y.max():
            skipped += 1
            continue
        cap = max(1, int(round(k * len(rows) / len(labels))))
        caps.append(cap)
        for m, f in fns.items():
            deltas[m].append(f(y, cand[rows], cap) - f(y, base[rows], cap))
    return {m: {"observed": obs[m], "ci95": [float(np.percentile(deltas[m], 2.5)),
                                             float(np.percentile(deltas[m], 97.5))],
                "share_of_draws_exactly_zero": float(np.mean(np.asarray(deltas[m]) == 0))}
            for m in fns} | {"draws": draws, "single_class_skipped": skipped,
                            "groups": int(len(uniq)),
                            "realised_depth": {"nominal": k, "min": int(min(caps)),
                                               "max": int(max(caps)), "mean": float(np.mean(caps))}}


def load_scores(name):
    path = (RUNS / "controls" / f"{name}.predictions.tsv" if name in CONTROLS or name in SELECTED
            else DATA / f"{name}.predictions.tsv")
    return {r["id"]: float(r["score"]) for r in read_tsv(path) if r["score"] != ""}


def exclusions(test_ids):
    s0 = {r["id"]: r["reason"] for r in read_tsv(DATA / "S0.unscored.tsv")}
    p0 = {r["id"]: r["reason"] for r in read_tsv(DATA / "P0.unscored.tsv")}
    out = []
    for i in sorted(set(s0) | set(p0)):
        text = s0.get(i, "") + " " + p0.get(i, "")
        reason = ("reference allele differs from GRCh38 (hg19->hg38 orientation)"
                  if "ref issue" in text or "Mismatch" in text else
                  "outside the GENCODE 44 canonical transcript span"
                  if "no annotated gene" in text or "gene body" in text else "other")
        out.append({"id": i, "group": test_ids[i]["group"], "reason": reason,
                    "spliceai_message": s0.get(i, "").split(":")[0],
                    "pangolin_message": p0.get(i, "").split("skipping variant: ")[-1].split(" (")[0]})
    return out


def cmd_evaluate(args):
    rows = [r for r in load_cohort() if r["split"] == "test"]
    by_id = {r["id"]: r for r in rows}
    if args.tutorial:
        # Small real-data subset for a first run: every 8th held-out group.
        keep = sorted({r["group"] for r in rows})[::8]
        rows = [r for r in rows if r["group"] in set(keep)]
        by_id = {r["id"]: r for r in rows}
    methods = list(CONTROLS) + list(SPECIALISTS)
    extra = SELECTED
    missing = [m for m in list(CONTROLS) + extra if not (RUNS / "controls" / f"{m}.predictions.tsv").exists()]
    if missing:
        raise SystemExit(f"missing control predictions {missing}; run `controls` first")
    scores = {m: load_scores(m) for m in methods + extra}
    scored = {m: {i for i in s if i in by_id} for m, s in scores.items()}
    common = sorted(set(by_id).intersection(*scored.values()))
    y = np.array([by_id[i]["sdv"] for i in common])
    g = np.array([by_id[i]["group"] for i in common])
    k = args.budget
    if not 1 <= k <= len(common):
        raise SystemExit(f"--budget must be between 1 and {len(common)} (the commonly scored "
                         f"variants); got {k}")
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    table = {}
    for m in methods + extra:
        s = np.array([scores[m][i] for i in common])
        bp = budget_precision(y, s, k)
        reg, _ = registered_precision(y, s, k)
        table[m] = {
            "description": {**CONTROLS, **SPECIALISTS}.get(m, "validation-selected hyperparameters"),
            "scores_from": SCORES_FROM.get(m, "fitted here (training groups)"),
            "scored_of_original": [len(scored[m]), len(by_id)],
            "precision_at_budget_expected": bp["expected"],
            "precision_at_budget_range": [bp["min"], bp["max"]],
            "precision_at_budget_registered_tie_order": reg,
            "recall_at_budget_expected": bp["expected"] * k / y.sum(),
            "tied_at_cutoff": bp["tied_at_cutoff"], "slots_in_tied_block": bp["slots_in_tied_block"],
            "average_precision": float(average_precision_score(y, s)),
            "auroc": float(roc_auc_score(y, s)),
            "budget_curve": {b: budget_precision(y, s, b)["expected"]
                             for b in (10, 25, 50, 100, 150, 200, 300, 400, 600, 800)
                             if b <= len(common)},
        }

    base = np.array([scores[args.baseline][i] for i in common])
    contrasts = {}
    for m in SPECIALISTS:
        cand = np.array([scores[m][i] for i in common])
        contrasts[f"{m} - {args.baseline}"] = paired_bootstrap(y, base, cand, g, k, args.draws, SEED)

    tops = {m: set(np.array(common)[registered_precision(y, np.array([scores[m][i] for i in common]), k)[1]])
            for m in methods}
    overlap = [{"a": a, "b": b, "shared_in_top_k": len(tops[a] & tops[b])}
               for a, b in itertools.combinations([m for m in methods if m != "prevalence"], 2)]

    # Where each configuration finds (or misses) disrupting variants, by distance
    # to the nearest exon/intron junction in the construct.
    dist = np.array([junction_distance(by_id[i]) for i in common])
    bands = {}
    for label, lo, hi in BANDS:
        mask = (dist >= lo) & (dist <= hi)
        band = {"variants": int(mask.sum()), "disrupting": int(y[mask].sum()), "methods": {}}
        for m in methods[1:]:
            s = np.array([scores[m][i] for i in common])[mask]
            captured = sum(1 for i in np.array(common)[mask] if i in tops[m] and by_id[i]["sdv"])
            band["methods"][m] = {
                "disrupting_in_top_k": captured,
                "auroc_within_band": (float(roc_auc_score(y[mask], s))
                                      if 0 < y[mask].sum() < mask.sum() else None)}
        bands[label] = band

    excluded = exclusions({r["id"]: r for r in read_tsv(DATA / "cohort.tsv") if r["split"] == "test"})
    excluded = [e for e in excluded if e["id"] in by_id]
    write_tsv(out / "excluded.csv", excluded, list(excluded[0]) if excluded else ["id"], delimiter=",")

    # Shortlist for the configuration the reader chose, with ties flagged.
    s = scores[args.method]
    ranked = sorted((i for i in common), key=lambda i: -s[i])
    cutoff = s[ranked[k - 1]]
    short = [{"rank": n + 1, "id": i, "gene": by_id[i]["symbol"], "chr": by_id[i]["chr"],
              "pos_hg38": by_id[i]["pos_hg38"], "group": by_id[i]["group"], "score": f"{s[i]:.4f}",
              "tied_with_cutoff": s[i] == cutoff, "mfass_outcome_retrospective": by_id[i]["sdv"]}
             for n, i in enumerate(ranked) if s[i] >= cutoff]
    write_tsv(out / "shortlist.csv", short, list(short[0]), delimiter=",")

    controls_receipt = json.loads((RUNS / "controls" / "receipt.json").read_text())
    resources = {
        "controls_measured_here": {
            "seconds_end_to_end": controls_receipt["seconds_end_to_end"],
            "peak_rss_mb": controls_receipt["peak_rss_mb"],
            "scope": "load cohort, validation grid (2 x 6 fits), final fits of all controls, "
                     "score 8,324 held-out rows", "environment": controls_receipt["environment"]},
        "specialists_recorded_by_study": {
            c: {k: v for k, v in json.loads((DATA / f"{c}.json").read_text())["timing_seconds"].items()}
            for c in SPECIALISTS},
        "specialist_scope": "Apple M4 CPU, 5 (SpliceAI) or 6 (Pangolin) threads; score_test covers "
                            "8,324 held-out rows; peak memory was not recorded",
        "specialist_downloads_bytes": DOWNLOADS,
    }
    metrics = {
        "resources": resources,
        "endpoint": "MFASS minigene exon recognition (large-effect disruption); not patient RNA",
        "budget": k, "baseline_for_contrasts": args.baseline, "tutorial_subset": args.tutorial,
        "population": {"held_out": len(by_id), "common_scored": len(common),
                       "positives": int(y.sum()), "groups": int(len(set(g))),
                       "excluded": len(excluded)},
        "methods": table, "paired_contrasts": contrasts, "top_k_overlap": overlap,
        "junction_distance_bands": bands,
        "status": "exploratory; test outcomes were inspected in earlier work; intervals unadjusted",
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    write_decision_table(out / "decision-table.md", metrics)
    print((out / "decision-table.md").read_text())
    print(f"wrote {out}/shortlist.csv ({len(short)} rows for budget {k}; "
          f"{sum(x['tied_with_cutoff'] for x in short)} tied at the cutoff), excluded.csv, metrics.json")


def write_decision_table(path, m):
    k, pop = m["budget"], m["population"]
    lines = [f"Budget {k}; common scored population {pop['common_scored']} of {pop['held_out']} "
             f"held-out variants ({pop['positives']} disrupting, {pop['groups']} groups); "
             f"{pop['excluded']} excluded.", "",
             f"| Configuration | Scores | P@{k} expected [range over tie orders] | Tied at cutoff | AP | AUROC |",
             "|---|---|---|---:|---:|---:|"]
    for name, t in m["methods"].items():
        lo, hi = t["precision_at_budget_range"]
        rng = f"{t['precision_at_budget_expected']:.3f} [{lo:.2f}, {hi:.2f}]"
        lines.append(f"| {name} | {t['scores_from']} | {rng} | {t['tied_at_cutoff']} | "
                     f"{t['average_precision']:.3f} | {t['auroc']:.3f} |")
    lines += ["", f"Paired contrasts against `{m['baseline_for_contrasts']}` (whole-group bootstrap, "
              "95% percentile, unadjusted, exploratory):", "",
              f"| Contrast | P@{k} | AP | AUROC |", "|---|---|---|---|"]
    for name, c in m["paired_contrasts"].items():
        cells = [f"{c[x]['observed']:+.3f} [{c[x]['ci95'][0]:+.3f}, {c[x]['ci95'][1]:+.3f}]"
                 for x in ("precision_at_budget", "average_precision", "auroc")]
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    depth = next(iter(m["paired_contrasts"].values()))["realised_depth"]
    lines += ["", f"Each bootstrap draw resamples whole groups and keeps the review fraction {k}/"
              f"{pop['common_scored']}, so realised shortlist depths ranged {depth['min']}-{depth['max']} "
              f"(mean {depth['mean']:.1f}); the observed difference uses exactly {k}."]
    names = list(next(iter(m["junction_distance_bands"].values()))["methods"])
    lines += ["", f"Disrupting variants captured in each top {k} (registered tie order), by distance "
              "to the nearest junction in the construct; AUROC within band in brackets:", "",
              "| Band (bases) | Variants | Disrupting | " + " | ".join(names) + " |",
              "|---|---:|---:|" + "---:|" * len(names)]
    for label, b in m["junction_distance_bands"].items():
        cells = [f"{b['methods'][n]['disrupting_in_top_k']} "
                 + (f"({b['methods'][n]['auroc_within_band']:.2f})"
                    if b['methods'][n]['auroc_within_band'] is not None else "(n/a)") for n in names]
        lines.append(f"| {label} | {b['variants']} | {b['disrupting']} | " + " | ".join(cells) + " |")
    path.write_text("\n".join(lines) + "\n")


def positive_draws(text):
    value = int(text)
    if value < 100:
        raise argparse.ArgumentTypeError("--draws must be at least 100")
    return value


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch").set_defaults(fn=cmd_fetch)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    sub.add_parser("annotation").set_defaults(fn=cmd_annotation)
    cv = sub.add_parser("check-variant")
    cv.add_argument("id")
    cv.set_defaults(fn=cmd_check_variant)
    sub.add_parser("controls").set_defaults(fn=cmd_controls)
    ev = sub.add_parser("evaluate")
    ev.add_argument("--budget", type=int, default=100, help="number of variants you can assay")
    ev.add_argument("--method", required=True, choices=list(CONTROLS) + SELECTED + list(SPECIALISTS),
                    help="configuration whose shortlist to export")
    ev.add_argument("--baseline", default="kmer_cons", choices=list(CONTROLS) + SELECTED,
                    help="reference for paired contrasts; the default is the historical "
                         "MFASS-v2 baseline with its published settings")
    ev.add_argument("--draws", type=positive_draws, default=2000,
                    help="bootstrap resamples (at least 100)")
    ev.add_argument("--tutorial", action="store_true", help="every 8th held-out group only")
    ev.add_argument("--out", default="out")
    ev.set_defaults(fn=cmd_evaluate)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
