#!/usr/bin/env python3
"""M28 telemetry feature ablation and candidate-only calibration analysis."""
from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import m26_objective_error as M26  # noqa: E402
import m27_frozen_error_holdout as M27  # noqa: E402


def _distances(classifier, row):
    values = [(float(row[name]) - mean) / scale
              for name, mean, scale in zip(classifier.features,
                                           classifier.means,
                                           classifier.scales)]
    return {label: sum((value - center) ** 2
                       for value, center in zip(values, centroid))
            for label, centroid in classifier.centroids.items()}


def fail_probability(classifier, row):
    """Softmax over negative squared centroid distances, per M26 predeclaration."""
    distances = _distances(classifier, row)
    lowest = min(distances.values())
    weights = {label: math.exp(-(distance - lowest))
               for label, distance in distances.items()}
    total = sum(weights.values())
    return weights.get("fail", 0.0) / total


def _fit_eval(train_rows, train_labels, holdout_rows, holdout_actual,
              features, seed_tag):
    classifier = M27.FrozenDictCentroid.fit(train_rows, train_labels, features)
    predicted = [classifier.predict(row) for row in holdout_rows]
    classes = sorted(set(holdout_actual) | {"pass", "fail"})
    metrics = M27.classification_metrics(
        holdout_actual, predicted, classes, f"m28:{seed_tag}:accuracy")
    return classifier, predicted, metrics


def ablation_report(manifest, train_rows, train_labels, holdout_rows,
                    holdout_actual):
    full_features = manifest["frozen_feature_sets"]["full_telemetry"]
    _, _, full_metrics = _fit_eval(
        train_rows, train_labels, holdout_rows, holdout_actual,
        full_features, "full")
    single, leave_one_out = {}, {}
    for feature in full_features:
        _, _, metrics = _fit_eval(
            train_rows, train_labels, holdout_rows, holdout_actual,
            [feature], f"single:{feature}")
        single[feature] = {
            "accuracy": metrics["accuracy"],
            "balanced_accuracy": metrics["balanced_accuracy"],
            "accuracy_bootstrap_95pct": metrics["accuracy_bootstrap_95pct"],
        }
        remaining = [name for name in full_features if name != feature]
        _, _, metrics = _fit_eval(
            train_rows, train_labels, holdout_rows, holdout_actual,
            remaining, f"loo:{feature}")
        leave_one_out[feature] = {
            "accuracy": metrics["accuracy"],
            "balanced_accuracy": metrics["balanced_accuracy"],
            "accuracy_drop_vs_full": full_metrics["accuracy"]
            - metrics["accuracy"],
        }
    return {
        "full_telemetry": {
            "features": list(full_features),
            "accuracy": full_metrics["accuracy"],
            "balanced_accuracy": full_metrics["balanced_accuracy"],
            "macro_f1": full_metrics["macro_f1"],
            "accuracy_bootstrap_95pct": full_metrics["accuracy_bootstrap_95pct"],
        },
        "single_feature": single,
        "leave_one_out": leave_one_out,
        "verifier_contradiction_feature": (
            "excluded by design: the deterministic verifier defines the "
            "pass/fail label, so its signal cannot be an input feature"),
    }


