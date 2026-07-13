"""M37J-C Phase 0B: bounded 16-prompt live smoke (steer 65c76ec harness).

Two-phase execution; run ONLY at a safe service window after M36T
completion, from the TP-corrected projection commit.

``--phase smoke``: one engine, three sequential legs under an explicit
lifecycle state machine. Per enabled prompt, dispatch-identity
summaries are fetched on every rank BEFORE the next reset (a mismatch
on prompt 1 cannot be erased by prompt 2's reset). Authoritative
readouts are structurally validated against the frozen configuration —
an empty readout is a feasibility FAILURE, never a vacuous pass.
Install results are validated on every rank against the exact rank set.
Success emits at best ``technical_gates_passed_pending_restore``; every
exception path writes an aggregate-only blocked artifact (exception
class + lifecycle stage + cleanup aggregates only) after ordered,
per-rank-verified cleanup and sampler shutdown.

``--phase finalize``: verifies the technical artifact is internally
consistent (exact schema/run_kind/commit/hash fields, complete exact
gate-key set, all booleans true, pending outcome, no pre-existing
gate 8), records its SHA-256, then issues the frozen verification
request. The reply must EQUAL ``SERVING-OK`` after whitespace
normalization (substring match forbidden) and the exact model id must
be listed. Only then is gate 8 written as boolean ``true`` with
``outcome: passed``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

REPO = ROOT.parent
PROVENANCE_FILES = (
    "src/m37jc_smoke.py",
    "src/jlens_vllm_telemetry/bridge.py",
    "src/jlens_vllm_telemetry/worker_ext.py",
    "reports/telemetry/m36v_phase1_router_telemetry.json",
)
SEMANTIC_KEYS = frozenset({
    "group_completion", "group_continuation", "group_verification",
    "group_error_conflict", "group_uncertainty"})
FORBIDDEN_KEYS = frozenset({
    "prompt", "prompts", "text", "output_text", "token_ids", "readout",
    "hidden", "hidden_states", "weights", "activations", "routes",
    "trace", "logits", "npz_path"})

ENVELOPE_SRC = "reports/telemetry/m36v_phase1_router_telemetry.json"
OUT = "reports/telemetry/m37jc_phase0b_smoke.json"
MAX_TOKENS = 256
MEM_GATE_GIB = 44.0
OVERHEAD_GATE = 1.50
EXPECTED_RANK_SET = frozenset({0, 1})
FROZEN_LAYERS = [4, 12, 20, 28, 36]
FROZEN_CADENCE = 32
FROZEN_TOP_K = 10
SERVING_URL = "http://localhost:9069/v1"
SERVING_PROBE = "Reply with exactly: SERVING-OK"

TECHNICAL_GATE_KEYS = frozenset({
    "disabled_path_within_envelope",
    "install_conformance_all_ranks",
    "dispatch_identity_all_prompts_all_ranks",
    "readout_conformance_all_prompts",
    "enabled_divergence_within_envelope",
    "combined_peak_within_44gib",
    "overhead_within_1p50",
    "cleanup_verified_all_ranks",
})

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


# -- provenance (steer 04920b0 item 4) ------------------------------------

def source_provenance() -> dict:
    """Exact git commit (clean tracked tree required) + sha256 of the
    committed bytes of every provenance-pinned file."""
    dirty = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=REPO, capture_output=True, text=True).stdout.strip()
    if dirty:
        raise SmokeBlocked("repository has uncommitted tracked changes")
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO,
        capture_output=True, text=True).stdout.strip()
    if len(commit) != 40:
        raise SmokeBlocked("could not derive full source commit")
    hashes = {}
    for rel in PROVENANCE_FILES:
        blob = subprocess.run(
            ["git", "show", f"HEAD:{rel}"], cwd=REPO,
            capture_output=True).stdout
        disk = (REPO / rel).read_bytes()
        if blob != disk:
            raise SmokeBlocked(f"working copy differs from HEAD: {rel}")
        hashes[rel] = hashlib.sha256(blob).hexdigest()
    return {"source_commit": commit, "file_sha256": hashes}


def verify_provenance(recorded: dict) -> None:
    """Recompute provenance and require exact equality (finalization)."""
    current = source_provenance()
    if recorded != current:
        raise SmokeBlocked("source provenance mismatch at finalization")


def audit_aggregate_only(obj, path="") -> None:
    """Recursive forbidden-key / private-path audit for public artifacts."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in FORBIDDEN_KEYS:
                raise SmokeBlocked(f"forbidden key '{k}' at {path}")
            audit_aggregate_only(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            audit_aggregate_only(v, f"{path}[{i}]")
    elif isinstance(obj, str):
        if "/home/" in obj or "/mnt/" in obj:
            raise SmokeBlocked(f"private path in artifact at {path}")


def expected_steps(n_decode: int, cadence: int = FROZEN_CADENCE) -> list:
    """The exact frozen schedule: periodic checkpoints 31,63,... < N,
    then N-1 exactly once when not already periodic."""
    steps = list(range(cadence - 1, n_decode, cadence))
    if n_decode > 0 and (not steps or steps[-1] != n_decode - 1):
        steps.append(n_decode - 1)
    return steps


# -- pure gate logic (unit-tested) ---------------------------------------

def envelope_from_artifact(artifact: dict) -> dict:
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


def _rank_set_ok(items: list[dict]) -> bool:
    ranks = [i.get("rank") for i in items]
    return (len(ranks) == len(EXPECTED_RANK_SET)
            and set(ranks) == set(EXPECTED_RANK_SET))


def check_identity_per_prompt(per_prompt_summaries: list[list[dict]],
                              n_prompts: int) -> dict:
    """Every prompt, every rank: exact rank set {0,1}, zero counters."""
    mism_max = miss_max = -1
    mism_sum = miss_sum = failures = 0
    ok = len(per_prompt_summaries) == n_prompts
    for summaries in per_prompt_summaries:
        prompt_ok = _rank_set_ok(summaries)
        for s in summaries:
            m = int(s.get("id_mismatch_total", -1))
            d = int(s.get("dispatch_missed_total", -1))
            mism_max, miss_max = max(mism_max, m), max(miss_max, d)
            mism_sum += max(m, 0)
            miss_sum += max(d, 0)
            prompt_ok &= (m == 0 and d == 0)
        failures += 0 if prompt_ok else 1
        ok &= prompt_ok
    return {"ok": bool(ok), "prompts_checked": len(per_prompt_summaries),
            "prompt_failures": failures,
            "id_mismatch_max": mism_max, "id_mismatch_sum": mism_sum,
            "dispatch_missed_max": miss_max,
            "dispatch_missed_sum": miss_sum}


def _validate_auth_readout(f: dict) -> None:
    """Structural validation of one authoritative fetch (raises)."""
    if f.get("layers") != FROZEN_LAYERS:
        raise SmokeBlocked("layers != frozen set")
    if f.get("cadence") != FROZEN_CADENCE or f.get("top_k") != FROZEN_TOP_K:
        raise SmokeBlocked("cadence/top_k mismatch")
    n_layers = len(FROZEN_LAYERS)
    for key in ("decode_steps", "captured_slots", "dropped"):
        if len(f.get(key, [])) != n_layers:
            raise SmokeBlocked(f"{key} count != {n_layers}")
    readout = f.get("readout") or {}
    if set(readout) != {str(l) for l in FROZEN_LAYERS}:
        raise SmokeBlocked("readout missing frozen layers or empty")
    expected_calls = 0
    from jlens_vllm_telemetry.bridge import SemanticBridgeCollector
    chunk = SemanticBridgeCollector.PROJECTION_CHUNK_SLOTS
    for li, layer in enumerate(FROZEN_LAYERS):
        steps_total = int(f["decode_steps"][li])
        if steps_total <= 0:
            raise SmokeBlocked("zero decode steps")
        want = expected_steps(steps_total)
        data = readout[str(layer)]
        steps, ids = data.get("steps", []), data.get("token_ids", [])
        # Exact frozen schedule, not merely monotone-in-range
        # (steer 04920b0 item 2).
        if steps != want:
            raise SmokeBlocked("steps != frozen cadence schedule")
        if len(ids) != len(steps):
            raise SmokeBlocked("misaligned steps/token_ids")
        if any(len(row) != FROZEN_TOP_K for row in ids):
            raise SmokeBlocked("top-k row width != 10")
        if not data.get("finite"):
            raise SmokeBlocked("non-finite readout")
        n_periodic = len(list(range(FROZEN_CADENCE - 1, steps_total,
                                    FROZEN_CADENCE)))
        if int(f["captured_slots"][li]) != n_periodic:
            raise SmokeBlocked("captured_slots != periodic checkpoints")
        if int(f["dropped"][li]) != 0:
            raise SmokeBlocked("dropped != 0 under smoke capacity")
        expected_calls += math.ceil(len(want) / chunk)
    if int(f.get("projection_calls", -1)) != expected_calls:
        raise SmokeBlocked("projection_calls != frozen schedule sum")


def check_authoritative(fetches: list[dict], vocab_size: int,
                        semantic_fn) -> dict:
    """Per-prompt cross-rank conformance; empty readouts FAIL."""
    result = {"ok": False, "n_authoritative": 0, "reason": None}
    try:
        if not _rank_set_ok(fetches):
            raise SmokeBlocked("rank set != {0,1}")
        auth = [f for f in fetches if f.get("authoritative")]
        non = [f for f in fetches if not f.get("authoritative")]
        if not auth:
            raise SmokeBlocked("no authoritative rank")
        if any(f.get("readout") for f in non):
            raise SmokeBlocked("non-authoritative readout leak")
        for f in auth:
            _validate_auth_readout(f)
            for data in f["readout"].values():
                for row in data["token_ids"]:
                    if any(t < 0 or t >= vocab_size for t in row):
                        raise SmokeBlocked("id outside global vocabulary")
        sem = [semantic_fn(f) for f in auth]
        for s in sem:
            if set(s) != SEMANTIC_KEYS:
                raise SmokeBlocked("semantic key set != frozen five groups")
            if any(not isinstance(v, float) or not math.isfinite(v)
                   for v in s.values()):
                raise SmokeBlocked("non-finite semantic aggregate")
        first = auth[0]
        for f in auth[1:]:
            if (f["readout"] != first["readout"]
                    or f.get("decode_steps") != first.get("decode_steps")):
                raise SmokeBlocked("authoritative ranks disagree")
        if sem[1:] and any(s != sem[0] for s in sem[1:]):
            raise SmokeBlocked("semantic aggregates disagree across ranks")
        for key in ("projection_calls", "decode_steps", "captured_slots",
                    "dropped"):
            if len({json.dumps(f.get(key)) for f in fetches}) != 1:
                raise SmokeBlocked(f"cross-rank {key} disagreement")
        result.update(ok=True, n_authoritative=len(auth),
                      semantic=sem[0])
    except SmokeBlocked as exc:
        result["reason"] = str(exc)
    return result


BRIDGE_INSTALL_FIELDS = ("bridge_layers", "cadence", "top_k", "n_slots",
                         "hidden_size", "n_decoder_layers")
TELEMETRY_INSTALL_FIELDS = ("num_moe_layers", "layer_ids", "num_experts",
                            "router_top_k", "capacity_tokens",
                            "raw_sample_tokens")


def check_install(bridge_installs: list[dict],
                  telemetry_installs: list[dict]) -> dict:
    """Complete all-rank install-metadata conformance (04920b0 item 5)."""
    ok, reason = True, None
    try:
        for name, items, fields in (
                ("bridge", bridge_installs, BRIDGE_INSTALL_FIELDS),
                ("telemetry", telemetry_installs,
                 TELEMETRY_INSTALL_FIELDS)):
            if not _rank_set_ok(items):
                raise SmokeBlocked(f"{name} install rank set != {{0,1}}")
            if any("error" in i for i in items):
                raise SmokeBlocked(f"{name} install error")
            for field in fields:
                values = {json.dumps(i.get(field, "__missing__"))
                          for i in items}
                if '"__missing__"' in values:
                    raise SmokeBlocked(f"{name} missing field {field}")
                if len(values) != 1:
                    raise SmokeBlocked(f"{name} cross-rank {field} "
                                       "disagreement")
        b0 = bridge_installs[0]
        if b0["bridge_layers"] != FROZEN_LAYERS:
            raise SmokeBlocked("bridge layers != frozen set")
        if b0["cadence"] != FROZEN_CADENCE or b0["top_k"] != FROZEN_TOP_K:
            raise SmokeBlocked("bridge cadence/top_k != frozen")
        if b0["n_slots"] != 80:
            raise SmokeBlocked("bridge slot capacity != 80")
        if b0["n_decoder_layers"] != 40:
            raise SmokeBlocked("unexpected decoder depth")
        if telemetry_installs[0]["num_moe_layers"] != 40:
            raise SmokeBlocked("unexpected MoE layer count")
    except SmokeBlocked as exc:
        ok, reason = False, str(exc)
    return {"ok": bool(ok), "reason": reason}


CLEANUP_STEPS = (
    ("jlens_bridge_set_enabled", (False,), False),
    ("jlens_set_telemetry_enabled", (False,), False),
    ("jlens_bridge_uninstall", (), True),
    ("jlens_uninstall_telemetry", (), True),
)


def run_cleanup(llm, expected_ranks: int) -> dict:
    """Ordered per-rank cleanup + final absent/disabled postcondition
    verification on every rank (steer 04920b0 item 1)."""
    report, ok = [], True
    for method, rpc_args, expect in CLEANUP_STEPS:
        try:
            results = llm.collective_rpc(method, args=rpc_args)
            step_ok = (len(results) == expected_ranks
                       and all(r == expect for r in results))
        except Exception as exc:
            results, step_ok = [f"exception: {type(exc).__name__}"], False
        report.append({"step": method, "ok": bool(step_ok)})
        ok &= step_ok
    try:
        statuses = llm.collective_rpc("jlens_status")
        post_ok = (len(statuses) == expected_ranks
                   and {s.get("rank") for s in statuses}
                   == set(EXPECTED_RANK_SET)
                   and all(not s.get("bridge_installed")
                           and not s.get("bridge_enabled")
                           and not s.get("telemetry_installed")
                           and not s.get("telemetry_enabled")
                           for s in statuses))
    except Exception:
        post_ok = False
    report.append({"step": "postcondition_absent_all_ranks",
                   "ok": bool(post_ok)})
    ok &= post_ok
    return {"ok": bool(ok), "steps": report}


def verify_technical_artifact(technical: dict,
                              check_sources: bool = True) -> str:
    """Internal-consistency check before finalization. Returns the
    CANONICAL-JSON content hash of the technical artifact (sorted-key
    JSON serialization — explicitly not raw file bytes; labeled as
    such in the final artifact)."""
    if technical.get("schema_version") != 1:
        raise SmokeBlocked("schema_version mismatch")
    if technical.get("run_kind") != "m37jc_phase0b_smoke":
        raise SmokeBlocked("run_kind mismatch")
    prov = technical.get("provenance")
    if (not isinstance(prov, dict)
            or len(prov.get("source_commit", "")) != 40
            or set(prov.get("file_sha256", {})) != set(PROVENANCE_FILES)):
        raise SmokeBlocked("missing or incomplete source provenance")
    if check_sources:
        verify_provenance(prov)      # recompute; exact equality required
    if not technical.get("override_hash"):
        raise SmokeBlocked("missing override_hash")
    if not technical.get("envelope", {}).get("sha256"):
        raise SmokeBlocked("missing envelope hash")
    gates = technical.get("gates")
    if not isinstance(gates, dict) or set(gates) != TECHNICAL_GATE_KEYS:
        raise SmokeBlocked("gate-key set incomplete or unexpected")
    if any(g is not True for g in gates.values()):
        raise SmokeBlocked("non-true technical gate")
    if technical.get("outcome") != "technical_gates_passed_pending_restore":
        raise SmokeBlocked("outcome is not pending-restore")
    if "serving_restored_and_verified" in gates:
        raise SmokeBlocked("gate 8 pre-exists")
    if "aggregate" not in str(technical.get("privacy_check_status", "")):
        raise SmokeBlocked("privacy status missing")
    audit_aggregate_only(technical)
    blob = json.dumps(technical, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()


def finalize_outcome(technical: dict, restore_ok: bool,
                     restore_record: dict, technical_sha: str) -> dict:
    final = dict(technical)
    final["gates"] = dict(technical["gates"])
    final["gates"]["serving_restored_and_verified"] = bool(restore_ok)
    final["restoration_verification"] = restore_record
    final["technical_artifact_canonical_json_sha256"] = technical_sha
    if (technical.get("outcome") == "technical_gates_passed_pending_restore"
            and restore_ok):
        audit_aggregate_only(final)
        final["outcome"] = "passed"
    else:
        final["outcome"] = "agents_a1_semantic_bridge_feasibility_blocked"
    return final


def reply_is_exact(reply: str) -> bool:
    return reply.strip() == "SERVING-OK"


# -- live phases ----------------------------------------------------------

def write_blocked(out_path: str, stage: str, exc: Exception,
                  cleanup: dict | None) -> None:
    Path(out_path).write_text(json.dumps({
        "schema_version": 1,
        "run_kind": "m37jc_phase0b_smoke",
        "outcome": "agents_a1_semantic_bridge_feasibility_blocked",
        "lifecycle_stage": stage,
        "exception_class": type(exc).__name__,
        "cleanup": cleanup,
        "privacy_check_status": "aggregate blocker only",
    }, indent=1) + "\n")


def phase_smoke(args) -> int:
    from m36v_phase0 import GpuPeakSampler
    from m36v_phase1 import override_hash
    from m36c_adaptive import make_llm
    from jlens_vllm_telemetry.bridge import semantic_group_scores
    from vllm import SamplingParams

    stage, llm, sampler, installed, cleanup = "init", None, None, False, None
    try:
        stage = "provenance"
        prov = source_provenance()   # clean tree + hashes, pre-engine
        env = envelope_from_artifact(json.load(open(ENVELOPE_SRC)))
        stage = "sampler_start"
        sampler = GpuPeakSampler()
        sampler.start()
        stage = "engine_construction"
        llm = make_llm(args.model_ref)
        tokenizer = llm.get_tokenizer()
        params = SamplingParams(temperature=0.0, max_tokens=MAX_TOKENS)
        hf_config = llm.llm_engine.model_config.hf_config
        text_cfg = getattr(hf_config, "text_config", hf_config)
        vocab_size = int(text_cfg.vocab_size)

        stage = "leg_a"
        ids_a, times_a = [], []
        for prompt in PROMPTS:
            t0 = time.time()
            out = llm.chat([[{"role": "user", "content": prompt}]],
                           params, use_tqdm=False)[0]
            times_a.append(time.time() - t0)
            ids_a.append(list(out.outputs[0].token_ids))

        stage = "install"
        installed = True   # attempted: exception path must clean up even
        # if only one component or one rank installed (04920b0 item 1)
        bridge_installs = llm.collective_rpc("jlens_bridge_install", args=(
            {"hidden_size": text_cfg.hidden_size},))
        telem_installs = llm.collective_rpc("jlens_install_telemetry",
                                            args=({"num_experts":
                                                   text_cfg.num_experts,
                                                   "top_k":
                                                   text_cfg.
                                                   num_experts_per_tok,
                                                   "capacity_tokens": 4096,
                                                   "raw_sample_tokens": 4},))
        install_conf = check_install(bridge_installs, telem_installs)

        stage = "leg_b"
        ids_b, times_b = [], []
        for prompt in PROMPTS:
            t0 = time.time()
            out = llm.chat([[{"role": "user", "content": prompt}]],
                           params, use_tqdm=False)[0]
            times_b.append(time.time() - t0)
            ids_b.append(list(out.outputs[0].token_ids))

        stage = "leg_c"
        llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))
        llm.collective_rpc("jlens_bridge_set_enabled", args=(True,))

        def semantic_fn(fetch):
            return semantic_group_scores(
                fetch, lambda t: tokenizer.decode([t]))

        ids_c, times_c = [], []
        prompt_identity, prompt_conformance = [], []
        for prompt in PROMPTS:
            llm.collective_rpc("jlens_bridge_reset")
            llm.collective_rpc("jlens_reset_telemetry")
            t0 = time.time()
            out = llm.chat([[{"role": "user", "content": prompt}]],
                           params, use_tqdm=False)[0]
            times_c.append(time.time() - t0)
            ids_c.append(list(out.outputs[0].token_ids))
            # Per-prompt fetches BEFORE any subsequent reset.
            prompt_identity.append(
                llm.collective_rpc("jlens_fetch_summary", args=(1,)))
            prompt_conformance.append(check_authoritative(
                llm.collective_rpc("jlens_bridge_fetch"),
                vocab_size, semantic_fn))
        identity = check_identity_per_prompt(prompt_identity, len(PROMPTS))
        stage = "gates"
    except Exception as exc:
        cleanup = (run_cleanup(llm, len(EXPECTED_RANK_SET))
                   if installed and llm is not None else
                   {"ok": True, "steps": []})
        if llm is not None:
            del llm
        if sampler is not None:
            sampler.stop_flag = True
            time.sleep(1.5)
        write_blocked(args.out, stage, exc, cleanup)
        print(f"[m37jc] smoke BLOCKED at {stage}: {type(exc).__name__}",
              flush=True)
        return 1
    else:
        cleanup = run_cleanup(llm, len(EXPECTED_RANK_SET))
        del llm
        sampler.stop_flag = True
        time.sleep(1.5)

    ab = divergence_stats(ids_a, ids_b)
    bc = divergence_stats(ids_b, ids_c)
    overhead = statistics.median(c / b for b, c in zip(times_b, times_c))
    peak_gib = sum(sampler.peaks.values()) / 1024.0
    conf_ok = (len(prompt_conformance) == len(PROMPTS)
               and all(c["ok"] for c in prompt_conformance))
    gates = {
        "disabled_path_within_envelope": within_envelope(ab, env),
        "install_conformance_all_ranks": install_conf["ok"],
        "dispatch_identity_all_prompts_all_ranks": identity["ok"],
        "readout_conformance_all_prompts": conf_ok,
        "enabled_divergence_within_envelope": within_envelope(bc, env),
        "combined_peak_within_44gib": peak_gib <= MEM_GATE_GIB,
        "overhead_within_1p50": overhead <= OVERHEAD_GATE,
        "cleanup_verified_all_ranks": cleanup["ok"],
    }
    technical_pass = all(gates.values())
    sem_agg = {}
    sems = [c.get("semantic") for c in prompt_conformance
            if c.get("semantic")]
    if sems:
        for key in sems[0]:
            vals = [s[key] for s in sems]
            sem_agg[key] = {"mean": round(statistics.mean(vals), 2),
                            "max": max(vals)}
    payload = {
        "schema_version": 1,
        "run_kind": "m37jc_phase0b_smoke",
        "steer": "04920b0",
        "provenance": prov,
        "override_hash": override_hash(),
        "envelope": env,
        "n_prompts": len(PROMPTS),
        "max_tokens": MAX_TOKENS,
        "install_conformance": install_conf,
        "divergence_pre_vs_disabled": ab,
        "divergence_disabled_vs_enabled": bc,
        "identity": identity,
        "readout_conformance_failures": sum(
            0 if c["ok"] else 1 for c in prompt_conformance),
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
        technical_sha = verify_technical_artifact(technical)
    except SmokeBlocked as exc:
        final = dict(technical)
        final["outcome"] = "agents_a1_semantic_bridge_feasibility_blocked"
        final["finalization_blocker"] = str(exc)
        Path(args.out).write_text(json.dumps(final, indent=1) + "\n")
        print(f"[m37jc] finalize BLOCKED: {exc}", flush=True)
        return 1
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
        record["reply_exact"] = reply_is_exact(reply)
        record["model_listed_exact"] = "agents-a1" in model_ids
        # Runbook health check: the service health endpoint must answer.
        health_ok = False
        try:
            with urllib.request.urlopen(
                    SERVING_URL.rsplit("/v1", 1)[0] + "/health",
                    timeout=30) as resp:
                health_ok = resp.status == 200
        except Exception:
            health_ok = False
        record["health_endpoint_ok"] = health_ok
        restore_ok = (record["reply_exact"]
                      and record["model_listed_exact"] and health_ok)
    except Exception as exc:
        record["error"] = type(exc).__name__
    final = finalize_outcome(technical, restore_ok, record, technical_sha)
    Path(args.out).write_text(json.dumps(final, indent=1) + "\n")
    print(f"[m37jc] finalize: outcome={final['outcome']} "
          f"restore={record}", flush=True)
    return 0 if final["outcome"] == "passed" else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--phase", choices=("smoke", "finalize"),
                    default="smoke")
    ap.add_argument("--model-ref")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    if args.phase == "smoke":
        if not args.model_ref:
            raise SystemExit("--model-ref required for smoke phase")
        return phase_smoke(args)
    return phase_finalize(args)


if __name__ == "__main__":
    raise SystemExit(main())
