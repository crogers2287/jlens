#!/usr/bin/env python3
"""Build a local escalation review queue from an Agents-A1 run log (M11).

Selects ONLY records the autonomous run flagged (auto_outcome.escalate_for_review
== true) and writes them to a LOCAL, gitignored review queue for a human. The
auto_outcome candidate is KEPT so the reviewer sees why it escalated; the HUMAN
outcome / review_meta fields are forced null (the reviewer fills them — the run
never does). auto_outcome is a candidate, not gold.

The queue is auto_outcome_v1-shaped. A human sets the `outcome` booleans during
review (see docs/SHADOW_OUTCOME_REVIEW.md); `null` = unreviewed, never false.

CLI:
  python src/make_escalation_review_queue.py \
      --in reports/shadow/private/agents_a1_run_local.jsonl \
      --out reports/shadow/private/agents_a1_review_local.jsonl        # gitignored
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

NULL_OUT = {"user_agreed": None, "was_wrong": None, "needed_retrieval": None,
            "needed_checker": None, "notes": None}
NULL_META = {"reviewer": None, "reviewed_at": None, "review_source": None,
             "review_confidence": None}


def to_review_record(rec: dict) -> dict:
    """Keep the record + auto_outcome; force HUMAN fields null for review."""
    out = dict(rec)
    out["outcome"] = dict(NULL_OUT)       # human fills these — never the run
    out["review_meta"] = dict(NULL_META)
    return out


def build(records):
    return [to_review_record(r) for r in records
            if r.get("auto_outcome", {}).get("escalate_for_review") is True]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)

    records = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    queue = build(records)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in queue:
            fh.write(json.dumps(r) + "\n")
    print(f"[jlens] escalation review queue: {len(queue)}/{len(records)} escalated "
          f"records (human outcome fields null) -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
