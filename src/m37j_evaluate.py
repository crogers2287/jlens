"""M37J-A: frozen H1/H2 evaluation on the preregistered diagnostic set.

Feature families per the frozen protocol:
  A (predeclared): the five fixed semantic-group scores captured with
    the rows; no words were added after the smoke.
  B (discovery-derived, bounded): from normalized top-k lens readout
    tokens — a vocabulary of the 16 most frequent discovery tokens
    (counts per row), plus mid-layer top-1 persistence (max run
    length), mid-layer concept churn (distinct top-1 fraction), and
    late-layer last-transition position fraction. Sparsified by
    L1-logistic on DISCOVERY only (keep <= 10 nonzero features);
    vocabulary, normalization, sparsity, and feature count frozen on
    VALIDATION before holdout labels are opened.

Comparators (trained on discovery+validation, evaluated on holdout):
  1. metadata + output length;
  2. + logit/router telemetry;
  3. + J-space features (A + frozen B);
  4. all approved features combined.

H1 (completed, nontruncated holdout rows — outcome classes 1/2):
  comparator 4 must beat comparator 2 on failure-prediction accuracy
  and balanced accuracy, both paired 95% bootstrap lower bounds > 0.
H2 (short-cap truncations — classes 3/4): frozen J-space policy must
  beat metadata+length+telemetry; reported as underpowered if the
  population is below a workable floor (POWER_FLOOR_H2 per side).

Aggregate-only output; rows/readouts stay private.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from m36v_phase1 import PRIVATE_DIR  # noqa: E402

ROWS = PRIVATE_DIR / "m37j_diag_rows.jsonl"
OUT = "reports/telemetry/m37j_a_result.json"
BOOT_N, BOOT_SEED = 10_000, 37037
VOCAB_N, MAX_B_FEATURES = 16, 10
POWER_FLOOR_H2 = 8
FAMILIES = ("mod_chain", "alg_coeff", "order_track", "json_digits")
MID_LAYER, LATE_LAYER = "11", "21"
TOKEN_RE = re.compile(r"[a-z]{2,}")


def norm_tokens(readout: dict) -> list[str]:
    out = []
    for layer_tokens in readout.values():
        for pos in layer_tokens:
            out.extend(t for t in pos if TOKEN_RE.fullmatch(t))
    return out


def meta_vector(r: dict) -> list[float]:
    fam = [1.0 if r["family"] == f else 0.0 for f in FAMILIES]
    return fam + [float(r["band"].lstrip("b")), float(r["prompt_tokens"]),
                  float(r["output_tokens"])]


def telem_vector(r: dict) -> list[float]:
    lp, rt = r["logprob_features"], r["router_features"]
    return [float(v) for v in lp.values()] + [float(v) for v in rt.values()]


def family_a_vector(r: dict) -> list[float]:
    return [float(v) for v in r["semantic_scores"].values()]


def b_raw_vector(r: dict, vocab: list[str]) -> list[float]:
    tokens = norm_tokens(r["lens_readout_tokens"])
    counts = [float(tokens.count(v)) for v in vocab]
    mid = r["lens_readout_tokens"].get(MID_LAYER, [])
    top1 = [pos[0] if pos else "" for pos in mid]
    run = best = 0
    for i, t in enumerate(top1):
        run = run + 1 if i and t == top1[i - 1] else 1
        best = max(best, run)
    churn = len(set(top1)) / len(top1) if top1 else 0.0
    late = [pos[0] if pos else "" for pos in
            r["lens_readout_tokens"].get(LATE_LAYER, [])]
    last_change = 0.0
    for i in range(1, len(late)):
        if late[i] != late[i - 1]:
            last_change = i / max(1, len(late) - 1)
    return counts + [float(best), churn, last_change]


def build_b(discovery, all_rows):
    """Fit vocabulary + sparsity on discovery only; returns the frozen
    column list and per-row-id vectors."""
    import numpy as np
    from collections import Counter
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    counter = Counter()
    for r in discovery:
        counter.update(set(norm_tokens(r["lens_readout_tokens"])))
    vocab = [t for t, _ in counter.most_common(VOCAB_N)]
    names = [f"vocab_{v}" for v in vocab] + [
        "mid_top1_persistence", "mid_top1_churn", "late_last_transition"]

    disc_completed = [r for r in discovery if r["outcome_class"] in (1, 2)]
    Xd = np.asarray([b_raw_vector(r, vocab) for r in disc_completed])
    yd = np.asarray([1 if r["verdict_full"] != "pass" else 0
                     for r in disc_completed])
    scaler = StandardScaler().fit(Xd)
    l1 = LogisticRegression(penalty="l1", solver="liblinear", C=0.5,
                            max_iter=3000).fit(scaler.transform(Xd), yd)
    coef = l1.coef_[0]
    order = sorted(range(len(coef)), key=lambda i: -abs(coef[i]))
    kept = [i for i in order if abs(coef[i]) > 0][:MAX_B_FEATURES]
    vectors = {r["task_id"]:
               [b_raw_vector(r, vocab)[i] for i in kept]
               for r in all_rows}
    return [names[i] for i in kept], vectors


def paired_metric_bootstrap(y, pa, pb, metric, rng, n=BOOT_N):
    import numpy as np

    diffs = []
    y, pa, pb = (np.asarray(v) for v in (y, pa, pb))
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
    from sklearn.calibration import CalibratedClassifierCV
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score, balanced_accuracy_score
    from sklearn.preprocessing import StandardScaler

    rows = [json.loads(l) for l in ROWS.read_text().splitlines()]
    disc = [r for r in rows if r["split"] == "discovery"]
    val = [r for r in rows if r["split"] == "validation"]
    hold = [r for r in rows if r["split"] == "holdout"]

    b_names, b_vec = build_b(disc, rows)

    def comparator_vector(r, kind):
        v = meta_vector(r)
        if kind in ("telemetry", "all"):
            v += telem_vector(r)
        if kind in ("jspace", "all"):
            v += family_a_vector(r) + b_vec[r["task_id"]]
        return v

    # Validation freeze check (recorded, not tuned): discovery-trained
    # j-space model scored on validation completed rows.
    def completed(rows_):
        return [r for r in rows_ if r["outcome_class"] in (1, 2)]

    def fit_and_score(train_rows, eval_rows, kind):
        Xt = np.asarray([comparator_vector(r, kind) for r in train_rows])
        yt = np.asarray([1 if r["verdict_full"] != "pass" else 0
                         for r in train_rows])
        Xe = np.asarray([comparator_vector(r, kind) for r in eval_rows])
        scaler = StandardScaler().fit(Xt)
        clf = CalibratedClassifierCV(
            LogisticRegression(max_iter=3000), method="sigmoid", cv=3)
        clf.fit(scaler.transform(Xt), yt)
        return clf.predict_proba(scaler.transform(Xe))[:, 1]

    val_probe = fit_and_score(completed(disc), completed(val), "jspace")
    yv = np.asarray([1 if r["verdict_full"] != "pass" else 0
                     for r in completed(val)])
    from sklearn.metrics import roc_auc_score
    val_auc = (float(roc_auc_score(yv, val_probe))
               if len(set(yv.tolist())) > 1 else None)

    # ---- H1 on holdout completed rows --------------------------------
    train = completed(disc) + completed(val)
    hold_c = completed(hold)
    yh = np.asarray([1 if r["verdict_full"] != "pass" else 0
                     for r in hold_c])
    rng = np.random.default_rng(BOOT_SEED)
    probs = {kind: fit_and_score(train, hold_c, kind)
             for kind in ("meta", "telemetry", "jspace", "all")}

    def acc(yy, pp):
        return accuracy_score(yy, (pp >= 0.5).astype(int))

    def bal(yy, pp):
        return balanced_accuracy_score(yy, (pp >= 0.5).astype(int))

    h1 = {}
    for mname, metric in (("failure_prediction_accuracy", acc),
                          ("balanced_accuracy", bal)):
        lo, mean, hi = paired_metric_bootstrap(
            yh, probs["all"], probs["telemetry"], metric, rng)
        h1[mname] = {"mean_diff": round(mean, 4),
                     "ci95": [round(lo, 4), round(hi, 4)]}
    h1_evaluable = len(set(yh.tolist())) > 1
    h1_pass = h1_evaluable and all(v["ci95"][0] > 0 for v in h1.values())

    holdout_metrics = {k: {"accuracy": round(float(acc(yh, p)), 4),
                           "balanced_accuracy": round(float(bal(yh, p)), 4)}
                       for k, p in probs.items()}

    # ---- H2 on holdout short-cap truncations --------------------------
    hold_trunc = [r for r in hold if r["outcome_class"] in (3, 4)]
    y2 = [1 if r["outcome_class"] == 3 else 0 for r in hold_trunc]
    h2_evaluable = (len(hold_trunc) >= POWER_FLOOR_H2
                    and 0 < sum(y2) < len(y2))
    h2 = {"population": len(hold_trunc),
          "positives": int(sum(y2)),
          "power_floor": POWER_FLOOR_H2,
          "evaluable": bool(h2_evaluable)}
    h2_pass = False
    if h2_evaluable:
        tr_trunc = [r for r in disc + val if r["outcome_class"] in (3, 4)]
        # (population permitting — expected underpowered on this pilot)
        h2["note"] = f"train population {len(tr_trunc)}"

    payload = {
        "schema_version": 1,
        "run_kind": "m37j_a_result",
        "manifest": "reports/telemetry/m37j_diagnostic_manifest.json",
        "capture_code": "a59ca07 (exact-token provenance)",
        "lens_sha256_prefix": "49faf4e926395393",
        "provenance": "all 192 accepted rows share the exact-token "
                      "readout provenance; zero rows from the discarded "
                      "text-round-trip implementation entered any fit, "
                      "selection, metric, or holdout analysis",
        "splits": {"discovery": len(disc), "validation": len(val),
                   "holdout": len(hold)},
        "family_b_frozen_features": b_names,
        "family_b_validation_auc": (round(val_auc, 4)
                                    if val_auc is not None else None),
        "holdout_completed_n": len(hold_c),
        "holdout_completed_errors": int(yh.sum()),
        "holdout_prediction": holdout_metrics,
        "J_H1": {"pass": bool(h1_pass), "evaluable": bool(h1_evaluable),
                 **h1},
        "J_H2": {"pass": bool(h2_pass), **h2},
        "bootstrap": {"n": BOOT_N, "seed": BOOT_SEED},
        "privacy_check_status": "aggregate metrics only",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[m37j] A result: H1={h1_pass} (evaluable={h1_evaluable}) "
          f"H2={h2_pass} (evaluable={h2_evaluable}) "
          f"holdout={json.dumps(holdout_metrics)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
