# jlens — Interpretability Sidecar for Qwen3.5/3.6 MoE — STATE

Current phase: 0
Iteration count: 7
Loop status: RUNNING (gates cleared by user "Do it all, use the 3.6 variant") 

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
iter 7 | git init + commit ce5e890; loop PARKED | all CPU-only work exhausted; awaiting user approval: (1) pip install bitsandbytes (download), (2) llama-swap unload window on the 2×3090s, (3) confirm target checkpoint + its config.json model_type (qwen3_6 absent from transformers 5.13.0) | next after gate: run capture on 12-prompt set, then load_captures.py analysis
iter 6 | prompts + loader done | data/prompts.jsonl (12 prompts, 6 categories: code/math/multilingual/factual/reasoning/creative+json) + src/load_captures.py (routing_summary: entropy, dead experts, top-k load); unit-tested with synthetic tensors — all assertions pass | next: git init+commit the repo, then BLOCKED on user gate (bitsandbytes install + llama-swap unload window) for the live capture run

## Iteration 8 (2026-07-08 07:04 EDT)
- Gates cleared: bitsandbytes 0.49.2 installed; llama-swap unloaded via :9069/unload (both 3090s freed, 50/18 MiB); target confirmed = Qwen/Qwen3.6-35B-A3B snapshot 995ad96e.
- Decision: Qwen3.6-35B-A3B config is a ForConditionalGeneration wrapper — model_type qwen3_5_moe (supported by transformers 5.13.0, no trust_remote_code needed), LM params nested under text_config (num_experts=256, top-k 8, 40 layers).
- Fix: capture_router_logits.py check_arch() now descends into text_config for expert-count detection.
- Capture launched: PID 691145, nf4, 12 prompts, out=data/captures/qwen3_6_35b_a3b, log=logs/capture_36_run2.log.
- Next after capture: load_captures.py analysis on the .pt outputs.
- Decision (2026-07-08): nf4 abandoned for Qwen3.6-35B-A3B — meta-device audit showed 32.7B/34.7B params live in fused 3D expert tensors (mlp.experts.gate_up_proj/down_proj) that bitsandbytes cannot quantize (nn.Linear only); nf4 est 62GiB > 46GiB VRAM. Pivot: --dtype bf16 + accelerate CPU offload (max_memory cpu=52GiB added to capture_router_logits.py). RAM check: 60GiB available, model 67GB on disk, ~20GiB overflow streams over PCIe. Prefill-only => speed irrelevant, bf16 > nf4 for logit fidelity anyway.
- Iteration 9 fix (2026-07-08): bf16 run 1 OOM'd on GPU0 — accelerate pre_forward stages offloaded expert tensors (~1.07GiB each bf16) on-GPU but 23GiB cap left no headroom, plus ollama nomic-embed-text woke mid-run and took 800MiB. Relaunch: --max-gpu-mem-gib 20 (≈3.5GiB staging headroom/GPU, survives embed-model wakes), PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True, nomic unloaded via ollama stop.

## Iteration 9 (2026-07-08 07:30 EDT) — CAPTURE + ANALYSIS COMPLETE
- bf16 r2 capture succeeded: 12/12 prompts -> data/captures/qwen3_6_35b_a3b (~49MB, 40 router layers + 41 hidden layers each). Runtime ~4 min incl. load; 20GiB caps + expandable_segments held (no OOM, survived with offload streaming).
- load_captures.py upgraded: default --top-k 8 (matches num_experts_per_tok), corpus-level aggregate_usage(), --json report writer. Report: reports/qwen3_6_35b_a3b_routing.json.
- Findings (12 prompts, 264 tokens total, top-8 of 256, 40 MoE layers):
  * Aggregate routing entropy 80-93% of max per layer — healthy load balancing, no collapsed layers.
  * L0-L2 most diffuse (90-93%), mid-stack (L7-L21) most specialized (80-83%) — matches the shared/general->specialized depth pattern seen in DeepSeek/Qwen MoE papers.
  * 17-89 experts per layer never selected across corpus — expected at 264 tokens, NOT evidence of dead experts; needs a larger corpus to claim true deadness.
  * Per-prompt active sets are small (46-63/256 in late layers) -> strong per-domain specialization signal, good substrate for the interpretability sidecar.
