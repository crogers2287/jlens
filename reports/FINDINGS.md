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

## 7. r3 token-level probe + per-layer depth sweep (roadmap item 1)
Tools: `src/token_probe.py` → `reports/qwen3_6_35b_a3b_r3_token_probe.json`,
`reports/qwen3_6_35b_a3b_r3_layer_sweep.json`. 32 prompts (4/domain × 8),
708 tokens, top-8 multi-hot, GroupKFold(4) by prompt.

- **All-layer token accuracy 0.816 vs 0.175 chance (~4.7×)** — up sharply from
  r2's 0.578 (12 prompts). 4× more data → much cleaner domain separability.
- Per-layer depth profile (single-layer probes):
  - early (L0–12) mean 0.472; **mid (L13–26) mean 0.613**; late (L27–39) 0.535
  - best single layer **L20 = 0.712**; weakest L0 = 0.233 (raw token layer),
    late decline (L33 = 0.369, L39 = 0.442 — motor/output zone)
- **All-layer (0.816) beats the best single layer (0.712)** → multi-layer
  tapping is necessary, not optional. Confirms the ROADMAP #3 decision to tap a
  spread of layers rather than only late-stack.
- Depth story here is cleaner than the near-flat expert-set Jaccard terciles:
  the token-level probe resolves a mid-stack peak (L7–L20) that set-overlap
  washed out. For sidecar heads, prioritize the mid-third; keep a few
  early+late taps for coverage.

## 8. r3 cross-domain overlap (stability check vs r2)
Tool: `src/expert_overlap.py` → `reports/qwen3_6_35b_a3b_r3_overlap.json`.
- Overlap estimates rose with more tokens/domain (more experts touched):
  math|reason still tightest (J=0.507), depth terciles 0.48/0.41/0.47.
- Exclusive-expert ranking stable: lang (442) and math (342) still carve the
  most private capacity; code_py/creative least. Directionally matches r2.

## 9. Capture schema v1 frozen (roadmap item 2)
- `src/export_schema.py` + `schema/v1.json` (JSON Schema draft-07) + `SCHEMA.md`.
- Router-only JSONL projection: per prompt, per layer → topk_experts,
  topk_probs (softmax over top-k), and full-distribution entropy (nats).
- r3 exported to `reports/schema/r3.jsonl` (32 objects, 3.52 MB vs ~120 MB raw
  .pt) — all 32 validate against schema/v1.json.
- This is the frozen contract sidecar heads (item 3) train on; raw .pt stays
  gitignored. `entropy` is over the full 256-way softmax so it doubles as the
  routing-confidence feature for the future risk head.

## 10. Sidecar head bakeoff (roadmap item 3) — LOOP STOP CONDITION MET
Tool: `src/sidecar_bakeoff.py` → `reports/qwen3_6_35b_a3b_r3_bakeoff.json`.
Prompt-level routing signature (10240-dim: 40 layers × 256-expert usage hist),
StratifiedGroupKFold(4), each prompt its own group. 32 prompts, 8 domains,
chance 0.125.

| head | acc | top-2 | ECE | predict ms |
|---|---|---|---|---|
| logreg | **0.938** | 1.000 | 0.704 | 0.99 |
| linear_svm | **0.938** | 0.812 | 0.404 | 1.37 |
| nearest_centroid | 0.906 | – | – | 1.91 |
| **tiny_mlp** | 0.875 | 1.000 | **0.133** | **0.16** |
| hist_gbm | 0.125 | 0.250 | 0.000 | 6.09 |

- **Router-only domain detection works**: 3 of 5 heads ≥0.90 (7.5× chance).
- **Accuracy ceiling** = linear models (logreg/SVM, 0.938) — routing signatures
  are close to linearly separable by domain.
- **Best deployable head = tiny_mlp**: best calibration (ECE 0.133 vs logreg's
  0.704 overconfidence), fastest predict (0.16 ms/prompt), perfect top-2, only
  ~6 pts below the linear accuracy ceiling. For a risk head, calibration + speed
  matter more than raw top-1, so tiny_mlp wins.
- **hist_gbm collapses to chance** at n=32 over 10240 features — boosting needs
  far more data; documented limitation, revisit at n≥200.
