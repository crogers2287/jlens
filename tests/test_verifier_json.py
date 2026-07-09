#!/usr/bin/env python3
"""Tests for the M12 JSON verifier + reviewed calibration. CPU-only, no network.

(a) json_object_check passes valid JSON (incl trailing whitespace/prose) and
    required-key checks, fails invalid JSON / missing keys / wrong type;
(b) routing — json_check tasks run json_object_check (not regex), regex tasks
    still run regex_or_schema_check;
(c) reviewed aggregate has NO text keys + agreement computed from a SYNTHETIC
    reviewed fixture;
(d) before/after — the JSON row flips wrong->ok under json_object_check and
    escalation drops by 1.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import verifiers as VZ  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402
import agents_a1_run_report as REP  # noqa: E402

CFG = SUP.load_config(str(ROOT / "config/agents_a1_shadow_run.json"))


# ---- (a) json_object_check verdicts ------------------------------------------
def test_json_object_check_cases():
    P, F = VZ.VERDICT_PASS, VZ.VERDICT_FAIL
    assert VZ.json_object_check('{"result":"success"}')["verdict"] == P
    assert VZ.json_object_check('{ "result": "success" }\n\nHope that helps!')["verdict"] == P
    assert VZ.json_object_check('```json\n{"a":1}\n```')["verdict"] == P
    assert VZ.json_object_check('  {"result":"ok"}  ', required_keys=["result"])["verdict"] == P
    assert VZ.json_object_check('{"other":1}', required_keys=["result"])["verdict"] == F
    assert VZ.json_object_check('not json')["verdict"] == F
    assert VZ.json_object_check('{"broken":')["verdict"] == F
    assert VZ.json_object_check('[1,2,3]', expected_type="array")["verdict"] == P
    assert VZ.json_object_check('{"a":1}', expected_type="array")["verdict"] == F
    # evidence is hashed, no raw text
    ev = VZ.json_object_check('{"TOKEN":"VAL"}', required_keys=["TOKEN"])["evidence_hash"]
    assert ev.startswith("[h:") and "VAL" not in ev and "TOKEN" not in ev


# ---- (b) routing -------------------------------------------------------------
def test_routing_json_vs_regex():
    json_task = {"prompt_id": "j", "prompt": "Return JSON", "task_category": "json",
                 "json_check": True, "json_required": ["result"]}
    names = [r["name"] for r in SUP._run_verifiers(json_task, '{"result":"ok"} ok', ['{"result":"ok"} ok'], CFG)]
    assert "json_object_check" in names and "regex_or_schema_check" not in names
    regex_task = {"prompt_id": "z", "prompt": "zip", "task_category": "format",
                  "pattern": r"\b\d{5}\b"}
    names2 = [r["name"] for r in SUP._run_verifiers(regex_task, "90210", ["90210"], CFG)]
    assert "regex_or_schema_check" in names2 and "json_object_check" not in names2


# ---- (c) reviewed aggregate: no text + agreement from synthetic --------------
def _rec(pid, auto_wrong, human_wrong):
    return {
        "prompt_id": pid, "policy": None, "mode": "shadow", "telemetry_missing": True,
        "prompt_preview": "SECRET", "output_preview": "SECRET",
        "outcome": {"user_agreed": None, "was_wrong": human_wrong,
                    "needed_retrieval": None, "needed_checker": None, "notes": None},
        "review_meta": {"reviewer": "op", "reviewed_at": None,
                        "review_source": "operator_review", "review_confidence": 1.0},
        "auto_outcome": {"auto_judged": True, "auto_was_wrong": auto_wrong,
                         "auto_needed_retrieval": None, "auto_needed_checker": None,
                         "verifier_names": ["json_object_check"], "verifier_confidence": 0.85,
                         "verifier_evidence_hash": "[h:0]", "escalate_for_review": True,
                         "auto_notes_redacted": None},
    }


def _no_text(obj):
    if isinstance(obj, dict):
        assert "prompt_preview" not in obj and "output_preview" not in obj
        for k, v in obj.items():
            assert not (k in REP.FORBIDDEN_KEYS and isinstance(v, str))
            _no_text(v)
    elif isinstance(obj, list):
        for v in obj:
            _no_text(v)


def test_reviewed_aggregate_no_text_and_agreement():
    fx = [_rec("a", True, False),   # auto wrong, human right -> disagree
          _rec("b", False, False),  # auto ok, human right -> agree
          _rec("c", None, False)]   # auto undecided -> not compared
    summ = REP.summarize(fx)
    _no_text(summ)
    ag = summ["auto_vs_human_agreement"]
    assert ag["n_compared"] == 2 and ag["agreement_rate"] == 0.5
    assert summ["human_reviewed_count"] == 3


# ---- (d) before/after: JSON row flips wrong->ok, escalation drops -------------
def test_json_verifier_flips_and_deescalates():
    rep = '{ "result": "success" }\n\nThis returns a single-key JSON object.'
    old = VZ.regex_or_schema_check(rep, pattern=r"^\{.*\}$")["verdict"]
    task = {"prompt_id": "sm_regex_01", "prompt": "Return a JSON object",
            "task_category": "json", "json_check": True, "json_required": ["result"]}
    res = SUP._run_verifiers(task, rep, [rep], CFG)
    new = next(r["verdict"] for r in res if r["name"] == "json_object_check")
    auto = SUP._build_auto_outcome(res, None, CFG)
    assert old == VZ.VERDICT_FAIL       # old regex full-anchor rejected valid JSON
    assert new == VZ.VERDICT_PASS       # json verifier accepts it
    assert auto["auto_was_wrong"] is False   # flips wrong -> ok
    assert auto["escalate_for_review"] is False  # and no longer escalates


TESTS = [test_json_object_check_cases, test_routing_json_vs_regex,
         test_reviewed_aggregate_no_text_and_agreement,
         test_json_verifier_flips_and_deescalates]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] verifier-json tests PASSED ({len(TESTS)} tests)")