- Next: cross-domain expert-overlap analysis (do code vs math vs lang prompts route to disjoint expert sets?) — this is the core sidecar question.

## Iteration 10 (2026-07-08) — Cross-domain expert-overlap analysis [COMPLETED]
- Built src/expert_overlap.py: per-layer Jaccard of top-8 expert sets across 8 domains (code_py, code_rust, creative, fact, json_tool, lang, math, reason); report → reports/qwen3_6_35b_a3b_overlap.json
- ANSWER to core sidecar question: domains do NOT route to disjoint expert sets, but are far from identical:
  - mean pairwise Jaccard 0.29–0.43 (top-k=8, 40 layers) — substantial sharing everywhere
  - most-similar pair: math|reason J=0.431; code_py|code_rust J=0.422 (semantic neighbors cluster)
  - least-similar: fact|json_tool J=0.294; code_py|reason J=0.295
  - depth terciles nearly flat (early 0.354 / mid 0.325 / late 0.363) — specialization is NOT concentrated at one depth; mid-stack slightly more specialized
  - exclusive experts are real and domain-skewed: lang=620 (peak L39), math=560 (peak L12), reason=375, fact=346 vs code_py only 54 — multilingual + math carve out the most private capacity
- Implication for interpretability sidecar: a routing-based domain classifier is viable (expert-set signatures separate domains), but expert-ablation domain surgery will have collateral damage due to ~30-40% overlap. Lang/math exclusive experts are the best ablation targets.
- Next: expert-set domain classifier probe — predict prompt domain from routing signature alone (per-layer expert histogram → logistic probe), quantify separability.

## Iteration 11 (2026-07-08) — Domain separability of routing signatures [COMPLETED]
- Built src/routing_probe.py (per-layer expert-usage histogram -> 10240-dim signature, logistic LOO probe) + NN-retrieval fallback.
- LOO probe returned 0.000 — INVALID, not a negative result: 4/8 domains are singletons, so their class is absent from LOO training folds by construction; n=12 vs 10240 dims.
- Honest test at n=12: cosine NN retrieval on full signatures:
  - retrieval@1 = 6/8 on 2-sample domains (misses: lang_es->json_tool, math_02->reason)
  - mean intra-domain cosine 0.5517 vs inter-domain 0.3738 (gap +0.178)
  - code_py<->code_rust are mutual NNs (cos 0.591) — code forms a cluster even across languages
- Conclusion: routing signature alone separates domains at coarse grain; sidecar domain-detection head is feasible.
- Next: expand data/prompts.jsonl to >=4 prompts/domain (~32 total), re-capture, then re-run probe validly.

