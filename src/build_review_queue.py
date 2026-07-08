#!/usr/bin/env python3
"""Build an all-null review queue from shadow records (M8).

Reads shadow records (reports/shadow/realuse_sample.jsonl and/or
shadow_log.jsonl) and emits each as a shadow_outcome_v1 record with EVERY
outcome + review_meta field null (UNREVIEWED). It NEVER sets an outcome value —
a human does that later via review_shadow_log.py. Every emitted record is
validated against schema/shadow_outcome_v1.json.

CLI:
  python src/build_review_queue.py \
      --inputs reports/shadow/realuse_sample.jsonl \
      --schema schema/shadow_outcome_v1.json \
      --out reports/shadow/review_queue_sample.jsonl
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

NULL_OUTCOME = {"user_agreed": None, "was_wrong": None, "needed_retrieval": None,
                "needed_checker": None, "notes": None}
NULL_META = {"reviewer": None, "reviewed_at": None, "review_source": None,
             "review_confidence": None}


def to_review_record(shadow: dict) -> dict:
    """Shadow record -> unreviewed shadow_outcome_v1 record (all outcomes null)."""
    return {
        "prompt_id": shadow.get("prompt_id"),
        "model": shadow.get("model"),
        "feature_source": shadow.get("feature_source"),
        "prompt_preview": shadow.get("prompt_preview"),
        "output_preview": shadow.get("output_preview"),
        "policy": shadow.get("policy"),
        "policy_note": shadow.get("policy_note"),
        "mode": shadow.get("mode", "shadow"),
        "outcome": dict(NULL_OUTCOME),      # NEVER pre-filled
        "review_meta": dict(NULL_META),     # NEVER pre-filled
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--inputs", nargs="+",
                    default=["reports/shadow/realuse_sample.jsonl"])
    ap.add_argument("--schema", default="schema/shadow_outcome_v1.json")
    ap.add_argument("--out", default="reports/shadow/review_queue_sample.jsonl")
    args = ap.parse_args(argv)

    from jsonschema import Draft7Validator
    validator = Draft7Validator(json.loads(Path(args.schema).read_text()))

    files = []
    for pat in args.inputs:
        files.extend(sorted(glob.glob(pat)) if any(c in pat for c in "*?[")
                     else [pat])
    seen = set()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    total = reviewed = 0
    with out.open("w", encoding="utf-8") as fh:
        for fp in files:
            if not Path(fp).exists():
                continue
            for line in open(fp, encoding="utf-8"):
                line = line.strip()
                if not line:
                    continue
                rec = to_review_record(json.loads(line))
                key = rec["prompt_id"]
                if key in seen:
                    continue
                seen.add(key)
                errs = list(validator.iter_errors(rec))
                if errs:
                    raise SystemExit(f"[jlens] queued record {key} invalid: "
                                     f"{errs[0].message}")
                # sanity: it MUST be unreviewed
                assert all(v is None for v in rec["outcome"].values())
                assert all(v is None for v in rec["review_meta"].values())
                fh.write(json.dumps(rec) + "\n")
                total += 1
    print(f"[jlens] review queue: reviewed={reviewed}/{total} (all UNREVIEWED) "
          f"-> {out}")
    return 0 if total else 1


if __name__ == "__main__":
    raise SystemExit(main())
