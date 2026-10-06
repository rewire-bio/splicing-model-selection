#!/usr/bin/env python3
"""Write evidence/paper-migration/claims-ledger.json for the imported-evidence manuscript.

Each substantive manuscript claim is tied to a historical artifact path, a pointer inside it and
the artifact's SHA-256 (archive members use the digests recorded in
evidence/reference-output-members.json; repository files use the import manifest or are hashed
here). No value is computed. Standard library only.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIPNAME = "downloads/splice-shortlist-outputs.zip"
MEMBERS = json.loads((ROOT / "evidence/reference-output-members.json").read_text())["members"]
MANIFEST = {f["path"]: f["sha256"] for f in json.loads((ROOT / "evidence/import-manifest.json").read_text())["files"]}
PUBLISHED = "article/published-original.md"


def file_sha(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def member(name: str, pointer: str) -> dict:
    key = "splice-shortlist/" + name
    return {"artifact": f"{ZIPNAME}!{key}", "pointer": pointer, "sha256": MEMBERS[key],
            "container_sha256": MANIFEST[ZIPNAME]}


def article(pointer: str) -> dict:
    return {"artifact": PUBLISHED, "pointer": pointer, "sha256": file_sha(PUBLISHED),
            "note": "byte-identical copy of the published article (import manifest digest "
                    + MANIFEST["article/original.md"][:12] + "...; link-adjusted copy at article/original.md)"}


def repo(path: str, pointer: str) -> dict:
    return {"artifact": path, "pointer": pointer, "sha256": MANIFEST.get(path) or file_sha(path)}


MS = "evidence/paper-migration/matched-study-contrasts.json"

CLAIMS = [
    ("C-POP", "Common scored population: 8,297 of 8,324 held-out variants, 314 disrupting, 460 groups; 27 excluded",
     "sec:population, tab:b100", "companion_computed", [member("out/metrics.json", "$.population")]),
    ("C-EXCL", "27 exclusions: 23 recorded alleles complementary to GRCh38; 4 ARHGEF3 outside the GENCODE 44 canonical span",
     "sec:population", "companion_computed",
     [member("out/excluded.csv", "all rows, reason column"), article("section 'The evaluation population is 8,297 of 8,324 held-out variants'")]),
    ("C-EXCL-TRAIN", "The orientation defect affects 90 cohort records (21 held-out records from the CYFIP1 exon) and 67 training-arm records",
     "sec:qc, sec:limitations", "matched_study_reported (exclusions addendum)",
     [article("check-variant section; Limits (Assembly)")]),
    ("C-BUILD", "Cohort build: 32,669 source rows, 27,733 eligible, 1,050 disrupting, 2,198 exons (2,185 spanned by eligible variants); legacy sequence reverse-complemented in 7,770; train 19,409/735/1,127; test 8,324/315/463",
     "sec:data", "companion_computed (article text only)", [article("section 'Reproduce the shortlist', build console block")]),
    ("C-KMER-BYTE", "Companion refit of kmer_cons is byte-identical to the published baseline-kmer-position-v2 predictions",
     "sec:controls", "companion_computed",
     [member("runs/controls/kmer_cons.predictions.tsv", "whole file; SHA-256 equals companion PINNED digest"),
      repo("companion/README.md", "Expected results, first bullet")]),
    ("C-HP-SEL", "Validation grid selects (0.06, 15) for kmer_assay and (0.1, 15) for kmer_cons; published (0.06, 31) kept as default",
     "sec:controls, tab:valgrid", "companion_computed", [member("runs/controls/receipt.json", "$.methods.*.validation_grid, validation_selected")]),
    ("C-REPLAY", "Replay reproduces matched-study AP and AUROC to 1e-12 and registered-order P@100",
     "sec:replay", "saved_score_replay", [repo("companion/README.md", "Expected results, second bullet"), article("text after Table 2")]),
    ("C-GTF", "GENCODE 44 GTF yields 62,754 Ensembl_canonical transcripts", "sec:replay",
     "companion_computed (article text only)", [article("section 'Reproduce the shortlist', annotation paragraph")]),
    ("T2", "Budget-100 table: expected P@100 with tie range, registered-order P@100, tie size, recall, AP, AUROC",
     "tab:b100", "companion_computed + saved_score_replay",
     [member("out/metrics.json", "$.methods.<name>.{precision_at_budget_expected, precision_at_budget_range, precision_at_budget_registered_tie_order, tied_at_cutoff, recall_at_budget_expected, average_precision, auroc}")]),
    ("T2-RES", "Resources: controls 30.81 s and 278.1 MB peak RSS; specialist scoring 6,921/6,102/19,153/18,655 s recorded by the matched study; downloads",
     "tab:resources", "companion_computed + matched_study_reported",
     [member("out/metrics.json", "$.resources"), member("runs/controls/receipt.json", "$.seconds_end_to_end, $.peak_rss_mb")]),
    ("T3", "Paired differences against kmer_cons at 25 (post hoc), 100, 300 (post hoc), AP, AUROC",
     "tab:contrasts-hist, fig:forest", "companion_computed + saved_score_replay",
     [member("out-b25/metrics.json", "$.paired_contrasts['<m> - kmer_cons']"),
      member("out/metrics.json", "$.paired_contrasts['<m> - kmer_cons']"),
      member("out-b300/metrics.json", "$.paired_contrasts['<m> - kmer_cons']")]),
    ("T3-ZERO", "Share of bootstrap draws with a P@k difference of exactly zero; realised depths",
     "tab:zero-share, tab:depths", "companion_computed",
     [member(f"{d}/metrics.json", "$.paired_contrasts.*.precision_at_budget.share_of_draws_exactly_zero; realised_depth")
      for d in ("out-b25", "out", "out-b300", "out-selected-b100", "out-tutorial")]),
    ("T4", "Paired differences against kmer_cons_selected at 100", "tab:contrasts-sel", "companion_computed + saved_score_replay",
     [member("out-selected-b100/metrics.json", "$.paired_contrasts['<m> - kmer_cons_selected']")]),
    ("M-STUDY", "Matched-study specialist-pair contrasts (S1-S0, P1-P0, P0-S0) on P@100, AP and AUROC",
     "tab:matched", "matched_study_reported (transcribed)",
     [repo(MS, "$.contrasts"), article("section 'At 100 experiments...', paragraph after Table 3")]),
    ("T5", "Expected precision with tie range at 25, 100 and 300", "tab:budgets", "companion_computed + saved_score_replay",
     [member(f"{d}/metrics.json", "$.methods.<name>.precision_at_budget_expected/range") for d in ("out-b25", "out", "out-b300")]),
    ("F4", "Budget curve at k in {10,...,800}; SpliceAI P@10 = 0.548", "fig:budget, tab:curve", "companion_computed + saved_score_replay",
     [member("out/metrics.json", "$.methods.<name>.budget_curve"), repo("article/assets/04-budget-curve.svg", "figure")]),
    ("F5", "Forest plot of paired P@k differences", "fig:forest", "companion_computed + saved_score_replay",
     [repo("article/assets/05-paired-differences-forest.svg", "figure")]),
    ("T6", "Junction-distance bands: disruptors captured in top 100/300 and within-band AUROC", "tab:bands, tab:bands-full",
     "companion_computed + saved_score_replay",
     [member("out/metrics.json", "$.junction_distance_bands"), member("out-b300/metrics.json", "$.junction_distance_bands"),
      member("out-b25/metrics.json", "$.junction_distance_bands")]),
    ("C-OVERLAP", "Top-100 overlap: kmer_cons and P0 share 61; S0 and P0 share 88", "sec:ties, tab:overlap", "companion_computed",
     [member("out/metrics.json", "$.top_k_overlap")]),
    ("C-TIES", "Tie structure at 25 (SpliceAI 7 at 1.00, 23 at 0.99 for 18 slots), at 100 (P1 3 tied for 2 slots) and distance (171 tied)",
     "sec:ties", "companion_computed + saved_score_replay",
     [member("out-b25/metrics.json", "$.methods.S1.tied_at_cutoff, slots"), member("out/metrics.json", "$.methods.P1, distance"),
      article("section 'One variant passes the scoring checks...'")]),
    ("C-CASES", "IPO9 and COL1A2 case variants (ranks under kmer_cons and specialists)", "sec:ties",
     "companion_computed (article text only; imported, unverified)", [article("final paragraph of the ties section")]),
    ("C-CHECKVAR", "check-variant worked examples: DDX1 passes; CYFIP1 fails reference check (135 vs 0 mismatches); ARHGEF3 outside canonical span",
     "sec:qc", "companion_computed (article text only)", [article("check-variant console blocks")]),
    ("C-DEPTH", "Realised bootstrap depths 21-31, 83-126, 250-378", "sec:stats, tab:depths", "companion_computed",
     [member(f"{d}/metrics.json", "$.paired_contrasts.*.realised_depth") for d in ("out-b25", "out", "out-b300")]),
    ("C-TUTORIAL", "Tutorial subset 977 variants, 44 disrupting, 58 groups; pipeline check only", "app:supp, tab:tutorial",
     "companion_computed", [member("out-tutorial/metrics.json", "$.population, $.paired_contrasts")]),
    ("C-COUNTS-INTERVALS", "Interval inventory: 9 matched-study, 20 distinct against kmer_cons, 12 against kmer_cons_selected; none adjusted",
     "sec:stats", "companion_computed + matched_study_reported", [article("section 'The evaluation population...', third paragraph")]),
    ("C-ARCHIVED-ANN", "Archived runs with other annotations scored 8,194 and 8,301 variants; not pooled", "sec:limitations",
     "matched_study_reported", [article("Limits and failure cases, Coverage")]),
    ("C-EXEC", "Companion commands executed 29-30 September 2026 by an AI coding agent on an Apple M4 CPU (macOS 26.6.2, uv 0.8.2); clean-archive rerun byte-identical except timing fields; pytest 26 passed",
     "sec:provenance", "execution record (article text only)", [article("section 'Reproduce the shortlist', final paragraphs")]),
    ("L-MFASS", "MFASS design, disruption definition, 27,733 variants, 1,050 (3.8%) disrupting, 83% outside canonical sites; 13 of 19 confirmed",
     "sec:background, sec:limitations", "literature (not re-retrieved)", [article("decision section; Limits")]),
    ("L-THRESH", "Optimal thresholds vary between exons, regions and variant classes (Smith and Kitzman)", "sec:background",
     "literature (not re-retrieved)", [article("decision section; Figure 2 caption")]),
    ("L-MASKFIG", "Background masking and annotation effects (11,795 / 8,719; 280 / 270; read from figure)", "sec:background, fig:mask",
     "literature (values read from a figure)", [article("Figure 3 caption")]),
    ("L-CLINGEN", "SpliceAI >=0.2 / <=0.1 are ClinGen calibrations; 0.2 high-recall and 0.5 recommended in SpliceAI README", "sec:background",
     "literature (not re-retrieved)", [article("decision section")]),
    ("L-CAGI5", "CAGI5: predicting a splicing assay cannot directly imply clinical significance", "sec:limitations",
     "literature (not re-retrieved)", [article("Limits, Reporter to patient")]),
    ("L-MASKDEF", "Mask defaults and semantics differ (SpliceAI -M 0, Pangolin -m True); per-gene patch", "sec:replay",
     "literature (not re-retrieved)", [article("Configurations section")]),
    ("L-LICENCES", "Pangolin GPL-3.0; SpliceAI PolyForm Strict 1.0.0 / CC BY-NC 4.0 vs PyPI GPLv3; MFASS no licence", "sec:availability",
     "literature (not re-retrieved)", [article("Limits and failure cases, licence paragraph")]),
    ("I-MAIN", "At 100, no specialist P@100 difference against either baseline was established; not equivalence", "abstract, sec:discussion",
     "interpretation", [member("out/metrics.json", "$.paired_contrasts"), member("out-selected-b100/metrics.json", "$.paired_contrasts")]),
    ("I-P300", "Pangolin P@300 and whole-list intervals exclude zero; 300 post hoc, so a lead to test", "abstract, sec:discussion",
     "interpretation", [member("out-b300/metrics.json", "$.paired_contrasts")]),
]


def main() -> None:
    ledger = {
        "schema_version": 1,
        "status": "historical_imported: every value comes from the 2026-09-29/30 companion run, the matched study it replays, "
                  "or the cited literature; nothing was recomputed or reproduced during migration",
        "evidence_classes": {
            "companion_computed": "computed/fitted by the companion on 2026-09-29/30 (archived outputs zip)",
            "saved_score_replay": "companion re-evaluation of published SpliceAI/Pangolin predictions (no inference)",
            "matched_study_reported": "values reported by rewire-benchmarks@093fd1a, cited or transcribed",
            "literature": "published third-party sources as cited in the original article; not re-retrieved",
            "interpretation": "authorial reading of the recorded values",
        },
        "claims": [{"id": i, "claim": c, "manuscript": loc, "evidence_class": cls, "evidence": ev}
                   for i, c, loc, cls, ev in CLAIMS],
    }
    out = ROOT / "evidence/paper-migration/claims-ledger.json"
    out.write_text(json.dumps(ledger, indent=2) + "\n")
    print(f"claims ledger: {len(CLAIMS)} claims")


if __name__ == "__main__":
    main()
