#!/usr/bin/env python3
"""M24 frozen holdout tests are CPU-only and inspect no real M24 telemetry."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import m24_frozen_holdout as M24  # noqa: E402

CLASSES = ["checker_needed", "no_action", "retrieval_needed", "review_needed"]


def _record(task_id, values):
    entropy, probability, margin, router_entropy, concentration = values
    return {
        "task_id": task_id,
        "logits": {
            "window": {"mean_entropy": entropy},
            "selected_token_probability": probability,
            "top_k_margin": margin,
        },
        "router": {
            "router_entropy_mean": router_entropy,
            "expert_concentration_mean": concentration,
        },
        "capture_status": "completed",
        "decode_step_count": 10,
    }


def _training_and_holdout():
    centers = {
        "checker_needed": (0.1, 0.9, 0.8, 3.8, 0.08),
        "no_action": (0.3, 0.95, 0.9, 3.65, 0.12),
        "retrieval_needed": (0.25, 0.92, 0.87, 3.45, 0.16),
        "review_needed": (0.24, 0.93, 0.89, 3.50, 0.15),
    }
    train_records, train_actions = [], []
    holdout_records, holdout_actions = [], []
    for class_i, label in enumerate(CLASSES):
        for i in range(8):
            task_id = f"train-{class_i}-{i}"
            offset = (i - 3.5) * 0.0001
            values = tuple(value + offset for value in centers[label])
            train_records.append(_record(task_id, values))
            train_actions.append({"task_id": task_id, "action_type": label})
        for i in range(10):
            task_id = f"holdout-{class_i}-{i}"
            holdout_records.append(_record(task_id, centers[label]))
            holdout_actions.append({"task_id": task_id, "action_type": label})
    return train_records, train_actions, holdout_records, holdout_actions


def _walk(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def test_corrected_manifest_is_balanced_resolved_and_training_disjoint(tmp_path):
    manifest, mapping = M24.load_manifest(
        ROOT / "data/prompts/m24_holdout_manifest.json")
    assert manifest["n_tasks"] == 40 and len(mapping) == 40
    assert all(list(mapping.values()).count(group) == 10
               for group in set(mapping.values()))
    selected = M24.prepare_selected_batch(
        ROOT / "data/prompts/m24_holdout_manifest.json",
        ROOT / "data/prompts/agents_a1_m19_batch.jsonl",
        ROOT / "data/prompts/m23_manifest.json", tmp_path / "private.jsonl")
    assert len(selected) == 40
    m23 = json.loads((ROOT / "data/prompts/m23_manifest.json").read_text())
    training_ids = {x for group in m23["groups"] for x in group["task_ids"]}
    assert not training_ids & {row["prompt_id"] for row in selected}


def test_frozen_classifiers_fit_only_balanced_m23_and_predict_holdout():
    train, train_actions, holdout, holdout_actions = _training_and_holdout()
    classifiers = M24.fit_frozen_classifiers(train, train_actions)
    assert set(classifiers) == {"full", "logits_only", "router_only"}
    assert all(model.training_count == 32 for model in classifiers.values())
    _, evaluations = M24.evaluate_classifiers(
        classifiers, holdout, holdout_actions)
    assert evaluations["full"]["accuracy"] == 1.0
    assert evaluations["full"]["balanced_accuracy"] == 1.0
    assert evaluations["full"]["macro_f1"] == 1.0
    assert evaluations["router_only"]["feature_count"] == 2


def test_lexical_tie_break_is_frozen():
    classifier = M24.FrozenNearestCentroid(
        ["decode_window_entropy"], [0.0], [1.0],
        {"z_class": [1.0], "a_class": [-1.0]}, 2)
    record = _record("x", (0.0, 0.5, 0.5, 1.0, 0.5))
    assert classifier.predict(record) == "a_class"


def test_metrics_include_confusion_per_class_and_fixed_bootstrap():
    actual = CLASSES * 10
    predicted = list(actual)
    first = M24.classification_metrics(actual, predicted, sorted(CLASSES))
    second = M24.classification_metrics(actual, predicted, sorted(CLASSES))
    assert first == second
    assert first["accuracy"] == first["balanced_accuracy"] == 1.0
    assert first["accuracy_bootstrap_95pct"] == [1.0, 1.0]
    assert all(first["confusion_matrix"][label][label] == 10 for label in CLASSES)
    assert all(first["per_class"][label]["support"] == 10 for label in CLASSES)


def test_public_evaluation_is_aggregate_and_has_no_task_ids_or_centroids():
    train, train_actions, holdout, holdout_actions = _training_and_holdout()
    classifiers = M24.fit_frozen_classifiers(train, train_actions)
    manifest = json.loads((ROOT / "data/prompts/m24_holdout_manifest.json").read_text())
    report = M24.build_evaluation_report(
        classifiers, train, train_actions, holdout, holdout_actions, manifest)
    assert report["majority_class_baseline_accuracy"] == 0.25
    assert report["centroids_updated_from_holdout"] is False
    assert report["features_or_thresholds_tuned_on_holdout"] is False
    public = json.dumps(report)
    assert "train-" not in public and "holdout-" not in public
    assert "centroids" not in report
    assert not ({"task_id", "prompt", "output", "generated_output",
                 "model_path", "router_logits"} & set(_walk(report)))
