#!/usr/bin/env python3
"""M27 frozen within-category error-prediction holdout evaluation."""
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
import m23_within_model as M23  # noqa: E402
import m26_objective_error as M26  # noqa: E402
from verifiers import evidence_hash  # noqa: E402

BASELINE_ORDER = ("majority_class", "metadata_only", "logits_only",
                  "router_only", "router_plus_logits", "full_telemetry")
METADATA_FEATURES = ("band_a", "band_b", "band_c", "band_d")


def feature_row(label_row, record):
    """Merge one-hot band metadata with telemetry features for one task."""
    row = {name: 1.0 if label_row["band"] == name else 0.0
           for name in METADATA_FEATURES}
    for name, getter in M26.FEATURES.items():
        value = getter(record)
        if value is None or not math.isfinite(float(value)):
            raise ValueError(
                f"missing/non-finite feature {name} for {label_row['task_id']}")
        row[name] = float(value)
    return row


class FrozenDictCentroid:
    """Train-standardized nearest centroid over named feature dictionaries."""

    def __init__(self, features, means, scales, centroids, training_count):
        self.features = tuple(features)
        self.means = tuple(means)
        self.scales = tuple(scales)
        self.centroids = {key: tuple(value) for key, value in centroids.items()}
        self.training_count = int(training_count)

    @classmethod
    def fit(cls, rows, labels, features):
        if len(rows) != len(labels) or not rows:
            raise ValueError("training rows/labels must be non-empty and aligned")
        raw = [[float(row[name]) for name in features] for row in rows]
        columns = list(zip(*raw))
        means = [statistics.fmean(column) for column in columns]
        scales = []
        for column in columns:
            scale = statistics.stdev(column) if len(column) >= 2 else 0.0
            scales.append(scale if scale > 0 else 1.0)
        standardized = [[(value - mean) / scale
                         for value, mean, scale in zip(row, means, scales)]
                        for row in raw]
        centroids = {}
        for label in sorted(set(labels)):
            members = [row for row, y in zip(standardized, labels) if y == label]
            if not members:
                raise ValueError(f"empty training class: {label}")
            centroids[label] = [statistics.fmean(column)
                                for column in zip(*members)]
        return cls(features, means, scales, centroids, len(rows))

    def predict(self, row):
        values = [(float(row[name]) - mean) / scale
                  for name, mean, scale in zip(self.features, self.means,
                                               self.scales)]
        candidates = []
        for label, centroid in self.centroids.items():
            distance = sum((value - center) ** 2
                           for value, center in zip(values, centroid))
            candidates.append((distance, label))
        return min(candidates)[1]


class MajorityBaseline:
    def __init__(self, labels):
        counts = Counter(labels)
        top = max(counts.values())
        self.label = min(label for label, count in counts.items()
                         if count == top)
        self.features = ()
        self.training_count = len(labels)

    def predict(self, _row):
        return self.label


def fit_frozen_baselines(manifest, train_rows, train_labels):
    feature_sets = manifest["frozen_feature_sets"]
    baselines = {"majority_class": MajorityBaseline(train_labels)}
    for name in BASELINE_ORDER[1:]:
        baselines[name] = FrozenDictCentroid.fit(
            train_rows, train_labels, feature_sets[name])
    return baselines


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


def classification_metrics(actual, predicted, classes, seed):
    if len(actual) != len(predicted) or not actual:
        raise ValueError("labels/predictions must be non-empty and aligned")
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
        per_class[label] = {"precision": precision, "recall": recall,
                            "f1": f1, "support": support}
    return {
        "n": len(actual),
        "accuracy": sum(a == p for a, p in zip(actual, predicted)) / len(actual),
        "balanced_accuracy": statistics.fmean(
            row["recall"] for row in per_class.values()),
        "macro_f1": statistics.fmean(row["f1"] for row in per_class.values()),
        "accuracy_bootstrap_95pct": _bootstrap_accuracy(actual, predicted, seed),
        "bootstrap_iterations": 2000,
        "confusion_matrix": confusion,
        "per_class": per_class,
    }


def load_dataset(labels_path, telemetry_path):
    labels = M23.read_jsonl(labels_path)
    telemetry = {row["task_id"]: row for row in M23.read_jsonl(telemetry_path)}
    if len(labels) != 96:
        raise ValueError("M27 requires the full 96-task M26 label file")
    missing = [row["task_id"] for row in labels
               if row["task_id"] not in telemetry]
    if missing:
        raise ValueError(f"M27 telemetry missing task ids: {len(missing)}")
    split = {"train": [], "holdout": []}
    undecided = Counter()
    for row in labels:
        if row["label"] == "undecided":
            undecided[row["split"]] += 1
            continue
        split[row["split"]].append(
            (row, feature_row(row, telemetry[row["task_id"]])))
    return split, dict(undecided)


