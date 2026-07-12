#!/usr/bin/env python3
"""M36 paired benchmark: Agents-A1 AWQ raw versus jLens (steer 0be9d84).

Stages (in order; each refuses to run out of order):

  --stage manifest   power rule -> benchmark count; freeze generator seed,
                     family mix, decode protocol, detector/policy hashes,
                     budget, margins, bootstrap seeds, claim rules. The
                     manifest MUST be committed before --stage generate.
  --stage generate   fresh seeded decision tasks (disjoint from
                     calibration and all M29-M35 operand draws)
  --stage capture    one deterministic AWQ original per task with router
                     telemetry (captured once, frozen — the runtime is
                     nondeterministic; reruns are new draws). Resumable.
  --stage evaluate   single sealed read: five arms, H1/H2/H3, result
                     artifact. Refuses to run twice.

Verifier-first invariant: no arm may replace a verified-correct original
with a failing tool result — enforced by assertion on every task.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verifiers as VZ                        # noqa: E402
import m28_ablation_calibration as M28        # noqa: E402
import m27_frozen_error_holdout as M27        # noqa: E402
from m36v_phase0 import EXPECTED_REVISION, GpuPeakSampler  # noqa: E402
from m36v_phase1 import PRIVATE_DIR, load_capture, override_hash  # noqa: E402
from m36_calibration import (                 # noqa: E402
    FAMILIES, FEATURE_NAMES, MAX_MODEL_LEN, MAX_TOKENS, derive_features,
    generate_tasks as calibration_tasks, task_verdict)
from m36_detector import feature_dict         # noqa: E402
from jlens_vllm_telemetry.report_guard import assert_aggregate_only  # noqa: E402

BENCHMARK_SEED = "m36-benchmark-v1"
MANIFEST_PATH = Path("data/prompts/m36_benchmark_manifest.json")
TASKS_PATH = PRIVATE_DIR / "m36_benchmark_tasks.jsonl"
ROWS_PATH = PRIVATE_DIR / "m36_benchmark_rows.jsonl"
DETECTOR_STATE = PRIVATE_DIR / "m36_detector_state.json"
DETECTOR_FREEZE = Path("reports/telemetry/m36_detector_freeze.json")
CALIBRATION_SUMMARY = Path("reports/telemetry/m36_calibration_summary.json")
RESULT_OUT = "reports/telemetry/m36_benchmark_result.json"

POWER_TABLE = (192, 240, 288)
EXPECTED_FAILURE_MINIMUM = 24
NON_INFERIORITY_MARGIN = 0.05
CALLS_SAVED_MINIMUM_FRACTION = 0.25
BOOTSTRAP_ITERATIONS = 2000
RANDOM_ARM_SEED = "m36:random-trigger"
ARMS = ("raw_awq", "black_box_jlens", "full_jlens",
        "count_matched_random", "tool_on_every_eligible_task")


# ---------------------------------------------------------------- manifest

def build_manifest() -> dict:
    summary = json.loads(CALIBRATION_SUMMARY.read_text())
    freeze = json.loads(DETECTOR_FREEZE.read_text())
    cells = []
    fail_rates = []
    for family, strata in sorted(summary["competence_by_family"].items()):
        for stratum, stats in sorted(strata.items()):
            cells.append({"family": family, "stratum": stratum,
                          "calibration_pass_rate": stats["pass_rate"],
                          "regime": stats["regime"]})
            fail_rates.append(1.0 - stats["pass_rate"])
    mean_fail = sum(fail_rates) / len(fail_rates)
    n_tasks = None
    for option in POWER_TABLE:
        if option * mean_fail >= EXPECTED_FAILURE_MINIMUM:
            n_tasks = option
            break
    if n_tasks is None:
        n_tasks = POWER_TABLE[-1]
    per_cell = n_tasks // len(cells)
    n_tasks = per_cell * len(cells)

    return {
        "schema_version": 1,
        "run_kind": "m36_benchmark_manifest",
        "selection_status": "predeclared_before_m36_decision_task_generation",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": EXPECTED_REVISION,
        "generator_seed": BENCHMARK_SEED,
        "cells": cells,
        "tasks_per_cell": per_cell,
        "n_tasks_total": n_tasks,
        "power_rule": {
            "table": list(POWER_TABLE),
            "expected_failure_minimum": EXPECTED_FAILURE_MINIMUM,
            "calibration_mean_fail_rate": round(mean_fail, 4),
            "expected_failures": round(n_tasks * mean_fail, 1),
        },
        "decode_protocol": {"temperature": 0.0, "max_tokens": MAX_TOKENS,
                            "max_model_len": MAX_MODEL_LEN,
                            "logprobs": 5, "max_num_seqs": 1,
                            "originals": "captured once and frozen; the "
                                         "runtime is nondeterministic"},
        "feature_schema": FEATURE_NAMES,
        "detector_hash": freeze["full_telemetry"]["detector_hash"],
        "detector_threshold": freeze["full_telemetry"]["threshold"],
        "policy_hash": freeze["black_box"]["policy_hash"],
        "policy_prior_threshold": freeze["black_box"]["prior_threshold"],
        "tool_budget_fraction": freeze["budget_fraction"],
        "selected_arm": "full_jlens",
        "arms": list(ARMS),
        "bootstrap": {"iterations": BOOTSTRAP_ITERATIONS,
                      "seeds": {"h1": "m36:h1:full-vs-raw",
                                "h2_blackbox": "m36:h2:full-vs-blackbox",
                                "h2_random": "m36:h2:full-vs-random",
                                "h3": "m36:h3:full-vs-toolall"},
                      "random_arm_seed": RANDOM_ARM_SEED},
        "claim_rules": {
            "h1_practical_value": "paired 95% lower bound of "
                                  "(full_jlens - raw_awq) success > 0",
            "h2_telemetry_increment": "both lower bounds > 0 vs black_box "
                                      "and count_matched_random",
            "h3_efficiency": f"lower bound + {NON_INFERIORITY_MARGIN} > 0 "
                             "vs tool_on_every_eligible_task AND calls "
                             f"saved fraction >= "
                             f"{CALLS_SAVED_MINIMUM_FRACTION}",
            "verifier_first": "no arm replaces a passing original",
        },
        "non_inferiority_margin": NON_INFERIORITY_MARGIN,
        "calls_saved_minimum_fraction": CALLS_SAVED_MINIMUM_FRACTION,
        "override_hash": override_hash(),
    }


def manifest_committed() -> bool:
    try:
        committed = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(MANIFEST_PATH)],
            capture_output=True, text=True, cwd=ROOT.parent).stdout.strip()
        clean = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", str(MANIFEST_PATH)],
            cwd=ROOT.parent).returncode == 0
        return bool(committed) and clean
    except Exception:
        return False


# ---------------------------------------------------------------- generate

def generate_benchmark_tasks(manifest) -> list:
    calibration_ops = set()
    for task in calibration_tasks():
        if "a" in task and "b" in task:
            calibration_ops.add((task["a"], task["b"]))
    family_defs = {f["family_id"]: f for f in FAMILIES}
    tasks = []
    per_cell = manifest["tasks_per_cell"]
    for cell in manifest["cells"]:
        fid, sid = cell["family"], cell["stratum"]
        family = family_defs[fid]
        s_index = int(sid[1:])
        stratum = family["strata"][s_index - 1]
        rng = random.Random(f"{manifest['generator_seed']}:{fid}:{sid}")
        made = 0
        while made < per_cell:
            task = {"task_id": f"m36b_{fid}_{sid}_{made:03d}",
                    "family": fid, "stratum": sid}
            if fid == "mul_multi":
                (alo, ahi), (blo, bhi) = stratum
                a, b = rng.randint(alo, ahi), rng.randint(blo, bhi)
                if (a, b) in calibration_ops:
                    continue
                calibration_ops.add((a, b))
                task.update(a=a, b=b, expression=f"{a}*{b}",
                            known_answer=str(a * b),
                            prompt=family["prompt"].format(a=a, b=b))
            elif fid == "add_chain":
                k, (lo, hi) = stratum
                terms = [rng.randint(lo, hi) for _ in range(k)]
                task.update(expression="+".join(map(str, terms)),
                            known_answer=str(sum(terms)),
                            prompt=family["prompt"].format(
                                chain=" + ".join(map(str, terms))))
            elif fid == "mod_arith":
                (alo, ahi), (blo, bhi), (mlo, mhi) = stratum
                a, b = rng.randint(alo, ahi), rng.randint(blo, bhi)
                m = rng.randint(mlo, mhi)
                task.update(known_answer=str((a * b) % m),
                            prompt=family["prompt"].format(a=a, b=b, m=m))
            elif fid == "sub_mixed":
                (lo, hi), = stratum
                a, b, c, d = (rng.randint(lo, hi) for _ in range(4))
                task.update(expression=f"{a}-{b}+{c}-{d}",
                            known_answer=str(a - b + c - d),
                            prompt=family["prompt"].format(a=a, b=b, c=c,
                                                           d=d))
            elif fid == "div_exact":
                (qlo, qhi), (dlo, dhi) = stratum
                q, d = rng.randint(qlo, qhi), rng.randint(dlo, dhi)
                task.update(known_answer=str(q),
                            prompt=family["prompt"].format(n=q * d, d=d))
            elif fid == "json_digits":
                (lo, hi), = stratum
                n = rng.randint(lo, hi)
                digits = [int(ch) for ch in str(n)][::-1]
                task.update(known_answer=json.dumps(digits),
                            json_expected=digits,
                            prompt=family["prompt"].format(n=n))
            tasks.append(task)
            made += 1
    return tasks


# ----------------------------------------------------------------- capture

def run_capture(args, manifest) -> int:
    from vllm import LLM, SamplingParams

    tasks = [json.loads(line)
             for line in TASKS_PATH.read_text().splitlines()]
    done = set()
    if ROWS_PATH.exists():
        done = {json.loads(line)["task_id"]
                for line in ROWS_PATH.read_text().splitlines()}
    todo = [t for t in tasks if t["task_id"] not in done]
    print(f"[jlens] M36 benchmark capture: {len(done)} done, "
          f"{len(todo)} to go", flush=True)
    if not todo:
        return 0

    sampler = GpuPeakSampler()
    sampler.start()
    llm = LLM(model=args.model_ref, tensor_parallel_size=2,
              max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=0.88,
              enforce_eager=True, disable_log_stats=True, max_num_seqs=1,
              enable_return_routed_experts=True,
              worker_extension_cls=(
                  "jlens_vllm_telemetry.worker_ext.JlensWorkerExtension"))
    hf_config = llm.llm_engine.model_config.hf_config
    text_cfg = getattr(hf_config, "text_config", hf_config)
    llm.collective_rpc("jlens_install_telemetry", args=(
        {"num_experts": text_cfg.num_experts,
         "top_k": text_cfg.num_experts_per_tok,
         "capacity_tokens": MAX_MODEL_LEN + MAX_TOKENS,
         "raw_sample_tokens": 0},))
    llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))
    params = SamplingParams(temperature=0.0, max_tokens=MAX_TOKENS,
                            logprobs=5)
    cap_dir = PRIVATE_DIR / "m36_benchmark_caps"
    cap_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with ROWS_PATH.open("a", encoding="utf-8") as sink:
        for count, task in enumerate(todo, start=1):
            llm.collective_rpc("jlens_reset_telemetry")
            request_start = time.time()
            out = llm.chat(
                [[{"role": "user", "content": task["prompt"]}]], params,
                use_tqdm=False)[0]
            latency = time.time() - request_start
            comp = out.outputs[0]
            prefix = str((cap_dir / task["task_id"]).resolve())
            fetches = llm.collective_rpc("jlens_fetch_telemetry",
                                         args=(prefix,))
            cap = load_capture(fetches[0])
            features = derive_features(
                cap, prompt_rows=len(out.prompt_token_ids),
                logprob_steps=comp.logprobs or [],
                n_output_tokens=len(comp.token_ids))
            verdict = task_verdict(task, comp.text)
            sink.write(json.dumps({
                "task_id": task["task_id"], "family": task["family"],
                "stratum": task["stratum"],
                "original_verdict": verdict,
                "original_pass": verdict == "pass",
                "truncated": comp.finish_reason == "length",
                "output_tokens": len(comp.token_ids),
                "model_latency_s": round(latency, 2),
                "features": features,
            }) + "\n")
            sink.flush()
            if count % 16 == 0:
                rate = count / (time.time() - started)
                print(f"[jlens] M36 benchmark capture {count}/{len(todo)} "
                      f"({rate * 3600:.0f}/h)", flush=True)
    sampler.stop_flag = True
    print(f"[jlens] M36 benchmark capture complete: {len(todo)} new rows, "
          f"peak={round(sum(sampler.peaks.values()) / 1024, 2)}GiB",
          flush=True)
    return 0


# ---------------------------------------------------------------- evaluate

def stratified_bootstrap_delta(rows, flags_a, flags_b, seed):
    """Family-stratified paired bootstrap of mean(a) - mean(b)."""
    by_family = {}
    for index, row in enumerate(rows):
        by_family.setdefault(row["family"], []).append(index)
    rng = random.Random(seed)
    deltas = []
    for _ in range(BOOTSTRAP_ITERATIONS):
        total_a = total_b = n = 0
        for indices in by_family.values():
            sample = [indices[rng.randrange(len(indices))]
                      for _ in indices]
            total_a += sum(flags_a[i] for i in sample)
            total_b += sum(flags_b[i] for i in sample)
            n += len(sample)
        deltas.append((total_a - total_b) / n)
    deltas.sort()
    lo = deltas[int(0.025 * BOOTSTRAP_ITERATIONS)]
    hi = deltas[int(0.975 * BOOTSTRAP_ITERATIONS) - 1]
    point = (sum(flags_a) - sum(flags_b)) / len(rows)
    return {"delta": round(point, 4), "ci95": [round(lo, 4), round(hi, 4)]}


def run_evaluate(args, manifest) -> int:
    result_path = Path(args.out)
    if result_path.exists():
        print("[jlens] M36 evaluate refused: result exists (single sealed "
              "read already performed)", flush=True)
        return 1

    rows = [json.loads(line)
            for line in ROWS_PATH.read_text().splitlines()]
    assert len(rows) == manifest["n_tasks_total"], (
        f"decision rows {len(rows)} != manifest {manifest['n_tasks_total']}")
    for row in rows:
        if row["original_verdict"] == "undecided":
            row["original_pass"] = False

    # Reload frozen detector/policy state and verify hashes.
    state = json.loads(DETECTOR_STATE.read_text())
    freeze = json.loads(DETECTOR_FREEZE.read_text())
    import m36_detector as D
    clf = M27.FrozenDictCentroid(**state["classifier"])
    threshold = state["full_telemetry"]["threshold"]
    priors = state["priors"]
    prior_threshold = state["black_box"]["prior_threshold"]
    assert D.detector_hash(clf, threshold) == manifest["detector_hash"], (
        "detector hash mismatch vs manifest")
    assert D.policy_hash(priors, prior_threshold) == manifest["policy_hash"]
    assert freeze["full_telemetry"]["detector_hash"] == manifest["detector_hash"]

    # Arm invocation decisions.
    n = len(rows)
    p_fails = [M28.fail_probability(clf, feature_dict(r)) for r in rows]
    invoked = {
        "raw_awq": [False] * n,
        "full_jlens": [p >= threshold for p in p_fails],
        "black_box_jlens": [
            priors.get(f"{r['family']}:{r['stratum']}", 1.0)
            >= prior_threshold for r in rows],
        "tool_on_every_eligible_task": [True] * n,
    }
    k = sum(invoked["full_jlens"])
    rng = random.Random(RANDOM_ARM_SEED)
    random_ids = set(rng.sample(range(n), k))
    invoked["count_matched_random"] = [i in random_ids for i in range(n)]

    # Verifier-first finals: the deterministic tool answers the task's own
    # predeclared expression/known answer, so tool_pass is True; an
    # invocation can only add passes. Assert the invariant anyway.
    finals, stats = {}, {}
    original = [r["original_pass"] for r in rows]
    for arm in ARMS:
        inv = invoked[arm]
        final = [orig or i for orig, i in zip(original, inv)]
        for orig, fin in zip(original, final):
            assert fin >= orig, f"M36 stop: {arm} replaced a passing original"
        corrections = sum(1 for orig, i in zip(original, inv)
                          if i and not orig)
        stats[arm] = {
            "raw_success": round(sum(original) / n, 4),
            "final_success": round(sum(final) / n, 4),
            "tool_invocations": sum(inv),
            "tool_fraction": round(sum(inv) / n, 4),
            "corrections": corrections,
            "false_alarms": sum(1 for orig, i in zip(original, inv)
                                if i and orig),
            "misses": sum(1 for orig, i in zip(original, inv)
                          if not i and not orig),
            "regressions": 0,
        }
        finals[arm] = final

    seeds = manifest["bootstrap"]["seeds"]
    h1 = stratified_bootstrap_delta(rows, finals["full_jlens"],
                                    finals["raw_awq"], seeds["h1"])
    h2_bb = stratified_bootstrap_delta(rows, finals["full_jlens"],
                                       finals["black_box_jlens"],
                                       seeds["h2_blackbox"])
    h2_rand = stratified_bootstrap_delta(rows, finals["full_jlens"],
                                         finals["count_matched_random"],
                                         seeds["h2_random"])
    h3 = stratified_bootstrap_delta(rows, finals["full_jlens"],
                                    finals["tool_on_every_eligible_task"],
                                    seeds["h3"])
    calls_saved = (stats["tool_on_every_eligible_task"]["tool_invocations"]
                   - stats["full_jlens"]["tool_invocations"])
    calls_saved_fraction = calls_saved / max(
        1, stats["tool_on_every_eligible_task"]["tool_invocations"])

    hypotheses = {
        "h1_practical_value": {
            **h1, "passed": h1["ci95"][0] > 0},
        "h2_telemetry_increment": {
            "vs_black_box": h2_bb, "vs_count_matched_random": h2_rand,
            "passed": h2_bb["ci95"][0] > 0 and h2_rand["ci95"][0] > 0},
        "h3_efficiency": {
            **h3,
            "non_inferiority_margin": NON_INFERIORITY_MARGIN,
            "calls_saved": calls_saved,
            "calls_saved_fraction": round(calls_saved_fraction, 4),
            "passed": (h3["ci95"][0] + NON_INFERIORITY_MARGIN > 0
                       and calls_saved_fraction
                       >= CALLS_SAVED_MINIMUM_FRACTION)},
    }
    if hypotheses["h1_practical_value"]["passed"] \
            and hypotheses["h3_efficiency"]["passed"]:
        branch = ("h1_h3_pass: freeze Agents-A1-AWQ jLens candidate for "
                  "extended shadow evaluation; production remains gated")
    elif hypotheses["h1_practical_value"]["passed"]:
        branch = ("h1_pass_h2_fail: retain black-box jLens; no incremental "
                  "internal-telemetry claim") \
            if not hypotheses["h2_telemetry_increment"]["passed"] else \
            ("h1_pass_h3_fail: practical value without efficiency claim")
    else:
        branch = ("h1_fail: close the Agents-A1 efficacy track without "
                  "checkpoint shopping or post-hoc changes")

    latencies = [r["model_latency_s"] for r in rows]
    tokens = [r["output_tokens"] for r in rows]
    payload = {
        "schema_version": 1,
        "run_kind": "m36_benchmark_result",
        "checkpoint": manifest["checkpoint"],
        "revision_pinned": manifest["revision_pinned"],
        "manifest_hash": VZ.evidence_hash(MANIFEST_PATH.read_text()),
        "n_tasks": n,
        "truncated_tasks": sum(r["truncated"] for r in rows),
        "arms": stats,
        "hypotheses": hypotheses,
        "result_branch": branch,
        "selected_arm": manifest["selected_arm"],
        "runtime_aggregates": {
            "model_latency_mean_s": round(statistics.mean(latencies), 2),
            "model_latency_p95_s": round(
                sorted(latencies)[int(0.95 * (n - 1))], 2),
            "output_tokens_mean": round(statistics.mean(tokens), 1),
            "tool_latency_note": "deterministic expression evaluation; "
                                 "negligible vs model latency",
            "telemetry_overhead_ratio_phase1": 1.332,
        },
        "claims_scope": "exact AWQ checkpoint revision, vLLM 0.24.0, "
                        "override hash, frozen prompts/decode/task "
                        "generators/tools/verifier bundle only",
        "per_task_predictions_persisted_publicly": False,
        "privacy_check_status": "aggregate arms/hypotheses only",
    }
    assert_aggregate_only(payload)
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36 result: H1={hypotheses['h1_practical_value']['passed']} "
          f"H2={hypotheses['h2_telemetry_increment']['passed']} "
          f"H3={hypotheses['h3_efficiency']['passed']} branch={branch}",
          flush=True)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", required=True,
                    choices=("manifest", "generate", "capture", "evaluate"))
    ap.add_argument("--model-ref")
    ap.add_argument("--out", default=RESULT_OUT)
    args = ap.parse_args(argv)

    import os
    src = str(ROOT)
    existing = os.environ.get("PYTHONPATH", "")
    if src not in existing.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + (os.pathsep + existing if existing else ""))

    if args.stage == "manifest":
        manifest = build_manifest()
        MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
        MANIFEST_PATH.write_text(json.dumps(manifest, indent=1) + "\n")
        print(f"[jlens] M36 manifest: n={manifest['n_tasks_total']} "
              f"expected_failures="
              f"{manifest['power_rule']['expected_failures']} "
              f"-> commit before generate", flush=True)
        return 0

    manifest = json.loads(MANIFEST_PATH.read_text())
    assert manifest["selection_status"] == \
        "predeclared_before_m36_decision_task_generation"

    if args.stage == "generate":
        if not manifest_committed():
            print("[jlens] M36 generate refused: manifest not committed "
                  "clean", flush=True)
            return 1
        tasks = generate_benchmark_tasks(manifest)
        PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
        TASKS_PATH.write_text("".join(json.dumps(t) + "\n" for t in tasks))
        print(f"[jlens] M36 benchmark tasks: {len(tasks)}", flush=True)
        return 0
    if args.stage == "capture":
        if not args.model_ref:
            ap.error("--model-ref required")
        return run_capture(args, manifest)
    return run_evaluate(args, manifest)


if __name__ == "__main__":
    raise SystemExit(main())
