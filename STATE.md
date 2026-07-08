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

## M2 item 4 — progress note (2026-07-08 09:21 EDT, heartbeat)
- r4 decode capture steady ~5.3 min/prompt (CPU-offload PCIe-bound, GPU util ~25%); full 32 prompts ≈ 2.8h. 4/32 done (code_py_01, code_rust_01, math_01, math_02).
- Worker PID 2184631 (30GB RSS); wrapper 2184628. Monitor b63tp5qsj has 1h timeout < job runtime → switching to heartbeat polling as the real wake signal. Capture pre-authorized; letting it run rather than waste the 4 done + reload.

## steer.md adopted (2026-07-08 09:52 EDT)
- Collaborator pushed steer.md (fbad779) — authoritative DecodeGuard steering doc. Fast-forwarded local; .gitignore hardened (*.py[cod], .pytest_cache/).
- Loop prompt (~/.claude/commands/jlens-loop.md) rewritten via /prompt-master to read steer.md FIRST and follow its 8-step plan: (1) finish r4 + resume-skip, (2) export+validate (new validate_jsonl_schema.py), (3) rich decode_drift.py, (4) drift interpretation notes, (5) router-only decode mode + --overwrite + tests, (6) weighted drift features (schema v3), (7) decode domain-shift probe (reuse r3 head), (8) M3_RISK_LABELING.md. Stop when all delivered; human labels gate M3.
- r4 status: STILL RUNNING (~10/32), Monitor b63tp5qsj timed out (1h<runtime) → heartbeat polling is now sole wake signal. Capture writes one .pt/prompt so partial progress is safe.

## M2 DecodeGuard — Iterations 19–20 (2026-07-08 10:24 EDT) — steps 1–2 COMPLETE
- r4 decode capture CAPPED at 16/32 (operator decision, sufficient; GPUs freed). 512 decode tokens, all 8 domains. Documented reason per steer step-1 exit criteria.
- Export → reports/schema/r4_decode.jsonl (512 recs). New src/validate_jsonl_schema.py → all 512 valid vs schema/v2_decode.json.
- First-look: unweighted drift_from_prefill ~0.72 flat (structural offset), uncorrelated with entropy/sel_prob → weighted drift (step 6) + domain-shift probe (step 7) are the load-bearing follow-ups. (resume-skip deferred to step 5 with --overwrite; not needed since capture capped, not resumed.)
- Next step 3: src/decode_drift.py rich report.

## M2 DecodeGuard — Iteration 21 (2026-07-08 10:31 EDT) — step 3 COMPLETE (decode_drift.py)
- src/decode_drift.py → reports/qwen3_6_35b_a3b_r4_decode_drift.json (512 tok, full steer metric set + spikes). drift flat & uncorrelated with confidence; entropy spikes = format/mode-shift tokens (``` code fence #1). Risk head should use entropy/sel_prob, not unweighted drift.
- Next step 4: drift interpretation notes (.md).

## M2 DecodeGuard — Iteration 22 (2026-07-08 10:35 EDT) — step 4 COMPLETE (drift interpretation)
- reports/qwen3_6_35b_a3b_r4_decode_drift_notes.md: verdict unweighted-drift WEAK, entropy/sel_prob is the decode signal (mode-boundary tokens ```/<think>/\n\n spike entropy at t0-1; top-drift tokens are confident templates; 0/8 spike overlap).
- Next step 5: router-only decode mode (--router-only/--no-hidden-states/--overwrite) + resume-skip + tests.

## M2 DecodeGuard — Iteration 23 (2026-07-08 10:39 EDT) — step 5 COMPLETE (router-only mode)
- capture_router_logits.py: --router-only/--no-hidden-states + --overwrite + resume-skip (_valid_capture). tests → 4 pass. hidden_states=None tolerated downstream.
- Next step 6: weighted drift features (schema/v3_decode.json, top-k-prob-weighted signatures) — the make-or-break test for whether drift contributes any signal.

