"""M36T Phase 1: single-run prefix capture for pre-truncation prediction.

One uninterrupted greedy Agents-A1 generation per task with a
2,048-token ceiling. From that single run, private prefix snapshots are
recorded at fixed decode steps 128/256/384 (primary decision point 256)
plus the final finish state. Prefix features use ONLY data at or before
the checkpoint: router summaries via the bounded expected_rows read
(prompt_rows + step) and logprob summaries over the first `step`
decode steps. Outcome classes from the single run:

  1. verified completion by 512 tokens;
  2. verified completion from 513-1024;
  3. verified completion from 1025-2048;
  4. still truncated, malformed, or verifier-failing at 2048.

Primary label: needs_more_than_512_tokens := class != 1.
Rows are private; resume skips already-captured task ids.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from m36_calibration import (  # noqa: E402
    ROUTER_FEATURE_NAMES, logprob_features, task_verdict)
from m36v_phase1 import PRIVATE_DIR, override_hash  # noqa: E402

CEILING = 2048
CHECKPOINTS = (128, 256, 384)
MAX_MODEL_LEN = 2560            # prompt + 2048-token output ceiling
VALIDATION_SAMPLE_EVERY = 16    # save raw npz for equivalence spot-checks
TASKS_IN = PRIVATE_DIR / "m36t_dev_tasks.jsonl"
ROWS_OUT = PRIVATE_DIR / "m36t_dev_rows.jsonl"


def make_llm(model_ref: str):
    from vllm import LLM

    return LLM(model=model_ref, tensor_parallel_size=2,
               max_model_len=MAX_MODEL_LEN, gpu_memory_utilization=0.88,
               enforce_eager=True, disable_log_stats=True, max_num_seqs=1,
               enable_return_routed_experts=True,
               worker_extension_cls=(
                   "jlens_vllm_telemetry.worker_ext.JlensWorkerExtension"))


def install(llm):
    hf_config = llm.llm_engine.model_config.hf_config
    text_cfg = getattr(hf_config, "text_config", hf_config)
    llm.collective_rpc("jlens_install_telemetry", args=(
        {"num_experts": text_cfg.num_experts,
         "top_k": text_cfg.num_experts_per_tok,
         "capacity_tokens": MAX_MODEL_LEN + 512,
         "raw_sample_tokens": 4},))
    llm.collective_rpc("jlens_set_telemetry_enabled", args=(True,))


def outcome_class(finish_reason: str, n_out: int, verdict: str) -> int:
    if verdict == "pass" and finish_reason != "length":
        if n_out <= 512:
            return 1
        if n_out <= 1024:
            return 2
        return 3
    return 4


def capture_task(llm, task, save_prefix=None) -> dict:
    from vllm import SamplingParams

    llm.collective_rpc("jlens_reset_telemetry")
    params = SamplingParams(temperature=0.0, max_tokens=CEILING, logprobs=5)
    t0 = time.time()
    out = llm.chat([[{"role": "user", "content": task["prompt"]}]], params,
                   use_tqdm=False)[0]
    generation_s = time.time() - t0
    comp = out.outputs[0]
    prompt_rows = len(out.prompt_token_ids)
    n_out = len(comp.token_ids)

    prefixes = {}
    for step in CHECKPOINTS:
        if n_out < step:
            continue  # run finished before this decision point
        # Bounded read aligned with logprobs[:step]: those distributions
        # come from the prefill plus decode forwards whose inputs are
        # tokens <= step-1, i.e. exactly rows < prompt_rows + step. Both
        # feature groups therefore observe the identical prefix and
        # nothing computed after the decision checkpoint.
        prefix = None
        if save_prefix is not None and step == 256:
            prefix = f"{save_prefix}_c{step}"
        summary = llm.collective_rpc(
            "jlens_fetch_summary",
            args=(prompt_rows, prefix, prompt_rows + step - 1))[0]
        feats = {name: summary[name] for name in ROUTER_FEATURE_NAMES}
        feats.update(logprob_features((comp.logprobs or [])[:step], step))
        prefixes[str(step)] = feats

    verdict = task_verdict(task, comp.text)
    cls = outcome_class(comp.finish_reason, n_out, verdict)
    return {
        "task_id": task["task_id"], "family": task["family"],
        "stratum": task["stratum"],
        "prompt_rows": prompt_rows,
        "output_tokens": n_out,
        "finish_reason": comp.finish_reason,
        "verdict": verdict,
        "outcome_class": cls,
        "needs_more_than_512_tokens": cls != 1,
        "generation_s": round(generation_s, 2),
        "prefix_features": prefixes,
        "output_text": comp.text,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--tasks", default=str(TASKS_IN))
    ap.add_argument("--out", default=str(ROWS_OUT))
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    import os
    src = str(ROOT)
    existing = os.environ.get("PYTHONPATH", "")
    if src not in existing.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            src + (os.pathsep + existing if existing else ""))

    tasks = [json.loads(l) for l in Path(args.tasks).read_text().splitlines()]
    out = Path(args.out)
    done = set()
    if out.exists():
        done = {json.loads(l)["task_id"]
                for l in out.read_text().splitlines()}
    todo = [t for t in tasks if t["task_id"] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"[jlens] M36T capture: {len(done)} done, {len(todo)} to go "
          f"(override_hash={override_hash()})", flush=True)
    if not todo:
        return 0

    llm = make_llm(args.model_ref)
    install(llm)
    cap_dir = PRIVATE_DIR / "m36t_dev_caps"
    cap_dir.mkdir(parents=True, exist_ok=True)

    with out.open("a") as sink:
        for i, task in enumerate(todo, start=1):
            prefix = (str((cap_dir / task["task_id"]).resolve())
                      if i % VALIDATION_SAMPLE_EVERY == 0 else None)
            row = capture_task(llm, task, save_prefix=prefix)
            sink.write(json.dumps(row) + "\n")
            sink.flush()
            if i % 4 == 0:
                print(f"[jlens] M36T capture {len(done) + i}/"
                      f"{len(done) + len(todo)} done", flush=True)
    print("[jlens] M36T capture complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
