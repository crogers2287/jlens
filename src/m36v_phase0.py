#!/usr/bin/env python3
"""M36V Phase 0: unmodified vLLM compressed-runtime gate (steer 709a52c)."""
from __future__ import annotations

import argparse
import json
import random
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import verifiers as VZ  # noqa: E402

EXPECTED_REVISION = "3e522d4e46438c782789b73c8ff4503e0edd037c"
GPU_GATE_GIB = 44.0
SMOKE_SEED = "m36v-phase0-smoke-v1"


def smoke_prompts():
    """Eight fixed private prompts; operands seeded, instances stay private."""
    rng = random.Random(SMOKE_SEED)
    a, b = rng.randint(100, 999), rng.randint(10, 99)
    c, d = rng.randint(1000, 9999), rng.randint(2, 9)
    e, f = rng.randint(10, 99), rng.randint(10, 99)
    items = [
        {"kind": "math", "prompt": f"What is {a} * {b}? Reply with the final "
                                   f"number only.",
         "expression": f"{a}*{b}", "known_answer": str(a * b)},
        {"kind": "math", "prompt": f"What is {c} + {d}? Reply with the final "
                                   f"number only.",
         "expression": f"{c}+{d}", "known_answer": str(c + d)},
        {"kind": "math", "prompt": f"Compute {e} * {f} + 7. Give the final "
                                   f"number.",
         "expression": f"{e}*{f}+7", "known_answer": str(e * f + 7)},
        {"kind": "json", "prompt": 'Return a JSON object with keys "name" '
                                   '(string) and "count" (integer). No other '
                                   'text.'},
        {"kind": "json", "prompt": 'Return a JSON array of the integers 1 to '
                                   '5. No other text.'},
        {"kind": "instruction", "prompt": "Reply with exactly the word: "
                                          "APPROVED"},
        {"kind": "instruction", "prompt": "List three prime numbers, comma-"
                                          "separated, nothing else."},
        {"kind": "reasoning", "prompt": "A train leaves at 3pm and arrives at "
                                        "6:30pm. How many minutes was the "
                                        "trip? Final number only."},
    ]
    items[-1]["known_answer"] = "210"
    for index, item in enumerate(items):
        item["prompt_id"] = f"m36v_smoke_{index:02d}"
    return items


