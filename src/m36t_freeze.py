"""M36T: development power check + step-256 comparator/classifier freeze.

Runs after the 96-task development capture. Per steer 0497526:

  - power gate: >=24 positive and >=24 negative development labels,
    else the run emits the power-failure artifact and M36T closes;
  - freezes the four step-256 comparators on development data only:
      1. metadata_only          — family one-hots + prompt length;
      2. metadata_plus_logprob  — + 8 prefix logprob summaries;
      3. metadata_plus_router   — + 4 prefix router summaries;
      4. full_prefix_telemetry  — + all 12 prefix summaries;
  - model: the project's established transparent classifier,
    CalibratedClassifierCV(LogisticRegression(max_iter=3000),
    isotonic, cv=3);
  - primary decision population: runs still alive at decode step 256
    (runs that finish earlier never reach the routing decision);
  - tool-call budget rule frozen from development data only:
    k = ceil(dev alive-at-256 positive prevalence x N_decision_alive);
  - steps 128/384 are secondary lead-time analyses (reported, not
    primary).

Public output is aggregate-only: counts, cross-validated metrics,
schema and config hashes. No per-task labels or predictions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from m36v_phase1 import PRIVATE_DIR  # noqa: E402

ROWS_IN = PRIVATE_DIR / "m36t_dev_rows.jsonl"
OUT = "reports/telemetry/m36t_freeze.json"
POWER_FLOOR = 24
PRIMARY_STEP = "256"
SECONDARY_STEPS = ("128", "384")
SEED = 36

LOGPROB_FEATURES = [
    "decode_window_entropy", "final_selected_probability",
    "final_top_k_margin", "mean_selected_probability",
    "high_entropy_count", "low_confidence_count", "top_k_margin_trend",
    "decode_step_count",
]
ROUTER_FEATURES = [
    "router_entropy_mean", "expert_concentration_mean",
    "windowed_expert_shift", "drift_final_window",
]
FAMILIES = ("div_exact", "json_digits", "mod_arith", "sub_mixed")

COMPARATORS = {
    "metadata_only": [],
    "metadata_plus_logprob": LOGPROB_FEATURES,
    "metadata_plus_router": ROUTER_FEATURES,
    "full_prefix_telemetry": LOGPROB_FEATURES + ROUTER_FEATURES,
}


def metadata_vector(row: dict) -> list[float]:
    fam = [1.0 if row["family"] == f else 0.0 for f in FAMILIES]
    stratum = float(row["stratum"].lstrip("s"))
    return fam + [stratum, float(row["prompt_rows"])]


def build_matrix(rows, step: str, telemetry: list[str]):
    import numpy as np

    X, y = [], []
    for row in rows:
        feats = row["prefix_features"].get(step)
        if feats is None:
            continue  # run finished before this decision point
        X.append(metadata_vector(row) + [float(feats[k]) for k in telemetry])
        y.append(1 if row["needs_more_than_512_tokens"] else 0)
    return np.asarray(X), np.asarray(y)


def cv_metrics(X, y) -> dict:
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import average_precision_score, balanced_accuracy_score
    from sklearn.model_selection import StratifiedKFold
    from sklearn.preprocessing import StandardScaler

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    proba = __import__("numpy").zeros(len(y), dtype=float)
    for train, test in skf.split(X, y):
        scaler = StandardScaler().fit(X[train])
        clf = CalibratedClassifierCV(
            LogisticRegression(max_iter=3000), method="isotonic", cv=3)
        clf.fit(scaler.transform(X[train]), y[train])
        proba[test] = clf.predict_proba(scaler.transform(X[test]))[:, 1]
    pred = (proba >= 0.5).astype(int)
    return {
        "balanced_accuracy": round(
            float(balanced_accuracy_score(y, pred)), 4),
        "average_precision": round(
            float(average_precision_score(y, proba)), 4),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rows", default=str(ROWS_IN))
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--dry-run", action="store_true",
                    help="report on partial rows; no freeze claim")
    args = ap.parse_args()

    rows = [json.loads(l) for l in Path(args.rows).read_text().splitlines()]
    pos = sum(1 for r in rows if r["needs_more_than_512_tokens"])
    neg = len(rows) - pos
    power_ok = pos >= POWER_FLOOR and neg >= POWER_FLOOR

    payload = {
        "schema_version": 1,
        "run_kind": "m36t_freeze" if not args.dry_run else "m36t_freeze_dry_run",
        "steer": "0497526",
        "dev_rows": len(rows),
        "labels": {"positive": pos, "negative": neg,
                   "power_floor": POWER_FLOOR, "power_ok": power_ok},
        "primary_step": int(PRIMARY_STEP),
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate metrics only",
    }
    if not power_ok and not args.dry_run:
        payload["run_kind"] = "m36t_power_failure"
        payload["outcome"] = "m36t_underpowered_development_set"
        Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
        print(f"[jlens] M36T POWER FAILURE: pos={pos} neg={neg} "
              f"(floor {POWER_FLOOR})", flush=True)
        return 1

    steps_report = {}
    alive_pos_prev = None
    for step in (PRIMARY_STEP, *SECONDARY_STEPS):
        per_comparator = {}
        for name, telemetry in COMPARATORS.items():
            X, y = build_matrix(rows, step, telemetry)
            if len(set(y.tolist())) < 2 or len(y) < 20:
                per_comparator[name] = {"skipped": f"n={len(y)}"}
                continue
            per_comparator[name] = {**cv_metrics(X, y), "n": int(len(y)),
                                    "n_features": int(X.shape[1])}
        n_alive = per_comparator.get("metadata_only", {}).get("n", 0)
        alive = [r for r in rows if r["prefix_features"].get(step)]
        a_pos = sum(1 for r in alive if r["needs_more_than_512_tokens"])
        steps_report[step] = {
            "alive_at_step": len(alive),
            "alive_positive": a_pos,
            "comparators": per_comparator,
        }
        if step == PRIMARY_STEP and alive:
            alive_pos_prev = a_pos / len(alive)

    schema = {"metadata": ["family_onehot_x4", "stratum_ordinal",
                           "prompt_rows"],
              "logprob": LOGPROB_FEATURES, "router": ROUTER_FEATURES}
    payload.update({
        "classifier": ("CalibratedClassifierCV(LogisticRegression("
                       "max_iter=3000), isotonic, cv=3) on standardized "
                       "features"),
        "cv": f"StratifiedKFold(5, shuffle, seed={SEED})",
        "feature_schema": schema,
        "feature_schema_sha256": hashlib.sha256(
            json.dumps(schema, sort_keys=True).encode()).hexdigest(),
        "tool_budget_rule": ("k = ceil(dev alive-at-256 positive "
                             "prevalence x N_decision_alive); prevalence "
                             f"= {round(alive_pos_prev, 4) if alive_pos_prev is not None else None}"),
        "steps": steps_report,
    })
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    primary = steps_report[PRIMARY_STEP]["comparators"]
    print(f"[jlens] M36T freeze{' (dry run)' if args.dry_run else ''}: "
          f"pos={pos} neg={neg} power_ok={power_ok} "
          f"primary256={json.dumps(primary)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
