#!/usr/bin/env python3
"""jlens risk-runtime CLI — score feature rows and SHADOW-LOG the advisory.

Wraps PolicyEngine v0. For each feature row it prints the advisory result and
APPENDS one shadow-log entry to reports/shadow/shadow_log.jsonl. Shadow logging
only records — it never changes behavior, never blocks, never executes. The
outcome_note field is null, reserved for later human annotation.

No wall-clock calls (Date/random are unavailable in this environment) — the
timestamp is a caller-supplied placeholder (--ts), defaulting to "unset".

CLI:
  python src/risk_runtime.py \
      --features reports/features/benchmark_m5_features.jsonl \
      --log reports/shadow/shadow_log.jsonl [--ts 2026-07-08T00:00:00Z] [--limit N]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from policy_engine import PolicyEngine


def shadow_entry(result: dict, feature_source: str, ts: str) -> dict:
    return {
        "ts_placeholder": ts,
        "prompt_id": result.get("prompt_id"),
        "feature_source": feature_source,
        "scores": result["scores"],
        "level": result["level"],
        "recommended_action": result["recommended_action"],
        "mode": "shadow",
        "outcome_note": None,          # for later human annotation
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--features",
                    default="reports/features/benchmark_m5_features.jsonl")
    ap.add_argument("--log", default="reports/shadow/shadow_log.jsonl")
    ap.add_argument("--config", default=None)
    ap.add_argument("--ts", default="unset",
                    help="timestamp placeholder recorded in the shadow log")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    eng = PolicyEngine(config_path=args.config)
    rows = [json.loads(l) for l in open(args.features, encoding="utf-8")]
    if args.limit:
        rows = rows[:args.limit]

    log = Path(args.log)
    log.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with log.open("a", encoding="utf-8") as fh:
        for r in rows:
            res = eng.score(r)
            print(f"[jlens][SHADOW] {res['prompt_id']}: {res['level']} "
                  f"-> {res['recommended_action']}  ({res['explanation']})")
            fh.write(json.dumps(shadow_entry(res, args.features, args.ts)) + "\n")
            n += 1
    print(f"[jlens] shadow-logged {n} advisories -> {log} (mode=shadow; "
          "advisory only, no actions taken)")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