- **Honest caveats**: n=32 is tiny → accuracies optimistic, ECE estimates
  coarse. This is a viability baseline, not a production number. A Platt/isotonic
  calibration wrapper should sit on whichever head ships. logreg's high accuracy
  but poor ECE is exactly why the risk head must be LEARNED + calibrated (not the
  external review's hand-set linear blend).

**Verdict:** the routerguard sidecar is feasible on 3090-class hardware with
sub-millisecond per-prompt overhead. Recommended head: calibrated tiny_mlp.

## 11. Decode-capture wiring fixed (M2 item 1)
- BUG (confirmed): `capture_one()` was prefill-only — no `max_new_tokens` param,
  call site never passed it, so the advertised `--max-new-tokens` CLI flag was
  a no-op. Decode capture never happened.
- FIX: `capture_one()` now takes `max_new_tokens`; when >0 it prefills with
  `use_cache=True` then greedily decodes k tokens via KV cache, capturing per
  generated token: per-layer router logits (forward that consumed the token),
  final-logit entropy, and selected-token probability. `max_new_tokens==0`
  path is byte-for-byte the old prefill-only behavior (no regression).
- Call site threads `args.max_new_tokens`; `.pt` gains a `decode_steps` list
  only when decoding.
- VERIFIED CPU-only via `tests/test_decode_capture.py` (HF-interface stub, no
  GPU/download): asserts k steps → k records with all 6 fields + correct router
  shapes, and prefill-only stays prefill-only. Both tests PASS.

## 12. token_probe CV upgraded to StratifiedGroupKFold (M2 item 2)
- BUG: token_probe.py used plain GroupKFold; with 32 prompts / 8 domains this
  produced folds that fully dropped a domain (the code then skipped them),
  biasing the estimate. sidecar_bakeoff.py already used StratifiedGroupKFold.
- FIX: token_probe now uses StratifiedGroupKFold (shuffle, seed 0), GroupKFold
  fallback only if a domain has fewer prompts than n_splits.
- r3 all-layer token accuracy: **0.816 (GroupKFold) → 0.863 (StratifiedGroupKFold)**
  vs 0.175 chance. Stratified folds keep all 8 domains present in train+test,
  so no folds are skipped and the estimate is cleaner (and higher).
- Report: reports/qwen3_6_35b_a3b_r3_token_probe_sgkf.json.

## 13. Decode schema v2 + exporter (M2 item 3)
- `schema/v2_decode.json` (draft-07): one record per GENERATED token —
  per-layer routing signature (topk_experts/topk_probs/full_entropy) plus
  decode-time signal (entropy_final_logits, selected_token_prob) and two drift
  measures. `schema/v1.json` (prefill) left frozen/untouched.
- `src/export_decode_schema.py`: reads `decode_steps` from decode captures,
  computes per-token per-layer expert-usage vectors, and derives:
  - `drift_from_prefill_signature` = cosine distance of the token's routing
    from the prompt's prefill signature
  - `drift_from_previous_token` = cosine distance from the prior token (null@0)
- VERIFIED CPU-only: schema passes `Draft7Validator.check_schema`; exporter
  dry-run on a synthetic 4-token decode capture → 4 records, all validate
  against v2, drift/entropy/prob fields correct. Real r4 export happens in
  item 4 after the GPU decode capture.

## 14. r4 decode capture (16/32, intentional cap) + export/validate (M2 steps 1–2)
- r4 decode capture stopped at **16/32 prompts** (512 decode tokens, all 8 domains
  represented) by operator decision — sufficient for the drift analysis and
  frees the fleet GPUs ~80 min early. bf16+CPU-offload decode ran ~5.3 min/prompt
  (PCIe-bound). Documented per steer.md step-1 exit criteria ("all 32 OR a
  documented reason for fewer").
- Exported → `reports/schema/r4_decode.jsonl` (512 records). New
  `src/validate_jsonl_schema.py` (draft-07, per-line, nonzero on first invalid):
  **all 512 records valid** against `schema/v2_decode.json`.
- First-look drift signal (drives steps 3,6,7):
  - drift_from_prefill mean 0.723 (sd 0.104), **flat across token index 0→31**
    (no stabilization) → unweighted count-drift-from-prefill is a near-constant
    structural offset (decode routes 1 token at a time vs prefill's whole prompt),
    NOT a per-token signal.
  - drift×entropy_final = −0.08, drift×selected_token_prob = +0.06 (≈ 0) →
    routing drift does NOT track output uncertainty at the unweighted level.
  - Real variation lives in entropy_final (max 2.85) / sel_prob (min 0.28) — the
    confidence spikes, independent of drift.
  - Implication: unweighted drift is too blunt; weighted drift (step 6) and the
    domain-shift probe (step 7) are the load-bearing follow-ups. Do NOT treat
    drift as a risk signal on this evidence.

## 15. DecodeGuard drift report (M2 step 3)
- `src/decode_drift.py` → `reports/qwen3_6_35b_a3b_r4_decode_drift.json` (512
  tokens, 16 prompts, 8 domains). Full metric set: distributions, by_domain,
  by_token_index, Pearson correlations, top spike records.
- Confirms the partial read at full resolution:
  - drift_from_prefill mean 0.723 (sd 0.104), FLAT across position (t0=0.653,
    t31=0.664) — structural offset, not a per-token signal.
  - All drift↔confidence correlations ≈ 0: drift_prefill×entropy −0.078,
    ×sel_prob +0.056; drift_prev×entropy −0.108, ×sel_prob +0.118.
  - **Entropy/confidence carries the mode-shift signal, NOT drift**: the #1
    entropy spike is the ` ``` ` code-fence token (code_py_01 @idx1, H=2.85,
    sel_prob 0.39); lowest sel_prob is `**` markdown (fact_01, 0.28). Format/
    structure-transition tokens light up entropy_final while routing drift stays
    flat.
- Takeaway for the risk head: use entropy_final_logits + selected_token_prob as
  the decode-time uncertainty features; unweighted routing drift is not
  predictive. Whether WEIGHTED drift (step 6) recovers signal is the open
  question.

## 16. Drift interpretation notes (M2 step 4) — verdict: drift WEAK, entropy is the signal
- `reports/qwen3_6_35b_a3b_r4_decode_drift_notes.md`. Grounded in actual spike tokens.
- Top-entropy = mode-boundary opens (` ``` ` code fence, `<think>`, `\n\n`) at
  t0–t1; top-drift = maximally-confident template tokens (`An`, `,`, ` thinking`,
  H≈0/p=1.0). **0/8 overlap** between the two spike sets.
- Uncertainty concentrates in first 1–2 generated tokens (mode selection):
  H(t0..1)=0.75→1.05 then collapses to ~0.1; drift is flat throughout.
- Low-confidence tokens include factual-content tokens (` NASA` p=0.35 in fact_01)
  — the interesting risk locus — and drift there is below average.
- Verdict: unweighted drift NOT usable as a risk feature; lead the risk head with
  entropy_final_logits + selected_token_prob. Step 6 (weighted drift) is the
  make-or-break test for whether drift contributes anything.

## 17. Router-only decode mode + resume-skip (M2 step 5)
- capture_router_logits.py: `--router-only`/`--no-hidden-states` (output_hidden_states=False,
  payload hidden_states=None) and `--overwrite`. Default = resume-skip: an existing
  .pt that loads with router_logits is skipped (`_valid_capture`), corrupt/partial
  files are re-captured. Backward compatible (prefill-only path unchanged).
- Rationale: DecodeGuard needs no hidden states; router-only shrinks payloads and
  lets interrupted captures resume without redoing completed prompts (would have
  saved the r4 cap/restart friction).
- tests/test_decode_capture.py extended to 4 tests, all PASS: prefill-only intact,
  decode intact, router-only omits hidden states (decode still works), resume-skip
  valid/missing/corrupt detection. Loaders/exporters tolerate hidden_states=None.

## 18. Weighted drift features + schema v3 (M2 step 6) — drift dead, but topk_mass lives
- `schema/v3_decode.json` = v2 superset (v2 frozen) + drift_from_prefill_weighted,
  drift_from_previous_token_weighted, topk_mass_or_margin. Exporter gains
  `--weighted`; r4 weighted export = 512 records, all valid against v3.
- **Make-or-break test — weighted drift does NOT recover signal**: prob-weighted
  drift_prefill × entropy = −0.062, × sel_prob = +0.030 (even weaker than the
  unweighted −0.078/+0.056). Weighting the 256-dim routing vector by top-k
  softmax mass instead of 1/k counts changes nothing. **Routing drift (either
  form) is confirmed dead as a confidence/risk feature.**
- **NEW positive — topk_mass_or_margin is the first routing feature that tracks
  confidence**: routing-concentration (mean summed top-k softmax mass, mean 0.231)
  × entropy = **+0.165**, × sel_prob = **−0.157**. Consistent sign both ways:
  when the router puts MORE mass on its chosen experts, the model is LESS
  confident in the emitted token. Modest but the strongest router→uncertainty
  link found so far.
- Consequence for the risk head: DROP drift; KEEP topk_mass as a candidate
  routing feature alongside the (stronger) entropy_final_logits + sel_prob.
  Caveat: 512 tokens / 16 prompts — ±0.16 is suggestive, needs the M3 labeled set
  to confirm.

## 19. Decode domain-shift probe (M2 step 7) — soft per-token, but a real code↔prose signal
- `src/decode_domain_shift.py`: trains the r3 sidecar domain head (logreg on r3
  prefill signatures) and applies it per decode token + to each r4 prefill sig.
  Report: `reports/qwen3_6_35b_a3b_r4_domain_shift.json`.
- **r3 head transfers to r4 prefill perfectly: 16/16** predicted domains match the
  true label — the domain sidecar generalizes to an unseen run.
- Per-token decode routing keeps REAL domain signal but soft: **72% of decode
  tokens predict the correct domain** (mean label-vs-decode disagree 0.281) vs
  12.5% chance — well above noise — yet at low per-token confidence (mean
  max-proba 0.249, margin 0.099). Single-token routing is sparse (8 experts/layer
  vs prefill's ~160), so predictions are correct-on-average but not sharp.
- **The "switches" are partly meaningful, not just noise.** Secondary votes are
  systematic: `lang` (prose/natural-language) dominates the non-true votes and
  concentrates on `<think>`/explanation spans. Clean-code output stays on-domain
  (code_py_01: 30/32 code_py); `<think>`-heavy prompts split (code_py_02/03: ~15
  code_py / ~12 lang). Decode routing captures a genuine **code↔prose mode
  shift** — when the model reasons/explains, its routing resembles the prose
  domain.
- Consequence: a WINDOWED/smoothed decode-domain estimate (not per-token) is a
  viable mode-shift feature for the risk head; per-token is too sparse for a hard
  label. Caveat: 16 prompts.
