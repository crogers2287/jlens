#!/usr/bin/env python3
"""Convert TruthfulQA (benchmark-gold) → jlens risk_labels_v2 JSONL.

TruthfulQA (Apache-2.0) is human-written truthfulness QA over common
misconceptions. Each question has human `correct_answers` and
`incorrect_answers`. We emit one benchmark_gold record PER answer:
  - a correct/truthful answer   -> unsupported_or_hallucinated = false,
                                   answerable_from_memory = true
  - an incorrect/false answer   -> unsupported_or_hallucinated = true
All 8 other labels stay null (NULL = UNKNOWN, never guessed).

Pulls the raw parquet via huggingface_hub (no `datasets` install). Raw parquet
is cached under data/raw/ (gitignored); only the converted JSONL is committed.

CLI:
  python src/convert_truthfulqa.py \
      --schema schema/risk_labels_v2.json \
      --out data/labels/benchmark/truthfulqa.jsonl [--limit N]
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

REPO = "truthful_qa"
FILE = "generation/validation-00000-of-00001.parquet"
SPLIT = "validation"
LICENSE = "Apache-2.0"
TEN = [
    "answerable_from_memory", "needs_current_info", "needs_exact_citation",
    "needs_math_verification", "needs_code_execution", "needs_user_file_context",
    "high_stakes_or_sensitive", "context_attack_present",
    "unsupported_or_hallucinated", "format_or_tool_mode_shift",
]


def _rec(rid, source_label, labels):
    full = {k: None for k in TEN}
    full.update(labels)
    return {
        "schema_version": 2,
        "prompt_id": f"tqa_{rid}",
        "labeler": None,
        "labels": full,
        "source_dataset": "TruthfulQA",
        "source_split": SPLIT,
        "source_record_id": str(rid),
        "source_label": source_label,
        "source_license": LICENSE,
        "label_source": "benchmark_gold",
        "label_confidence": 1.0,
        "non_commercial": False,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--schema", default="schema/risk_labels_v2.json")
    ap.add_argument("--out", default="data/labels/benchmark/truthfulqa.jsonl")
    ap.add_argument("--limit", type=int, default=0, help="0 = all questions")
    args = ap.parse_args(argv)

    import pandas as pd
    from huggingface_hub import hf_hub_download
    from jsonschema import Draft7Validator

    schema = json.loads(Path(args.schema).read_text())
    validator = Draft7Validator(schema)

    raw_dir = Path("data/raw"); raw_dir.mkdir(parents=True, exist_ok=True)
    path = hf_hub_download(REPO, FILE, repo_type="dataset",
                           local_dir=str(raw_dir))
    df = pd.read_parquet(path)
    if args.limit:
        df = df.head(args.limit)

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    counts = Counter()
    n = 0
    with out.open("w", encoding="utf-8") as fh:
        for qi, row in df.iterrows():
            # one record per correct answer, one per incorrect answer
            for _ in row["correct_answers"]:
                rec = _rec(f"{qi}_c{_hash(_)}", "correct",
                           {"unsupported_or_hallucinated": False,
                            "answerable_from_memory": True})
                _emit(fh, validator, rec); counts["correct"] += 1; n += 1
            for _ in row["incorrect_answers"]:
                rec = _rec(f"{qi}_i{_hash(_)}", "incorrect",
                           {"unsupported_or_hallucinated": True})
                _emit(fh, validator, rec); counts["incorrect"] += 1; n += 1

    # class balance on the label the source actually determines
    n_true = counts["incorrect"]
    n_false = counts["correct"]
    print(f"[jlens] TruthfulQA -> {out}: {n} records "
          f"(source: {counts['correct']} correct / {counts['incorrect']} incorrect)")
    print(f"[jlens]   unsupported_or_hallucinated: "
          f"n_true={n_true} n_false={n_false} n_null=0")
    print(f"[jlens]   answerable_from_memory: n_true={n_false} n_false=0 "
          f"n_null={n_true} (only set on correct answers)")
    return 0 if n else 1


def _hash(s: str) -> str:
    # stable short id from answer text (avoids Date/random; deterministic)
    h = 0
    for ch in s:
        h = (h * 131 + ord(ch)) & 0xFFFFFFFF
    return f"{h:08x}"


def _emit(fh, validator, rec):
    errs = list(validator.iter_errors(rec))
    if errs:
        raise SystemExit(f"[jlens] record {rec['prompt_id']} invalid: {errs[0].message}")
    fh.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
