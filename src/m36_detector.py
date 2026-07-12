#!/usr/bin/env python3
"""M36 detector fit + black-box policy calibration (steer 0be9d84).

Consumes the private calibration rows (never benchmark decision data),
splits them D/R (fit / calibrate) stratified by family x stratum, and
freezes:

  - full-telemetry track: an Agents-A1-specific global detector
    (train-standardized nearest-centroid over the fresh 12-feature AWQ
    schema, M27 classifier machinery) with a threshold chosen on R under
    the frozen tool budget — no proxy threshold, centroid, prior, or
    score scale is imported;
  - black-box track: per family x stratum competence priors from
    calibration outcomes with a prior threshold chosen on R under the
    same budget.

Both freezes carry config hashes; the benchmark refuses to run if a
refit does not reproduce them.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import m27_frozen_error_holdout as M27       # noqa: E402
import m28_ablation_calibration as M28       # noqa: E402
from m36_calibration import FEATURE_NAMES, ROWS_PATH  # noqa: E402
from m36v_phase1 import PRIVATE_DIR          # noqa: E402
from jlens_vllm_telemetry.report_guard import assert_aggregate_only  # noqa: E402

FREEZE_OUT = "reports/telemetry/m36_detector_freeze.json"
BUDGET_FRACTION = 0.5           # frozen: tool on at most half the tasks
THRESHOLD_GRID = [round(0.05 * i, 2) for i in range(1, 20)]
PRIOR_GRID = [round(0.05 * i, 2) for i in range(1, 20)]


def load_rows():
    rows = [json.loads(line)
            for line in ROWS_PATH.read_text().splitlines()]
    for row in rows:
        if row["verdict"] == "undecided":
            # Undecided verifier outcomes are treated as failures for
            # detector training: the policy's job is to flag tasks whose
            # original answer cannot be trusted.
            row["original_pass"] = False
    return rows


def split_dr(rows):
    """Alternate D/R within each family x stratum cell (deterministic)."""
    counters = {}
    d_rows, r_rows = [], []
    for row in sorted(rows, key=lambda r: r["task_id"]):
        key = (row["family"], row["stratum"])
        index = counters.get(key, 0)
        counters[key] = index + 1
        (d_rows if index % 2 == 0 else r_rows).append(row)
    return d_rows, r_rows


def feature_dict(row):
    return {name: float(row["features"][name]) for name in FEATURE_NAMES}


def fit_detector(d_rows):
    return M27.FrozenDictCentroid.fit(
        [feature_dict(r) for r in d_rows],
        ["pass" if r["original_pass"] else "fail" for r in d_rows],
        FEATURE_NAMES)


def calibrate_threshold(clf, r_rows):
    """Pick the fail-probability threshold on R: maximize final success
    under the frozen budget, ties broken toward fewer invocations."""
    scored = [(M28.fail_probability(clf, feature_dict(r)),
               r["original_pass"]) for r in r_rows]
    n = len(scored)
    best = None
    for threshold in THRESHOLD_GRID:
        invoked = [p >= threshold for p, _ in scored]
        fraction = sum(invoked) / n
        if fraction > BUDGET_FRACTION:
            continue
        success = sum(1 for (p, ok), inv in zip(scored, invoked)
                      if ok or inv) / n
        key = (success, -fraction)
        if best is None or key > best[0]:
            best = (key, threshold, fraction, success)
    _, threshold, fraction, success = best
    return {"threshold": threshold, "r_invocation_fraction": round(fraction, 4),
            "r_final_success": round(success, 4)}


def cell_priors(d_rows):
    cells = {}
    for row in d_rows:
        key = f"{row['family']}:{row['stratum']}"
        cell = cells.setdefault(key, [0, 0])
        cell[0] += int(not row["original_pass"])
        cell[1] += 1
    return {key: round(fails / total, 4)
            for key, (fails, total) in sorted(cells.items())}


def calibrate_prior_threshold(priors, r_rows):
    n = len(r_rows)
    best = None
    for threshold in PRIOR_GRID:
        invoked = [priors.get(f"{r['family']}:{r['stratum']}", 1.0)
                   >= threshold for r in r_rows]
        fraction = sum(invoked) / n
        if fraction > BUDGET_FRACTION:
            continue
        success = sum(1 for r, inv in zip(r_rows, invoked)
                      if r["original_pass"] or inv) / n
        key = (success, -fraction)
        if best is None or key > best[0]:
            best = (key, threshold, fraction, success)
    _, threshold, fraction, success = best
    return {"prior_threshold": threshold,
            "r_invocation_fraction": round(fraction, 4),
            "r_final_success": round(success, 4)}


def detector_hash(clf, threshold: float) -> str:
    h = hashlib.sha256()
    h.update(json.dumps({
        "features": clf.features,
        "means": clf.means, "scales": clf.scales,
        "centroids": clf.centroids,
        "training_count": clf.training_count,
        "threshold": threshold,
        "budget": BUDGET_FRACTION,
    }, sort_keys=True).encode())
    return h.hexdigest()[:16]


def policy_hash(priors: dict, threshold: float) -> str:
    h = hashlib.sha256()
    h.update(json.dumps({"priors": priors, "threshold": threshold,
                         "budget": BUDGET_FRACTION},
                        sort_keys=True).encode())
    return h.hexdigest()[:16]


def build_freeze(rows):
    d_rows, r_rows = split_dr(rows)
    clf = fit_detector(d_rows)
    telemetry_cal = calibrate_threshold(clf, r_rows)
    priors = cell_priors(d_rows)
    blackbox_cal = calibrate_prior_threshold(priors, r_rows)

    d_fail = sum(1 for r in d_rows if not r["original_pass"])
    freeze = {
        "schema_version": 1,
        "run_kind": "m36_detector_freeze",
        "rows_total": len(rows),
        "d_rows": len(d_rows), "r_rows": len(r_rows),
        "d_fail_count": d_fail,
        "feature_names": FEATURE_NAMES,
        "budget_fraction": BUDGET_FRACTION,
        "full_telemetry": {
            **telemetry_cal,
            "detector_hash": detector_hash(clf, telemetry_cal["threshold"]),
            "model_class": "train-standardized nearest-centroid "
                           "(M27 FrozenDictCentroid), fresh AWQ fit",
        },
        "black_box": {
            **blackbox_cal,
            "policy_hash": policy_hash(priors, blackbox_cal["prior_threshold"]),
            "cells": len(priors),
        },
        "proxy_import": "none (fresh fit; no proxy threshold/centroid/prior)",
        "calibration_rows_are_benchmark_data": False,
        "per_task_predictions_persisted_publicly": False,
        "privacy_check_status": "aggregate fit/calibration stats only",
    }
    return freeze, clf, priors


def refit_and_verify(freeze):
    """Refit from the same rows and confirm both hashes reproduce."""
    rows = load_rows()
    refreeze, clf, priors = build_freeze(rows)
    ok = (refreeze["full_telemetry"]["detector_hash"]
          == freeze["full_telemetry"]["detector_hash"]
          and refreeze["black_box"]["policy_hash"]
          == freeze["black_box"]["policy_hash"])
    return ok, clf, priors


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=FREEZE_OUT)
    args = ap.parse_args(argv)

    rows = load_rows()
    freeze, clf, priors = build_freeze(rows)
    assert_aggregate_only(freeze)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(freeze, indent=1) + "\n")
    # Private sidecar so the benchmark can reload the exact fitted state
    # without re-reading calibration rows.
    sidecar = {
        "classifier": {"features": clf.features, "means": clf.means,
                       "scales": clf.scales, "centroids": clf.centroids,
                       "training_count": clf.training_count},
        "priors": priors,
        "full_telemetry": freeze["full_telemetry"],
        "black_box": freeze["black_box"],
    }
    (PRIVATE_DIR / "m36_detector_state.json").write_text(
        json.dumps(sidecar, indent=1) + "\n")
    print(f"[jlens] M36 detector freeze: d={freeze['d_rows']} "
          f"r={freeze['r_rows']} d_fail={freeze['d_fail_count']} "
          f"tel_thr={freeze['full_telemetry']['threshold']} "
          f"(frac={freeze['full_telemetry']['r_invocation_fraction']}) "
          f"bb_thr={freeze['black_box']['prior_threshold']} "
          f"(frac={freeze['black_box']['r_invocation_fraction']})",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
