#!/usr/bin/env python3
"""M35 track B: transfer-robust detector fitting (D), LOFO, sealed B-test."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import m27_frozen_error_holdout as M27  # noqa: E402
import m28_ablation_calibration as M28  # noqa: E402

THRESHOLD = 0.5
# Hierarchical regime prior gates, fixed before any sealed read.
PRIOR_FAIL_GATE = 0.85
PRIOR_PASS_GATE = 0.15
FAMILIES = ("add_carry", "sub_borrow", "mul_carry", "div_exact", "mul_add",
            "mod_mul")


def scalar_features(row):
    return dict(row["features"])


def global_features(row, known_families):
    """Scalar features plus family one-hots; unknown family maps to zeros."""
    out = dict(row["features"])
    for family in known_families:
        out[f"family_{family}"] = 1.0 if row["family"] == family else 0.0
    return out


def _labels(rows):
    return ["pass" if row["original_pass"] else "fail" for row in rows]


def fit_variants(d_rows, families=None):
    """Fit the three detector variants on development rows only."""
    families = tuple(families if families is not None
                     else sorted({row["family"] for row in d_rows}))
    feature_names = sorted(d_rows[0]["features"])
    global_names = list(feature_names) + [f"family_{f}" for f in families]
    global_clf = M27.FrozenDictCentroid.fit(
        [global_features(row, families) for row in d_rows],
        _labels(d_rows), global_names)
    fallback_clf = M27.FrozenDictCentroid.fit(
        [scalar_features(row) for row in d_rows],
        _labels(d_rows), feature_names)
    per_family, priors = {}, {}
    for family in families:
        rows = [row for row in d_rows if row["family"] == family]
        if not rows:
            continue
        fails = sum(1 for row in rows if not row["original_pass"])
        priors[family] = fails / len(rows)
        labels = _labels(rows)
        if len(set(labels)) == 2:
            per_family[family] = M27.FrozenDictCentroid.fit(
                [scalar_features(row) for row in rows], labels,
                feature_names)
    pooled_prior = (sum(1 for row in d_rows if not row["original_pass"])
                    / len(d_rows))
    return {"families": families, "global": global_clf,
            "fallback": fallback_clf, "per_family": per_family,
            "priors": priors, "pooled_prior": pooled_prior}


def p_fail(variants, variant, row):
    family = row["family"]
    known = family in variants["families"]
    if variant == "global":
        return M28.fail_probability(
            variants["global"], global_features(row, variants["families"]))
    if variant == "per_family":
        clf = variants["per_family"].get(family) if known else None
        clf = clf or variants["fallback"]
        return M28.fail_probability(clf, scalar_features(row))
    if variant == "hierarchical":
        if not known:
            return M28.fail_probability(variants["fallback"],
                                        scalar_features(row))
        prior = variants["priors"][family]
        if prior >= PRIOR_FAIL_GATE or prior <= PRIOR_PASS_GATE:
            return prior
        clf = variants["per_family"].get(family) or variants["fallback"]
        return M28.fail_probability(clf, scalar_features(row))
    raise ValueError(f"unknown variant {variant}")


def detector_metrics(variants, variant, rows):
    triggered = hits = fails = 0
    for row in rows:
        fail = not row["original_pass"]
        fails += fail
        if p_fail(variants, variant, row) >= THRESHOLD:
            triggered += 1
            hits += fail
    return {
        "n_rows": len(rows),
        "original_fail_count": fails,
        "trigger_count": triggered,
        "trigger_precision": hits / triggered if triggered else None,
        "trigger_recall": hits / fails if fails else None,
    }


def config_hash(variants):
    """Deterministic hash over every fitted parameter, for the freeze commit."""
    def encode_clf(clf):
        return {"features": clf.features, "means": clf.means,
                "scales": clf.scales, "centroids": clf.centroids,
                "training_count": clf.training_count}
    payload = {
        "families": variants["families"],
        "global": encode_clf(variants["global"]),
        "fallback": encode_clf(variants["fallback"]),
        "per_family": {family: encode_clf(clf) for family, clf
                       in sorted(variants["per_family"].items())},
        "priors": dict(sorted(variants["priors"].items())),
        "pooled_prior": variants["pooled_prior"],
        "threshold": THRESHOLD,
        "prior_gates": [PRIOR_PASS_GATE, PRIOR_FAIL_GATE],
    }
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]


def lofo_variants(d_rows, withheld):
    """Refit the ENTIRE pipeline on D minus the withheld family."""
    remaining = [row for row in d_rows if row["family"] != withheld]
    families = tuple(f for f in sorted({r["family"] for r in remaining}))
    return fit_variants(remaining, families=families)


def run_lofo(d_rows, b_rows):
    results = {}
    for withheld in FAMILIES:
        variants = lofo_variants(d_rows, withheld)
        family_b = [row for row in b_rows if row["family"] == withheld]
        results[withheld] = {
            variant: detector_metrics(variants, variant, family_b)
            for variant in ("global", "per_family", "hierarchical")}
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rows",
                    default="reports/shadow/private/m35_campaign_rows_local.jsonl")
    ap.add_argument("--stage", choices=("fit", "b_test"), required=True)
    ap.add_argument("--freeze-out",
                    default="reports/telemetry/hf_m35_track_b_freeze.json")
    ap.add_argument("--evaluation-out",
                    default="reports/telemetry/hf_m35_track_b_evaluation.json")
    args = ap.parse_args(argv)

    rows = [json.loads(line) for line in
            Path(args.rows).read_text().splitlines() if line]
    d_rows = [row for row in rows if row["split"] == "D"]
    if args.stage == "fit":
        variants = fit_variants(d_rows)
        d_metrics = {variant: detector_metrics(variants, variant, d_rows)
                     for variant in ("global", "per_family", "hierarchical")}
        freeze = {
            "schema_version": 1,
            "run_kind": "m35_track_b_freeze",
            "fit_split": "D",
            "d_row_count": len(d_rows),
            "config_hash": config_hash(variants),
            "threshold": THRESHOLD,
            "prior_gates": {"pass": PRIOR_PASS_GATE, "fail": PRIOR_FAIL_GATE},
            "in_sample_d_metrics_descriptive": d_metrics,
            "sealed_reads_performed": [],
            "per_task_predictions_persisted_publicly": False,
            "privacy_check_status": "aggregate metrics only",
        }
        Path(args.freeze_out).write_text(json.dumps(freeze, indent=1) + "\n")
        print(f"[jlens] M35 track B frozen: config_hash="
              f"{freeze['config_hash']}; D in-sample "
              f"{ {k: round(v['trigger_precision'] or 0, 3) for k, v in d_metrics.items()} }",
              flush=True)
        return 0

    # b_test stage: single sealed read
    freeze = json.loads(Path(args.freeze_out).read_text())
    if freeze.get("sealed_reads_performed"):
        raise ValueError("M35 B-test has already been read; refusing reread")
    variants = fit_variants(d_rows)
    if config_hash(variants) != freeze["config_hash"]:
        raise ValueError("M35 track B refit does not match frozen config hash")
    b_rows = [row for row in rows if row["split"] == "B_test"]
    pooled = {variant: detector_metrics(variants, variant, b_rows)
              for variant in ("global", "per_family", "hierarchical")}
    per_family_b = {}
    by_family = defaultdict(list)
    for row in b_rows:
        by_family[row["family"]].append(row)
    for family, family_rows in sorted(by_family.items()):
        per_family_b[family] = {
            variant: detector_metrics(variants, variant, family_rows)
            for variant in ("global", "per_family", "hierarchical")}
    lofo = run_lofo(d_rows, b_rows)
    evaluation = {
        "schema_version": 1,
        "run_kind": "m35_track_b_evaluation",
        "config_hash": freeze["config_hash"],
        "b_test_row_count": len(b_rows),
        "primary_lofo": lofo,
        "full_fit_per_family_descriptive": per_family_b,
        "pooled_b_test_secondary": pooled,
        "claim_scope": ("LOFO establishes robustness across these named "
                        "withheld families under this generator/prompt/"
                        "model/decode/telemetry regime and nothing beyond; "
                        "pooled held-out performance is secondary and is "
                        "not transfer evidence"),
        "per_task_predictions_persisted_publicly": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate metrics only",
    }
    Path(args.evaluation_out).write_text(
        json.dumps(evaluation, indent=1) + "\n")
    freeze["sealed_reads_performed"] = ["B_test"]
    Path(args.freeze_out).write_text(json.dumps(freeze, indent=1) + "\n")
    print("[jlens] M35 B-test read complete (single read recorded)",
          flush=True)
    for withheld, metrics in lofo.items():
        h = metrics["hierarchical"]
        print(f"[jlens]  LOFO {withheld}: hierarchical precision="
              f"{h['trigger_precision']} recall={h['trigger_recall']}",
              flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
