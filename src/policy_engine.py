#!/usr/bin/env python3
"""jlens PolicyEngine v0 — ADVISORY / SHADOW risk scorer.

Fits the two M5-covered prototype heads (answerable_from_memory,
unsupported_or_hallucinated) from the benchmark join table, then scores a
feature row into an advisory recommendation. It RECOMMENDS and (via
risk_runtime) LOGS; it NEVER blocks, executes, or gates a real action.
Prototype thresholds only — final/production stays gold/audit gated.

Usage:
  from policy_engine import PolicyEngine
  eng = PolicyEngine()                       # loads config + fits heads
  result = eng.score(feature_row_dict)       # {prompt_id, level, scores,
                                             #  recommended_action, explanation}
"""
from __future__ import annotations

import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
import sys
sys.path.insert(0, str(_ROOT / "src"))
from train_risk_heads import _flatten_features  # reuse M5 feature vectorizer

DRIFT_KEYS = {"drift_from_prefill_signature", "drift_from_previous_token",
              "drift_from_prefill_weighted", "drift_from_previous_token_weighted"}


class PolicyEngine:
    def __init__(self, config_path=None, features_path=None, labels_dir=None):
        self.config = self.load_config(
            config_path or _ROOT / "config/policy_engine_v0.json")
        self.features_path = Path(
            features_path or _ROOT / "reports/features/benchmark_m5_features.jsonl")
        self.labels_dir = Path(labels_dir or _ROOT / "data/labels/benchmark")
        self.scored = self.config["scored_labels"]
        self._fit()

    @staticmethod
    def load_config(path):
        return json.loads(Path(path).read_text())

    def _fit(self):
        """Fit one calibrated-ish logreg head per scored label from the M5 join."""
        import numpy as np
        from sklearn.linear_model import LogisticRegression

        rows = [json.loads(l) for l in open(self.features_path, encoding="utf-8")]
        # guard: features never carry drift
        for r in rows:
            assert not (DRIFT_KEYS & _all_keys(r)), "drift feature in feature row"
        feats = {r["prompt_id"]: np.array(_flatten_features(r)[0], dtype=float)
                 for r in rows}
        labels = {}
        for fp in sorted(self.labels_dir.glob("*.jsonl")):
            for line in open(fp, encoding="utf-8"):
                o = json.loads(line)
                labels[o["prompt_id"]] = o["labels"]

        self.heads = {}
        for L in self.scored:
            ids = [pid for pid in feats
                   if labels.get(pid, {}).get(L) is not None]
            X = np.stack([feats[pid] for pid in ids])
            y = np.array([1 if labels[pid][L] else 0 for pid in ids])
            if len(set(y)) < 2:
                self.heads[L] = None  # can't fit; scores as unknown -> 0.5
                continue
            self.heads[L] = LogisticRegression(max_iter=3000).fit(X, y)
        self._n_features = len(next(iter(feats.values())))

    # -- scoring ----------------------------------------------------------
    def _proba(self, L, x):
        import numpy as np
        head = self.heads.get(L)
        if head is None:
            return 0.5
        return float(head.predict_proba(np.asarray(x).reshape(1, -1))[0, 1])

    def _risk_contribution(self, L, p):
        """Map a label probability to its risk contribution per config."""
        spec = self.config["risk_score"]["components"][L]
        return (1.0 - p) if spec["risk_is"] == "false" else p

    def _level(self, risk):
        for lv in ("critical", "high", "medium", "low"):
            lo, hi = self.config["levels"][lv]
            if lo <= risk < hi:
                return lv
        return "low"

    def score(self, feature_row: dict) -> dict:
        """Advisory recommendation for one feature row. No side effects."""
        x = _flatten_features(feature_row)[0]
        scores, contribs = {}, {}
        for L in self.scored:
            p = self._proba(L, x)
            scores[L] = round(p, 4)
            contribs[L] = self._risk_contribution(L, p)
        driver = max(contribs, key=contribs.get)
        risk = contribs[driver]
        level = self._level(risk)
        action = self.config["level_action_map"][level]
        expl = (f"risk={risk:.2f} (driver: {driver} p={scores[driver]:.2f}) "
                f"-> level={level} -> advise: {action} [SHADOW/advisory]")
        return {
            "prompt_id": feature_row.get("prompt_id"),
            "level": level,
            "scores": scores,
            "risk": round(risk, 4),
            "recommended_action": action,
            "explanation": expl,
        }


def _all_keys(d, acc=None):
    acc = acc if acc is not None else set()
    for k, v in d.items():
        acc.add(k)
        if isinstance(v, dict):
            _all_keys(v, acc)
    return acc


if __name__ == "__main__":
    # smoke: score the first M5 feature row
    eng = PolicyEngine()
    row = json.loads(open(eng.features_path, encoding="utf-8").readline())
    print(json.dumps(eng.score(row), indent=1))
