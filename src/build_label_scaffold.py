#!/usr/bin/env python3
"""Build the M3 risk-label SCAFFOLD: one all-null record per prompt.

Emits unlabeled seed rows (labeler=null, every one of the 10 labels=null) for
the union of prompt ids in data/prompts.jsonl and the r4 decode export. NEVER
invents a label value — those are filled only by a human labeler later. Every
emitted row is validated against schema/risk_labels_v1.json.

CLI:
  python src/build_label_scaffold.py \
      --prompts data/prompts.jsonl \
      --decode reports/schema/r4_decode.jsonl \
      --schema schema/risk_labels_v1.json \
      --out data/labels/risk_labels_seed.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

LABELS = [
    "answerable_from_memory", "needs_current_info", "needs_exact_citation",
    "needs_math_verification", "needs_code_execution", "needs_user_file_context",
    "high_stakes_or_sensitive", "context_attack_present",
    "unsupported_or_hallucinated", "format_or_tool_mode_shift",
]


def collect_prompt_ids(prompts_path, decode_path) -> list[str]:
    ids = set()
    if prompts_path and Path(prompts_path).exists():
        for line in open(prompts_path, encoding="utf-8"):
            line = line.strip()
            if line:
                ids.add(json.loads(line)["id"])
    if decode_path and Path(decode_path).exists():
        for line in open(decode_path, encoding="utf-8"):
            line = line.strip()
            if line:
                ids.add(json.loads(line)["prompt_id"])
    return sorted(ids)


def scaffold_record(prompt_id: str) -> dict:
    # all-null: unlabeled. labels stay null until a HUMAN sets them.
    return {
        "schema_version": 1,
        "prompt_id": prompt_id,
        "labeler": None,
        "labels": {k: None for k in LABELS},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--prompts", default="data/prompts.jsonl")
    ap.add_argument("--decode", default="reports/schema/r4_decode.jsonl")
    ap.add_argument("--schema", default="schema/risk_labels_v1.json")
    ap.add_argument("--out", default="data/labels/risk_labels_seed.jsonl")
    args = ap.parse_args(argv)

    from jsonschema import Draft7Validator

    schema = json.loads(Path(args.schema).read_text())
    validator = Draft7Validator(schema)

    ids = collect_prompt_ids(args.prompts, args.decode)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for pid in ids:
            rec = scaffold_record(pid)
            errs = list(validator.iter_errors(rec))
            if errs:
                raise SystemExit(f"[jlens] scaffold record for {pid} invalid: "
                                 f"{errs[0].message}")
            fh.write(json.dumps(rec) + "\n")
            n += 1
    print(f"[jlens] wrote {n} all-null scaffold records -> {out} "
          f"(labeler=null, all labels=null; awaiting human labeling)")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
