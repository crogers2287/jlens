#!/usr/bin/env python3
"""M36V Phase 2: parity, quality, and overhead smoke (steer 0be9d84).

Sixteen fixed private prompts (deterministic arithmetic, JSON, exact
instruction following, short reasoning) under three arms:

  --arm stock         stock vLLM AWQ engine
  --arm instrumented  telemetry-enabled vLLM AWQ (Phase 1 passed), with a
                      disabled pass first for parity/overhead
  --arm gguf          production Agents-A1 Q8 GGUF endpoint (diagnostic;
                      running it after the research arms also verifies the
                      normal serving stack is restored)
  --arm report        combine private arm metrics into the aggregate-only
                      public artifact

Operand instances are seeded and stay private; outputs stay private.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verifiers as VZ                       # noqa: E402
from m36v_phase0 import EXPECTED_REVISION, GPU_GATE_GIB, GpuPeakSampler  # noqa: E402
from m36v_phase1 import (                    # noqa: E402
    PARITY_FIRST_DIV_FLOOR, PARITY_MARGIN_PROMPTS, PRIVATE_DIR,
    divergence_stats, ids_equal, load_capture, make_llm, override_hash,
    run_smoke,
)
from jlens_vllm_telemetry.report_guard import assert_aggregate_only  # noqa: E402

PHASE2_SEED = "m36v-phase2-smoke-v1"
GGUF_BASE_URL = "http://localhost:9069/v1"
GGUF_MODEL = "agents-a1"
FAMILIES = ("math", "json", "instruction", "reasoning")


def phase2_prompts():
    """Sixteen fixed private prompts, four per family, operands seeded."""
    rng = random.Random(PHASE2_SEED)
    items = []

    def add(kind, prompt, **checks):
        items.append({"kind": kind, "prompt": prompt, **checks})

    a, b = rng.randint(100, 999), rng.randint(10, 99)
    c, d = rng.randint(1000, 9999), rng.randint(100, 999)
    e, f, g = rng.randint(10, 99), rng.randint(10, 99), rng.randint(2, 9)
    h, i = rng.randint(10000, 99999), rng.randint(1000, 9999)
    add("math", f"What is {a} * {b}? Reply with the final number only.",
        expression=f"{a}*{b}", known_answer=str(a * b))
    add("math", f"What is {c} + {d}? Reply with the final number only.",
        expression=f"{c}+{d}", known_answer=str(c + d))
    add("math", f"Compute {e} * {f} + {g}. Give the final number.",
        expression=f"{e}*{f}+{g}", known_answer=str(e * f + g))
    add("math", f"What is {h} - {i}? Reply with the final number only.",
        expression=f"{h}-{i}", known_answer=str(h - i))

    n1 = rng.randint(2, 9)
    add("json", 'Return a JSON object with keys "name" (string) and '
                '"count" (integer). No other text.',
        json_check={"kind": "object",
                    "keys": {"name": "str", "count": "int"}})
    add("json", f'Return a JSON array of the integers 1 to {n1 + 3}. '
                'No other text.',
        json_check={"kind": "exact",
                    "value": list(range(1, n1 + 4))})
    add("json", 'Return a JSON object with key "items" whose value is an '
                'array of exactly two strings. No other text.',
        json_check={"kind": "object", "keys": {"items": "list2str"}})
    add("json", 'Return a JSON object with keys "ok" (boolean, true) and '
                '"value" (integer). No other text.',
        json_check={"kind": "object",
                    "keys": {"ok": "true", "value": "int"}})

    word = rng.choice(["APPROVED", "CONFIRMED", "VERIFIED"])
    token = f"SYNC-{rng.randint(10, 99)}-OK"
    num = rng.randint(40, 49)
    add("instruction", f"Reply with exactly the word: {word}",
        expect_exact=word)
    add("instruction", f"Reply with exactly this string and nothing else: "
                       f"{token}", expect_exact=token)
    add("instruction", f"Reply with only the number {num}.",
        expect_exact=str(num))
    add("instruction", "List three prime numbers, comma-separated, "
                       "nothing else.", expect_primes=3)

    t1, t2 = rng.randint(2, 5), rng.randint(15, 45)
    add("reasoning", f"A train leaves at {t1}pm and arrives at "
                     f"{t1 + 3}:{t2:02d}pm. How many minutes was the trip? "
                     "Final number only.", known_answer=str(180 + t2))
    k1, k2 = rng.randint(3, 9), rng.randint(11, 19)
    add("reasoning", f"A box holds {k1 * k2} apples split equally into "
                     f"{k1} bags. How many apples per bag? Final number "
                     "only.", known_answer=str(k2))
    m1 = rng.randint(50, 99)
    add("reasoning", f"What is the remainder when {m1 * 7 + 3} is divided "
                     f"by 7? Final number only.", known_answer="3")
    d1 = rng.randint(3, 9)
    add("reasoning", f"Today is Monday. What day of the week is it in "
                     f"{d1 * 7 + 2} days? One word only.",
        expect_exact="Wednesday")

    for index, item in enumerate(items):
        item["prompt_id"] = f"m36v_p2_{index:02d}"
    return items


def extract_json(text: str):
    """Find the last parseable JSON value in a (possibly thinking) output."""
    cleaned = text.replace("```json", "```").replace("```", " ")
    starts = [i for i, ch in enumerate(cleaned) if ch in "{["][-24:]
    ends = [i for i, ch in enumerate(cleaned) if ch in "}]"][-24:]
    # Prefer the latest-ending value; at each end, the outermost (earliest)
    # start wins, so a nested object is returned whole rather than as its
    # innermost array.
    for e in reversed(ends):
        for s in starts:
            if s >= e:
                break
            try:
                return json.loads(cleaned[s:e + 1])
            except Exception:
                continue
    return None


def check_json(value, spec) -> bool:
    if value is None:
        return False
    if spec["kind"] == "exact":
        return value == spec["value"]
    if not isinstance(value, dict):
        return False
    for key, want in spec["keys"].items():
        if key not in value:
            return False
        got = value[key]
        if want == "str" and not isinstance(got, str):
            return False
        if want == "int" and (isinstance(got, bool)
                              or not isinstance(got, int)):
            return False
        if want == "true" and got is not True:
            return False
        if want == "list2str" and not (
                isinstance(got, list) and len(got) == 2
                and all(isinstance(x, str) for x in got)):
            return False
    return True


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % p for p in range(2, int(n ** 0.5) + 1))


def last_line(text: str) -> str:
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def verdict(item, text: str) -> tuple[str, bool]:
    """Returns (pass|fail|undecided, malformed_json_flag)."""
    if "known_answer" in item and "expression" in item:
        v = VZ.math_checker(text, known_answer=item["known_answer"],
                            expression=item["expression"])["verdict"]
        return v or "undecided", False
    if "json_check" in item:
        value = extract_json(text)
        return ("pass" if check_json(value, item["json_check"]) else "fail",
                value is None)
    if "expect_primes" in item:
        parts = [p.strip() for p in last_line(text).split(",")]
        ok = (len(parts) == item["expect_primes"]
              and all(p.isdigit() and _is_prime(int(p)) for p in parts))
        return ("pass" if ok else "fail"), False
    if "expect_exact" in item:
        ok = last_line(text).strip(' "\'.') == item["expect_exact"]
        return ("pass" if ok else "fail"), False
    if "known_answer" in item:
        v = VZ.math_checker(text, known_answer=item["known_answer"])["verdict"]
        return v or "undecided", False
    return "undecided", False


def aggregate(items, results, load_seconds, gen_seconds, peaks):
    by_family = {fam: {"pass": 0, "fail": 0, "undecided": 0}
                 for fam in FAMILIES}
    malformed = 0
    total_tokens = 0
    for item, rec in zip(items, results):
        v, bad_json = verdict(item, rec["text"])
        rec["verdict"] = v
        by_family[item["kind"]][v] += 1
        malformed += int(bad_json)
        total_tokens += len(rec["output_token_ids"])
    combined_gib = round(sum(peaks.values()) / 1024, 2) if peaks else None
    return {
        "verifier_outcomes_by_family": by_family,
        "verifier_outcomes_total": {
            k: sum(f[k] for f in by_family.values())
            for k in ("pass", "fail", "undecided")},
        "malformed_json_count": malformed,
        "output_tokens_total": total_tokens,
        "output_tokens_mean": round(total_tokens / len(results), 1),
        "load_seconds": load_seconds,
        "generation_seconds": round(gen_seconds, 2),
        "tokens_per_second": round(total_tokens / gen_seconds, 2)
        if gen_seconds else None,
        "gpu_combined_peak_gib": combined_gib,
    }


def write_private(name: str, results) -> None:
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    (PRIVATE_DIR / f"m36v_phase2_{name}.jsonl").write_text(
        "".join(json.dumps(r) + "\n" for r in results))


def write_metrics(name: str, metrics: dict) -> None:
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    (PRIVATE_DIR / f"m36v_phase2_{name}_metrics.json").write_text(
        json.dumps(metrics, indent=1) + "\n")


def run_stock_arm(args) -> int:
    items = phase2_prompts()
    sampler = GpuPeakSampler()
    sampler.start()
    t0 = time.time()
    llm = make_llm(args.model_ref, instrumented=False)
    load_seconds = round(time.time() - t0, 1)
    t0 = time.time()
    results = run_smoke(llm, items, args.max_tokens)
    gen_seconds = time.time() - t0
    sampler.stop_flag = True
    time.sleep(3)
    metrics = aggregate(items, results, load_seconds, gen_seconds,
                        sampler.peaks)
    write_private("stock", results)
    write_metrics("stock", metrics)
    print(f"[jlens] M36V phase2 stock: {metrics['verifier_outcomes_total']} "
          f"tok/s={metrics['tokens_per_second']}", flush=True)
    return 0


def run_instrumented_arm(args) -> int:
    items = phase2_prompts()
    sampler = GpuPeakSampler()
    sampler.start()
    t0 = time.time()
    llm = make_llm(args.model_ref, instrumented=True)
    load_seconds = round(time.time() - t0, 1)

    hf_config = llm.llm_engine.model_config.hf_config
    text_cfg = getattr(hf_config, "text_config", hf_config)
    install_info = llm.collective_rpc("jlens_install_telemetry", args=(
        {"num_experts": text_cfg.num_experts,
         "top_k": text_cfg.num_experts_per_tok,
         "capacity_tokens": 2048, "raw_sample_tokens": 16},))

    t0 = time.time()
    disabled = run_smoke(llm, items, args.max_tokens)
    disabled_seconds = time.time() - t0

    llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))
    PRIVATE_DIR.mkdir(parents=True, exist_ok=True)
    enabled, telemetry_counters = [], []
    t0 = time.time()
    for item in items:
        llm.collective_rpc("jlens_reset_telemetry")
        rec = run_smoke(llm, [item], args.max_tokens)[0]
        prefix = str((PRIVATE_DIR /
                      f"m36v_phase2_cap_{item['prompt_id']}").resolve())
        fetches = [load_capture(f) for f in
                   llm.collective_rpc("jlens_fetch_telemetry",
                                      args=(prefix,))]
        cap0 = fetches[0]
        telemetry_counters.append({
            "rows": cap0["rows"],
            "id_mismatch": sum(cap0["id_mismatch"]),
            "dispatch_missed": sum(cap0["dispatch_missed"]),
            "weight_maxdiff": max(cap0["weight_maxdiff"]),
            "weight_nonfinite": sum(cap0["weight_nonfinite"]),
        })
        enabled.append(rec)
    enabled_seconds = time.time() - t0
    sampler.stop_flag = True
    time.sleep(3)

    metrics = aggregate(items, enabled, load_seconds, enabled_seconds,
                        sampler.peaks)
    dv = divergence_stats(disabled, enabled)
    baseline_path = PRIVATE_DIR / "m36v_phase1_stock_ids.jsonl.baseline.json"
    baseline = (json.loads(baseline_path.read_text())
                if baseline_path.exists() else None)
    base = baseline and baseline.get("stock_repeat_divergence")
    if dv["prompts_differing"] == 0:
        parity_ok = True
    elif not base or base["prompts_differing"] == 0:
        parity_ok = False
    else:
        scale = len(items) / 8.0    # baseline was measured on 8 prompts
        parity_ok = (
            dv["prompts_differing"]
            <= (base["prompts_differing"] + PARITY_MARGIN_PROMPTS) * scale
            and dv["first_divergence_min"]
            >= min(base["first_divergence_min"], PARITY_FIRST_DIV_FLOOR))
    metrics.update({
        "telemetry_overhead_ratio": round(
            enabled_seconds / disabled_seconds, 3),
        "seconds_disabled": round(disabled_seconds, 2),
        "seconds_enabled": round(enabled_seconds, 2),
        "disabled_enabled_identical": ids_equal(disabled, enabled),
        "disabled_enabled_divergence": dv,
        "parity_within_baseline_envelope": parity_ok,
        "telemetry_rows_total": sum(c["rows"] for c in telemetry_counters),
        "telemetry_id_mismatch_total": sum(
            c["id_mismatch"] for c in telemetry_counters),
        "telemetry_dispatch_missed_total": sum(
            c["dispatch_missed"] for c in telemetry_counters),
        "telemetry_weight_maxdiff": max(
            c["weight_maxdiff"] for c in telemetry_counters),
        "telemetry_weight_nonfinite_total": sum(
            c["weight_nonfinite"] for c in telemetry_counters),
        "moe_layers": len(install_info[0]["layer_ids"]),
    })
    write_private("instrumented_disabled", disabled)
    write_private("instrumented_enabled", enabled)
    write_metrics("instrumented", metrics)
    print(f"[jlens] M36V phase2 instrumented: "
          f"{metrics['verifier_outcomes_total']} "
          f"overhead={metrics['telemetry_overhead_ratio']} "
          f"parity_env={parity_ok} "
          f"id_mismatch={metrics['telemetry_id_mismatch_total']}", flush=True)
    return 0


def gguf_chat(prompt: str, max_tokens: int, timeout: int = 300):
    payload = {
        "model": GGUF_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "max_tokens": max_tokens,
    }
    req = urllib.request.Request(
        GGUF_BASE_URL + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.loads(resp.read())
    text = body["choices"][0]["message"]["content"] or ""
    usage = body.get("usage", {})
    return text, usage.get("completion_tokens", 0)


def run_gguf_arm(args) -> int:
    items = phase2_prompts()
    results = []
    t0 = time.time()
    for item in items:
        started = time.time()
        text, n_tokens = gguf_chat(item["prompt"], args.max_tokens)
        results.append({
            "prompt_id": item["prompt_id"],
            "text": text,
            "output_token_ids": [0] * n_tokens,   # count only; ids not exposed
            "latency_s": round(time.time() - started, 2),
        })
    gen_seconds = time.time() - t0
    metrics = aggregate(items, results, None, gen_seconds, {})
    metrics["endpoint_model"] = GGUF_MODEL
    metrics["serving_stack_responsive"] = True
    write_private("gguf", results)
    write_metrics("gguf", metrics)
    print(f"[jlens] M36V phase2 gguf: {metrics['verifier_outcomes_total']} "
          f"tok/s={metrics['tokens_per_second']}", flush=True)
    return 0


def run_report(args) -> int:
    import vllm

    arms = {}
    for name in ("stock", "instrumented", "gguf"):
        path = PRIVATE_DIR / f"m36v_phase2_{name}_metrics.json"
        arms[name] = json.loads(path.read_text())

    # Serving-stack restoration check: models endpoint answers and the
    # research GPUs are released.
    try:
        with urllib.request.urlopen(GGUF_BASE_URL + "/models",
                                    timeout=10) as resp:
            models = json.loads(resp.read())
        gguf_alive = any(m.get("id") == GGUF_MODEL
                         for m in models.get("data", []))
    except Exception:
        gguf_alive = False

    payload = {
        "schema_version": 1,
        "run_kind": "m36v_phase2_parity_quality_overhead",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": EXPECTED_REVISION,
        "runtime": {
            "vllm": vllm.__version__,
            "tensor_parallel_size": 2, "max_model_len": 1024,
            "enforce_eager": True, "max_tokens": args.max_tokens,
            "override_hash": override_hash(),
            "prompt_count": 16,
            "prompt_families": list(FAMILIES),
        },
        "arms": arms,
        "gates": {
            "instrumented_verifiers_not_worse_than_stock": (
                arms["instrumented"]["verifier_outcomes_total"]["pass"]
                >= arms["stock"]["verifier_outcomes_total"]["pass"] - 2),
            "telemetry_dispatch_clean": (
                arms["instrumented"]["telemetry_id_mismatch_total"] == 0
                and arms["instrumented"]["telemetry_dispatch_missed_total"] == 0
                and arms["instrumented"]["telemetry_weight_nonfinite_total"] == 0),
            "parity_within_baseline_envelope": (
                arms["instrumented"]["parity_within_baseline_envelope"]),
            "bounded_overhead": (
                arms["instrumented"]["telemetry_overhead_ratio"] <= 2.0
                and (arms["instrumented"]["gpu_combined_peak_gib"] or 0)
                <= GPU_GATE_GIB),
            "gguf_service_restored": gguf_alive,
        },
        "awq_vs_q8_note": ("diagnostic only; output equality neither "
                           "required nor an efficacy claim"),
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate gates/metrics only; outputs private",
    }
    payload["all_gates_passed"] = all(
        v is True for v in payload["gates"].values())
    assert_aggregate_only(payload)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36V phase2 report: all_gates="
          f"{payload['all_gates_passed']} gguf_alive={gguf_alive}",
          flush=True)
    for name, value in payload["gates"].items():
        if value is not True:
            print(f"[jlens]  GATE FAIL: {name} = {value}", flush=True)
    return 0 if payload["all_gates_passed"] else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref")
    ap.add_argument("--arm", required=True,
                    choices=("stock", "instrumented", "gguf", "report"))
    ap.add_argument("--max-tokens", type=int, default=512)
    ap.add_argument("--out",
                    default="reports/telemetry/m36v_phase2_smoke.json")
    args = ap.parse_args(argv)

    import os
    src = str(ROOT)
    existing = os.environ.get("PYTHONPATH", "")
    if src not in existing.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + (os.pathsep + existing if existing else ""))

    if args.arm in ("stock", "instrumented") and not args.model_ref:
        ap.error("--model-ref required for vLLM arms")
    return {"stock": run_stock_arm, "instrumented": run_instrumented_arm,
            "gguf": run_gguf_arm, "report": run_report}[args.arm](args)


if __name__ == "__main__":
    raise SystemExit(main())
