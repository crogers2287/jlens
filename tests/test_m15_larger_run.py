#!/usr/bin/env python3
"""Tests for the M15 larger Agents-A1 run harness. CPU-only, no network.

(a) the m15 batch validates (250-500, unique ids, all category types incl numeric
    + explain-rubric, required fields per category);
(b) aggregate report over a SYNTHETIC m15-shaped fixture has NO text keys +
    correct counts incl verifier_distribution;
(c) resume — a second run over the same out-log adds zero (fake endpoint), bounded
    by batch.size;
(d) the comparison report has the expected keys (M15/M13/baseline) + no text.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import gen_m15_batch as GEN  # noqa: E402
import agents_a1_run_report as REP  # noqa: E402
import run_agents_a1_shadow_batch as RUN  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

V = Draft7Validator(json.loads((ROOT / "schema/auto_outcome_v1.json").read_text()))


# ---- (a) batch validation ----------------------------------------------------
def test_m15_batch_valid():
    rows = GEN.build()
    assert 250 <= len(rows) <= 500
    ids = [r["prompt_id"] for r in rows]
    assert len(set(ids)) == len(ids)
    # category TYPES present incl numeric + explain-rubric
    types = set()
    for r in rows:
        if r.get("numeric"):
            types.add("numeric")
        elif r.get("required_facts"):
            types.add("explain-rubric")
        else:
            types.add(r["task_category"])
    assert {"math", "exact_answer", "numeric", "json", "regex",
            "current_info", "explain", "explain-rubric"} <= types, types
    for r in rows:
        assert r.get("prompt_id") and r.get("prompt")
        if r.get("numeric"):
            assert r.get("expected_value") is not None
        elif r.get("required_facts") is not None:
            assert r["required_facts"]
        elif r["task_category"] == "math":
            assert r.get("known_answer") and r.get("expression")
    assert GEN.build() == rows  # deterministic


# ---- (b) aggregate over synthetic m15-shaped fixture -------------------------
def _rec(pid, wrong=None, esc=False, retr=None, chk=None, verifiers=("math_checker",)):
    return {
        "prompt_id": pid, "model": "agents-a1", "policy": None, "mode": "shadow",
        "telemetry_missing": True, "prompt_preview": "SECRET", "output_preview": "SECRET",
        "outcome": {"user_agreed": None, "was_wrong": None, "needed_retrieval": None,
                    "needed_checker": None, "notes": None},
        "review_meta": {"reviewer": None, "reviewed_at": None,
                        "review_source": None, "review_confidence": None},
        "auto_outcome": {"auto_judged": True, "auto_was_wrong": wrong,
                         "auto_needed_retrieval": retr, "auto_needed_checker": chk,
                         "verifier_names": list(verifiers), "verifier_confidence": 0.7,
                         "verifier_evidence_hash": "[h:0]", "escalate_for_review": esc,
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


def test_aggregate_no_text_and_verifier_dist():
    fx = [_rec("a", wrong=False, verifiers=("numeric_tolerant_check",)),
          _rec("b", wrong=True, esc=True, verifiers=("exact_answer_match",)),
          _rec("c", esc=True, verifiers=("explain_rubric_check",))]
    summ = REP.summarize(fx, {"run_id": "x", "n_tasks": 3, "n_failed": 0})
    _no_text(summ)
    assert summ["n_completed"] == 3
    assert summ["escalation_count"] == 2
    assert summ["auto_was_wrong_count"] == 1
    assert summ["verifier_distribution"]["numeric_tolerant_check"] == 1
    assert summ["verifier_distribution"]["explain_rubric_check"] == 1


# ---- (c) resume adds nothing -------------------------------------------------
def test_resume_adds_zero():
    cfg = SUP.load_config(str(ROOT / "config/agents_a1_m15_run.json"))
    with tempfile.TemporaryDirectory() as d:
        out = str(Path(d) / "run.jsonl")
        model = lambda p: "the answer is 999"  # noqa: E731  deterministic fake
        m1 = RUN.run_batch(cfg, model, out, validator=V,
                           source_path=str(ROOT / "data/prompts/agents_a1_m15_batch.jsonl"))
        n1 = sum(1 for _ in open(out))
        m2 = RUN.run_batch(cfg, model, out, validator=V,
                           source_path=str(ROOT / "data/prompts/agents_a1_m15_batch.jsonl"))
        n2 = sum(1 for _ in open(out))
        assert n1 == n2 and m2["n_completed_this_run"] == 0
        assert m1["n_completed_this_run"] <= cfg["batch"]["size"]  # bounded


# ---- (d) comparison report shape --------------------------------------------
def test_comparison_report_shape():
    p = ROOT / "reports/outcomes/agents_a1_m15_vs_baseline.json"
    if not p.exists():
        return  # generated in step 6; skip if not yet present
    rep = json.loads(p.read_text())
    for side in ("m15_261task", "m13_110task", "baseline_m11_m12_25task"):
        assert side in rep
        for k in ("n_tasks", "escalation_count", "escalation_rate",
                  "auto_was_wrong_count", "verifier_distribution"):
            assert k in rep[side]
    assert isinstance(rep.get("escalation_rate_trend"), list)
    _no_text(rep)


TESTS = [test_m15_batch_valid, test_aggregate_no_text_and_verifier_dist,
         test_resume_adds_zero, test_comparison_report_shape]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] m15-larger-run tests PASSED ({len(TESTS)} tests)")
