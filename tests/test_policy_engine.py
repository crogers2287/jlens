#!/usr/bin/env python3
"""Tests for jlens PolicyEngine v0 (advisory/shadow). CPU-only, no GPU."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from policy_engine import PolicyEngine  # noqa: E402
from risk_runtime import shadow_entry  # noqa: E402

V0_ACTIONS = {"answer_locally", "verify", "retrieve", "run_checker",
              "ask_user", "require_confirmation"}


def test_config_loads_and_actions_valid():
    eng = PolicyEngine()
    cfg = eng.config
    assert cfg["mode"] == "shadow" and cfg["advisory"] is True
    assert cfg["gating"]["blocks_real_actions"] is False
    levels = [k for k in cfg["levels"] if not k.startswith("_")]
    assert set(levels) == {"low", "medium", "high", "critical"}
    for lv in levels:
        assert cfg["level_action_map"][lv] in V0_ACTIONS


def test_score_shape_on_real_row():
    eng = PolicyEngine()
    row = json.loads(open(eng.features_path, encoding="utf-8").readline())
    r = eng.score(row)
    assert {"prompt_id", "level", "scores", "recommended_action",
            "explanation"} <= set(r)
    assert set(r["scores"]) == set(eng.scored)
    assert all(0.0 <= v <= 1.0 for v in r["scores"].values())
    assert r["recommended_action"] in V0_ACTIONS
    assert r["level"] in {"low", "medium", "high", "critical"}


def test_level_action_mapping_at_bands():
    eng = PolicyEngine()
    # drive _level directly across representative risk values
    cases = {0.10: "low", 0.45: "medium", 0.65: "high", 0.90: "critical"}
    for risk, want in cases.items():
        lv = eng._level(risk)
        assert lv == want, f"risk {risk} -> {lv}, expected {want}"
        assert eng.config["level_action_map"][lv] in V0_ACTIONS


def test_shadow_entry_shape_and_write():
    eng = PolicyEngine()
    row = json.loads(open(eng.features_path, encoding="utf-8").readline())
    entry = shadow_entry(eng.score(row), "feat.jsonl", ts="unset")
    req = {"ts_placeholder", "prompt_id", "feature_source", "scores", "level",
           "recommended_action", "mode", "outcome_note"}
    assert req <= set(entry)
    assert entry["mode"] == "shadow" and entry["outcome_note"] is None
    # round-trips through a written line
    with tempfile.NamedTemporaryFile("w+", suffix=".jsonl", delete=False) as fh:
        fh.write(json.dumps(entry) + "\n")
        path = fh.name
    back = json.loads(open(path).readline())
    assert back == entry


if __name__ == "__main__":
    test_config_loads_and_actions_valid()
    test_score_shape_on_real_row()
    test_level_action_mapping_at_bands()
    test_shadow_entry_shape_and_write()
    print("[jlens] PolicyEngine v0 tests PASSED (4 tests)")
