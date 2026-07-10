#!/usr/bin/env python3
"""M24 frozen M23-trained nearest-centroid holdout evaluation."""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import action_executor as EXEC  # noqa: E402
from hf_telemetry_backend import HFTelemetryBackend  # noqa: E402
import m23_within_model as M23  # noqa: E402
from verifiers import evidence_hash  # noqa: E402


EXPECTED_FEATURE_SETS = {
    "full": ["decode_window_entropy", "final_selected_probability",
             "final_top_k_margin", "router_entropy", "expert_concentration"],
    "logits_only": ["decode_window_entropy", "final_selected_probability",
                    "final_top_k_margin"],
    "router_only": ["router_entropy", "expert_concentration"],
}


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != \
            "corrected_and_frozen_before_m24_holdout_telemetry_run":
        raise ValueError("M24 manifest is not corrected/frozen before capture")
    groups = manifest.get("groups") or []
    if manifest.get("n_tasks") != 40 or len(groups) != 4:
        raise ValueError("M24 manifest must contain four groups and 40 tasks")
    mapping = {}
    for group in groups:
        if len(group.get("task_ids") or []) != 10:
            raise ValueError("each M24 group must contain ten task ids")
        for task_id in group["task_ids"]:
            if task_id in mapping:
                raise ValueError(f"duplicate M24 task id: {task_id}")
            mapping[task_id] = group["group"]
    if manifest.get("frozen_feature_sets") != EXPECTED_FEATURE_SETS:
        raise ValueError("M24 feature sets differ from frozen protocol")
    return manifest, mapping


def prepare_selected_batch(manifest_path, source_path, training_manifest_path,
                           output_path):
    manifest, groups = load_manifest(manifest_path)
    training, training_groups = M23.load_manifest(training_manifest_path)
    del training
    overlap = set(groups) & set(training_groups)
    if overlap:
        raise ValueError(f"M24 holdout overlaps M23 training ids: {sorted(overlap)}")
    by_id = {row["prompt_id"]: row for row in M23.read_jsonl(source_path)}
    ordered = [task_id for group in manifest["groups"]
               for task_id in group["task_ids"]]
    missing = [task_id for task_id in ordered if task_id not in by_id]
    if missing:
        raise ValueError(f"M24 source missing ids: {missing}")
    selected = []
    for task_id in ordered:
        row = dict(by_id[task_id])
        row["m24_predeclared_group"] = groups[task_id]
        selected.append(row)
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(row) + "\n" for row in selected))
    return selected


def feature_vector(record, features):
    values = []
    for feature in features:
        value = M23.METRICS[feature](record)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(f"missing/non-finite frozen feature: {feature}")
        values.append(float(value))
    return values


class FrozenNearestCentroid:
    """M23-standardized Euclidean centroid classifier with lexical tie breaks."""

    def __init__(self, features, means, scales, centroids, training_count):
        self.features = tuple(features)
        self.means = tuple(means)
        self.scales = tuple(scales)
        self.centroids = {key: tuple(value) for key, value in centroids.items()}
        self.training_count = int(training_count)

    @classmethod
    def fit(cls, records, labels, features):
        if len(records) != len(labels) or not records:
            raise ValueError("training records/labels must be non-empty and aligned")
        raw = [feature_vector(record, features) for record in records]
        columns = list(zip(*raw))
        means = [statistics.fmean(column) for column in columns]
        scales = []
        for column in columns:
            scale = statistics.stdev(column) if len(column) >= 2 else 0.0
            scales.append(scale if scale > 0 else 1.0)
        standardized = [
            [(value - mean) / scale
             for value, mean, scale in zip(row, means, scales)]
            for row in raw]
        classes = sorted(set(labels))
        centroids = {}
        for label in classes:
            rows = [row for row, y in zip(standardized, labels) if y == label]
            if not rows:
                raise ValueError(f"empty training class: {label}")
            centroids[label] = [statistics.fmean(column)
                                for column in zip(*rows)]
        return cls(features, means, scales, centroids, len(records))

    def predict(self, record):
        raw = feature_vector(record, self.features)
        row = [(value - mean) / scale
               for value, mean, scale in zip(raw, self.means, self.scales)]
        candidates = []
        for label, centroid in self.centroids.items():
            distance = sum((value - center) ** 2
                           for value, center in zip(row, centroid))
            candidates.append((distance, label))
        return min(candidates)[1]


