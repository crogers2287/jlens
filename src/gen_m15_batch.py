#!/usr/bin/env python3
"""Deterministic generator for the M15 larger workload batch (250-500 tasks).

Reuses the M13 pools (exact/json/regex/current_info/explain) and adds a large
deterministic math grid plus NUMERIC (M14 numeric-tolerant) and EXPLAIN-RUBRIC
(M14 required_facts) pools. No RNG — reproducible. Public benchmark-style prompts
only.

  python src/gen_m15_batch.py --out data/prompts/agents_a1_m15_batch.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_m13_batch as M13  # reuse pools


def big_math_tasks():
    """A large deterministic arithmetic grid + the M13 percent/power extras."""
    specs = []
    ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b),
           ("*", lambda a, b: a * b)]
    for a in range(6, 160):
        sym, fn = ops[a % 3]
        b = (a % 9) + 2
        specs.append({"prompt": f"What is {a} {sym} {b}?", "task_category": "math",
                      "known_answer": str(fn(a, b)), "expression": f"{a}{sym}{b}"})
    for m in M13.math_tasks():
        if m.get("known_answer") and "**" in m.get("expression", "") or "/" in m.get("expression", "") or "100" in m.get("expression", ""):
            specs.append(m)  # keep the percent/power/division extras
    return specs


def numeric_tasks():
    """Approximate / unit-converted numeric answers (route to numeric_tolerant_check)."""
    fixed = [
        ("What is the speed of light approximately, in km per second?", 300000, None, 0.01, "km"),
        ("What is the boiling point of water at sea level, in Celsius?", 100, 0.5, None, "C"),
        ("Approximately how many km is Earth's circumference?", 40075, None, 0.02, "km"),
        ("What is absolute zero in degrees Celsius?", -273.15, 0.5, None, "C"),
        ("What is the approximate value of pi?", 3.14159, 0.01, None, None),
        ("Approximately how many meters are in a mile?", 1609, 5.0, None, "m"),
        ("What is the freezing point of water in Fahrenheit?", 32, 0.5, None, "F"),
        ("Approximately how many seconds are in an hour?", 3600, 1.0, None, None),
        ("What is the approximate acceleration due to gravity, in m/s^2?", 9.81, 0.05, None, None),
        ("Approximately how many days are in a year?", 365, 1.0, None, None),
    ]
    specs = []
    for p, ev, tol, rel, units in fixed:
        r = {"prompt": p, "task_category": "exact_answer", "numeric": True,
             "expected_value": ev, "known_answer": str(ev)}
        if tol is not None:
            r["tolerance"] = tol
        if rel is not None:
            r["rel_tolerance"] = rel
        if units is not None:
            r["expected_units"] = units
        specs.append(r)
    # deterministic "approximately X/Y" division tasks with rounding tolerance
    for i, (x, y) in enumerate([(1000, 3), (100, 7), (22, 7), (500, 9), (250, 6),
                                (1000, 6), (2000, 7), (355, 113), (10, 3), (50, 3)]):
        specs.append({"prompt": f"Approximately what is {x} divided by {y}?",
                      "task_category": "exact_answer", "numeric": True,
                      "expected_value": round(x / y, 2), "tolerance": 0.5,
                      "known_answer": str(round(x / y, 2))})
    return specs


def rubric_tasks():
    """Open-ended explanations scored ONLY against a public fact checklist."""
    pool = [
        ("Explain what a prime number is.", ["greater than 1", "divisor"]),
        ("Explain photosynthesis in one sentence.", ["light", "energy"]),
        ("Explain what an integer is.", ["whole number"]),
        ("Explain what gravity is in one sentence.", ["force", "mass"]),
        ("Explain what evaporation is.", ["liquid", "gas"]),
        ("Explain what an ecosystem is.", ["organisms", "environment"]),
        ("Explain the difference between speed and velocity.", ["direction"]),
        ("Explain what renewable energy is.", ["replenish"]),
        ("Explain what the water cycle is.", ["evaporation", "precipitation"]),
        ("Explain what inflation means in economics.", ["prices", "rise"]),
        ("Explain what DNA does.", ["genetic"]),
        ("Explain what a noun is.", ["person", "place", "thing"]),
        ("Explain what a verb is.", ["action"]),
        ("Explain the difference between weather and climate.", ["long-term", "short-term"]),
        ("Explain what a molecule is.", ["atoms"]),
    ]
    return [{"prompt": p, "task_category": "explain", "required_facts": facts}
            for p, facts in pool]


def build():
    groups = [
        ("m", big_math_tasks()),
        ("e", M13.exact_tasks()),
        ("n", numeric_tasks()),
        ("j", M13.json_tasks()),
        ("r", M13.regex_tasks()),
        ("c", M13.current_info_tasks()),
        ("x", M13.explain_tasks()),
        ("k", rubric_tasks()),
    ]
    rows = []
    for prefix, specs in groups:
        for i, s in enumerate(specs):
            rec = M13.normalize_numeric_metadata(dict(s))  # M16: tag numeric exact rows
            rows.append({"prompt_id": f"m15_{prefix}_{i:03d}", **rec})
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default="data/prompts/agents_a1_m15_batch.jsonl")
    args = ap.parse_args(argv)
    rows = build()
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    cats = {}
    for r in rows:
        key = ("numeric" if r.get("numeric") else
               "explain-rubric" if r.get("required_facts") else r["task_category"])
        cats[key] = cats.get(key, 0) + 1
    print(f"[jlens] wrote {len(rows)} m15 tasks -> {out} | {cats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
