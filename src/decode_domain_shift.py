#!/usr/bin/env python3
"""Decode domain-shift probe: does routing drift DOMAINS during generation?

Trains the r3 router sidecar domain head (prompt-level prefill signatures,
schema v1 JSONL) and applies it to each decode-step routing signature (schema
v2/v3 JSONL) plus each prompt's r4 prefill signature. Reports, per prompt and
in aggregate:
  prefill_label                     (true domain)
  prefill_predicted_domain          (head on the prompt's prefill signature)
  prefill_label_vs_decode_pred_disagree   (frac decode tokens pred != true)
  prefill_pred_vs_decode_pred_disagree     (frac decode tokens pred != prefill pred)
  decode_domain_confidence          (mean max predict_proba over decode tokens)
  decode_domain_margin              (mean top1-top2 proba)
  number_of_domain_switches         (consecutive predicted-domain changes)
  first_domain_switch_token_index   (first index of a switch, or null)

CLI:
  python src/decode_domain_shift.py \
      --train reports/schema/r3.jsonl \
      --decode reports/schema/r4_decode.jsonl \
      --captures data/captures/qwen3_6_35b_a3b_r4_decode \
      --json reports/qwen3_6_35b_a3b_r4_domain_shift.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

from load_captures import iter_captures


def _sig_from_layers(layers, num_experts):
    """Per-layer 256 expert-usage histogram (count-normalized) concatenated.
    `layers` is a list of topk_experts lists (one per layer)."""
    vecs = []
    for experts in layers:
        h = np.zeros(num_experts, dtype=np.float32)
        for e in experts:
            h[e] += 1.0
        s = h.sum()
        if s:
            h /= s
        vecs.append(h)
    return np.concatenate(vecs)


def load_train(v1_jsonl):
    """r3 prefill signatures (schema v1): per prompt, layers[].topk_experts."""
    X, y = [], []
    for line in open(v1_jsonl, encoding="utf-8"):
        o = json.loads(line)
        ne = o["num_experts"]
        # v1 topk_experts is [tokens][k]; flatten per layer into one usage hist
        layers = [[e for row in L["topk_experts"] for e in row] for L in o["layers"]]
        X.append(_sig_from_layers(layers, ne))
        y.append(o["domain"])
    return np.stack(X), np.array(y)


def decode_token_sigs(decode_jsonl):
    """Per (prompt, token) decode signature from schema v2/v3 router_layers."""
    per_prompt = defaultdict(list)  # prompt_id -> list[(idx, domain, sig)]
    for line in open(decode_jsonl, encoding="utf-8"):
        o = json.loads(line)
        ne = o["num_experts"]
        layers = [L["topk_experts"] for L in o["router_layers"]]
        sig = _sig_from_layers(layers, ne)
        per_prompt[o["prompt_id"]].append(
            (o["generated_token_index"], o["domain"], sig))
    for pid in per_prompt:
        per_prompt[pid].sort(key=lambda t: t[0])
    return per_prompt


def prefill_sigs(captures_dir, num_experts, top_k):
    """r4 prefill signature per prompt, featurized like the decode tokens."""
    import torch
    out = {}
    for name, cap in iter_captures(captures_dir):
        layers = []
        for logits in cap["router_logits"]:
            lg = logits.float()
            if lg.dim() == 1:
                lg = lg.unsqueeze(0)
            idx = torch.topk(lg, k=min(top_k, lg.shape[-1]), dim=-1).indices
            layers.append(idx.flatten().tolist())
        out[Path(name).stem] = _sig_from_layers(layers, num_experts)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--train", required=True, help="r3 v1 JSONL (prefill sigs)")
    ap.add_argument("--decode", required=True, help="r4 decode JSONL (v2/v3)")
    ap.add_argument("--captures", required=True, help="r4 capture dir (prefill)")
    ap.add_argument("--top-k", type=int, default=8)
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    from sklearn.linear_model import LogisticRegression

    Xtr, ytr = load_train(args.train)
    clf = LogisticRegression(max_iter=3000, C=1.0)
    clf.fit(Xtr, ytr)
    classes = list(clf.classes_)
    ne = Xtr.shape[1] // 40  # 10240 / 40 layers

    per_prompt = decode_token_sigs(args.decode)
    pref = prefill_sigs(args.captures, ne, args.top_k)

    prompt_reports = []
    for pid, toks in sorted(per_prompt.items()):
        true_dom = toks[0][1]
        pref_pred = clf.predict(pref[pid][None])[0] if pid in pref else None
        sigs = np.stack([t[2] for t in toks])
        proba = clf.predict_proba(sigs)
        preds = [classes[i] for i in proba.argmax(1)]
        srt = np.sort(proba, axis=1)
        conf = float(srt[:, -1].mean())
        margin = float((srt[:, -1] - srt[:, -2]).mean())
        switches = sum(1 for i in range(1, len(preds)) if preds[i] != preds[i - 1])
        first_switch = next((i for i in range(1, len(preds))
                             if preds[i] != preds[i - 1]), None)
        prompt_reports.append({
            "prompt_id": pid,
            "prefill_label": true_dom,
            "prefill_predicted_domain": pref_pred,
            "n_decode_tokens": len(preds),
            "prefill_label_vs_decode_pred_disagree": round(
                sum(p != true_dom for p in preds) / len(preds), 4),
            "prefill_pred_vs_decode_pred_disagree": (None if pref_pred is None
                else round(sum(p != pref_pred for p in preds) / len(preds), 4)),
            "decode_domain_confidence": round(conf, 4),
            "decode_domain_margin": round(margin, 4),
            "number_of_domain_switches": switches,
            "first_domain_switch_token_index": first_switch,
            "decode_pred_domain_counts": dict(Counter(preds)),
        })

    agg = {
        "n_prompts": len(prompt_reports),
        "mean_label_vs_decode_disagree": round(float(np.mean(
            [p["prefill_label_vs_decode_pred_disagree"] for p in prompt_reports])), 4),
        "mean_prefillpred_vs_decode_disagree": round(float(np.mean(
            [p["prefill_pred_vs_decode_pred_disagree"] for p in prompt_reports
             if p["prefill_pred_vs_decode_pred_disagree"] is not None])), 4),
        "mean_decode_domain_confidence": round(float(np.mean(
            [p["decode_domain_confidence"] for p in prompt_reports])), 4),
        "mean_decode_domain_margin": round(float(np.mean(
            [p["decode_domain_margin"] for p in prompt_reports])), 4),
        "mean_domain_switches": round(float(np.mean(
            [p["number_of_domain_switches"] for p in prompt_reports])), 4),
        "prefill_pred_matches_label": sum(
            p["prefill_predicted_domain"] == p["prefill_label"]
            for p in prompt_reports),
    }
    print(f"[jlens] domain-shift probe over {agg['n_prompts']} prompts")
    print(f"  prefill pred matches label: {agg['prefill_pred_matches_label']}"
          f"/{agg['n_prompts']}")
    print(f"  mean label-vs-decode disagree: {agg['mean_label_vs_decode_disagree']}")
    print(f"  mean prefillpred-vs-decode disagree: "
          f"{agg['mean_prefillpred_vs_decode_disagree']}")
    print(f"  mean decode domain confidence: {agg['mean_decode_domain_confidence']}"
          f"  margin: {agg['mean_decode_domain_margin']}")
    print(f"  mean domain switches/prompt: {agg['mean_domain_switches']}")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(
            {"aggregate": agg, "by_prompt": prompt_reports}, indent=1))
        print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