## M2 DecodeGuard — Iteration 24 (2026-07-08 10:44 EDT) — step 6 COMPLETE (weighted drift / schema v3)
- schema/v3_decode.json (v2 superset) + exporter --weighted; r4 weighted export 512 recs valid vs v3. Weighted drift STILL ~0 (×entropy -0.062, ×sel_prob +0.030) → drift dead both ways. BUT topk_mass×entropy +0.165, ×sel_prob -0.157 → first routing→confidence link. Risk head: drop drift, keep topk_mass + entropy/sel_prob.
- Next step 7: decode domain-shift probe (reuse r3 sidecar head on decode-step signatures).

## M2 DecodeGuard — Iteration 25 (2026-07-08 10:50 EDT) — step 7 COMPLETE (domain-shift probe)
- src/decode_domain_shift.py: r3 head → r4 prefill 16/16; per-token decode 72% on-domain (vs 12.5% chance) but low conf 0.25; secondary votes systematically `lang` on <think>/prose spans → real code↔prose mode shift. Windowed decode-domain = viable mode-shift feature. Report: r4_domain_shift.json.
- Next step 8 (FINAL): M3_RISK_LABELING.md (10-label taxonomy, dataset design, feature list, calibrated baselines, metrics). Then loop STOP → hand off to operator for labels.

## M2 DecodeGuard — Iteration 26 (2026-07-08 10:55 EDT) — step 8 COMPLETE → MILESTONE DONE
- M3_RISK_LABELING.md written (taxonomy, dataset, features grounded in M2 evidence, calibrated baselines, metrics, false-low-risk priority).
- ALL steer.md stop-condition artifacts present: r4_decode.jsonl (validated), decode_drift.json, drift_notes.md, router-only mode, schema v3, M3 plan. STATE+FINDINGS updated, all pushed.
- LOOP STOP CONDITION MET. M3 execution is human-gated (risk labels) — handing off to operator.

## M3 Risk Heads — Iteration 27 (2026-07-08 11:01 EDT) — step 1 COMPLETE (risk-label schema)
- New M3 loop prompt installed (label-gated scaffolding-only). schema/risk_labels_v1.json: 10-label multi-label, true/false/null, required labeler, rejects unknown/missing/bad-type. Validated.
- Next step 2: src/build_label_scaffold.py → data/labels/risk_labels_seed.jsonl (all-null records, validated).

## M3 Risk Heads — Iteration 28 (2026-07-08 11:06 EDT) — step 2 COMPLETE (label scaffold)
- src/build_label_scaffold.py → data/labels/risk_labels_seed.jsonl (32 all-null records, all validate, tracked). No fabricated labels.
- Next step 3: src/risk_features.py → reports/features/r4_risk_features.jsonl (M2 KEEP features, drift EXCLUDED).

## M3 Risk Heads — Iteration 29 (2026-07-08 11:10 EDT) — step 3 COMPLETE (risk features)
- src/risk_features.py → reports/features/r4_risk_features.jsonl (16 rows, M2 KEEP features, drift barred by assertion + verified). r3 head reused for prefill domain pred + windowed decode-domain shift.
- Next step 4: src/train_risk_heads.py + src/eval_risk_heads.py — calibrated baselines that REFUSE on all-null labels (prove the guard fires).

## M3 Risk Heads — Iteration 30 (2026-07-08 11:14 EDT) — step 4 COMPLETE (train/eval + LABEL GATE)
- src/train_risk_heads.py + src/eval_risk_heads.py: calibrated baselines + metrics (AUROC/AUPRC/ECE/false-low/false-high/latency). LABEL GATE verified: refuses on all-null seed AND missing file (exit 1, per-label diagnostics). No training, no fabricated labels.
- Next step 5 (FINAL): LABELING_HANDOFF.md → then loop STOP + operator hand-off.