def fit_frozen_classifiers(training_records, training_actions, feature_sets=None):
    feature_sets = feature_sets or EXPECTED_FEATURE_SETS
    actions = {row["task_id"]: row["action_type"] for row in training_actions}
    labels = [actions[row["task_id"]] for row in training_records]
    if len(training_records) != 32:
        raise ValueError("M24 classifier must train on exactly 32 M23 records")
    if Counter(labels) != Counter({
            "checker_needed": 8, "retrieval_needed": 8,
            "review_needed": 8, "no_action": 8}):
        raise ValueError("M23 training action classes are not frozen balanced 8/8/8/8")
    return {name: FrozenNearestCentroid.fit(training_records, labels, features)
            for name, features in feature_sets.items()}


def _bootstrap_accuracy(actual, predicted, seed, iterations=2000):
    rng = random.Random(seed)
    n = len(actual)
    samples = []
    for _ in range(iterations):
        indices = [rng.randrange(n) for _ in range(n)]
        samples.append(sum(actual[i] == predicted[i] for i in indices) / n)
    samples.sort()
    return [samples[int(0.025 * (iterations - 1))],
            samples[int(0.975 * (iterations - 1))]]


def classification_metrics(actual, predicted, classes):
    if len(actual) != len(predicted) or not actual:
        raise ValueError("holdout labels/predictions must be non-empty and aligned")
    classes = list(classes)
    confusion = {true: {pred: 0 for pred in classes} for true in classes}
    for true, pred in zip(actual, predicted):
        confusion[true][pred] += 1
    per_class = {}
    for label in classes:
        tp = confusion[label][label]
        support = sum(confusion[label].values())
        predicted_count = sum(confusion[true][label] for true in classes)
        precision = tp / predicted_count if predicted_count else 0.0
        recall = tp / support if support else 0.0
        f1 = (2 * precision * recall / (precision + recall)
              if precision + recall else 0.0)
        per_class[label] = {
            "precision": precision, "recall": recall, "f1": f1,
            "support": support,
        }
    accuracy = sum(a == p for a, p in zip(actual, predicted)) / len(actual)
    return {
        "n": len(actual),
        "accuracy": accuracy,
        "balanced_accuracy": statistics.fmean(
            row["recall"] for row in per_class.values()),
        "macro_f1": statistics.fmean(row["f1"] for row in per_class.values()),
        "accuracy_bootstrap_95pct": _bootstrap_accuracy(
            actual, predicted, "m24:frozen:accuracy"),
        "bootstrap_iterations": 2000,
        "confusion_matrix": confusion,
        "per_class": per_class,
    }


def evaluate_classifiers(classifiers, holdout_records, holdout_actions):
    labels = {row["task_id"]: row["action_type"] for row in holdout_actions}
    actual = [labels[row["task_id"]] for row in holdout_records]
    classes = sorted(set(actual))
    evaluations = {}
    for name, classifier in sorted(classifiers.items()):
        predicted = [classifier.predict(record) for record in holdout_records]
        metrics = classification_metrics(actual, predicted, classes)
        metrics["feature_count"] = len(classifier.features)
        metrics["features"] = list(classifier.features)
        evaluations[name] = metrics
    return actual, evaluations


