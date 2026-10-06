"""Tests for splice_shortlist.py.

Unit tests run anywhere. Data tests need `fetch`, `build`, `controls` and
`evaluate --budget 100 --method P0` to have been run first and are skipped
otherwise.
"""
import csv
import json
import pathlib

import numpy as np
import pytest

import splice_shortlist as ss

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "out"
needs_data = pytest.mark.skipif(not (OUT / "metrics.json").exists(),
                                reason="run fetch/build/controls/evaluate first")


# ------------------------------------------------------------------ unit tests

def test_budget_precision_without_ties():
    labels = [1, 0, 1, 0, 0]
    scores = [0.9, 0.8, 0.7, 0.2, 0.1]
    r = ss.budget_precision(labels, scores, 2)
    assert r["expected"] == r["min"] == r["max"] == 0.5
    assert r["tied_at_cutoff"] == 1


def test_budget_precision_with_tied_block():
    # Top score alone, then four tied for the remaining two slots, one positive among them.
    labels = [1, 1, 0, 0, 0, 0]
    scores = [0.9, 0.5, 0.5, 0.5, 0.5, 0.1]
    r = ss.budget_precision(labels, scores, 3)
    assert r["tied_at_cutoff"] == 4 and r["slots_in_tied_block"] == 2
    assert r["min"] == pytest.approx(1 / 3)
    assert r["max"] == pytest.approx(2 / 3)
    assert r["expected"] == pytest.approx((1 + 2 * 1 / 4) / 3)


def test_constant_scores_give_prevalence():
    labels = [1, 0, 0, 0]
    r = ss.budget_precision(labels, [0.3] * 4, 2)
    assert r["expected"] == pytest.approx(0.25)
    assert (r["min"], r["max"]) == (0.0, 0.5)


def test_junction_distance_is_symmetric_around_both_junctions():
    row = {"intron1_len": "40", "exon_len": "60"}
    # Intron 1 is positions 1..40, exon 41..100, intron 2 from 101.
    assert ss.junction_distance({**row, "rel_position": "40"}) == 0
    assert ss.junction_distance({**row, "rel_position": "41"}) == 0
    assert ss.junction_distance({**row, "rel_position": "38"}) == 2
    assert ss.junction_distance({**row, "rel_position": "100"}) == 0
    assert ss.junction_distance({**row, "rel_position": "101"}) == 0
    assert ss.junction_distance({**row, "rel_position": "70"}) == 29


def test_assay_pair_rejects_allele_disagreement():
    ref = "A" * 170
    mut = "A" * 9 + "G" + "A" * 160
    row = {"id": "x", "natural_seq": ref, "original_seq": mut, "sequence": mut,
           "rel_position": "10", "strand": "+", "ref_allele": "A", "alt_allele": "G"}
    assert ss.assay_pair(row)[2] == "assay"
    with pytest.raises(ValueError):
        ss.assay_pair({**row, "alt_allele": "T"})
    # On the minus strand the genomic alleles are complemented before comparison.
    assert ss.assay_pair({**row, "strand": "-", "ref_allele": "T", "alt_allele": "C"})[0] == ref


# ------------------------------------------------------------------ data tests

@needs_data
def test_every_pinned_input_verified():
    receipt = json.loads((ss.DATA / "fetch-receipt.json").read_text())
    assert len(receipt) == len(ss.PINNED)
    assert all(r["status"] == "ok" for r in receipt)


@needs_data
def test_split_counts():
    rows = ss.load_cohort()
    test = [r for r in rows if r["split"] == "test"]
    assert len(rows) == 27733 and sum(r["sdv"] for r in rows) == 1050
    assert len(test) == 8324 and sum(r["sdv"] for r in test) == 315
    assert len({r["group"] for r in test}) == 463


@needs_data
def test_cpu_rerun_reproduces_published_baseline_predictions():
    def load(p):
        return {r["id"]: float(r["score"]) for r in csv.DictReader(open(p), delimiter="\t")}
    published = load(ss.DATA / "baseline-kmer-position-v2.predictions.tsv")
    rerun = load(ss.RUNS / "controls" / "kmer_cons.predictions.tsv")
    assert published.keys() == rerun.keys()
    assert max(abs(published[i] - rerun[i]) for i in published) < 1e-9


