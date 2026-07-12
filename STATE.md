# jlens — Interpretability Sidecar for Qwen3.5/3.6 MoE — STATE

Current phase: M36C (adaptive Agents-A1 calibration) + M37J pilot (parallel)
Live status: docs/OVERNIGHT_STATUS_2026-07-12.md and steer.md are current
M1-M35 sealed; M36V complete (full_telemetry). Below is the original
phase-0 planning record, retained for history.

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

## M8 Outcome review — Iteration M8.1 (2026-07-08 14:37 EDT) — step 1 COMPLETE (outcome schema)
- New M8 loop prompt (CPU-only, never-fabricate-outcomes). schema/shadow_outcome_v1.json: outcome + review_meta, null=unreviewed, rejects bad type/unknown/range. Validated.
- Next step 2: src/build_review_queue.py → reports/shadow/review_queue_sample.jsonl (all-null, validated).

## M8 Outcome review — Iteration M8.2 (2026-07-08 14:43 EDT) — step 2 COMPLETE (review queue)
- src/build_review_queue.py → reports/shadow/review_queue_sample.jsonl: 9 all-null unreviewed records (public prompts), all validate. reviewed=0/9. No fabricated outcomes.
- Next step 3: src/review_shadow_log.py (safe non-interactive CLI to set fields; refuses bad type/unknown/unknown-id).

## M8 Outcome review — Iteration M8.3 (2026-07-08 14:47 EDT) — step 3 COMPLETE (review CLI)
- src/review_shadow_log.py: explicit-flag review, validates, --dry-run, refuses bad bool/range/unknown-id, never guesses. Exercised on throwaway copy; committed queue stays all-null.
- Next step 4: src/outcome_report.py → reports/outcomes/outcome_coverage.json (honest 0-reviewed).

## M8 Outcome review — Iteration M8.4 (2026-07-08 14:51 EDT) — steps 4–5 COMPLETE (coverage + calibration)
- src/outcome_report.py → outcome_coverage.json (reviewed=0/9) + calibration_notes.md ("pending" honest). FLR/FHR from reviewed-only; verified on synthetic fixtures (FLR 0.5/FHR 0.0). Production stays gated.
- Next step 6: docs/SHADOW_OUTCOME_REVIEW.md. Then step 7 tests.

## M8 Outcome review — Iteration M8.5 (2026-07-08 14:55 EDT) — step 6 COMPLETE (review guide)
- docs/SHADOW_OUTCOME_REVIEW.md: reviewer flow, field meanings, null-if-unsure, calibration explanation, honesty+gating. Next step 7 (FINAL): tests/test_outcome_review.py.

## M8 Outcome review — Iteration M8.6 (2026-07-08 14:58 EDT) — step 7 COMPLETE → M8 DONE
- tests/test_outcome_review.py 5/5 pass; all 4 suites pass (17 tests). All M8 artifacts present; committed queue all-null; final refuses. M8 STOP CONDITION MET. Hand off to HUMAN reviewer: annotate outcomes → calibration → (once enough reviewed) unlock production thresholds via gold audit.

