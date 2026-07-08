#!/usr/bin/env python3
"""Reconstruct prompt TEXT for a balanced M5 smoke sample from benchmark labels.

Selects a small, deterministic, class-balanced set of benchmark prompts for the
two coverage-passing labels (answerable_from_memory, unsupported_or_hallucinated)
and reconstructs each prompt's text from the cached raw source files
(data/raw/, gitignored) keyed by source_record_id.

Composition (4 each = 16 prompts, 8 per class for each covered label):
  - TruthfulQA correct  -> answerable_from_memory=true,  unsupported=false
  - GSM8K               -> answerable_from_memory=false (needs_math_verification)
  - FEVER SUPPORTS      -> unsupported_or_hallucinated=false (needs_exact_citation)
  - FEVER REFUTES       -> unsupported_or_hallucinated=true

METHODOLOGICAL CAVEAT: the benchmark label describes a reference ANSWER, but we
capture telemetry on the PROMPT. This is a prompt-level PROXY label for a smoke
prototype — indicative, not a final claim. Deterministic selection (no RNG).

CLI:
  python src/build_benchmark_prompts.py \
      --per-group 4 --out data/prompts/benchmark_m5_sample.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load_benchmark(dir_="data/labels/benchmark"):
    recs = []
    for fp in sorted(Path(dir_).glob("*.jsonl")):
        for line in open(fp, encoding="utf-8"):
            recs.append(json.loads(line))
    return recs


def _tqa_questions():
    import pandas as pd
    df = pd.read_parquet("data/raw/generation/validation-00000-of-00001.parquet")
    return {str(i): row["question"] for i, row in df.iterrows()}


def _gsm8k_questions():
    import pandas as pd
    df = pd.read_parquet("data/raw/main/test-00000-of-00001.parquet")
    return {str(i): row["question"] for i, row in df.iterrows()}


def _fever_claims():
    out = {}
    for line in open("data/raw/valid.jsonl", encoding="utf-8"):
        r = json.loads(line)
        out[str(r["id"])] = r["claim"]
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--per-group", type=int, default=4)
    ap.add_argument("--out", default="data/prompts/benchmark_m5_sample.jsonl")
    args = ap.parse_args(argv)

    bench = _load_benchmark()
    tqa = _tqa_questions()
    gsm = _gsm8k_questions()
    fever = _fever_claims()

    def pick(pred, reconstruct, n):
        """First n benchmark records matching pred, deduped by reconstructed text."""
        out, seen = [], set()
        for r in sorted(bench, key=lambda x: x["prompt_id"]):
            if not pred(r):
                continue
            text = reconstruct(r)
            if not text or text in seen:
                continue
            seen.add(text)
            out.append((r, text))
            if len(out) >= n:
                break
        return out

    groups = [
        ("TruthfulQA-correct",
         lambda r: r["source_dataset"] == "TruthfulQA" and r["source_label"] == "correct",
         lambda r: tqa.get(r["source_record_id"].split("_")[0])),
        ("GSM8K",
         lambda r: r["source_dataset"] == "GSM8K",
         lambda r: gsm.get(r["source_record_id"])),
        ("FEVER-SUPPORTS",
         lambda r: r["source_dataset"] == "FEVER" and r["source_label"] == "SUPPORTS",
         lambda r: fever.get(r["source_record_id"])),
        ("FEVER-REFUTES",
         lambda r: r["source_dataset"] == "FEVER" and r["source_label"] == "REFUTES",
         lambda r: fever.get(r["source_record_id"])),
    ]

    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    summary = {}
    with out.open("w", encoding="utf-8") as fh:
        for name, pred, recon in groups:
            picked = pick(pred, recon, args.per_group)
            summary[name] = len(picked)
            for r, text in picked:
                fh.write(json.dumps({
                    "id": r["prompt_id"],
                    "text": text,
                    "source_dataset": r["source_dataset"],
                    "source_label": r["source_label"],
                    "labels": r["labels"],
                }) + "\n")
                n += 1

    print(f"[jlens] wrote {n} sample prompts -> {out}")
    for name, c in summary.items():
        print(f"[jlens]   {name}: {c}")
    # class balance across the two covered labels
    rows = [json.loads(l) for l in open(out)]
    for L in ("answerable_from_memory", "unsupported_or_hallucinated"):
        t = sum(1 for r in rows if r["labels"].get(L) is True)
        f = sum(1 for r in rows if r["labels"].get(L) is False)
        nul = sum(1 for r in rows if r["labels"].get(L) is None)
        print(f"[jlens]   {L}: n_true={t} n_false={f} n_null={nul}")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