def calibration_report(classifier, train_pairs, holdout_pairs):
    """Train-derived candidate threshold plus holdout reliability, per M26."""
    train_scores = [(fail_probability(classifier, row), label_row["label"])
                    for label_row, row in train_pairs]
    holdout_scores = [(fail_probability(classifier, row), label_row["label"])
                      for label_row, row in holdout_pairs]

    def balanced_accuracy(scores, threshold):
        outcomes = {"fail": [0, 0], "pass": [0, 0]}
        for score, label in scores:
            predicted = "fail" if score >= threshold else "pass"
            outcomes[label][0] += predicted == label
            outcomes[label][1] += 1
        recalls = [hit / total for hit, total in outcomes.values() if total]
        return statistics.fmean(recalls) if recalls else 0.0

    grid = [round(0.05 * step, 2) for step in range(1, 20)]
    train_curve = [(threshold, balanced_accuracy(train_scores, threshold))
                   for threshold in grid]
    best_threshold, best_train_bacc = max(
        train_curve, key=lambda item: (item[1], -item[0]))

    ordered = sorted(holdout_scores, key=lambda item: item[0])
    n_bins = 4
    bins = []
    ece = 0.0
    for index in range(n_bins):
        chunk = ordered[index * len(ordered) // n_bins:
                        (index + 1) * len(ordered) // n_bins]
        if not chunk:
            continue
        mean_predicted = statistics.fmean(score for score, _ in chunk)
        observed = statistics.fmean(
            1.0 if label == "fail" else 0.0 for _, label in chunk)
        ece += (len(chunk) / len(ordered)) * abs(mean_predicted - observed)
        bins.append({"n": len(chunk),
                     "mean_predicted_fail_probability": mean_predicted,
                     "observed_fail_rate": observed})
    return {
        "score_definition": ("softmax over negative squared centroid "
                             "distances; probability mass on the fail class"),
        "reliability_bins_equal_count": bins,
        "expected_calibration_error": ece,
        "candidate_threshold": {
            "status": "candidate-only",
            "not_for_production": True,
            "derived_from": "train split balanced-accuracy grid search only",
            "threshold_fail_probability": best_threshold,
            "train_balanced_accuracy_at_threshold": best_train_bacc,
            "holdout_balanced_accuracy_at_threshold_descriptive":
                balanced_accuracy(holdout_scores, best_threshold),
        },
    }


def error_analysis(classifier, holdout_pairs):
    """Aggregate false-positive/false-negative counts; positive class = fail."""
    by_band = {}
    totals = Counter()
    for label_row, row in holdout_pairs:
        predicted = classifier.predict(row)
        band = by_band.setdefault(label_row["band"], Counter())
        if predicted == "fail" and label_row["label"] == "pass":
            band["false_positive"] += 1
            totals["false_positive"] += 1
        elif predicted == "pass" and label_row["label"] == "fail":
            band["false_negative"] += 1
            totals["false_negative"] += 1
        else:
            band["correct"] += 1
            totals["correct"] += 1
        band["n"] += 1
    return {
        "positive_class": "fail",
        "totals": dict(sorted(totals.items())),
        "by_band": {band: dict(sorted(counts.items()))
                    for band, counts in sorted(by_band.items())},
    }


def build_report(manifest, split):
    train_rows = [row for _, row in split["train"]]
    train_labels = [label_row["label"] for label_row, _ in split["train"]]
    holdout_rows = [row for _, row in split["holdout"]]
    holdout_actual = [label_row["label"] for label_row, _ in split["holdout"]]

    ablation = ablation_report(
        manifest, train_rows, train_labels, holdout_rows, holdout_actual)
    full_classifier = M27.FrozenDictCentroid.fit(
        train_rows, train_labels,
        manifest["frozen_feature_sets"]["full_telemetry"])
    calibration = calibration_report(
        full_classifier, split["train"], split["holdout"])
    errors = error_analysis(full_classifier, split["holdout"])
    return {
        "schema_version": 1,
        "run_kind": "m28_telemetry_ablation_calibration",
        "task_category": manifest["task_category"],
        "n_train_used": len(train_rows),
        "n_holdout_used": len(holdout_rows),
        "protocol_source": "m28_frozen_protocol predeclared in the M26 manifest",
        "ablation": ablation,
        "calibration": calibration,
        "false_positive_negative_analysis": errors,
        "small_holdout_caveat": (
            "n=32 holdout tasks produce wide bootstrap intervals; ablation "
            "rankings are descriptive and must not be read as stable feature "
            "importance"),
        "threshold_status": "candidate-only",
        "production_threshold_set": False,
        "per_task_predictions_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate ablation/calibration only; no ids/text/paths",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default="data/prompts/m26_error_manifest.json")
    ap.add_argument("--labels",
                    default="reports/shadow/private/m26_error_labels_local.jsonl")
    ap.add_argument("--telemetry",
                    default="reports/shadow/private/m26_hf_telemetry_records_local.jsonl")
    ap.add_argument("--report-out",
                    default="reports/telemetry/hf_m28_ablation_calibration.json")
    args = ap.parse_args(argv)

    manifest = M26.load_manifest(args.manifest)
    split, _undecided = M27.load_dataset(args.labels, args.telemetry)
    report = build_report(manifest, split)
    out = Path(args.report_out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=1) + "\n")
    print(f"[jlens] M28: ablation/calibration written; ECE="
          f"{report['calibration']['expected_calibration_error']:.3f} "
          f"(candidate-only)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
