#!/usr/bin/env python3
"""Convert FEVER (benchmark-gold) → jlens risk_labels_v2 JSONL.

FEVER is human-annotated claim verification against Wikipedia evidence
(SUPPORTS / REFUTES / NOT ENOUGH INFO). Source: copenlu/fever_gold_evidence
(CC-BY-SA-3.0), chosen over SciFact (CC-BY-NC) for redistribution-friendliness.

Mapping (evidence-grounded claim verification):
  - every verifiable claim requires cited evidence -> needs_exact_citation = true
  - REFUTES  -> unsupported_or_hallucinated = true   (claim is false vs evidence)
  - SUPPORTS -> unsupported_or_hallucinated = false
  - NOT ENOUGH INFO -> unsupported_or_hallucinated = null (can't judge)
All other labels stay null (NULL = UNKNOWN, never guessed).

Pulls raw jsonl via huggingface_hub (no `datasets` install); raw stays under
data/raw/ (gitignored). Only the converted JSONL is committed.

CLI:
  python src/convert_fever.py \
      --schema schema/risk_labels_v2.json \
      --out data/labels/benchmark/fever.jsonl [--limit N]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

REPO = "copenlu/fever_gold_evidence"
FILE = "valid.jsonl"
SPLIT = "valid"
LICENSE = "CC-BY-SA-3.0"
TEN = [
    "answerable_from_memory", "needs_current_info", "needs_exact_citation",
    "needs_math_verification", "needs_code_execution", "needs_user_file_context",
    "high_stakes_or_sensitive", "context_attack_present",
    "unsupported_or_hallucinated", "format_or_tool_mode_shift",
]
# FEVER label -> unsupported_or_hallucinated
UNSUP = {"REFUTES": True, "SUPPORTS": False, "NOT ENOUGH INFO": None}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schema", default="schema/risk_labels_v2.json")
    ap.add_argument("--out", default="data/labels/benchmark/fever.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    from huggingface_hub import hf_hub_download
    from jsonschema import Draft7Validator

    validator = Draft7Validator(json.loads(Path(args.schema).read_text()))
    raw = Path("data/raw"); raw.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(REPO, FILE, repo_type="dataset", local_dir=str(raw))

    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    if args.limit:
        rows = rows[:args.limit]

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    bal = {"needs_exact_citation": Counter(),
           "unsupported_or_hallucinated": Counter()}
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            src_label = r.get("label")
            labels = {k: None for k in TEN}
            # verifiable claims are evidence-grounded -> need citation
            labels["needs_exact_citation"] = (
                True if r.get("verifiable") == "VERIFIABLE" else None)
            labels["unsupported_or_hallucinated"] = UNSUP.get(src_label)
            rec = {
                "schema_version": 2,
                "prompt_id": f"fever_{r.get('id')}",
                "labeler": None,
                "labels": labels,
                "source_dataset": "FEVER",
                "source_split": SPLIT,
                "source_record_id": str(r.get("id")),
                "source_label": src_label,
                "source_license": LICENSE,
                "label_source": "benchmark_gold",
                "label_confidence": 1.0,
                "non_commercial": False,
            }
            errs = list(validator.iter_errors(rec))
            if errs:
                raise SystemExit(f"[jlens] {rec['prompt_id']} invalid: {errs[0].message}")
            fh.write(json.dumps(rec) + "\n")
            for L in bal:
                bal[L][labels[L]] += 1
            n += 1

    print(f"[jlens] FEVER -> {out}: {n} records")
    for L, c in bal.items():
        print(f"[jlens]   {L}: n_true={c[True]} n_false={c[False]} n_null={c[None]}")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
