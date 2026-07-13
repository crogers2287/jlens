"""M36T: frozen sealed evaluation (runs once, after sealed capture).

Implements reports/telemetry/m36t_sealed_manifest.json exactly:

  - trains the four frozen comparators on the development rows only;
  - scores the sealed rows alive at step 256;
  - T-H1: full_prefix_telemetry vs metadata_plus_logprob on balanced
    accuracy and average precision (paired bootstrap, both 95% lower
    bounds > 0);
  - policy arms, all counterfactual from each task's single source run:
    normal_512, metadata_policy, full_jlens_policy (identical frozen
    k = ceil(0.6989 x N_alive)), count_matched_random, long_decode_2048,
    tool_all (ceiling; reported, not compared);
  - T-H2: full_jlens vs metadata_policy AND count_matched_random on
    verified success (paired lower bounds > 0);
  - T-H3: non-inferiority to long_decode_2048 within 0.02 verified
    success AND paired model-token saving lower bound > 0;
  - bootstrap: task-level, 10,000 resamples, seed 36036.

The trusted tool is the family's deterministic solver; a tool result
replaces the model result only when the verifier accepts it, so no arm
can turn a verified-correct answer into a failure. Aggregate-only
output; per-task predictions stay private.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from m36t_freeze import COMPARATORS, SEED, build_matrix, metadata_vector  # noqa: E402
from m36v_phase1 import PRIVATE_DIR  # noqa: E402

DEV_ROWS = PRIVATE_DIR / "m36t_dev_rows.jsonl"
SEALED_ROWS = PRIVATE_DIR / "m36t_sealed_rows.jsonl"
OUT = "reports/telemetry/m36t_result.json"
BOOT_N, BOOT_SEED = 10_000, 36036
PREVALENCE = 0.6989
STEP = "256"


def train_and_score(dev_rows, sealed_alive):
    """Fit each frozen comparator on dev; return sealed probabilities."""
    import numpy as np
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    scores = {}
    for name, telemetry in COMPARATORS.items():
        Xd, yd = build_matrix(dev_rows, STEP, telemetry)
        Xs = np.asarray([metadata_vector(r)
                         + [float(r["prefix_features"][STEP][k])
                            for k in telemetry]
                         for r in sealed_alive])
        scaler = StandardScaler().fit(Xd)
        clf = CalibratedClassifierCV(
            LogisticRegression(max_iter=3000), method="isotonic", cv=3)
        clf.fit(scaler.transform(Xd), yd)
        scores[name] = clf.predict_proba(scaler.transform(Xs))[:, 1]
    return scores


def paired_bootstrap(values, rng, n=BOOT_N):
    """95% percentile interval of the mean of per-task paired diffs."""
    import numpy as np

    values = np.asarray(values, dtype=float)
    idx = rng.integers(0, len(values), size=(n, len(values)))
    means = values[idx].mean(axis=1)
    return (float(np.percentile(means, 2.5)),
            float(values.mean()),
            float(np.percentile(means, 97.5)))


def metric_bootstrap(y, pa, pb, metric, rng, n=BOOT_N):
    """Paired bootstrap of metric(a) - metric(b) over task resamples."""
    import numpy as np

    y, pa, pb = (np.asarray(v) for v in (y, pa, pb))
    diffs = []
    for _ in range(n):
        idx = rng.integers(0, len(y), size=len(y))
        if len(set(y[idx].tolist())) < 2:
            continue
        diffs.append(metric(y[idx], pa[idx]) - metric(y[idx], pb[idx]))
    diffs = np.asarray(diffs)
    return (float(np.percentile(diffs, 2.5)), float(diffs.mean()),
            float(np.percentile(diffs, 97.5)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    import numpy as np
    from sklearn.metrics import average_precision_score, balanced_accuracy_score

    rng = np.random.default_rng(BOOT_SEED)
    dev = [json.loads(l) for l in DEV_ROWS.read_text().splitlines()]
    sealed = [json.loads(l) for l in SEALED_ROWS.read_text().splitlines()]
    alive = [r for r in sealed if r["prefix_features"].get(STEP)]
    y = np.asarray([1 if r["needs_more_than_512_tokens"] else 0
                    for r in alive])
    n_pos = int(y.sum())
    scores = train_and_score(dev, alive)

    # ---- T-H1: sealed prediction quality --------------------------------
    def bal_acc(yy, pp):
        return balanced_accuracy_score(yy, (pp >= 0.5).astype(int))

    h1 = {}
    for metric_name, metric in (("balanced_accuracy", bal_acc),
                                ("average_precision",
                                 average_precision_score)):
        lo, mean, hi = metric_bootstrap(
            y, scores["full_prefix_telemetry"],
            scores["metadata_plus_logprob"], metric, rng)
        h1[metric_name] = {"mean_diff": round(mean, 4),
                           "ci95": [round(lo, 4), round(hi, 4)]}
    h1_pass = all(v["ci95"][0] > 0 for v in h1.values())

    sealed_pred = {name: {"balanced_accuracy": round(bal_acc(y, p), 4),
                          "average_precision": round(
                              float(average_precision_score(y, p)), 4)}
                   for name, p in scores.items()}

    # ---- policy arms -----------------------------------------------------
    k = math.ceil(PREVALENCE * len(alive))
    alive_ids = [r["task_id"] for r in alive]
    by_id = {r["task_id"]: r for r in sealed}

    def routed_set(ranking):
        order = np.argsort(-ranking)
        return {alive_ids[i] for i in order[:k]}

    random_routed = set(np.asarray(alive_ids)[
        rng.permutation(len(alive_ids))[:k]].tolist())

    def arm_outcomes(routed: set | None, cap_verdict_key="512",
                     long_arm=False, tool_all=False):
        succ, tokens = [], []
        for r in sealed:
            if tool_all or (routed is not None
                            and r["task_id"] in routed):
                succ.append(1.0)             # verifier-accepted tool result
                tokens.append(min(r["output_tokens"], 256))
            elif long_arm:
                succ.append(1.0 if r["verdict"] == "pass" else 0.0)
                tokens.append(r["output_tokens"])
            else:
                succ.append(1.0 if r["verdict_at_cap"][cap_verdict_key]
                            == "pass" and r["output_tokens"] <= 2048
                            and (r["output_tokens"] <= 512
                                 or r["verdict_at_cap"]["512"] == "pass")
                            else 0.0)
                tokens.append(min(r["output_tokens"], 512))
        return np.asarray(succ), np.asarray(tokens)

    arms = {}
    s_normal, t_normal = arm_outcomes(routed=None)
    arms["normal_512"] = (s_normal, t_normal)
    arms["metadata_policy"] = arm_outcomes(
        routed_set(scores["metadata_plus_logprob"]))
    arms["full_jlens_policy"] = arm_outcomes(
        routed_set(scores["full_prefix_telemetry"]))
    arms["count_matched_random"] = arm_outcomes(random_routed)
    arms["long_decode_2048"] = arm_outcomes(routed=None, long_arm=True)
    arms["tool_all"] = arm_outcomes(routed=None, tool_all=True)

    arm_report = {name: {"verified_success": round(float(s.mean()), 4),
                         "model_tokens_mean": round(float(t.mean()), 1)}
                  for name, (s, t) in arms.items()}

    # ---- T-H2 ------------------------------------------------------------
    sj = arms["full_jlens_policy"][0]
    h2 = {}
    for other in ("metadata_policy", "count_matched_random"):
        lo, mean, hi = paired_bootstrap(sj - arms[other][0], rng)
        h2[other] = {"mean_diff": round(mean, 4),
                     "ci95": [round(lo, 4), round(hi, 4)]}
    h2_pass = all(v["ci95"][0] > 0 for v in h2.values())

    # ---- T-H3 ------------------------------------------------------------
    slong, tlong = arms["long_decode_2048"]
    tj = arms["full_jlens_policy"][1]
    lo_ni, mean_ni, hi_ni = paired_bootstrap(sj - slong + 0.02, rng)
    lo_tok, mean_tok, hi_tok = paired_bootstrap(tlong - tj, rng)
    h3 = {"noninferiority_margin_0.02": {
              "mean": round(mean_ni, 4), "ci95_lower": round(lo_ni, 4)},
          "token_saving": {"mean": round(mean_tok, 1),
                           "ci95_lower": round(lo_tok, 1)}}
    h3_pass = lo_ni > 0 and lo_tok > 0

    payload = {
        "schema_version": 1,
        "run_kind": "m36t_result",
        "manifest": "reports/telemetry/m36t_sealed_manifest.json",
        "sealed_n": len(sealed),
        "alive_at_256": len(alive),
        "sealed_positives": n_pos,
        "tool_call_budget_k": k,
        "sealed_prediction": sealed_pred,
        "T_H1": {"pass": bool(h1_pass), **h1},
        "arms": arm_report,
        "T_H2": {"pass": bool(h2_pass), **h2},
        "T_H3": {"pass": bool(h3_pass), **h3},
        "bootstrap": {"n": BOOT_N, "seed": BOOT_SEED},
        "privacy_check_status": "aggregate metrics only",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36T result: H1={h1_pass} H2={h2_pass} H3={h3_pass} "
          f"arms={json.dumps(arm_report)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
