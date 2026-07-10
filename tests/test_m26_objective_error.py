#!/usr/bin/env python3
"""M26 objective error dataset tests are CPU-only and no-network."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m26_objective_error as M26  # noqa: E402

MANIFEST = ROOT / "data/prompts/m26_error_manifest.json"


def _telemetry(task_id, *, entropy=1.0, prob=0.8, margin=0.5,
               router_entropy=3.0, concentration=0.2, steps=8, shift=0.1):
    return {
        "task_id": task_id,
        "capture_status": "completed",
        "decode_step_count": steps,
        "logits": {
            "status": "available",
            "selected_token_probability": prob,
            "top_k_margin": margin,
            "window": {"step_count": steps, "mean_entropy": entropy,
                       "high_entropy_count": 1, "low_confidence_count": 0,
                       "top_k_margin_trend": 0.05},
        },
        "router": {
            "status": "available",
            "router_entropy_mean": router_entropy,
            "expert_concentration_mean": concentration,
            "windowed_expert_shift": shift,
        },
    }


def _fixture_dataset():
    manifest = M26.load_manifest(MANIFEST)
    tasks = M26.generate_tasks(manifest)
    telemetry, actions, labels = [], [], []
    for index, task in enumerate(tasks):
        # Deterministic synthetic outcome: hard bands fail, easy bands pass,
        # plus two undecided rows inside the train split.
        if task["prompt_id"] in ("m26_a_002", "m26_b_002"):
            label = "undecided"
        elif task["m26_band"] in ("band_c", "band_d"):
            label = "fail"
        else:
            label = "pass"
        entropy = 2.0 if label == "fail" else 0.5
        telemetry.append(_telemetry(task["prompt_id"], entropy=entropy,
                                    steps=8 + (index % 3)))
        actions.append({"task_id": task["prompt_id"],
                        "action_type": "checker_needed"})
        labels.append({"task_id": task["prompt_id"], "band": task["m26_band"],
                       "split": task["m26_split"], "label": label})
    return manifest, tasks, telemetry, actions, labels


def _walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_generation_is_deterministic_predeclared_and_in_band():
    manifest = M26.load_manifest(MANIFEST)
    tasks = M26.generate_tasks(manifest)
    again = M26.generate_tasks(manifest)
    assert tasks == again
    assert len(tasks) == 96
    assert len({task["prompt_id"] for task in tasks}) == 96
    bands = {band["band_id"]: band for band in manifest["bands"]}
    split_counts = {}
    for task in tasks:
        band = bands[task["m26_band"]]
        a, op_b = task["expression"].split(band["operator"], 1)
        a, b = int(a), int(op_b)
        assert band["operand_a_range"][0] <= a <= band["operand_a_range"][1]
        assert band["operand_b_range"][0] <= b <= band["operand_b_range"][1]
        expected = a + b if band["operator"] == "+" else a * b
        assert task["known_answer"] == str(expected)
        assert task["prompt"] == manifest["prompt_template"].format(
            a=a, op=band["operator"], b=b)
        assert task["task_category"] == "math"
        key = (task["m26_band"], task["m26_split"])
        split_counts[key] = split_counts.get(key, 0) + 1
    for band_id in bands:
        assert split_counts[(band_id, "train")] == 16
        assert split_counts[(band_id, "holdout")] == 8


def test_operand_tuples_are_unique_within_band():
    manifest = M26.load_manifest(MANIFEST)
    tasks = M26.generate_tasks(manifest)
    seen = {}
    for task in tasks:
        seen.setdefault(task["m26_band"], set()).add(task["expression"])
    for band_id, expressions in seen.items():
        assert len(expressions) == 24, band_id


def test_label_rule_maps_checker_verdicts_only():
    assert M26.label_from_result({"checker_verdict": "pass"}) == "pass"
    assert M26.label_from_result({"checker_verdict": "fail"}) == "fail"
    assert M26.label_from_result({"checker_verdict": None}) == "undecided"
    assert M26.label_from_result({}) == "undecided"


def test_run_summary_seals_holdout_and_checks_minimum():
    manifest, tasks, telemetry, actions, labels = _fixture_dataset()
    summary = M26.build_run_summary(manifest, tasks, telemetry, actions, labels)
    assert summary["holdout_label_distribution"] == "sealed_until_m27"
    assert summary["holdout_telemetry_aggregates"] == "sealed_until_m27"
    assert summary["train_label_distribution"] == {
        "fail": 32, "pass": 30, "undecided": 2}
    assert summary["actual_action_type_distribution"] == {"checker_needed": 96}
    assert summary["minimum_modeling_requirement_met"] is True
    assert summary["train_decode_cap_reached_count"] == 0


def test_run_summary_reports_shortfall_honestly():
    manifest, tasks, telemetry, actions, labels = _fixture_dataset()
    flipped = [dict(row, label="pass" if row["label"] == "fail" else row["label"])
               for row in labels]
    summary = M26.build_run_summary(manifest, tasks, telemetry, actions, flipped)
    assert summary["minimum_modeling_requirement_met"] is False


def test_telemetry_summary_is_train_only_with_descriptive_effects():
    manifest, tasks, telemetry, actions, labels = _fixture_dataset()
    del manifest, actions
    report = M26.build_telemetry_summary(tasks, telemetry, labels)
    assert report["split_scope"] == "train_only"
    assert report["n_train_records"] == 64
    assert report["train_label_distribution"] == {
        "fail": 32, "pass": 30, "undecided": 2}
    comparison = report["train_fail_vs_pass"]
    assert comparison["fail"]["n"] == 32 and comparison["pass"]["n"] == 30
    entropy_effect = comparison["effects"]["decode_window_entropy"]
    assert entropy_effect["status"] == "descriptive_only"
    assert entropy_effect["mean_difference_fail_minus_pass"] > 0
    assert report["predictive_value_claimed"] is False


def test_public_reports_have_no_ids_text_expressions_or_paths():
    manifest, tasks, telemetry, actions, labels = _fixture_dataset()
    summary = M26.build_run_summary(manifest, tasks, telemetry, actions, labels)
    report = M26.build_telemetry_summary(tasks, telemetry, labels)
    for payload in (summary, report):
        public = json.dumps(payload)
        assert "m26_a_" not in public and "m26_d_" not in public
        assert "What is" not in public
        assert not ({"task_id", "prompt", "expression", "known_answer",
                     "generated_output", "model_path", "router_logits", "label"}
                    & set(_walk(payload)))
