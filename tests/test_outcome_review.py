#!/usr/bin/env python3
"""Tests for the M8 outcome-review + calibration tooling. CPU-only, no network.

Uses SYNTHETIC in-memory fixtures for reviewed records — never written as real
reviewed data. Committed queues stay all-null.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from jsonschema import Draft7Validator  # noqa: E402
import build_review_queue as BQ  # noqa: E402
import outcome_report as OR  # noqa: E402

SCHEMA = json.loads((ROOT / "schema/shadow_outcome_v1.json").read_text())
V = Draft7Validator(SCHEMA)
NULL_OUT = {"user_agreed": None, "was_wrong": None, "needed_retrieval": None,
            "needed_checker": None, "notes": None}
NULL_META = {"reviewer": None, "reviewed_at": None, "review_source": None,
             "review_confidence": None}


def _rec(**over):
    r = {"prompt_id": "x", "policy": None, "outcome": dict(NULL_OUT),
         "review_meta": dict(NULL_META)}
    r.update(over)
    return r


def test_schema_accepts_null_and_reviewed_rejects_bad():
    Draft7Validator.check_schema(SCHEMA)
    assert not list(V.iter_errors(_rec()))  # all-null ok
    reviewed = _rec(outcome={**NULL_OUT, "was_wrong": True},
                    review_meta={**NULL_META, "reviewer": "t",
                                 "review_confidence": 0.8})
    assert not list(V.iter_errors(reviewed))  # reviewed ok
    assert list(V.iter_errors(_rec(outcome={**NULL_OUT, "was_wrong": "yes"})))
    assert list(V.iter_errors(_rec(outcome={**NULL_OUT, "made_up": True})))
    assert list(V.iter_errors(_rec(review_meta={**NULL_META,
                                                 "review_confidence": 2.0})))


def test_build_review_queue_all_null():
    shadow = {"prompt_id": "tqa_1", "policy": {"level": "low"}, "mode": "shadow"}
    rec = BQ.to_review_record(shadow)
    assert not list(V.iter_errors(rec))
    assert all(v is None for v in rec["outcome"].values())
    assert all(v is None for v in rec["review_meta"].values())


def test_review_cli_sets_field_on_fixture():
    # exercise the CLI on a THROWAWAY queue (not committed as real)
    import review_shadow_log as RS
    q = _rec(prompt_id="p1", policy={"level": "high"})
    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False) as fh:
        fh.write(json.dumps(q) + "\n")
        path = fh.name
    RS.main(["--queue", path, "--prompt-id", "p1", "--was-wrong", "true",
             "--reviewer", "tester", "--schema",
             str(ROOT / "schema/shadow_outcome_v1.json")])
    back = json.loads(open(path).readline())
    assert back["outcome"]["was_wrong"] is True
    assert back["review_meta"]["reviewer"] == "tester"
    assert not list(V.iter_errors(back))


def test_calibration_from_reviewed_only():
    fx = [
        _rec(policy={"level": "critical"},
             outcome={**NULL_OUT, "was_wrong": True},
             review_meta={**NULL_META, "reviewer": "t"}),   # wrong@critical -> TP
        _rec(policy={"level": "low"},
             outcome={**NULL_OUT, "was_wrong": True},
             review_meta={**NULL_META, "reviewer": "t"}),   # wrong@low -> FN
        _rec(policy={"level": "low"},
             outcome={**NULL_OUT, "was_wrong": False},
             review_meta={**NULL_META, "reviewer": "t"}),   # fine@low -> TN
        _rec(),  # unreviewed — must be excluded
    ]
    cov = OR.coverage(fx)
    assert cov["n_reviewed"] == 3 and cov["n_unreviewed"] == 1
    cal = OR.calibration(fx)
    assert cal["false_low_risk_rate"] == 0.5   # 1 FN / 2 positives
    assert cal["false_high_risk_rate"] == 0.0  # 0 FP / 1 negative
    assert cal["confusion"] == {"tp": 1, "fn": 1, "fp": 0, "tn": 1}


def test_calibration_pending_when_none_reviewed():
    assert OR.calibration([_rec(), _rec()]) is None


if __name__ == "__main__":
    test_schema_accepts_null_and_reviewed_rejects_bad()
    test_build_review_queue_all_null()
    test_review_cli_sets_field_on_fixture()
    test_calibration_from_reviewed_only()
    test_calibration_pending_when_none_reviewed()
    print("[jlens] outcome-review tests PASSED (5 tests)")