## M9 Private workflow — Iteration M9.1 (2026-07-08 15:59 EDT) — step 1 COMPLETE (private dir gitignored)
- New M9 loop prompt (privacy-as-invariant, CPU-only). .gitignore blocks reports/shadow/private/*.jsonl; README stub committed. Verified check-ignore.
- Next step 2: document local private-log generation (public-fixture example only) — folded into step 6 doc.

## M9 Private workflow — Iteration M9.2 (2026-07-08 16:05 EDT) — step 3 COMPLETE (redaction) [step 2 doc folds into step 6]
- src/redact_shadow_log.py: scrubs prompt/output/notes, keeps structure/bools; verified on public fixture, no text leak.
- Next step 4: src/private_outcome_summary.py → reports/outcomes/private_summary_sample.json (aggregate-only, no text).

## M9 Private workflow — Iteration M9.3 (2026-07-08 16:12 EDT) — step 4 COMPLETE (aggregate summary)
- src/private_outcome_summary.py → reports/outcomes/private_summary_sample.json: total/reviewed/unreviewed, level + action distributions, per-outcome-field non-null counts, calibration (reviewed-only, null when 0). Output built from scratch + recursive no-text-string guard. Verified on public fixture: 6 records, 0 reviewed, no leaked text.
- Next step 5: src/check_commit_safe.py (guard: refuse private-path refs + unredacted prompt/output/notes text; pass aggregate/all-null/redacted).

## M9 Private workflow — Iteration M9.4 (2026-07-08 16:17 EDT) — step 5 COMPLETE (commit-safety guard)
- src/check_commit_safe.py: refuses private-log paths, private-dir refs, and unredacted prompt/output/notes text; passes aggregate/all-null-text/redacted. All 6 cases verified. Conservative by design (can't distinguish public benchmark text from private) → workflow commits only aggregates/redacted going forward.
- Next step 6: docs/PRIVATE_SHADOW_WORKFLOW.md (end-to-end local-only workflow, public-fixture examples, gating note).

## M9 Private workflow — Iteration M9.5 (2026-07-08 16:22 EDT) — step 6 COMPLETE (workflow doc) [folds step 2]
- docs/PRIVATE_SHADOW_WORKFLOW.md: local-only end-to-end (generate→review→aggregate/redact→guard→commit), public-fixture examples, commands verified vs real flags, gating note. Scoped check_commit_safe private-path content check to JSON records only (prose passes) — re-verified 5 cases.
- Next step 7 (FINAL): tests/test_private_workflow.py, then M9 DONE.

## M9 Private workflow — Iteration M9.6 (2026-07-08 16:23 EDT) — step 7 COMPLETE → M9 DONE
- tests/test_private_workflow.py 5/5 pass; full suite green (22 tests). All M9 artifacts present: private dir gitignored + README; workflow doc (public-fixture); redact tool; aggregate summary; commit-safe guard; tests. No private text committed; production thresholds gated. M9 STOP CONDITION MET.
- HAND OFF TO HUMAN: run real prompts locally → review outcomes → aggregate/redact → commit-safe share; accumulated reviewed records eventually calibrate + unlock production thresholds via gold audit.

## M10 Autonomous supervisor — Iteration M10.1 (2026-07-08 17:44 EDT) — step 1 COMPLETE (supervisor config)
- New M10 loop prompt installed (autonomous supervisor, privacy+autonomy invariants, CPU-only) via /prompt-master. steer.md synced to post-M9 (461c2ad).
- config/autonomous_supervisor_v0.json: Agents-A1 GGUF endpoint (placeholder), task_sources (public fixture + optional private), verifier toggles, escalation thresholds, private-dir default log. Loads OK; log path gitignored; no secrets.
- Next step 2: schema/auto_outcome_v1.json (NEW draft-07, separate from frozen shadow_outcome_v1; auto_outcome candidate fields + human fields stay null).

## M10 Autonomous supervisor — Iteration M10.2 (2026-07-08 17:49 EDT) — step 2 COMPLETE (auto_outcome schema)
- schema/auto_outcome_v1.json: NEW draft-07, separate from frozen shadow_outcome_v1 (confirmed). auto_outcome candidate fields + telemetry_missing bool; human outcome/review_meta present but supervisor never writes them. 6 validation behaviors verified (good validates; bad bool/unknown-field/conf>1 rejected; undecided all-null valid).
- Next step 3: src/verifiers.py (6 cheap verifier adapters, evidence hashed, self-consistency disagreement=escalation).

## M10 Autonomous supervisor — Iteration M10.3 (2026-07-08 17:53 EDT) — step 3 COMPLETE (verifier adapters)
- src/verifiers.py: 6 adapters (exact/regex/math/code-fixture-stub/retrieval-heuristic/self-consistency). Evidence hashed (no raw text, verified). code_test_stub runs fixture callable only (no arbitrary exec). self-consistency disagreement=undecided(escalation) not fail. All verified on fixtures.
- Next step 4: src/autonomous_shadow_supervisor.py (fake-endpoint end-to-end run → auto_outcome records + escalation; telemetry_missing honest; human fields untouched).

## M10 Autonomous supervisor — Iteration M10.4 (2026-07-08 17:57 EDT) — step 4 COMPLETE (supervisor end-to-end)
- src/autonomous_shadow_supervisor.py + public fixture data/prompts/autonomous_tasks_sample.jsonl (6 tasks). Run: 6 auto_outcome_v1-valid records, escalated=4, telemetry_missing all true + policy null (honest GGUF), needs_retrieval flagged on current-info, human outcome/review_meta all null (auto never writes). Default out = gitignored private log.
- Next step 5: src/autonomous_outcome_report.py (aggregate-only run summary, no text; committed sample from public fixtures).

## M10 Autonomous supervisor — Iteration M10.5 (2026-07-08 18:01 EDT) — steps 5–6 COMPLETE (aggregate report + sample)
- src/autonomous_outcome_report.py (aggregate-only, no-text guard) + committed reports/outcomes/autonomous_summary_sample.json from public fixture: 6 records, telemetry_missing=6, escalation rate 0.667, agreement null (no human review). Leak grep clean; check_commit_safe passes.
- Next step 7: docs/AUTONOMOUS_SHADOW_SUPERVISOR.md (end-to-end, guardrails, gating).

## M10 Autonomous supervisor — Iteration M10.6 (2026-07-08 18:04 EDT) — step 7 COMPLETE (workflow doc)
- docs/AUTONOMOUS_SHADOW_SUPERVISOR.md: end-to-end (config→run→verifiers→auto/human separation→escalation→aggregate→commit-safe), public-fixture examples, commands verified vs real flags, guardrails + gating.
- Next step 8 (FINAL): tests/test_autonomous_supervisor.py, then M10 DONE.

## M10 Autonomous supervisor — Iteration M10.7 (2026-07-08 18:06 EDT) — step 8 COMPLETE → M10 DONE
- tests/test_autonomous_supervisor.py 5/5 pass; full suite green (27 tests). All M10 deliverables present: config, auto_outcome_v1 schema, verifiers, supervisor, aggregate report + committed sample, doc, tests. auto_outcome separate from human fields (verified untouched); telemetry_missing honest; escalation exercised; no private text committed; production thresholds gated. M10 STOP CONDITION MET.
- HAND OFF TO HUMAN: run local workload → auto_outcome candidates + escalations accumulate → review escalated subset → calibration unlocks production thresholds via gold audit.

## M11 Agents-A1 workload — Iteration M11.1 (2026-07-08 18:13 EDT) — step 1 COMPLETE (run config + ignore fix)
- New M11 loop prompt installed (bounded Agents-A1 workload; smoke-path build) via /prompt-master. steer.md synced post-M10 (7cf9b3b). NOTE: operator confirmed fusion is OFF — 3090s available; a genuinely LIVE Agents-A1 run is now authorized as the harness-complete follow-up (confirm serving approach first; don't disrupt llama-swap's existing models/config).
- config/agents_a1_shadow_run.json (run_id cd08d63a145be1d2). Hardened .gitignore to reports/shadow/private/* except README (run-meta .json was previously not ignored).
- Next step 2: data/prompts/agents_a1_smoke_batch.jsonl (public ~25-task batch).

## M11 Agents-A1 workload — Iteration M11.2 (2026-07-08 18:15 EDT) — step 2 COMPLETE (public smoke batch)
- data/prompts/agents_a1_smoke_batch.jsonl: 25 public tasks (math5/exact5/regex4/current_info4/explain7), unique ids, within cap. Public input, tracked.
- Next step 3: src/run_agents_a1_shadow_batch.py (bounded + resume-safe wrapper + run metadata + failure counting).

## M11 Agents-A1 workload — Iteration M11.3 (2026-07-08 18:19 EDT) — step 3 COMPLETE (batch runner)
- src/run_agents_a1_shadow_batch.py: bounded + resume-safe + run metadata + failure-count/continue. Smoke: run1 25 completed (13 escalated, telemetry_missing 25), run2 resume adds 0; failure injection → 25 failed continue; records valid; run_id stable. Private outputs gitignored.
- Next step 4: src/make_escalation_review_queue.py (only-escalated local queue, human fields null).

## M11 Agents-A1 workload — Iteration M11.4 (2026-07-08 18:21 EDT) — step 4 COMPLETE (escalation queue)
- src/make_escalation_review_queue.py: only escalate_for_review==true rows → local gitignored queue; auto_outcome kept for reviewer context; human outcome/review_meta forced null. Smoke: 13/25 escalated, queue=13 (matches), human-null, valid.
- Next step 5: src/agents_a1_run_report.py (aggregate-only run report + metadata) + committed public sample.

## M11 Agents-A1 workload — Iteration M11.5 (2026-07-08 18:24 EDT) — step 5 COMPLETE (aggregate run report + sample)
- src/agents_a1_run_report.py (metadata + distributions, no-text guard) + committed reports/outcomes/agents_a1_run_summary_sample.json from public smoke run: 25 completed, escalation rate 0.52, agreement null, no text keys, commit-safe.
- Next step 6: docs/AGENTS_A1_SHADOW_RUN.md (run locally, resume, review escalated, live path HUMAN-GATED, guardrails).

## M11 Agents-A1 workload — Iteration M11.6 (2026-07-08 18:25 EDT) — step 6 COMPLETE (run doc)
- docs/AGENTS_A1_SHADOW_RUN.md: smoke + live (serve-endpoint-first) runs, resume/retry, escalated-subset review, aggregate report + commit-safe, guardrails/gating. Commands verified vs flags.
- Next step 7 (FINAL): tests/test_agents_a1_shadow_run.py, then M11 harness DONE (live Agents-A1 GPU run = deliberate follow-up on the now-available 3090s).

## M11 Agents-A1 workload — Iteration M11.7 (2026-07-08 18:28 EDT) — step 7 COMPLETE → M11 HARNESS DONE
- tests/test_agents_a1_shadow_run.py 5/5 pass; full suite green (32 tests). Fixed test_private_workflow gitignore assertion (git check-ignore README) after private-dir ignore hardening. All M11 harness deliverables present: config, smoke batch, resume-safe runner, escalation queue, aggregate report + sample, doc, tests. Private raw logs gitignored + never staged; auto never wrote human fields; production thresholds gated. M11 HARNESS STOP CONDITION MET.
- NEXT (deliberate, authorized 3090s): serve Agents-A1-Q8_0-GGUF on a free port + run 25-task batch --mode live → escalation queue → review. Operator confirmed fusion off.

## M11 Agents-A1 workload — Iteration M11.8 (2026-07-08 18:36 EDT) — LIVE RUN DONE (capstone)
- FIRST live Agents-A1 run: endpoint already served by llama-swap on fred :9069 (model `agents-a1`, Q8_0 no-mtp, both 3090s) — no serving needed. run_id 88e140ea5d129bc3: 25/25 completed, 0 failed, telemetry_missing 25, escalated 7 (rate 0.28), ~1min. Auto verdicts (candidates): math 5/5 + exact 5/5 correct, regex 3/4 (1 escalated), current_info flagged needs-retrieval, explain escalated low-conf. Committed public aggregate agents_a1_run_summary_live.json (commit-safe, no text); private raw logs gitignored.
- NEXT: human-review the 7 escalated rows (reports/shadow/private/agents_a1_review_live.jsonl) via the M8 review CLI → first auto-vs-human agreement; then M12 (calibration / broader run / label converters per steer).

## M12 Verifier calibration — Iteration M12.1 (2026-07-08 19:44 EDT) — step 1 COMPLETE (JSON verifier)
- New M12 loop prompt installed (verifier hardening + reviewed calibration) via /prompt-master. steer.md synced post-M11 (c792170).
- src/verifiers.py: json_object_check (json.loads + balanced-brace extraction, type + required_keys, hashed evidence); regex unchanged; registered. Fixes #75 live false-positive. 9 cases verified; no leak.
- Next step 2: route JSON tasks to json_object_check in _run_verifiers + update smoke batch JSON row to json_check.

## M12 Verifier calibration — Iteration M12.2 (2026-07-08 19:50 EDT) — step 2 COMPLETE (JSON routing)
- _run_verifiers routes json_check/json_required tasks → json_object_check; regex guarded to skip json tasks (regex for regex only); escalation/confidence math untouched. Smoke fixture sm_regex_01 → json_check+json_required. Routing verified; full suite green.
- Next step 3: review the 7 escalated live records (objective/ground-truth) → gitignored reviewed queue.

## M12 Verifier calibration — Iteration M12.3 (2026-07-08 19:52 EDT) — step 3 COMPLETE (objective review)
- Reviewed all 7 escalated live rows vs public benchmark ground truth (operator_review) → gitignored agents_a1_reviewed_live.jsonl (valid, unstaged). All objectively correct (was_wrong=False). sm_regex_01 = the one agreement-comparable row (auto=wrong, human=right → the false-positive). 6 explain rows auto=None (low-conf escalation).
- Next step 4: run agents_a1_run_report over reviewed queue → public reviewed aggregate + first auto_vs_human_agreement.

## M12 Verifier calibration — Iteration M12.4 (2026-07-08 19:55 EDT) — step 4 COMPLETE (first agreement)
- Public reviewed aggregate agents_a1_reviewed_summary_sample.json (over 7-row reviewed subset): FIRST auto_vs_human_agreement = n_compared 1, rate 0.0 (sm_regex_01 auto=wrong vs human=right = the false-positive); human_reviewed_count 7. No text keys; commit-safe.
- Next step 5: before/after escalation comparison (old regex vs new json verifier on the live JSON row).

## M12 Verifier calibration — Iteration M12.5 (2026-07-09 00:04 EDT) — step 5 COMPLETE (before/after)
- Added json_object_check to CORRECTNESS (its verdict now feeds auto_was_wrong — completes the wiring; escalation formula unchanged). Public before/after agents_a1_verifier_beforeafter_sample.json: regex fail vs json pass on representative output → sm_regex_01 flips wrong→ok, escalation 7→6, auto_was_wrong 1→0. Suite green; commit-safe.
- Next step 6: docs/M12_VERIFIER_REVIEW_CALIBRATION.md.

## M12 Verifier calibration — Iteration M12.6 (2026-07-09 00:06 EDT) — step 6 COMPLETE (doc)
- docs/M12_VERIFIER_REVIEW_CALIBRATION.md: finding → JSON verifier + routing + CORRECTNESS → objective review → first agreement (n=1, 0.0) → before/after (7→6, 1→0) → gating. Public aggregates only.
- Next step 7 (FINAL): tests (json verifier, routing, reviewed aggregate, before/after), then M12 DONE.

## M12 Verifier calibration — Iteration M12.7 (2026-07-09 00:08 EDT) — step 7 COMPLETE → M12 DONE
- tests/test_verifier_json.py 4/4 pass; full suite green (36 tests). All M12 deliverables: json_object_check + routing + CORRECTNESS wiring; objective review of 7 escalated (gitignored); public reviewed aggregate (agreement n=1 rate 0.0); before/after (7→6, 1→0); doc; tests. Private never staged; auto candidate; production gated. M12 STOP CONDITION MET.
- NEXT per steer M13: A larger Agents-A1 run (100-250) / B calibration from reviewed records / C missing-label converters.

## M13 Larger run — Iteration M13.1 (2026-07-09 00:32 EDT) — step 1 COMPLETE (batch generator)
- New M13 loop prompt installed (larger live run; call-endpoint-never-serve) via /prompt-master. steer.md synced post-M12 (56f6ab4).
- src/gen_m13_batch.py → data/prompts/agents_a1_m13_batch.jsonl: 110 public tasks (math44/exact20/json10/regex8/current10/explain18), unique, deterministic, math self-consistent.
- Next step 2: config/agents_a1_m13_run.json (agents-a1 endpoint, batch size 120 cap 250, self_consistency_samples 1).

## M13 Larger run — Iteration M13.2 (2026-07-09 00:37 EDT) — step 2 COMPLETE (run config)
- config/agents_a1_m13_run.json: agents-a1 endpoint, batch 120/cap 250, self_consistency_samples 1 (110 calls), private out paths. run_id 8f702be95736bbe5 stable; paths ignored.
- Next step 3: LIVE run of the 110-task batch against agents-a1 on fred (capped model_fn) → gitignored private log.

## M13 Larger run — Iteration M13.3 (2026-07-09 00:44 EDT) — step 3 COMPLETE (LIVE 110-task run)
- LIVE agents-a1 run run_id cd3d744045af170e: 110/110 completed, 0 failed, telemetry_missing 110, escalated 18 (rate 0.164 vs baseline 0.28), auto_was_wrong 1. math/json/regex 0 escalated (JSON fix validated at scale); explain 17/18 escalated (unverifiable); exact 1 wrong. Records valid, human-null, private unstaged.
- Next step 4: aggregate report (public) + escalation queue (gitignored).

## M13 Larger run — Iteration M13.4 (2026-07-09 00:48 EDT) — step 4 COMPLETE (aggregate + escalation queue)
- Public agents_a1_m13_summary_sample.json: 110 completed, ok81/wrong1/undecided28, escalation 18 (0.164), verifier dist (json_object_check 10, math 44, etc.), agreement null. Escalation queue gitignored (18/110, human-null). No text; commit-safe.
- Next step 5: review a representative escalated subset (objective) → public reviewed-subset summary.

## M13 Larger run — Iteration M13.5 (2026-07-09 00:52 EDT) — step 5 COMPLETE (reviewed subset)
- Reviewed representative 6/18 escalated rows (objective) → gitignored subset + public agents_a1_m13_reviewed_subset_sample.json: human_reviewed_count 6, agreement n=1 rate 0.0. m13_e_019 = NEW exact_answer_match strictness finding (approx/unit-converted numerics; model was right ~300k km/s). No text; commit-safe.
- Next step 6: M13-vs-baseline comparison report.

## M13 Larger run — Iteration M13.6 (2026-07-09 00:55 EDT) — step 6 COMPLETE (baseline comparison)
- Public agents_a1_m13_vs_baseline.json: escalation 0.28→0.164 at 4.4× scale; JSON tasks 0 escalated (M12 fix validated); the 1 M13 auto-wrong is a new exact-match numeric-strictness case, not the fixed JSON one. No text; commit-safe.
- Next step 7: docs/M13_LARGER_AGENTS_A1_RUN.md.

## M13 Larger run — Iteration M13.7 (2026-07-09 00:57 EDT) — step 7 COMPLETE (run doc)
- docs/M13_LARGER_AGENTS_A1_RUN.md: build + live run (call-endpoint-never-serve) + resume + aggregate/escalation/review + results + baseline comparison + gating. Commands verified.
- Next step 8 (FINAL): tests/test_m13_larger_run.py, then M13 DONE.

## M13 Larger run — Iteration M13.8 (2026-07-09 01:00 EDT) — step 8 COMPLETE → M13 DONE
- tests/test_m13_larger_run.py 4/4 pass; full suite green (40 tests). All M13 deliverables: generator+110-task batch, run config, LIVE 110-task run (escalation 0.164 vs 0.28 baseline, 0 failures, JSON fix validated), aggregate+escalation queue, reviewed subset (agreement n=1 rate 0.0), baseline comparison, doc, tests. Private never staged; auto candidate; production gated. M13 STOP CONDITION MET.
- NEXT per steer M14: A calibration / B broaden / C label converters / D verifier coverage (numeric-tolerant exact-match + open-ended explain — motivated by the M13 exact-match finding).

## M14 Verifier coverage — Iteration M14.1 (2026-07-09 01:16 EDT) — step 1 COMPLETE (numeric verifier)
- New M14 loop prompt installed (numeric-tolerant + explain rubric) via /prompt-master. steer.md synced post-M13 (db01298).
- src/verifiers.py: numeric_tolerant_check (all-number extract + unit norm + abs/rel tolerance + accepted_values; hashed evidence). Fixes #87 exact-match numeric strictness. 7 cases verified incl speed-of-light PASS; exact_answer_match unchanged; registered.
- Next step 2: explain_rubric_check (rubric-only, escalate on weak/absent coverage).

## M14 Verifier coverage — Iteration M14.2 (2026-07-09 01:22 EDT) — step 2 COMPLETE (explain rubric)
- src/verifiers.py: explain_rubric_check (rubric-only fact checklist; PASS at full coverage; escalate on weak/absent rubric; never gold without rubric). 5 cases verified; registered. Full suite green.
- Next step 3: route numeric tasks → numeric_tolerant_check + explain-rubric tasks → explain_rubric_check; add both to CORRECTNESS.

## M14 Verifier coverage — Iteration M14.3 (2026-07-09 01:26 EDT) — step 3 COMPLETE (routing + CORRECTNESS)
- _run_verifiers routes numeric→numeric_tolerant_check, required_facts→explain_rubric_check; exact_answer_match skips numeric (kept for pure strings). Both new verifiers added to CORRECTNESS (escalation math unchanged). Routing verified 3 ways; suite green.
- Next step 4: public numeric/rubric fixture rows + metadata; verify routing.

## M14 Verifier coverage — Iteration M14.4 (2026-07-09 01:29 EDT) — step 4 COMPLETE (public numeric/rubric fixture)
- data/prompts/agents_a1_numeric_batch.jsonl: 4 numeric (metadata numeric/expected_value/tolerance/rel_tolerance/expected_units) + 2 explain-rubric (required_facts). All route correctly (numeric→numeric_tolerant_check, rubric→explain_rubric_check). Public, tracked.
- Next step 5: before/after showing the numeric verifier flips the M13 speed-of-light false-positive.

## M14 Verifier coverage — Iteration M14.5 (2026-07-09 01:33 EDT) — step 5 COMPLETE (numeric before/after)
- Public agents_a1_numeric_beforeafter_sample.json: old exact_answer_match fail → new numeric_tolerant_check pass; numeric row flips wrong→ok + de-escalates. M13 finding fixed. commit-safe.
- Next step 6: docs/M14_VERIFIER_COVERAGE.md.

## M14 Verifier coverage — Iteration M14.6 (2026-07-09 01:37 EDT) — step 6 COMPLETE (doc)
- docs/M14_VERIFIER_COVERAGE.md: numeric verifier + explain rubric + routing + metadata-field table + before/after + gating.
- Next step 7 (FINAL): tests (numeric/exact/routing/rubric/before-after), then M14 DONE.

## M14 Verifier coverage — Iteration M14.7 (2026-07-09 01:40 EDT) — step 7 COMPLETE → M14 DONE
- tests/test_numeric_verifier.py 5/5 pass; full suite green (45 tests). All M14 deliverables: numeric_tolerant_check + explain_rubric_check, routing + CORRECTNESS wiring, public numeric/rubric fixture, before/after flip, doc, tests. exact_answer_match unchanged; escalation math unchanged; auto candidate; production gated. M14 STOP CONDITION MET.
- NEXT per steer M15: A larger run 250-500 / B calibration / C label converters / D retrieval+checker actions.

## M15 Larger run — Iteration M15.1 (2026-07-09 01:56 EDT) — step 1 COMPLETE (261-task batch)
- New M15 loop prompt installed (250-500 live run; call-endpoint-never-serve; two-baseline comparison) via /prompt-master. steer.md synced post-M14 (6ca7663).
- src/gen_m15_batch.py → data/prompts/agents_a1_m15_batch.jsonl: 261 tasks (math160/exact20/numeric20/json10/regex8/current10/explain18/rubric15), unique, deterministic, numeric+rubric route correctly.
- Next step 2: config/agents_a1_m15_run.json (agents-a1 endpoint, batch 300/cap 500).

## M15 Larger run — Iteration M15.2 (2026-07-09 02:02 EDT) — step 2 COMPLETE (run config)
- config/agents_a1_m15_run.json: agents-a1 endpoint, batch 300/cap 500, numeric+rubric verifiers enabled, 1 call/task (261 calls). run_id stable; private paths gitignored.
- Next step 3: LIVE 261-task run against agents-a1 on fred (background + poll).

## M15 Larger run — Iteration M15.3 (2026-07-09 02:12 EDT) — step 3 COMPLETE (LIVE 261-task run)
- LIVE agents-a1 run run_id 25ca35429474c407: 261/261 completed, 0 failed, telemetry_missing 261, escalated 19 (rate 0.073 vs M13 0.164 vs M11 0.28), auto_was_wrong 1. json auto_wrong=0 + numeric auto_wrong=0 → BOTH fixes hold at scale. explain 17/18 escalated (unverifiable); rubric 1 weak-coverage; exact 1 miss. Records valid, human-null, private unstaged.
- Next step 4: aggregate report (public) + escalation queue (gitignored).

## M15 Larger run — Iteration M15.4 (2026-07-09 02:14 EDT) — step 4 COMPLETE (aggregate + escalation queue)
- Public agents_a1_m15_summary_sample.json: 261 completed, ok231/wrong1/undecided29, escalation 19 (0.0728), verifier dist all 7 (numeric 20, rubric 15), agreement null. Escalation queue gitignored (19/261, human-null). No text; commit-safe.
- Next step 5: review a representative escalated subset (objective) → public reviewed-subset summary.

## M15 Larger run — Iteration M15.5 (2026-07-09 02:16 EDT) — step 5 COMPLETE (reviewed subset)
- Reviewed representative 6/19 escalated (objective) → gitignored subset + public agents_a1_m15_reviewed_subset_sample.json: human_reviewed_count 6, agreement n=1 rate 0.0. m15_e_019 = task-metadata gap (string speed-of-light lacks numeric metadata → exact_answer_match strict; numeric-tagged version passed). m15_k_003 rubric escalated on synonym (interaction vs force) — as designed, not wrong. No text; commit-safe.
- Next step 6: M15-vs-BOTH-baselines comparison report.

## M15 Larger run — Iteration M15.6 (2026-07-09 02:18 EDT) — step 6 COMPLETE (two-baseline comparison)
- Public agents_a1_m15_vs_baseline.json: escalation trend [0.28, 0.164, 0.073] monotonic across M11/M12→M13→M15 at 25→110→261 tasks; JSON+numeric fixes held (0 auto_wrong each at scale); single M15 auto_wrong = task-metadata gap. No text; commit-safe.
- Next step 7: docs/M15_LARGER_AGENTS_A1_RUN.md.

## M15 Larger run — Iteration M15.7 (2026-07-09 02:20 EDT) — step 7 COMPLETE (run doc)
- docs/M15_LARGER_AGENTS_A1_RUN.md: build + live run + resume + aggregate/escalation/review + two-baseline comparison + results + gating. Commands verified.
- Next step 8 (FINAL): tests/test_m15_larger_run.py, then M15 DONE.

## M15 Larger run — Iteration M15.8 (2026-07-09 02:24 EDT) — step 8 COMPLETE → M15 DONE
- tests/test_m15_larger_run.py 4/4 pass; full suite green (49 tests). All M15 deliverables: generator + 261-task batch, run config, LIVE 261-task run (escalation 0.073, 0 failed, both fixes hold), aggregate + escalation queue, reviewed subset (agreement n=1), two-baseline comparison (trend 0.28→0.164→0.073), doc, tests. Private never staged; auto candidate; production gated. M15 STOP CONDITION MET.
- NEXT per steer M16: A calibration / B retrieval+checker actions / C label converters / D broader model comparison. MOTIVATED FIXTURE FIX: tag numeric-answer exact rows with numeric metadata (M15 task-metadata gap).

## M16 Action routing — Iteration M16.1 (2026-07-09 02:28 EDT) — step 1 COMPLETE (metadata validator)
- New M16 loop prompt installed (action routing + metadata cleanup; read-only actions) via /prompt-master. steer.md synced post-M15 (afca8b9).
- src/validate_task_metadata.py: flags numeric-looking exact rows missing numeric metadata (7 in M15 batch incl speed-of-light) + json/numeric sanity. Exits nonzero on issues.
- Next step 2: generator metadata-normalization → tag numeric exact rows; regenerate M15 batch; validator zero gaps.

## M16 Action routing — Iteration M16.2 (2026-07-09 02:34 EDT) — step 2 COMPLETE (generator normalization)
- gen_m13_batch.normalize_numeric_metadata applied in both generators; regenerated M15+M13 batches. Validator zero gaps; 7 exact→numeric (exact 20→13, numeric 20→27); speed-of-light routes to numeric_tolerant_check; deterministic, 261. Suite green.
- Next step 3: schema/action_record_v1.json.

## M16 Action routing — Iteration M16.3 (2026-07-09 02:36 EDT) — step 3 COMPLETE (action_record schema)
- schema/action_record_v1.json: draft-07, separate from frozen; action_type/status enums, no raw-text field. 6 validation behaviors verified.
- Next step 4: src/action_router.py (read-only; retrieval/checker(approved)/review/no_action).

## M16 Action routing — Iteration M16.4 (2026-07-09 02:38 EDT) — step 4 COMPLETE (action router)
- src/action_router.py: read-only; retrieval_needed/checker_needed(approved-only,else skipped)/review_needed/no_action; hashed evidence, no raw text. 5 cases verified + schema-valid.
- Next step 5: before/after metadata-cleanup report (exact→numeric move + speed-of-light flip).

## M16 Action routing — Iteration M16.5 (2026-07-09 02:41 EDT) — step 5 COMPLETE (before/after metadata)
- Public agents_a1_m16_metadata_beforeafter_sample.json: 7 reused exact rows newly tagged exact→numeric; speed-of-light flips fail→pass, de-escalates. Honest count (excluded already-numeric pool). No text; commit-safe.
- Next step 6: action-routing summary over the M15 run log.

## M16 Action routing — Iteration M16.6 (2026-07-09 02:44 EDT) — step 6 COMPLETE (action summary)
- Public agents_a1_m16_action_summary_sample.json over M15 run (read-only, all planned): checker_needed 160 (approved), no_action 70, review_needed 19, retrieval_needed 12 (current-info → retrieval record). No text; commit-safe; private unstaged.
- Next step 7: docs/M16_ACTION_ROUTING.md.

## M16 Action routing — Iteration M16.7 (2026-07-09 02:46 EDT) — step 7 COMPLETE (doc)
- docs/M16_ACTION_ROUTING.md: metadata validator+normalization, action_record schema, read-only router rules table + M15 distribution, gating. Commands verified.
- Next step 8 (FINAL): tests/test_action_routing.py, then M16 DONE.

## M16 Action routing — Iteration M16.8 (2026-07-09 02:50 EDT) — step 8 COMPLETE → M16 DONE
- tests/test_action_routing.py 5/5 pass; full suite green (54 tests). All M16 deliverables: metadata validator, generator normalization (7 exact→numeric, zero gaps), action_record_v1 schema, read-only action_router, before/after metadata report, action-routing summary, doc, tests. Actions read-only/planned; auto candidate; production gated. M16 STOP CONDITION MET.
- NEXT per steer M17: A calibration / B 500-task run w/ action routing / C label converters / D broader model comparison.

## M17 Reviewed calibration — Iteration M17.1 (2026-07-09 03:04 EDT) — step 1 COMPLETE (calibration report)
- New M17 loop prompt installed (reviewed calibration; reporting-only) via /prompt-master. steer.md synced post-M16 (6a5c513).
- src/reviewed_calibration_report.py: category-level over M11-M16 reviewed logs (read locally). 44 scanned/19 reviewed/3 comparable. exact+regex agreement 0.0 (the fixed false-positives); open-explain verifier_gap; rubric needs_more_review. Action planned-only counts folded in. No-text guard + guard clean.
- Next step 2: commit the summary artifact (verify no-text + commit-safe).

## M17 Reviewed calibration — Iteration M17.2 (2026-07-09 03:10 EDT) — step 2 COMPLETE (committed summary)
- Public agents_a1_reviewed_calibration_summary.json committed: category-level reviewed/comparable/agreement, fixed_findings, remaining_gaps, action planned-only. No-text guard + leak grep clean; commit-safe; private unstaged.
- Next step 3: docs/M17_REVIEWED_CALIBRATION.md.

## M17 Reviewed calibration — Iteration M17.3 (2026-07-09 03:13 EDT) — step 3 COMPLETE (doc)
- docs/M17_REVIEWED_CALIBRATION.md: category table + agreement, fixed false-positives, category maturity (usable_shadow/needs_more_review/verifier_gap), action planned-only, gating.
- Next step 4 (FINAL): tests/test_reviewed_calibration.py, then M17 DONE.

## M17 Reviewed calibration — Iteration M17.4 (2026-07-09 03:16 EDT) — step 4 COMPLETE → M17 DONE
- tests/test_reviewed_calibration.py 4/4 pass; full suite green (58 tests). All M17 deliverables: reviewed_calibration_report, committed public summary (category-level, agreement-where-comparable, fixed findings + gaps, action planned-only), doc, tests. Private reviewed logs never staged; auto candidate; production gated. M17 STOP CONDITION MET.
- NEXT per steer M18: A 500-task run w/ action routing / B retrieval+checker execution / C label converters / D broader model comparison.

## M17 Reviewed calibration — Post-completion bugfix (2026-07-09 23:27 EDT)
- Fixed KeyError in reviewed_calibration_report.py main() (stale total_reviewed_records
  reference from the step-1 honesty rename). CLI verified clean; regenerated output
  byte-identical to committed artifact (no data change). Full suite 58/58 green.

## M18 Safe action execution (2026-07-09) — MILESTONE COMPLETE
- Added `schema/action_result_v1.json`: aggregate-safe results linked to M16
  action records; fixed enums/confidence/hashes only, `candidate_only=true`, no
  raw task/output/retrieved context.
- Added `src/action_executor.py`: execution is disabled by default; explicit
  `--execute` enables only fixture/public-fixture retrieval and the allowlisted
  deterministic checkers (`math_checker`, `json_object_check`,
  `numeric_tolerant_check`). No shell/subprocess/dynamic command surface.
- Replayed the M15/M16 distribution: 261 planned -> 172 completed (12 retrieval,
  160 checker) + 89 intentionally skipped (19 review, 70 no-action). All 12
  retrievals reached an executable fixture path and still require grounded
  regeneration.
- Honest limitation: M15 retained only truncated output previews. Checker replay
  is 70 pass/90 fail but explicitly marked invalid for correctness measurement;
  a future live run must pass full output transiently before logging/truncation.
- Added public aggregate summary + M18 doc + 6 safety tests covering default-off,
  retrieval, checker allowlisting, malicious-command refusal, schema/no-text,
  and planned-vs-executed comparison. Full suite 64/64 green; production remains
  gated.

## M19 Live full-output action run (2026-07-09) — MILESTONE COMPLETE
- Built deterministic, metadata-clean 500-task batch + explicit-opt-in M19 live
  config. Endpoint `agents-a1` was already served; runner only called it.
- Added transient full-output return path in the supervisor and integrated the
  M18 executor into the resumable batch runner. Full output reaches approved
  checkers before truncation but is never persisted; resume requires paired
  runtime/action-result ids.
- Live run `c20512612a978d60`: 500/500 complete, 0 failed, 27 escalated (0.054
  vs M15 0.0728), telemetry_missing 500, policy null 500.
- 383/500 actions completed: 360 full-output math checks + 23 fixture retrievals;
  117 review/no-action records intentionally skipped. Checker results are now
  valid for execution input: 356 pass / 4 fail (real arithmetic miss candidates),
  replacing M18's invalid truncated-preview split.
- Current-info separated honestly: 20/20 fixture retrieval paths completed;
  3 non-current heuristic false positives (2 explain weather rows, 1 numeric
  sale-price row). All 20 still require grounded regeneration.
- Added three aggregate reports, M19 doc, and 6 CPU/no-network tests for batch,
  transient/no-persistence, explicit opt-in, safe retrieval, aggregation,
  current-info separation, and resume. Candidate-only; production gated.

## M20 Grounded regeneration after retrieval (2026-07-09) — MILESTONE COMPLETE
- Added aggregate-safe `grounded_result_v1` + explicit-opt-in
  `grounded_regenerator.py`. Only completed retrieval actions for true
  current_info tasks may call the local model; fixture context + grounded output
  remain transient and hashes/enums only persist.
- Controlled live run processed 23 M19 retrieval candidates: 20/20 true
  current-info tasks produced changed grounded answers; 3 reviewed non-current
  false positives skipped before any model call.
- All 20 grounded answers were deterministically checked against a controlled
  fixture expected token: 4 pass / 16 fail (match rate 0.20). This proves the
  second-pass path but exposes generic-context quality limits; it is not
  real-world correctness. Follow-up remains on 19 rows (16 fail + 3 skip).
- Public review summary confirms all 4 M19 arithmetic miss candidates against
  deterministic metadata and all 3 retrieval heuristic false positives; zero
  gold promotions. Freshness regex refined so bare weather/price/stock/news no
  longer trigger non-current tasks; explicit current_info still routes.
- Added public grounded + review summaries, M20 doc, summary-only rebuild mode,
  and 6 safety/report tests. Full suite 76/76 green; production remains gated.

## M21 HF/safetensors telemetry backend (2026-07-10) — MILESTONE COMPLETE
- Added versioned aggregate-safe `hf_telemetry_record_v1` and backend descriptors
  separating GGUF runtime (`telemetry_access=missing`) from HF/safetensors
  telemetry. Existing GGUF supervisor remains unchanged.
- Added no-download loader contract: existing local safetensors directory or
  explicitly approved cached model ID only; Transformers always receives
  local_files_only=true + trust_remote_code=false. No model selected/downloaded,
  no weights loaded.
- Added aggregate logits/decode telemetry (entropy, selected probability/token,
  top-k mass/margin, window counts/trend), optional hidden summaries, and honest
  router states/features (available/not_moe/missing/unsupported; never inferred).
- Tiny fake batch: 3 schema-valid records; logits available2/missing1;
  hidden available1/disabled1/missing1; router available1/not_moe1/missing1;
  weights_loaded=0. Outcome-id alignment flags cover auto/action/grounded.
- Added public fixture aggregate, M21 doc, and 8 tests including no-download
  flags, missing/not-MoE handling, no raw text/tensors, schema validation, and
  no tracked model weights. Production remains gated.

## M22 real HF MoE telemetry validation (2026-07-10) — MILESTONE COMPLETE
- Operator approved MoE, model selection, GPU-first execution, and Thor storage.
  Selected public Qwen1.5-MoE-A2.7B-Chat (`qwen2_moe`) because its 14.3B total /
  2.7B active size fits BF16 across the two 3090s without CPU/disk offload.
- Downloaded approximately 27 GiB to the Thor mount outside the repository.
  Loader resolved the local safetensors directory with local_files_only=true and
  trust_remote_code=false. No weight/cache/path is tracked.
- Temporarily unloaded llama-swap, loaded BF16 with a 20 GiB/GPU cap, and captured
  8 shared M19 task IDs × 4 decode steps. All 8 expose real 24-layer × 60-expert
  router output; logits 8/8 available, router 8/8 available, hidden disabled 8/8.
  Restored agents-a1 and verified a live response plus prior dual-GPU residency.
- Added precomputed-scalar conversion so full vocabulary logits need not persist;
  raw router tensors/text remain in ignored captures. Eight schema-valid detailed
  records remain private. Public artifacts contain aggregate groups only.
- Alignment coverage: auto8/action8/grounded1/reviewed1. Checker-needed mean decode
  entropy 0.6767 vs 1.3162 not-needed, while router entropy was 3.4300 vs 3.4277.
  These labels came from agents-a1 on shared IDs, so this is cross-model task-demand
  alignment, not Qwen error prediction. Retrieval/review have n=1 positives; no
  predictive-value claim. Production gated.
- Added M22 adapter/reporting, docs, and CPU fixture tests. Full suite green:
  89/89 tests.

## M23 within-model telemetry/outcome validation (2026-07-10) — MILESTONE COMPLETE
- Predeclared a fixed 32-task public-ID manifest before inspecting M23 telemetry:
  checker8/retrieval8/review8/no-action8. Features/comparisons were frozen in code.
- Added chat-template capture and private decoded-output retention. The same Qwen
  capture now supplies real logits/router telemetry and the output passed to the
  existing supervisor, verifiers, router, and allowlisted executor; no cross-model
  label source remains. Detailed text/tensors stay ignored.
- Real dual-3090 BF16 run completed 32/32 with logits and 24-layer × 60-expert
  router telemetry available for every row; hidden disabled. Actual action split
  exactly matched 8/8/8/8. Checkers: 7 pass/1 fail; retrieval fixture paths 8/8.
- Nine prose rows hit the 64-token cap (retrieval3/review6); every checker reached
  EOS first. Capped rows are not claimed as complete answers, and their metadata-
  driven retrieval/review labels remain valid for routing analysis.
- Descriptive separation: checker router entropy g=+1.896 and concentration
  g=-1.932; retrieval router entropy g=-1.370/concentration g=+1.276; review router
  entropy g=-1.017/concentration g=+0.892. Fixed-seed bootstrap intervals exclude
  zero for those selected effects, but task category/output length remain confounds.
- Checker fail/pass effects withheld honestly (n=1/7, minimum 4/group). No policy,
  threshold, causal, or predictive-value claim. agents-a1 serving restored/verified.
- Added public aggregate summary/alignment report, M23 doc, and CPU/no-network tests.
  Full suite green: 95/95 tests. Production gated.

## M24 frozen telemetry holdout (2026-07-10) — MILESTONE COMPLETE
- Preregistered a 48-ID manifest, caught 12 unavailable source IDs before capture,
  preserved the invalid commit, and transparently corrected to 40 valid/disjoint
  IDs (10/class) before model load. Frozen features/classifiers/metrics unchanged.
- Fit full/logits/router nearest-centroid models only on 32 private M23 rows:
  M23 mean/sample-SD scaling, balanced class centroids, squared Euclidean distance,
  lexical ties. Classifiers instantiated before any M24 capture was loaded.
- Real same-model holdout completed 40/40; logits/router available 40/40, hidden
  disabled. Actual routes checker10/retrieval10/review11/no-action9. Eighteen rows
  hit 64 tokens (retrieval7/review10/control1); no checker was capped.
- Frozen holdout: router-only accuracy 0.700 [0.550,0.850], balanced accuracy
  0.693, macro-F1 0.700; full 0.600 [0.450,0.750]; logits-only 0.225
  [0.100,0.350]; actual majority baseline 0.275. No holdout tuning occurred.
- Router-only recall: checker .80/no-action .44/retrieval .80/review .73. Main
  confusions are no-action→review (5) and review→retrieval (3). Category/template
  confounds remain; result supports investigation, not a policy.
- Qwen checker outcomes shifted to 1 pass/9 fail, all EOS-complete. No error
  predictor was fit. agents-a1 serving restored and verified. Production gated.
- Added public aggregate summary/evaluation, M24 doc, and CPU tests. Full suite
  green: 100/100 tests.

## M25 identical-input router falsification (2026-07-10) — MILESTONE COMPLETE
- Preregistered 16 synthetic ID/pair/action groups, then generated 32 private tasks
  with byte-identical prompts inside each pair. Eight pairs varied checker vs
  no-action metadata; eight varied retrieval vs review metadata.
- Applied only the frozen M23 router-only classifier (router entropy/concentration),
  with no refit/scaling/threshold/feature update. Same local Qwen/hardware plan.
- Real run completed 32/32; logits/router available 32/32, hidden disabled. Actual
  action distribution exactly balanced 8/class and matched intended labels 32/32.
  All 8 arithmetic checks passed/EOS; all 16 topic members hit the symmetric cap.
- Decisive pair result: actual labels discordant16/16, outputs identical16/16,
  predictions identical16/16, divergence rate0. Both router-feature mean/max
  absolute differences are exactly0 across stored aggregates.
- Frozen router accuracy .500 [0.3125,0.6875], balanced accuracy .500, macro-F1
  .413 vs majority .250. Checker recall1/no-action0; identical input cannot expose
  metadata-only label changes. M24 .70 was substantially template/category signal.
- Conclusion: telemetry-only action routing is not supported. Future work must
  either explicitly include trusted task metadata or study balanced within-category
  objective errors. No policy/threshold; production gated. agents-a1 restored.
- Added public aggregate pair/run reports, M25 doc, and CPU tests. Full suite green:
  105/105 tests.

## M26 objective error dataset (2026-07-10) — MILESTONE COMPLETE
- Operator selected steer option B (objective error prediction) via the loop
  contract. Preregistered data/prompts/m26_error_manifest.json before any task
  generation: one arithmetic category/template, four difficulty bands (24 each),
  per-ID 16/8 train/holdout split, deterministic seeded generation with no
  post-hoc selection, math_checker label rule, constant checker applicability,
  holdout seal, and frozen M27/M28 protocols.
- Deterministic generator produced 96 unique private tasks; one GPU window
  captured 96/96 with logits + 24-layer × 60-expert router telemetry (BF16,
  chat template, greedy, 64-token cap, router-only, ~1 s/task). agents-a1
  restored and verified after the window.
- Action applicability held constant: 96/96 actual actions checker_needed. No
  train row hit the decode cap; 0 undecided verdicts.
- Train labels (holdout sealed until M27): band_a 16 pass, band_b 16 pass,
  band_c 13 pass/3 fail, band_d 1 pass/15 fail → 46 pass/18 fail, meeting the
  predeclared ≥8/≥8 modeling minimum without reselection.
- Train fail-vs-pass descriptive separation: decode entropy g≈+3.0,
  high-entropy count g≈+2.4, expert concentration g≈+1.9, router entropy
  g≈-1.9, low-confidence count g≈+1.6, margin trend g≈-1.2 (band confound
  explicit; no classifier/threshold fitted).
- Public artifacts aggregate-only (manifest, run summary, telemetry summary);
  commit-safe check passed; private tasks/captures/records/labels gitignored.
  Full suite green: 123 tests. Production gated. Next: frozen M27 evaluation.

## M27 frozen holdout error prediction (2026-07-10) — MILESTONE COMPLETE
- Evaluated the sealed 32-task holdout (9 fail/23 pass, 0 undecided) exactly
  once under the protocol frozen in the M26 manifest: train-standardized
  nearest centroid fit on 64 train rows, six predeclared baselines, fixed-seed
  bootstrap CIs, no refit/tuning after reading holdout rows.
- Results: majority .719; metadata_only (band shortcut) .969; logits_only .969
  (balanced .978, fail recall 1.0); router_only .812 (fail recall 1.0,
  precision .60); router_plus_logits .906; full_telemetry 1.000.
- Honest read: within-category telemetry predicts objective errors on a frozen
  holdout — logits-only matches the strong band shortcut with no metadata and
  catches a within-band fail the shortcut cannot see — but the increment over
  metadata is one task at n=32 with overlapping CIs; full_telemetry includes
  length/cap features correlated with band difficulty, and its [1.0,1.0]
  bootstrap is degenerate. No predictive-increment or production claim.
- Public artifacts aggregate-only (frozen holdout manifest + six-baseline
  evaluation); commit-safe passed; per-task predictions stay private/ignored.
  Full suite green: 123 tests. Production gated. Next: M28 ablation/calibration.

## M28 telemetry ablation and calibration (2026-07-10) — MILESTONE COMPLETE
- Ran the manifest-frozen ablation/calibration protocol (train-fit,
  holdout-eval, same centroid family). M28 is a decomposition of the
  already-read M27 holdout, flagged descriptive at n=32.
- Single-feature: high_entropy_count alone 1.000; decode_window_entropy .938;
  expert_concentration .844; decode_step_count .844; low_confidence_count
  .844; router_entropy .781; final-token confidence features .438 (below the
  .719 majority) and windowed_expert_shift .312. Error signal concentrates in
  decode-window entropy behavior, not final-token confidence or router shift.
- Leave-one-out: max drop +.031 — features heavily redundant, none load-bearing.
- Calibration: softmax-distance p(fail), 4 equal-count bins, ECE .004 with
  saturated scores (dataset separability, not general calibration quality).
- FP/FN by band: full model has 0 errors in every band; feature-level over-
  and under-flagging documented instead.
- Threshold proposal p(fail) ≥ 0.95 derived from train only, marked
  candidate-only/not-for-production throughout; no production threshold set.
- Public report aggregate-only; commit-safe passed; full suite green: 123
  tests. Production gated. Autoloop limit (M26–M28) reached — stopping.

## M29 scaled objective error prediction power test (2026-07-10) — MILESTONE COMPLETE
- Operator selected option A. Preregistered data/prompts/m29_power_manifest.json
  before generation: 384 tasks across six boundary-spanning multiplication
  bands, sealed 192/96/96 train/validation/holdout split, seven frozen
  baselines (incl. metadata+telemetry and the M28-motivated window_entropy
  set), paired-bootstrap incremental-value rule, validation-only thresholds,
  power minimums. M27 holdout not reused.
- One GPU window captured 384/384 (~1 s/task); agents-a1 restored/verified.
  All 384 actions checker_needed; 0 undecided; 0 capped. Labels: train 106
  fail/86 pass, validation 54/42, holdout 51/45 — every power minimum met.
- Holdout (n=96, read once): majority .531; metadata_only .823; logits_only
  .854; router_only .750; window_entropy .833; full_telemetry .885
  [.823,.948]; metadata_plus_telemetry .865.
- Predeclared increment test: full−metadata +.063 [−.021,+.146] (12 wins/6
  losses), meta+tel−metadata +.042 [−.031,+.115], window−metadata +.010 —
  all intervals include zero → telemetry increment NOT established at n=96,
  reported honestly per the claim rule.
- Established instead: M28's perfect single-feature score was a band-
  separability artifact (window_entropy .833 here); telemetry and metadata
  err differently (metadata over-flags .961 recall/.766 precision; logits
  under-flag .784/.930); band metadata adds nothing once telemetry is present
  (.865 < .885); calibration degrades off easy/hard splits (ECE .059/.117),
  thresholds candidate-only. Decisive test needs holdout n≈200.
- Public artifacts aggregate-only; commit-safe passed; full suite green: 130
  tests. Production gated.

## M30 decisive telemetry increment test (2026-07-10) — MILESTONE COMPLETE
- Executed the operator-preregistered decisive protocol (steer 2a4699e):
  768 fresh tasks (six bands × 128, sealed 384/192/192 split), operand tuples
  deterministically disjoint from M29, same M29 centroid family, primary
  confirmatory comparison full_telemetry vs metadata_only with the
  established/not-established/negative rule fixed before generation.
- One GPU window captured 768/768 (~1 s/task); agents-a1 restored/verified.
  All 768 actions checker_needed; 0 undecided; 0 capped. Labels: train 210
  fail/174 pass, validation 105/87, holdout 103/89 — every power minimum met.
- Once-read n=192 holdout: majority .536; metadata_only .818; logits_only
  .854; router_only .833; window_entropy .849; full_telemetry .917
  [.875,.953]; metadata_plus_telemetry .922.
- PRIMARY RESULT: full−metadata Δacc +.099, 95% CI [+.042,+.156]; Δbacc CI
  [+.050,+.165]; 27 metadata errors corrected vs 8 introduced. Verdict under
  the preregistered rule: ESTABLISHED. Secondary: meta+tel +.104 [+.057,
  +.156]; window_entropy alone +.031 [−.042,+.104] (not sufficient alone).
- Calibration: ECE .032 (full, thr .50) / .043 (meta+tel, thr .75), holdout
  bacc at threshold .916/.938 — all candidate-only; no production threshold.
- Scope: one category, one model, one decode protocol; no transfer/causal/
  production claim. Public artifacts aggregate-only; commit-safe passed; full
  suite green: 136 tests. Next per operator Branch 1: M31 telemetry-triggered
  intervention study.

## M31 telemetry-triggered intervention study (2026-07-10) — MILESTONE COMPLETE
- Preregistered manifest before generation: 192 fresh tasks (M29/M30-disjoint
  operands), frozen M30 full_telemetry score (refit verified against the
  published M30 confusion matrix, threshold .50), seeded temperature-0.7
  single-retry protocol (opt-in capture-script sampling; greedy path
  unchanged), four replace-on-retry policies, paired-delta metrics with a
  fixed useful/harmful/not-established rule.
- One GPU window: 192 greedy + 192 sampled captures; agents-a1 restored and
  verified. 192/192 checker_needed; 0 undecided; 0 capped. Original 90
  pass/102 fail; retry 89 pass/103 fail; trigger rate .516.
- Policies: no_retry .469; always_retry .464 (90 false alarms, 7 introduced);
  random_retry .458; telemetry_triggered .474 (11 false alarms, 4 rescued, 3
  introduced). Deltas: vs no_retry +.005 [−.021,+.031]; vs random +.016
  [−.010,+.042]. VERDICT: NOT ESTABLISHED.
- Decomposition: the trigger replicated (~89% of triggered retries hit real
  failures, third consecutive fresh set); the repair operator is the
  bottleneck — a temperature resample rescues only ~4.5% of triggered
  failures because these errors are systematic, not stochastic. Telemetry
  gating was the only non-losing policy. 4 verified recovery traces written
  (private, gitignored) — too few for training use.
- Implication recorded for the next gate: keep the frozen trigger, replace
  the repair operator (checker-guided/decomposition regeneration or tools).
- Public artifacts aggregate-only; commit-safe passed; full suite green: 143
  tests. Production gated. Autoloop: M30+M31 = 2 of 3 authorized milestones;
  the branch-appropriate third milestone depends on an operator decision, so
  stopping at the post-M31 gate.

## M32 structured repair — SUPERSEDED BEFORE EXECUTION (2026-07-10)
- The M32 structured-repair bakeoff was preregistered (5f0edfe) and its
  implementation/tests written; the staged capture driver had produced only
  partial private originals when operator steer 9aaded9 superseded the
  milestone before any result inspection. The in-flight capture was killed
  and all partial private captures deleted; nothing was processed, labeled,
  or evaluated. Per the supersession notice the manifest, module, and tests
  are preserved as historical artifacts and must not be run or reported as
  evidence. agents-a1 serving is unaffected.

## M32R counterfactual expert routing — PHASE-0 GATE FAILED, STOPPED (2026-07-10)
- Operator protocol docs/M32R_AGENTS_A1_COUNTERFACTUAL_ROUTING_AUTOLOOP.md
  (e68bef0/9aaded9): Agents-A1 HF safetensors research load under a hard
  44 GiB dual-3090 ceiling, route-override hooks, counterfactual expert
  screen. Phase 0 (loader feasibility) precedes preregistration.
- Config-only audit (no weights downloaded): InternScience/Agents-A1 is
  qwen3_5_moe, 40 layers/256 experts/top-8, 34.66B params with 32.21B (93%)
  in fused 3D expert tensors that bitsandbytes cannot quantize → NF4-mixed
  estimate 61.9 GiB and BF16 64.6 GiB, both far over the 44 GiB gate. This
  reproduces the iteration-8 Qwen3.6-35B-A3B audit exactly.
- InternScience/Agents-A1-FP8 is compressed-tensors; the package is not in
  the approved stack (new-dependency gate) and Ampere sm86 has no FP8 kernel
  path, so the installed loader cannot run it within the ceiling.
- Verdict: BRANCH 4 (resource/loader failure) — stopped before any
  preregistration, generation, or capture, per protocol. Public feasibility
  report: reports/telemetry/hf_m32r_feasibility_gate.json (aggregate only).
  Unblock options recorded for the operator. Full suite green: 151 tests.

## M32P proxy counterfactual expert routing (2026-07-10) — MILESTONE COMPLETE
- Executed the operator's amended model-calibrated protocol (35b12c3) with
  separate hook/calibration/preregistration/result commits.
- Phase 0A: route-override hook on the qwen2_moe TopKRouter (last-row logit
  editing, model's own selection arithmetic, bit-identical when disabled);
  6 CPU tests on a tiny real qwen2_moe; real smoke passed (parity, forced
  swap changes routing, peak 27.95 GiB).
- Phase 0B: predeclared 288-row calibration sweep mapped the proxy frontier —
  carry structure dominates difficulty (2x2 .96 low/.42 heavy; 3x2 .83/.04;
  4x2 .71/.00; middle-zero .375; near-pow10 .667). Frozen rules chose N=192:
  4 boundary cells x36 + easy/hard anchors x12; expected failures 90.
- Decision run (34 min, peak 28.3 GiB): realized failures 41/18/21 met all
  power minimums; 0 undecided. Frozen M30 trigger degraded on the frontier
  distribution (precision .766, recall .738 vs ~.89 band-based) — reported,
  not tuned. 7,204 one-step screens; 616 full branched continuations with
  equal heuristic/random budgets.
- VERDICTS: H1 route recoverability NOT ESTABLISHED — sealed-holdout
  heuristic oracle rescue .125 vs matched-random .125, paired CI [0,0];
  oracle-recoverable fraction 11.9%. Route families rescue at random-noise
  rates and regress more than they rescue (heuristic 17/32 vs random 21/32
  in 308 continuations each). H2 NOT ESTABLISHED — frozen policy .5625 =
  normal .5625 = random .5625. H3 — no soft-penalty candidate survived
  discovery. Proxy-scoped; nothing claimed about Agents-A1.
- Interpretation: systematic proxy multiplication failures are not caused by
  locally poor top-4 expert choices at fragile tokens; ~12% of failures are
  decode-path-sensitive to ANY equal-compute perturbation. Per Branch 3 the
  expert-routing track stops; remaining repair directions are structured
  prompting operators and telemetry-gated tools.
- Public artifacts aggregate-only; commit-safe passed; suite green: 166
  tests. agents-a1 restored/verified. Production gated.

## M32 structured repair (2026-07-11) — MILESTONE COMPLETE
- Capture interrupted by a power outage mid diagnose_stage_b and resumed via
  the idempotent capture driver (identical frozen prompts/settings); all six
  phases complete: 384 originals, 384 resample_t07, 203 each for
  independent_deliberate / checker_guided_repair / diag_a / diag_b.
- VERDICTS: H1 repair_not_established (bundle .0056 vs resample .0333 on 180
  triggered failures, delta CI [-.0556, 0]); H2 not_established (+.0026,
  CI [0, .0078] vs both no_repair and random trigger). Structured operators
  pass at ~0% while costing ~7x resample tokens. Verifier-first arms
  introduced zero errors (stop condition held).
- Frozen M30 trigger reproduced in-band: precision .900, recall .887.
  Deterministic tool ceiling .940 vs .471 no_repair (180/200 rescues, zero
  decode tokens). Model-side self-correction now negative across three
  operator families (M31 resample, M32P rerouting, M32 structured prompting).
- Secondary per-band descriptives (steer-required, non-confirmatory) show the
  detector weakest mid-frontier (band_3 precision .64) and strongest on hard
  bands (band_4/6 precision 1.0) — mirrors M32P off-distribution finding.
- External consult (Codex gpt-5.6-terra) reviewed the design pre-evaluation;
  its score-stratification concerns are answered by the band artifact and
  moot for uplift given ~0% operator pass rates.
- BRANCH DECISION (preregistered): model-side repair not improved + large tool
  ceiling → M33 telemetry-gated tool routing, remaining milestone for
  detector transfer/robustness. No self-correction claim.
- Public artifacts aggregate-only; check_commit_safe passed; 9 private
  recovery traces intentionally not committed; suite green: 168 tests.
  Production gated.

## M33 telemetry-gated tool routing (2026-07-11) — MILESTONE COMPLETE
- Executed preregistered Branch 3 of the M32 cluster: manifest predeclared
  (5bfaf46) before generation/capture; implementation a4c2440; steer c10190e.
- Fresh 384-task set (six bands, disjoint from M29-M32, regression-tested);
  single greedy originals GPU capture; frozen M30 gate at threshold 0.5.
- Reproduction gate PASSED: precision .902 / recall .889 (214 triggers).
- VERDICTS: H1 USEFUL — telemetry_trigger_tool .938 verified success vs
  no_repair .435 (CI [.453, .555]) and vs count-matched random .714
  (CI [.177, .271]). H2 EFFICIENT — uplift retention .889 (CI [.846, .929])
  at invocation fraction .557; 170/384 invocations saved. Zero errors
  introduced (verifier-first held in all arms).
- Framing: product/runtime routing evidence; no self-correction claim; no
  training data from tool outputs.
- Public artifacts aggregate-only; check_commit_safe passed; suite green:
  174 tests. Production gated.
- NEXT per Branch 3: M34 second-category detector transfer test (separate
  steer commit). Autoloop budget: M32, M33 done — one milestone remains.

## M34 second-category detector transfer (2026-07-11) — MILESTONE COMPLETE, AUTOLOOP STOPPED
- Executed preregistered protocol: manifest 7300b20 (predeclared before
  generation/capture), implementation 5220b32, steer 7b2e462. Fresh 384-task
  a*b+c set, (a,b) disjoint from M29-M33, c in [2,99] per band.
- Category shift collapsed the model: 18 pass / 366 fail (95.3% failure).
- VERDICT T1 = TRANSFER_FAILED: frozen-trigger recall .612 (precision .966 is
  trivial at 95% base rate); H1 not_established (telemetry .630 vs random
  .617, CI [-.060, .083]); H2 not_established (retention .612, invocation
  fraction .604). Zero errors introduced (verifier-first held).
- Interpretation: the detector is distribution-bound; selective gating only
  pays in the mixed-competence regime (M33). Near-total failure regimes want
  tool-on-every-task, not a gate.
- Bugfix during evaluation: top_k_mass float32 clamp at capture write + read
  (f747193, c84e054), regression-tested, no-op for prior milestones.
- Public artifacts aggregate-only; check_commit_safe passed; suite green:
  183 tests. Production gated.
- BOUNDED AUTOLOOP COMPLETE (M32, M33, M34). Loop STOPS per steer.md; any
  further milestone requires a fresh operator decision.

## M35 parallel tracks A/B/C (2026-07-11) — MILESTONE COMPLETE
- Campaign: 1536 tasks / six families / fail rates .041-.953; splits
  D 576 / R 288 / B-test 288 / A-test 384; each sealed set read exactly once
  in order; commits: manifest 47f4ed3 (+2ad210b amendment), impl 2ad210b,
  extraction 089de66/7ad320c, track B impl 864a44c, detector freeze 6b7e5fc
  (hash 8cb5e95f3adfc0c4), B-test 89c80d6, track A impl 9c07216, router
  freeze b7b86b3 (hash d2b9333c3c8da41f), A-test + report fb6e5cb.
- TRACK B: LOFO transfer holds for mul_carry/mul_add/mod_mul, fails for
  div_exact (.50 precision); no triggers on high-competence families.
  Pooled secondary: global .92/.82 best (finding 215).
- TRACK A: A-H1 not_established (router ≈ global threshold at matched
  budget, +.003 CI [0,.010]); A-H2 not_established ([-.079,-.035] vs -.05
  margin, 251/384 calls saved). Hierarchy redundant (finding 216).
- TRACK C: advisory-only shadow policy shipped (601fa3c) with audit-schema
  rollups; live smokes quantify the M34 recall collapse on real workloads.
- Strongest supported artifact: single global detector thresholded to
  budget — .94 verified success at ~35% tool calls (finding 217).
- Suite green: 205 tests; commit-safe passed on all staged reports;
  verifier-first held everywhere; production gated.
- NEXT per operator steer 31d702c: M36P — Agents-A1 AWQ INT4
  (cyankiwi/Agents-A1-AWQ-INT4) load/quality/telemetry preflight, then the
  three-arm raw-vs-jLens benchmark. Checkpoint download + compressed-tensors
  dependency authorized for the research venv only.

## M36P AWQ preflight (2026-07-11) — BLOCKED, operator decision required
- Checkpoint downloaded complete at pinned revision 3e522d4 (24.5 GB,
  authenticated aria2c per hf-download pattern); compressed-tensors 0.17.1
  installed in the research venv (with recovery from pip's silent torch
  upgrade — venv restored to system torch 2.5.1, suite re-verified green).
- BLOCKER (finding 218): transformers 5.13 qwen3_5_moe fused-expert
  DecompressExperts conversion is incompatible with the checkpoint's
  per-expert asymmetric INT4 modules — assertion failure + inherent
  BF16 decompression that cannot fit the 44 GiB gate.
- Recorded options: (A) different transformers/compressed-tensors pair that
  runs per-expert modules compressed (venv-churn risk to M22-M35 stack);
  (B) vLLM/SGLang only if router telemetry is exposed (else black-box arm);
  (C) different checkpoint identity — operator decides. No silent switch.
- GPUs freed; ollama/llama-server verified up. Suite 205 green.
