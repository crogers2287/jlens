#!/usr/bin/env python3
"""Safe non-interactive review CLI for the M8 shadow-outcome queue.

Sets outcome / review_meta fields on ONE queue record (by --prompt-id) from
EXPLICIT flags a HUMAN passes. It writes only the fields given, validates the
whole record against schema/shadow_outcome_v1.json, and refuses invalid types,
unknown fields, or an unknown prompt_id. It NEVER auto-fills or guesses a value.

CLI:
  python src/review_shadow_log.py \
      --queue reports/shadow/review_queue_sample.jsonl \
      --prompt-id tqa_0_c5971ef7b \
      --user-agreed true --reviewer skinny --review-confidence 0.9
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

OUTCOME_BOOL = ["user_agreed", "was_wrong", "needed_retrieval", "needed_checker"]


def _tri(v):
    """'true'/'false' -> bool; anything else is a CLI error (no guessing)."""
    if v is None:
        return None
    s = str(v).strip().lower()
    if s == "true":
        return True
    if s == "false":
        return False
    raise SystemExit(f"[jlens] invalid boolean {v!r} (use true|false)")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--queue", required=True)
    ap.add_argument("--prompt-id", required=True)
    ap.add_argument("--schema", default="schema/shadow_outcome_v1.json")
    for f in OUTCOME_BOOL:
        ap.add_argument(f"--{f.replace('_', '-')}", default=None,
                        help="true|false (human judgment; omit to leave unreviewed)")
    ap.add_argument("--notes", default=None)
    ap.add_argument("--reviewer", default=None)
    ap.add_argument("--reviewed-at", default=None, help="placeholder string")
    ap.add_argument("--review-source", default=None)
    ap.add_argument("--review-confidence", type=float, default=None)
    ap.add_argument("--dry-run", action="store_true",
                    help="print the updated record but do not write the file")
    args = ap.parse_args(argv)

    from jsonschema import Draft7Validator
    validator = Draft7Validator(json.loads(Path(args.schema).read_text()))

    qpath = Path(args.queue)
    records = [json.loads(l) for l in open(qpath, encoding="utf-8") if l.strip()]
    idx = next((i for i, r in enumerate(records)
                if r.get("prompt_id") == args.prompt_id), None)
    if idx is None:
        raise SystemExit(f"[jlens] unknown prompt_id {args.prompt_id!r} in {qpath}")

    rec = records[idx]
    # apply ONLY the flags the human passed (leave the rest as-is / null)
    for f in OUTCOME_BOOL:
        v = getattr(args, f)
        if v is not None:
            rec["outcome"][f] = _tri(v)
    if args.notes is not None:
        rec["outcome"]["notes"] = args.notes
    for f in ("reviewer", "review_source"):
        v = getattr(args, f)
        if v is not None:
            rec["review_meta"][f] = v
    if args.reviewed_at is not None:
        rec["review_meta"]["reviewed_at"] = args.reviewed_at
    if args.review_confidence is not None:
        rec["review_meta"]["review_confidence"] = args.review_confidence

    errs = list(validator.iter_errors(rec))
    if errs:
        raise SystemExit(f"[jlens] REFUSE: updated record invalid — {errs[0].message}")

    if args.dry_run:
        print(json.dumps(rec, indent=1))
        print("[jlens] dry-run: validated, NOT written.")
        return 0

    records[idx] = rec
    with qpath.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r) + "\n")
    print(f"[jlens] reviewed {args.prompt_id} (fields set + validated). "
          f"reviewer={rec['review_meta']['reviewer']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
