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
    from m37jc_smoke import expected_steps
    import math as _math
    steps = expected_steps(steps_total)
    n_periodic = len(list(range(31, steps_total, 32)))
    calls = sum(_math.ceil(len(expected_steps(steps_total)) / 8)
                for _ in FROZEN_LAYERS)
    readout = {str(l): {"steps": list(steps),
                        "token_ids": [[1] * 10 for _ in steps],
                        "finite": True}
               for l in FROZEN_LAYERS}
    return {"rank": rank, "authoritative": authoritative,
            "layers": list(FROZEN_LAYERS), "cadence": 32, "top_k": 10,
            "decode_steps": [steps_total] * N_LAYERS,
            "captured_slots": [n_periodic] * N_LAYERS,
            "dropped": [0] * N_LAYERS,
            "projection_calls": calls,
            "readout": readout if authoritative else {}}


def sem_fn(fetch):
    return {"group_completion": 1.0, "group_continuation": 0.0,
            "group_verification": 0.0, "group_error_conflict": 0.0,
            "group_uncertainty": 0.0}


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
            "cadence": 32, "top_k": 10, "n_slots": 80,
            "hidden_size": 4096, "n_decoder_layers": 40}


def good_telem(rank):
    return {"rank": rank, "num_moe_layers": 40,
            "layer_ids": list(range(40)), "num_experts": 256,
            "router_top_k": 8, "capacity_tokens": 4096,
            "raw_sample_tokens": 4}


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
        if method == "jlens_status":
            return [{"rank": r, "bridge_installed": False,
                     "bridge_enabled": False,
                     "telemetry_installed": False,
                     "telemetry_enabled": False}
                    for r in range(self.ranks)]
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
    assert llm.calls == [s[0] for s in CLEANUP_STEPS] + ["jlens_status"]
    llm2 = FakeLLM(raise_step="jlens_set_telemetry_enabled")
    r = run_cleanup(llm2, 2)
    assert not r["ok"]
    assert llm2.calls == [s[0] for s in CLEANUP_STEPS] + ["jlens_status"]


# -- 4. finalizer --------------------------------------------------------------

from m37jc_smoke import PROVENANCE_FILES


def technical_artifact(**over):
    art = {"schema_version": 1, "run_kind": "m37jc_phase0b_smoke",
           "provenance": {"source_commit": "a" * 40,
                          "file_sha256": {f: "b" * 64
                                          for f in PROVENANCE_FILES}},
           "override_hash": "9f4d46aa",
           "envelope": {"sha256": "e" * 64},
           "gates": {k: True for k in TECHNICAL_GATE_KEYS},
           "outcome": "technical_gates_passed_pending_restore",
           "privacy_check_status": "aggregate gate results only"}
    art.update(over)
    return art


def test_finalizer_verifies_and_records_sha():
    art = technical_artifact()
    sha = verify_technical_artifact(art, check_sources=False)
    assert len(sha) == 64
    final = finalize_outcome(art, True, {"reply_exact": True}, sha)
    assert final["outcome"] == "passed"
    assert final["technical_artifact_canonical_json_sha256"] == sha
    assert final["gates"]["serving_restored_and_verified"] is True


def test_finalizer_rejects_gate_inconsistencies():
    bad_false = technical_artifact()
    bad_false["gates"]["overhead_within_1p50"] = False
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(bad_false, check_sources=False)
    missing = technical_artifact()
    del missing["gates"]["cleanup_verified_all_ranks"]
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(missing, check_sources=False)
    extra = technical_artifact()
    extra["gates"]["bonus_gate"] = True
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(extra, check_sources=False)
    nonbool = technical_artifact()
    nonbool["gates"]["overhead_within_1p50"] = "true"
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(nonbool, check_sources=False)
    pre_g8 = technical_artifact()
    pre_g8["gates"]["serving_restored_and_verified"] = True
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(pre_g8, check_sources=False)
    wrong_outcome = technical_artifact(outcome="passed")
    with pytest.raises(SmokeBlocked):
        verify_technical_artifact(wrong_outcome, check_sources=False)


def test_finalizer_reply_must_be_exact():
    assert reply_is_exact("  SERVING-OK\n")
    assert not reply_is_exact("NOT SERVING-OK")
    assert not reply_is_exact("SERVING-OK indeed")


def test_finalize_restore_failure_blocks():
    art = technical_artifact()
    sha = verify_technical_artifact(art, check_sources=False)
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


# -- steer 04920b0 additions ---------------------------------------------------

def test_off_cadence_monotone_steps_fail():
    f = [good_fetch(0), good_fetch(1, authoritative=False)]
    for l in FROZEN_LAYERS:
        f[0]["readout"][str(l)]["steps"] = [5, 10, 69]
        f[0]["readout"][str(l)]["token_ids"] = [[1] * 10] * 3
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]


def test_wrong_slot_dropped_or_call_counts_fail():
    base = lambda: [good_fetch(0), good_fetch(1, authoritative=False)]
    f = base(); f[0]["captured_slots"] = [9] * N_LAYERS
    f[1]["captured_slots"] = [9] * N_LAYERS
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]
    f = base(); f[0]["dropped"] = [1] * N_LAYERS
    f[1]["dropped"] = [1] * N_LAYERS
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]
    f = base(); f[0]["projection_calls"] = 99
    f[1]["projection_calls"] = 99
    assert not check_authoritative(f, VOCAB, sem_fn)["ok"]


