#!/usr/bin/env python3
"""Tests for the M10 autonomous shadow supervisor. CPU-only, no network.

Covers: (a) fake-endpoint supervisor run yields auto_outcome_v1-valid records;
(b) each verifier adapter's verdict/confidence on a fixture + hashed evidence;
(c) auto_outcome_v1 schema validates good records and rejects bad/unknown fields;
(d) aggregate summary has NO text-preview/notes keys + correct counts/escalation;
(e) auto judgments NEVER populate human outcome/review_meta fields.

All endpoints are FAKE in-process callables; no real model, no network.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from jsonschema import Draft7Validator  # noqa: E402
import verifiers as VZ  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402
import autonomous_outcome_report as REP  # noqa: E402

SCHEMA = json.loads((ROOT / "schema/auto_outcome_v1.json").read_text())
V = Draft7Validator(SCHEMA)
CFG = json.loads((ROOT / "config/autonomous_supervisor_v0.json").read_text())

TASKS = [
    {"prompt_id": "m1", "prompt": "What is 6*7?", "task_category": "math",
     "known_answer": "42", "expression": "6*7"},
    {"prompt_id": "e1", "prompt": "Capital of France?",
     "task_category": "exact_answer", "known_answer": "Paris"},
    {"prompt_id": "f1", "prompt": "current price of gold today",
     "task_category": "current_info"},
]


# ---- (b) verifier adapters ---------------------------------------------------
def test_verifier_adapters():
    assert VZ.exact_answer_match("It is Paris.", "Paris")["verdict"] == VZ.VERDICT_PASS
    assert VZ.exact_answer_match("London", "Paris")["verdict"] == VZ.VERDICT_FAIL
    assert VZ.math_checker("= 42", expression="6*7")["verdict"] == VZ.VERDICT_PASS
    assert VZ.math_checker("= 41", expression="6*7")["verdict"] == VZ.VERDICT_FAIL
    assert VZ.regex_or_schema_check('{"k":1}', r'^\{.*\}$')["verdict"] == VZ.VERDICT_PASS
    assert VZ.retrieval_required_heuristic("x", task_category="current_info")["verdict"] == VZ.VERDICT_FAIL
    # self-consistency: disagreement is UNDECIDED (escalation), never FAIL
    dis = VZ.self_consistency(["42", "7", "42"])
    assert dis["verdict"] == VZ.VERDICT_UNDECIDED and dis["confidence"] < 1.0
    assert VZ.self_consistency(["42", "42"])["verdict"] == VZ.VERDICT_PASS
    # code stub runs a trusted fixture callable only
    assert VZ.code_test_stub("ok", fixture_test=lambda o: "ok" in o)["verdict"] == VZ.VERDICT_PASS
    assert VZ.code_test_stub("x")["verdict"] == VZ.VERDICT_UNDECIDED  # no fixture -> no-op
    # evidence is a hash, never raw text
    ev = VZ.exact_answer_match("TOKENVALUE here", "TOKENVALUE here")["evidence_hash"]
    assert ev.startswith("[h:") and "TOKENVALUE" not in ev


# ---- (a) fake-endpoint supervisor run + (e) human fields untouched ----------
def _wrong_endpoint(prompt):
    return "the answer is 999"  # deterministic FAKE: wrong number + wrong text


def test_supervisor_run_valid_and_human_untouched():
    records = SUP.run(CFG, TASKS, _wrong_endpoint, tempfile.mktemp(suffix=".jsonl"),
                      validator=V)
    assert len(records) == 3
    for r in records:
        assert not list(V.iter_errors(r))                 # (a) schema-valid
        assert r["telemetry_missing"] is True             # fake/GGUF: no telemetry
        assert r["policy"] is None
        # (e) auto NEVER writes human fields
        assert all(v is None for v in r["outcome"].values())
        assert all(v is None for v in r["review_meta"].values())
    # the always-wrong math + exact tasks must be judged wrong and escalated
    m1 = next(r for r in records if r["prompt_id"] == "m1")
    assert m1["auto_outcome"]["auto_was_wrong"] is True
    assert m1["auto_outcome"]["escalate_for_review"] is True
    # the current-info task must flag retrieval
    f1 = next(r for r in records if r["prompt_id"] == "f1")
    assert f1["auto_outcome"]["auto_needed_retrieval"] is True


# ---- (c) schema accepts good, rejects bad -----------------------------------
def test_schema_good_and_bad():
    Draft7Validator.check_schema(SCHEMA)
    good = SUP.run_task(TASKS[0], _wrong_endpoint, CFG)
    assert not list(V.iter_errors(good))
    bad_unknown = json.loads(json.dumps(good)); bad_unknown["surprise"] = 1
    assert list(V.iter_errors(bad_unknown))
    bad_auto = json.loads(json.dumps(good)); bad_auto["auto_outcome"]["made_up"] = True
    assert list(V.iter_errors(bad_auto))
    bad_conf = json.loads(json.dumps(good)); bad_conf["auto_outcome"]["verifier_confidence"] = 2.0
    assert list(V.iter_errors(bad_conf))
    bad_tel = json.loads(json.dumps(good)); bad_tel["telemetry_missing"] = "yes"
    assert list(V.iter_errors(bad_tel))


# ---- (d) aggregate summary: no text + correct counts/escalation -------------
def _no_text(obj, where="root"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            assert not (k in REP.FORBIDDEN_KEYS and isinstance(v, str)), f"text at {where}.{k}"
            assert "prompt_preview" not in obj and "output_preview" not in obj
            _no_text(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _no_text(v, f"{where}[{i}]")


def test_aggregate_summary_no_text_and_counts():
    records = SUP.run(CFG, TASKS, _wrong_endpoint, tempfile.mktemp(suffix=".jsonl"))
    summ = REP.summarize(records)
    _no_text(summ)
    assert summ["n_total"] == 3
    assert summ["n_telemetry_missing"] == 3
    assert summ["level_distribution"] == {"unscored": 3}
    # m1 (math wrong) and e1 (exact wrong) escalate; f1 (retrieval-only) does not
    assert summ["escalation"]["count"] == 2
    assert summ["auto_field_nonnull_counts"]["auto_was_wrong"] == 2
    # no human reviews yet -> agreement is null, never fabricated
    assert summ["auto_vs_human_agreement"] is None


def test_agreement_only_over_reviewed():
    records = SUP.run(CFG, TASKS, _wrong_endpoint, tempfile.mktemp(suffix=".jsonl"))
    # SYNTHETIC human review on one record (a human would do this, not the auto loop)
    records[0]["outcome"]["was_wrong"] = True   # matches auto_was_wrong=True
    summ = REP.summarize(records)
    ag = summ["auto_vs_human_agreement"]
    assert ag is not None and ag["n_compared"] == 1 and ag["agreement_rate"] == 1.0


TESTS = [test_verifier_adapters,
         test_supervisor_run_valid_and_human_untouched,
         test_schema_good_and_bad,
         test_aggregate_summary_no_text_and_counts,
         test_agreement_only_over_reviewed]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] autonomous-supervisor tests PASSED ({len(TESTS)} tests)")
