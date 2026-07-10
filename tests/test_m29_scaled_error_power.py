#!/usr/bin/env python3
"""M29 scaled power-test tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m23_within_model as M23  # noqa: E402
import m29_scaled_error_power as M29  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m29_power_manifest.json"


def _telemetry(task_id, *, entropy, prob, high_count):
    return {
        "task_id": task_id,
        "capture_status": "completed",
        "decode_step_count": 8,
        "logits": {
            "status": "available",
            "selected_token_probability": prob,
            "top_k_margin": prob / 2,
            "window": {"step_count": 8, "mean_entropy": entropy,
                       "high_entropy_count": high_count,
                       "low_confidence_count": 1 if prob < 0.5 else 0,
                       "top_k_margin_trend": -0.05 if entropy > 1 else 0.02},
        },
        "router": {
            "status": "available",
            "router_entropy_mean": 2.5 + entropy / 10,
            "expert_concentration_mean": 0.2 + (0.05 if entropy > 1 else 0.0),
            "windowed_expert_shift": 0.1,
        },
    }


def _label_for(task, index):
    # Bands 1-2 pass, bands 4/6 fail, bands 3/5 mixed within band so the
    # metadata shortcut cannot be perfect while telemetry can be.
    if task["band"] in ("band_1", "band_2"):
        return "pass"
    if task["band"] in ("band_4", "band_6"):
        return "fail"
    return "fail" if index % 2 == 0 else "pass"


def _synthetic_files(tmp_path, *, telemetry_informative=True):
    manifest = M29.load_manifest(MANIFEST_PATH)
    labels, telemetry = [], []
    for index, task in enumerate(manifest["tasks"]):
        label = _label_for(task, index)
        if task["task_id"] == "m29_b1_002":
            label = "undecided"
        is_fail = label == "fail"
        entropy = (1.8 if is_fail else 0.4) if telemetry_informative else 1.0
        entropy += 0.001 * (index % 7)
        labels.append({"task_id": task["task_id"], "band": task["band"],
                       "split": task["split"], "label": label})
        telemetry.append(_telemetry(
            task["task_id"], entropy=entropy,
            prob=0.4 if is_fail and telemetry_informative else 0.9,
            high_count=6 if is_fail and telemetry_informative else 0))
    labels_path = tmp_path / "labels.jsonl"
    telemetry_path = tmp_path / "telemetry.jsonl"
    M23.write_jsonl(labels_path, labels)
    M23.write_jsonl(telemetry_path, telemetry)
    return manifest, labels_path, telemetry_path


def _walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_generation_is_deterministic_in_band_with_sealed_split():
    manifest = M29.load_manifest(MANIFEST_PATH)
    tasks = M29.generate_tasks(manifest)
    assert tasks == M29.generate_tasks(manifest)
    assert len(tasks) == 384
    bands = {band["band_id"]: band for band in manifest["bands"]}
    counts = {}
    expressions = {}
    for task in tasks:
        band = bands[task["m29_band"]]
        a, b = task["expression"].split(band["operator"], 1)
        a, b = int(a), int(b)
        assert band["operand_a_range"][0] <= a <= band["operand_a_range"][1]
        assert band["operand_b_range"][0] <= b <= band["operand_b_range"][1]
        assert task["known_answer"] == str(a * b)
        assert task["prompt"] == manifest["prompt_template"].format(
            a=a, op=band["operator"], b=b)
        key = (task["m29_band"], task["m29_split"])
        counts[key] = counts.get(key, 0) + 1
        expressions.setdefault(task["m29_band"], set()).add(task["expression"])
    for band_id in bands:
        assert counts[(band_id, "train")] == 32
        assert counts[(band_id, "validation")] == 16
        assert counts[(band_id, "holdout")] == 16
        assert len(expressions[band_id]) == 64


def test_load_dataset_builds_three_splits_and_excludes_undecided(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M29.load_dataset(manifest, labels_path, telemetry_path)
    assert len(split["train"]) == 191
    assert len(split["validation"]) == 96
    assert len(split["holdout"]) == 96
    assert undecided == {"train": 1}
    _, row = split["train"][0]
    assert sum(row[band] for band in
               ("band_1", "band_2", "band_3", "band_4", "band_5",
                "band_6")) == 1.0
    assert "high_entropy_count" in row and "router_entropy" in row


def test_power_check_reports_honest_flags(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M29.load_dataset(manifest, labels_path, telemetry_path)
    power = M29.check_power(manifest, split, undecided)
    assert power["increment_test_adequately_powered"] is True
    starved = dict(split)
    starved["holdout"] = [pair for pair in split["holdout"]
                          if pair[0]["label"] == "pass"][:30] + \
                         [pair for pair in split["holdout"]
                          if pair[0]["label"] == "fail"][:5]
    power = M29.check_power(manifest, starved, undecided)
    assert power["met_by_split"]["holdout"] is False
    assert power["increment_test_adequately_powered"] is False


def test_paired_delta_bootstrap_zero_for_identical_and_positive_for_better():
    actual = ["fail", "pass"] * 20
    same = list(actual)
    delta = M29.paired_delta_bootstrap(actual, same, same, "t:same")
    assert delta["delta_accuracy"] == 0.0
    assert delta["delta_accuracy_bootstrap_95pct"] == [0.0, 0.0]
    worse = ["pass"] * 40
    delta = M29.paired_delta_bootstrap(actual, same, worse, "t:better")
    assert delta["delta_accuracy"] == 0.5
    lo, hi = delta["delta_accuracy_bootstrap_95pct"]
    assert lo > 0 and hi >= lo
    counts = delta["prediction_agreement_counts"]
    assert sum(counts.values()) == 40


def test_evaluate_reports_seven_baselines_increment_and_calibration(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M29.load_dataset(manifest, labels_path, telemetry_path)
    report = M29.evaluate(manifest, split, undecided)
    assert report["baseline_order"] == manifest["baseline_order"]
    assert set(report["evaluations"]) == set(manifest["baseline_order"])
    assert report["evaluations"]["metadata_only"]["feature_count"] == 6
    assert report["evaluations"]["window_entropy"]["feature_count"] == 2
    assert report["evaluations"]["metadata_plus_telemetry"][
        "feature_count"] == 16
    # Metadata cannot decide mixed bands 3/5; informative telemetry can.
    assert (report["evaluations"]["metadata_plus_telemetry"]["accuracy"]
            > report["evaluations"]["metadata_only"]["accuracy"])
    increment = report["incremental_value_over_metadata"][
        "metadata_plus_telemetry_vs_metadata_only"]
    assert increment["delta_accuracy"] > 0
    assert increment["paired"] is True
    assert increment["interval_excludes_zero"] is True
    assert increment["meaningful_increment_established"] is True
    for name in M29.CALIBRATED_MODELS:
        block = report["calibration"][name]
        bins = block["reliability_bins_equal_count"]
        assert len(bins) == 8 and sum(b["n"] for b in bins) == 96
        assert 0.0 <= block["expected_calibration_error"] <= 1.0
        threshold = block["candidate_threshold"]
        assert threshold["status"] == "candidate-only"
        assert threshold["derived_from"].startswith("validation split")
    assert report["production_threshold_set"] is False


def test_uninformative_telemetry_reports_no_established_increment(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(
        tmp_path, telemetry_informative=False)
    split, undecided = M29.load_dataset(manifest, labels_path, telemetry_path)
    report = M29.evaluate(manifest, split, undecided)
    increment = report["incremental_value_over_metadata"][
        "metadata_plus_telemetry_vs_metadata_only"]
    assert increment["meaningful_increment_established"] is False


def test_public_reports_have_no_ids_text_or_paths(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M29.load_dataset(manifest, labels_path, telemetry_path)
    report = M29.evaluate(manifest, split, undecided)
    public = json.dumps(report)
    assert "m29_b" not in public and "What is" not in public
    assert "candidate-only" in public
    assert not ({"task_id", "prompt", "expression", "known_answer",
                 "generated_output", "model_path", "predictions"}
                & set(_walk(report)))
    assert report["per_task_predictions_persisted_publicly"] is False