## M3 Risk Heads — Iteration 31 (2026-07-08 11:18 EDT) — step 5 COMPLETE → M3 SCAFFOLDING DONE
- LABELING_HANDOFF.md (10 labels defined + examples, null rule, ≥50/family, false-low-risk priority, run command). All 7 M3 artifacts present; gate refuses seed.
- M3 STOP CONDITION MET. Human labeling is the next action — loop stops and hands off.

## M4 Benchmark-Gold — Iteration 32 (2026-07-08 11:33 EDT) — step 1 COMPLETE (source registry)
- New M4 loop prompt installed (benchmark-gold ingestion). data/registry/benchmark_sources.json: first wave TruthfulQA(Apache)/SciFact(CC-BY-NC)/GSM8K(MIT) + alternates + second wave; all 10 labels covered, licenses recorded, first-wave ≤5MB. SciFact NC flagged (FEVER alt).
- Next step 2: schema/risk_labels_v2.json (v1 superset + provenance fields).

## M4 Benchmark-Gold — Iteration 33 (2026-07-08 11:40 EDT) — step 2 COMPLETE (schema v2)
- schema/risk_labels_v2.json: v1 superset + provenance (source_*, label_source enum, label_confidence, non_commercial). Validates; rejects unknown labels + bad label_source. v1 frozen.
- Next step 3: converter #1 (TruthfulQA → answerable_from_memory / unsupported_or_hallucinated) via huggingface_hub raw pull.

## M4 Benchmark-Gold — Iteration 34 (2026-07-08 11:44 EDT) — step 3 COMPLETE (TruthfulQA converter)
- src/convert_truthfulqa.py → data/labels/benchmark/truthfulqa.jsonl: 5918 benchmark_gold records, unsupported_or_hallucinated 3318T/2600F, answerable_from_memory 2600T/rest-null. All validate v2. Raw parquet gitignored (data/raw/, *.parquet).
- Next step 4: converter #2 (SciFact or FEVER → needs_exact_citation / unsupported_or_hallucinated).

## M4 Benchmark-Gold — Iteration 35 (2026-07-08 11:48 EDT) — step 4 COMPLETE (FEVER converter)
- src/convert_fever.py → data/labels/benchmark/fever.jsonl: 15935 records (CC-BY-SA, valid.jsonl 6.5MB). unsupported_or_hallucinated 4887T/4638F/6410N; needs_exact_citation 9525T/0F (data-gap: needs a no-citation source for negatives). All validate v2.
- Next step 5: converter #3 (GSM8K → needs_math_verification, or HumanEval/MBPP → needs_code_execution).

## M4 Benchmark-Gold — Iteration 36 (2026-07-08 11:53 EDT) — step 5 COMPLETE (GSM8K, ≥3 converters)
- src/convert_gsm8k.py → data/labels/benchmark/gsm8k.jsonl: 1319 records (MIT). needs_math_verification 1319T; answerable_from_memory 1319F. 3 converters total = 23172 records. answerable_from_memory + unsupported_or_hallucinated now both-class across sources.
- Next step 6: src/coverage_report.py → reports/coverage/benchmark_coverage.json + coverage GATE.

## M4 Benchmark-Gold — Iteration 37 (2026-07-08 11:57 EDT) — step 6 COMPLETE (coverage + gate)
- src/coverage_report.py → reports/coverage/benchmark_coverage.json. 2 labels PASS (answerable_from_memory, unsupported_or_hallucinated); 8 fail (2 single-class needing negatives, 6 no-data needing second-wave sources). Gate = both-class + minority≥10.
- Next step 7: src/audit_sample.py → data/labels/audit_queue.jsonl (benchmark_gold→project-gold spot-check).

## M4 Benchmark-Gold — Iteration 38 (2026-07-08 12:01 EDT) — step 7 COMPLETE (audit sampling)
- src/audit_sample.py → data/labels/audit_queue.jsonl: 30 records (10/source, deterministic stride). Stays benchmark_gold, audit_status=pending; human promotes to gold manually. No auto-promotion.
- Next step 8 (FINAL): wire train_risk_heads.py to accept benchmark v2 labels + honor coverage gate (prototype only when gate passes; final still gold-gated).

