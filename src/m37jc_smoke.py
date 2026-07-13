"""M37J-C Phase 0B: bounded 16-prompt live smoke (steer 821e430 harness).

Two-phase execution; run ONLY at a safe service window after M36T
completion, from the TP-corrected projection commit:

  --phase smoke     one engine, three sequential legs (pre-install /
                    installed-disabled / enabled) over the 16 frozen
                    public-safe prompts. Gates 1-7 are hard booleans;
                    on success the artifact outcome is
                    ``technical_gates_passed_pending_restore`` — never
                    ``passed``. Cleanup (bridge disable -> telemetry
                    disable -> bridge uninstall -> telemetry uninstall
                    -> engine release) runs in a ``finally`` block and
                    is verified per rank; any cleanup failure blocks.
  --phase finalize  after the external serving restore: issues the
                    frozen public-safe verification request against the
                    production endpoint, checks the model list and the
                    exact expected reply, and only then writes gate 8
                    as boolean ``true`` and ``outcome: passed``. Any
                    restore/verification failure writes
                    ``agents_a1_semantic_bridge_feasibility_blocked``.

The frozen M36V parity envelope (margin_prompts 2,
first_divergence_floor 8) is loaded, field-checked, and hashed from the
pinned artifact; dispatch identity is required to be zero on EVERY
tensor-parallel rank; authoritative global readouts must agree across
any ranks that hold full-vocabulary logits, non-authoritative ranks
must emit nothing, and projection-call/captured-slot counts must match
across ranks per prompt. Aggregate-only artifacts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

ENVELOPE_SRC = "reports/telemetry/m36v_phase1_router_telemetry.json"
OUT = "reports/telemetry/m37jc_phase0b_smoke.json"
MAX_TOKENS = 256
MEM_GATE_GIB = 44.0
OVERHEAD_GATE = 1.50
EXPECTED_RANKS = 2
SERVING_URL = "http://localhost:9069/v1"
SERVING_PROBE = "Reply with exactly: SERVING-OK"

PROMPTS = [
    "Explain in two sentences why the sky appears blue.",
    "Name three renewable energy sources and one advantage of each.",
    "Summarize the water cycle in three steps.",
    "What is the difference between speed and velocity?",
    "Describe how a bill becomes a law in one short paragraph.",
    "Explain the difference between weather and climate.",
    "List four primary colors of light and what mixing them yields.",
    "Why do ships float even though steel is denser than water?",
    "Explain photosynthesis in plain language, two sentences.",
    "What causes the phases of the moon?",
    "Describe the role of the CPU in a computer briefly.",
    "Why is the boiling point of water lower at high altitude?",
    "Explain the difference between a virus and a bacterium.",
    "What is compound interest? Give a one-line example.",
    "Describe how vaccines train the immune system, briefly.",
    "Why do we see lightning before hearing thunder?",
]


class SmokeBlocked(Exception):
    pass


# -- pure gate logic (unit-tested) ---------------------------------------

def envelope_from_artifact(artifact: dict) -> dict:
    """Load, field-check, and hash the complete frozen parity envelope."""
    detail = artifact["detail"]
    env = detail["parity_envelope"]
    if set(env) != {"margin_prompts", "first_divergence_floor"}:
        raise SmokeBlocked(f"unexpected envelope fields: {sorted(env)}")
    baseline = detail["baseline_determinism"]["stock_repeat_divergence"]
    blob = json.dumps({"parity_envelope": env, "baseline": baseline},
                      sort_keys=True).encode()
    return {"margin_prompts": int(env["margin_prompts"]),
            "first_divergence_floor": int(env["first_divergence_floor"]),
            "baseline_prompts_differing": int(baseline["prompts_differing"]),
            "sha256": hashlib.sha256(blob).hexdigest()}


def first_divergence(a: list[int], b: list[int]) -> int | None:
    for i, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return i
    return None if len(a) == len(b) else min(len(a), len(b))


def divergence_stats(legs_a, legs_b) -> dict:
    firsts = [first_divergence(a, b) for a, b in zip(legs_a, legs_b)]
    diffs = [f for f in firsts if f is not None]
    return {"prompts_differing": len(diffs),
            "first_divergence_min": min(diffs) if diffs else None}


def within_envelope(stats: dict, env: dict) -> bool:
    if stats["prompts_differing"] > (env["baseline_prompts_differing"]
                                     + env["margin_prompts"]):
        return False
    fd = stats["first_divergence_min"]
    return fd is None or fd >= env["first_divergence_floor"]


def check_identity(summaries: list[dict], expected_ranks: int) -> dict:
    ranks = [s.get("rank") for s in summaries]
    mism = [int(s.get("id_mismatch_total", -1)) for s in summaries]
    miss = [int(s.get("dispatch_missed_total", -1)) for s in summaries]
    ok = (len(summaries) == expected_ranks
          and len(set(ranks)) == expected_ranks
          and all(m == 0 for m in mism) and all(m == 0 for m in miss))
    return {"ok": bool(ok), "rank_count": len(summaries),
            "unique_ranks": len(set(ranks)),
            "id_mismatch_max": max(mism, default=-1),
            "id_mismatch_sum": sum(mism),
            "dispatch_missed_max": max(miss, default=-1),
            "dispatch_missed_sum": sum(miss)}


def check_authoritative(fetches: list[dict]) -> dict:
    """Per-prompt cross-rank readout conformance (steer 821e430 item 5)."""
    auth = [f for f in fetches if f.get("authoritative")]
    non = [f for f in fetches if not f.get("authoritative")]
    ok = len(auth) >= 1
    leak_free = all(not f.get("readout") for f in non)
    agree = all(a.get("readout") == auth[0].get("readout")
                for a in auth[1:]) if len(auth) > 1 else True
    calls = {f.get("projection_calls") for f in fetches}
    slots = {tuple(f.get("captured_slots", ())) for f in fetches}
    uniform = len(calls) == 1 and len(slots) == 1
    finite = all(l.get("finite") for a in auth
                 for l in a.get("readout", {}).values())
    return {"ok": bool(ok and leak_free and agree and uniform and finite),
            "n_authoritative": len(auth),
            "non_authoritative_leak_free": bool(leak_free),
            "authoritative_agreement": bool(agree),
            "uniform_calls_and_slots": bool(uniform),
            "finite": bool(finite)}


CLEANUP_STEPS = (
    ("jlens_bridge_set_enabled", (False,), False),
    ("jlens_set_telemetry_enabled", (False,), False),
    ("jlens_bridge_uninstall", (), True),
    ("jlens_uninstall_telemetry", (), True),
)


def run_cleanup(llm, expected_ranks: int) -> dict:
    """Ordered, per-rank-verified cleanup. Returns aggregate report."""
    report, ok = [], True
    for method, rpc_args, expect in CLEANUP_STEPS:
        try:
            results = llm.collective_rpc(method, args=rpc_args)
            step_ok = (len(results) == expected_ranks
                       and all(r == expect for r in results))
        except Exception as exc:            # RPC failure blocks
            results, step_ok = [f"exception: {type(exc).__name__}"], False
        report.append({"step": method, "ok": bool(step_ok)})
        ok &= step_ok
    return {"ok": bool(ok), "steps": report}


def finalize_outcome(technical: dict, restore_ok: bool,
                     restore_record: dict) -> dict:
    final = dict(technical)
    final["gates"] = dict(technical["gates"])
    final["gates"]["serving_restored_and_verified"] = bool(restore_ok)
    final["restoration_verification"] = restore_record
    if (technical.get("outcome") == "technical_gates_passed_pending_restore"
            and restore_ok):
        final["outcome"] = "passed"
    else:
        final["outcome"] = "agents_a1_semantic_bridge_feasibility_blocked"
    return final


# -- live phases ----------------------------------------------------------

def run_leg(llm, params, fetch_readout=False):
    token_ids, times, fetch_sets = [], [], []
    for prompt in PROMPTS:
        if fetch_readout:
            llm.collective_rpc("jlens_bridge_reset")
            llm.collective_rpc("jlens_reset_telemetry")
        t0 = time.time()
        out = llm.chat([[{"role": "user", "content": prompt}]], params,
                       use_tqdm=False)[0]
        times.append(time.time() - t0)
        token_ids.append(list(out.outputs[0].token_ids))
        if fetch_readout:
            fetch_sets.append(llm.collective_rpc("jlens_bridge_fetch"))
    return token_ids, times, fetch_sets


def phase_smoke(args) -> int:
    from m36v_phase0 import GpuPeakSampler
    from m36v_phase1 import override_hash
    from m36c_adaptive import make_llm
    from jlens_vllm_telemetry.bridge import semantic_group_scores
    from vllm import SamplingParams

    env = envelope_from_artifact(json.load(open(ENVELOPE_SRC)))
    sampler = GpuPeakSampler()
    sampler.start()
    llm = make_llm(args.model_ref)
    tokenizer = llm.get_tokenizer()
    params = SamplingParams(temperature=0.0, max_tokens=MAX_TOKENS)

    installed = False
    try:
        ids_a, times_a, _ = run_leg(llm, params)

        hf_config = llm.llm_engine.model_config.hf_config
        text_cfg = getattr(hf_config, "text_config", hf_config)
        install_info = llm.collective_rpc("jlens_bridge_install", args=(
            {"hidden_size": text_cfg.hidden_size},))[0]
        llm.collective_rpc("jlens_install_telemetry", args=(
            {"num_experts": text_cfg.num_experts,
             "top_k": text_cfg.num_experts_per_tok,
             "capacity_tokens": 4096, "raw_sample_tokens": 4},))
        installed = True
        ids_b, times_b, _ = run_leg(llm, params)

        llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))
        llm.collective_rpc("jlens_bridge_set_enabled", args=(True,))
        ids_c, times_c, fetch_sets = run_leg(llm, params,
                                             fetch_readout=True)
        identity = check_identity(
            llm.collective_rpc("jlens_fetch_summary", args=(1,)),
            EXPECTED_RANKS)
        conformance = [check_authoritative(fs) for fs in fetch_sets]
        sem_scores = []
        for fs in fetch_sets:
            auth = [f for f in fs if f.get("authoritative")]
            if auth:
                sem_scores.append(semantic_group_scores(
                    auth[0], lambda t: tokenizer.decode([t])))
    finally:
        cleanup = (run_cleanup(llm, EXPECTED_RANKS) if installed
                   else {"ok": True, "steps": []})
        del llm                                  # release engine
        sampler.stop_flag = True
        time.sleep(1.5)

    ab = divergence_stats(ids_a, ids_b)
    bc = divergence_stats(ids_b, ids_c)
    overhead = statistics.median(c / b for b, c in zip(times_b, times_c))
    peak_gib = sum(sampler.peaks.values()) / 1024.0
    gates = {
        "disabled_path_within_envelope": within_envelope(ab, env),
        "dispatch_identity_all_ranks": identity["ok"],
        "readout_conformance_all_prompts": (
            len(conformance) == len(PROMPTS)
            and all(c["ok"] for c in conformance)),
        "enabled_divergence_within_envelope": within_envelope(bc, env),
        "combined_peak_within_44gib": peak_gib <= MEM_GATE_GIB,
        "overhead_within_1p50": overhead <= OVERHEAD_GATE,
        "cleanup_verified_all_ranks": cleanup["ok"],
    }
    technical_pass = all(gates.values())
    sem_agg = {}
    if sem_scores:
        for key in sem_scores[0]:
            vals = [s[key] for s in sem_scores]
            sem_agg[key] = {"mean": round(statistics.mean(vals), 2),
                            "max": max(vals)}
    payload = {
        "schema_version": 1,
        "run_kind": "m37jc_phase0b_smoke",
        "steer": "821e430",
        "projection_commit": "290e7e8",
        "smoke_driver_commit": args.driver_commit,
        "override_hash": override_hash(),
        "envelope": env,
        "n_prompts": len(PROMPTS),
        "max_tokens": MAX_TOKENS,
        "bridge_layers": install_info.get("bridge_layers"),
        "divergence_pre_vs_disabled": ab,
        "divergence_disabled_vs_enabled": bc,
        "identity": identity,
        "readout_conformance_failures": sum(
            0 if c["ok"] else 1 for c in conformance),
        "generation_overhead_median": round(overhead, 3),
        "combined_peak_gib": round(peak_gib, 2),
        "semantic_group_aggregates": sem_agg,
        "cleanup": cleanup,
        "gates": gates,
        "outcome": ("technical_gates_passed_pending_restore"
                    if technical_pass
                    else "agents_a1_semantic_bridge_feasibility_blocked"),
        "privacy_check_status": "aggregate gate results only",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[m37jc] smoke phase: outcome={payload['outcome']} "
          f"gates={gates}", flush=True)
    return 0 if technical_pass else 1


def phase_finalize(args) -> int:
    import urllib.request

    technical = json.loads(Path(args.out).read_text())
    record: dict = {"probe": "frozen public-safe verification request"}
    restore_ok = False
    try:
        req = urllib.request.Request(
            f"{SERVING_URL}/chat/completions",
            data=json.dumps({
                "model": "agents-a1", "temperature": 0, "max_tokens": 10,
                "messages": [{"role": "user",
                              "content": SERVING_PROBE}]}).encode(),
            headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=240) as resp:
            reply = json.load(resp)["choices"][0]["message"]["content"]
        with urllib.request.urlopen(f"{SERVING_URL}/models",
                                    timeout=30) as resp:
            model_ids = [m["id"] for m in json.load(resp)["data"]]
        record["reply_expected"] = "SERVING-OK" in reply
        record["model_listed"] = "agents-a1" in model_ids
        restore_ok = record["reply_expected"] and record["model_listed"]
    except Exception as exc:
        record["error"] = type(exc).__name__
    final = finalize_outcome(technical, restore_ok, record)
    Path(args.out).write_text(json.dumps(final, indent=1) + "\n")
    print(f"[m37jc] finalize: outcome={final['outcome']} "
          f"restore={record}", flush=True)
    return 0 if final["outcome"] == "passed" else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase", choices=("smoke", "finalize"),
                    default="smoke")
    ap.add_argument("--model-ref")
    ap.add_argument("--driver-commit", default="uncommitted")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    if args.phase == "smoke":
        if not args.model_ref:
            raise SystemExit("--model-ref required for smoke phase")
        return phase_smoke(args)
    return phase_finalize(args)


if __name__ == "__main__":
    raise SystemExit(main())
