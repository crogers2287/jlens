# jlens

Router-logit interpretability sidecar experiments for **Qwen3.6-35B-A3B** (MoE),
captured on 3090-class hardware with bf16 + CPU offload, prefill-only.

## What's here
- `src/capture_router_logits.py` — capture per-layer router logits + hidden
  states for a prompt set (40 router layers × 256 experts).
- `src/expert_overlap.py` — per-domain expert usage, pairwise Jaccard overlap,
  depth-tercile analysis, exclusive-expert counts.
- `src/routing_probe.py` — sequence-level domain probes / cosine NN retrieval.
- `src/token_probe.py` — token-level domain probe with **prompt-grouped CV**
  (no token leakage across train/test prompts).
- `data/prompts.jsonl` — 32 prompts, 4 per domain × 8 domains
  (code_py, code_rust, creative, fact, json_tool, lang, math, reason).
- `reports/` — JSON reports per run; `FINDINGS.md` — numbered findings log.
- `ROADMAP.md` — router-first ("routerguard") decision record and next steps.

## Headline results so far
- Routing signatures carry domain identity: cosine NN retrieval 6/8 (r2);
  intra-domain cosine > inter-domain.
- Token-level signal survives prompt-held-out splits: 0.578 grouped-CV
  accuracy vs 0.208 chance (r2, all-layer top-8 multi-hot).
- Expert pools overlap heavily across domains (mean pairwise Jaccard
  ~0.29–0.51) → naive expert ablation/surgery would cause collateral damage.
- Specialization is spread across depth (terciles near-flat, mid-stack
  slightly most exclusive) → sidecar should tap a spread of layers.

## Not in the repo
Raw capture tensors (`data/captures/*.pt`, ~250MB/run) and logs are
gitignored. Reproduce with `src/capture_router_logits.py` — see `STATE.md`
for exact invocations.

## Status
Active research. See `ROADMAP.md` for the routerguard build order:
schema freeze → sidecar head bakeoff → retrieval-need labels →
decode-step capture → learned+calibrated risk head → hidden-state phase 2.
