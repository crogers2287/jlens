#!/usr/bin/env python3
"""M30 decisive increment tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m23_within_model as M23  # noqa: E402
import m29_scaled_error_power as M29  # noqa: E402
import m30_decisive_increment as M30  # noqa: E402
from test_m29_scaled_error_power import _telemetry  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m30_decisive_manifest.json"
M29_MANIFEST_PATH = ROOT / "data/prompts/m29_power_manifest.json"


def _label_for(task, index):
    if task["band"] in ("band_1", "band_2"):
        return "pass"
    if task["band"] in ("band_4", "band_6"):
        return "fail"
    return "fail" if index % 2 == 0 else "pass"


def _synthetic_files(tmp_path, *, telemetry_informative=True):
    manifest = M30.load_manifest(MANIFEST_PATH)
    labels, telemetry = [], []
    for index, task in enumerate(manifest["tasks"]):
        label = _label_for(task, index)
        if task["task_id"] == "m30_b1_002":
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


def test_generation_is_deterministic_sealed_and_disjoint_from_m29():
    manifest = M30.load_manifest(MANIFEST_PATH)
    tasks = M30.generate_tasks(manifest, M29_MANIFEST_PATH)
    assert tasks == M30.generate_tasks(manifest, M29_MANIFEST_PATH)
    assert len(tasks) == 768
    prior = M30.m29_tuples_by_band(M29_MANIFEST_PATH)
    bands = {band["band_id"]: band for band in manifest["bands"]}
    counts = {}
    expressions = {}
    for task in tasks:
        band = bands[task["m30_band"]]
        a, b = task["expression"].split(band["operator"], 1)
        a, b = int(a), int(b)
        assert band["operand_a_range"][0] <= a <= band["operand_a_range"][1]
        assert band["operand_b_range"][0] <= b <= band["operand_b_range"][1]
        assert (a, b) not in prior[task["m30_band"]]
        assert task["known_answer"] == str(a * b)
        key = (task["m30_band"], task["m30_split"])
        counts[key] = counts.get(key, 0) + 1
        expressions.setdefault(task["m30_band"], set()).add(task["expression"])
    for band_id in bands:
        assert counts[(band_id, "train")] == 64
        assert counts[(band_id, "validation")] == 32
        assert counts[(band_id, "holdout")] == 32
        assert len(expressions[band_id]) == 128


def test_load_dataset_and_power_flags(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M30.load_dataset(manifest, labels_path, telemetry_path)
    assert len(split["train"]) == 383
    assert len(split["validation"]) == 192
    assert len(split["holdout"]) == 192
    assert undecided == {"train": 1}
    power = M29.check_power(manifest, split, undecided)
    assert power["increment_test_adequately_powered"] is True


def test_classification_rule_maps_all_three_outcomes():
    established = {"delta_accuracy_bootstrap_95pct": [0.01, 0.12]}
    negative = {"delta_accuracy_bootstrap_95pct": [-0.12, -0.01]}
    spanning = {"delta_accuracy_bootstrap_95pct": [-0.02, 0.10]}
    assert M30.classify_increment(established, True) == "established"
    assert M30.classify_increment(established, False) == "not_established"
    assert M30.classify_increment(negative, True) == "negative"
    assert M30.classify_increment(spanning, True) == "not_established"


def test_evaluate_reports_primary_verdict_and_all_baselines(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M30.load_dataset(manifest, labels_path, telemetry_path)
    report = M30.evaluate(manifest, split, undecided)
    assert set(report["evaluations"]) == set(manifest["baseline_order"])
    assert report["primary_comparison"] == ["full_telemetry", "metadata_only"]
    primary = report["incremental_value_over_metadata"][
        "full_telemetry_vs_metadata_only"]
    assert primary["delta_accuracy"] > 0
    assert report["primary_increment_classification"] == "established"
    for name in M30.CALIBRATED_MODELS:
        block = report["calibration"][name]
        bins = block["reliability_bins_equal_count"]
        assert len(bins) == 8 and sum(b["n"] for b in bins) == 192
        assert block["candidate_threshold"]["status"] == "candidate-only"
        assert block["candidate_threshold"]["derived_from"].startswith(
            "validation split")
    assert report["holdout_evaluated_once"] is True
    assert report["production_threshold_set"] is False


def test_uninformative_telemetry_is_not_established(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(
        tmp_path, telemetry_informative=False)
    split, undecided = M30.load_dataset(manifest, labels_path, telemetry_path)
    report = M30.evaluate(manifest, split, undecided)
    assert report["primary_increment_classification"] in (
        "not_established", "negative")


def test_public_report_has_no_ids_text_or_paths(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M30.load_dataset(manifest, labels_path, telemetry_path)
    report = M30.evaluate(manifest, split, undecided)
    public = json.dumps(report)
    assert "m30_b" not in public and "What is" not in public
    assert "candidate-only" in public
    assert not ({"task_id", "prompt", "expression", "known_answer",
                 "generated_output", "model_path", "predictions"}
                & set(_walk(report)))
