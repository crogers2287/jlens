#!/usr/bin/env python3
"""Read-only action router (M16).

Turns an auto_outcome candidate into a PLANNED action_record (schema
action_record_v1). It NEVER executes anything by default — it only records what a
verifier signal SUGGESTS. Checker actions route ONLY to an approved deterministic
checker list; if none applies, the action is marked "skipped". For current-info
tasks the retrieval signal always yields a retrieval_needed record — the base
model answer is never treated as sufficient.

Evidence is hashed; no raw task/output text ever enters an action record.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import verifiers as VZ  # evidence_hash

# Only these deterministic checkers may back a checker_needed action.
APPROVED_CHECKERS = {"math_checker", "json_object_check", "numeric_tolerant_check"}


def route(record: dict) -> dict:
    """Derive a PLANNED action_record from an auto_outcome record. Read-only."""
    pid = record.get("prompt_id", "")
    auto = record.get("auto_outcome", {}) or {}
    vnames = set(auto.get("verifier_names", []) or [])
    conf = auto.get("verifier_confidence")

    if auto.get("auto_needed_retrieval") is True:
        action_type, reason, src, status = (
            "retrieval_needed", "needs_fresh_or_grounded_info",
            "retrieval_required_heuristic", "planned")
    elif auto.get("auto_needed_checker") is True:
        approved = sorted(vnames & APPROVED_CHECKERS)
        if approved:
            action_type, reason, src, status = (
                "checker_needed", "approved_deterministic_checker_available",
                approved[0], "planned")
        else:
            # a checker is wanted but none is approved for this task -> do nothing
            action_type, reason, src, status = (
                "checker_needed", "no_approved_checker_available", None, "skipped")
    elif auto.get("escalate_for_review") is True:
        action_type, reason, src, status = (
            "review_needed", "low_confidence_or_contradiction_escalation", None, "planned")
    else:
        action_type, reason, src, status = ("no_action", "clean", None, "planned")

    return {
        "task_id": pid,
        "action_type": action_type,
        "reason_code": reason,
        "source_verifier": src,
        "confidence": conf,
        "status": status,
        "evidence_hash": VZ.evidence_hash(pid, action_type, reason, *sorted(vnames)),
    }


def route_all(records):
    return [route(r) for r in records]


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    records = [json.loads(l) for l in open(args.inp, encoding="utf-8") if l.strip()]
    actions = route_all(records)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for a in actions:
            fh.write(json.dumps(a) + "\n")
    from collections import Counter
    dist = Counter(a["action_type"] for a in actions)
    print(f"[jlens] routed {len(actions)} action records (read-only) -> {out} | {dict(dist)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
