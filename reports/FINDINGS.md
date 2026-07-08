# jlens — Interpretability Sidecar for Qwen3.5/3.6 MoE: Findings to Date

Status: capture r3 (32 prompts) in flight. Findings below are from r2
(12 prompts, bf16, prefill-only, Qwen3.6-35B-A3B, 40 layers x 256 experts, top-k 8).

## 1. Capture pipeline (iterations 1–9)
- `src/capture_router_logits.py` captures per-layer router logits + hidden
  states on a 3090-class GPU via bf16 + CPU offload (`--max-gpu-mem-gib 20`,
  `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`). nf4 also supported.
- Prefill-only capture (`--max-new-tokens 0`) is sufficient for routing
  analysis and keeps runs cheap.
- Loader compatibility notes and VRAM behavior are logged in STATE.md.

## 2. Routing statistics (r2)
- Healthy load balancing: no collapsed/dead experts observed at prompt scale;
  aggregate routing entropy stays high (see `reports/qwen3_6_35b_a3b_routing.json`).
- Per-layer expert usage is broad but not uniform; a minority of experts take
  disproportionate traffic per domain.

## 3. Cross-domain expert overlap (iteration 10)
Tool: `src/expert_overlap.py` → `reports/qwen3_6_35b_a3b_overlap.json`.
8 domains: code_py, code_rust, creative, fact, json_tool, lang, math, reason.

- **Domains do NOT route to disjoint expert sets.** Mean pairwise Jaccard of
  per-layer top-8 expert sets: 0.29–0.43.
- Semantic neighbors cluster: math|reason J=0.431, code_py|code_rust J=0.422.
  Most distinct: fact|json_tool J=0.294.
- Depth terciles nearly flat (early 0.354 / mid 0.325 / late 0.363):
  specialization is distributed across the stack, slightly stronger mid-stack.
- Exclusive experts are real and skewed: lang=620 layer-slots (peak L39),
  math=560 (peak L12), reason=375, fact=346 — vs code_py only 54.
  Multilingual and math carve out the most private capacity.

## 4. Domain separability of routing signatures (iteration 11)
Tool: `src/routing_probe.py` → `reports/qwen3_6_35b_a3b_probe.json`.

- Logistic LOO probe at n=12 returned 0.000 accuracy — **invalid by
  construction**, not a negative result: 4/8 domains were singletons (absent
  from every LOO training fold), and n=12 vs 10240-dim features.
- Valid small-n test — cosine nearest-neighbor retrieval on full signatures:
  - retrieval@1 = 6/8 on two-sample domains
  - intra-domain cosine 0.552 vs inter-domain 0.374 (gap +0.178)
  - code_py ↔ code_rust are mutual nearest neighbors (0.591)
- **Conclusion:** routing signatures alone carry coarse domain identity.

## 5. Implications for the sidecar
1. A routing-based **domain-detection head is feasible** (cheap: reads router
   logits only, no hidden-state access needed).
2. **Expert-ablation domain surgery will have collateral damage** (~30–40%
   expert-set overlap between any two domains). Best ablation targets are the
   lang/math exclusive experts.
3. Depth-flat specialization means the sidecar should tap multiple layers,
   not just late stack.

## 6. Next steps
- [in flight] r3 capture: 32 prompts, 4/domain (near-duplicate prompts deduped)
  → valid k-fold/LOO probe with no singleton classes.
- Re-run overlap on r3 to check stability of Jaccard estimates.
- Token-level (not prompt-level) probe with prompt-held-out splits.
- Exclusive-expert ablation experiment on lang/math.
