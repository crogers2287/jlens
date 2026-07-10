#!/usr/bin/env python3
"""M25 identical-input falsification tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m24_frozen_holdout as M24  # noqa: E402
import m25_identical_input as M25  # noqa: E402


def _telemetry(task_id, router_entropy, concentration):
    return {
        "task_id": task_id,
        "capture_status": "completed",
        "decode_step_count": 10,
        "logits": {"status": "available"},
        "router": {
            "status": "available",
            "router_entropy_mean": router_entropy,
            "expert_concentration_mean": concentration,
        },
    }


def _classifier():
    return M24.FrozenNearestCentroid(
        ["router_entropy", "expert_concentration"],
        [0.0, 0.0], [1.0, 1.0], {
            "checker_needed": [1.0, 0.0],
            "no_action": [-1.0, 0.0],
            "retrieval_needed": [0.0, 1.0],
            "review_needed": [0.0, -1.0],
        }, 32)


def _fixture_rows(tmp_path):
    tasks = M25.prepare_private_tasks(
        ROOT / "data/prompts/m25_pair_manifest.json", tmp_path / "tasks.jsonl")
    captures, telemetry, actions = [], [], []
    for task in tasks:
        is_math = task["m25_pair_type"] == "checker_vs_no_action"
        features = (1.0, 0.0) if is_math else (0.0, 1.0)
        telemetry.append(_telemetry(task["prompt_id"], *features))
        captures.append({"prompt_id": task["prompt_id"],
                         "generated_output": f"same-{task['m25_pair_id']}"})
        actions.append({"task_id": task["prompt_id"],
                        "action_type": task["m25_intended_action"]})
    return tasks, captures, telemetry, actions


def _walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_manifest_and_private_generator_have_16_byte_equal_prompt_pairs(tmp_path):
    manifest = M25.load_manifest(ROOT / "data/prompts/m25_pair_manifest.json")
    assert manifest["n_pairs"] == 16 and manifest["n_tasks"] == 32
    tasks = M25.prepare_private_tasks(
        ROOT / "data/prompts/m25_pair_manifest.json", tmp_path / "tasks.jsonl")
    pairs = {}
    for task in tasks:
        pairs.setdefault(task["m25_pair_id"], []).append(task)
    assert len(pairs) == 16
    for rows in pairs.values():
        assert rows[0]["prompt"] == rows[1]["prompt"]
        assert rows[0]["task_category"] != rows[1]["task_category"]
        assert rows[0]["m25_intended_action"] != rows[1]["m25_intended_action"]


def test_identical_telemetry_yields_identical_predictions_and_half_ceiling(tmp_path):
    tasks, captures, telemetry, actions = _fixture_rows(tmp_path)
    report = M25.evaluate_pairs(
        tasks, captures, telemetry, actions, _classifier())
    assert report["actual_class_distribution"] == {
        "checker_needed": 8, "no_action": 8,
        "retrieval_needed": 8, "review_needed": 8}
    assert report["intended_action_match_count"] == 32
    assert report["overall_pair_checks"]["actual_labels_discordant"] == 16
    assert report["overall_pair_checks"]["outputs_identical"] == 16
    assert report["overall_pair_checks"]["predictions_identical"] == 16
    assert report["overall_pair_checks"]["prediction_divergence_rate"] == 0.0
    assert report["frozen_router_classifier_metrics"]["accuracy"] == 0.5
    assert report["majority_class_baseline_accuracy"] == 0.25


def test_pair_feature_differences_are_aggregate_and_exact_zero(tmp_path):
    tasks, captures, telemetry, actions = _fixture_rows(tmp_path)
    report = M25.evaluate_pairs(
        tasks, captures, telemetry, actions, _classifier())
    checks = report["overall_pair_checks"]
    assert checks["router_entropy_abs_diff_mean"] == 0.0
    assert checks["router_entropy_abs_diff_max"] == 0.0
    assert checks["expert_concentration_abs_diff_mean"] == 0.0
    assert checks["expert_concentration_abs_diff_max"] == 0.0


def test_output_mismatch_is_reported_without_changing_pair(tmp_path):
    tasks, captures, telemetry, actions = _fixture_rows(tmp_path)
    captures[1]["generated_output"] = "different"
    report = M25.evaluate_pairs(
        tasks, captures, telemetry, actions, _classifier())
    assert report["overall_pair_checks"]["outputs_identical"] == 15
    assert report["overall_pair_checks"]["n_pairs"] == 16


def test_public_pair_report_has_no_ids_text_predictions_or_paths(tmp_path):
    tasks, captures, telemetry, actions = _fixture_rows(tmp_path)
    report = M25.evaluate_pairs(
        tasks, captures, telemetry, actions, _classifier())
    public = json.dumps(report)
    assert "m25_math_" not in public and "m25_topic_" not in public
    assert "same-math" not in public and "same-topic" not in public
    assert not ({"task_id", "pair_id", "prompt", "output", "generated_output",
                 "prediction", "model_path", "router_logits"}
                & set(_walk(report)))
    assert report["classifier_refit_or_holdout_update"] is False
