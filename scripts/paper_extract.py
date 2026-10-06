#!/usr/bin/env python3
"""Format archived historical results into LaTeX tables for the imported-evidence paper.

Formatting and extraction only. Nothing is recomputed: every number below is read from a
member of the archived `downloads/splice-shortlist-outputs.zip` (read in memory, never
extracted to disk) or from the transcribed matched-study record in
`evidence/paper-migration/matched-study-contrasts.json`. Each member's SHA-256 is checked
against `evidence/reference-output-members.json` and the archive digest against
`evidence/import-manifest.json` before any value is used. Generated strings are then
cross-checked against the values the original article reported (as transcribed in
`migration-plan/evidence-map.json`); any disagreement stops the build.

Standard library only; no network, no environment creation.
"""
from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZIP = ROOT / "downloads/splice-shortlist-outputs.zip"
GEN = ROOT / "paper/generated"
PREFIX = "splice-shortlist/"
RUNS = {"b25": "out-b25", "b100": "out", "b300": "out-b300", "sel": "out-selected-b100", "tut": "out-tutorial"}
ORDER = ["prevalence", "distance", "kmer_assay", "kmer_cons", "kmer_assay_selected", "kmer_cons_selected",
         "S0", "S1", "P0", "P1"]
SPEC = ["S0", "S1", "P0", "P1"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def tt(name: str) -> str:
    return r"\texttt{" + name.replace("_", r"\_") + "}"


def signed(x: float, nd: int = 3) -> str:
    s = f"{x:+.{nd}f}"
    if s in ("+0." + "0" * nd, "-0." + "0" * nd):
        s = "+0." + "0" * nd
    return s


def m(s: str) -> str:
    """Typeset a signed decimal string in math mode (true minus sign)."""
    return "$" + s + "$"


def ci(observed: float, lo: float, hi: float) -> tuple[str, str]:
    plain = f"{signed(observed)} [{signed(lo)}, {signed(hi)}]"
    tex = f"\\ci{{{m(signed(observed))}}}{{{m(signed(lo))}}}{{{m(signed(hi))}}}"
    return plain, tex


def rng(expected: float, lo: float, hi: float) -> tuple[str, str]:
    plain = f"{expected:.3f} [{lo:.2f}, {hi:.2f}]"
    return plain, plain


def load_archive() -> tuple[dict, dict]:
    manifest = json.loads((ROOT / "evidence/import-manifest.json").read_text())
    want_zip = next(f["sha256"] for f in manifest["files"] if f["path"] == "downloads/splice-shortlist-outputs.zip")
    raw = ZIP.read_bytes()
    if sha256(raw) != want_zip:
        sys.exit(f"archive digest mismatch for {ZIP.name}")
    members = json.loads((ROOT / "evidence/reference-output-members.json").read_text())["members"]
    zf = zipfile.ZipFile(io.BytesIO(raw))
    used = {}

    def read(member: str) -> bytes:
        data = zf.read(PREFIX + member)
        if sha256(data) != members[PREFIX + member]:
            sys.exit(f"member digest mismatch: {member}")
        used[PREFIX + member] = members[PREFIX + member]
        return data

    metrics = {k: json.loads(read(f"{d}/metrics.json")) for k, d in RUNS.items()}
    receipt = json.loads(read("runs/controls/receipt.json"))
    return {"metrics": metrics, "receipt": receipt, "zip_sha256": want_zip}, used


def write(name: str, text: str) -> None:
    (GEN / name).write_text(text)


def main() -> None:
    GEN.mkdir(parents=True, exist_ok=True)
    data, used = load_archive()
    M, R = data["metrics"], data["receipt"]
    emap = json.loads((ROOT / "migration-plan/evidence-map.json").read_text())
    claims = {c["id"]: c for c in emap["claims"]}
    mismatches: list[str] = []

    def check(label: str, got: str, want: str) -> None:
        if got.replace("−", "-") != want.replace("−", "-"):
            mismatches.append(f"{label}: generated {got!r} != article {want!r}")

    # ---- population sanity (exact)
    pop = M["b100"]["population"]
    for k, v in claims["C-POP"]["values"].items():
        if k in pop and pop[k] != v:
            mismatches.append(f"population {k}: {pop[k]} != {v}")

    # ---- Table: budget 100 summary
    b = M["b100"]["methods"]
    res = M["b100"]["resources"]
    t2 = claims["T2"]["rows"]
    source = {"prevalence": "Computed", "distance": "Computed (fixed rule)", "kmer_assay": "Fitted",
              "kmer_cons": "Fitted", "kmer_assay_selected": "Fitted (val.\\ selected)",
              "kmer_cons_selected": "Fitted (val.\\ selected)", "S0": "Replay", "S1": "Replay",
              "P0": "Replay", "P1": "Replay"}
    lines = []
    for name in ORDER:
        x = b[name]
        p_plain, p_tex = rng(x["precision_at_budget_expected"], *x["precision_at_budget_range"])
        if name in t2:
            check(f"T2 {name} P@100", p_plain, f"{t2[name]['p100']} {t2[name]['range']}")
            check(f"T2 {name} AP", f"{x['average_precision']:.3f}", t2[name]["ap"])
            check(f"T2 {name} AUROC", f"{x['auroc']:.3f}", t2[name]["auroc"])
        scored = f"{x['scored_of_original'][0]:,}"
        lines.append(f"{tt(name)} & {source[name]} & {scored} & {p_tex} & "
                     f"{x['precision_at_budget_registered_tie_order']:.2f} & {x['tied_at_cutoff']:,} & "
                     f"{x['recall_at_budget_expected']:.3f} & {x['average_precision']:.3f} & {x['auroc']:.3f} \\\\")
        if name == "kmer_cons_selected":
            lines.append(r"\midrule")
    write("tab_b100.tex", "\n".join(lines) + "\n")

    # ---- Table: resources
    ctl = res["controls_measured_here"]
    spec = res["specialists_recorded_by_study"]
    rl = [f"Controls (all six, incl.\\ 12-fit validation grid) & Measured in the companion run & "
          f"{ctl['seconds_end_to_end']:.2f}\\,s end to end & {ctl['peak_rss_mb']:.1f}\\,MB \\\\"]
    for name in SPEC:
        s = spec[name]
        rl.append(f"{tt(name)} scoring of the held-out arm & Recorded by matched study & "
                  f"{s['score_test']:,.0f}\\,s ({s['per_variant_total']:.2f}\\,s/variant) & not recorded \\\\")
    write("tab_resources.tex", "\n".join(rl) + "\n")
    dl = []
    for k, v in res["specialist_downloads_bytes"].items():
        dl.append(f"{k} & {v / 1e6:,.0f}\\,MB \\\\")
    write("tab_downloads.tex", "\n".join(dl) + "\n")

    # ---- Table: paired contrasts vs kmer_cons
    t3 = claims["T3"]["rows"]
    keymap = {"b25": "p25_posthoc", "b100": "p100", "b300": "p300_posthoc"}
    lines = []
    for name in SPEC:
        cells = []
        for run in ("b25", "b100", "b300"):
            c = M[run]["paired_contrasts"][f"{name} - kmer_cons"]["precision_at_budget"]
            plain, tex = ci(c["observed"], *c["ci95"])
            check(f"T3 {name} {run}", plain, t3[name][keymap[run]])
            cells.append(tex)
        for met, key in (("average_precision", "ap"), ("auroc", "auroc")):
            c = M["b100"]["paired_contrasts"][f"{name} - kmer_cons"][met]
            plain, tex = ci(c["observed"], *c["ci95"])
            check(f"T3 {name} {met}", plain, t3[name][key])
            # AP/AUROC must not depend on budget: confirm identical across the three runs
            for run in ("b25", "b300"):
                if M[run]["paired_contrasts"][f"{name} - kmer_cons"][met] != c:
                    mismatches.append(f"{name} {met} differs between budget runs")
            cells.append(tex)
        lines.append(f"{tt(name)} & " + " & ".join(cells) + r" \\")
    write("tab_contrasts_hist.tex", "\n".join(lines) + "\n")

    # share of bootstrap draws with a difference of exactly zero, and realised depths
    lines = []
    for name in SPEC:
        cells = []
        for run in ("b25", "b100", "b300", "sel"):
            base = "kmer_cons_selected" if run == "sel" else "kmer_cons"
            c = M[run]["paired_contrasts"][f"{name} - {base}"]["precision_at_budget"]
            cells.append(f"{100 * c['share_of_draws_exactly_zero']:.2f}\\%")
        lines.append(f"{tt(name)} & " + " & ".join(cells) + r" \\")
    depths = []
    for run, label in (("b25", "25"), ("b100", "100"), ("b300", "300"), ("sel", "100 (selected baseline)"),
                       ("tut", "20 (tutorial subset)")):
        any_c = next(iter(M[run]["paired_contrasts"].values()))
        d = any_c["realised_depth"]
        depths.append(f"{label} & {d['min']}--{d['max']} & {d['mean']:.1f} & {any_c['draws']:,} & "
                      f"{any_c['groups']} & {any_c['single_class_skipped']} \\\\")
    write("tab_zero_share.tex", "\n".join(lines) + "\n")
    write("tab_depths.tex", "\n".join(depths) + "\n")

    # ---- Table: contrasts vs validation-selected baseline
    t4 = claims["T4"]["rows"]
    lines = []
    for name in SPEC:
        cells = []
        for met, key in (("precision_at_budget", "p100"), ("average_precision", "ap"), ("auroc", "auroc")):
            c = M["sel"]["paired_contrasts"][f"{name} - kmer_cons_selected"][met]
            plain, tex = ci(c["observed"], *c["ci95"])
            check(f"T4 {name} {met}", plain, t4[name][key])
            cells.append(tex)
        lines.append(f"{tt(name)} & " + " & ".join(cells) + r" \\")
    write("tab_contrasts_sel.tex", "\n".join(lines) + "\n")

    # ---- Table: precision at 25 / 100 / 300 with tie ranges
    t5 = claims["T5"]["rows"]
    lines = []
    for name in ORDER[1:]:
        cells = []
        for i, run in enumerate(("b25", "b100", "b300")):
            x = M[run]["methods"][name]
            plain, tex = rng(x["precision_at_budget_expected"], *x["precision_at_budget_range"])
            if name in t5:
                check(f"T5 {name} {run}", plain, t5[name][i])
            cells.append(tex)
        lines.append(f"{tt(name)} & " + " & ".join(cells) + r" \\")
    write("tab_budgets.tex", "\n".join(lines) + "\n")

    # ---- Table: full budget curve (appendix)
    ks = list(M["b100"]["methods"]["kmer_cons"]["budget_curve"].keys())
    head = " & ".join(ks)
    lines = [r"Configuration & " + head + r" \\", r"\midrule"]
    for name in ORDER:
        curve = M["b100"]["methods"][name]["budget_curve"]
        lines.append(f"{tt(name)} & " + " & ".join(f"{curve[k]:.3f}" for k in ks) + r" \\")
    write("tab_curve.tex", "\n".join(lines) + "\n")
    if f"{M['b100']['methods']['S0']['budget_curve']['10']:.3f}" != "0.548":
        mismatches.append("F4 SpliceAI P@10 is not 0.548")

    # ---- Table: junction-distance bands (main text, as in the article)
    t6 = claims["T6"]["rows"]
    lines = []
    for band, v100 in M["b100"]["junction_distance_bands"].items():
        v300 = M["b300"]["junction_distance_bands"][band]
        hits = [v100["methods"][n]["disrupting_in_top_k"] for n in ("kmer_cons", "P0", "P1")]
        hits += [v300["methods"][n]["disrupting_in_top_k"] for n in ("kmer_cons", "P0", "P1")]
        au = f"{v100['methods']['kmer_cons']['auroc_within_band']:.2f} / {v100['methods']['P0']['auroc_within_band']:.2f}"
        w = t6[band]
        want = [w["top100"][n] for n in ("kmer_cons", "P0", "P1")] + [w["top300"][n] for n in ("kmer_cons", "P0", "P1")]
        if hits != want or v100["variants"] != w["variants"] or v100["disrupting"] != w["disrupting"]:
            mismatches.append(f"T6 band {band}: {hits} != {want}")
        check(f"T6 {band} AUROC", au, w["auroc"])
        label = band.replace(">", "$>$").replace("-", "--")
        lines.append(f"{label} & {v100['variants']:,} & {v100['disrupting']} & " + " & ".join(map(str, hits))
                     + f" & {au} \\\\")
    write("tab_bands.tex", "\n".join(lines) + "\n")

    # ---- Appendix: bands for every configuration at 25, 100 and 300
    meths = ["distance", "kmer_assay", "kmer_cons", "S0", "S1", "P0", "P1"]
    lines = []
    for run, k in (("b25", 25), ("b100", 100), ("b300", 300)):
        for band, v in M[run]["junction_distance_bands"].items():
            label = band.replace(">", "$>$").replace("-", "--")
            cells = [f"{v['methods'][n]['disrupting_in_top_k']} ({v['methods'][n]['auroc_within_band']:.2f})"
                     for n in meths]
            lines.append(f"{k} & {label} & {v['disrupting']} & " + " & ".join(cells) + r" \\")
        if k != 300:
            lines.append(r"\midrule")
    write("tab_bands_full.tex", "\n".join(lines) + "\n")

    # ---- Appendix: top-100 overlap matrix
    ov = {(o["a"], o["b"]): o["shared_in_top_k"] for o in M["b100"]["top_k_overlap"]}
    names = ["distance", "kmer_assay", "kmer_cons", "S0", "S1", "P0", "P1"]
    lines = []
    for a in names:
        row = []
        for b2 in names:
            if a == b2:
                row.append("--")
            else:
                row.append(str(ov.get((a, b2), ov.get((b2, a), ""))))
        lines.append(f"{tt(a)} & " + " & ".join(row) + r" \\")
    write("tab_overlap.tex", "\n".join(lines) + "\n")
    if ov[("kmer_cons", "P0")] != 61 or ov[("S0", "P0")] != 88:
        mismatches.append("C-OVERLAP mismatch")

    # ---- Appendix: validation grid
    lines = []
    for name in ("kmer_assay", "kmer_cons"):
        g = R["methods"][name]
        for row in g["validation_grid"]:
            mark = []
            if {"learning_rate": row["learning_rate"], "max_leaf_nodes": row["max_leaf_nodes"]} == g["params_used"]:
                mark.append("published")
            if {"learning_rate": row["learning_rate"], "max_leaf_nodes": row["max_leaf_nodes"]} == g["validation_selected"]:
                mark.append("selected")
            lines.append(f"{tt(name)} & {row['learning_rate']} & {row['max_leaf_nodes']} & "
                         f"{row['validation_ap']:.4f} & {', '.join(mark)} \\\\")
        lines.append(r"\midrule")
    lines.pop()
    split = R["methods"]["kmer_cons"]["validation_split"]
    write("tab_valgrid.tex", "\n".join(lines) + "\n")

    # ---- Matched-study specialist contrasts (transcribed)
    ms = json.loads((ROOT / "evidence/paper-migration/matched-study-contrasts.json").read_text())
    lines = []
    for label, v in ms["contrasts"].items():
        cells = []
        for key in ("p_at_100", "average_precision", "auroc"):
            c = v[key]
            cells.append(ci(c["observed"], *c["ci95"])[1])
        name, _, desc = label.partition(" (")
        lines.append(f"{name.replace(' - ', ' $-$ ')} ({desc} & " + " & ".join(cells) + r" \\")
    write("tab_matched.tex", "\n".join(lines) + "\n")
    mstudy = claims["M-STUDY"]["statement"]
    for needle in ("+0.020 [-0.033, +0.083]", "+0.093 [+0.064, +0.124]", "+0.073 [+0.048, +0.096]",
                   "+0.017 [+0.006, +0.028]", "+0.022 [+0.011, +0.034]"):
        if needle not in mstudy:
            mismatches.append(f"M-STUDY value {needle} not in evidence map")

    # ---- Tutorial subset (pipeline check only)
    tut = M["tut"]
    lines = []
    for name in SPEC:
        c = tut["paired_contrasts"][f"{name} - kmer_cons"]
        cells = [ci(c[k]["observed"], *c[k]["ci95"])[1] for k in ("precision_at_budget", "average_precision", "auroc")]
        lines.append(f"{tt(name)} & " + " & ".join(cells) + r" \\")
    write("tab_tutorial.tex", "\n".join(lines) + "\n")

    # ---- Macros
    tp = tut["population"]
    mac = {
        "HeldOut": f"{pop['held_out']:,}", "Common": f"{pop['common_scored']:,}", "Positives": str(pop["positives"]),
        "Groups": str(pop["groups"]), "Excluded": str(pop["excluded"]),
        "Draws": f"{M['b100']['paired_contrasts']['S0 - kmer_cons']['draws']:,}",
        "TrainVariants": f"{R['train_variants']:,}", "TrainGroups": f"{R['train_groups']:,}",
        "ValVariants": f"{split['validation_variants']:,}", "ValGroups": str(split["validation_groups"]),
        "ValPositives": str(split["validation_positives"]), "InnerVariants": f"{split['inner_variants']:,}",
        "ControlsSeconds": f"{R['seconds_end_to_end']:.2f}", "ControlsRSS": f"{R['peak_rss_mb']:.1f}",
        "PrevalenceTrain": f"{R['methods']['prevalence']['value']:.4f}",
        "TutVariants": str(tp["common_scored"]), "TutPositives": str(tp["positives"]), "TutGroups": str(tp["groups"]),
        "EnvPython": R["environment"]["python"], "EnvSklearn": R["environment"]["sklearn"],
        "EnvNumpy": R["environment"]["numpy"], "OutputsZipShort": data["zip_sha256"][:12],
    }
    write("macros.tex", "".join(f"\\newcommand{{\\{k}}}{{{v}}}\n" for k, v in mac.items()))

    receipt = {
        "schema_version": 1,
        "kind": "formatting/extraction only; no recomputation",
        "archive": "downloads/splice-shortlist-outputs.zip",
        "archive_sha256": data["zip_sha256"],
        "members_read_in_memory": used,
        "transcribed_inputs": {"evidence/paper-migration/matched-study-contrasts.json":
                               sha256((ROOT / "evidence/paper-migration/matched-study-contrasts.json").read_bytes())},
        "cross_check_against_article_values": "evidence-map T2, T3, T4, T5, T6, C-POP, C-OVERLAP, F4, M-STUDY",
        "cross_check_mismatches": mismatches,
        "generated": sorted(p.name for p in GEN.glob("*.tex")),
    }
    (GEN / "extraction-receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    if mismatches:
        print("\n".join(mismatches))
        sys.exit("generated tables disagree with the article's reported values")
    print(f"extracted {len(used)} archive members; {len(receipt['generated'])} generated files; 0 mismatches")


if __name__ == "__main__":
    main()
