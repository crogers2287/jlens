#!/usr/bin/env python3
"""Deterministic generator for the M13 larger workload batch.

Writes a PUBLIC mixed batch across the 6 scorable categories the verifiers
handle. No RNG — everything is derived from fixed pools / index arithmetic, so
the file is reproducible. Public benchmark-style prompts only; no private text.

  python src/gen_m13_batch.py --out data/prompts/agents_a1_m13_batch.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def math_tasks():
    """Arithmetic with a safe evaluable expression + known answer."""
    specs = []
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b),
           ("*", lambda a, b: a * b)]
    i = 0
    for a in range(6, 44):                       # deterministic grid
        sym, fn = ops[a % 3]
        b = (a % 7) + 3
        expr = f"{a}{sym}{b}"
        specs.append({"prompt": f"What is {a} {sym} {b}?",
                      "task_category": "math",
                      "known_answer": str(fn(a, b)), "expression": expr})
        i += 1
    # a few percent / power / division tasks
    extra = [("What is 20% of 150?", "30", "150*20/100"),
             ("What is 15% of 300?", "45", "300*15/100"),
             ("What is 2 to the power of 8?", "256", "2**8"),
             ("What is 3 to the power of 4?", "81", "3**4"),
             ("What is 144 divided by 12?", "12", "144/12"),
             ("What is 1000 divided by 8?", "125", "1000/8")]
    for p, ans, ex in extra:
        specs.append({"prompt": p, "task_category": "math",
                      "known_answer": ans, "expression": ex})
    return specs


def exact_tasks():
    facts = [
        ("What is the capital of France?", "Paris"),
        ("What is the capital of Japan?", "Tokyo"),
        ("What is the capital of Italy?", "Rome"),
        ("What is the capital of Canada?", "Ottawa"),
        ("What is the capital of Australia?", "Canberra"),
        ("What is the chemical symbol for gold?", "Au"),
        ("What is the chemical symbol for oxygen?", "O"),
        ("What is the chemical symbol for iron?", "Fe"),
        ("How many continents are there?", "7"),
        ("How many sides does a hexagon have?", "6"),
        ("What planet is known as the Red Planet?", "Mars"),
        ("What is the largest ocean on Earth?", "Pacific"),
        ("What is the largest planet in the solar system?", "Jupiter"),
        ("What gas do plants primarily absorb from the air?", "carbon dioxide"),
        ("What is the freezing point of water in Celsius?", "0"),
        ("Who wrote the play Romeo and Juliet?", "Shakespeare"),
        ("What is the square root of 81?", "9"),
        ("How many days are in a leap year?", "366"),
        ("What is the smallest prime number?", "2"),
        ("What is the speed of light approximately, in km per second?", "300000"),
    ]
    return [{"prompt": p, "task_category": "exact_answer", "known_answer": a}
            for p, a in facts]


def json_tasks():
    specs = [
        ('Return a JSON object with a single key named "result".', ["result"]),
        ('Return a JSON object with keys "name" and "age".', ["name", "age"]),
        ('Return a JSON object with a key "status".', ["status"]),
        ('Return a JSON object with keys "city" and "country".', ["city", "country"]),
        ('Return a JSON object with a key "ok" set to true.', ["ok"]),
        ('Return a JSON object with keys "id" and "value".', ["id", "value"]),
        ('Return a JSON object with a key "count".', ["count"]),
        ('Return a JSON object with keys "first" and "last".', ["first", "last"]),
        ('Return a JSON object with a key "message".', ["message"]),
        ('Return a JSON object with keys "x", "y".', ["x", "y"]),
    ]
    return [{"prompt": p, "task_category": "json", "json_check": True,
             "json_required": keys} for p, keys in specs]


def regex_tasks():
    specs = [
        ("Reply with a US ZIP code (5 digits).", r"\b\d{5}\b"),
        ("Give an ISO date in YYYY-MM-DD form.", r"\d{4}-\d{2}-\d{2}"),
        ("Return a hex color code.", r"#[0-9a-fA-F]{6}"),
        ("Reply with a US phone number like 555-123-4567.", r"\d{3}-\d{3}-\d{4}"),
        ("Give a time in HH:MM 24-hour format.", r"\b\d{2}:\d{2}\b"),
        ("Return an IPv4 address.", r"\b\d{1,3}(\.\d{1,3}){3}\b"),
        ("Reply with a single uppercase word.", r"\b[A-Z]{2,}\b"),
        ("Give a percentage like 42%.", r"\b\d{1,3}%"),
    ]
    return [{"prompt": p, "task_category": "regex", "pattern": pat}
            for p, pat in specs]


def current_info_tasks():
    prompts = [
        "What is the current price of gold today?",
        "Who is the current CEO of Twitter?",
        "What is the latest iPhone model released this year?",
        "What is today's weather in Tampa?",
        "What is the current population of Tokyo right now?",
        "What is the latest version of Python released this year?",
        "Who won the most recent Super Bowl?",
        "What is the current stock price of Apple?",
        "What are the current top news headlines?",
        "What is the exchange rate for USD to EUR right now?",
    ]
    return [{"prompt": p, "task_category": "current_info"} for p in prompts]


def explain_tasks():
    prompts = [
        "Explain what a prime number is.",
        "Describe how photosynthesis works in one paragraph.",
        "Summarize the water cycle briefly.",
        "What are the primary colors?",
        "Give a one-sentence definition of gravity.",
        "Explain the difference between weather and climate.",
        "What is the boiling point of water at sea level in Celsius?",
        "Explain what an ecosystem is.",
        "Describe what an integer is in mathematics.",
        "Explain the concept of supply and demand briefly.",
        "What is the function of the human heart?",
        "Explain what renewable energy means.",
        "Describe the role of DNA in living organisms.",
        "Explain what inflation is in economics.",
        "What is the difference between speed and velocity?",
        "Explain what a noun is in grammar.",
        "Describe how a rainbow forms.",
        "Explain what evaporation is.",
    ]
    return [{"prompt": p, "task_category": "explain"} for p in prompts]


def build():
    groups = [("m", math_tasks()), ("e", exact_tasks()), ("j", json_tasks()),
              ("r", regex_tasks()), ("c", current_info_tasks()),
              ("x", explain_tasks())]
    rows = []
    for prefix, specs in groups:
        for i, s in enumerate(specs):
            rec = dict(s)
            rec = {"prompt_id": f"m13_{prefix}_{i:03d}", **rec}
            rows.append(rec)
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="data/prompts/agents_a1_m13_batch.jsonl")
    args = ap.parse_args(argv)
    rows = build()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    cats = {}
    for r in rows:
        cats[r["task_category"]] = cats.get(r["task_category"], 0) + 1
    print(f"[jlens] wrote {len(rows)} m13 tasks -> {out} | categories: {cats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
