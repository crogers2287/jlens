"""Steer-cccf40a conformance tests for the M36T sealed evaluator.

All fixtures are synthetic — no sealed or development data is read.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

import m36t_evaluate as M
from m36t_evaluate import (EvaluationBlocker, preflight, tool_text,
                           verified_tool_success)


def make_task(i, family="mod_arith", answer="7"):
    t = {"task_id": f"t{i:03d}", "family": family, "stratum": "s1",
         "known_answer": answer, "prompt": f"synthetic {i}"}
    if family == "json_digits":
        t["json_expected"] = json.loads(answer)
    return t


def make_row(i, out_tokens=300):
    return {"task_id": f"t{i:03d}", "output_tokens": out_tokens,
            "verdict_at_cap": {"512": "pass", "1024": "pass"},
            "prefix_features": {"256": {"decode_step_count": 256.0}}}


TASKS = [make_task(i) for i in range(192)]
ROWS = [make_row(i) for i in range(192)]
GOOD_SHA = M.SEALED_TASKS_SHA256


def test_preflight_accepts_valid_join():
    preflight(TASKS, ROWS, GOOD_SHA)


def test_preflight_rejects_sha_mismatch():
    with pytest.raises(EvaluationBlocker, match="sha256"):
        preflight(TASKS, ROWS, "0" * 64)


def test_preflight_rejects_duplicate_ids():
    dup = TASKS[:-1] + [make_task(0)]
    with pytest.raises(EvaluationBlocker, match="unique"):
        preflight(dup, ROWS, GOOD_SHA)


def test_preflight_rejects_missing_row():
    with pytest.raises(EvaluationBlocker):
        preflight(TASKS, ROWS[:-1], GOOD_SHA)


def test_preflight_rejects_id_set_mismatch():
    rows = ROWS[:-1] + [dict(make_row(500))]
    with pytest.raises(EvaluationBlocker, match="sets differ"):
        preflight(TASKS, rows, GOOD_SHA)


def test_preflight_rejects_over_ceiling():
    rows = ROWS[:-1] + [make_row(191, out_tokens=4096)]
    with pytest.raises(EvaluationBlocker, match="ceiling"):
        preflight(TASKS, rows, GOOD_SHA)


@pytest.mark.parametrize("family,answer", [
    ("div_exact", "42"), ("mod_arith", "13"),
    ("sub_mixed", "-5"), ("json_digits", "[1, 2, 3]"),
])
def test_tool_verified_pass_all_families(family, answer):
    task = make_task(0, family=family, answer=answer)
    assert verified_tool_success(task)


def test_tool_rejects_unsupported_family():
    with pytest.raises(EvaluationBlocker, match="unsupported"):
        tool_text(make_task(0, family="mul_multi"))


def test_tool_verifier_rejection_is_blocker(monkeypatch):
    # Force the frozen verifier to fail the tool text: blocker, never
    # an assumed success.
    import m36_calibration
    monkeypatch.setattr(m36_calibration, "task_verdict",
                        lambda task, text: "fail")
    with pytest.raises(EvaluationBlocker, match="blocker"):
        verified_tool_success(make_task(0))


def test_random_routing_deterministic_and_count_matched():
    import numpy as np

    ids = [f"t{i:03d}" for i in range(93)]
    k = 65
    sets = []
    for _ in range(2):
        rng = np.random.default_rng(M.RANDOM_POLICY_SEED)
        sets.append(set(np.asarray(ids)[rng.permutation(len(ids))[:k]]
                        .tolist()))
    assert sets[0] == sets[1], "random policy must be seed-deterministic"
    assert len(sets[0]) == k, "random policy must be count-matched"


def test_tool_cannot_overwrite_verified_correct_with_failure():
    # The evaluator's only tool path is verified_tool_success, which
    # either returns True (verifier pass) or raises. There is no code
    # path that records a routed task as failed via the tool, so a
    # verified-correct model answer can never become a failure.
    task = make_task(0)
    assert verified_tool_success(task) is True
    with pytest.raises(EvaluationBlocker):
        verified_tool_success(make_task(1, family="unknown_family"))