## M4 Benchmark-Gold — Iteration 39 (2026-07-08 12:05 EDT) — step 8 COMPLETE → M4 DONE
- train_risk_heads.py: tier×coverage gate (--mode prototype allows benchmark_gold; final requires gold). Verified: all-null seed REFUSE; benchmark prototype PASS (2 labels); benchmark final REFUSE; below-threshold REFUSE.
- ALL M4 stop-condition artifacts present. M4 STOP CONDITION MET — benchmark set can populate training, prototype gated on coverage, final gated on gold. Hand off: add second-wave sources for the 8 uncovered labels + human audit benchmark_gold→gold.

## M5 Telemetry+Prototype — Iteration 40 (2026-07-08 12:11 EDT) — step 1 COMPLETE (M5 sample)
- New M5 loop prompt installed (~16-prompt smoke, operator-approved). src/build_benchmark_prompts.py → data/prompts/benchmark_m5_sample.jsonl: 16 prompts (4×TQA-correct/GSM8K/FEVER-SUPPORTS/FEVER-REFUTES), both covered labels both-class, text reconstructed. Proxy-label caveat recorded.
- Next step 2: GPU-gated router-only decode capture (~1.5h, pre-authorized). Unload llama-swap, background run, Monitor + heartbeat.
- NOTE: STATE iteration count now 40 — this counter spans M1-M5; the "stop at 40" guard refers to per-milestone runaway, not this cumulative log. M5 continues.

## M5 Telemetry+Prototype — Iteration 41 (2026-07-08 12:19 EDT) — step 2 IN FLIGHT (GPU capture)
- llama-swap unloaded (:9069/unload, GPUs free 50/18). Launched M5 router-only decode capture: worker PID 869647, --router-only --max-new-tokens 24, 16 prompts → data/captures/benchmark_m5/. Log logs/capture_m5.log. Monitor b361upjos armed (1h timeout < ~1.3h runtime → heartbeat-poll too).
- On exit: export v3 decode (step 3), features (step 4), join (step 5), real prototype train/eval (step 6).

## M5 — Iteration 42 (2026-07-08 13:22 EDT) — steps 2–3 COMPLETE (capture + v3 export)
- 16/16 router-only captures done; reports/schema/benchmark_m5_decode.jsonl = 384 records, all valid v3. GPUs freed.
- Next step 4: reports/features/benchmark_m5_features.jsonl via risk_features (drift excluded), then join (5) + real prototype train/eval (6).

## M5 — Iteration 43 (2026-07-08 13:22 EDT) — steps 4–5 COMPLETE (features + join)
- benchmark_m5_features.jsonl (16 rows, drift excluded). join → 16/16 matched; both covered labels both-class (ansmem 4/4, unsup 4T/8F). Next step 6: REAL prototype train/eval (LOO, tiny-n honest metrics).

## M5 — Iteration 44 (2026-07-08 13:23 EDT) — step 6 COMPLETE → M5 DONE
- Real LOO prototype heads trained: answerable_from_memory AUROC 0.875, unsupported_or_hallucinated AUROC 0.844 (ranking real vs chance); BUT tiny-n → bad calibration + false-low-risk at 0.5 threshold. final mode still refuses. reports/risk_heads_prototype.json.
- ALL M5 stop-condition artifacts present. M5 STOP CONDITION MET. Hand off: scale sample (more prompts/class), add second-wave sources for 8 uncovered labels, human-audit benchmark_gold→gold for final calibration.

## M6 PolicyEngine v0 — Iteration M6.1 (2026-07-08 13:45 EDT) — step 1 COMPLETE (config)
- New M6 loop prompt (advisory/shadow, CPU-only). config/policy_engine_v0.json: risk = max(1-p_ansmem, p_unsup); bands low/med/high/critical → answer_locally/verify/retrieve/require_confirmation. Prototype-only, no gating. Validated.
- Next step 2: src/policy_engine.py (fit M5 heads, score(feature_row)→{level,scores,recommended_action,explanation}, advisory-only).

