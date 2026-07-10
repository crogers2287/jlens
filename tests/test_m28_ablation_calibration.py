#!/usr/bin/env python3
"""M28 ablation/calibration tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m26_objective_error as M26  # noqa: E402
import m27_frozen_error_holdout as M27  # noqa: E402
import m28_ablation_calibration as M28  # noqa: E402
from test_m27_frozen_error_holdout import _synthetic_files  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m26_error_manifest.json"


def _report(tmp_path, separable=True):
    manifest, labels_path, telemetry_path = _synthetic_files(
        tmp_path, separable=separable)
    split, _ = M27.load_dataset(labels_path, telemetry_path)
    return M28.build_report(manifest, split), manifest, split


def test_fail_probability_is_bounded_and_orders_separable_rows(tmp_path):
    _, manifest, split = _report(tmp_path)
    classifier = M27.FrozenDictCentroid.fit(
        [row for _, row in split["train"]],
        [label_row["label"] for label_row, _ in split["train"]],
        manifest["frozen_feature_sets"]["full_telemetry"])
    fail_scores, pass_scores = [], []
    for label_row, row in split["holdout"]:
        probability = M28.fail_probability(classifier, row)
        assert 0.0 <= probability <= 1.0
        (fail_scores if label_row["label"] == "fail" else pass_scores).append(
            probability)
    assert min(fail_scores) > max(pass_scores)


def test_ablation_covers_every_full_telemetry_feature(tmp_path):
    report, manifest, _ = _report(tmp_path)
    features = manifest["frozen_feature_sets"]["full_telemetry"]
    assert set(report["ablation"]["single_feature"]) == set(features)
    assert set(report["ablation"]["leave_one_out"]) == set(features)
    assert len(features) == 10
    assert "excluded by design" in str(
        report["ablation"]["verifier_contradiction_feature"])


def test_calibration_bins_ece_and_candidate_threshold(tmp_path):
    report, _, _ = _report(tmp_path)
    calibration = report["calibration"]
    bins = calibration["reliability_bins_equal_count"]
    assert len(bins) == 4 and sum(item["n"] for item in bins) == 32
    assert 0.0 <= calibration["expected_calibration_error"] <= 1.0
    threshold = calibration["candidate_threshold"]
    assert threshold["status"] == "candidate-only"
    assert threshold["not_for_production"] is True
    assert threshold["derived_from"].startswith("train split")
    assert 0.0 < threshold["threshold_fail_probability"] < 1.0


def test_error_analysis_counts_are_aggregate_and_complete(tmp_path):
    report, _, _ = _report(tmp_path)
    analysis = report["false_positive_negative_analysis"]
    assert analysis["positive_class"] == "fail"
    assert sum(analysis["totals"].values()) == 32
    assert sum(counts["n"] for counts in analysis["by_band"].values()) == 32


def test_public_report_is_candidate_only_without_ids_or_text(tmp_path):
    report, _, _ = _report(tmp_path)
    public = json.dumps(report)
    assert "candidate-only" in public
    assert report["production_threshold_set"] is False
    assert "m26_a_" not in public and "What is" not in public
    assert report["small_holdout_caveat"].startswith("n=32")
    assert set(M26.FEATURES) == set(
        report["ablation"]["single_feature"])
