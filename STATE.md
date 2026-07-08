# jlens — Interpretability Sidecar for Qwen3.5/3.6 MoE — STATE

Current phase: 0
Iteration count: 6

## Phase 0 — Feasibility (exit: go/no-go memo in STATE.md)
- [x] Create project venv + dir layout (jlens/{src,probes,data,lenses,reports})
- [x] Verify HF transformers version supports Qwen3.5/3.6 MoE with output_hidden_states AND output_router_logits — cite the actual class/source line
- [ ] VRAM math: can Qwen3.6-35B-A3B run 4-bit via transformers on <=20GB while capturing hidden states? Test with smallest Qwen3.5 MoE first if available
- [ ] Verify existence of claimed tools: neuronpedia/jacobian-lens (HF), Qwen-Scope SAEs — record real URLs or mark FALSIFIED
- [ ] Write go/no-go: if full 35B instrumentation infeasible, propose fallback (smaller MoE, layer subset, CPU offload)

## Phase 1 — Instrumentation + probes (exit: probe AUC report)
- [ ] Capture script: hidden_states (middle-third layers), router logits, final logits, token probs -> .npz per prompt
- [ ] Build eval set: ~200 factual QA (known-answer), ~50 adversarial/prompt-injection, ~50 uncertain/unanswerable
- [ ] Train logistic-regression probes: knows-answer, likely-factual, injection-present, needs-retrieval
- [ ] Report AUC per probe per layer; identify best layers

## Phase 2 — Approximate J-lens (exit: lens readout demo)
- [ ] Calibration corpus 500+ diverse examples; low-rank averaged-Jacobian approximation, middle layers only, bf16
- [ ] Compare lens readout vs raw logit-lens on held-out prompts; quantify improvement

## Phase 3 — Runtime policy sidecar (exit: working demo + report)
- [ ] Risk scorer combining probe outputs + router-instability metric (entropy of router logits across layers)
- [ ] Sidecar script: given a prompt, emit risk tier (low/medium/high/critical) + recommended action (fast/careful/RAG/refuse)
- [ ] Final report: reports/FINDINGS.md — what worked, what was falsified, latency cost, whether production integration is worth it

## Decisions
- VERIFIED (iter 3): transformers 5.13.0 (in .venv) supports Qwen3.5 MoE with router logits. Citations (models/qwen3_5_moe/modeling_qwen3_5_moe.py): `class Qwen3_5MoeForCausalLM` L1788; `output_router_logits` forward param L1818, config fallback L1845-1846, returned in outputs L1871-1873; `class Qwen3_5MoeTopKRouter` L779 with `router_logits = F.linear(...)` L789; OutputRecorder hook `"router_logits": OutputRecorder(Qwen3_5MoeTopKRouter, index=0)` L909; output dataclass fields `router_logits` L1229/L1242. output_hidden_states is standard PreTrainedModel plumbing.
- RESOLVED (iter 4): torch install gate AVOIDED — system python has torch 2.5.1+cu121 with working CUDA. Enabled `include-system-site-packages = true` in .venv/pyvenv.cfg; verified `.venv/bin/python` imports torch 2.5.1+cu121 (cuda True) + transformers 5.13.0 together. No download needed.
- VRAM MATH (iter 4): Qwen3.5-35B-A3B at 4-bit NF4 ≈ 35e9 × ~0.55 B/param ≈ **~19.3 GB weights** (incl. quant metadata). Single 3090 (24576 MiB) is too tight with CUDA context + activations; **2×3090 with device_map=auto is comfortable (~10 GB/card)**. Capture overhead per 1k tokens: hidden states ~48 layers × 4096 hidden × 2 B ≈ 400 MB (stream to CPU per forward); router logits ~48 × 128 experts × 2 B ≈ 12 MB — negligible. Conclusion: capture test is feasible on this box.
- GATE ADDITION (iter 5): `bitsandbytes` is NOT installed in the venv (accelerate 1.11.0 IS present). Installing it is a pip download — bundled into the same user-approval gate as the llama-swap unload window. Script defaults to nf4 but supports `--dtype bf16` (won't fit 35B on this box, only useful for smaller checkpoints).
- GATE (iter 4, HUMAN/OPERATIONAL): both 3090s are currently ~full (23042/24576 and 20297/24576 MiB) serving llama-swap. Running the 4-bit capture test requires temporarily unloading llama-swap models — do NOT do this without user approval since it disrupts live serving. Loop will proceed with non-GPU tasks (probe/capture script authoring) until user approves a GPU window.
- RISK (iter 3): NO `qwen3_6` architecture exists in transformers 5.13.0 (checked models/ dir and configuration_auto.py). Qwen3.6-35B-A3B presumably ships under the qwen3_5_moe (or qwen3_next) architecture, or needs a newer transformers — must confirm against the actual model's config.json `model_type` before the VRAM test. Note: pip'd transformers has no torch yet (tokenizer/config-only) — torch install is a separate, larger step.

## Iteration Log
iter 1 | bootstrap STATE.md | created with all tasks unchecked | next: create venv + dir layout
iter 2 | venv + dir layout | .venv (Python 3.12.3) + src/probes/data/lenses/reports created, verified via ls | next: verify HF transformers Qwen3.5/3.6 MoE router-logits support
iter 3 | transformers MoE verification | VERIFIED qwen3_5_moe router logits (transformers 5.13.0, citations in Decisions); qwen3_6 arch ABSENT — flagged risk | next: VRAM math + 4-bit capture test (needs torch install first — flag at gate if large)
iter 4 | torch wiring + VRAM math | system torch 2.5.1+cu121 reused via pyvenv.cfg (no download); VRAM math done — 4-bit 35B-A3B fits on 2×3090 (~19.3 GB); GPU capture test GATED on user approving llama-swap unload | next: author capture script (src/capture_router_logits.py) — no GPU needed to write+lint it
iter 5 | capture script authored | src/capture_router_logits.py written (arch guard for missing qwen3_6, NF4 config, CPU-streamed captures); py_compile OK, --help OK; bitsandbytes missing → added to approval gate | next: author data/prompts.jsonl starter set + analysis-side loader (src/load_captures.py), both CPU-only
iter 6 | prompts + loader done | data/prompts.jsonl (12 prompts, 6 categories: code/math/multilingual/factual/reasoning/creative+json) + src/load_captures.py (routing_summary: entropy, dead experts, top-k load); unit-tested with synthetic tensors — all assertions pass | next: git init+commit the repo, then BLOCKED on user gate (bitsandbytes install + llama-swap unload window) for the live capture run
