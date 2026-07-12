#!/usr/bin/env python3
"""M36C: profiled, adaptive Agents-A1 calibration (steer 9faf213).

Stages:
  --stage profile   Phase 0: per-component harness timing on a fixed
                    private eight-prompt set (short/medium/truncation-
                    prone) + summary-vs-raw feature equivalence gate
                    (<= 1e-5 per feature) + overhead target check
                    (median non-generation <= 25% of generation).
  --stage adaptive  Phase 1+2: four-row probes per remaining cell at
                    staged budgets (512 -> rescue 2 @1024 -> rescue 1
                    @2048), then selective expansion under the frozen
                    rule until class quotas are met or 192 retained
                    rows are exhausted.

Every output is classified completed_correct / completed_incorrect /
truncated_budget; a capped output is never evidence of incorrect
reasoning. The 88 rows completed before the amendment are preserved and
counted; capped reruns of the same prompt do not count against the
192-row retention cap.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from m36v_phase0 import EXPECTED_REVISION, GpuPeakSampler   # noqa: E402
from m36v_phase1 import PRIVATE_DIR, load_capture, override_hash  # noqa: E402
from m36_calibration import (                                # noqa: E402
    FAMILIES, MAX_MODEL_LEN, ROUTER_FEATURE_NAMES,
    TASKS_PATH as ORIGINAL_TASKS_PATH,
    ROWS_PATH as ORIGINAL_ROWS_PATH,
    logprob_features, router_features, task_verdict)
from jlens_vllm_telemetry.report_guard import assert_aggregate_only  # noqa: E402

PROFILE_SEED = "m36c-profile-v1"
ROWS_PATH = PRIVATE_DIR / "m36c_rows.jsonl"
PROFILE_OUT = "reports/telemetry/m36c_phase0_profile.json"
FRONTIER_OUT = "reports/telemetry/m36c_frontier_map.json"
RESULT_OUT = "reports/telemetry/m36c_calibration_result.json"

PROBE_BUDGET = 512
RESCUE_BUDGETS = (1024, 2048)
RESCUE_COUNTS = (2, 1)          # max reruns per cell at each rescue budget
EQUIVALENCE_TOL = 1e-5
OVERHEAD_TARGET = 0.25
VALIDATION_SAMPLE_EVERY = 16    # full NPZ capture cadence during adaptive

# Frozen expansion rule (steer 9faf213 Phase 2).
MIXED_LOW, MIXED_HIGH = 0.20, 0.80
TRUNC_OK = 0.25
BUDGET_BOUND_TRUNC = 0.50
MIXED_TARGET_ROWS = 16
ANCHOR_TARGET_ROWS = 8
RETENTION_CAP = 192
QUOTAS = {"completed_correct": 48, "completed_incorrect": 48,
          "failure_families": 3, "mixed_cells": 2}


def classify(verdict: str, truncated: bool) -> str:
    if truncated:
        return "truncated_budget"
    return "completed_correct" if verdict == "pass" else "completed_incorrect"


def profile_prompts():
    rng = random.Random(PROFILE_SEED)
    a, b = rng.randint(100, 999), rng.randint(10, 99)
    c = rng.randint(1000, 9999)
    items = [
        {"kind": "short", "prompt": "Reply with exactly the word: READY"},
        {"kind": "short", "prompt": f"What is {a} + {b}? Final number only.",
         "known_answer": str(a + b), "expression": f"{a}+{b}"},
        {"kind": "short", "prompt": f"What is {a} - {b}? Final number only.",
         "known_answer": str(a - b), "expression": f"{a}-{b}"},
        {"kind": "medium", "prompt": f"What is {a} * {b}? Reply with the "
                                     "final number only.",
         "known_answer": str(a * b), "expression": f"{a}*{b}"},
        {"kind": "medium", "prompt": f"What is {c} * {b}? Reply with the "
                                     "final number only.",
         "known_answer": str(c * b), "expression": f"{c}*{b}"},
        {"kind": "medium", "prompt": f"Compute {a} - {b} + {c} - {a}. Reply "
                                     "with the final number only.",
         "known_answer": str(c - b), "expression": f"{a}-{b}+{c}-{a}"},
        {"kind": "truncation_prone",
         "prompt": f"What is {rng.randint(10000, 99999)} * "
                   f"{rng.randint(1000, 9999)}? Reply with the final number "
                   "only."},
        {"kind": "truncation_prone",
         "prompt": f"What is {rng.randint(100000, 999999)} * "
                   f"{rng.randint(10000, 99999)}? Reply with the final "
                   "number only."},
    ]
    for index, item in enumerate(items):
        item["prompt_id"] = f"m36c_profile_{index:02d}"
    return items


def make_llm(model_ref: str):
    from vllm import LLM

    return LLM(model=model_ref, tensor_parallel_size=2,
               max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=0.88,
               enforce_eager=True, disable_log_stats=True, max_num_seqs=1,
               enable_return_routed_experts=True,
               worker_extension_cls=(
                   "jlens_vllm_telemetry.worker_ext.JlensWorkerExtension"))


def install(llm, raw_sample_tokens: int = 4):
    hf_config = llm.llm_engine.model_config.hf_config
    text_cfg = getattr(hf_config, "text_config", hf_config)
    llm.collective_rpc("jlens_install_telemetry", args=(
        {"num_experts": text_cfg.num_experts,
         "top_k": text_cfg.num_experts_per_tok,
         "capacity_tokens": MAX_MODEL_LEN + 2048,
         "raw_sample_tokens": raw_sample_tokens},))
    llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))


def timed_generation(llm, prompt: str, max_tokens: int, save_prefix=None):
    """One instrumented task; returns (record, timings) with per-component
    seconds. The summary path is primary; raw NPZ only when save_prefix."""
    from vllm import SamplingParams

    timings = {}
    t0 = time.time()
    llm.collective_rpc("jlens_reset_telemetry")
    timings["reset_rpc_s"] = time.time() - t0

    params = SamplingParams(temperature=0.0, max_tokens=max_tokens,
                            logprobs=5)
    t0 = time.time()
    out = llm.chat([[{"role": "user", "content": prompt}]], params,
                   use_tqdm=False)[0]
    timings["generation_s"] = time.time() - t0
    comp = out.outputs[0]
    prompt_rows = len(out.prompt_token_ids)

    t0 = time.time()
    summary = llm.collective_rpc(
        "jlens_fetch_summary",
        args=(prompt_rows, save_prefix))[0]
    timings["summary_fetch_rpc_s"] = time.time() - t0

    t0 = time.time()
    features = {name: summary[name] for name in ROUTER_FEATURE_NAMES}
    features.update(logprob_features(comp.logprobs or [],
                                     len(comp.token_ids)))
    timings["feature_derivation_s"] = time.time() - t0

    record = {
        "prompt_rows": prompt_rows,
        "output_tokens": len(comp.token_ids),
        "truncated": comp.finish_reason == "length",
        "text": comp.text,
        "features": features,
        "telemetry_rows": summary.get("rows", 0),
        "id_mismatch_total": summary.get("id_mismatch_total", 0),
        "npz_path": summary.get("npz_path"),
    }
    return record, timings


def run_profile(args) -> int:
    import numpy as np

    items = profile_prompts()
    sampler = GpuPeakSampler()
    sampler.start()
    llm = make_llm(args.model_ref)
    install(llm)
    cap_dir = PRIVATE_DIR / "m36c_profile_caps"
    cap_dir.mkdir(parents=True, exist_ok=True)

    per_task = []
    equivalence = []
    for item in items:
        prefix = str((cap_dir / item["prompt_id"]).resolve())
        record, timings = timed_generation(
            llm, item["prompt"], PROBE_BUDGET, save_prefix=prefix)

        # Raw-path costs measured explicitly for the profile.
        t0 = time.time()
        cap = load_capture({"npz_path": record["npz_path"]})
        cap["rows"] = record["telemetry_rows"]
        cap["num_experts"] = 256
        timings["npz_read_s"] = time.time() - t0
        t0 = time.time()
        raw = router_features(cap, record["prompt_rows"])
        timings["raw_feature_derivation_s"] = time.time() - t0

        t0 = time.time()
        verdict = task_verdict(item, record["text"]) \
            if "known_answer" in item else "unchecked"
        timings["verifier_s"] = time.time() - t0

        t0 = time.time()
        with (PRIVATE_DIR / "m36c_profile_rows.jsonl").open("a") as sink:
            sink.write(json.dumps({
                "prompt_id": item["prompt_id"], "kind": item["kind"],
                "verdict": verdict, **{k: v for k, v in record.items()
                                       if k != "text"}}) + "\n")
            sink.flush()
        timings["append_fsync_s"] = time.time() - t0

        diffs = {name: abs(record["features"][name] - raw[name])
                 for name in ROUTER_FEATURE_NAMES}
        equivalence.append(max(diffs.values()))
        timings["non_generation_s"] = sum(
            v for k, v in timings.items()
            if k.endswith("_s") and k != "generation_s")
        timings["kind"] = item["kind"]
        timings["truncated"] = record["truncated"]
        per_task.append(timings)

    sampler.stop_flag = True

    def agg(key):
        values = sorted(t[key] for t in per_task)
        return {"median": round(statistics.median(values), 3),
                "p95": round(values[int(0.95 * (len(values) - 1))], 3)}

    overhead_ratios = sorted(t["non_generation_s"] / t["generation_s"]
                             for t in per_task)
    overhead_median = statistics.median(overhead_ratios)
    payload = {
        "schema_version": 1,
        "run_kind": "m36c_phase0_profile",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": EXPECTED_REVISION,
        "override_hash": override_hash(),
        "profile_set": {"prompts": len(items), "decode_cap": PROBE_BUDGET,
                        "kinds": ["short", "medium", "truncation_prone"]},
        "component_seconds": {
            key: agg(key) for key in
            ("generation_s", "reset_rpc_s", "summary_fetch_rpc_s",
             "feature_derivation_s", "npz_read_s",
             "raw_feature_derivation_s", "verifier_s", "append_fsync_s",
             "non_generation_s")},
        "overhead_ratio_median": round(overhead_median, 4),
        "overhead_ratio_p95": round(overhead_ratios[-1], 4),
        "overhead_target": OVERHEAD_TARGET,
        "equivalence": {
            "prompts_checked": len(equivalence),
            "per_feature_tolerance": EQUIVALENCE_TOL,
            "max_abs_diff": float(np.max(equivalence)),
            "passed": bool(np.max(equivalence) <= EQUIVALENCE_TOL
                           and len(equivalence) >= 8),
        },
        "gates": {},
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate medians/p95 only",
    }
    payload["gates"] = {
        "summary_equivalence": payload["equivalence"]["passed"],
        "overhead_within_target": overhead_median <= OVERHEAD_TARGET,
    }
    payload["all_gates_passed"] = all(payload["gates"].values())
    assert_aggregate_only(payload)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36C profile: overhead_median="
          f"{payload['overhead_ratio_median']} "
          f"equiv_maxdiff={payload['equivalence']['max_abs_diff']:.2e} "
          f"gates={payload['gates']}", flush=True)
    return 0 if payload["all_gates_passed"] else 1


# ---------------------------------------------------------- adaptive stage

def load_original_rows():
    rows = []
    for line in ORIGINAL_ROWS_PATH.read_text().splitlines():
        row = json.loads(line)
        row["budget"] = 1024
        row["classification"] = classify(
            row.get("verdict", "pass" if row["original_pass"] else "fail"),
            row["truncated"])
        rows.append(row)
    return rows


def load_new_rows():
    if not ROWS_PATH.exists():
        return []
    return [json.loads(line) for line in ROWS_PATH.read_text().splitlines()]


def retained_rows(original, new):
    """Unique task_ids, preferring a completed capture at the lowest budget
    that completed. Capped reruns of the same prompt never add rows."""
    by_task = {}
    for row in original + new:
        existing = by_task.get(row["task_id"])
        if existing is None:
            by_task[row["task_id"]] = row
            continue
        old_done = existing["classification"] != "truncated_budget"
        new_done = row["classification"] != "truncated_budget"
        if (new_done and not old_done) or (
                new_done and old_done
                and row["budget"] < existing["budget"]):
            by_task[row["task_id"]] = row
    return list(by_task.values())


def quota_state(rows):
    """Retention counts completed calibration rows; truncated rows are a
    separate budget-policy dataset per the steer and are tracked apart."""
    completed_correct = sum(
        1 for r in rows if r["classification"] == "completed_correct")
    completed_incorrect = sum(
        1 for r in rows if r["classification"] == "completed_incorrect")
    failure_families = len({r["family"] for r in rows
                            if r["classification"] == "completed_incorrect"})
    truncated = sum(1 for r in rows
                    if r["classification"] == "truncated_budget")
    return {"completed_correct": completed_correct,
            "completed_incorrect": completed_incorrect,
            "failure_families": failure_families,
            "retained_total": completed_correct + completed_incorrect,
            "truncated_budget_rows": truncated}


def cell_stats(rows):
    cells = {}
    for row in rows:
        cell = cells.setdefault((row["family"], row["stratum"]), [])
        cell.append(row)
    out = {}
    for key, cell_rows in cells.items():
        completed = [r for r in cell_rows
                     if r["classification"] != "truncated_budget"]
        done_pass = sum(1 for r in completed
                        if r["classification"] == "completed_correct")
        out[key] = {
            "rows": len(cell_rows),
            "completed": len(completed),
            "completed_pass_rate": (done_pass / len(completed)
                                    if completed else None),
            "truncation_rate": 1 - len(completed) / len(cell_rows),
        }
    return out


def cell_regime(stats) -> str:
    rate = stats["completed_pass_rate"]
    trunc = stats["truncation_rate"]
    if trunc > BUDGET_BOUND_TRUNC:
        return "budget_bound"
    if rate is None:
        return "unknown"
    if MIXED_LOW <= rate <= MIXED_HIGH and trunc <= TRUNC_OK:
        return "mixed_frontier"
    if trunc <= TRUNC_OK:
        return "anchor_high" if rate > MIXED_HIGH else "anchor_low"
    return "between"


def run_adaptive(args) -> int:
    tasks = {t["task_id"]: t for t in
             (json.loads(line)
              for line in ORIGINAL_TASKS_PATH.read_text().splitlines())}
    tasks_by_cell = {}
    for task in tasks.values():
        tasks_by_cell.setdefault(
            (task["family"], task["stratum"]), []).append(task)
    for cell in tasks_by_cell.values():
        cell.sort(key=lambda t: t["task_id"])

    original = load_original_rows()
    new_rows = load_new_rows()
    captured_ids = ({r["task_id"] for r in original}
                    | {(r["task_id"], r["budget"]) for r in new_rows})

    sampler = GpuPeakSampler()
    sampler.start()
    llm = make_llm(args.model_ref)
    install(llm)
    cap_dir = PRIVATE_DIR / "m36c_caps"
    cap_dir.mkdir(parents=True, exist_ok=True)
    sink = ROWS_PATH.open("a", encoding="utf-8")
    capture_count = 0

    def capture(task, budget, rescue=False):
        nonlocal capture_count
        capture_count += 1
        prefix = (str((cap_dir / f"{task['task_id']}_b{budget}").resolve())
                  if capture_count % VALIDATION_SAMPLE_EVERY == 0 else None)
        record, timings = timed_generation(llm, task["prompt"], budget,
                                           save_prefix=prefix)
        verdict = task_verdict(task, record["text"])
        row = {
            "task_id": task["task_id"], "family": task["family"],
            "stratum": task["stratum"], "budget": budget,
            "rescue": rescue,
            "verdict": verdict,
            "original_pass": verdict == "pass",
            "truncated": record["truncated"],
            "classification": classify(verdict, record["truncated"]),
            "output_tokens": record["output_tokens"],
            "generation_s": round(timings["generation_s"], 2),
            "non_generation_s": round(
                sum(v for k, v in timings.items()
                    if k.endswith("_s") and k != "generation_s"), 3),
            "features": record["features"],
            "output_text": record["text"],
        }
        sink.write(json.dumps(row) + "\n")
        sink.flush()
        new_rows.append(row)
        captured_ids.add((task["task_id"], budget))
        return row

    # ---- Phase 1: four-row probes at staged budgets --------------------
    original_cells = {(r["family"], r["stratum"]) for r in original}
    probe_cells = [key for key in sorted(tasks_by_cell)
                   if key[0] != "mul_multi"]
    for key in probe_cells:
        cell_tasks = tasks_by_cell[key][:4]
        have = {r["task_id"] for r in original + new_rows
                if (r["family"], r["stratum"]) == key}
        probe_rows = []
        for task in cell_tasks:
            if task["task_id"] in have:
                continue
            if (task["task_id"], PROBE_BUDGET) in captured_ids:
                continue
            probe_rows.append(capture(task, PROBE_BUDGET))
        # Staged rescues for truncated probes (predetermined order).
        cell_rows = [r for r in new_rows + original
                     if (r["family"], r["stratum"]) == key]
        truncated = [r for r in cell_rows
                     if r["classification"] == "truncated_budget"
                     and not r.get("rescue")]
        truncated.sort(key=lambda r: r["task_id"])
        for budget, max_count in zip(RESCUE_BUDGETS, RESCUE_COUNTS):
            still = [r for r in truncated
                     if not any(n["task_id"] == r["task_id"]
                                and n["budget"] >= budget
                                for n in new_rows)]
            rescued = 0
            for row in still:
                if rescued >= max_count:
                    break
                if row["budget"] >= budget:
                    continue
                result = capture(tasks[row["task_id"]], budget, rescue=True)
                rescued += 1
                if result["classification"] != "truncated_budget":
                    truncated = [r for r in truncated
                                 if r["task_id"] != row["task_id"]]
        print(f"[jlens] M36C probe {key[0]}:{key[1]} done", flush=True)

    # ---- frontier map ----------------------------------------------------
    retained = retained_rows(original, new_rows)
    stats = cell_stats(retained)
    frontier = {}
    for (family, stratum), s in sorted(stats.items()):
        cell_retained = [r for r in retained
                         if (r["family"], r["stratum"]) == (family, stratum)]
        lengths = sorted(r["output_tokens"] for r in cell_retained)
        gens = sorted(r.get("generation_s", 0) for r in cell_retained
                      if r.get("generation_s"))
        frontier.setdefault(family, {})[stratum] = {
            "rows": s["rows"], "completed": s["completed"],
            "completed_pass_rate": (round(s["completed_pass_rate"], 3)
                                    if s["completed_pass_rate"] is not None
                                    else None),
            "truncation_rate": round(s["truncation_rate"], 3),
            "regime": cell_regime(s),
            "output_tokens_median": lengths[len(lengths) // 2],
            "output_tokens_p95": lengths[int(0.95 * (len(lengths) - 1))],
            "generation_s_median": (gens[len(gens) // 2] if gens else None),
        }

    # ---- Phase 2: selective expansion under the frozen rule -------------
    # Selection among rule-eligible cells is quota-deficit driven: when
    # the completed-incorrect quota is unmet, expand the eligible cell
    # with the highest expected failure yield (1 - completed pass rate);
    # when only the correct quota is unmet, highest pass yield. Anchors
    # and between-cells expand only while a quota deficit remains (the
    # frozen rule marks their expansion as optional).
    def eligible_for_expansion(state):
        current = cell_stats(retained_rows(original, new_rows))
        need_incorrect = (QUOTAS["completed_incorrect"]
                          - state["completed_incorrect"])
        order = []
        for key, s in current.items():
            regime_now = cell_regime(s)
            target = (MIXED_TARGET_ROWS if regime_now == "mixed_frontier"
                      else ANCHOR_TARGET_ROWS
                      if regime_now in ("anchor_high", "anchor_low",
                                        "between")
                      else 0)
            if s["rows"] >= target:
                continue
            rate = s["completed_pass_rate"]
            if rate is None:
                continue
            yield_score = (1.0 - rate) if need_incorrect > 0 else rate
            order.append((-yield_score, key))
        order.sort()
        return [key for _, key in order]

    while True:
        retained = retained_rows(original, new_rows)
        state = quota_state(retained)
        mixed_cells = sum(1 for s in cell_stats(retained).values()
                          if cell_regime(s) == "mixed_frontier")
        quotas_met = (
            state["completed_correct"] >= QUOTAS["completed_correct"]
            and state["completed_incorrect"] >= QUOTAS["completed_incorrect"]
            and state["failure_families"] >= QUOTAS["failure_families"]
            and mixed_cells >= QUOTAS["mixed_cells"])
        if quotas_met:
            outcome = "quotas_met"
            break
        if state["retained_total"] >= RETENTION_CAP:
            outcome = "completed_failure_frontier_not_found"
            break
        next_task, chosen_key = None, None
        for key in eligible_for_expansion(state):
            have = {r["task_id"] for r in retained
                    if (r["family"], r["stratum"]) == key}
            candidate = next((t for t in tasks_by_cell[key]
                              if t["task_id"] not in have), None)
            if candidate is not None:
                next_task, chosen_key = candidate, key
                break
        if next_task is None:
            outcome = "completed_failure_frontier_not_found"
            break
        # Chosen cap: smallest tested budget with cell truncation <= 0.25.
        cell_current = cell_stats(retained)[chosen_key]
        budget = (PROBE_BUDGET
                  if cell_current["truncation_rate"] <= TRUNC_OK
                  else RESCUE_BUDGETS[0])
        capture(next_task, budget)

    sink.close()
    sampler.stop_flag = True
    retained = retained_rows(original, new_rows)
    state = quota_state(retained)
    mixed_cells = sum(1 for s in cell_stats(retained).values()
                      if cell_regime(s) == "mixed_frontier")

    # D/R split: deterministic within cell over completed retained rows.
    d_count = r_count = 0
    for key in sorted({(r["family"], r["stratum"]) for r in retained}):
        completed = sorted(
            (r for r in retained
             if (r["family"], r["stratum"]) == key
             and r["classification"] != "truncated_budget"),
            key=lambda r: r["task_id"])
        for index, row in enumerate(completed):
            row["split"] = "D" if index % 3 < 2 else "R"
            d_count += int(row["split"] == "D")
            r_count += int(row["split"] == "R")
    (PRIVATE_DIR / "m36c_retained_rows.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in retained))

    payload = {
        "schema_version": 1,
        "run_kind": "m36c_calibration_result",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": EXPECTED_REVISION,
        "override_hash": override_hash(),
        "amendment_steer": "9faf213",
        "outcome": outcome,
        "quotas": QUOTAS,
        "quota_state": {**state, "mixed_cells": mixed_cells},
        "new_captures": capture_count,
        "budgets": {"probe": PROBE_BUDGET, "rescues": list(RESCUE_BUDGETS),
                    "rescue_counts": list(RESCUE_COUNTS)},
        "retention_semantics": "192-row cap counts completed calibration "
                               "rows; truncated_budget rows are a separate "
                               "budget-policy dataset and capped reruns of "
                               "the same prompt are excluded entirely",
        "expansion_rule": {
            "mixed": f"pass {MIXED_LOW}-{MIXED_HIGH}, trunc <= {TRUNC_OK} "
                     f"-> {MIXED_TARGET_ROWS} rows",
            "anchor": f"pass > {MIXED_HIGH} or < {MIXED_LOW}, trunc <= "
                      f"{TRUNC_OK} -> {ANCHOR_TARGET_ROWS} rows",
            "budget_bound": f"trunc > {BUDGET_BOUND_TRUNC} at 1024 -> no "
                            "expansion",
            "retention_cap": RETENTION_CAP,
        },
        "d_rows": d_count, "r_rows": r_count,
        "frontier_map": frontier,
        "truncated_rows_kept_separate": True,
        "calibration_rows_are_benchmark_data": False,
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate cell stats only; rows private",
    }
    assert_aggregate_only(payload)
    Path(args.frontier_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.frontier_out).write_text(json.dumps(
        {"schema_version": 1, "run_kind": "m36c_frontier_map",
         "frontier_map": frontier,
         "privacy_check_status": "aggregate cell stats only"},
        indent=1) + "\n")
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36C adaptive: outcome={outcome} "
          f"quota_state={payload['quota_state']} "
          f"new_captures={capture_count}", flush=True)
    return 0 if outcome == "quotas_met" else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", required=True, choices=("profile", "adaptive"))
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--out")
    ap.add_argument("--frontier-out", default=FRONTIER_OUT)
    args = ap.parse_args(argv)
    if args.out is None:
        args.out = PROFILE_OUT if args.stage == "profile" else RESULT_OUT

    import os
    src = str(ROOT)
    existing = os.environ.get("PYTHONPATH", "")
    if src not in existing.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + (os.pathsep + existing if existing else ""))

    return (run_profile if args.stage == "profile" else run_adaptive)(args)


if __name__ == "__main__":
    raise SystemExit(main())