def build_run_summary(telemetry, runtimes, actions, results, tasks):
    capped = [task for task, record in zip(tasks, telemetry)
              if record["decode_step_count"] == 64]
    return {
        "schema_version": 1,
        "run_kind": "m24_frozen_holdout_same_run",
        "within_model_alignment": True,
        "training_milestone": "M23",
        "holdout_milestone": "M24",
        "training_records": 32,
        "holdout_records": len(telemetry),
        "architecture_family": "qwen2_moe",
        "hardware_plan": "two_24gib_nvidia_gpus_bf16",
        "hidden_capture": "disabled",
        "predeclared_group_distribution": dict(sorted(Counter(
            task["m24_predeclared_group"] for task in tasks).items())),
        "capture_status_distribution": dict(sorted(Counter(
            row["capture_status"] for row in telemetry).items())),
        "logits_status_distribution": dict(sorted(Counter(
            row["logits"]["status"] for row in telemetry).items())),
        "router_status_distribution": dict(sorted(Counter(
            row["router"]["status"] for row in telemetry).items())),
        "actual_action_type_distribution": dict(sorted(Counter(
            row["action_type"] for row in actions).items())),
        "checker_verdict_distribution": dict(sorted(Counter(
            row["checker_verdict"] for row in results
            if row.get("checker_verdict") is not None).items())),
        "decode_cap_tokens": 64,
        "decode_cap_reached_count": len(capped),
        "decode_cap_reached_group_distribution": dict(sorted(Counter(
            task["m24_predeclared_group"] for task in capped).items())),
        "same_capture_supplied_telemetry_and_output": True,
        "captured_output_passed_transiently_to_verifiers": True,
        "per_task_predictions_persisted_publicly": False,
        "raw_text_token_tensor_or_path_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only frozen holdout summary",
    }