class GpuPeakSampler(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.peaks = {}
        self.stop_flag = False

    def run(self):
        while not self.stop_flag:
            try:
                out = subprocess.run(
                    ["nvidia-smi", "--query-gpu=index,memory.used",
                     "--format=csv,noheader,nounits"],
                    capture_output=True, text=True, timeout=10).stdout
                for line in out.strip().splitlines():
                    index, used = line.split(",")
                    key = f"gpu_{index.strip()}"
                    mib = float(used)
                    self.peaks[key] = max(self.peaks.get(key, 0.0), mib)
            except Exception:
                pass
            time.sleep(2)


def verdict(item, text):
    if "known_answer" not in item:
        return None
    return VZ.math_checker(text, known_answer=item["known_answer"],
                           expression=item.get("expression"))["verdict"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--out",
                    default="reports/telemetry/m36v_phase0_gate.json")
    ap.add_argument("--private-out",
                    default="reports/shadow/private/m36v_smoke_local.jsonl")
    args = ap.parse_args(argv)

    import vllm
    from vllm import LLM, SamplingParams
    import resource

    sampler = GpuPeakSampler()
    sampler.start()
    start = time.time()
    llm = LLM(model=args.model_ref, tensor_parallel_size=2,
              max_model_len=1024, gpu_memory_utilization=0.88,
              enforce_eager=True, disable_log_stats=True)
    load_seconds = round(time.time() - start, 1)

    hf_config = llm.llm_engine.model_config.hf_config
    text_cfg = getattr(hf_config, "text_config", hf_config)
    quant = llm.llm_engine.model_config.quantization
    gates = {
        "model_type_qwen3_5_moe": hf_config.model_type == "qwen3_5_moe",
        "routed_text_layers_40":
            getattr(text_cfg, "num_hidden_layers", None) == 40,
        "experts_per_layer_256":
            getattr(text_cfg, "num_experts", None) == 256,
        "top_8_active_experts":
            getattr(text_cfg, "num_experts_per_tok", None) == 8,
        "quantization_backend_reported": bool(quant),
    }

    items = smoke_prompts()
    params = SamplingParams(temperature=0.0, max_tokens=64, logprobs=5)
    tok_start = time.time()
    outputs = llm.chat(
        [[{"role": "user", "content": item["prompt"]}] for item in items],
        params)
    gen_seconds = round(time.time() - tok_start, 2)

    rows, total_tokens = [], 0
    finite_logprobs = True
    verdicts = {"pass": 0, "fail": 0, "undecided": 0, "unchecked": 0}
    malformed_json = 0
    for item, output in zip(items, outputs):
        text = output.outputs[0].text
        n_tokens = len(output.outputs[0].token_ids)
        total_tokens += n_tokens
        for step in (output.outputs[0].logprobs or []):
            for lp in step.values():
                if lp.logprob != lp.logprob or lp.logprob in (
                        float("inf"), float("-inf")):
                    finite_logprobs = False
        v = verdict(item, text)
        verdicts[v if v else "unchecked"] += 1
        if item["kind"] == "json":
            try:
                json.loads(text.strip().strip("`").replace("json\n", "", 1))
            except Exception:
                malformed_json += 1
        rows.append({"prompt_id": item["prompt_id"], "kind": item["kind"],
                     "prompt": item["prompt"], "output": text,
                     "n_tokens": n_tokens, "verdict": v})

    sampler.stop_flag = True
    time.sleep(3)
    peak_combined_gib = round(sum(sampler.peaks.values()) / 1024, 2)
    peak_rss_gib = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 2)

    gates["finite_logprobs"] = finite_logprobs
    gates["stable_text_generation"] = all(r["output"].strip() for r in rows)
    gates["gpu_combined_within_44gib"] = peak_combined_gib <= GPU_GATE_GIB

    Path(args.private_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.private_out).write_text(
        "".join(json.dumps(r) + "\n" for r in rows))

    payload = {
        "schema_version": 1,
        "run_kind": "m36v_phase0_gate",
        "checkpoint": "cyankiwi/Agents-A1-AWQ-INT4",
        "revision_pinned": EXPECTED_REVISION,
        "model_ref_hash": VZ.evidence_hash(args.model_ref),
        "runtime": {"vllm": vllm.__version__,
                    "quantization_backend": str(quant),
                    "tensor_parallel_size": 2,
                    "max_model_len": 1024, "enforce_eager": True,
                    "hidden_state_capture": "disabled"},
        "gates": gates,
        "all_gates_passed": all(v is True for v in gates.values()),
        "load_seconds": load_seconds,
        "generation_seconds_8_prompts": gen_seconds,
        "output_tokens_total": total_tokens,
        "tokens_per_second": round(total_tokens / gen_seconds, 2)
        if gen_seconds else None,
        "gpu_peak_mib_per_device": sampler.peaks,
        "gpu_combined_peak_gib": peak_combined_gib,
        "peak_process_rss_gib": peak_rss_gib,
        "smoke_verifier_outcomes": verdicts,
        "malformed_json_count": malformed_json,
        "per_task_text_persisted_publicly": False,
        "privacy_check_status": "aggregate gates/metrics only; outputs private",
    }
    Path(args.out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[jlens] M36V phase0: all_gates={payload['all_gates_passed']} "
          f"combined={peak_combined_gib}GiB tok/s="
          f"{payload['tokens_per_second']} verdicts={verdicts} "
          f"quant={quant}", flush=True)
    for name, value in gates.items():
        if value is not True:
            print(f"[jlens]  GATE FAIL: {name} = {value}", flush=True)
    return 0 if payload["all_gates_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
