#!/usr/bin/env python3
"""Tests for the M11 Agents-A1 bounded shadow-run harness. CPU-only, no network.

Covers: (a) run config validates (keys/types, batch cap, run_id stable);
(b) RESUME — a second run over the same out-log adds no duplicate rows;
(c) aggregate report has NO text keys + correct metadata counts, agreement null
until a synthetic human review; (d) escalation queue = only escalated, human
fields null; (e) endpoint-failure path increments n_failed and continues.

All endpoints are FAKE in-process callables; no real model, no network.
"""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from jsonschema import Draft7Validator  # noqa: E402
import run_agents_a1_shadow_batch as RUN  # noqa: E402
import make_escalation_review_queue as EQ  # noqa: E402
import agents_a1_run_report as REP  # noqa: E402
import autonomous_shadow_supervisor as SUP  # noqa: E402

CFG = SUP.load_config(str(ROOT / "config/agents_a1_shadow_run.json"))
V = Draft7Validator(json.loads((ROOT / "schema/auto_outcome_v1.json").read_text()))
SMOKE = str(ROOT / "data/prompts/agents_a1_smoke_batch.jsonl")


def _wrong(prompt):
    return "the answer is 999"  # deterministic FAKE: wrong number + wrong text


def _cfg_to(tmp):
    c = json.loads(json.dumps(CFG))
    c["task_sources"] = [{"path": SMOKE, "kind": "public_smoke"}]
    return c


# ---- (a) config validation ---------------------------------------------------
def test_config_valid_and_run_id_stable():
    assert isinstance(CFG["endpoint"]["model"], str)
    assert CFG["endpoint"]["model"] == "InternScience/Agents-A1-Q8_0-GGUF"
    assert CFG["batch"]["size"] <= CFG["batch"]["cap"]
    assert isinstance(CFG["resume"]["enabled"], bool)
    a = RUN.config_run_id(CFG)
    b = RUN.config_run_id(json.loads(json.dumps(CFG)))
    assert a == b and len(a) == 16
    # batch bound: never loads more than size
    tasks, _ = RUN.load_batch(_cfg_to(None))
    assert len(tasks) <= CFG["batch"]["size"]


# ---- (b) resume --------------------------------------------------------------
def test_resume_adds_no_duplicates():
    with tempfile.TemporaryDirectory() as d:
        out = str(Path(d) / "run.jsonl")
        c = _cfg_to(d)
        m1 = RUN.run_batch(c, _wrong, out, validator=V)
        n1 = sum(1 for _ in open(out))
        m2 = RUN.run_batch(c, _wrong, out, validator=V)   # resume
        n2 = sum(1 for _ in open(out))
        assert n1 == n2, "resume must not add duplicate rows"
        assert m2["n_completed_this_run"] == 0
        assert m2["n_already_done_skipped"] == m1["n_tasks"]


# ---- (e) endpoint failure counts + continues --------------------------------
def test_failure_counts_and_continues():
    with tempfile.TemporaryDirectory() as d:
        out = str(Path(d) / "run.jsonl")
        def boom(p):
            raise RuntimeError("endpoint down")
        m = RUN.run_batch(_cfg_to(d), boom, out, validator=V)
        assert m["n_completed_this_run"] == 0
        assert m["n_failed"] == m["n_tasks"] and m["n_failed"] > 0  # counted, no crash


# ---- (d) escalation queue: only escalated, human fields null -----------------
def test_escalation_queue():
    with tempfile.TemporaryDirectory() as d:
        out = str(Path(d) / "run.jsonl")
        RUN.run_batch(_cfg_to(d), _wrong, out, validator=V)
        recs = [json.loads(l) for l in open(out)]
        queue = EQ.build(recs)
        run_esc = sum(1 for r in recs if r["auto_outcome"]["escalate_for_review"])
        assert len(queue) == run_esc and run_esc > 0
        for r in queue:
            assert r["auto_outcome"]["escalate_for_review"] is True
            assert all(v is None for v in r["outcome"].values())
            assert all(v is None for v in r["review_meta"].values())
            assert not list(V.iter_errors(r))  # still auto_outcome_v1-valid


# ---- (c) aggregate report: no text + counts + agreement ----------------------
def _no_text(obj, where="root"):
    if isinstance(obj, dict):
        assert "prompt_preview" not in obj and "output_preview" not in obj
        for k, v in obj.items():
            assert not (k in REP.FORBIDDEN_KEYS and isinstance(v, str)), f"text at {where}.{k}"
            _no_text(v, f"{where}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _no_text(v, f"{where}[{i}]")


def test_report_no_text_counts_and_agreement():
    with tempfile.TemporaryDirectory() as d:
        out = str(Path(d) / "run.jsonl")
        meta = RUN.run_batch(_cfg_to(d), _wrong, out, validator=V)
        recs = [json.loads(l) for l in open(out)]
        summ = REP.summarize(recs, meta)
        _no_text(summ)
        assert summ["n_completed"] == meta["n_completed_this_run"]
        assert summ["n_failed"] == 0
        assert summ["escalation_count"] == sum(
            1 for r in recs if r["auto_outcome"]["escalate_for_review"])
        assert summ["auto_vs_human_agreement"] is None   # no human review yet
        # SYNTHETIC human review on one escalated wrong row -> agreement appears
        wrong_row = next(r for r in recs
                         if r["auto_outcome"]["auto_was_wrong"] is True)
        wrong_row["outcome"]["was_wrong"] = True          # a human sets this
        summ2 = REP.summarize(recs, meta)
        ag = summ2["auto_vs_human_agreement"]
        assert ag is not None and ag["n_compared"] == 1 and ag["agreement_rate"] == 1.0


TESTS = [test_config_valid_and_run_id_stable,
         test_resume_adds_no_duplicates,
         test_failure_counts_and_continues,
         test_escalation_queue,
         test_report_no_text_counts_and_agreement]

if __name__ == "__main__":
    for t in TESTS:
        t()
    print(f"[jlens] agents-a1 shadow-run tests PASSED ({len(TESTS)} tests)")
