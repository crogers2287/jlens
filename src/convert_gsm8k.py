#!/usr/bin/env python3
"""Convert GSM8K (benchmark-gold) → jlens risk_labels_v2 JSONL.

GSM8K (MIT) is grade-school math word problems with human step-by-step
solutions and a final numeric answer. Every item is a numeric problem, so:
  - needs_math_verification = true   (all items)
  - answerable_from_memory   = false (self-contained but requires computation,
                                      not recall — the answer must be derived)
All other labels stay null (NULL = UNKNOWN, never guessed). Note: a bare prompt
does NOT set unsupported_or_hallucinated — that requires grading the TARGET
model's output against the gold answer (a later, output-dependent step). We keep
the gold answer in provenance so that grading is possible downstream.

Pulls raw parquet via huggingface_hub (no `datasets`); raw under data/raw/
(gitignored). Only converted JSONL is committed.

CLI:
  python src/convert_gsm8k.py \
      --schema schema/risk_labels_v2.json \
      --out data/labels/benchmark/gsm8k.jsonl [--limit N]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

REPO = "gsm8k"
FILE = "main/test-00000-of-00001.parquet"
SPLIT = "test"
LICENSE = "MIT"
TEN = [
    "answerable_from_memory", "needs_current_info", "needs_exact_citation",
    "needs_math_verification", "needs_code_execution", "needs_user_file_context",
    "high_stakes_or_sensitive", "context_attack_present",
    "unsupported_or_hallucinated", "format_or_tool_mode_shift",
]


def _gold_answer(ans: str) -> str:
    # GSM8K answers end with "#### <number>"
    return ans.split("####")[-1].strip() if "####" in ans else ""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schema", default="schema/risk_labels_v2.json")
    ap.add_argument("--out", default="data/labels/benchmark/gsm8k.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    import pandas as pd
    from huggingface_hub import hf_hub_download
    from jsonschema import Draft7Validator

    validator = Draft7Validator(json.loads(Path(args.schema).read_text()))
    raw = Path("data/raw"); raw.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(REPO, FILE, repo_type="dataset", local_dir=str(raw))
    df = pd.read_parquet(path)
    if args.limit:
        df = df.head(args.limit)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    bal = {"needs_math_verification": Counter(), "answerable_from_memory": Counter()}
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for i, row in df.iterrows():
            labels = {k: None for k in TEN}
            labels["needs_math_verification"] = True
            labels["answerable_from_memory"] = False
            rec = {
                "schema_version": 2,
                "prompt_id": f"gsm8k_{i}",
                "labeler": None,
                "labels": labels,
                "source_dataset": "GSM8K",
                "source_split": SPLIT,
                "source_record_id": str(i),
                "source_label": f"gold_answer={_gold_answer(row['answer'])}",
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

    print(f"[jlens] GSM8K -> {out}: {n} records")
    for L, c in bal.items():
        print(f"[jlens]   {L}: n_true={c[True]} n_false={c[False]} n_null={c[None]}")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