def build_holdout_manifest(manifest, manifest_path):
    holdout = [task for task in manifest["tasks"] if task["split"] == "holdout"]
    return {
        "milestone": "M27",
        "schema_version": 1,
        "selection_status": "frozen_in_m26_manifest_before_capture",
        "source_manifest": str(manifest_path),
        "source_manifest_hash": evidence_hash(
            json.dumps(manifest, sort_keys=True)),
        "n_holdout_tasks": len(holdout),
        "holdout_band_counts": dict(sorted(Counter(
            task["band"] for task in holdout).items())),
        "holdout_task_ids": [task["task_id"] for task in holdout],
        "prompt_family_constant": True,
        "template_leakage_note": (
            "train and holdout share the single predeclared prompt template by "
            "design; operand tuples are unique so no task instance repeats; the "
            "metadata_only baseline quantifies the difficulty-band shortcut"),
        "no_refit_after_holdout_capture": True,
        "candidate_only": True,
        "production_gated": True,
    }


def evaluate(manifest, split, undecided):
    train_rows = [row for _, row in split["train"]]
    train_labels = [label_row["label"] for label_row, _ in split["train"]]
    if Counter(train_labels).get("pass", 0) < 8 \
            or Counter(train_labels).get("fail", 0) < 8:
        raise ValueError("M26 predeclared train pass/fail minimum not met")
    baselines = fit_frozen_baselines(manifest, train_rows, train_labels)

    holdout_rows = [row for _, row in split["holdout"]]
    actual = [label_row["label"] for label_row, _ in split["holdout"]]
    classes = sorted(set(actual) | {"pass", "fail"})
    distribution = Counter(actual)
    evaluations = {}
    for name in BASELINE_ORDER:
        baseline = baselines[name]
        predicted = [baseline.predict(row) for row in holdout_rows]
        metrics = classification_metrics(
            actual, predicted, classes, f"m27:frozen:{name}:accuracy")
        metrics["features"] = list(baseline.features)
        metrics["feature_count"] = len(baseline.features)
        evaluations[name] = metrics

    return {
        "schema_version": 1,
        "run_kind": "m27_frozen_error_holdout_evaluation",
        "task_category": manifest["task_category"],
        "label_classes": ["fail", "pass"],
        "n_train_used": len(train_rows),
        "n_holdout_used": len(holdout_rows),
        "undecided_excluded_counts": undecided,
        "train_label_distribution": dict(sorted(Counter(train_labels).items())),
        "holdout_label_distribution": dict(sorted(distribution.items())),
        "majority_class_baseline_accuracy": (
            max(distribution.values()) / len(actual)),
        "classifier_family": "train-standardized nearest centroid",
        "distance": "squared_euclidean",
        "tie_break": "lexicographic (fail before pass)",
        "baseline_order": list(BASELINE_ORDER),
        "evaluations": evaluations,
        "holdout_evaluated_once": True,
        "refit_or_threshold_tuning_after_holdout": False,
        "prompt_family_shortcut_control": (
            "single shared template; metadata_only baseline reports the "
            "difficulty-band shortcut explicitly"),
        "per_task_predictions_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate metrics/confusion only; no ids/text/paths",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m26_error_manifest.json")
    ap.add_argument("--labels",
                    default="reports/shadow/private/m26_error_labels_local.jsonl")
    ap.add_argument("--telemetry",
                    default="reports/shadow/private/m26_hf_telemetry_records_local.jsonl")
    ap.add_argument("--holdout-manifest-out",
                    default="data/prompts/m27_holdout_manifest.json")
    ap.add_argument("--evaluation-out",
                    default="reports/telemetry/hf_m27_frozen_error_evaluation.json")
    args = ap.parse_args(argv)

    manifest = M26.load_manifest(args.manifest)
    split, undecided = load_dataset(args.labels, args.telemetry)
    holdout_manifest = build_holdout_manifest(manifest, args.manifest)
    report = evaluate(manifest, split, undecided)
    for path, payload in ((args.holdout_manifest_out, holdout_manifest),
                          (args.evaluation_out, report)):
        out = Path(path); out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=1) + "\n")
    best = max(BASELINE_ORDER,
               key=lambda name: report["evaluations"][name]["accuracy"])
    print(f"[jlens] M27: frozen holdout n={report['n_holdout_used']}; "
          f"best baseline={best} "
          f"acc={report['evaluations'][best]['accuracy']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
