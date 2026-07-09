#!/usr/bin/env python3
"""Tests for the M14 numeric-tolerant + explain-rubric verifiers. CPU-only, no net.

(a) numeric_tolerant_check — speed-of-light/unit-conversion/approximate pass,
    clearly-wrong fail, no-number undecided;
(b) exact_answer_match still strict for pure strings;
(c) routing — numeric→numeric_tolerant_check, string exact→exact_answer_match,
    explain-rubric→explain_rubric_check;
(d) explain_rubric_check — full coverage pass, missing fact escalate, no rubric
    undecided, never gold without a rubric;
(e) before/after — the numeric row flips wrong→ok and de-escalates.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import verifiers as VZ  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402

P, F, U = VZ.VERDICT_PASS, VZ.VERDICT_FAIL, VZ.VERDICT_UNDECIDED
CFG = {"verifiers": {}}


def _names(task, out):
    return [r["name"] for r in SUP._run_verifiers(task, out, [out], CFG)]


# ---- (a) numeric verifier ----------------------------------------------------
def test_numeric_tolerant_check():
    assert VZ.numeric_tolerant_check("299,792 km/s", expected_value=300000,
                                     rel_tolerance=0.01)["verdict"] == P
    assert VZ.numeric_tolerant_check("about 300000", expected_value=299792,
                                     rel_tolerance=0.01)["verdict"] == P
    assert VZ.numeric_tolerant_check("100 C", expected_value=100,
                                     tolerance=0.5)["verdict"] == P
    assert VZ.numeric_tolerant_check("42000", expected_value=300000,
                                     rel_tolerance=0.05)["verdict"] == F
    assert VZ.numeric_tolerant_check("no number here", expected_value=1,
                                     tolerance=1)["verdict"] == U
    assert VZ.numeric_tolerant_check("value 5")["verdict"] == U  # no target
    ev = VZ.numeric_tolerant_check("secret 5", expected_value=5, tolerance=0)["evidence_hash"]
    assert "secret" not in ev


# ---- (b) exact_answer_match unchanged / strict -------------------------------
def test_exact_answer_still_strict():
    assert VZ.exact_answer_match("The answer is Paris.", "Paris")["verdict"] == P
    assert VZ.exact_answer_match("London", "Paris")["verdict"] == F


# ---- (c) routing -------------------------------------------------------------
def test_routing():
    numeric = {"prompt_id": "n", "prompt": "km/s", "task_category": "exact_answer",
               "known_answer": "300000", "numeric": True, "expected_value": 300000,
               "rel_tolerance": 0.01}
    n = _names(numeric, "299,792 km/s")
    assert "numeric_tolerant_check" in n and "exact_answer_match" not in n
    string = {"prompt_id": "s", "prompt": "capital", "task_category": "exact_answer",
              "known_answer": "Paris"}
    assert "exact_answer_match" in _names(string, "Paris")
    rubric = {"prompt_id": "e", "prompt": "explain", "task_category": "explain",
              "required_facts": ["greater than 1"]}
    assert "explain_rubric_check" in _names(rubric, "a number greater than 1")
    assert {"numeric_tolerant_check", "explain_rubric_check"} <= SUP.CORRECTNESS


# ---- (d) explain rubric ------------------------------------------------------
def test_explain_rubric():
    out = "A prime is greater than 1 with divisors 1 and itself"
    assert VZ.explain_rubric_check(out, ["greater than 1", "divisor"])["verdict"] == P
    assert VZ.explain_rubric_check(out, ["greater than 1", "even"])["verdict"] == U
    assert VZ.explain_rubric_check(out, None)["verdict"] == U
    # never gold without a rubric
    assert VZ.explain_rubric_check("anything", None)["verdict"] != P


# ---- (e) before/after flip ---------------------------------------------------
def test_numeric_flip_and_deescalate():
    rep = "The speed of light is 299,792,458 m/s = 299,792 km/s."
    old = VZ.exact_answer_match(rep, known_answer="300000")["verdict"]
    task = {"prompt_id": "num_light_kms", "prompt": "km/s", "task_category": "exact_answer",
            "numeric": True, "expected_value": 300000, "rel_tolerance": 0.01,
            "expected_units": "km"}
    res = SUP._run_verifiers(task, rep, [rep], CFG)
    new = next(r["verdict"] for r in res if r["name"] == "numeric_tolerant_check")
    auto = SUP._build_auto_outcome(res, None, CFG)
    assert old == F and new == P
    assert auto["auto_was_wrong"] is False
    assert auto["escalate_for_review"] is False


TESTS = [test_numeric_tolerant_check, test_exact_answer_still_strict, test_routing,
         test_explain_rubric, test_numeric_flip_and_deescalate]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] numeric-verifier tests PASSED ({len(TESTS)} tests)")
