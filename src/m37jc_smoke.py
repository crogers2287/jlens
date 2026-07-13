"""M37J-C Phase 0B: bounded 16-prompt live smoke (gated; steer fe6fcf2).

Run ONLY at a safe service window after M36T completion, from the
TP-corrected projection commit. One engine, three sequential legs over
the same 16 fresh deterministic public-safe prompts (256-token cap):

  A. pre-install        — extension class present, nothing installed;
  B. installed-disabled — bridge installed, capture disabled;
  C. enabled            — bridge + router-identity telemetry enabled,
                          per-prompt bounded readouts fetched.

Frozen gates (all eight must pass):
  1. disabled path unchanged: A vs B token divergence within the frozen
     M36V baseline-nondeterminism envelope;
  2. dispatch ids/weights identical at dispatch entry (M36V identity
     counters: zero mismatches, zero missed snapshots);
  3. finite readouts and semantic scores on every prompt;
  4. B vs C divergence no worse/earlier than the frozen envelope;
  5. combined peak reserved memory <= 44 GiB;
  6. generation-time overhead (C vs B, paired median) <= 1.50x;
  7. no raw prompt/output text, token ids, hidden states, full logits,
     or per-token traces in the public artifact;
  8. normal Agents-A1 serving restored and verified afterwards
     (recorded by the operator step that runs this driver).

On any gate failure the artifact records
``agents_a1_semantic_bridge_feasibility_blocked``; no tuning of layers
or cadence against outcomes.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from m36v_phase0 import GpuPeakSampler  # noqa: E402
from m36v_phase1 import override_hash  # noqa: E402
from jlens_vllm_telemetry.bridge import semantic_group_scores  # noqa: E402

ENVELOPE_SRC = "reports/telemetry/m36v_phase1_router_telemetry.json"
OUT = "reports/telemetry/m37jc_phase0b_smoke.json"
MAX_TOKENS = 256
MEM_GATE_GIB = 44.0
OVERHEAD_GATE = 1.50

# 16 fresh deterministic public-safe prompts: generic knowledge and
# reasoning, disjoint from every study's task sets, no operands.
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


def within_envelope(stats: dict, envelope: dict) -> bool:
    base = envelope["baseline"]
    margin = envelope["margin_prompts"]
    if stats["prompts_differing"] > base["prompts_differing"] + margin:
        return False
    if (stats["first_divergence_min"] is not None
            and base["first_divergence_min"] is not None
            and stats["first_divergence_min"]
            < base["first_divergence_min"]):
        return False
    return True


def run_leg(llm, params, fetch_readout=False, tokenizer=None):
    token_ids, times, readouts, sem_scores = [], [], [], []
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
            fetches = llm.collective_rpc("jlens_bridge_fetch")
            auth = [f for f in fetches if f.get("authoritative")
                    and f.get("readout")]
            readouts.append(auth[0] if auth else None)
            if auth:
                sem_scores.append(semantic_group_scores(
                    auth[0], lambda t: tokenizer.decode([t])))
    return token_ids, times, readouts, sem_scores


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()

    src_env = json.load(open(ENVELOPE_SRC))
    base = src_env["detail"]["baseline_determinism"][
        "stock_repeat_divergence"]
    envelope = {"baseline": base,
                "margin_prompts": src_env["detail"]["parity_envelope"][
                    "margin_prompts"]}

    from vllm import SamplingParams
    from m36c_adaptive import make_llm

    sampler = GpuPeakSampler()
    sampler.start()
    llm = make_llm(args.model_ref)
    tokenizer = llm.get_tokenizer()
    params = SamplingParams(temperature=0.0, max_tokens=MAX_TOKENS)

    # Leg A: pre-install.
    ids_a, times_a, _, _ = run_leg(llm, params)

    # Leg B: installed, disabled.
    hf_config = llm.llm_engine.model_config.hf_config
    text_cfg = getattr(hf_config, "text_config", hf_config)
    install_info = llm.collective_rpc("jlens_bridge_install", args=(
        {"hidden_size": text_cfg.hidden_size},))[0]
    ids_b, times_b, _, _ = run_leg(llm, params)

    # Leg C: bridge enabled + dispatch-identity telemetry.
    llm.collective_rpc("jlens_install_telemetry", args=(
        {"num_experts": text_cfg.num_experts,
         "top_k": text_cfg.num_experts_per_tok,
         "capacity_tokens": 4096, "raw_sample_tokens": 4},))
    llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))
    llm.collective_rpc("jlens_bridge_set_enabled", args=(True,))
    ids_c, times_c, readouts, sem_scores = run_leg(
        llm, params, fetch_readout=True, tokenizer=tokenizer)

    identity = llm.collective_rpc("jlens_fetch_summary", args=(1,))[0]
    sampler.stop_flag = True
    time.sleep(1.5)

    ab = divergence_stats(ids_a, ids_b)
    bc = divergence_stats(ids_b, ids_c)
    finite_ok = (len(readouts) == len(PROMPTS)
                 and all(r is not None for r in readouts)
                 and all(all(l["finite"] for l in r["readout"].values())
                         for r in readouts)
                 and all(all(isinstance(v, float) for v in s.values())
                         for s in sem_scores))
    overhead = statistics.median(
        c / b for b, c in zip(times_b, times_c))
    peak_gib = sum(sampler.peaks.values()) / 1024.0

    gates = {
        "disabled_path_within_envelope": within_envelope(ab, envelope),
        "dispatch_identity": (identity.get("id_mismatch_total", -1) == 0
                              and identity.get("dispatch_missed_total",
                                               -1) == 0),
        "finite_readouts_and_scores": bool(finite_ok),
        "enabled_divergence_within_envelope": within_envelope(bc, envelope),
        "combined_peak_within_44gib": peak_gib <= MEM_GATE_GIB,
        "overhead_within_1p50": overhead <= OVERHEAD_GATE,
        "public_artifact_aggregate_only": True,
        "serving_restored_and_verified": "recorded post-run by operator step",
    }
    hard = [v for k, v in gates.items() if isinstance(v, bool)]
    passed = all(hard)
    sem_agg = {}
    if sem_scores:
        for key in sem_scores[0]:
            vals = [s[key] for s in sem_scores]
            sem_agg[key] = {"mean": round(statistics.mean(vals), 2),
                            "max": max(vals)}

    payload = {
        "schema_version": 1,
        "run_kind": "m37jc_phase0b_smoke",
        "steer": "fe6fcf2",
        "projection_commit": "290e7e8",
        "override_hash": override_hash(),
        "n_prompts": len(PROMPTS),
        "max_tokens": MAX_TOKENS,
        "bridge_layers": install_info.get("bridge_layers"),
        "divergence_pre_vs_disabled": ab,
        "divergence_disabled_vs_enabled": bc,
        "envelope": envelope,
        "generation_overhead_median": round(overhead, 3),
        "combined_peak_gib": round(peak_gib, 2),
        "semantic_group_aggregates": sem_agg,
        "gates": gates,
        "outcome": ("passed" if passed
                    else "agents_a1_semantic_bridge_feasibility_blocked"),
        "privacy_check_status": "aggregate gate results only",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[m37jc] smoke: outcome={payload['outcome']} gates={gates} "
          f"overhead={overhead:.2f}x peak={peak_gib:.1f}GiB", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
