"""M38E Phase 0 unit tests: determinism, correctness, verifier behavior."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from m38e_families import BANDS, GENERATORS, generate, verdict


ALL_CELLS = [(f, b) for f in GENERATORS for b in range(1, len(BANDS[f]) + 1)]


@pytest.mark.parametrize("family,band", ALL_CELLS)
def test_determinism(family, band):
    a = [generate(family, band, i) for i in range(8)]
    b = [generate(family, band, i) for i in range(8)]
    assert a == b


@pytest.mark.parametrize("family,band", ALL_CELLS)
def test_tasks_unique_within_cell(family, band):
    tasks = [generate(family, band, i) for i in range(24)]
    assert len({t["prompt"] for t in tasks}) == 24
    assert len({t["task_id"] for t in tasks}) == 24


@pytest.mark.parametrize("family,band", ALL_CELLS)
def test_verifier_accepts_known_answer_and_rejects_wrong(family, band):
    for i in range(8):
        task = generate(family, band, i)
        assert verdict(task, f"The final answer is {task['known_answer']}."
                       ) == "pass", task["task_id"]
        wrong = str(int(task["known_answer"]) + 1)
        assert verdict(task, f"The final answer is {wrong}.") != "pass"


def test_mod_chain_answers_in_range():
    for band in range(1, 5):
        for i in range(8):
            task = generate("mod_chain", band, i)
            # Final reduce keeps the answer within the modulus band cap.
            assert 0 <= int(task["known_answer"]) < 10000


def test_alg_coeff_matches_bruteforce_expansion():
    import re
    for band in range(1, 5):
        for i in range(8):
            task = generate("alg_coeff", band, i)
            nums = re.match(
                r"Consider the polynomial \((\d+)x \+ (-?\d+)\)\^(\d+) \* "
                r"\((\d+)x \+ (-?\d+)\)\^(\d+)\. What is the coefficient "
                r"of x\^(\d+)", task["prompt"])
            a, b, n, c, d, m, k = (int(g) for g in nums.groups())
            poly1 = [1]
            for _ in range(n):
                nxt = [0] * (len(poly1) + 1)
                for deg, co in enumerate(poly1):
                    nxt[deg] += co * b
                    nxt[deg + 1] += co * a
                poly1 = nxt
            poly2 = [1]
            for _ in range(m):
                nxt = [0] * (len(poly2) + 1)
                for deg, co in enumerate(poly2):
                    nxt[deg] += co * d
                    nxt[deg + 1] += co * c
                poly2 = nxt
            full = [0] * (len(poly1) + len(poly2) - 1)
            for d1, c1 in enumerate(poly1):
                for d2, c2 in enumerate(poly2):
                    full[d1 + d2] += c1 * c2
            assert full[k] == int(task["known_answer"]), task["task_id"]


def test_order_track_positions_valid():
    for band in range(1, 5):
        cfg = BANDS["order_track"][band - 1]
        for i in range(8):
            task = generate("order_track", band, i)
            assert 1 <= int(task["known_answer"]) <= cfg["objects"]


def test_bands_scale_difficulty():
    # Harder bands must have strictly more steps/ops or larger spaces.
    mc = BANDS["mod_chain"]
    assert all(mc[i]["steps"] < mc[i + 1]["steps"] for i in range(3))
    ot = BANDS["order_track"]
    assert all(ot[i]["ops"] < ot[i + 1]["ops"] for i in range(3))
    ac = BANDS["alg_coeff"]
    assert all(ac[i]["n_hi"] < ac[i + 1]["n_hi"] for i in range(3))
