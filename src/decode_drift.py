#!/usr/bin/env python3
"""DecodeGuard drift analysis over a decode schema JSONL (schema v2/v3).

Turns per-generated-token routing telemetry into a summary report: drift
distributions, entropy/confidence distributions, per-domain and per-token-index
summaries, Pearson correlations between drift and output-confidence signals,
and top spike records for manual inspection.

CLI:
  python src/decode_drift.py reports/schema/r4_decode.jsonl \
      --json reports/qwen3_6_35b_a3b_r4_decode_drift.json
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

# Metric keys present on v2 records (+ weighted variants when v3).
BASE_METRICS = ["drift_from_prefill_signature", "drift_from_previous_token",
                "entropy_final_logits", "selected_token_prob"]


def _pearson(a, b):
    pairs = [(x, y) for x, y in zip(a, b) if x is not None and y is not None]
    n = len(pairs)
    if n < 3:
        return None
    ax = [p[0] for p in pairs]
    bx = [p[1] for p in pairs]
    ma, mb = sum(ax) / n, sum(bx) / n
    num = sum((x - ma) * (y - mb) for x, y in pairs)
    da = math.sqrt(sum((x - ma) ** 2 for x in ax))
    db = math.sqrt(sum((y - mb) ** 2 for y in bx))
    return round(num / (da * db), 4) if da and db else None


def _summ(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return None
    n = len(v)
    mean = sum(v) / n
    sd = math.sqrt(sum((x - mean) ** 2 for x in v) / n)
    return {"n": n, "mean": round(mean, 4), "sd": round(sd, 4),
            "min": round(min(v), 4), "max": round(max(v), 4)}


def _spikes(rows, key, n=8, lowest=False):
    keyed = [r for r in rows if r.get(key) is not None]
    keyed.sort(key=lambda r: r[key], reverse=not lowest)
    out = []
    for r in keyed[:n]:
        out.append({
            "prompt_id": r["prompt_id"], "domain": r["domain"],
            "generated_token_index": r["generated_token_index"],
            "generated_token_text": r["generated_token_text"],
            "drift_from_prefill_signature": r.get("drift_from_prefill_signature"),
            "drift_from_previous_token": r.get("drift_from_previous_token"),
            "entropy_final_logits": r.get("entropy_final_logits"),
            "selected_token_prob": r.get("selected_token_prob"),
        })
    return out


def analyze(rows):
    metrics = list(BASE_METRICS)
    for extra in ["drift_from_prefill_weighted", "drift_from_previous_token_weighted"]:
        if any(extra in r for r in rows):
            metrics.append(extra)

    by_domain = defaultdict(list)
    by_index = defaultdict(list)
    for r in rows:
        by_domain[r["domain"]].append(r)
        by_index[r["generated_token_index"]].append(r)

    dp = [r["drift_from_prefill_signature"] for r in rows]
    dv = [r["drift_from_previous_token"] for r in rows]
    en = [r["entropy_final_logits"] for r in rows]
    sp = [r["selected_token_prob"] for r in rows]

    report = {
        "n_records": len(rows),
        "n_prompts": len({r["prompt_id"] for r in rows}),
        "n_domains": len({r["domain"] for r in rows}),
        "distributions": {m: _summ([r.get(m) for r in rows]) for m in metrics},
        "correlations": {
            "drift_prefill_x_entropy": _pearson(dp, en),
            "drift_prefill_x_sel_prob": _pearson(dp, sp),
            "drift_prev_x_entropy": _pearson(dv, en),
            "drift_prev_x_sel_prob": _pearson(dv, sp),
        },
        "by_domain": {
            d: {m: _summ([r.get(m) for r in rs]) for m in metrics}
            for d, rs in sorted(by_domain.items())
        },
        "by_token_index": {
            str(i): {
                "n": len(rs),
                "drift_from_prefill_mean": round(
                    sum(r["drift_from_prefill_signature"] for r in rs) / len(rs), 4),
                "entropy_final_mean": round(
                    sum(r["entropy_final_logits"] for r in rs) / len(rs), 4),
                "sel_prob_mean": round(
                    sum(r["selected_token_prob"] for r in rs) / len(rs), 4),
            }
            for i, rs in sorted(by_index.items())
        },
        "top_spikes": {
            "drift_from_prefill": _spikes(rows, "drift_from_prefill_signature"),
            "drift_from_previous": _spikes(rows, "drift_from_previous_token"),
            "entropy_final_logits": _spikes(rows, "entropy_final_logits"),
            "lowest_selected_token_prob": _spikes(
                rows, "selected_token_prob", lowest=True),
        },
    }
    if "drift_from_prefill_weighted" in metrics:
        report["correlations"]["drift_prefill_weighted_x_entropy"] = _pearson(
            [r.get("drift_from_prefill_weighted") for r in rows], en)
        report["correlations"]["drift_prefill_weighted_x_sel_prob"] = _pearson(
            [r.get("drift_from_prefill_weighted") for r in rows], sp)
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("decode_jsonl")
    ap.add_argument("--json", metavar="PATH", default=None)
    args = ap.parse_args(argv)

    rows = [json.loads(l) for l in open(args.decode_jsonl, encoding="utf-8")
            if l.strip()]
    if not rows:
        print(f"[jlens] no records in {args.decode_jsonl}")
        return 1
    report = analyze(rows)

    d = report["distributions"]
    c = report["correlations"]
    print(f"[jlens] {report['n_records']} tokens, {report['n_prompts']} prompts, "
          f"{report['n_domains']} domains")
    print(f"  drift_prefill {d['drift_from_prefill_signature']}")
    print(f"  drift_prev    {d['drift_from_previous_token']}")
    print(f"  entropy_final {d['entropy_final_logits']}")
    print(f"  sel_prob      {d['selected_token_prob']}")
    print(f"  corr drift_prefill x entropy={c['drift_prefill_x_entropy']} "
          f"x sel_prob={c['drift_prefill_x_sel_prob']}")
    print(f"  corr drift_prev    x entropy={c['drift_prev_x_entropy']} "
          f"x sel_prob={c['drift_prev_x_sel_prob']}")

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=1))
        print(f"[jlens] report written: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
