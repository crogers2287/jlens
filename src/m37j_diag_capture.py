"""M37J-A: diagnostic capture on the pilot model (V100, frozen manifest).

Runs the preregistered 192-task set (commit 81432ff) unchanged: one
greedy source run per task at the 1,024-token long cap; the 256-token
short-cap outcome derives from the same run's prefix (EOS position).
Collects privately, per task:

  - metadata and output-length features;
  - output-logit confidence summaries (from generation scores);
  - MoE router summaries via gate hooks (entropy/top-k mass per step);
  - J-lens top-k token readouts at the frozen layers [2,6,11,16,21],
    every 32 decode tokens plus the final position, top-k 10, via a
    teacher-forced re-forward of the recorded generation;
  - deterministic verifier labels and finish state.

Outcome classes (raw facts stored; classes derived):
  1 completed_correct           — EOS <= 256 and verifier pass;
  2 completed_incorrect         — EOS <= 1024 and verifier fail;
  3 short_cap_truncated_long_cap_correct — 256 < EOS <= 1024 and pass;
  4 truncated_at_both_caps      — no EOS by 1024.
Capped outputs are never labeled completed-wrong. Rows are private;
resume by task id. No feature uses the verifier result or answer.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

SHORT_CAP, LONG_CAP = 256, 1024
LENS_LAYERS = (2, 6, 11, 16, 21)
READOUT_EVERY = 32
TOP_K_TOKENS = 10

SEMANTIC_GROUPS = {
    "completion": ["final", "answer", "done", "complete", "conclude"],
    "continuation": ["continue", "next", "more", "step", "then"],
    "verification": ["check", "verify", "recheck", "confirm", "calculate"],
    "error_conflict": ["error", "wrong", "mistake", "conflict", "but"],
    "uncertainty": ["uncertain", "maybe", "perhaps", "unsure", "doubt"],
}


def outcome_class(eos_pos: int | None, verdict_short: str,
                  verdict_full: str) -> int:
    if eos_pos is not None and eos_pos <= SHORT_CAP:
        return 1 if verdict_short == "pass" else 2
    if eos_pos is not None:  # 256 < eos <= 1024
        return 3 if verdict_full == "pass" else 2
    return 4


def logprob_summaries(scores, token_ids) -> dict:
    import torch

    selected, margins, entropies = [], [], []
    for step, logits in enumerate(scores):
        logp = torch.log_softmax(logits[0].float(), dim=-1)
        top2 = torch.topk(logp, 2)
        selected.append(float(logp[token_ids[step]].exp()))
        margins.append(float(top2.values[0] - top2.values[1]))
        p = logp.exp()
        entropies.append(float(-(p * logp).sum()))

    def mean(xs):
        return float(sum(xs) / len(xs)) if xs else 0.0

    return {
        "mean_selected_probability": mean(selected),
        "final_selected_probability": selected[-1] if selected else 0.0,
        "decode_entropy_mean": mean(entropies),
        "final_top2_margin": margins[-1] if margins else 0.0,
        "low_confidence_count": float(sum(s <= 0.5 for s in selected)),
    }


class RouterTap:
    """Collect per-step router entropy / top-k mass from gate hooks."""

    def __init__(self, model, top_k: int):
        import torch

        self.torch, self.top_k = torch, top_k
        self.entropy, self.mass = [], []
        self.handles = []
        for name, module in model.named_modules():
            if name.endswith("mlp.gate"):
                self.handles.append(
                    module.register_forward_hook(self._hook))

    def _hook(self, module, inputs, output):
        torch = self.torch
        if isinstance(output, tuple):
            output = output[0]
        if not torch.is_tensor(output):
            return
        logits = output.detach().float()
        if logits.ndim != 2 or logits.shape[0] != 1:
            return  # decode steps only (single-token rows)
        probs = torch.softmax(logits, dim=-1)
        p = probs[0]
        self.entropy.append(float(-(p * p.clamp_min(1e-12).log()).sum()))
        self.mass.append(float(torch.topk(p, self.top_k).values.sum()))

    def remove(self):
        for h in self.handles:
            h.remove()

    def summaries(self) -> dict:
        def mean(xs):
            return float(sum(xs) / len(xs)) if xs else 0.0

        n = len(self.entropy)
        tail = max(1, n // 8)
        return {
            "router_entropy_mean": mean(self.entropy),
            "router_mass_mean": mean(self.mass),
            "router_entropy_final_window": mean(self.entropy[-tail:]),
            "router_mass_final_window": mean(self.mass[-tail:]),
        }


def lens_readouts(lens, model, hf_model, tokenizer, prompt_ids,
                  gen_ids) -> dict:
    """Teacher-forced re-forward on the EXACT token ids (no text
    round-trip: decode->encode is not length-preserving and drifts the
    frozen positions); lens.transport + unembed at the frozen
    layers/positions."""
    import torch
    from jlens.hooks import ActivationRecorder

    n_prompt, n_gen = len(prompt_ids), len(gen_ids)
    positions = sorted({n_prompt + p for p in
                        range(READOUT_EVERY - 1, n_gen, READOUT_EVERY)}
                       | {n_prompt + n_gen - 1})
    ids = torch.tensor([prompt_ids + gen_ids],
                       device=next(hf_model.parameters()).device)
    with torch.no_grad(), ActivationRecorder(
            model.layers, at=list(LENS_LAYERS)) as rec:
        hf_model(ids)
    readout = {}
    for layer in LENS_LAYERS:
        acts = rec.activations[layer][0]  # [seq_len, d_model]
        per_pos = []
        for p in positions:
            transported = lens.transport(
                acts[p].float().to("cuda:0"), layer)
            logits = model.unembed(transported.half())
            top = torch.topk(logits.float(), TOP_K_TOKENS).indices.tolist()
            per_pos.append([tokenizer.decode([t]).strip().lower()
                            for t in top])
        readout[str(layer)] = per_pos
    return readout


def semantic_scores(readout: dict) -> dict:
    scores, misses = {}, 0
    for group, words in SEMANTIC_GROUPS.items():
        hits = 0
        for layer_tokens in readout.values():
            for pos_tokens in layer_tokens:
                if any(any(w in tok for tok in pos_tokens) for w in words):
                    hits += 1
        scores[f"group_{group}"] = float(hits)
    return scores


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--lens", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int)
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from jlens.hf import from_hf
    from jlens.lens import JacobianLens

    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from verifiers import math_checker

    def extract_json(text: str):
        """Last parseable JSON value (mirror of m36v_phase2.extract_json)."""
        cleaned = text.replace("```json", "```").replace("```", " ")
        starts = [i for i, ch in enumerate(cleaned) if ch in "{["][-24:]
        ends = [i for i, ch in enumerate(cleaned) if ch in "}]"][-24:]
        for e in reversed(ends):
            for s in starts:
                if s >= e:
                    break
                try:
                    return json.loads(cleaned[s:e + 1])
                except Exception:
                    continue
        return None

    def task_verdict(task, text: str) -> str:
        if "json_expected" in task:
            return ("pass" if extract_json(text) == task["json_expected"]
                    else "fail")
        v = math_checker(text, known_answer=task["known_answer"],
                         expression=task.get("expression"))["verdict"]
        return v or "undecided"

    tasks = [json.loads(l) for l in Path(args.tasks).read_text().splitlines()]
    out = Path(args.out)
    done = set()
    if out.exists():
        done = {json.loads(l)["task_id"]
                for l in out.read_text().splitlines()}
    todo = [t for t in tasks if t["task_id"] not in done]
    if args.limit:
        todo = todo[:args.limit]
    print(f"[m37j] diag capture: {len(done)} done, {len(todo)} to go",
          flush=True)
    if not todo:
        return 0

    device = "cuda:0"
    torch.zeros(1, device=device)
    hf_model = AutoModelForCausalLM.from_pretrained(
        args.model_ref, dtype=torch.float16, device_map={"": device})
    hf_model.eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model_ref)
    model = from_hf(hf_model, tokenizer)
    lens = JacobianLens.load(args.lens)
    text_cfg = getattr(hf_model.config, "text_config", hf_model.config)
    top_k = getattr(text_cfg, "num_experts_per_tok", 4)

    with out.open("a") as sink:
        for i, task in enumerate(todo, start=1):
            msgs = [{"role": "user", "content": task["prompt"]}]
            chat_text = tokenizer.apply_chat_template(
                msgs, add_generation_prompt=True, tokenize=False)
            prompt_ids = tokenizer(chat_text,
                                   add_special_tokens=False)["input_ids"]
            input_t = torch.tensor([prompt_ids], device=device)
            tap = RouterTap(hf_model, top_k)
            t0 = time.time()
            with torch.no_grad():
                gen = hf_model.generate(
                    input_t, max_new_tokens=LONG_CAP, do_sample=False,
                    output_scores=True, return_dict_in_generate=True,
                    pad_token_id=tokenizer.eos_token_id)
            gen_s = time.time() - t0
            tap.remove()
            gen_ids = gen.sequences[0][len(prompt_ids):].tolist()
            eos_id = tokenizer.eos_token_id
            eos_pos = (gen_ids.index(eos_id) + 1 if eos_id in gen_ids
                       else None)
            n_out = eos_pos if eos_pos is not None else len(gen_ids)
            text_full = tokenizer.decode(gen_ids[:n_out],
                                         skip_special_tokens=True)
            text_short = tokenizer.decode(gen_ids[:min(n_out, SHORT_CAP)],
                                          skip_special_tokens=True)
            v_short = task_verdict(task, text_short)
            v_full = task_verdict(task, text_full)
            cls = outcome_class(eos_pos, v_short, v_full)

            readout = lens_readouts(lens, model, hf_model, tokenizer,
                                    list(prompt_ids), gen_ids[:n_out])
            row = {
                "task_id": task["task_id"], "family": task["family"],
                "band": task["band"], "split": task["split"],
                "prompt_tokens": len(prompt_ids),
                "output_tokens": n_out,
                "eos_position": eos_pos,
                "verdict_short_cap": v_short,
                "verdict_full": v_full,
                "outcome_class": cls,
                "generation_s": round(gen_s, 2),
                "logprob_features": logprob_summaries(
                    gen.scores[:n_out], gen_ids[:n_out]),
                "router_features": tap.summaries(),
                "semantic_scores": semantic_scores(readout),
                "lens_readout_tokens": readout,
            }
            sink.write(json.dumps(row) + "\n")
            sink.flush()
            if i % 8 == 0:
                print(f"[m37j] diag {len(done) + i}/"
                      f"{len(done) + len(todo)}", flush=True)
    print("[m37j] diag capture complete", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