@needs_data
def test_replay_reproduces_study_metrics():
    m = json.loads((OUT / "metrics.json").read_text())
    for cond in ss.SPECIALISTS:
        pub = json.loads((ss.DATA / f"{cond}.json").read_text())["metrics"]
        t = m["methods"][cond]
        assert t["average_precision"] == pytest.approx(pub["average_precision_sklearn"], abs=1e-12)
        assert t["auroc"] == pytest.approx(pub["auroc"], abs=1e-12)
        assert t["precision_at_budget_registered_tie_order"] == pub["precision_at_capacity"]


@needs_data
def test_common_population_and_exclusions():
    m = json.loads((OUT / "metrics.json").read_text())
    assert m["population"] == {"held_out": 8324, "common_scored": 8297, "positives": 314,
                               "groups": 460, "excluded": 27}
    reasons = [r["reason"] for r in csv.DictReader(open(OUT / "excluded.csv"))]
    assert sum("orientation" in r for r in reasons) == 23
    assert sum("canonical transcript span" in r for r in reasons) == 4


@needs_data
def test_masked_pangolin_p100_depends_on_tie_order():
    t = json.loads((OUT / "metrics.json").read_text())["methods"]["P1"]
    assert t["precision_at_budget_range"] == [0.65, 0.66]
    assert t["tied_at_cutoff"] == 3


@needs_data
def test_outputs_do_not_republish_alleles_or_sequences():
    for name in ("shortlist.csv", "excluded.csv"):
        header = next(csv.reader(open(OUT / name)))
        assert not {"ref_allele", "alt_allele", "reference_sequence", "mutant_sequence"} & set(header)


@needs_data
def test_shortlist_contains_budget_plus_ties():
    m = json.loads((OUT / "metrics.json").read_text())
    rows = list(csv.DictReader(open(OUT / "shortlist.csv")))
    assert len(rows) >= m["budget"]
    scores = np.array([float(r["score"]) for r in rows])
    assert np.all(np.diff(scores) <= 0)


@needs_data
def test_distance_bands_partition_the_population_and_hits():
    m = json.loads((OUT / "metrics.json").read_text())
    bands = m["junction_distance_bands"].values()
    assert sum(b["variants"] for b in bands) == m["population"]["common_scored"]
    assert sum(b["disrupting"] for b in bands) == m["population"]["positives"]
    for name in ("kmer_cons", "S0", "P0"):
        hits = sum(b["methods"][name]["disrupting_in_top_k"] for b in bands)
        expected = m["methods"][name]["precision_at_budget_registered_tie_order"] * m["budget"]
        assert hits == round(expected)


# ------------------------------------------------------------ input validation

@pytest.mark.parametrize("k", [0, -1, 4])
def test_helpers_reject_budgets_outside_the_population(k):
    labels, scores = [1, 0, 1], [0.9, 0.5, 0.1]
    with pytest.raises(ValueError):
        ss.budget_precision(labels, scores, k)
    with pytest.raises(ValueError):
        ss.registered_precision(labels, scores, k)


def test_helpers_agree_at_the_full_population():
    labels, scores = [1, 0, 1], [0.9, 0.5, 0.1]
    assert ss.budget_precision(labels, scores, 3)["expected"] == pytest.approx(2 / 3)
    assert ss.registered_precision(labels, scores, 3)[0] == pytest.approx(2 / 3)


def _cli(*args):
    import subprocess
    import sys
    return subprocess.run([sys.executable, str(HERE / "splice_shortlist.py"), *args],
                          capture_output=True, text=True, cwd=HERE)


@pytest.mark.parametrize("draws", ["0", "99", "-5"])
def test_cli_rejects_too_few_draws(draws):
    r = _cli("evaluate", "--budget", "10", "--method", "P0", "--draws", draws, "--out", "unused")
    assert r.returncode != 0 and "--draws must be at least 100" in r.stderr


