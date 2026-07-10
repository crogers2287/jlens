#!/usr/bin/env python3
"""M27 frozen error-holdout tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m23_within_model as M23  # noqa: E402
import m26_objective_error as M26  # noqa: E402
import m27_frozen_error_holdout as M27  # noqa: E402

MANIFEST_PATH = ROOT / "data/prompts/m26_error_manifest.json"


def _telemetry(task_id, *, entropy, prob, router_entropy):
    return {
        "task_id": task_id,
        "capture_status": "completed",
        "decode_step_count": 8,
        "logits": {
            "status": "available",
            "selected_token_probability": prob,
            "top_k_margin": prob / 2,
            "window": {"step_count": 8, "mean_entropy": entropy,
                       "high_entropy_count": 1 if entropy > 1 else 0,
                       "low_confidence_count": 0,
                       "top_k_margin_trend": 0.02},
        },
        "router": {
            "status": "available",
            "router_entropy_mean": router_entropy,
            "expert_concentration_mean": 1.0 / router_entropy,
            "windowed_expert_shift": 0.1,
        },
    }


def _synthetic_files(tmp_path, *, separable=True):
    manifest = M26.load_manifest(MANIFEST_PATH)
    labels, telemetry = [], []
    for index, task in enumerate(manifest["tasks"]):
        if task["band"] in ("band_c", "band_d"):
            label = "fail"
        else:
            label = "pass"
        if task["task_id"] == "m26_a_003":
            label = "undecided"
        is_fail = label == "fail"
        entropy = (2.0 if is_fail else 0.4) if separable else 1.0
        entropy += 0.01 * (index % 5)
        labels.append({"task_id": task["task_id"], "band": task["band"],
                       "split": task["split"], "label": label})
        telemetry.append(_telemetry(
            task["task_id"], entropy=entropy,
            prob=0.3 if is_fail and separable else 0.9,
            router_entropy=3.5 if is_fail and separable else 2.5))
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


def test_load_dataset_splits_and_excludes_undecided(tmp_path):
    _, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M27.load_dataset(labels_path, telemetry_path)
    assert len(split["train"]) == 63 and len(split["holdout"]) == 32
    assert undecided == {"train": 1}
    label_row, features = split["train"][0]
    assert set(M27.METADATA_FEATURES) <= set(features)
    assert set(M26.FEATURES) <= set(features)
    assert label_row["label"] in ("pass", "fail")


def test_all_six_baselines_evaluate_with_frozen_features(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M27.load_dataset(labels_path, telemetry_path)
    report = M27.evaluate(manifest, split, undecided)
    assert report["baseline_order"] == list(M27.BASELINE_ORDER)
    assert set(report["evaluations"]) == set(M27.BASELINE_ORDER)
    assert report["evaluations"]["majority_class"]["feature_count"] == 0
    assert report["evaluations"]["metadata_only"]["feature_count"] == 4
    assert report["evaluations"]["router_only"]["feature_count"] == 2
    assert report["evaluations"]["full_telemetry"]["feature_count"] == 10
    for name in M27.BASELINE_ORDER:
        metrics = report["evaluations"][name]
        assert metrics["n"] == 32
        lo, hi = metrics["accuracy_bootstrap_95pct"]
        assert 0.0 <= lo <= metrics["accuracy"] <= 1.0 and lo <= hi <= 1.0
    # Separable telemetry must beat the majority baseline on synthetic data.
    assert (report["evaluations"]["full_telemetry"]["accuracy"]
            > report["evaluations"]["majority_class"]["accuracy"])
    assert report["holdout_evaluated_once"] is True
    assert report["refit_or_threshold_tuning_after_holdout"] is False


def test_majority_baseline_is_constant_with_lexical_tie_break():
    baseline = M27.MajorityBaseline(["pass", "pass", "fail"])
    assert baseline.predict({}) == "pass"
    tied = M27.MajorityBaseline(["pass", "fail"])
    assert tied.predict({}) == "fail"


def test_evaluate_stops_when_train_minimum_unmet(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M27.load_dataset(labels_path, telemetry_path)
    starved = {"train": [pair for pair in split["train"]
                         if pair[0]["label"] == "pass"][:16]
               + [pair for pair in split["train"]
                  if pair[0]["label"] == "fail"][:7],
               "holdout": split["holdout"]}
    try:
        M27.evaluate(manifest, starved, undecided)
    except ValueError as error:
        assert "minimum" in str(error)
    else:
        raise AssertionError("expected predeclared minimum to stop evaluation")


def test_holdout_manifest_is_frozen_aggregate_metadata_only(tmp_path):
    manifest, _, _ = _synthetic_files(tmp_path)
    holdout = M27.build_holdout_manifest(manifest, MANIFEST_PATH)
    assert holdout["selection_status"] == "frozen_in_m26_manifest_before_capture"
    assert holdout["n_holdout_tasks"] == 32
    assert holdout["holdout_band_counts"] == {
        "band_a": 8, "band_b": 8, "band_c": 8, "band_d": 8}
    public = json.dumps(holdout)
    assert "What is" not in public and "expression" not in public
    assert holdout["no_refit_after_holdout_capture"] is True


def test_public_evaluation_has_no_predictions_text_or_paths(tmp_path):
    manifest, labels_path, telemetry_path = _synthetic_files(tmp_path)
    split, undecided = M27.load_dataset(labels_path, telemetry_path)
    report = M27.evaluate(manifest, split, undecided)
    public = json.dumps(report)
    assert "m26_a_" not in public and "m26_d_" not in public
    assert "What is" not in public
    assert not ({"task_id", "prompt", "expression", "known_answer",
                 "generated_output", "model_path", "predictions"}
                & set(_walk(report)))
    assert report["per_task_predictions_persisted_publicly"] is False
