"""Steer-65c76ec conformance tests for the M37J-C smoke harness.

Synthetic fixtures only; no engine, no live prompts.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

import m37jc_smoke as S
from m37jc_smoke import (CLEANUP_STEPS, FROZEN_LAYERS, SmokeBlocked,
                         TECHNICAL_GATE_KEYS, check_authoritative,
                         check_identity_per_prompt, check_install,
                         divergence_stats, envelope_from_artifact,
                         finalize_outcome, reply_is_exact, run_cleanup,
                         verify_technical_artifact, within_envelope,
                         write_blocked)

ARTIFACT = {"detail": {
    "parity_envelope": {"margin_prompts": 2, "first_divergence_floor": 8},
    "baseline_determinism": {"stock_repeat_divergence": {
        "prompts_differing": 5, "first_divergence_min": 13,
        "first_divergence_mean": 122.8}}}}

VOCAB = 64
N_LAYERS = len(FROZEN_LAYERS)


def clean_summary(rank):
    return {"rank": rank, "id_mismatch_total": 0,
            "dispatch_missed_total": 0}


def good_fetch(rank, authoritative=True, steps_total=70):
    steps = [31, 63, steps_total - 1] if steps_total - 1 != 63 else [31, 63]
    readout = {str(l): {"steps": list(steps),
                        "token_ids": [[1] * 10 for _ in steps],
                        "finite": True}
               for l in FROZEN_LAYERS}
    return {"rank": rank, "authoritative": authoritative,
            "layers": list(FROZEN_LAYERS), "cadence": 32, "top_k": 10,
            "decode_steps": [steps_total] * N_LAYERS,
            "captured_slots": [2] * N_LAYERS,
            "dropped": [0] * N_LAYERS,
            "projection_calls": 12,
            "readout": readout if authoritative else {}}


def sem_fn(fetch):
    return {"group_completion": 1.0, "group_uncertainty": 0.0}


# -- envelope ------------------------------------------------------------

def test_envelope_uses_frozen_floor():
    env = envelope_from_artifact(ARTIFACT)
    assert env["first_divergence_floor"] == 8
    assert within_envelope({"prompts_differing": 5,
                            "first_divergence_min": 9}, env)
    assert not within_envelope({"prompts_differing": 5,
                                "first_divergence_min": 7}, env)
    assert not within_envelope({"prompts_differing": 8,
                                "first_divergence_min": 20}, env)


# -- 1. per-prompt identity ------------------------------------------------

def test_identity_mismatch_on_prompt1_then_clean_prompt2_fails():
    p1 = [clean_summary(0),
          {"rank": 1, "id_mismatch_total": 2, "dispatch_missed_total": 0}]
    p2 = [clean_summary(0), clean_summary(1)]
    r = check_identity_per_prompt([p1, p2], 2)
    assert not r["ok"] and r["prompt_failures"] == 1
    assert r["id_mismatch_max"] == 2


def test_identity_exact_rank_set_enforced():
    for ranks in ({0, 2}, {None, 0}):
        bad = [[clean_summary(r) for r in ranks]]
        assert not check_identity_per_prompt(bad, 1)["ok"]
    dup = [[clean_summary(0), clean_summary(0)]]
    assert not check_identity_per_prompt(dup, 1)["ok"]
    missing = [[clean_summary(0)]]
    assert not check_identity_per_prompt(missing, 1)["ok"]


def test_identity_missing_prompt_coverage_fails():
    good = [[clean_summary(0), clean_summary(1)]]
    assert not check_identity_per_prompt(good, 2)["ok"]  # expected 2 prompts
    assert check_identity_per_prompt(good * 2, 2)["ok"]


# -- 2. readout conformance --------------------------------------------------

def test_empty_authoritative_readout_fails():
    f = good_fetch(0)
    f["readout"] = {}
    r = check_authoritative([f, good_fetch(1, authoritative=False)],
                            VOCAB, sem_fn)
    assert not r["ok"] and "frozen layers" in r["reason"]


def test_missing_layer_zero_steps_bad_ids_fail():
    base = lambda: [good_fetch(0), good_fetch(1, authoritative=False)]
    f = base(); del f[0]["readout"]["4"]
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]
    f = base(); f[0]["decode_steps"] = [0] * N_LAYERS
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]
    f = base(); f[0]["readout"]["4"]["token_ids"][0] = [1] * 9   # width 9
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]
    f = base(); f[0]["readout"]["4"]["steps"] = []
    f[0]["readout"]["4"]["token_ids"] = []
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]


def test_nonmonotone_or_duplicate_final_steps_fail():
    f = [good_fetch(0), good_fetch(1, authoritative=False)]
    f[0]["readout"]["12"]["steps"] = [63, 31, 69]
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]
    g = [good_fetch(0, steps_total=64), good_fetch(1, False,
                                                   steps_total=64)]
    # steps_total=64 -> final step 63 IS the cadence checkpoint; a
    # duplicated final entry must fail.
    g[0]["readout"]["4"]["steps"] = [31, 63, 63]
    g[0]["readout"]["4"]["token_ids"] = [[1] * 10] * 3
    assert not check_authoritative(g, VOCAB, sem_fn)["ok"]


def test_final_step_must_be_recorded_once():
    f = [good_fetch(0), good_fetch(1, authoritative=False)]
    f[0]["readout"]["20"]["steps"] = [31, 63]        # missing final 69
    f[0]["readout"]["20"]["token_ids"] = [[1] * 10] * 2
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]


def test_shard_local_id_fails():
    f = [good_fetch(0), good_fetch(1, authoritative=False)]
    f[0]["readout"]["4"]["token_ids"][0] = [VOCAB + 5] + [1] * 9
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]


def test_nonfinite_semantic_aggregate_fails():
    f = [good_fetch(0), good_fetch(1, authoritative=False)]
    bad_sem = lambda fetch: {"group_completion": float("nan")}
    assert not check_authoritative(f, VOCAB, bad_sem)["ok"]


def test_cross_rank_disagreement_fails():
    a, b = good_fetch(0), good_fetch(1)
    b["readout"]["4"]["token_ids"] = [[2] * 10] * len(
        b["readout"]["4"]["steps"])
    assert not check_authoritative([a, b], VOCAB, sem_fn)["ok"]
    a2, b2 = good_fetch(0), good_fetch(1, authoritative=False)
    b2["captured_slots"] = [9] * N_LAYERS
    assert not check_authoritative([a2, b2], VOCAB, sem_fn)["ok"]


def test_two_agreeing_authoritative_ranks_pass():
    r = check_authoritative([good_fetch(0), good_fetch(1)], VOCAB, sem_fn)
    assert r["ok"] and r["n_authoritative"] == 2


def test_nonauthoritative_leak_fails():
    a = good_fetch(0)
    leak = good_fetch(1, authoritative=False)
    leak["readout"] = {"4": {"steps": [31], "token_ids": [[1] * 10],
                             "finite": True}}
    assert not check_authoritative([a, leak], VOCAB, sem_fn)["ok"]


# -- 3. install conformance ---------------------------------------------------

def good_install(rank):
    return {"rank": rank, "bridge_layers": list(FROZEN_LAYERS),
            "n_decoder_layers": 40}


def good_telem(rank):
    return {"rank": rank, "num_moe_layers": 40, "layer_ids": list(range(40))}


def test_install_conformance_pass_and_failures():
    assert check_install([good_install(0), good_install(1)],
                         [good_telem(0), good_telem(1)])["ok"]
    err = [good_install(0), {"rank": 1, "error": "already installed"}]
    assert not check_install(err, [good_telem(0), good_telem(1)])["ok"]
    diff = [good_install(0), dict(good_install(1), n_decoder_layers=39)]
    assert not check_install(diff, [good_telem(0), good_telem(1)])["ok"]
    one_rank = [good_install(0)]
    assert not check_install(one_rank, [good_telem(0), good_telem(1)])["ok"]


# -- cleanup ------------------------------------------------------------------

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
            return [expect, not expect]
        return [expect] * self.ranks


def test_cleanup_order_success_and_exception_continue():
    llm = FakeLLM()
    assert run_cleanup(llm, 2)["ok"]
    assert llm.calls == [s[0] for s in CLEANUP_STEPS]
    llm2 = FakeLLM(raise_step="jlens_set_telemetry_enabled")
    r = run_cleanup(llm2, 2)
    assert not r["ok"] and llm2.calls == [s[0] for s in CLEANUP_STEPS]


# -- 4. finalizer --------------------------------------------------------------

def technical_artifact(**over):
    art = {"schema_version": 1, "run_kind": "m37jc_phase0b_smoke",
           "projection_commit": "290e7e8", "smoke_driver_commit": "abc123",
           "override_hash": "9f4d46aa",
           "envelope": {"sha256": "e" * 64},
           "gates": {k: True for k in TECHNICAL_GATE_KEYS},
           "outcome": "technical_gates_passed_pending_restore",
           "privacy_check_status": "aggregate gate results only"}
    art.update(over)
    return art


def test_finalizer_verifies_and_records_sha():
    art = technical_artifact()
    sha = verify_technical_artifact(art)
    assert len(sha) == 64
    final = finalize_outcome(art, True, {"reply_exact": True}, sha)
    assert final["outcome"] == "passed"
    assert final["technical_artifact_sha256"] == sha
    assert final["gates"]["serving_restored_and_verified"] is True


def test_finalizer_rejects_gate_inconsistencies():
    bad_false = technical_artifact()
    bad_false["gates"]["overhead_within_1p50"] = False
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(bad_false)
    missing = technical_artifact()
    del missing["gates"]["cleanup_verified_all_ranks"]
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(missing)
    extra = technical_artifact()
    extra["gates"]["bonus_gate"] = True
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(extra)
    nonbool = technical_artifact()
    nonbool["gates"]["overhead_within_1p50"] = "true"
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(nonbool)
    pre_g8 = technical_artifact()
    pre_g8["gates"]["serving_restored_and_verified"] = True
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(pre_g8)
    wrong_outcome = technical_artifact(outcome="passed")
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(wrong_outcome)


def test_finalizer_reply_must_be_exact():
    assert reply_is_exact("  SERVING-OK\n")
    assert not reply_is_exact("NOT SERVING-OK")
    assert not reply_is_exact("SERVING-OK indeed")


def test_finalize_restore_failure_blocks():
    art = technical_artifact()
    sha = verify_technical_artifact(art)
    final = finalize_outcome(art, False, {"error": "URLError"}, sha)
    assert final["outcome"] == "agents_a1_semantic_bridge_feasibility_blocked"


# -- 5. exception-path blocker artifact -----------------------------------------

def test_blocked_artifact_is_aggregate_only(tmp_path):
    out = tmp_path / "smoke.json"
    write_blocked(str(out), "engine_construction",
                  RuntimeError("secret /home/user/path token 12345"),
                  {"ok": True, "steps": []})
    data = json.loads(out.read_text())
    assert data["outcome"] == "agents_a1_semantic_bridge_feasibility_blocked"
    assert data["exception_class"] == "RuntimeError"
    assert data["lifecycle_stage"] == "engine_construction"
    raw = out.read_text()
    assert "secret" not in raw and "/home/" not in raw
    assert "token 12345" not in raw


def test_technical_phase_cannot_emit_passed():
    src = Path(S.__file__).read_text()
    smoke_body = src.split("def phase_smoke")[1].split(
        "def phase_finalize")[0]
    assert '"passed"' not in smoke_body


def test_divergence_stats_counts():
    s = divergence_stats([[1, 2, 3], [4, 5, 6]], [[1, 2, 3], [4, 9, 6]])
    assert s == {"prompts_differing": 1, "first_divergence_min": 1}