def test_infinite_and_malformed_semantic_values_fail():
    f = lambda: [good_fetch(0), good_fetch(1, authoritative=False)]
    for bad in (float("inf"), float("-inf"), "1.0"):
        def make(b):
            def fn(fetch):
                d = sem_fn(fetch)
                d["group_completion"] = b
                return d
            return fn
        assert not check_authoritative(f(), VOCAB, make(bad))["ok"]
    missing = lambda fetch: {k: 0.0 for k in list(S.SEMANTIC_KEYS)[:4]}
    assert not check_authoritative(f(), VOCAB, missing)["ok"]
    extra = lambda fetch: dict(sem_fn(fetch), group_bonus=1.0)
    assert not check_authoritative(f(), VOCAB, extra)["ok"]


def test_semantic_cross_rank_disagreement_fails():
    a, b = good_fetch(0), good_fetch(1)
    vals = iter([1.0, 2.0])
    def fn(fetch):
        d = sem_fn(fetch)
        d["group_completion"] = next(vals)
        return d
    assert not check_authoritative([a, b], VOCAB, fn)["ok"]


def test_provenance_requires_clean_tree(monkeypatch):
    import subprocess as sp
    def fake_run(cmd, **kw):
        class R:
            stdout = " M src/foo.py\n" if "status" in cmd else "x" * 40
        return R()
    monkeypatch.setattr(S.subprocess, "run", fake_run)
    with pytest.raises(SmokeBlocked, match="uncommitted"):
        S.source_provenance()


def test_finalizer_rejects_incomplete_or_stale_provenance():
    art = technical_artifact()
    art["provenance"]["source_commit"] = "abc123"   # abbreviated
    with pytest.raises(SmokeBlocked, match="provenance"):
        verify_technical_artifact(art, check_sources=False)
    art2 = technical_artifact()
    del art2["provenance"]["file_sha256"][S.PROVENANCE_FILES[0]]
    with pytest.raises(SmokeBlocked, match="provenance"):
        verify_technical_artifact(art2, check_sources=False)
    art3 = technical_artifact()
    def boom(recorded):
        raise SmokeBlocked("source provenance mismatch at finalization")
    orig = S.verify_provenance
    S.verify_provenance = boom
    try:
        with pytest.raises(SmokeBlocked, match="mismatch"):
            verify_technical_artifact(art3, check_sources=True)
    finally:
        S.verify_provenance = orig


def test_install_metadata_omissions_fail():
    inc = [good_install(0), good_install(1)]
    del inc[1]["cadence"]
    assert not check_install(inc, [good_telem(0), good_telem(1)])["ok"]
    tel = [good_telem(0), dict(good_telem(1), num_experts=128)]
    assert not check_install([good_install(0), good_install(1)], tel)["ok"]


def test_restoration_health_failure_blocks():
    art = technical_artifact()
    sha = verify_technical_artifact(art, check_sources=False)
    record = {"reply_exact": True, "model_listed_exact": True,
              "health_endpoint_ok": False}
    restore_ok = (record["reply_exact"] and record["model_listed_exact"]
                  and record["health_endpoint_ok"])
    final = finalize_outcome(art, restore_ok, record, sha)
    assert final["outcome"] == "agents_a1_semantic_bridge_feasibility_blocked"


def test_audit_rejects_forbidden_keys_and_paths():
    with pytest.raises(SmokeBlocked, match="forbidden"):
        S.audit_aggregate_only({"gates": {}, "token_ids": [[1]]})
    with pytest.raises(SmokeBlocked, match="private path"):
        S.audit_aggregate_only({"note": "see /home/user/x"})
    S.audit_aggregate_only({"gates": {"a": True}, "n": 1})


def test_worker_installs_are_transactional_and_idempotent(monkeypatch):
    import torch
    from jlens_vllm_telemetry.worker_ext import JlensWorkerExtension
    from jlens_vllm_telemetry import bridge as B

    class FakeLayer(torch.nn.Module):
        def forward(self, x):
            return x

    layers = torch.nn.ModuleList([FakeLayer() for _ in range(40)])

    class W(JlensWorkerExtension):
        rank = 0
        class model_runner:
            device = "cpu"
        def _jlens_find_decoder_stack(self):
            return layers, torch.nn.LayerNorm(8), None

    w = W()
    # allocation raises -> every attached hook removed, state absent
    monkeypatch.setattr(B.SemanticBridgeCollector, "allocate",
                        lambda self, dev: (_ for _ in ()).throw(
                            RuntimeError("alloc fail")))
    with pytest.raises(RuntimeError):
        w.jlens_bridge_install({"hidden_size": 8})
    assert getattr(w, "_jlens_bridge", None) is None
    assert all(not m._forward_hooks for m in layers)
    # idempotent uninstalls: absent components report success
    assert w.jlens_bridge_uninstall() is True
    assert w.jlens_uninstall_telemetry() is True
    # status RPC is bounded booleans
    st = w.jlens_status()
    assert set(st) == {"rank", "telemetry_installed", "telemetry_enabled",
                       "bridge_installed", "bridge_enabled"}
    assert not st["bridge_installed"]
