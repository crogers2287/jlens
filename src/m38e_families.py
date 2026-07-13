"""M38E Phase 0: deterministic hard-task generators and verifiers.

Per docs/M38E_HARD_COMPLETED_ERROR_PROTOCOL.md — procedural families
where Agents-A1 should usually complete but produce a meaningful mix of
objectively correct and wrong answers. Every task has an exact integer
answer and an objective verifier (the shared numeric checker). Bands
scale genuine multi-step difficulty, not prompt length.

Families:
  mod_chain    — k-step modular arithmetic with exponentiation steps;
  alg_coeff    — coefficient of x^k in a product of binomial powers;
  order_track  — object tracking through a sequence of swap/rotate ops.

All generation is seeded per (family, band, index); answers are
computed by direct simulation/arithmetic in the generator itself.
"""
from __future__ import annotations

import json
import math
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

M38E_SEED = "m38e-dev-v1"

# Bands: family -> list of band dicts (b1 easiest .. b4 hardest).
BANDS = {
    "mod_chain": [
        {"steps": 3, "mod_lo": 7, "mod_hi": 97, "base_hi": 99, "exp_hi": 5},
        {"steps": 4, "mod_lo": 11, "mod_hi": 997, "base_hi": 999,
         "exp_hi": 7},
        {"steps": 6, "mod_lo": 101, "mod_hi": 997, "base_hi": 9999,
         "exp_hi": 9},
        {"steps": 8, "mod_lo": 101, "mod_hi": 9973, "base_hi": 99999,
         "exp_hi": 12},
    ],
    "alg_coeff": [
        {"n_hi": 4, "m_hi": 3, "coef_hi": 5, "k_mode": "middle"},
        {"n_hi": 6, "m_hi": 4, "coef_hi": 9, "k_mode": "middle"},
        {"n_hi": 8, "m_hi": 6, "coef_hi": 9, "k_mode": "any"},
        {"n_hi": 10, "m_hi": 8, "coef_hi": 12, "k_mode": "any"},
    ],
    "order_track": [
        {"objects": 5, "ops": 8},
        {"objects": 7, "ops": 14},
        {"objects": 9, "ops": 22},
        {"objects": 12, "ops": 32},
    ],
}


def _rng(family: str, band: int, index: int) -> random.Random:
    return random.Random(f"{M38E_SEED}:{family}:b{band}:{index}")


def gen_mod_chain(band: int, index: int) -> dict:
    cfg = BANDS["mod_chain"][band - 1]
    rng = _rng("mod_chain", band, index)
    m = rng.randint(cfg["mod_lo"], cfg["mod_hi"])
    value = rng.randint(2, cfg["base_hi"])
    lines = [f"Start with x = {value}."]
    for _ in range(cfg["steps"]):
        op = rng.choice(("add", "mul", "pow"))
        if op == "add":
            a = rng.randint(2, cfg["base_hi"])
            lines.append(f"Add {a} to x.")
            value = value + a
        elif op == "mul":
            a = rng.randint(2, cfg["base_hi"])
            lines.append(f"Multiply x by {a}.")
            value = value * a
        else:
            e = rng.randint(2, cfg["exp_hi"])
            lines.append(f"Raise x to the power {e}.")
            value = value ** e
        value %= m  # answer tracked mod m throughout
        lines.append(f"Reduce x modulo {m}.")
    prompt = (" ".join(lines)
              + " What is the final value of x? Reply with the final "
                "number only.")
    return {"prompt": prompt, "known_answer": str(value)}


def gen_alg_coeff(band: int, index: int) -> dict:
    cfg = BANDS["alg_coeff"][band - 1]
    rng = _rng("alg_coeff", band, index)
    n, m = rng.randint(2, cfg["n_hi"]), rng.randint(1, cfg["m_hi"])
    a, c = rng.randint(1, cfg["coef_hi"]), rng.randint(1, cfg["coef_hi"])
    b = rng.choice((-1, 1)) * rng.randint(1, cfg["coef_hi"])
    d = rng.choice((-1, 1)) * rng.randint(1, cfg["coef_hi"])
    deg = n + m
    if cfg["k_mode"] == "middle":
        k = deg // 2
    else:
        k = rng.randint(1, deg - 1)
    coeff = 0
    for i in range(0, n + 1):
        j = k - i
        if 0 <= j <= m:
            coeff += (math.comb(n, i) * a**i * b**(n - i)
                      * math.comb(m, j) * c**j * d**(m - j))
    prompt = (f"Consider the polynomial ({a}x + {b})^{n} * "
              f"({c}x + {d})^{m}. What is the coefficient of x^{k} in "
              f"its full expansion? Reply with the final number only.")
    return {"prompt": prompt, "known_answer": str(coeff)}


def gen_order_track(band: int, index: int) -> dict:
    cfg = BANDS["order_track"][band - 1]
    rng = _rng("order_track", band, index)
    n = cfg["objects"]
    row = list(range(1, n + 1))
    lines = [f"Balls numbered 1 to {n} sit in a row of positions "
             f"1 to {n}, in that order (ball i starts at position i)."]
    for _ in range(cfg["ops"]):
        op = rng.choice(("swap_pos", "swap_ball", "rotate"))
        if op == "swap_pos":
            p, q = rng.sample(range(n), 2)
            lines.append(f"Swap the balls at positions {p + 1} and "
                         f"{q + 1}.")
            row[p], row[q] = row[q], row[p]
        elif op == "swap_ball":
            x, y = rng.sample(range(1, n + 1), 2)
            lines.append(f"Ball {x} and ball {y} exchange positions.")
            p, q = row.index(x), row.index(y)
            row[p], row[q] = row[q], row[p]
        else:
            k = rng.randint(1, n - 1)
            lines.append(f"Rotate the entire row {k} positions to the "
                         f"right (the last {k} balls wrap to the front).")
            row = row[-k:] + row[:-k]
    ball = rng.randint(1, n)
    answer = row.index(ball) + 1
    prompt = (" ".join(lines)
              + f" At which position is ball {ball} now? Reply with the "
                "final number only.")
    return {"prompt": prompt, "known_answer": str(answer)}


GENERATORS = {"mod_chain": gen_mod_chain, "alg_coeff": gen_alg_coeff,
              "order_track": gen_order_track}


def generate(family: str, band: int, index: int) -> dict:
    task = GENERATORS[family](band, index)
    task.update(task_id=f"m38e_{family}_b{band}_{index:03d}",
                family=family, band=f"b{band}")
    return task


def verdict(task: dict, text: str) -> str:
    """Objective verifier: shared numeric checker on the exact answer."""
    from m36_calibration import task_verdict
    return task_verdict({"known_answer": task["known_answer"]}, text)


def main() -> int:
    # Smoke print: one aggregate line per family/band (no task content).
    for family in GENERATORS:
        for band in range(1, len(BANDS[family]) + 1):
            tasks = [generate(family, band, i) for i in range(4)]
            assert len({t["prompt"] for t in tasks}) == len(tasks)
            print(f"[m38e] {family} b{band}: {len(tasks)} ok, "
                  f"answer_digits_median="
                  f"{sorted(len(t['known_answer']) for t in tasks)[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
