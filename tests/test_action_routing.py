#!/usr/bin/env python3
"""Tests for M16 metadata cleanup + read-only action routing. CPU-only, no net.

(a) validator flags a numeric-looking exact row missing metadata + passes the
    cleaned M15 batch;
(b) generator normalization tags numeric exact rows -> route to numeric_tolerant_check;
(c) action_record_v1 validates good records + rejects bad enum/unknown fields;
(d) action_router — current-info->retrieval_needed, math/numeric->checker_needed
    (approved), escalated explain->review_needed, clean->no_action, checker-with-no-
    approved->skipped; all schema-valid;
(e) before/after + action summary artifacts have no text keys.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import validate_task_metadata as VM  # noqa: E402
import gen_m13_batch as M13  # noqa: E402
import action_router as AR  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402
import agents_a1_run_report as REP  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

AV = Draft7Validator(json.loads((ROOT / "schema/action_record_v1.json").read_text()))


# ---- (a) validator ------------------------------------------------------------
def test_validator_flags_and_passes():
    gap = [{"prompt_id": "x", "task_category": "exact_answer", "known_answer": "300000"}]
    issues = VM.validate(gap)
    assert issues.get("numeric_metadata_gap") == ["x"]
    # non-numeric answer not flagged
    assert not VM.validate([{"prompt_id": "p", "task_category": "exact_answer",
                             "known_answer": "Paris"}])
    # the cleaned M15 batch is clean
    rows = [json.loads(l) for l in open(ROOT / "data/prompts/agents_a1_m15_batch.jsonl")]
    assert VM.validate(rows) == {}


# ---- (b) generator normalization ---------------------------------------------
def test_normalization_tags_and_routes():
    r = M13.normalize_numeric_metadata(
        {"task_category": "exact_answer", "known_answer": "300000"})
    assert r["numeric"] is True and r["expected_value"] == 300000
    # non-numeric untouched
    assert "numeric" not in M13.normalize_numeric_metadata(
        {"task_category": "exact_answer", "known_answer": "Paris"})
    # a tagged row routes to numeric_tolerant_check (not exact_answer_match)
    task = {"prompt_id": "n", "prompt": "km/s", **r}
    names = [x["name"] for x in SUP._run_verifiers(task, "299,792 km/s", ["299,792 km/s"], {"verifiers": {}})]
    assert "numeric_tolerant_check" in names and "exact_answer_match" not in names


# ---- (c) action_record_v1 schema ---------------------------------------------
def test_action_record_schema():
    Draft7Validator.check_schema(json.loads((ROOT / "schema/action_record_v1.json").read_text()))
    good = {"task_id": "t", "action_type": "no_action", "reason_code": "clean",
            "source_verifier": None, "confidence": None, "status": "planned",
            "evidence_hash": None}
    assert not list(AV.iter_errors(good))
    assert list(AV.iter_errors({**good, "action_type": "delete_all"}))
    assert list(AV.iter_errors({**good, "status": "running"}))
    assert list(AV.iter_errors({**good, "surprise": 1}))


# ---- (d) action_router --------------------------------------------------------
def _auto(pid, **over):
    a = {"auto_judged": True, "auto_was_wrong": None, "auto_needed_retrieval": None,
         "auto_needed_checker": None, "verifier_names": [], "verifier_confidence": 0.7,
         "verifier_evidence_hash": "[h:0]", "escalate_for_review": False,
         "auto_notes_redacted": None}
    a.update(over)
    return {"prompt_id": pid, "auto_outcome": a}


def test_action_router_cases():
    cases = [
        (_auto("c", auto_needed_retrieval=True), "retrieval_needed", "planned"),
        (_auto("m", auto_needed_checker=True, verifier_names=["math_checker"]),
         "checker_needed", "planned"),
        (_auto("k", auto_needed_checker=True, verifier_names=["explain_rubric_check"]),
         "checker_needed", "skipped"),
        (_auto("e", escalate_for_review=True), "review_needed", "planned"),
        (_auto("z"), "no_action", "planned"),
    ]
    for rec, want_type, want_status in cases:
        a = AR.route(rec)
        assert a["action_type"] == want_type and a["status"] == want_status
        assert not list(AV.iter_errors(a))


# ---- (e) M16 aggregate artifacts have no text keys ---------------------------
def test_m16_artifacts_no_text():
    for name in ("agents_a1_m16_metadata_beforeafter_sample.json",
                 "agents_a1_m16_action_summary_sample.json"):
        p = ROOT / "reports/outcomes" / name
        if not p.exists():
            continue
        obj = json.loads(p.read_text())

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    assert not (k in REP.FORBIDDEN_KEYS and isinstance(v, str))
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(obj)


TESTS = [test_validator_flags_and_passes, test_normalization_tags_and_routes,
         test_action_record_schema, test_action_router_cases, test_m16_artifacts_no_text]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] action-routing tests PASSED ({len(TESTS)} tests)")