## Iteration 12 (2026-07-08 08:20 EDT) — Roadmap item 1 COMPLETE (r3 token probe + per-layer sweep)
- Loop restarted via /prompt-master → /jlens-loop (new routerguard loop prompt installed at ~/.claude/commands/jlens-loop.md).
- r3 all-layer token acc 0.816 vs 0.175 chance (708 tokens, GroupKFold-4 by prompt) — up from r2 0.578.
- Per-layer sweep: mid-third strongest (L13-26 mean 0.613), best L20=0.712, weak at L0 (0.233) and late motor zone (L33 0.369). All-layer > best single layer → multi-layer tap required.
- r3 overlap stability check committed (findings #8). Reports: r3_token_probe.json, r3_layer_sweep.json, r3_overlap.json.
- Tasks #17/#18 satisfied. Next roadmap item: 2. Freeze capture schema v1 (CPU-only, no gate).

## Iteration 13 (2026-07-08 08:26 EDT) — Roadmap item 2 COMPLETE (freeze capture schema v1)
- src/export_schema.py + schema/v1.json (draft-07) + SCHEMA.md; router-only JSONL (topk_experts/topk_probs/full-dist entropy per layer).
- r3 exported → reports/schema/r3.jsonl (32 objs, 3.52 MB), all validate against schema/v1.json (jsonschema present in venv).
- Next roadmap item: 3. Sidecar head bakeoff on routing signatures (centroid→logreg→SVM→GBM→MLP, calibration/ECE). CPU-only. This item's completion is the loop's STOP condition.

## Iteration 14 (2026-07-08 08:30 EDT) — Roadmap item 3 COMPLETE → LOOP STOP CONDITION MET
- src/sidecar_bakeoff.py: 5-head bakeoff on frozen r3 schema, StratifiedGroupKFold(4), ECE calibration + latency.
- Results (chance 0.125): logreg/linear_svm 0.938 acc (accuracy ceiling); tiny_mlp best deployable (ECE 0.133, 0.16ms, top2 1.000); hist_gbm collapses to chance at n=32.
- Report: reports/qwen3_6_35b_a3b_r3_bakeoff.json. Verdict: routerguard sidecar feasible, sub-ms overhead, recommend calibrated tiny_mlp.
- Loop hard-stop condition ("sidecar head bakeoff has calibrated results committed") SATISFIED → stopping. Post-loop next items (NOT auto-run, need operator go): 4. retrieval-need labels, 5. decode-step capture, 6. learned risk head.

## M2 DecodeGuard — Iteration 15 (2026-07-08) — item 1 COMPLETE (real greedy decode)
- New loop prompt (M2 DecodeGuard) installed via /prompt-master. Fixes confirmed prefill-only bug.
- capture_one() now does real greedy decode when --max-new-tokens>0 (KV-cache, per-token router logits + final-logit entropy + selected-token prob). Prefill path unchanged at max_new_tokens=0.
- Verified by tests/test_decode_capture.py (CPU stub, no GPU). Next item 2: token_probe.py GroupKFold → StratifiedGroupKFold.

## M2 DecodeGuard — Iteration 16 (2026-07-08) — item 2 COMPLETE (StratifiedGroupKFold)
- token_probe.py GroupKFold → StratifiedGroupKFold (fallback to GroupKFold if infeasible). r3 all-layer token acc 0.816 → 0.863 vs 0.175 chance.
- Report: reports/qwen3_6_35b_a3b_r3_token_probe_sgkf.json. Next item 3: schema/v2_decode.json + exporter.

## M2 DecodeGuard — Iteration 17 (2026-07-08) — item 3 COMPLETE (decode schema v2 + exporter)
- schema/v2_decode.json (draft-07) + src/export_decode_schema.py. Per-generated-token records with drift_from_prefill_signature + drift_from_previous_token (cosine on per-layer expert-usage vectors).
- Verified: schema is valid draft-07; exporter dry-run on synthetic decode capture → 4 records all validate. v1 frozen schema untouched.
- Next item 4: GPU-gated r4 decode capture (--max-new-tokens 32) on Qwen3.6-35B-A3B. PRE-AUTHORIZED. Unload llama-swap first, run in background, arm Monitor.

## M2 DecodeGuard — Iteration 18 (2026-07-08 08:54 EDT) — item 4 IN FLIGHT (r4 decode capture)
- llama-swap unloaded (:9069/unload, both 3090s free 50/18 MiB). Launched r4 decode capture PID 2184628: --max-new-tokens 32, bf16, --max-gpu-mem-gib 20, expandable_segments, 32 prompts → data/captures/qwen3_6_35b_a3b_r4_decode/. Log: logs/capture_r4_decode.log. Monitor b63tp5qsj armed on PID.
- On exit: export → reports/schema/r4_decode.jsonl (validate against schema/v2_decode.json), then item 5 drift analysis.
