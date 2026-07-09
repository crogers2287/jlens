#!/usr/bin/env python3
"""Tests for the M17 reviewed-calibration report. CPU-only, no network.

(a) reviewed-record loading/grouping works on a SYNTHETIC fixture;
(b) the committed summary has NO text-preview/notes keys;
(c) category grouping is correct (numeric/json/exact/math/regex/explain-rubric/
    retrieval/open-explain) from verifier_names + task_category;
(d) auto_vs_human_agreement is computed only where comparable and null otherwise;
(e) action counts are carried as planned-only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import reviewed_calibration_report as RC  # noqa: E402


def _rec(cat=None, verifiers=(), auto_wrong=None, human_wrong=None):
    return {
        "prompt_id": "x", "task_category": cat, "policy": None,
        "outcome": {"user_agreed": None, "was_wrong": human_wrong,
                    "needed_retrieval": None, "needed_checker": None, "notes": None},
        "auto_outcome": {"auto_judged": True, "auto_was_wrong": auto_wrong,
                         "verifier_names": list(verifiers), "escalate_for_review": True},
    }


# ---- (c) category grouping ---------------------------------------------------
def test_category_of():
    assert RC.category_of(_rec(verifiers=["numeric_tolerant_check"])) == "numeric"
    assert RC.category_of(_rec(verifiers=["json_object_check"])) == "json"
    assert RC.category_of(_rec(verifiers=["exact_answer_match"])) == "exact"
    assert RC.category_of(_rec(verifiers=["math_checker"])) == "math"
    assert RC.category_of(_rec(verifiers=["regex_or_schema_check"])) == "regex"
    assert RC.category_of(_rec(verifiers=["explain_rubric_check"])) == "explain-rubric"
    # no decisive verifier -> task_category decides
    assert RC.category_of(_rec(cat="current_info",
                               verifiers=["retrieval_required_heuristic"])) == "retrieval/current-info"
    assert RC.category_of(_rec(cat="explain",
                               verifiers=["retrieval_required_heuristic"])) == "open-explain"


# ---- (a)+(d) grouping + agreement only where comparable ----------------------
def test_per_category_agreement():
    fx = [
        _rec(verifiers=["exact_answer_match"], auto_wrong=True, human_wrong=False),   # comparable, disagree
        _rec(verifiers=["exact_answer_match"], auto_wrong=False, human_wrong=False),  # comparable, agree
        _rec(cat="explain", verifiers=["retrieval_required_heuristic"],
             auto_wrong=None, human_wrong=False),   # reviewed but auto=None -> not comparable
    ]
    cats = RC.per_category(fx)
    ex = cats["exact"]
    assert ex["reviewed_count"] == 2 and ex["comparable_count"] == 2
    assert ex["auto_vs_human_agreement"]["agreement_rate"] == 0.5  # 1 of 2 agree
    oe = cats["open-explain"]
    assert oe["reviewed_count"] == 1 and oe["comparable_count"] == 0
    assert oe["auto_vs_human_agreement"] is None
    assert oe["calibration_status"] == "verifier_gap"


# ---- (b) committed summary has no text keys ----------------------------------
def test_summary_no_text_keys():
    p = ROOT / "reports/outcomes/agents_a1_reviewed_calibration_summary.json"
    if not p.exists():
        return
    d = json.loads(p.read_text())
    RC.assert_no_text(d)  # raises on any forbidden text value
    # agreement present only where comparable
    for c in d["per_category"].values():
        assert (c["auto_vs_human_agreement"] is None) or (c["comparable_count"] > 0)


# ---- (e) action counts carried as planned-only -------------------------------
def test_action_planned_only():
    summ = RC.build(ROOT)
    ac = summ.get("action_routing_planned_only")
    if ac is not None:  # present when the M16 action summary exists
        assert set(ac).issubset(
            {"retrieval_needed", "checker_needed", "review_needed", "no_action"})
        assert all(isinstance(v, int) for v in ac.values())
    assert summ["fixed_findings"] and summ["remaining_gaps"]


TESTS = [test_category_of, test_per_category_agreement,
         test_summary_no_text_keys, test_action_planned_only]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] reviewed-calibration tests PASSED ({len(TESTS)} tests)")