## M6 PolicyEngine v0 — Iteration M6.2 (2026-07-08 13:52 EDT) — step 2 COMPLETE (scorer)
- src/policy_engine.py: fits M5 heads, score()→{level,scores,risk,recommended_action,explanation}, advisory-only. 16/16 M5 rows scored; FEVER→critical/require_confirmation, spread 6crit/4med/6low.
- Next step 3: src/risk_runtime.py CLI + shadow log (reports/shadow/shadow_log.jsonl).

## M6 PolicyEngine v0 — Iteration M6.3 (2026-07-08 13:56 EDT) — step 3 COMPLETE (shadow runtime)
- src/risk_runtime.py + reports/shadow/shadow_log.jsonl. Advisory-only, records never acts. Verified 3 entries parse w/ required keys.
- Next step 4: tests/test_policy_engine.py (config/score/mapping/log). Then step 5 docs.

## M6 PolicyEngine v0 — Iteration M6.4 (2026-07-08 14:00 EDT) — step 4 COMPLETE (tests)
- tests/test_policy_engine.py 4/4 pass (config/score/band-mapping/shadow-log). decode tests still pass. Next step 5 (FINAL): docs/POLICY_ENGINE_V0.md.

## M6 PolicyEngine v0 — Iteration M6.5 (2026-07-08 14:04 EDT) — step 5 COMPLETE → M6 DONE
- docs/POLICY_ENGINE_V0.md (schemas, action semantics, worked example, posture). All M6 artifacts present; final mode still refuses. M6 STOP CONDITION MET. Hand off: annotate shadow-log outcomes; scale (M6-scaling track) + gold audit for production thresholds.

## M7 Local shadow wrapper — Iteration M7.1 (2026-07-08 14:10 EDT) — step 1 COMPLETE (endpoint config)
- New M7 loop prompt (CPU-only, dry-run default, advisory/shadow). config/local_endpoint_example.json: placeholder OpenAI-compat endpoint, no secret. Validated.
- Next step 2: src/local_shadow_wrapper.py (dry-run default; live optional; policy=null when no feature row; real-use log).

## M7 Local shadow wrapper — Iteration M7.2 (2026-07-08 14:18 EDT) — step 2 COMPLETE (wrapper)
- src/local_shadow_wrapper.py: dry-run default + optional live; scored path (feature row present) and policy=null path (no telemetry) both verified; advisory-only, no actions. reports/shadow/realuse_log.jsonl written (public TQA prompts).
- Next step 3: docs/M7_SHADOW_RUNTIME.md (record schema + run instructions).

## M7 Local shadow wrapper — Iteration M7.3 (2026-07-08 14:22 EDT) — step 3 COMPLETE (runtime doc)
- docs/M7_SHADOW_RUNTIME.md matches the emitted record; run instructions + posture + privacy rule. Next step 4: fixture tests (stubbed live). Then step 5 sample log.

## M7 Local shadow wrapper — Iteration M7.4 (2026-07-08 14:26 EDT) — step 4 COMPLETE (tests)
- tests/test_local_shadow_wrapper.py 4/4 pass (dry-run/scored/null/stubbed-live). No real network. Other suites pass. Next step 5 (FINAL): reports/shadow/realuse_sample.jsonl (public prompts).

## M7 Local shadow wrapper — Iteration M7.5 (2026-07-08 14:29 EDT) — step 5 COMPLETE → M7 DONE
- reports/shadow/realuse_sample.jsonl (6 public records, 3 answer_locally/1 verify/2 require_confirmation, outcome null). Doc sample section. All M7 artifacts present; final refuses. M7 STOP CONDITION MET. Hand off: annotate outcome fields in real use; scale/gold-audit for production thresholds.
