"""Steer-821e430 conformance tests for the M37J-C smoke harness.

Synthetic fixtures only; no engine, no live prompts.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from m37jc_smoke import (CLEANUP_STEPS, SmokeBlocked, check_authoritative,
                         check_identity, divergence_stats,
                         envelope_from_artifact, finalize_outcome,
                         run_cleanup, within_envelope)

ARTIFACT = {"detail": {
    "parity_envelope": {"margin_prompts": 2, "first_divergence_floor": 8},
    "baseline_determinism": {"stock_repeat_divergence": {
        "prompts_differing": 5, "first_divergence_min": 13,
        "first_divergence_mean": 122.8}}}}


def good_fetch(rank, authoritative, readout=True):
    return {"rank": rank, "authoritative": authoritative,
            "projection_calls": 12, "captured_slots": [3, 3, 3, 3, 3],
            "readout": ({"4": {"steps": [31], "token_ids": [[1, 2]],
                               "finite": True}} if readout else {})}


# 1. envelope: exact frozen fields, floor 8 used (not baseline min 13)
def test_envelope_uses_frozen_floor():
    env = envelope_from_artifact(ARTIFACT)
    assert env["first_divergence_floor"] == 8
    # divergence at 9 is EARLIER than baseline min 13 but within floor 8
    assert within_envelope({"prompts_differing": 5,
                            "first_divergence_min": 9}, env)
    assert not within_envelope({"prompts_differing": 5,
                                "first_divergence_min": 7}, env)
    assert not within_envelope({"prompts_differing": 8,
                                "first_divergence_min": 20}, env)
    assert within_envelope({"prompts_differing": 7,
                            "first_divergence_min": None}, env)


def test_envelope_field_mismatch_blocks():
    bad = {"detail": {"parity_envelope": {"margin_prompts": 2},
                      "baseline_determinism": ARTIFACT["detail"][
                          "baseline_determinism"]}}
    with pytest.raises(SmokeBlocked):
        envelope_from_artifact(bad)


# 2. dispatch identity per rank
def test_identity_all_ranks_zero_passes():
    s = [{"rank": 0, "id_mismatch_total": 0, "dispatch_missed_total": 0},
         {"rank": 1, "id_mismatch_total": 0, "dispatch_missed_total": 0}]
    assert check_identity(s, 2)["ok"]


def test_identity_nonzero_on_nonroot_rank_fails():
    s = [{"rank": 0, "id_mismatch_total": 0, "dispatch_missed_total": 0},
         {"rank": 1, "id_mismatch_total": 3, "dispatch_missed_total": 0}]
    r = check_identity(s, 2)
    assert not r["ok"] and r["id_mismatch_max"] == 3


def test_identity_missing_or_duplicate_rank_fails():
    one = [{"rank": 0, "id_mismatch_total": 0, "dispatch_missed_total": 0}]
    assert not check_identity(one, 2)["ok"]
    dup = one + [dict(one[0])]
    assert not check_identity(dup, 2)["ok"]


# 5. authoritative conformance
def test_multiple_authoritative_ranks_must_agree():
    a, b = good_fetch(0, True), good_fetch(1, True)
    assert check_authoritative([a, b])["ok"]
    b2 = good_fetch(1, True)
    b2["readout"]["4"]["token_ids"] = [[9, 9]]
    assert not check_authoritative([a, b2])["ok"]


def test_nonauthoritative_leak_fails():
    a = good_fetch(0, True)
    leak = good_fetch(1, False, readout=True)   # non-auth WITH readout
    r = check_authoritative([a, leak])
    assert not r["ok"] and not r["non_authoritative_leak_free"]


def test_no_authoritative_rank_fails():
    r = check_authoritative([good_fetch(0, False, readout=False),
                             good_fetch(1, False, readout=False)])
    assert not r["ok"]


def test_unequal_calls_or_slots_fails():
    a, b = good_fetch(0, True), good_fetch(1, False, readout=False)
    b["projection_calls"] = 11
    assert not check_authoritative([a, b])["ok"]
    b["projection_calls"] = 12
    b["captured_slots"] = [3, 3, 3, 3, 2]
    assert not check_authoritative([a, b])["ok"]


# 3. cleanup: ordered, per-rank verified, exception-safe
class FakeLLM:
    def __init__(self, fail_step=None, raise_step=None, ranks=2):
        self.calls = []
        self.fail_step, self.raise_step, self.ranks = (fail_step,
                                                       raise_step, ranks)

    def collective_rpc(self, method, args=()):
        self.calls.append(method)
        if method == self.raise_step:
            raise RuntimeError("rpc failure")
        expect = {"jlens_bridge_set_enabled": False,
                  "jlens_set_telemetry_enabled": False,
                  "jlens_bridge_uninstall": True,
                  "jlens_uninstall_telemetry": True}[method]
        if method == self.fail_step:
            return [expect, not expect]     # one rank misbehaves
        return [expect] * self.ranks


def test_cleanup_order_and_success():
    llm = FakeLLM()
    r = run_cleanup(llm, 2)
    assert r["ok"]
    assert llm.calls == [s[0] for s in CLEANUP_STEPS]


def test_cleanup_rank_failure_blocks():
    r = run_cleanup(FakeLLM(fail_step="jlens_bridge_uninstall"), 2)
    assert not r["ok"]


def test_cleanup_exception_blocks_but_continues():
    llm = FakeLLM(raise_step="jlens_set_telemetry_enabled")
    r = run_cleanup(llm, 2)
    assert not r["ok"]
    assert llm.calls == [s[0] for s in CLEANUP_STEPS]  # later steps still ran


# 1+6. restoration gate as boolean; state transitions
def technical(outcome="technical_gates_passed_pending_restore"):
    return {"outcome": outcome,
            "gates": {"disabled_path_within_envelope": True}}


def test_finalize_pass_requires_restore_true():
    final = finalize_outcome(technical(), True, {"reply_expected": True})
    assert final["outcome"] == "passed"
    assert final["gates"]["serving_restored_and_verified"] is True


def test_finalize_restore_failure_blocks():
    final = finalize_outcome(technical(), False, {"error": "URLError"})
    assert final["outcome"] == "agents_a1_semantic_bridge_feasibility_blocked"
    assert final["gates"]["serving_restored_and_verified"] is False


def test_finalize_never_upgrades_blocked_technical():
    final = finalize_outcome(
        technical("agents_a1_semantic_bridge_feasibility_blocked"),
        True, {"reply_expected": True})
    assert final["outcome"] == "agents_a1_semantic_bridge_feasibility_blocked"


def test_technical_phase_cannot_emit_passed():
    # The smoke phase's only success outcome string is pending-restore.
    import m37jc_smoke as S
    src = Path(S.__file__).read_text()
    smoke_body = src.split("def phase_smoke")[1].split("def phase_finalize")[0]
    assert '"passed"' not in smoke_body


def test_divergence_stats_counts():
    a = [[1, 2, 3], [4, 5, 6]]
    b = [[1, 2, 3], [4, 9, 6]]
    s = divergence_stats(a, b)
    assert s == {"prompts_differing": 1, "first_divergence_min": 1}
