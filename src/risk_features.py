#!/usr/bin/env python3
"""Extract per-prompt risk-head features from the r4 decode export.

Feature set is the M2-validated KEEP list ONLY. Drift fields are DELIBERATELY
excluded (M2 finding #18: routing drift, unweighted and weighted, does not track
output confidence). The extractor asserts no drift key ever lands in a row.

Feature groups (per prompt, aggregated over its decode tokens):
  prefill domain prediction + margin      (reuse r3 sidecar head)
  entropy_final_logits stats              (mean / max / std)
  selected_token_prob stats               (mean / min / std)
  topk_mass_or_margin stats               (mean / min / std; from v3 export)
  windowed decode-domain-shift stats      (off-prefill-domain frac, switch count)
  low-confidence / high-entropy spike counts

CLI:
  python src/risk_features.py \
      --train reports/schema/r3.jsonl \
      --decode reports/schema/r4_decode_weighted.jsonl \
      --captures data/captures/qwen3_6_35b_a3b_r4_decode \
      --out reports/features/r4_risk_features.jsonl
"""
from __future__ import annotations

import argparse
import json
import statistics as st
from pathlib import Path

import numpy as np

from decode_domain_shift import (_sig_from_layers, load_train, prefill_sigs)

DRIFT_KEYS = {"drift_from_prefill_signature", "drift_from_previous_token",
              "drift_from_prefill_weighted", "drift_from_previous_token_weighted"}
LOW_CONF_TAU = 0.5
HIGH_ENT_TAU = 1.0


def _stats(xs, lo=False):
    xs = [x for x in xs if x is not None]
    if not xs:
        return {"mean": None, "extreme": None, "std": None}
    return {"mean": round(st.mean(xs), 6),
            "extreme": round(min(xs) if lo else max(xs), 6),
            "std": round(st.pstdev(xs), 6)}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--train", default="reports/schema/r3.jsonl")
    ap.add_argument("--decode", default="reports/schema/r4_decode_weighted.jsonl")
    ap.add_argument("--captures", default="data/captures/qwen3_6_35b_a3b_r4_decode")
    ap.add_argument("--out", default="reports/features/r4_risk_features.jsonl")
    args = ap.parse_args(argv)

    from sklearn.linear_model import LogisticRegression

    # r3 sidecar domain head
    Xtr, ytr = load_train(args.train)
    clf = LogisticRegression(max_iter=3000, C=1.0)
    clf.fit(Xtr, ytr)
    classes = list(clf.classes_)
    ne = Xtr.shape[1] // 40

    # group decode rows by prompt
    by_prompt = {}
    for line in open(args.decode, encoding="utf-8"):
        o = json.loads(line)
        by_prompt.setdefault(o["prompt_id"], []).append(o)
    for pid in by_prompt:
        by_prompt[pid].sort(key=lambda r: r["generated_token_index"])

    pref = prefill_sigs(args.captures, ne, top_k=8)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for pid, toks in sorted(by_prompt.items()):
            true_dom = toks[0]["domain"]
            # prefill domain prediction + margin
            pref_proba = clf.predict_proba(pref[pid][None])[0]
            srt = np.sort(pref_proba)
            pref_pred = classes[int(pref_proba.argmax())]
            pref_margin = float(srt[-1] - srt[-2])

            ent = [t["entropy_final_logits"] for t in toks]
            sp = [t["selected_token_prob"] for t in toks]
            mass = [t.get("topk_mass_or_margin") for t in toks]

            # windowed decode domain-shift (per-token predicted domain)
            tok_sigs = np.stack([
                _sig_from_layers([L["topk_experts"] for L in t["router_layers"]], ne)
                for t in toks])
            dpred = [classes[i] for i in clf.predict_proba(tok_sigs).argmax(1)]
            offdomain_frac = round(sum(p != true_dom for p in dpred) / len(dpred), 6)
            switches = sum(1 for i in range(1, len(dpred)) if dpred[i] != dpred[i - 1])

            row = {
                "prompt_id": pid,
                "domain": true_dom,
                "n_decode_tokens": len(toks),
                "prefill_pred_domain": pref_pred,
                "prefill_pred_margin": round(pref_margin, 6),
                "prefill_pred_correct": int(pref_pred == true_dom),
                "entropy_final": _stats(ent),
                "selected_token_prob": _stats(sp, lo=True),
                "topk_mass": _stats(mass, lo=True),
                "decode_offdomain_frac": offdomain_frac,
                "decode_domain_switches": switches,
                "low_conf_spike_count": sum(1 for x in sp if x < LOW_CONF_TAU),
                "high_entropy_spike_count": sum(1 for x in ent if x > HIGH_ENT_TAU),
            }
            # HARD GUARD: no drift feature may ever enter a feature row.
            leaked = DRIFT_KEYS & set(_flatten_keys(row))
            assert not leaked, f"drift feature leaked into row: {leaked}"
            fh.write(json.dumps(row) + "\n")
            n += 1
    print(f"[jlens] wrote {n} feature rows -> {out} (drift excluded)")
    return 0 if n else 1


def _flatten_keys(d, prefix=""):
    keys = []
    for k, v in d.items():
        keys.append(k)
        if isinstance(v, dict):
            keys.extend(_flatten_keys(v, k))
    return keys


if __name__ == "__main__":
    raise SystemExit(main())
