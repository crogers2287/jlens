#!/usr/bin/env python3
"""Build the deterministic 500-task M19 mixed workload.

Starts with the cleaned 261-task M15 batch so baseline categories remain
comparable, then adds 239 unique tasks: 200 math, 10 exact, 10 current-info,
10 explain-rubric, and 9 numeric. All checker metadata is explicit.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import gen_m15_batch as M15  # noqa: E402
import gen_m13_batch as M13  # noqa: E402


def _math_tasks():
    rows = []
    for i in range(200):
        a, b, c = 101 + i, 2 + (i % 17), i % 23
        expr = f"{a}*{b}+{c}"
        rows.append({
            "prompt_id": f"m19_m_{i:03d}",
            "prompt": f"Compute {a} * {b} + {c}. Give the final number.",
            "task_category": "math",
            "known_answer": str(a * b + c),
            "expression": expr,
        })
    return rows


def _exact_tasks():
    items = [
        ("symbol for silver", "Ag"), ("capital of Portugal", "Lisbon"),
        ("largest ocean", "Pacific Ocean"), ("author of 1984", "George Orwell"),
        ("chemical symbol for potassium", "K"), ("capital of Kenya", "Nairobi"),
        ("smallest prime number", "2"), ("hardest natural mineral", "diamond"),
        ("planet known as the Red Planet", "Mars"),
        ("language primarily spoken in Brazil", "Portuguese"),
    ]
    return [{
        "prompt_id": f"m19_e_{i:03d}",
        "prompt": f"Give only the answer: What is the {question}?",
        "task_category": "exact_answer", "known_answer": answer,
    } for i, (question, answer) in enumerate(items)]


def _current_info_tasks():
    prompts = [
        "What is the current federal funds target range today?",
        "Who is the current prime minister of Canada?",
        "What is the latest stable Node.js release this year?",
        "What is today's closing price for the S&P 500?",
        "Who won the most recent NBA Finals?",
        "What is the current Bitcoin price in US dollars?",
        "What are today's top technology news headlines?",
        "What is the current temperature in Miami?",
        "What is the latest stable Rust compiler version?",
        "What is the current USD to GBP exchange rate?",
    ]
    return [{"prompt_id": f"m19_c_{i:03d}", "prompt": prompt,
             "task_category": "current_info"}
            for i, prompt in enumerate(prompts)]


def _rubric_tasks():
    specs = [
        ("Explain photosynthesis.", ["light", "carbon dioxide", "glucose"]),
        ("Explain plate tectonics.", ["plates", "mantle", "movement"]),
        ("Explain how vaccines train immunity.", ["antigen", "immune", "memory"]),
        ("Explain supply and demand.", ["price", "quantity", "market"]),
        ("Explain public-key encryption.", ["public key", "private key", "ciphertext"]),
        ("Explain natural selection.", ["variation", "inheritance", "reproduction"]),
        ("Explain the water cycle.", ["evaporation", "condensation", "precipitation"]),
        ("Explain how a battery produces electricity.", ["electrode", "electrolyte", "electron"]),
        ("Explain why seasons occur.", ["tilt", "orbit", "sunlight"]),
        ("Explain how DNS resolves a domain.", ["resolver", "nameserver", "IP address"]),
    ]
    return [{"prompt_id": f"m19_k_{i:03d}", "prompt": prompt,
             "task_category": "explain", "required_facts": facts}
            for i, (prompt, facts) in enumerate(specs)]


def _numeric_tasks():
    specs = [
        ("How many meters are in 3.5 kilometers?", 3500, "meters"),
        ("Convert 2.25 kilometers to meters.", 2250, "meters"),
        ("What is 18 percent of 250?", 45, None),
        ("A $120 item is discounted by 25 percent. What is the sale price?", 90, None),
        ("Convert 0.75 kilometers to meters.", 750, "meters"),
        ("What is the mean of 10, 20, 30, and 40?", 25, None),
        ("What is 7.5 multiplied by 12?", 90, None),
        ("A car travels 180 miles in 3 hours. What is its average mph?", 60, None),
        ("What is the area of a 12 by 8 rectangle?", 96, None),
    ]
    rows = []
    for i, (prompt, value, units) in enumerate(specs):
        row = {"prompt_id": f"m19_n_{i:03d}", "prompt": prompt,
               "task_category": "numeric", "numeric": True,
               "expected_value": value, "tolerance": 0.01}
        if units:
            row["expected_units"] = units
        rows.append(row)
    return rows


def build():
    base = M15.build()
    added = (_math_tasks() + _exact_tasks() + _current_info_tasks()
             + _rubric_tasks() + _numeric_tasks())
    # M15 intentionally contains five prompt-text reuses across verifier
    # variants; preserve those baseline rows, but add no new text duplicates.
    assert len({r["prompt"] for r in added}) == 239
    assert not ({r["prompt"] for r in base} & {r["prompt"] for r in added})
    rows = base + added
    rows = [M13.normalize_numeric_metadata(r) for r in rows]
    assert len(rows) == 500
    assert len({r["prompt_id"] for r in rows}) == 500
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="data/prompts/agents_a1_m19_batch.jsonl")
    args = ap.parse_args(argv)
    rows = build()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")
    from collections import Counter
    print(f"[jlens] M19 batch: {len(rows)} tasks -> {out} | "
          f"{dict(Counter(r['task_category'] for r in rows))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