def build_evaluation_report(classifiers, training_records, training_actions,
                            holdout_records, holdout_actions, manifest):
    actual, evaluations = evaluate_classifiers(
        classifiers, holdout_records, holdout_actions)
    distribution = Counter(actual)
    majority = max(distribution.values()) / len(actual)
    training_ids = sorted(row["task_id"] for row in training_records)
    training_labels = {row["task_id"]: row["action_type"]
                       for row in training_actions}
    return {
        "schema_version": 1,
        "run_kind": "m24_frozen_telemetry_holdout_evaluation",
        "training_records": len(training_records),
        "holdout_records": len(holdout_records),
        "class_order": sorted(distribution),
        "holdout_class_distribution": dict(sorted(distribution.items())),
        "majority_class_baseline_accuracy": majority,
        "classifier_family": "m23_standardized_nearest_centroid",
        "distance": "squared_euclidean",
        "tie_break": "lexicographic",
        "training_protocol_hash": evidence_hash(
            *training_ids, *[training_labels[x] for x in training_ids],
            json.dumps(EXPECTED_FEATURE_SETS, sort_keys=True)),
        "holdout_manifest_hash": evidence_hash(
            json.dumps(manifest, sort_keys=True)),
        "evaluations": evaluations,
        "centroids_updated_from_holdout": False,
        "features_or_thresholds_tuned_on_holdout": False,
        "per_task_predictions_persisted_publicly": False,
        "predictive_value_interpretation": "frozen holdout task-demand classification only",
        "causal_or_production_claim": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate metrics/confusion only; no ids/text/paths/tensors",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m24_holdout_manifest.json")
    ap.add_argument("--training-manifest", default="data/prompts/m23_manifest.json")
    ap.add_argument("--source-prompts", default="data/prompts/agents_a1_m19_batch.jsonl")
    ap.add_argument("--selected-prompts-out",
                    default="reports/shadow/private/m24_hf_prompts_local.jsonl")
    ap.add_argument("--captures", default="data/captures/m24_qwen15_moe")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--training-telemetry",
                    default="reports/shadow/private/m23_hf_telemetry_records_local.jsonl")
    ap.add_argument("--training-actions",
                    default="reports/shadow/private/m23_qwen_actions_local.jsonl")
    ap.add_argument("--telemetry-out",
                    default="reports/shadow/private/m24_hf_telemetry_records_local.jsonl")
    ap.add_argument("--runtime-out",
                    default="reports/shadow/private/m24_qwen_auto_outcomes_local.jsonl")
    ap.add_argument("--actions-out",
                    default="reports/shadow/private/m24_qwen_actions_local.jsonl")
    ap.add_argument("--results-out",
                    default="reports/shadow/private/m24_qwen_action_results_local.jsonl")
    ap.add_argument("--summary-out", default="reports/telemetry/hf_m24_holdout_summary.json")
    ap.add_argument("--evaluation-out", default="reports/telemetry/hf_m24_frozen_evaluation.json")
    args = ap.parse_args(argv)

    manifest, _ = load_manifest(args.manifest)
    tasks = prepare_selected_batch(
        args.manifest, args.source_prompts, args.training_manifest,
        args.selected_prompts_out)
    if args.prepare_only:
        completion = M23.capture_completion(args.captures, tasks)
        print(f"[jlens] M24 frozen prompts: {len(tasks)}; "
              f"existing={len(completion['complete'])}, "
              f"pending={len(completion['missing_or_invalid'])}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required for M24 real capture processing")

    # Freeze M23-only classifiers before loading any M24 capture.
    training_records = M23.read_jsonl(args.training_telemetry)
    training_actions = M23.read_jsonl(args.training_actions)
    classifiers = fit_frozen_classifiers(
        training_records, training_actions, manifest["frozen_feature_sets"])

    import torch
    from jsonschema import Draft7Validator
    schemas = {
        "telemetry": Draft7Validator(json.loads(Path(
            "schema/hf_telemetry_record_v1.json").read_text())),
        "runtime": Draft7Validator(json.loads(Path(
            "schema/auto_outcome_v1.json").read_text())),
        "action": Draft7Validator(json.loads(Path(
            "schema/action_record_v1.json").read_text())),
        "result": Draft7Validator(json.loads(Path(
            "schema/action_result_v1.json").read_text())),
    }
    backend = HFTelemetryBackend(
        model_ref=args.model_ref, source_kind="local_path", top_k=5)
    adapter = EXEC.FixtureRetrievalAdapter({
        "*": {"source_kind": "public_fixture",
              "context": "M24 controlled local fixture context",
              "confidence": 0.8}
    })
    cfg = M23._qwen_config()
    telemetry, runtimes, actions, results = [], [], [], []
    for task in tasks:
        path = Path(args.captures) / f"{task['prompt_id']}.pt"
        if not path.exists():
            raise FileNotFoundError(f"missing M24 capture: {task['prompt_id']}")
        capture = torch.load(path, map_location="cpu", weights_only=False)
        rows = M23.process_same_capture(
            task, capture, backend, cfg=cfg, retrieval_adapter=adapter)
        for kind, row in zip(("telemetry", "runtime", "action", "result"), rows):
            errors = list(schemas[kind].iter_errors(row))
            if errors:
                raise ValueError(
                    f"invalid {kind} for {task['prompt_id']}: {errors[0].message}")
        t, runtime, action, result = rows
        telemetry.append(t); runtimes.append(runtime)
        actions.append(action); results.append(result)

    M23.write_jsonl(args.telemetry_out, telemetry)
    M23.write_jsonl(args.runtime_out, runtimes)
    M23.write_jsonl(args.actions_out, actions)
    M23.write_jsonl(args.results_out, results)
    summary = build_run_summary(telemetry, runtimes, actions, results, tasks)
    evaluation = build_evaluation_report(
        classifiers, training_records, training_actions,
        telemetry, actions, manifest)
    for path, payload in ((args.summary_out, summary),
                          (args.evaluation_out, evaluation)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M24: {len(telemetry)} frozen holdout records evaluated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
