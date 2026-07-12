#!/usr/bin/env python3
"""M36 calibration sweep: Agents-A1-AWQ capability mapping (steer 0be9d84).

Private capability sweep on the exact pinned AWQ checkpoint over fresh
deterministic, tool-checkable families. Calibration rows are never
benchmark decision data. The sweep must locate Agents-A1's own
high-competence cells, mixed cells, near-total-failure anchors, and
output-length requirements.

Stages:
  --stage generate   build the seeded task set (fresh; multiplication
                     tuples disjoint from every M29-M35 draw)
  --stage capture    one engine load; per task: greedy generation with
                     router telemetry + logprobs, verdict, feature row
                     (private JSONL); resumable (skips captured task_ids)
  --stage summarize  aggregate-only public cell-competence report

Feature schema is derived fresh from AWQ telemetry (same estimator for
calibration and benchmark); no proxy threshold, centroid, prior, or
score scale is imported.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verifiers as VZ                        # noqa: E402
from m36v_phase0 import EXPECTED_REVISION, GpuPeakSampler   # noqa: E402
from m36v_phase1 import PRIVATE_DIR, load_capture, override_hash  # noqa: E402
from m36v_phase2 import extract_json          # noqa: E402
from jlens_vllm_telemetry.report_guard import assert_aggregate_only  # noqa: E402

CALIBRATION_SEED = "m36-calibration-v1"
TASKS_PATH = PRIVATE_DIR / "m36_calibration_tasks.jsonl"
ROWS_PATH = PRIVATE_DIR / "m36_calibration_rows.jsonl"
SUMMARY_OUT = "reports/telemetry/m36_calibration_summary.json"
MAX_TOKENS = 1024
MAX_MODEL_LEN = 2048
TASKS_PER_CELL = 16

HIGH_ENTROPY_THRESHOLD = 1.0    # nats over top-5 truncated distribution
LOW_CONFIDENCE_THRESHOLD = 0.5  # selected-token probability

FAMILIES = [
    {"family_id": "mul_multi",
     "prompt": "What is {a} * {b}? Reply with the final number only.",
     "answer": lambda a, b: a * b, "expression": "{a}*{b}",
     "strata": [((100, 999), (10, 99)), ((1000, 9999), (100, 999)),
                ((10000, 99999), (1000, 9999)),
                ((100000, 999999), (10000, 99999))]},
    {"family_id": "add_chain",
     "prompt": "What is the sum: {chain}? Reply with the final number only.",
     "answer": None,   # built by generator
     "strata": [(3, (100, 999)), (5, (1000, 9999)),
                (8, (10000, 99999)), (12, (100000, 999999))]},
    {"family_id": "mod_arith",
     "prompt": "What is ({a} * {b}) mod {m}? Reply with the final number "
               "only.",
     "answer": lambda a, b, m: (a * b) % m, "expression": None,
     "strata": [((10, 99), (10, 99), (2, 9)),
                ((100, 999), (100, 999), (10, 99)),
                ((1000, 9999), (1000, 9999), (100, 999)),
                ((10000, 99999), (10000, 99999), (1000, 9999))]},
    {"family_id": "sub_mixed",
     "prompt": "Compute {a} - {b} + {c} - {d}. Reply with the final number "
               "only.",
     "answer": lambda a, b, c, d: a - b + c - d,
     "expression": "{a}-{b}+{c}-{d}",
     "strata": [((100, 999),), ((1000, 9999),), ((10000, 99999),),
                ((100000, 999999),)]},
    {"family_id": "div_exact",
     "prompt": "What is {n} / {d}? The division is exact. Reply with the "
               "final number only.",
     "answer": lambda q, d: q, "expression": None,
     "strata": [((10, 99), (2, 9)), ((100, 999), (10, 99)),
                ((1000, 9999), (100, 999)), ((10000, 99999), (1000, 9999))]},
    {"family_id": "json_digits",
     "prompt": "Return a JSON array of the digits of {n} in reverse order, "
               "as integers. No other text.",
     "answer": None,
     "strata": [((100, 999),), ((10000, 99999),), ((1000000, 9999999),),
                ((100000000, 999999999),)]},
]


def prior_tuples() -> set:
    """Multiplication operand tuples drawn by M29-M34 (disjointness)."""
    try:
        import m35_campaign as M35
        return set(M35.prior_multiplication_tuples(
            "data/prompts/m29_scaled_error_manifest.json",
            "data/prompts/m30_decisive_manifest.json",
            "data/prompts/m32p_proxy_routing_manifest.json",
            "data/prompts/m33_routing_manifest.json",
            "data/prompts/m34_transfer_manifest.json"))
    except Exception:
        return set()


def m35_task_tuples() -> set:
    path = PRIVATE_DIR / "m35_campaign_tasks_local.jsonl"
    tuples = set()
    if path.exists():
        for line in path.read_text().splitlines():
            rec = json.loads(line)
            if "a" in rec and "b" in rec:
                tuples.add((rec["a"], rec["b"]))
    return tuples


def generate_tasks():
    seen = prior_tuples() | m35_task_tuples()
    tasks = []
    for family in FAMILIES:
        fid = family["family_id"]
        for s_index, stratum in enumerate(family["strata"], start=1):
            rng = random.Random(f"{CALIBRATION_SEED}:{fid}:s{s_index}")
            for index in range(TASKS_PER_CELL):
                task = {"task_id": f"m36c_{fid}_s{s_index}_{index:03d}",
                        "family": fid, "stratum": f"s{s_index}"}
                if fid == "mul_multi":
                    (alo, ahi), (blo, bhi) = stratum
                    while True:
                        a, b = rng.randint(alo, ahi), rng.randint(blo, bhi)
                        if (a, b) not in seen:
                            seen.add((a, b))
                            break
                    task.update(a=a, b=b, expression=f"{a}*{b}",
                                known_answer=str(a * b),
                                prompt=family["prompt"].format(a=a, b=b))
                elif fid == "add_chain":
                    k, (lo, hi) = stratum
                    terms = [rng.randint(lo, hi) for _ in range(k)]
                    chain = " + ".join(str(t) for t in terms)
                    task.update(expression="+".join(str(t) for t in terms),
                                known_answer=str(sum(terms)),
                                prompt=family["prompt"].format(chain=chain))
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
                                prompt=family["prompt"].format(
                                    a=a, b=b, c=c, d=d))
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
    return tasks


def task_verdict(task, text: str) -> str:
    if "json_expected" in task:
        value = extract_json(text)
        return "pass" if value == task["json_expected"] else "fail"
    v = VZ.math_checker(text, known_answer=task["known_answer"],
                        expression=task.get("expression"))["verdict"]
    return v or "undecided"


# -- feature derivation (fresh AWQ schema; same estimator everywhere) -----

def logprob_step_stats(step_logprobs) -> tuple[float, float, float]:
    """(selected_prob, top1_top2_margin, truncated_entropy) per step."""
    entries = sorted((lp.logprob for lp in step_logprobs.values()),
                     reverse=True)
    probs = [math.exp(x) for x in entries]
    selected = None
    for lp in step_logprobs.values():
        if getattr(lp, "rank", None) == 1:
            selected = math.exp(lp.logprob)
            break
    if selected is None:
        selected = probs[0]
    margin = (entries[0] - entries[1]) if len(entries) > 1 else entries[0]
    total = sum(probs)
    norm = [p / total for p in probs]
    entropy = -sum(p * math.log(max(p, 1e-12)) for p in norm)
    return selected, margin, entropy


ROUTER_FEATURE_NAMES = [
    "router_entropy_mean", "expert_concentration_mean",
    "windowed_expert_shift", "drift_final_window",
]


def router_features(cap: dict, prompt_rows: int) -> dict:
    """Router-side features recomputed from a raw capture (numpy path).

    The device-side mirror is RouterTelemetryCollector.summarize; the
    M36C equivalence gate holds them within 1e-5 per feature.
    """
    import numpy as np

    rows = cap["rows"]
    prompt_rows = min(prompt_rows, rows)
    entropy = cap["entropy"][prompt_rows:rows]
    mass = cap["mass"][prompt_rows:rows]
    num_experts = cap["num_experts"]

    def usage(rows_ids, rows_w):
        L = rows_ids.shape[1]
        out = np.zeros((L, num_experts))
        for layer in range(L):
            np.add.at(out[layer], rows_ids[:, layer, :].reshape(-1),
                      rows_w[:, layer, :].reshape(-1))
            s = out[layer].sum()
            if s:
                out[layer] /= s
        return out.reshape(-1)

    prefill_sig = usage(cap["ids"][:prompt_rows], cap["weights"][:prompt_rows])
    drift = []
    step = max(1, (rows - prompt_rows) // 8)
    for start in range(prompt_rows, rows, step):
        window_sig = usage(cap["ids"][start:start + step],
                           cap["weights"][start:start + step])
        na, nb = np.linalg.norm(window_sig), np.linalg.norm(prefill_sig)
        drift.append(0.0 if na == 0 or nb == 0 else
                     float(1.0 - window_sig @ prefill_sig / (na * nb)))

    return {
        "router_entropy_mean": float(entropy.mean()) if entropy.size else 0.0,
        "expert_concentration_mean": float(mass.mean()) if mass.size else 0.0,
        "windowed_expert_shift": (float(sum(drift) / len(drift))
                                  if drift else 0.0),
        "drift_final_window": drift[-1] if drift else 0.0,
    }


def logprob_features(logprob_steps, n_output_tokens: int) -> dict:
    stats = [logprob_step_stats(s) for s in (logprob_steps or []) if s]
    selected = [s[0] for s in stats]
    margins = [s[1] for s in stats]
    entropies = [s[2] for s in stats]

    def mean(xs):
        return float(sum(xs) / len(xs)) if xs else 0.0

    return {
        "decode_window_entropy": mean(entropies),
        "final_selected_probability": selected[-1] if selected else 0.0,
        "final_top_k_margin": margins[-1] if margins else 0.0,
        "mean_selected_probability": mean(selected),
        "high_entropy_count": float(sum(e >= HIGH_ENTROPY_THRESHOLD
                                        for e in entropies)),
        "low_confidence_count": float(sum(p <= LOW_CONFIDENCE_THRESHOLD
                                          for p in selected)),
        "top_k_margin_trend": (margins[-1] - margins[0]) if len(margins) > 1
        else 0.0,
        "decode_step_count": float(n_output_tokens),
    }


def derive_features(cap: dict, prompt_rows: int, logprob_steps,
                    n_output_tokens: int) -> dict:
    return {**router_features(cap, prompt_rows),
            **logprob_features(logprob_steps, n_output_tokens)}


FEATURE_NAMES = [
    "router_entropy_mean", "expert_concentration_mean",
    "windowed_expert_shift", "drift_final_window", "decode_window_entropy",
    "final_selected_probability", "final_top_k_margin",
    "mean_selected_probability", "high_entropy_count",
    "low_confidence_count", "top_k_margin_trend", "decode_step_count",
]


def run_generate(args) -> int:
    tasks = generate_tasks()
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    TASKS_PATH.write_text("".join(json.dumps(t) + "\n" for t in tasks))
    families = sorted({t["family"] for t in tasks})
    print(f"[jlens] M36 calibration: {len(tasks)} tasks, "
          f"{len(families)} families x 4 strata x {TASKS_PER_CELL}",
          flush=True)
    return 0


def run_capture(args) -> int:
    from vllm import LLM, SamplingParams

    tasks = [json.loads(line)
             for line in TASKS_PATH.read_text().splitlines()]
    done_ids = set()
    if ROWS_PATH.exists():
        done_ids = {json.loads(line)["task_id"]
                    for line in ROWS_PATH.read_text().splitlines()}
    todo = [t for t in tasks if t["task_id"] not in done_ids]
    print(f"[jlens] M36 capture: {len(done_ids)} done, {len(todo)} to go",
          flush=True)
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
         "raw_sample_tokens": 4},))
    llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))
    params = SamplingParams(temperature=0.0, max_tokens=MAX_TOKENS,
                            logprobs=5)

    cap_prefix = PRIVATE_DIR / "m36_calibration_caps"
    cap_prefix.mkdir(parents=True, exist_ok=True)
    started = time.time()
    with ROWS_PATH.open("a", encoding="utf-8") as sink:
        for count, task in enumerate(todo, start=1):
            llm.collective_rpc("jlens_reset_telemetry")
            out = llm.chat(
                [[{"role": "user", "content": task["prompt"]}]], params,
                use_tqdm=False)[0]
            comp = out.outputs[0]
            prefix = str((cap_prefix / task["task_id"]).resolve())
            fetches = llm.collective_rpc("jlens_fetch_telemetry",
                                         args=(prefix,))
            cap = load_capture(fetches[0])
            features = derive_features(
                cap, prompt_rows=len(out.prompt_token_ids),
                logprob_steps=comp.logprobs or [],
                n_output_tokens=len(comp.token_ids))
            verdict = task_verdict(task, comp.text)
            row = {
                "task_id": task["task_id"], "family": task["family"],
                "stratum": task["stratum"],
                "original_pass": verdict == "pass",
                "verdict": verdict,
                "truncated": comp.finish_reason == "length",
                "output_tokens": len(comp.token_ids),
                "features": features,
                "output_text": comp.text,
            }
            sink.write(json.dumps(row) + "\n")
            sink.flush()
            if count % 16 == 0:
                rate = count / (time.time() - started)
                print(f"[jlens] M36 capture {count}/{len(todo)} "
                      f"({rate * 3600:.0f}/h)", flush=True)
    sampler.stop_flag = True
    print(f"[jlens] M36 capture complete: {len(todo)} new rows, peak="
          f"{round(sum(sampler.peaks.values()) / 1024, 2)}GiB", flush=True)
    return 0


def regime(pass_rate: float) -> str:
    if pass_rate >= 0.9:
        return "high"
    if pass_rate <= 0.1:
        return "near_total_failure"
    return "mixed"


def run_summarize(args) -> int:
    rows = [json.loads(line)
            for line in ROWS_PATH.read_text().splitlines()]
    cells = {}
    for row in rows:
        key = (row["family"], row["stratum"])
        cell = cells.setdefault(key, {"n": 0, "pass": 0, "truncated": 0,
                                      "tokens": []})
        cell["n"] += 1
        cell["pass"] += int(row["original_pass"])
        cell["truncated"] += int(row["truncated"])
        cell["tokens"].append(row["output_tokens"])

    by_family = {}
    for (family, stratum), cell in sorted(cells.items()):
        rate = cell["pass"] / cell["n"]
        by_family.setdefault(family, {})[stratum] = {
            "n": cell["n"],
            "pass_rate": round(rate, 3),
            "regime": regime(rate),
            "truncation_rate": round(cell["truncated"] / cell["n"], 3),
            "output_tokens_mean": round(
                sum(cell["tokens"]) / len(cell["tokens"]), 1),
            "output_tokens_p95": sorted(cell["tokens"])[
                int(0.95 * (len(cell["tokens"]) - 1))],
        }

    regimes = [s["regime"] for f in by_family.values() for s in f.values()]
    payload = {
        "schema_version": 1,
        "run_kind": "m36_calibration_summary",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": EXPECTED_REVISION,
        "runtime": {"max_tokens": MAX_TOKENS,
                    "max_model_len": MAX_MODEL_LEN,
                    "override_hash": override_hash(),
                    "seed": CALIBRATION_SEED,
                    "tasks_per_cell": TASKS_PER_CELL},
        "cells_total": len(cells),
        "rows_total": len(rows),
        "regime_counts": {r: regimes.count(r)
                          for r in ("high", "mixed", "near_total_failure")},
        "competence_by_family": by_family,
        "calibration_rows_are_benchmark_data": False,
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate cell stats only; rows private",
    }
    assert_aggregate_only(payload)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36 calibration summary: {len(rows)} rows, "
          f"regimes={payload['regime_counts']}", flush=True)
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--stage", required=True,
                    choices=("generate", "capture", "summarize"))
    ap.add_argument("--model-ref")
    ap.add_argument("--out", default=SUMMARY_OUT)
    args = ap.parse_args(argv)

    import os
    src = str(ROOT)
    existing = os.environ.get("PYTHONPATH", "")
    if src not in existing.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + (os.pathsep + existing if existing else ""))

    if args.stage == "capture" and not args.model_ref:
        ap.error("--model-ref required for capture")
    return {"generate": run_generate, "capture": run_capture,
            "summarize": run_summarize}[args.stage](args)


if __name__ == "__main__":
    raise SystemExit(main())
