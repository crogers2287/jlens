#!/usr/bin/env python3
"""Tests for the M13 larger Agents-A1 run harness. CPU-only, no network.

(a) the m13 batch validates (100-250, unique ids, all 6 categories, required
    fields per category);
(b) aggregate report over a SYNTHETIC m13-shaped fixture has NO text keys +
    correct counts;
(c) resume — a second run over the same out-log adds zero (fake endpoint);
(d) the comparison report shape has the expected keys + no text.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import gen_m13_batch as GEN  # noqa: E402
import agents_a1_run_report as REP  # noqa: E402
import run_agents_a1_shadow_batch as RUN  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402
from jsonschema import Draft7Validator  # noqa: E402

CATS = {"math", "exact_answer", "json", "regex", "current_info", "explain"}
V = Draft7Validator(json.loads((ROOT / "schema/auto_outcome_v1.json").read_text()))


# ---- (a) batch validation ----------------------------------------------------
def test_m13_batch_valid():
    rows = GEN.build()
    assert 100 <= len(rows) <= 250
    ids = [r["prompt_id"] for r in rows]
    assert len(set(ids)) == len(ids)
    cats = set(r["task_category"] for r in rows)
    assert cats == CATS, cats
    for r in rows:
        assert r.get("prompt_id") and r.get("prompt")
        c = r["task_category"]
        if c == "math":
            assert r.get("known_answer") and r.get("expression")
        elif c == "exact_answer":
            assert r.get("known_answer")
        elif c == "json":
            assert r.get("json_check") and r.get("json_required")
        elif c == "regex":
            assert r.get("pattern")
    # deterministic: build twice, identical
    assert GEN.build() == rows


# ---- (b) aggregate report over synthetic m13-shaped fixture ------------------
def _rec(pid, cat, wrong=None, esc=False, retr=None, chk=None):
    return {
        "prompt_id": pid, "model": "agents-a1", "policy": None, "mode": "shadow",
        "telemetry_missing": True, "task_category": cat,
        "prompt_preview": "SECRET", "output_preview": "SECRET",
        "outcome": {"user_agreed": None, "was_wrong": None, "needed_retrieval": None,
                    "needed_checker": None, "notes": None},
        "review_meta": {"reviewer": None, "reviewed_at": None,
                        "review_source": None, "review_confidence": None},
        "auto_outcome": {"auto_judged": True, "auto_was_wrong": wrong,
                         "auto_needed_retrieval": retr, "auto_needed_checker": chk,
                         "verifier_names": ["math_checker"], "verifier_confidence": 0.7,
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


def test_aggregate_no_text_and_counts():
    fx = [_rec("a", "math", wrong=False, chk=True),
          _rec("b", "math", wrong=True, esc=True, chk=True),
          _rec("c", "current_info", retr=True),
          _rec("d", "explain", esc=True)]
    summ = REP.summarize(fx, {"run_id": "x", "n_tasks": 4, "n_failed": 0})
    _no_text(summ)
    assert summ["n_completed"] == 4
    assert summ["escalation_count"] == 2
    assert summ["auto_was_wrong_count"] == 1
    assert summ["auto_needed_retrieval_count"] == 1
    assert summ["auto_needed_checker_count"] == 2
    assert summ["auto_vs_human_agreement"] is None


# ---- (c) resume adds nothing -------------------------------------------------
def test_resume_adds_zero():
    cfg = SUP.load_config(str(ROOT / "config/agents_a1_m13_run.json"))
    with tempfile.TemporaryDirectory() as d:
        out = str(Path(d) / "run.jsonl")
        model = lambda p: "the answer is 999"  # noqa: E731  deterministic fake
        m1 = RUN.run_batch(cfg, model, out, validator=V,
                           source_path=str(ROOT / "data/prompts/agents_a1_m13_batch.jsonl"))
        n1 = sum(1 for _ in open(out))
        m2 = RUN.run_batch(cfg, model, out, validator=V,
                           source_path=str(ROOT / "data/prompts/agents_a1_m13_batch.jsonl"))
        n2 = sum(1 for _ in open(out))
        assert n1 == n2 and m2["n_completed_this_run"] == 0
        # bounded by batch.size
        assert m1["n_completed_this_run"] <= cfg["batch"]["size"]


# ---- (d) comparison report shape --------------------------------------------
def test_comparison_report_shape():
    # the committed comparison report is counts-only, no text
    p = ROOT / "reports/outcomes/agents_a1_m13_vs_baseline.json"
    if not p.exists():
        return  # generated in step 6; skip if not yet present
    rep = json.loads(p.read_text())
    for side in ("baseline_m11_m12_25task", "m13_110task"):
        assert side in rep
        for k in ("n_tasks", "escalation_count", "escalation_rate",
                  "auto_was_wrong_count", "verifier_distribution"):
            assert k in rep[side]
    _no_text(rep)


TESTS = [test_m13_batch_valid, test_aggregate_no_text_and_counts,
         test_resume_adds_zero, test_comparison_report_shape]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] m13-larger-run tests PASSED ({len(TESTS)} tests)")
