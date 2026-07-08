#!/usr/bin/env python3
"""Fixture tests for the M7 local shadow wrapper. NO real network."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
import local_shadow_wrapper as W  # noqa: E402
from policy_engine import PolicyEngine  # noqa: E402

V0_ACTIONS = {"answer_locally", "verify", "retrieve", "run_checker",
              "ask_user", "require_confirmation"}
REQ = {"prompt_id", "model", "feature_source", "prompt_preview",
       "output_preview", "policy", "policy_note", "mode", "outcome"}
OUTCOME = {"user_agreed", "was_wrong", "needed_retrieval", "needed_checker", "notes"}


def _engine():
    return PolicyEngine()


def test_dryrun_record_shape_and_null_outcomes():
    eng = _engine()
    feats = W.load_feature_rows(eng.features_path)
    pid = next(iter(feats))
    rec = W.build_record(pid, "hello", W.dry_run_output("hello"),
                         "dry-run-fixture", feats, eng)
    assert REQ <= set(rec)
    assert set(rec["outcome"]) == OUTCOME
    assert all(v is None for v in rec["outcome"].values())
    assert rec["mode"] == "shadow"


def test_policy_scored_when_feature_row_exists():
    eng = _engine()
    feats = W.load_feature_rows(eng.features_path)
    pid = next(iter(feats))
    rec = W.build_record(pid, "hi", "out", "m", feats, eng)
    assert rec["policy"] is not None
    assert rec["policy"]["recommended_action"] in V0_ACTIONS
    assert rec["policy_note"] is None


def test_policy_null_when_no_feature_row():
    eng = _engine()
    feats = W.load_feature_rows(eng.features_path)
    rec = W.build_record("no_such_id_xyz", "hi", "out", "m", feats, eng)
    assert rec["policy"] is None
    assert rec["policy_note"] == W.NO_TELEMETRY_NOTE
    assert rec["feature_source"] is None


def test_live_mode_uses_stubbed_http_no_real_network(monkeypatch=None):
    """live_output must go through the HTTP client — stub it; assert no real call."""
    calls = {"n": 0}

    class _FakeResp:
        def json(self):
            return {"choices": [{"message": {"content": "STUBBED"}}]}

    def _fake_post(url, json=None, headers=None, timeout=None):
        calls["n"] += 1
        assert url.endswith("/chat/completions")
        return _FakeResp()

    import requests
    orig = requests.post
    requests.post = _fake_post
    try:
        out = W.live_output("prompt", {"base_url": "http://localhost:9069/v1",
                                       "model": "x", "api_key": "not-needed"})
    finally:
        requests.post = orig
    assert out == "STUBBED" and calls["n"] == 1


if __name__ == "__main__":
    test_dryrun_record_shape_and_null_outcomes()
    test_policy_scored_when_feature_row_exists()
    test_policy_null_when_no_feature_row()
    test_live_mode_uses_stubbed_http_no_real_network()
    print("[jlens] local shadow wrapper tests PASSED (4 tests)")