@needs_data
@pytest.mark.parametrize("budget", ["0", "-1", "8298"])
def test_cli_rejects_budgets_outside_the_common_population(budget):
    out = ss.RUNS / "test-invalid-budget"
    r = _cli("evaluate", "--budget", budget, "--method", "P0", "--out", str(out))
    assert r.returncode != 0 and "--budget must be between 1 and 8297" in r.stderr
    assert not (out / "metrics.json").exists()


@needs_data
def test_validation_selected_models_are_exportable_and_usable_as_baseline():
    import shutil
    receipt = json.loads((ss.RUNS / "controls" / "receipt.json").read_text())
    for name in ("kmer_assay", "kmer_cons"):
        assert (ss.RUNS / "controls" / f"{name}_selected.predictions.tsv").exists()
        assert "validation_selected" in receipt["methods"][name]
    out = ss.RUNS / "test-selected-export"
    shutil.rmtree(out, ignore_errors=True)
    r = _cli("evaluate", "--tutorial", "--budget", "20", "--draws", "100",
             "--baseline", "kmer_cons_selected", "--method", "kmer_cons_selected", "--out", str(out))
    assert r.returncode == 0, r.stderr
    m = json.loads((out / "metrics.json").read_text())
    assert m["baseline_for_contrasts"] == "kmer_cons_selected"
    assert set(m["paired_contrasts"]) == {f"{c} - kmer_cons_selected" for c in ss.SPECIALISTS}
    assert m["methods"]["kmer_cons_selected"]["scores_from"].endswith("(validation-selected settings)")
    shutil.rmtree(out)


@needs_data
def test_bootstrap_records_variable_realised_depths():
    m = json.loads((OUT / "metrics.json").read_text())
    for c in m["paired_contrasts"].values():
        d = c["realised_depth"]
        assert d["nominal"] == m["budget"] and d["min"] < m["budget"] < d["max"]


# Prospective integrity guards; no source data or scientific rerun required.
@pytest.mark.parametrize("rows, message", [
    (["x\tg1\t1\t0.1", "x\tg1\t1\t0.2"], "duplicate"),
    (["x\tg1\t1\tnan"], "nonfinite"),
    (["x\tg1\t1\tinf"], "nonfinite"),
    (["x\tg1\t0\t0.1"], "label/group mismatch"),
    (["x\tg2\t1\t0.1"], "label/group mismatch"),
    (["other\tg1\t1\t0.1"], "outside held-out"),
])
def test_scores_reject_ambiguous_or_corrupt_rows(tmp_path, monkeypatch, rows, message):
    monkeypatch.setattr(ss, "DATA", tmp_path)
    (tmp_path / "S0.predictions.tsv").write_text("id\tgroup\tlabel\tscore\n" + "\n".join(rows) + "\n")
    with pytest.raises(ValueError, match=message):
        ss.load_scores("S0", {"x": {"group": "g1", "sdv": 1}})


def test_missing_control_score_is_not_silently_excluded(tmp_path, monkeypatch):
    monkeypatch.setattr(ss, "RUNS", tmp_path)
    (tmp_path / "controls").mkdir()
    (tmp_path / "controls/kmer_cons.predictions.tsv").write_text("id\tgroup\tlabel\tscore\nx\tg1\t1\t\n")
    with pytest.raises(ValueError, match="cover every held-out"):
        ss.load_scores("kmer_cons", {"x": {"group": "g1", "sdv": 1}})


def test_missingness_requires_exact_exclusion_accounting():
    ss.validate_exclusions({"a": {}, "b": {}}, ["a"], [{"id": "b"}])
    for report in ([], [{"id": "a"}], [{"id": "b"}, {"id": "b"}]):
        with pytest.raises(ValueError, match="missingness"):
            ss.validate_exclusions({"a": {}, "b": {}}, ["a"], report)


def test_cohort_rejects_group_leakage_and_duplicate_ids():
    rows = [{"id": "a", "group": "g1", "sdv": 1, "split": "train"},
            {"id": "b", "group": "g2", "sdv": 0, "split": "test"}]
    ss.validate_cohort(rows)
    with pytest.raises(ValueError, match="groups overlap"):
        ss.validate_cohort([rows[0], {**rows[1], "group": "g1"}])
    with pytest.raises(ValueError, match="duplicate"):
        ss.validate_cohort([rows[0], {**rows[1], "id": "a"}])
