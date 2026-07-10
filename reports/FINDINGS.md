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

## 20. M3 risk-labeling plan (M2 step 8) — DecodeGuard milestone COMPLETE
- `M3_RISK_LABELING.md`: 10-label taxonomy (8 prompt-time + 2 generation-time),
  ≥50 prompts/family, prompt-held-out splits, calibrated baselines
  (logreg/SVM/tiny_mlp + hand-score-for-comparison), metrics
  (AUROC/AUPRC/ECE/false-low-risk/false-high-risk/latency), false-low-risk
  prioritized over false-high-risk.
- Feature set grounded in M2 evidence: EXCLUDES drift (dead), leads with
  entropy_final_logits + selected_token_prob, includes topk_mass and a WINDOWED
  domain-shift feature; scale target ≥500 prompts (all M2 caveats are n=16/32).
- Execution is HUMAN-GATED (risk labels). Loop stops here per steer.md stop
  condition; hand off to operator.

### DecodeGuard M2 — summary of the empirical story
Router-only decode telemetry is feasible on 3090-class HW. Of the candidate
decode-time signals: routing DRIFT is a dead end; ENTROPY + SELECTED-TOKEN
PROB are the real uncertainty signal (spiking at mode boundaries); TOPK_MASS is
a weak-but-real routing-concentration signal; WINDOWED DOMAIN-SHIFT captures a
code↔prose transition. These define the M3 risk-head feature set. Everything
awaits labeled data to become a calibrated governor.

## 21. M3 risk-label schema v1 (M3 step 1)
- `schema/risk_labels_v1.json` (draft-07): one record per prompt, 10-label
  multi-label. Each label true|false|**null** (null = UNKNOWN, not false).
  Required `labeler` (string|null; non-null = finalized/human-labeled).
  additionalProperties:false at both levels + all 10 labels required.
- Verified: valid draft-07; accepts all-null scaffold + partially-labeled
  records; **REJECTS** unknown label keys, missing labels, and non-bool/null
  values. This is the contract the human-labeling handoff writes against; the
  trainer refuses until non-null labels exist.

## 22. Label scaffold (M3 step 2)
- `src/build_label_scaffold.py` → `data/labels/risk_labels_seed.jsonl`: 32
  all-null records (union of data/prompts.jsonl + r4 decode prompt_ids), one per
  prompt. labeler=null, all 10 labels=null — the generator NEVER invents a value.
- Verified: 32 records, all validate against schema/risk_labels_v1.json, all
  confirmed all-null; file is tracked (not gitignored). Awaiting human labeling.

## 23. Risk feature extractor (M3 step 3) — drift barred by assertion
- `src/risk_features.py` → `reports/features/r4_risk_features.jsonl`: 16 rows (one
  per r4 prompt). Feature groups = the M2 KEEP set: prefill domain pred + margin
  (r3 head), entropy_final (mean/max/std), selected_token_prob (mean/min/std),
  topk_mass (mean/min/std, from v3 export), windowed decode-domain-shift
  (off-prefill-domain frac + switch count), low-confidence & high-entropy spike
  counts.
- **Drift explicitly excluded and enforced**: a runtime assertion fails the
  extractor if any of the 4 drift keys appears in a row; verified 0 drift keys in
  all 16 rows. Independent re-check confirms all feature groups present.
- These rows join the (currently all-null) labels by prompt_id once a human
  labels; the trainer stays blocked until then.

## 24. Calibrated train/eval skeleton + LABEL GATE (M3 step 4)
- `src/train_risk_heads.py` + `src/eval_risk_heads.py`. Baselines wired:
  calibrated logreg / linear SVM / tiny MLP (CalibratedClassifierCV, isotonic) +
  hand-score baseline for comparison only. Prompt-held-out (StratifiedGroupKFold).
- Metrics implemented + unit-sane: AUROC, AUPRC, ECE, false-low-risk rate,
  false-high-risk rate, latency. `false_low_risk` = P(pred neg | truly pos) —
  the costly miss, prioritized over `false_high_risk`.
- **LABEL GATE proven**: `check_trainable()` refuses (nonzero exit, clear
  per-label message) when the label file is missing, all-null, or below
  min-per-label (10) with both classes. Verified all three refusal paths on the
  current all-null seed — NO head is trained, NO label is fabricated. Training
  body executes only once a human provides labels.

## 25. Labeling handoff (M3 step 5) — M3 scaffolding COMPLETE
- `LABELING_HANDOFF.md`: per-label definition + positive/negative example for all
  10 labels (8 prompt-time, 2 generation-time), the true/false/**null** rule
  (null=unknown, never guess), the ≥50/label + prompt-held-out requirement, why
  false-low-risk > false-high-risk, and the exact train/eval command (which
  refuses until labeled).
- All M3 stop-condition artifacts verified present; the label gate still refuses
  the all-null seed. M3 scaffolding milestone COMPLETE — hand off to the operator
  for human labeling.

### M3 summary
Built the full label-gated risk-modeling scaffold WITHOUT fabricating a single
label: risk_labels_v1.json (rejects unknown labels), 32 all-null seed records,
risk_features.py (M2 KEEP features, drift barred by assertion), calibrated
train/eval skeleton that provably refuses unlabeled data, and LABELING_HANDOFF.md.
Next action is HUMAN: label ≥50 prompts/family, then re-run the loop to train +
calibrate the heads.

## 26. Benchmark dataset source registry (M4 step 1)
- `data/registry/benchmark_sources.json`: first wave (TruthfulQA Apache-2.0,
  SciFact CC-BY-NC-2.0, GSM8K MIT) + alternates (SimpleQA, FEVER, HumanEval, MBPP)
  + second wave (BeaverTails/PKU-SafeRLHF, BFCL, deepset/prompt-injections,
  SWE-bench, GAIA). Each source: hf repo_id, split, task, exact license, size,
  tier=benchmark_gold, and the jlens-label mapping rule.
- Verified: every source has a license; all mappings target valid jlens labels;
  **all 10 labels covered** across the registry; first-wave sizes ≤5 MB (well
  under the 1 GB download gate).
- Licensing policy recorded: SciFact/BeaverTails/PKU-SafeRLHF are NON-COMMERCIAL
  (CC-BY-NC) → store derived labels + ids + minimal text, flag non_commercial,
  never redistribute forbidden raw text. FEVER (CC-BY-SA) is the redistribution-
  friendlier alternate to SciFact. No downloads this step (registry only).

## 27. Risk labels schema v2 — provenance superset (M4 step 2)
- `schema/risk_labels_v2.json` (draft-07): v1's 10-label body (true/false/null,
  null=UNKNOWN) unchanged, plus provenance fields — source_dataset, source_split,
  source_record_id, source_label, source_license, label_source
  (enum bronze|silver|benchmark_gold|gold), label_confidence, non_commercial.
- Provenance fields are optional (hand-labeled v2 rows without a source still
  validate); converters MUST fill them for benchmark rows.
- Verified: check_schema passes; a benchmark_gold record validates; unknown label
  keys STILL rejected; an invalid label_source enum ("platinum") rejected. v1
  frozen/untouched.

## 28. Converter #1: TruthfulQA → benchmark_gold (M4 step 3)
- `src/convert_truthfulqa.py`: pulls the generation parquet via huggingface_hub
  (no `datasets` install; pyarrow/pandas already present) → cached under
  data/raw/ (gitignored). Emits one benchmark_gold record per human answer.
- Output `data/labels/benchmark/truthfulqa.jsonl`: **5,918 records** (2,600
  correct + 3,318 incorrect). Mapping: correct → unsupported_or_hallucinated=false
  + answerable_from_memory=true; incorrect → unsupported_or_hallucinated=true;
  all 8 other labels null (null=unknown, never guessed).
- Class balance: unsupported_or_hallucinated n_true=3318 / n_false=2600 / n_null=0
  (both classes, far above the coverage gate min of 10); answerable_from_memory
  set true only on correct answers (null on the myths — we don't claim a myth is
  un-answerable-from-memory). All 5,918 rows validate against schema/risk_labels_v2.json.
- License Apache-2.0 (non_commercial=false). Raw parquet stays out of git; only
  the derived JSONL + converter are committed.

## 29. Converter #2: FEVER → benchmark_gold (M4 step 4)
- `src/convert_fever.py`: pulls copenlu/fever_gold_evidence valid.jsonl (6.5 MB,
  **CC-BY-SA-3.0** — chosen over SciFact CC-BY-NC for redistribution) via
  huggingface_hub. Output `data/labels/benchmark/fever.jsonl`: **15,935 records**,
  all v2-valid.
- Mapping: REFUTES → unsupported_or_hallucinated=true; SUPPORTS → false;
  NOT ENOUGH INFO → null. verifiable claim → needs_exact_citation=true (else null).
- Class balance: unsupported_or_hallucinated n_true=4887 / n_false=4638 / n_null=6410
  (strong both-class); needs_exact_citation n_true=9525 / n_false=0 / n_null=6410.
- DATA-GAP flagged: needs_exact_citation has NO false examples from FEVER — a
  claim-verification set only yields citation-needed positives. The coverage gate
  will (correctly) fail that label until a "no-citation-needed" source (stable
  closed-book QA) supplies negatives. Honest partial coverage, per null≠false.

## 30. Converter #3: GSM8K → benchmark_gold (M4 step 5) — 3 converters done
- `src/convert_gsm8k.py`: pulls gsm8k main/test parquet (MIT, ~2MB) via
  huggingface_hub. Output `data/labels/benchmark/gsm8k.jsonl`: **1,319 records**,
  all v2-valid. Mapping: every item → needs_math_verification=true,
  answerable_from_memory=false (requires derivation, not recall). Gold answer
  kept in provenance (source_label) so target-model output can be graded for
  unsupported_or_hallucinated downstream.
- **≥3 benchmark_gold converters delivered** — 23,172 total records
  (TruthfulQA 5,918 + FEVER 15,935 + GSM8K 1,319).
- Cross-source coverage emerging: answerable_from_memory now has BOTH classes
  (TruthfulQA 2600 true + GSM8K 1319 false); unsupported_or_hallucinated strongly
  covered (TruthfulQA + FEVER). Single-source labels (needs_math_verification,
  needs_exact_citation) still lack negatives — the coverage report will quantify.

## 31. Coverage report + gate (M4 step 6)
- `src/coverage_report.py` → `reports/coverage/benchmark_coverage.json`:
  per-label true/false/null aggregated over 23,172 records × 3 sources, with a
  per-label COVERAGE GATE (pass iff both classes present AND minority ≥ 10).
- **2 labels PASS (training-ready)**: answerable_from_memory (2600T/1319F),
  unsupported_or_hallucinated (8205T/7238F) — both strong both-class from
  complementary sources (TruthfulQA+GSM8K, TruthfulQA+FEVER).
- **8 labels FAIL** — the gate pinpoints the data gaps:
  - single-class (need NEGATIVES): needs_exact_citation (9525T/0F),
    needs_math_verification (1319T/0F)
  - no data yet (need second-wave sources): needs_current_info,
    needs_code_execution, needs_user_file_context, high_stakes_or_sensitive,
    context_attack_present, format_or_tool_mode_shift
- Next-source shopping list (from GOLD plan): BeaverTails/PKU-SafeRLHF→high_stakes;
  BFCL→format_or_tool_mode_shift; prompt-injection benchmark→context_attack;
  SWE-bench→needs_user_file_context; GAIA/BrowseComp→needs_current_info;
  HumanEval/MBPP→needs_code_execution; stable closed-book QA→citation/math negatives.

## 32. Audit-sampling script (M4 step 7)
- `src/audit_sample.py` → `data/labels/audit_queue.jsonl`: deterministic
  evenly-spaced stride sample of N=10 records per source (30 total: 10 each
  TruthfulQA/FEVER/GSM8K) for human spot-check.
- The script ONLY QUEUES — every queued record keeps label_source=benchmark_gold
  and audit_status="pending"; a human confirms/rejects and the operator
  manually promotes confirmed records to label_source="gold" (benchmark_gold →
  project-gold). Verified: queue non-empty, nothing auto-promoted, identical on
  re-run (deterministic, no RNG).

## 33. Trainer honors coverage gate (M4 step 8) — MILESTONE COMPLETE
- `src/train_risk_heads.py` now accepts v1/v2 label files (file/glob/dir) and
  gates by TIER × coverage: `--mode prototype` allows benchmark_gold+gold;
  `--mode final` requires human-audited gold. `trainable_labels()` selects only
  labels with ≥min both-class values of the allowed tier; refuses if none pass.
- Verified 4 behaviors: (1) all-null v1 seed → REFUSE; (2) benchmark set
  (prototype) → PASS for answerable_from_memory + unsupported_or_hallucinated;
  (3) same set (final) → REFUSE (benchmark_gold ≠ gold — final needs audited
  gold); (4) synthetic below-threshold → REFUSE. All exits correct (0/1/1/1).
- Prototype training is now unlockable on the 2 covered labels; final threshold
  calibration stays gold-gated. Training body still a scaffold stub (no
  fabricated results).

### M4 summary
Ingested 23,172 public benchmark-gold records (TruthfulQA/FEVER/GSM8K) into
risk_labels_v2 with full provenance + licensing, WITHOUT fabricating a label.
Coverage gate: 2/10 labels training-ready; the rest have a documented source
shopping list. Trainer prototype-trains only covered labels; final stays
gold-gated; audit queue promotes benchmark_gold→gold via human review only.

## 34. M5 benchmark prompt sample (M5 step 1)
- `src/build_benchmark_prompts.py` → `data/prompts/benchmark_m5_sample.jsonl`:
  16 prompts, deterministic + class-balanced for the two covered labels, prompt
  text reconstructed from cached raw sources (data/raw, gitignored) by
  source_record_id. Composition: 4 TruthfulQA-correct + 4 GSM8K + 4 FEVER-SUPPORTS
  + 4 FEVER-REFUTES.
- Balance: answerable_from_memory 4T/4F/8null; unsupported_or_hallucinated
  4T/8F/4null — both covered labels have both classes.
- **METHODOLOGICAL CAVEAT (recorded):** the benchmark label describes a reference
  ANSWER, but telemetry is captured on the PROMPT. This is a prompt-level PROXY
  label for a smoke prototype — indicative, not a final claim. Licenses permit the
  prompt text (TruthfulQA Apache / FEVER CC-BY-SA / GSM8K MIT); raw sources stay
  gitignored.

## 35. M5 decode capture + v3 export (M5 steps 2–3)
- Router-only decode telemetry captured for all 16 sample prompts (24 gen tokens
  each; ~5 min/prompt, ~1.3h; GPUs then freed for llama-swap). Raw .pt gitignored.
- Exported → reports/schema/benchmark_m5_decode.jsonl: 384 decode-token records
  (v3 weighted, incl. topk_mass), all validate against schema/v3_decode.json.

## 36. M5 features + label↔feature join (M5 steps 4–5)
- reports/features/benchmark_m5_features.jsonl: 16 rows (M2 KEEP features, drift
  excluded/asserted). src/join_labels_features.py → reports/benchmark_m5_join.json:
  16/16 matched. Joined-set class balance: answerable_from_memory 4T/4F (trainable),
  unsupported_or_hallucinated 4T/8F (trainable). This is the prototype training table.

## 37. M5 real prototype heads (M5 step 6) — MILESTONE COMPLETE
- train_risk_heads.py stub REPLACED with real leave-one-out prototype training
  (logreg / linear SVM / hand-score baseline) on the joined 16-prompt table.
  --min-per-label lowered to 3 for the smoke run (stated). --mode final STILL
  refuses (gold-gated) — verified. Report: reports/risk_heads_prototype.json.
- REAL metrics (LOO, tiny-n):
  - answerable_from_memory (n=8, 4+/4-): best AUROC 0.875 (logreg & hand_score);
    hand_score FLR=0.25/FHR=0.25 is the best operating point.
  - unsupported_or_hallucinated (n=12, 4+/8-): linsvm AUROC 0.844 BUT
    false-low-risk-rate=1.0 at the 0.5 threshold (ranks well, catches zero
    positives operationally — classic good-AUROC/bad-threshold trap). logreg
    AUROC 0.688 with FLR=0.25.
- HONEST TAKEAWAY: the telemetry carries real RANKING signal (AUROC 0.84–0.88 vs
  chance) — the core bet holds — but at n=8–12 the CALIBRATION (ECE 0.15–0.42)
  and thresholds are unusable, and false-low-risk (the error we care about most)
  is bad at the default operating point. Exactly why final thresholds stay
  gold-gated and need far more data.
- CAVEATS (in the report): tiny n; answerable_from_memory confounded with domain
  (trivia vs math); prompt-level PROXY labels (not graded model outputs); ECE
  unreliable at this n. No inflated numbers.

### M5 summary
First END-TO-END trained jlens risk heads: 16-prompt benchmark sample → GPU
router-only decode telemetry → v3 export → drift-excluded features → label join →
real LOO prototype training. Ranking signal is real (AUROC ~0.84–0.88); operating
points are not (tiny-n, uncalibrated). Pipeline is now complete and honest end to
end; scaling data is the next lever.

## 38. PolicyEngine v0 config (M6 step 1)
- `config/policy_engine_v0.json`: shadow/advisory posture; scores only the two
  M5-covered labels. Overall risk = max of per-label risk contributions
  (answerable_from_memory risk = 1−p; unsupported_or_hallucinated risk = p). Four
  contiguous score bands over [0,1] → v0 actions: low→answer_locally,
  medium→verify, high→retrieve, critical→require_confirmation.
- Explicitly PROTOTYPE thresholds (not production); `blocks_real_actions:false`;
  final thresholds `gold_audit_gated`. Verified: loads, bands contiguous & cover
  [0,1], every level maps to a valid v0 action, posture flags correct.

## 39. PolicyEngine v0 scorer (M6 step 2)
- `src/policy_engine.py`: PolicyEngine fits the two covered-label heads from the
  M5 join table (reuses train_risk_heads `_flatten_features`; drift excluded +
  asserted), then `score(feature_row)` returns {prompt_id, level, scores{label:p},
  risk, recommended_action, explanation}. Overall risk = max per-label risk
  contribution; level via config bands; level→v0 action. ADVISORY-only: no file
  writes, never blocks/executes.
- Verified on the 16 M5 rows: all return the 4-field shape. Sensible spread —
  6 critical→require_confirmation, 4 medium→verify, 6 low→answer_locally. FEVER
  claim-verification prompts (highest telemetry uncertainty) correctly land
  critical. Prototype thresholds only; no production claim.

## 40. Shadow-logging runtime CLI (M6 step 3)
- `src/risk_runtime.py`: wraps PolicyEngine, scores a feature JSONL row/file,
  prints the advisory, and APPENDS one entry per row to
  `reports/shadow/shadow_log.jsonl` {ts_placeholder, prompt_id, feature_source,
  scores, level, recommended_action, mode:"shadow", outcome_note:null}. No
  wall-clock (env-safe --ts placeholder). Records only — never blocks/executes.
- Verified: 3 advisories logged, every line parses with all required keys,
  mode=shadow, outcome_note=null. Shadow log is tracked (small/shareable).

## 41. PolicyEngine v0 tests (M6 step 4)
- `tests/test_policy_engine.py` (4 tests, all PASS): config loads + shadow/advisory
  posture + every level maps to a valid v0 action; score() 4-field shape on a real
  M5 row (both label scores in [0,1], valid action/level); level→action correct at
  band-representative risk values; shadow_entry shape + round-trips through a
  written JSONL line. Decode-capture tests still pass (no regression).

## 42. PolicyEngine v0 docs (M6 step 5) — MILESTONE COMPLETE
- `docs/POLICY_ENGINE_V0.md`: policy output schema, shadow-log schema, v0 action
  semantics, a WORKED end-to-end example (FEVER prompt → critical →
  require_confirmation), the advisory/shadow posture, and the explicit statement
  that final/production thresholds stay gold/audit gated + M5 path preserved.
- All M6 artifacts present. train --mode final still REFUSES (gold-gated). M6
  PolicyEngine v0 COMPLETE.

### M6 summary
jlens now has a RUNTIME layer: an advisory, shadow-mode risk governor that scores
a prompt's telemetry (two covered labels) into a level + recommended action and
logs every call — never blocking, never executing. Config → scorer → shadow-log
CLI → tests (4/4) → docs. Prototype-only; production decisions stay gold-gated.

## 43. M7 local-endpoint example config (M7 step 1)
- `config/local_endpoint_example.json`: EXAMPLE OpenAI-compatible endpoint
  (base_url localhost placeholder, model placeholder, api_key "not-needed",
  timeout) with per-field _doc. Placeholder only — no secret, no real host.
  Notes the GGUF-has-no-router-logits reality (live prompts → policy=null).
  Verified: loads, localhost placeholder, no secret.

## 44. M7 local shadow wrapper (M7 step 2)
- `src/local_shadow_wrapper.py`: --mode dry-run (default, no network, fixture
  output) and --mode live (OpenAI-compatible /chat/completions via requests, urllib
  fallback — output text only). Per prompt: get output → attach feature row by
  prompt_id if present → PolicyEngine.score, else policy=null + note. Writes a
  real-use runtime record to reports/shadow/realuse_log.jsonl. ADVISORY only —
  never performs a tool/file/GitHub action; require_confirmation is a recommendation.
- Verified both paths: TQA prompts (feature rows exist) score low→answer_locally;
  an unknown prompt → policy=null with the GGUF-no-telemetry note; all outcome
  fields null. Records carry the full metadata shape.

## 45. M7 runtime schema doc (M7 step 3)
- `docs/M7_SHADOW_RUNTIME.md`: documents the real-use runtime record (matches the
  wrapper's emitted shape exactly, incl. policy=null + policy_note path), dry-run
  and live run commands, the advisory/shadow posture, that require_confirmation
  never executes, final thresholds gold-gated, and the privacy rule (public
  prompts only in committed logs).

## 46. M7 wrapper fixture tests (M7 step 4)
- `tests/test_local_shadow_wrapper.py` (4 tests, all PASS): dry-run record shape +
  all 5 outcome fields null; policy scored when a feature row exists (valid v0
  action); policy=null + no-telemetry note when no feature row; live mode goes
  through a STUBBED requests.post (asserts exactly one call, no real network).
  PolicyEngine + decode-capture suites still pass (no regression).

## 47. M7 public sample log (M7 step 5) — MILESTONE COMPLETE
- `reports/shadow/realuse_sample.jsonl`: 6 real-use records from dry-run over
  PUBLIC benchmark prompts (TruthfulQA/GSM8K only). Advice spread 3 answer_locally
  / 1 verify / 2 require_confirmation; all outcome fields null (awaiting human
  review). Doc gained a sample-log run section.
- All M7 artifacts present; train --mode final still REFUSES (gold-gated). M7
  COMPLETE.

### M7 summary
jlens now produces REAL-USE shadow logs: the local wrapper obtains a model output
(dry-run fixture or optional live endpoint), attaches telemetry when a feature row
exists (else policy=null — GGUF has no router logits), scores via PolicyEngine v0,
and logs an advisory record with human-review outcome fields. Advisory/shadow only
— never executes; require_confirmation is a recommendation. Public prompts only;
production thresholds stay gold-gated.

## 48. Reviewed-outcome schema v1 (M8 step 1)
- `schema/shadow_outcome_v1.json` (draft-07): shadow record + outcome{user_agreed,
  was_wrong, needed_retrieval, needed_checker (bool|null), notes (str|null)} +
  review_meta{reviewer, reviewed_at (placeholder, no wall-clock), review_source
  (str|null), review_confidence (0..1|null)}. null = UNREVIEWED (not false);
  additionalProperties:false everywhere.
- Verified: valid draft-07; all-null (unreviewed) record validates;
  fully-reviewed record validates; bad-type (user_agreed:"yes"), unknown field,
  and review_confidence>1 all REJECTED. Humans set outcomes; schema enforces the
  shape, never fabricates.

## 49. Review-queue builder (M8 step 2)
- `src/build_review_queue.py` → `reports/shadow/review_queue_sample.jsonl`:
  converts shadow records (public realuse_sample + shadow_log) into 9 deduped
  shadow_outcome_v1 records with EVERY outcome + review_meta field null
  (reviewed=0/9). NEVER sets an outcome value. All 9 validate against
  schema/shadow_outcome_v1.json; asserted all-null. Public prompts only.

## 50. Safe review CLI (M8 step 3)
- `src/review_shadow_log.py`: non-interactive CLI to set outcome/review_meta on
  ONE queue record (by --prompt-id) from EXPLICIT human flags. Writes only the
  passed fields, validates the whole record against schema/shadow_outcome_v1.json,
  supports --dry-run, and REFUSES invalid booleans (e.g. "maybe"), out-of-range
  confidence, and unknown prompt_ids. NEVER auto-fills/guesses.
- Exercised on a THROWAWAY copy (not the committed queue): dry-run validates
  without writing; a write sets was_wrong + reviewer and re-validates; bad type +
  unknown id both refused. Committed review_queue_sample.jsonl remains all-null —
  no fabricated outcomes committed.

## 51. Outcome coverage + calibration (M8 steps 4–5)
- `src/outcome_report.py` → `reports/outcomes/outcome_coverage.json` (reviewed vs
  unreviewed, per-field non-null counts, per-reviewer counts) +
  `reports/outcomes/calibration_notes.md` (policy level vs reviewed was_wrong;
  false-low-risk / false-high-risk from REVIEWED rows only).
- On the current all-null queue: coverage honestly reports **reviewed=0/9**;
  calibration notes say exactly "calibration pending — no reviewed outcomes yet"
  and keep production gated. No outcome is inferred to fill a gap.
- Calibration math verified on SYNTHETIC in-memory fixtures (never committed):
  1 wrong@critical + 1 wrong@low + 1 fine@low → FLR=0.5, FHR=0.0, confusion
  tp1/fn1/fp0/tn1. Computes from reviewed rows only.

## 52. Human-review guide (M8 step 6)
- `docs/SHADOW_OUTCOME_REVIEW.md`: the reviewer flow (build queue → review CLI →
  coverage/calibration), each outcome/review field's meaning, the "leave null if
  unsure — never guess" rule, what false-low-risk / false-high-risk measure, and
  the honesty + gating rules (never fabricate; production stays gold-gated;
  public prompts only).

## 53. Outcome-review tests (M8 step 7) — MILESTONE COMPLETE
- `tests/test_outcome_review.py` (5 tests, all PASS): schema accepts null +
  reviewed, rejects bad-type/unknown/range; build_review_queue emits all-null
  valid records; review CLI sets a field on a throwaway fixture and re-validates;
  calibration computes FLR 0.5 / FHR 0.0 from reviewed-only synthetic fixtures;
  calibration returns None (pending) when nothing reviewed. All 4 jlens suites
  pass (17 tests). Committed queue verified still all-null; train --mode final
  still refuses (gold-gated). M8 COMPLETE.

### M8 summary
jlens now has the human-review + calibration loop: schema/shadow_outcome_v1
(null=unreviewed), an all-null review queue builder, a safe explicit-flag review
CLI (never guesses), a coverage report, calibration (false-low/high-risk from
reviewed-only, honest "pending" at 0 reviewed), a reviewer guide, and tests.
Nothing fabricated: outcomes are set only by a human; production thresholds stay
gold/audit gated. This closes the feedback loop — the project now ends where
human judgment begins.

## 54. Private-log dir convention (M9 step 1)
- `.gitignore` gains `reports/shadow/private/*.jsonl` — private real-use shadow
  logs (real prompt/output text) are LOCAL-ONLY, never committed. Committed a
  `reports/shadow/private/README.md` stub (the only tracked file there)
  explaining the local-only rule + the redact/aggregate/check-commit-safe path.
- Verified: git check-ignore blocks reports/shadow/private/realuse_local.jsonl;
  the README is NOT ignored.

## 55. Redaction tool (M9 step 3)
- `src/redact_shadow_log.py`: scrubs the three free-text fields (prompt_preview,
  output_preview, outcome.notes) to '[redacted]' (or --hash: a stable
  non-reversible tag), KEEPS prompt_id / policy(level/action/scores/explanation) /
  policy_note / mode / outcome booleans / review_meta.
- Verified on the PUBLIC fixture: 6 records redacted — text fields gone, all
  structural fields + booleans preserved, and NO original prompt text leaks
  anywhere in the output. Enables safe sharing of a private log.

## 56. Aggregate-only summary is safe by construction (M9 step 4)
`src/private_outcome_summary.py` builds its output dict from a fixed set of
count/label keys, so free text (prompt/output/notes) never enters — a recursive
`_assert_no_text` guard then hard-fails if any forbidden key ever holds a
STRING value (integer counts like `outcome_field_nonnull_counts.notes` are
allowed; they are aggregates, not text). Verified on the PUBLIC fixture
(reports/shadow/realuse_sample.jsonl → reports/outcomes/private_summary_sample.json):
6 records, 0 reviewed (honest null calibration — nobody has reviewed yet),
level_distribution {low:3, medium:1, critical:2}, action_distribution
{answer_locally:3, verify:1, require_confirmation:2}. Grep for the fixture's
prompt text ("watermelon", "artificial intelligence", "dry-run fixture output")
returned NOTHING in the summary — no leak. This makes the summary committable
even when its INPUT is a private real-use log.

## 57. Commit-safety guard (M9 step 5)
`src/check_commit_safe.py` scans staged files and exits nonzero if any (1) is a
private-log path (reports/shadow/private/*.jsonl, README exempt), (2) references
that private dir anywhere in its content, or (3) carries UNREDACTED
prompt_preview / output_preview / outcome.notes text (a non-empty string that is
not a `[redacted]` / `[redacted:<hash>]` marker). It PASSES aggregate-only
summaries, all-null-text queues, and redacted files. Verified: PASS on
private_summary_sample.json and an all-null-text queue; PASS on a redacted file;
FAIL on real prompt_preview text, FAIL on unredacted outcome.notes, FAIL on a
private-log path. DESIGN NOTE: the guard is deliberately conservative — it
cannot tell public benchmark prompt text from private real-use text, so it flags
ALL unredacted prompt/output text (including the M7/M8 public benchmark
review_queue_sample.jsonl, committed earlier under explicit public-demo
approval). Going forward the M9 workflow commits only aggregate summaries or
redacted logs; raw text queues stay in the gitignored private dir.

## 58. Private shadow workflow doc + guard scoping (M9 step 6)
`docs/PRIVATE_SHADOW_WORKFLOW.md` documents the end-to-end local-only flow:
generate a private log (gitignored) → review locally (M8 CLI) → make a shareable
artifact (aggregate-only summary OR redacted log) → run check_commit_safe.py
before staging. Every example uses the PUBLIC fixture; documented commands match
the wrappers' real flags (--mode/--prompts/--log; build_review_queue --inputs/--out;
review_shadow_log --queue/--prompt-id/...). Also refined check_commit_safe: the
private-path *content* check now applies to parsed JSON records only, so prose
(docs, FINDINGS narrative) that merely MENTIONS the private path passes —
documentation is not a leak. File-path check + JSON text-field check + JSON
private-path-reference check still FAIL on real leaks. Re-verified all 5 cases.
Gating restated: production/final thresholds stay gold/audit gated until enough
reviewed real-use records exist; scores stay PROTOTYPE tiny-n M5 numbers.

## 59. Private-workflow tests (M9 step 7) — MILESTONE COMPLETE
`tests/test_private_workflow.py` (5 tests, CPU-only, no network) locks the four
privacy invariants: (a) reports/shadow/private/*.jsonl is gitignored and the
README is not (asserted against .gitignore + `git check-ignore`); (b) redaction
scrubs prompt_preview/output_preview/outcome.notes to `[redacted]` while keeping
prompt_id/policy/mode/booleans/review_meta, doesn't mutate the source, and
`--hash` gives a stable non-reversible tag with no original text; (c) the
aggregate summary carries NO prompt/output text and every `notes` key is an
integer count, with correct level/action distributions and reviewed-only
FLR=0.5 / FHR=0.0 from a SYNTHETIC reviewed fixture (unreviewed rows excluded;
calibration null when 0 reviewed — never fabricated); (d) check_commit_safe
PASSES aggregate/all-null-text/redacted files and FAILS real prompt text +
unredacted notes. Full suite green: 22 tests (decode-stub 4, shadow-wrapper 4,
outcome-review 5, policy-engine 4, private-workflow 5).

### M9 summary — Private real-use logging + review workflow
jlens can now be pointed at a REAL local workload safely: private logs stay in a
gitignored dir, humans review outcomes locally, and only aggregate-only summaries
or explicitly-redacted logs leave the machine — with `check_commit_safe.py` as a
mandatory pre-commit gate. Nothing fabricated (null = unreviewed), no private
text committed, production/final thresholds still gold/audit gated. This is the
mechanism by which reviewed real-use records accumulate to eventually calibrate
and unlock production thresholds. HAND OFF TO HUMAN: run real prompts locally →
review → aggregate/redact → commit-safe share.

## 60. Autonomous supervisor config (M10 step 1)
`config/autonomous_supervisor_v0.json` — placeholder config for the M10 autonomous
shadow supervisor. Explicitly targets `InternScience/Agents-A1-Q8_0-GGUF` via a
local OpenAI-compatible endpoint, and documents (via `_doc` keys, mirroring
config/local_endpoint_example.json) that a GGUF chat endpoint returns output text
ONLY — no router logits — so live tasks get telemetry_missing=true + policy=null,
never fabricated features. Includes task_sources (public fixture + optional
gitignored private queue), verifier toggles (6 adapters + self_consistency_samples),
and escalation thresholds (low_confidence_below 0.55, self_consistency_min_agreement
0.67, high_impact_levels [high,critical], escalate_on_verifier_contradiction). Default
run.log points at the gitignored private dir so raw text stays local. Verified: loads
as JSON; run.log path is git-ignored. No secrets.

## 61. auto_outcome_v1 schema (M10 step 2)
`schema/auto_outcome_v1.json` — NEW draft-07 schema for autonomous supervisor
records; the frozen `shadow_outcome_v1.json` is untouched (verified: it has no
auto_outcome). Carries shadow fields (prompt_id, policy nullable, mode,
local-only prompt/output previews) + `telemetry_missing` (bool; true ⇒ policy
null, no fabricated features) + HUMAN `outcome`/`review_meta` (present but the
supervisor NEVER sets them — stay null) + an `auto_outcome` CANDIDATE object
{auto_judged, auto_was_wrong, auto_needed_retrieval, auto_needed_checker,
verifier_names[], verifier_confidence 0..1, verifier_evidence_hash (hash, never
raw text), escalate_for_review, auto_notes_redacted}. additionalProperties:false
everywhere; null = undecided/unknown. Verified: schema self-checks; a good
record validates; non-bool telemetry_missing, unknown top-level field, unknown
auto_outcome field, and confidence>1 all rejected; an all-null (undecided) auto
record is valid. auto_outcome is a candidate, never gold.

## 62. Verifier adapters (M10 step 3)
`src/verifiers.py` — six cheap adapters, each returning
{name, confidence 0..1, verdict (pass/fail/undecided), evidence_hash}:
exact_answer_match, regex_or_schema_check, math_checker (safe arithmetic-only
eval of a whitelisted expression, else compares final numbers), code_test_stub
(runs a TRUSTED in-process FIXTURE callable only — no arbitrary/untrusted command
execution; low-confidence no-op without a fixture), retrieval_required_heuristic
(flags freshness/current-info tasks → auto_needed_retrieval), and self_consistency
(compares small-N samples; DISAGREEMENT → verdict "undecided" = ESCALATION signal,
never "fail"/proof-of-wrong; confidence = agreement fraction). Evidence is a stable
non-reversible hash of inputs (evidence_hash), NEVER raw text — verified no leak on
a token-bearing input. All adapters verified on fixtures: exact hit/miss/undecided,
regex ok/bad, math expr pass/fail + ref pass + no-number undecided, code
no-fixture/ok/no, retrieval cat+kw/none, self-consistency agree(pass 1.0)/disagree
(undecided 0.667). Verdicts feed the auto_outcome CANDIDATE only — never gold, never
the human fields.

## 63. Autonomous shadow supervisor (M10 step 4)
`src/autonomous_shadow_supervisor.py` runs a task queue against a local endpoint
(dry-run deterministic default / live via config / injectable fake for tests),
and per task: gets model output, attaches telemetry IF a feature row exists else
sets telemetry_missing=true + policy=null (honest GGUF — never fabricates
features), runs enabled+applicable verifiers, assembles an auto_outcome CANDIDATE
(aggregate verifier_confidence; hashed combined evidence), and escalates when
confidence<threshold OR correctness verifiers contradict OR policy level is
high-impact OR self-consistency agreement<min OR auto_was_wrong. HUMAN
outcome/review_meta fields are ALWAYS null — the supervisor never writes them.
Records validate against auto_outcome_v1 and default to the gitignored private
log. Public task fixture data/prompts/autonomous_tasks_sample.jsonl (6 tasks:
math/exact/regex/current-info/plain). Verified end-to-end: 6 valid records,
4 escalated (correctness fails vs the dry-run stub output), telemetry_missing all
true + policy all null, current-info task flagged auto_needed_retrieval, and
human fields confirmed all-null. Advisory/shadow only; auto_outcome is a
candidate, not gold.

## 64. Autonomous run report + committed sample (M10 steps 5–6)
`src/autonomous_outcome_report.py` emits an AGGREGATE-ONLY summary of an
autonomous run: n_total, n_telemetry_missing, level/action distributions
(policy null → "unscored"), verifier_name distribution, escalation count+rate,
auto_field_nonnull_counts, confidence buckets, and auto-vs-human agreement
computed ONLY over human-reviewed rows (null until humans review). Output is
built from fixed numeric/label keys with a recursive no-text-string guard.
Committed sample reports/outcomes/autonomous_summary_sample.json (from the PUBLIC
task fixture run): 6 records, telemetry_missing=6, policy all unscored (honest
GGUF), escalation rate 0.667, auto_was_wrong non-null on 4, auto_vs_human_agreement
null. Verified: zero text-preview/notes keys (leak grep clean); check_commit_safe
PASSES. auto_outcome stays a candidate; production/final thresholds gold/audit gated.

## 65. Autonomous supervisor doc (M10 step 7)
`docs/AUTONOMOUS_SHADOW_SUPERVISOR.md` documents the end-to-end autonomous flow:
config → run supervisor (dry-run public-fixture + live Agents-A1 GGUF examples) →
verifier signal table → auto_outcome-vs-human namespace separation → escalation
triggers → aggregate-only report → check_commit_safe gate. Commands verified vs
real CLI flags (supervisor --config/--tasks/--out/--mode; report --in/--out;
guard positional). States guardrails (auto_outcome candidate not gold; human
fields null; telemetry_missing honest; no real tool exec beyond fixtures; hashed
evidence; private dir gitignored) and gating (production/final thresholds
gold/audit gated until enough human-reviewed records; auto_outcome promoted only
by later audit). Public fixtures in every example.

## 66. Autonomous-supervisor tests (M10 step 8) — MILESTONE COMPLETE
`tests/test_autonomous_supervisor.py` (5 tests, CPU-only, no network, FAKE
in-process endpoints) locks the M10 invariants: (a) a fake-endpoint run yields
auto_outcome_v1-valid records with telemetry_missing=true + policy=null; (b) each
verifier's verdict/confidence on a fixture, self-consistency disagreement =
undecided (escalation) never fail, code stub runs a trusted fixture only, and
evidence is a hash with no raw-text leak; (c) auto_outcome_v1 validates good
records and rejects unknown top-level/auto fields, confidence>1, and non-bool
telemetry_missing; (d) the aggregate summary has NO prompt/output/notes keys and
computes correct counts + escalation (2 of 3 with a deterministic wrong-answer
fake) with auto_vs_human_agreement null until review; (e) auto judgments NEVER
populate the human outcome/review_meta fields, and agreement is computed ONLY
over a SYNTHETIC human-reviewed row. Full suite green: 27 tests (autonomous 5,
decode-stub 4, shadow-wrapper 4, outcome-review 5, policy-engine 4,
private-workflow 5).

### M10 summary — Autonomous shadow supervisor
The manual bottleneck is gone: jlens can now run a task queue autonomously
against a local (Agents-A1 GGUF) endpoint, apply six cheap verifiers, and record
an auto_outcome CANDIDATE per task — with hashed evidence, honest telemetry_missing
when GGUF exposes no router logits, and low-confidence/contradictory/high-impact
cases escalated for later human review. auto_outcome is never gold and never
touches the human outcome fields; only aggregate-only summaries leave the machine,
gated by check_commit_safe. Production/final thresholds remain gold/audit gated.
HAND OFF TO HUMAN: run a local workload → auto_outcome candidates + escalations
accumulate → review the escalated subset → calibration eventually unlocks
production thresholds via a gold audit.

## 67. Agents-A1 shadow-run config + private-dir ignore hardening (M11 step 1)
`config/agents_a1_shadow_run.json` — placeholder run config for a bounded
Agents-A1 GGUF workload: endpoint (alias/base_url/model=InternScience/Agents-A1-Q8_0-GGUF/
api_key placeholder/timeout, documented no-router-logits ⇒ telemetry_missing+policy=null),
task_sources (public smoke batch + optional gitignored private queue), batch
{size 25, cap 100}, verifier toggles + escalation thresholds (reuse M10 shape),
resume {enabled}, deterministic run defaults with all outputs (run_log,
review_queue, run_meta) under the gitignored private dir. Verified: loads;
sha256-over-config run_id stable (cd08d63a145be1d2). Hardened .gitignore:
reports/shadow/private/* (all file types, was *.jsonl only) with
!reports/shadow/private/README.md — closes a gap where a run-meta .json would not
have been ignored. Verified: run_meta.json / run/review .jsonl all ignored, README
still tracked + committed.

## 68. Public smoke batch fixture (M11 step 2)
`data/prompts/agents_a1_smoke_batch.jsonl` — 25 PUBLIC benchmark-style tasks
demonstrating the real workload batch format: 5 math (known_answer+expression),
5 exact_answer (known_answer), 4 format/regex (pattern), 4 current_info, 7 plain
explain. Verified: valid JSONL, every row has prompt_id+prompt, unique ids,
within the batch cap (100). No private text — safe to commit as run input.

## 69. Bounded resume-safe batch runner (M11 step 3)
`src/run_agents_a1_shadow_batch.py` — thin wrapper over
autonomous_shadow_supervisor.run_task: bounds the batch to config batch.size
(≤cap), is RESUME-safe (reads existing run-log prompt_ids, runs only missing
tasks, APPENDS — never rewrites completed rows), records run metadata
(run_id=config sha256, model, endpoint_alias, n_tasks/n_completed/n_failed/
n_telemetry_missing/escalation counts, placeholder timestamps in deterministic
mode), and on a per-task endpoint failure increments n_failed and CONTINUES.
Raw records + run-meta sidecar go to the gitignored private dir; auto_outcome is
a candidate; human fields never written. Verified on the public smoke batch:
run 1 completed=25 escalated=13 telemetry_missing=25 (honest GGUF), all records
auto_outcome_v1-valid; run 2 skipped=25 completed=0 (resume adds zero, log stays
25 lines); run_id stable (cd08d63a145be1d2); injected failing endpoint → n_failed=25
n_completed=0, run continued without crashing; private artifacts unstaged/gitignored.

## 70. Escalation review queue builder (M11 step 4)
`src/make_escalation_review_queue.py` reads a run log and emits a LOCAL,
gitignored review queue containing ONLY records with
auto_outcome.escalate_for_review==true. The auto_outcome candidate is KEPT so the
human reviewer sees why each row escalated; the HUMAN outcome/review_meta fields
are forced null (the reviewer fills them per docs/SHADOW_OUTCOME_REVIEW.md — the
run never does). Verified on the smoke run: 13/25 escalated → queue size 13
(matches run escalation_count), only escalated rows included, human fields all
null, auto_outcome retained, every record auto_outcome_v1-valid, queue gitignored
and unstaged.

## 71. Agents-A1 aggregate run report + committed sample (M11 step 5)
`src/agents_a1_run_report.py` merges run metadata (run-meta sidecar) with run-log
distributions into an AGGREGATE-ONLY report: run_id, model, endpoint_alias,
n_tasks/n_completed/n_failed/n_telemetry_missing, level & action distributions,
auto_verdict_distribution, escalation_count+rate, verifier_distribution,
auto_needed_retrieval/checker/was_wrong counts, human_reviewed_count,
auto_vs_human_agreement (reviewed-only, null until review), privacy_check_status.
Built from fixed numeric/label keys with a recursive no-text guard. Committed
sample reports/outcomes/agents_a1_run_summary_sample.json from the PUBLIC smoke
run: run_id cd08d63a145be1d2, 25 completed, 0 failed, telemetry_missing 25 (honest
GGUF), escalation rate 0.52, agreement null. Verified: zero text keys (leak grep
clean); check_commit_safe PASSES.

## 72. Agents-A1 run doc (M11 step 6)
`docs/AGENTS_A1_SHADOW_RUN.md`: smoke run (deterministic), live run (serve the
Agents-A1 GGUF endpoint on a free port first — the runner never starts models;
leave llama-swap's own models alone), resume/retry behavior, escalated-subset
review (links the M8 review CLI), aggregate report + commit-safe gate, and
guardrails/gating (no private raw logs/text committed; auto_outcome candidate not
gold; human fields never written; telemetry_missing honest; failures counted +
continue; production/final thresholds gold/audit gated). Commands verified vs real
CLI flags. Public fixtures in every example.

## 73. Agents-A1 shadow-run tests (M11 step 7) — HARNESS COMPLETE
`tests/test_agents_a1_shadow_run.py` (5 tests, CPU-only, no network, FAKE
endpoints) locks the M11 harness: (a) run config validates (model=Agents-A1,
batch size≤cap, resume bool, run_id stable 16-hex, batch bound respected);
(b) RESUME — a second run over the same out-log adds zero rows, skips all;
(c) aggregate report has NO text keys + correct metadata counts (n_completed,
n_failed=0, escalation_count) and agreement null until a SYNTHETIC human review
(then n_compared=1, rate 1.0); (d) escalation queue = only escalated rows, human
fields null, all auto_outcome_v1-valid; (e) endpoint-failure path counts n_failed
== n_tasks and continues without crashing. Also fixed test_private_workflow's
gitignore assertion to use `git check-ignore` (README not ignored) after the
private-dir ignore was hardened to `reports/shadow/private/*` + README negation.
Full suite green: 32 tests (agents-a1 5, autonomous 5, decode-stub 4,
shadow-wrapper 4, outcome-review 5, policy-engine 4, private-workflow 5).

### M11 summary — Agents-A1 bounded workload harness
jlens now has a bounded, resumable, privacy-safe run harness: it drives a task
batch through a local Agents-A1 endpoint, records auto_outcome candidates to a
gitignored private log, counts endpoint failures and continues, resumes without
duplicating, emits a local escalation review queue (only-escalated, human-null),
and an aggregate-only run report (no prompt/output text) with full run metadata.
Verified end-to-end on the deterministic smoke path. REMAINING (deliberate,
now-authorized on the 3090s): serve InternScience/Agents-A1-Q8_0-GGUF on a free
port and run the 25-task batch in --mode live, then review the escalated subset —
the reviewed records are what eventually unlock production thresholds via a gold
audit.

## 74. FIRST LIVE Agents-A1 run (M11 capstone) — real 25-task batch
Ran the bounded batch LIVE against the Agents-A1 Q8_0 endpoint already served by
llama-swap on fred (:9069, model id `agents-a1`, Q8_0 no-mtp across both 3090s) —
no model serving needed. run_id 88e140ea5d129bc3: 25/25 completed, 0 failed, all
telemetry_missing (GGUF, no router logits), ~1 min wall. Results (auto_outcome
candidates, NOT gold): math 5/5 and exact-answer 5/5 judged correct; regex 3/4
pass (1 escalated — likely format strictness, not a model error); current_info
correctly flagged auto_needed_retrieval (not judged wrong); open-ended explain
tasks escalated on low confidence (no applicable verifier). escalation_count=7
(rate 0.28): 1 candidate-wrong + 6 unverifiable. Committed public-safe aggregate
reports/outcomes/agents_a1_run_summary_live.json (check_commit_safe clean, no
text). Raw run/review/meta logs stayed in the gitignored private dir. Human
outcome fields untouched (auto never writes them); production thresholds still
gated. NEXT: human-review the 7 escalated rows → first auto-vs-human agreement.

## 75. Live-run insight: regex verifier full-anchor is too strict (M11 follow-up)
The one live auto_was_wrong=True row (sm_regex_01) is a VERIFIER false-positive,
not a model error: Agents-A1 returned a valid JSON object, but
regex_or_schema_check uses `^\{.*\}$` (full-string anchors, no DOTALL), so any
trailing text/newline after the JSON fails the match. This is exactly what the
escalation loop is for — it surfaced an uncertain auto-verdict for human review,
and review shows the auto-verdict was wrong (the model was right). Candidate
improvement for a future milestone (NOT applied here — verifier change is a
deliberate decision): use re.search without ^…$ anchors (+re.DOTALL) or a real
json.loads-based schema check for the JSON case. This is the auto-vs-human loop
working as designed: auto_outcome is a candidate, humans correct it, and the
corrections are the calibration signal.

## 76. JSON-aware verifier (M12 step 1)
Added `json_object_check(output, required_keys, expected_type)` to src/verifiers.py
(fixes the #75 false-positive). Strips whitespace and `json.loads`; on failure,
extracts the FIRST balanced {...}/[...] substring (brace matching that respects
strings/escapes) so trailing prose / markdown fences are tolerated; checks
expected_type (object/array) + required_keys. Returns hashed-evidence verdict
(pass on valid JSON meeting requirements, fail otherwise). regex_or_schema_check
left UNCHANGED for true regex tasks; json_object_check registered in ADAPTERS.
Verified: the live case `{ "result": "success" }` PASSES (was the false-wrong),
valid+trailing-prose PASSES, markdown-fenced PASSES, required-key-present PASSES,
missing-key/garbage/truncated FAIL, array vs object type checks correct, no
evidence text leak. (Also added the missing `import json`.)

## 77. JSON-task routing (M12 step 2)
Routed JSON tasks to the new verifier in autonomous_shadow_supervisor._run_verifiers:
a task with `json_check` true (or `json_required` keys) now runs json_object_check
(with required_keys + optional json_type), and the regex verifier is guarded to
skip json_check tasks — "regex for regex tasks only." Confidence/escalation math
unchanged (additive routing only). Updated data/prompts/agents_a1_smoke_batch.jsonl
sm_regex_01 to task_category "json" + json_check + json_required ["result"] (dropped
the full-anchor pattern). Verified: a JSON task runs json_object_check and NOT regex
(verdict pass on valid JSON+trailing text); a real regex task still runs
regex_or_schema_check; full suite stays green.

## 78. Objective review of the 7 escalated live records (M12 step 3)
Reviewed all 7 M11 escalated rows against PUBLIC benchmark ground truth (operator
review, review_source="operator_review", confidence 1.0) into a gitignored private
queue (agents_a1_reviewed_live.jsonl, all auto_outcome_v1-valid, never staged).
Every output was objectively correct: sm_regex_01 returned valid JSON with the
required `result` key (was_wrong=False — the model was right, confirming #75); the
6 explain tasks (prime number, photosynthesis, water cycle, primary colors,
gravity, water boils at 100°C at sea level) were all factually correct
(was_wrong=False). Agreement-relevant rows are only those where BOTH auto and human
was_wrong are set: sm_regex_01 alone (auto=wrong, human=right) → a single
disagreement, the pre-fix verifier false-positive quantified. The 6 explain rows
had auto_was_wrong=None (escalated on low confidence, no applicable verifier) so
they populate human_reviewed_count but not agreement. Honest: only objectively
determinable ground truth set; null left where undeterminable; auto_outcome stays
a candidate.

## 79. First auto-vs-human agreement (M12 step 4)
Ran agents_a1_run_report over the reviewed escalated queue → public-safe
reports/outcomes/agents_a1_reviewed_summary_sample.json (aggregate-only, no text,
commit-safe). This is the reviewed SUBSET (7 escalated rows), so n_completed=7 /
escalation_rate=1.0 by construction. The headline: FIRST auto_vs_human_agreement =
{n_compared: 1, agreement_rate: 0.0}, human_reviewed_count=7, auto_was_wrong_count=1.
Agreement is 0% on the single comparable row precisely because sm_regex_01's auto
verdict was the #75 false-positive (auto=wrong vs human=right). The 6 explain rows
were reviewed correct but had auto_was_wrong=None (low-confidence escalation, no
verifier) so they don't enter the agreement denominator. This is the pre-fix
baseline; step 5's before/after shows the JSON verifier flipping that row.

## 80. Before/after verifier comparison + CORRECTNESS wiring (M12 step 5)
Completing the fix: json_object_check must be in the supervisor's CORRECTNESS set
or its verdict never feeds auto_was_wrong (a JSON pass left the row undecided).
Added it (it IS a correctness checker; this completes the verifier wiring, it does
not change the escalation formula/thresholds). Public-safe before/after report
reports/outcomes/agents_a1_verifier_beforeafter_sample.json (counts only, no text):
on a representative valid-JSON+trailing-prose output the OLD regex full-anchor
FAILS and json_object_check PASSES, so sm_regex_01 flips wrong→ok and no longer
escalates (auto_was_wrong False, escalate False). Batch impact: escalation 7→6,
auto_was_wrong 1→0 (delta −1/−1). Full suite still green (27 tests). This is the
verifier-quality improvement the M11 finding called for, quantified.

## 81. M12 calibration doc (M12 step 6)
docs/M12_VERIFIER_REVIEW_CALIBRATION.md: the M11 finding, the json_object_check
fix + JSON-vs-regex routing + CORRECTNESS wiring (thresholds unchanged), the
objective operator/ground-truth review of the 7 escalated rows (honesty rules,
null=unreviewed, private text never committed), the first auto-vs-human agreement
(n=1, 0.0 — the false-positive), and the before/after (escalation 7→6, wrong 1→0).
Gating restated (auto_outcome candidate not gold; production/final gold/audit
gated). Public aggregates only in examples.

## 82. M12 verifier-json tests (M12 step 7) — MILESTONE COMPLETE
`tests/test_verifier_json.py` (4 tests, CPU-only, no network): (a) json_object_check
passes valid JSON incl trailing whitespace/prose + markdown fences + required-key,
fails invalid/missing-key/wrong-type, evidence hashed no-leak; (b) routing — json_check
tasks run json_object_check not regex, regex tasks still run regex_or_schema_check;
(c) reviewed aggregate has NO text keys + agreement from a SYNTHETIC reviewed fixture
(n_compared 2, rate 0.5); (d) before/after — the JSON row flips wrong→ok under
json_object_check and no longer escalates. Full suite green: 36 tests (agents-a1 5,
autonomous 5, decode-stub 4, shadow-wrapper 4, outcome-review 5, policy-engine 4,
private-workflow 5, verifier-json 4).

### M12 summary — verifier hardening + reviewed escalation calibration
Closed the loop on the M11 live finding: added json_object_check (json.loads +
balanced-brace extraction, type/required-keys), routed JSON tasks to it and kept
regex for regex only, and wired it into CORRECTNESS so its verdict feeds
auto_was_wrong. Reviewed the 7 escalated live records against public benchmark
ground truth (all correct; honest operator_review; private text never committed),
producing the FIRST auto-vs-human agreement (n=1, 0.0 — the verifier false-positive).
Before/after: the JSON row flips wrong→ok, escalation 7→6, auto_was_wrong 1→0. This
is the auto-vs-human loop doing its job: auto flagged uncertainty, human review
corrected it, and the checker was fixed. auto_outcome stays candidate; production
thresholds gated. NEXT (steer M13): larger live run / calibration from reviewed
records / missing-label converters.

## 83. M13 larger batch generator (M13 step 1)
`src/gen_m13_batch.py` (deterministic, no RNG) → data/prompts/agents_a1_m13_batch.jsonl:
110 PUBLIC tasks across all 6 scorable categories — math 44 (known_answer +
arithmetic expression), exact_answer 20 (facts + known_answer), json 10
(json_check + json_required), regex 8 (pattern), current_info 10, explain 18.
Unique prompt_ids. Verified: count in [100,250], all 6 categories present, required
fields per category, regeneration byte-identical (deterministic), math tasks
self-consistent (known_answer matches expression under math_checker). Public
benchmark-style prompts only.

## 84. M13 run config (M13 step 2)
`config/agents_a1_m13_run.json` — points at the agents-a1 llama-swap endpoint
(:9069, model "agents-a1", timeout 180) and the 110-task public M13 batch; batch
{size 120, cap 250}; verifier toggles with self_consistency_samples=1 (one call
per task → bounds the run at 110 calls; self-consistency skipped at n<2);
escalation thresholds reused; resume enabled; deterministic; private out paths
(run/meta/review) under the gitignored dir. Verified: loads, sha256 run_id stable
(8f702be95736bbe5), private paths gitignored. No secrets.

## 85. M13 LIVE 110-task Agents-A1 run (M13 step 3)
Ran the 110-task batch LIVE against agents-a1 (fred llama-swap :9069) via a capped
model_fn (max_tokens 384, temp 0). run_id cd3d744045af170e: 110/110 completed, 0
failed, all telemetry_missing (GGUF), ~4 min. All records auto_outcome_v1-valid;
human outcome/review_meta all null; private log gitignored + unstaged.
escalation_count 18 (rate 0.164 — DOWN from the 25-task baseline's 0.28).
Per-category (total/escalated/auto_wrong): math 44/0/0, json 10/0/0 (the M12 JSON
verifier fix HOLDS on fresh data — zero false-positives), regex 8/0/0,
exact_answer 20/1/1 (one genuine miss to review), current_info 10/0/0 (correctly
flagged needs-retrieval, not escalated), explain 18/17/0 (unverifiable open-ended,
low-confidence escalation as designed). auto_outcome candidates only; production
thresholds gated.

## 86. M13 aggregate report + escalation queue (M13 step 4)
Public-safe reports/outcomes/agents_a1_m13_summary_sample.json (aggregate-only, no
task text, commit-safe): 110 completed / 0 failed / telemetry_missing 110;
auto_verdict {ok 81, wrong 1, undecided 28}; escalation 18 (rate 0.1636);
verifier_distribution {math_checker 44, retrieval_required_heuristic 110,
exact_answer_match 20, json_object_check 10, regex_or_schema_check 8};
auto_needed_checker 44, auto_needed_retrieval 11, auto_was_wrong 1; agreement null
(pre-review). Escalation queue (gitignored) = 18/110 escalated rows, all escalated,
human outcome/review_meta null. No leak; private unstaged.

## 87. M13 representative escalated-subset review (M13 step 5)
Reviewed a representative 6-row subset of the 18 escalated M13 rows against public
benchmark ground truth (operator_review): the one auto_was_wrong=True row
(m13_e_019, "speed of light in km/s") + 5 explain facts (prime, photosynthesis,
water cycle, primary colors, gravity). All objectively correct → was_wrong=False.
Public reviewed-subset summary reports/outcomes/agents_a1_m13_reviewed_subset_sample.json
(no text, commit-safe): human_reviewed_count 6, auto_vs_human_agreement {n_compared 1,
rate 0.0}. NEW finding: m13_e_019 is another VERIFIER false-positive — Agents-A1
answered 299,792,458 m/s ≈ 299,792 km/s ≈ 300,000 (correct), but exact_answer_match
required the literal "300000" substring and failed. So exact_answer_match is too
strict for APPROXIMATE / unit-converted numeric answers (distinct from the fixed
JSON issue). Candidate for a future milestone (numeric-tolerant exact match) — NOT
applied here. Reviewed subset stays gitignored; auto_outcome candidate; production gated.

## 88. M13-vs-baseline comparison (M13 step 6)
Public-safe reports/outcomes/agents_a1_m13_vs_baseline.json (counts only, no text,
commit-safe): M13 110-task run (run_id cd3d744045af170e) vs the M11/M12 25-task
baseline (88e140ea5d129bc3). Escalation rate fell 0.28 → 0.164 at 4.4× scale;
n_failed 0 both; telemetry_missing all (GGUF). Both have 1 auto_was_wrong but from
DIFFERENT causes: baseline = the JSON verifier false-positive (fixed in M12); M13 =
exact_answer_match strictness on an approximate/unit-converted numeric (model was
right). M13 verifier_distribution now includes json_object_check (10) and JSON tasks
escalated 0 times — the M12 fix validated at scale. auto_needed_checker 5→44 (more
math tasks), auto_needed_retrieval 5→11. auto_outcome candidate; production gated.

## 89. M13 run doc (M13 step 7)
docs/M13_LARGER_AGENTS_A1_RUN.md: deterministic 110-task batch build (6-category
table), live run against the ALREADY-SERVED agents-a1 endpoint on fred (the agent
CALLS it, never serves models), resume/failure handling, aggregate + escalation +
representative-subset review, results (escalation 0.164, JSON 0 escalated, the
exact-match numeric strictness case), baseline comparison, and gating. Commands
match real CLI flags. Public fixtures/aggregates only.

## 90. M13 larger-run tests (M13 step 8) — MILESTONE COMPLETE
`tests/test_m13_larger_run.py` (4 tests, CPU-only, no network): (a) the m13 batch
validates (100-250, unique ids, all 6 categories, per-category required fields,
deterministic); (b) aggregate report over a SYNTHETIC m13-shaped fixture has NO
text keys + correct counts (escalation/wrong/retrieval/checker); (c) resume — a
second run over the same out-log adds zero (fake endpoint), bounded by batch.size;
(d) the committed comparison report has the expected keys + no text. Full suite
green: 40 tests (agents-a1 5, autonomous 5, decode-stub 4, shadow-wrapper 4,
m13 4, outcome-review 5, policy-engine 4, private-workflow 5, verifier-json 4).

### M13 summary — larger Agents-A1 live run
Scaled the live run 25→110 tasks against agents-a1 on fred (deterministic 6-category
batch). Escalation rate fell 0.28→0.164 at 4.4× scale; 0 failures. The M12 JSON
verifier fix held at scale (JSON tasks escalated 0 times). Reviewed a representative
6/18 escalated subset → first M13 auto-vs-human agreement (n=1, 0.0). The one
auto-wrong was a NEW verifier-strictness finding: exact_answer_match rejects
approximate/unit-converted numeric answers (model was right about the speed of
light). Committed public aggregates only (summary, reviewed-subset, vs-baseline);
private detailed/reviewed records stayed gitignored. auto_outcome candidate;
production thresholds gated. NEXT per steer M14: A calibration from reviewed records
/ B broaden scale+diversity / C missing-label converters / D numeric-tolerant +
open-ended verifier coverage (the M13 exact-match finding motivates D).

## 91. Numeric-tolerant verifier (M14 step 1)
Added `numeric_tolerant_check(output, expected_value, tolerance, rel_tolerance,
expected_units, accepted_values)` to src/verifiers.py (fixes the #87/#88 exact-match
numeric strictness). Extracts ALL numbers (thousands separators stripped), optional
simple unit normalization (m/km family), and passes if any extracted/normalized
value is within absolute `tolerance` OR `rel_tolerance` of any accepted target;
FAIL when numbers present but all outside tolerance; UNDECIDED (escalate) when no
number extractable or no target given. Hashed evidence; exact_answer_match left
UNCHANGED; registered in ADAPTERS. Verified 7 cases incl the M13 speed-of-light
(299,792 km/s vs expected 300000 @ rel_tolerance 0.01 → PASS), approx value,
unit-converted (100 C), clearly-wrong (FAIL), no-number (UNDECIDED), no-target
(UNDECIDED), accepted_values exact (PASS); no evidence leak. Full suite green.

## 92. Explain rubric verifier (M14 step 2)
Added `explain_rubric_check(output, required_facts)` to src/verifiers.py: scores an
open-ended explanation ONLY against a public fact checklist — counts required facts
present (case-insensitive), PASS only at full coverage, UNDECIDED/escalate on weak
coverage OR when the rubric is missing/empty. It NEVER claims a subjective
explanation is gold without a rubric (verified: no PASS without required_facts).
Hashed evidence; registered in ADAPTERS. Verified: full-coverage PASS, missing-fact
→ undecided, weak coverage → undecided, no-rubric → undecided, empty-rubric →
undecided; no evidence leak. Full suite green.

## 93. Numeric + explain-rubric routing + CORRECTNESS wiring (M14 step 3)
autonomous_shadow_supervisor._run_verifiers now routes: a task with numeric
metadata (numeric:true OR any of expected_value/tolerance/rel_tolerance/
expected_units/accepted_values) → numeric_tolerant_check; a task with
required_facts → explain_rubric_check; exact_answer_match is guarded to skip
numeric tasks (kept for PURE-STRING exact answers). Added numeric_tolerant_check
and explain_rubric_check to CORRECTNESS so their verdicts feed auto_was_wrong
(completes wiring; escalation/confidence math UNCHANGED). Verified: numeric task →
numeric_tolerant_check (exact avoided); string exact task → exact_answer_match;
explain-rubric task → explain_rubric_check; CORRECTNESS contains both. Full suite green.

## 94. Numeric/rubric public fixture (M14 step 4)
`data/prompts/agents_a1_numeric_batch.jsonl` — 6 PUBLIC rows exercising the new
verifiers: 4 numeric exact-answer tasks (speed of light km/s + rel_tolerance +
expected_units; water boiling point C; Earth circumference km; absolute zero C)
carrying the new optional metadata (numeric, expected_value, tolerance,
rel_tolerance, expected_units, accepted_values), and 2 explain-rubric tasks with
required_facts checklists. Verified: valid JSONL, every row has prompt_id+prompt,
numeric rows route to numeric_tolerant_check (exact_answer_match avoided), rubric
rows route to explain_rubric_check. Public — tracked, no private text.

## 95. Numeric before/after — M13 flip (M14 step 5)
Public-safe reports/outcomes/agents_a1_numeric_beforeafter_sample.json (verdicts/
counts only, no task text; check_commit_safe clean): re-scored the M13 speed-of-light
finding on a representative approximate/unit-converted output. OLD exact_answer_match
= fail (wanted literal "300000"); NEW numeric_tolerant_check = pass (299,792 km/s
within rel_tolerance of 300000). With CORRECTNESS wiring the numeric row flips
auto_was_wrong True→False and escalate True→False — the M13 false-positive is fixed.
(Descriptive note references the public speed-of-light constant, not private text.)

## 96. M14 verifier-coverage doc (M14 step 6)
docs/M14_VERIFIER_COVERAGE.md: the M13 finding, numeric_tolerant_check behavior +
routing, explain_rubric_check strategy (rubric-only, never overclaims), the new
optional task-metadata fields (numeric/expected_value/tolerance/rel_tolerance/
expected_units/accepted_values/required_facts) with a table, the before/after
numeric flip (exact_answer_match fail → numeric_tolerant_check pass), and gating.
Public fixtures/aggregates only.

## 97. M14 numeric-verifier tests (M14 step 7) — MILESTONE COMPLETE
`tests/test_numeric_verifier.py` (5 tests, CPU-only, no network): (a) numeric_tolerant_check
speed-of-light/approx/unit-conversion PASS, clearly-wrong FAIL, no-number/no-target
UNDECIDED, no evidence leak; (b) exact_answer_match still strict for pure strings;
(c) routing — numeric→numeric_tolerant_check (exact avoided), string→exact_answer_match,
explain-rubric→explain_rubric_check, both in CORRECTNESS; (d) explain_rubric_check
full-coverage PASS, missing-fact/no-rubric UNDECIDED, never gold without rubric;
(e) before/after — numeric row flips wrong→ok + de-escalates. Full suite green:
45 tests (agents-a1 5, autonomous 5, decode-stub 4, shadow-wrapper 4, m13 4,
numeric-verifier 5, outcome-review 5, policy-engine 4, private-workflow 5,
verifier-json 4).

### M14 summary — numeric-tolerant verifier + explain coverage
Fixed the M13 exact-match numeric-strictness false-positive with numeric_tolerant_check
(all-number extraction + unit normalization + absolute/relative tolerance +
accepted_values) and added explain_rubric_check (rubric-only fact checklist that
NEVER claims subjective answers gold — escalates on weak/absent coverage). Routed
numeric tasks to the numeric verifier (exact_answer_match kept for pure strings) and
explain-rubric tasks to the rubric verifier, wiring both into CORRECTNESS. Public
numeric/rubric fixture added; before/after shows the speed-of-light row flips
wrong→ok + de-escalates. Two verifier-strictness false-positives (JSON in M12,
numeric here) are now both fixed — the auto-vs-human loop found them, humans
confirmed, and the checkers improved. auto_outcome candidate; production gated.
NEXT per steer M15: A larger run (250-500) / B calibration / C label converters /
D retrieval+checker actions for current-info.

## 98. M15 larger batch generator (M15 step 1)
`src/gen_m15_batch.py` (deterministic, reuses M13 pools) → data/prompts/agents_a1_m15_batch.jsonl:
261 PUBLIC tasks across ALL 8 category types — math 160, exact_answer(string) 20,
numeric 20 (numeric+expected_value+tolerance/rel_tolerance+expected_units,
approximate/unit-converted to exercise M14 numeric coverage), json 10, regex 8,
current_info 10, explain 18, explain-rubric 15 (required_facts checklists to
exercise M14 explain coverage). Unique prompt_ids. Verified: count in [250,500],
all category types present, required fields per category, numeric rows route to
numeric_tolerant_check + rubric rows to explain_rubric_check, regeneration
byte-identical (deterministic). Public prompts only.

## 99. M15 run config (M15 step 2)
`config/agents_a1_m15_run.json` — agents-a1 llama-swap endpoint (:9069, model
"agents-a1", timeout 180) + the 261-task public M15 batch; batch {size 300, cap
500}; all verifier toggles incl numeric_tolerant_check + explain_rubric_check,
self_consistency_samples=1 (261 calls); escalation thresholds reused; resume
enabled; deterministic; private out paths (run/meta/review) gitignored. Verified:
loads, sha256 run_id stable, private paths gitignored. No secrets.

## 100. M15 LIVE 261-task Agents-A1 run (M15 step 3) — both verifier fixes HOLD at scale
Ran the 261-task batch LIVE against agents-a1 (fred llama-swap :9069) via a capped
model_fn. run_id 25ca35429474c407: 261/261 completed, 0 failed, all telemetry_missing
(GGUF), ~8 min. All records auto_outcome_v1-valid; human fields all null; private log
gitignored + unstaged. escalation_count 19 (rate 0.073 — DOWN again from M13's 0.164
and M11's 0.28). HEADLINE: json auto_was_wrong=0 AND numeric auto_was_wrong=0 — the
M12 JSON fix and M14 numeric fix BOTH HOLD at scale. Per-verifier-category
(total/escalated/auto_wrong): math 160/0/0, numeric 20/0/0 (approx/unit-converted
answers pass cleanly), json 10/0/0, regex 8/0/0, exact 20/1/1 (one string miss to
review), current_info 10/0/0 (flagged needs-retrieval), explain 18/17/0 (unverifiable
open-ended), rubric 15/1/0 (explain_rubric_check escalated 1 weak-coverage as designed).
The escalation rate has fallen monotonically 0.28→0.164→0.073 as verifier coverage
improved. auto_outcome candidates only; production thresholds gated.

## 101. M15 aggregate report + escalation queue (M15 step 4)
Public-safe reports/outcomes/agents_a1_m15_summary_sample.json (aggregate-only, no
task text, commit-safe): 261 completed / 0 failed / telemetry_missing 261;
auto_verdict {ok 231, wrong 1, undecided 29}; escalation 19 (rate 0.0728);
verifier_distribution {math_checker 160, retrieval_required_heuristic 261,
exact_answer_match 20, numeric_tolerant_check 20, json_object_check 10,
regex_or_schema_check 8, explain_rubric_check 15} — all 7 verifiers active at scale
incl the two M14 additions; auto_needed_checker 160, auto_needed_retrieval 12,
auto_was_wrong 1; agreement null (pre-review). Escalation queue (gitignored) =
19/261, all escalated, human null. No leak; private unstaged.

## 102. M15 representative escalated-subset review (M15 step 5)
Reviewed a representative 6/19 escalated M15 subset against public benchmark ground
truth (operator_review): m15_e_019 (speed of light, STRING exact) + m15_k_003
(gravity, rubric) + 4 explain facts. All objectively correct → was_wrong=False.
Public reviewed-subset summary reports/outcomes/agents_a1_m15_reviewed_subset_sample.json
(no text, commit-safe): human_reviewed_count 6, auto_vs_human_agreement {n_compared 1,
rate 0.0}. TWO instructive escalations:
(1) m15_e_019 auto_was_wrong=True is a TASK-METADATA GAP, not a verifier bug — this
speed-of-light row comes from the reused M13 exact_tasks pool WITHOUT numeric
metadata, so it routes to exact_answer_match (strict) instead of the M14
numeric_tolerant_check. The numeric-TAGGED version (numeric pool, 20/20) passed. Fix:
tag numeric-answer exact benchmark rows with numeric metadata (candidate for a later
milestone).
(2) m15_k_003 (rubric) escalated but did NOT claim wrong — the model said "fundamental
interaction" where the rubric keyword was "force" (synonym not matched). explain_rubric_check
correctly escalated for review rather than falsely marking wrong — working as designed;
suggests rubric facts could allow synonyms later. auto_outcome candidate; production gated.

## 103. M15-vs-both-baselines comparison (M15 step 6)
Public-safe reports/outcomes/agents_a1_m15_vs_baseline.json (counts only, no text,
commit-safe): M15 (261 tasks, run_id 25ca35429474c407) vs M13 (110,
cd3d744045af170e) vs M11/M12 (25, 88e140ea5d129bc3). HEADLINE — escalation_rate_trend
[0.28, 0.1636, 0.0728] fell monotonically across the three live runs as verifier
coverage improved. n_failed 0 all; telemetry_missing all (GGUF). Both prior
verifier false-positives stayed FIXED at scale: JSON auto_was_wrong=0 (M12 fix),
numeric-TAGGED auto_was_wrong=0 (M14 fix). M15's single auto_was_wrong is a
task-metadata gap (untagged string-exact numeric row), not a regression. M15
verifier_distribution adds numeric_tolerant_check (20) + explain_rubric_check (15).
auto_outcome candidate; production gated.

## 104. M15 run doc (M15 step 7)
docs/M15_LARGER_AGENTS_A1_RUN.md: deterministic 261-task batch build (8-category
table with verifier mapping), live run against the already-served agents-a1 on
fred (call-endpoint-never-serve), resume/failure handling, aggregate + escalation
+ representative-subset review, two-baseline comparison, results (escalation trend
0.28→0.164→0.073; both fixes held; task-metadata-gap + rubric-synonym findings),
and gating. Commands match real CLI flags. Public fixtures/aggregates only.

## 105. M15 larger-run tests (M15 step 8) — MILESTONE COMPLETE
`tests/test_m15_larger_run.py` (4 tests, CPU-only, no network): (a) the m15 batch
validates (250-500, unique ids, all 8 category types incl numeric + explain-rubric,
per-category required fields, deterministic); (b) aggregate report over a SYNTHETIC
m15-shaped fixture has NO text keys + correct counts incl verifier_distribution with
the M14 verifiers; (c) resume — a second run over the same out-log adds zero (fake
endpoint), bounded by batch.size; (d) the committed comparison report has the M15/M13/
baseline keys + escalation_rate_trend + no text. Full suite green: 49 tests.

### M15 summary — larger Agents-A1 live run after verifier fixes
Scaled the live run to 261 tasks (8 categories incl the M14 numeric + explain-rubric)
against agents-a1 on fred: 261/261 completed, 0 failed. The decisive result — BOTH
prior verifier false-positives stayed fixed at scale (JSON auto_was_wrong=0, numeric-
tagged auto_was_wrong=0), and the escalation rate fell monotonically across three live
runs (0.28 → 0.164 → 0.073) as verifier coverage improved. Reviewed a representative
6/19 escalated subset → agreement n=1 rate 0.0, driven by a TASK-METADATA gap (a reused
string-exact numeric row lacking numeric metadata) rather than a regression; a rubric
row escalated correctly on a synonym. Committed public aggregates only (summary,
reviewed-subset, two-baseline comparison); private records stayed gitignored.
auto_outcome candidate; production gated. NEXT per steer M16: A calibration / B
retrieval+checker actions / C label converters / D broader model comparison — plus a
small fixture fix (tag numeric-answer exact rows with numeric metadata) is now motivated.

## 106. Task-metadata validator (M16 step 1)
`src/validate_task_metadata.py` detects the M15 numeric-metadata gap: exact_answer
rows whose known_answer is a clean numeric value but which carry NO numeric
metadata (so they route to strict exact_answer_match instead of
numeric_tolerant_check). Also basic sanity (numeric rows need expected_value; json
rows need json_required). Reports offending prompt_ids (non-sensitive), exits
nonzero on issues. Verified on the current data/prompts/agents_a1_m15_batch.jsonl:
FLAGS 7 numeric-looking exact rows including m15_e_019 (speed of light, "300000")
plus continents/hexagon/freezing-point/sqrt-81/leap-year/smallest-prime. These are
exactly the reused string-exact numeric rows behind the M15 finding; step 2 tags
them so they route to numeric_tolerant_check.

## 107. Generator metadata-normalization (M16 step 2)
Added `normalize_numeric_metadata(rec)` to gen_m13_batch (imported + applied by
gen_m15_batch): deterministically tags numeric-answer exact_answer rows with
numeric=true + expected_value (parsed from known_answer) + default tolerance
(rel_tolerance 0.01 when |value|>=1000, else absolute 0.5); non-numeric answers
(Paris, Au) untouched. Regenerated data/prompts/agents_a1_m15_batch.jsonl (+ m13):
validate_task_metadata now reports ZERO gaps. 7 exact rows moved to numeric routing
(M15 category mix: exact_answer 20→13, numeric 20→27). m15_e_019 (speed of light) now
{numeric, expected_value 300000, rel_tolerance 0.01} → routes to numeric_tolerant_check
(exact_answer_match avoided). Batch still deterministic, count 261. Full suite green.

## 108. action_record_v1 schema (M16 step 3)
`schema/action_record_v1.json` — NEW draft-07 schema for READ-ONLY/PLANNED action
records (separate from frozen schemas): {task_id, action_type (enum
retrieval_needed|checker_needed|no_action|review_needed), reason_code,
source_verifier nullable, confidence nullable 0..1, status (enum
planned|skipped|completed|failed), evidence_hash nullable}. additionalProperties:false;
NO raw task-text field. Verified: schema self-checks; good record validates;
unknown field, bad action_type/status enum, and confidence>1 rejected; minimal
required-only record valid. status default "planned" (read-only); completed/failed
only ever from an approved deterministic action, never fabricated.

## 109. Read-only action router (M16 step 4)
`src/action_router.py` derives a PLANNED action_record (action_record_v1) from an
auto_outcome candidate — READ-ONLY, executes nothing by default. Rules:
auto_needed_retrieval → retrieval_needed (planned, source retrieval_required_heuristic);
else auto_needed_checker → checker_needed ONLY if an APPROVED deterministic checker
(math_checker/json_object_check/numeric_tolerant_check) is present, else status
"skipped"; else escalate_for_review → review_needed; else no_action. Evidence hashed;
no raw task text. Verified 5 cases (current-info→retrieval_needed; math/numeric→
checker_needed approved; checker-with-no-approved→skipped; escalated explain→
review_needed; clean→no_action) — all schema-valid. Current-info always yields a
retrieval_needed record (base answer never treated as sufficient).

## 110. Before/after metadata cleanup (M16 step 5)
Public-safe reports/outcomes/agents_a1_m16_metadata_beforeafter_sample.json (counts/
verdicts only, no task text, commit-safe): M16 normalization NEWLY tagged 7 reused
exact_answer rows (m15_e_008/009/014/016/017/018/019) with numeric metadata so they
route to numeric_tolerant_check instead of strict exact_answer_match. (The 20 m15_n_
numeric-pool rows already carried numeric metadata pre-M16 — excluded from the count
to stay honest.) The speed-of-light row (m15_e_019) flips old exact_answer_match FAIL
-> new numeric_tolerant_check PASS, auto_was_wrong False, no longer escalates — the
M15 task-metadata gap is closed. First pass over-counted (27) by stripping metadata
from the already-numeric pool; corrected to 7 newly-tagged.

## 111. Action-routing summary (M16 step 6)
Public-safe reports/outcomes/agents_a1_m16_action_summary_sample.json (aggregate-only,
no task text, commit-safe): read-only action routing over the M15 run (261 records,
router executes nothing — all status "planned"). action_type distribution:
checker_needed 160 (all approved deterministic checkers, 0 skipped), no_action 70,
review_needed 19, retrieval_needed 12. The 12 current-info tasks each yield a
retrieval_needed record — the base model answer is never treated as sufficient. The
160 math tasks route to an approved checker (math_checker); the 19 escalations →
review_needed. Verifier signals are now turned into safe planned next-actions.
auto_outcome candidate; production gated.

## 112. M16 action-routing doc (M16 step 7)
docs/M16_ACTION_ROUTING.md: the metadata validator + generator normalization (numeric
exact rows tagged, zero gaps, speed-of-light flip), the action_record_v1 schema + fields,
the READ-ONLY action-router rules table (retrieval_needed always for current-info;
checker_needed approved-only else skipped; review_needed; no_action) with the M15 action
distribution, and gating (actions read-only/planned; current-info never faked; auto_outcome
candidate; production gated). Commands match real CLI flags. Public fixtures/aggregates only.

## 113. M16 action-routing tests (M16 step 8) — MILESTONE COMPLETE
`tests/test_action_routing.py` (5 tests, CPU-only, no network): (a) validator flags a
numeric-looking exact row missing metadata, ignores non-numeric answers, and passes the
cleaned M15 batch; (b) generator normalization tags numeric exact rows (untouched for
non-numeric) and they route to numeric_tolerant_check; (c) action_record_v1 validates
good records + rejects bad enum/unknown fields; (d) action_router — current-info→
retrieval_needed, math→checker_needed(approved), checker-with-no-approved→skipped,
escalated→review_needed, clean→no_action, all schema-valid; (e) the M16 aggregate
artifacts have no text keys. Full suite green: 54 tests.

### M16 summary — action routing + metadata cleanup
Closed both M15 loose ends. (1) Metadata: a validator now detects numeric-looking
exact_answer rows missing numeric metadata, and a deterministic generator normalization
tags them (7 reused exact rows moved exact→numeric; validator reports zero gaps; the
speed-of-light row flips exact-match fail→numeric pass and de-escalates). (2) Action
routing: a READ-ONLY action_router turns verifier signals into PLANNED action records
(schema action_record_v1) — current-info→retrieval_needed (base answer never treated as
sufficient), checker→approved deterministic checkers only (else skipped), escalated→
review_needed, clean→no_action. Over the M15 run: checker 160 / no_action 70 / review 19 /
retrieval 12, all planned (nothing executed). auto_outcome candidate; production gated.
NEXT per steer M17: A calibration / B 500-task run with action routing / C label converters
/ D broader model comparison.

## 114. Reviewed calibration report (M17 step 1)
`src/reviewed_calibration_report.py` consolidates the M11-M16 reviewed logs (read
locally, gitignored) into a CATEGORY-LEVEL summary — aggregate-only, built from
fixed numeric/label keys with a recursive no-text guard. Over 44 records scanned,
19 human-reviewed, 3 comparable (both auto+human was_wrong set). Per category:
exact reviewed 2/comparable 2/agreement 0.0/usable_shadow; regex reviewed
1/comparable 1/agreement 0.0/usable_shadow; explain-rubric reviewed 1/comparable
0/needs_more_review; open-explain reviewed 15/comparable 0/verifier_gap. The exact
+ regex 0.0-agreement rows are exactly the two false-positives review FOUND and that
are now FIXED (JSON M12, numeric M14+M16) — honest historical disagreements.
open-explain has no objective verifier (verifier_gap). Folds in M16 action-routing
PLANNED-only counts (retrieval 12/checker 160/review 19/no_action 70). Leak grep +
no-text guard clean; commit-safe.

## 115. Committed reviewed-calibration summary (M17 step 2)
reports/outcomes/agents_a1_reviewed_calibration_summary.json committed (public-safe,
aggregate-only): 44 scanned / 19 reviewed / 3 comparable; per-category exact
(2/2, agreement 0.0, usable_shadow), regex (1/1, 0.0, usable_shadow), explain-rubric
(1/0, needs_more_review), open-explain (15/0, verifier_gap); fixed_findings (JSON M12,
numeric M14+M16), remaining_gaps (open-explain verifier_gap, rubric synonyms),
action_routing_planned_only (retrieval 12/checker 160/review 19/no_action 70).
Verified: recursive no-text guard PASS, leak grep clean, agreement only where
comparable, check_commit_safe PASS, no private staged.

## 116. M17 reviewed-calibration doc (M17 step 3)
docs/M17_REVIEWED_CALIBRATION.md: what the reviewed data says (44 scanned/19
reviewed/3 comparable; per-category table), the two found-by-review-and-fixed
verifier false-positives (JSON M12, numeric M14+M16), category maturity
(usable_shadow: exact/numeric/json/math/regex; needs_more_review: explain-rubric
synonyms; verifier_gap: open-ended explain), the M16 action-routing planned-only
counts, and gating. Public fixtures/aggregates only. Commands match real flags.

## 117. M17 reviewed-calibration tests (M17 step 4) — MILESTONE COMPLETE
`tests/test_reviewed_calibration.py` (4 tests, CPU-only, no network): (a)+(d) per_category
grouping + agreement only where comparable (synthetic exact fixture: 2 reviewed/2
comparable/agreement 0.5; open-explain 1 reviewed/0 comparable/null/verifier_gap);
(b) the committed summary passes the recursive no-text guard + agreement only where
comparable; (c) category_of maps verifier_names→category correctly (numeric/json/exact/
math/regex/explain-rubric) with task_category tiebreaker (current_info→retrieval,
explain→open-explain); (e) action counts carried as planned-only ints, fixed_findings +
remaining_gaps present. Full suite green: 58 tests.

### M17 summary — reviewed calibration pass
Consolidated the M11-M16 reviewed subsets into a public-safe category-level calibration
summary (private logs read locally, never committed). Headline: of 44 records scanned,
19 human-reviewed, only 3 objectively comparable — and those 3 (exact 2 + regex 1,
agreement 0.0) are exactly the two verifier false-positives review FOUND and that are
now FIXED (JSON M12 json_object_check; numeric M14 numeric_tolerant_check + M16 metadata
normalization). Category maturity: usable_shadow (exact/numeric/json/math/regex — known
false-positives fixed); needs_more_review (explain-rubric — synonym matching basic);
verifier_gap (open-ended explain — no objective verifier, the biggest remaining gap).
M16 action-routing PLANNED-only counts folded in (retrieval 12/checker 160/review 19/
no_action 70). auto_outcome candidate; production/final thresholds gold/audit gated —
this summary is the honest per-category scoreboard of how close to gating-unlock the
reviewed data is. NEXT per steer M18: A 500-task run w/ action routing / B retrieval+checker
execution / C label converters / D broader model comparison.

## 118. Post-M17 CLI bugfix — main() referenced renamed key
`src/reviewed_calibration_report.py:main()` still printed `summary['total_reviewed_records']`,
a key removed during the step-1 honesty rename to `total_records_scanned`/
`total_reviewed`/`total_comparable`. Running the script directly (not via `build()`,
which tests call) raised `KeyError`. Fixed the print line to use the three current
keys. Verified: CLI now runs clean (`44 scanned, 19 reviewed, 3 comparable`); regenerated
output is byte-identical (`diff`) to the already-committed summary, so this is a
pure code fix with no data change. Full suite still green (58 tests); check_commit_safe
PASS.

## 119. M18 aggregate-safe action results + explicit opt-in executor
`schema/action_result_v1.json` + `src/action_executor.py`: execution defaults OFF
(`execution_disabled`) and requires explicit `--execute`. Retrieval can only use
the read-only FixtureRetrievalAdapter with fixture/public_fixture source kinds;
checkers resolve through a fixed allowlist (math/json/numeric). No subprocess,
shell, dynamic import, arbitrary callable, or model-command surface. Results link
to action records but contain only ids/enums/confidence/hashes, never raw context
or output; candidate-only, production gated.

## 120. M18 planned-versus-executed replay
Public-safe `agents_a1_m18_action_execution_summary.json`: replayed the M16 M15-run
distribution (261 planned). 172 executed through approved paths: retrieval 12/12
via fixture adapter and checker 160/160 via math_checker. 89 intentionally skipped:
19 human-review + 70 no-action. All retrieval completions keep followup_needed=true
because fixture context availability is not answer correctness — grounded
regeneration remains required.

## 121. Historical checker replay limitation is now explicit
M15 private records retain only 160-character output_preview values, so the M18
checker replay's 70 pass/90 fail split is NOT a correctness measurement (many final
answers were truncated). The aggregate marks checker_input_mode=
legacy_truncated_preview_replay and correctness_interpretation=
not_valid_from_legacy_truncated_previews. Future M19 live execution must pass full
output transiently into the executor before truncation/logging; no attempt was made
to relabel preview artifacts as model failures.

## 122. M18 safe-action tests + milestone complete
`tests/test_action_execution.py` adds 6 CPU/no-network tests: action_result schema +
disabled-by-default, fixture retrieval with no text leak, approved deterministic
checker execution, malicious expression/fixture callable cannot execute, retrieval
source allowlist/missing-adapter refusal, and aggregate before/after/no-text checks.
M18 doc records the safety contract, commands, replay results, preview limitation,
and unchanged production/human-review gates. Full suite green: 64 tests; all 261
private action results validate against action_result_v1; public M18 artifacts pass
check_commit_safe.

## 123. M19 transient full-output action path
`autonomous_shadow_supervisor.run_task(return_full_output=True)` now returns full
output only to the private runner. With actions explicitly enabled, the runner
routes + executes the approved action before writing the bounded runtime preview;
only action_result_v1 persists. Actions remain disabled in other configs. Resume
requires both runtime prompt_id and action-result task_id. No shell/network
retrieval/dynamic callable surface added.

## 124. M19 deterministic 500-task workload + live completion
`gen_m19_batch.py` + `agents_a1_m19_run.json`: cleaned M15 261 baseline plus 239
unique added tasks = 500 (math360/exact50/explain43/current20/json10/numeric9/
regex8), metadata validator clean. Live run c20512612a978d60 against already-served
agents-a1 completed 500/500, 0 endpoint failures, telemetry_missing 500, policy
null 500, escalated 27 (0.054 vs M15 0.0728). Private detailed logs remain ignored.

## 125. Full-output checker results replace the invalid M18 preview split
M19 executed 360 allowlisted math checks on transient FULL output: 356 pass / 4
fail. The four compact wrong answers are objective candidates (2062 vs 1972; 863
vs 862; 3365 vs 3345; 3052 vs 3032), not truncation artifacts. auto_outcome and
action_result remain candidates pending human calibration; no gold promotion.

## 126. Retrieval reporting separates current-info from heuristic false positives
23 fixture retrievals completed, but only 20 were actual current_info tasks. Three
non-current routes are reported separately: weather/climate explain x2 (keyword
`weather`) and a static discount numeric task (keyword `price`). Current-info path
coverage is 20/20; every row still needs grounded regeneration. Fixture completion
is not answer correctness.

## 127. M19 aggregate reports, tests, and milestone completion
Public-safe reports: M19 run summary, action execution summary, and M15/M18
baseline comparison. `tests/test_m19_live_full_output.py` covers deterministic
500-task generation/metadata, full-output checker handoff with no raw persistence,
paired resume, disabled actions, fixture-only wildcard retrieval, aggregate
no-text/baseline interpretation, and current-info separation. Production remains
gated; detailed records and retrieval payload stay gitignored.

## 128. M20 aggregate-safe grounded-result contract
`schema/grounded_result_v1.json` + `src/grounded_regenerator.py`: regeneration
defaults OFF and accepts only completed retrieval actions for true current_info
tasks through FixtureRetrievalAdapter. Context and grounded output stay transient;
records contain action linkage, source/model enums, verifier verdicts, change flag,
confidence, hashes, follow-up/error, candidate_only=true. No raw text schema fields.

## 129. M20 controlled live grounded regeneration
Local agents-a1 processed the M19 retrieval subset: 23 candidates -> 20 true
current-info grounded calls completed + 3 non-current false positives skipped
before model invocation. 20/20 current-info rows produced answers and all 20 changed
from the stored original preview. Detailed results + fixture remain gitignored.

## 130. Generic fixture context exposes grounding-quality limit
All 20 completed grounded outputs were checked for the controlled fixture expected
token: 4 pass / 16 fail (0.20). The generic fixture established a response token
but did not provide question-specific real-world evidence; many outputs treated it
as insufficient or omitted the token. This is execution-path quality, NOT real-
world answer correctness. Follow-up needed: 16 fails + 3 skipped = 19.

## 131. Reviewed M19 misses and retrieval false positives
Public M20 review summary: four full-output arithmetic misses rechecked against
deterministic task metadata -> 4 confirmed wrong candidates, 0 gold promotions.
Three retrieval false positives confirmed (explain weather x2, numeric price x1).
Freshness regex removes bare weather/price/stock/news triggers while preserving
explicit current_info routing and temporal-expression detection.

## 132. M20 summaries, tests, and milestone completion
Public grounded + review summaries are aggregate-only and no-text; existing private
results can rebuild them via `--summarize-existing` without model calls. Six M20
tests cover default-off, transient fixture context/no text leak, non-current no-call,
grounding-quality aggregation, 4+3 review summary, and heuristic refinement.
All 23 private results validate grounded_result_v1; public artifacts pass
check_commit_safe; full suite 76/76 green. auto/action/grounded results remain
candidates; production gated.

## 133. M21 backend separation + no-download loader contract
New `hf_telemetry_record_v1` / `hf_telemetry_backend.py` keeps HF internal
telemetry separate from GGUF auto_outcome runtime records. GGUF descriptor stays
telemetry_access=missing. HF loader accepts only an existing safetensors directory
or explicitly approved cached ID and always passes local_files_only=true +
trust_remote_code=false. Unapproved IDs fail before Transformers; zero downloads,
weights, licenses, or hardware choices in M21.

## 134. Logits/decode telemetry is numeric and aggregate-only
Backend captures final entropy, selected-token probability/id, top-k mass/margin,
and decode-window mean entropy/high-entropy/low-confidence counts/margin trend.
Record schema excludes prompt, token text, full output, model path, raw logits,
hidden vectors, router vectors, and weights. Model/evidence references are hashed;
candidate-only and production-gated.

## 135. Router/hidden telemetry is capability-honest
Hidden summaries are captured only when enabled + present; otherwise disabled or
missing. Dense fixture reports router=not_moe. Fake MoE reports real fixture-derived
router entropy, expert concentration, top expert IDs, and first-to-last expert
shift. MoE hook refusal reports unsupported; absent unknown data reports missing.
No router/expert data is inferred from dense or unavailable sources.

## 136. M21 fixture batch + summary
Three in-memory records validate v1: dense (logits available/hidden disabled/
router not_moe), MoE (all available), unknown (logits+hidden+router missing).
Public hf_fixture_summary: weights_loaded=0; logits 2/1; hidden 1 available/1
disabled/1 missing; router 1 available/1 not_moe/1 missing; alignments auto2/
action2/grounded1/reviewed0. No raw text/tensors persisted.

## 137. M21 tests + real-model stop gate
Eight tests cover telemetry math/window aggregates, missing/disabled states,
dense/MoE/unsupported router handling, unapproved/no-safetensors refusal,
no-download loader flags, schema/no-text/backend separation, and no tracked model
weights/caches. A real dense/MoE run now requires operator-selected local path or
approved cached model ID plus hardware/VRAM approval; autosteer must stop there.

## 138. M22 approved real MoE fits dual 3090s without offload
Operator approved MoE, GPU-first execution, model choice/download, and Thor
storage. Qwen1.5-MoE-A2.7B-Chat (`qwen2_moe`, 14.3B total/2.7B active) occupies
about 27 GiB on the external Thor mount. BF16 placement used roughly 14.9/13.9
GiB across dual 3090s under a 20 GiB/GPU cap; no CPU/disk offload or hidden-state
capture. llama-swap was temporarily unloaded and agents-a1 was restored/verified.

## 139. Real logits and router telemetry validate end to end
Eight shared M19 IDs completed four greedy decode steps each. Every capture exposed
24 router layers with 60 real expert logits per decoded token. M22 converts full
vocabulary distributions to capture-time entropy/probability/top-k scalars and
raw router rows to aggregate router entropy/concentration/top-expert shift. All 8
schema records validate; logits and router statuses are available 8/8, hidden is
honestly disabled 8/8. Detailed records and raw captures remain gitignored.

## 140. Tiny alignment shows logits movement, not a telemetry policy
Alignment coverage is auto8/action8/grounded1/reviewed1. Checker-needed rows (n=2)
show lower mean decode entropy than not-needed rows (0.6767 vs 1.3162) and lower
final selected probability (0.6943 vs 0.8056), but router entropy is effectively
unchanged (3.4300 vs 3.4277). Retrieval and review positives are each n=1. These
labels came from agents-a1 outcomes on the shared IDs while telemetry came from
Qwen, so the result measures cross-model task-demand association, not whether
Qwen telemetry predicts Qwen errors. These are selected-sample observations only:
no predictive value, threshold, calibration, or production usefulness is claimed.

## 141. Public M22 artifacts remain aggregate-only
`hf_m22_real_summary.json` records completion/capability distributions, aggregate
means, hardware class, and alignment coverage. `hf_m22_alignment.json` records
category counts and action/need group means. Neither includes IDs, text, local
paths, tensors, or model weights. Candidate-only outcome sources and the production
gate remain unchanged.

## 142. M22 tests and milestone completion
Five new CPU/no-network tests cover precomputed scalar conversion, real-router
aggregation, honest missing/unsupported states, the fixed shared eight-task batch,
candidate alignment, aggregate grouping, and no-text/path/tensor public reports.
Decode-capture tests now require top-k mass/margin fields. Full suite: 89/89 green.

## 143. M23 removes the cross-model outcome confound
The predeclared manifest fixes 32 existing public IDs into checker/retrieval/review/
control groups of eight before telemetry inspection. Capture now applies the Qwen
chat template and stores its bounded decoded output only in ignored `.pt` files.
That same output is passed to the existing verifier/action path while telemetry is
derived from the same decode. Qwen signals are no longer aligned to agents-a1 output.

## 144. Same-run Qwen batch completes with balanced actual actions
All 32 BF16 dual-GPU captures completed with real logits and 24×60 router telemetry;
hidden states remained disabled. Actual routes exactly matched checker8/retrieval8/
review8/no-action8. The safe executor completed all 8 checker and all 8 fixture-
retrieval actions; review/no-action stayed unautomated. Arithmetic verdicts: 7 pass,
1 fail. agents-a1 was restored and verified after the capture window.

## 145. Decode cap is isolated from objective checker results
Nine tasks reached 64 generated tokens: 3 retrieval and 6 review. All 8 checker
tasks reached EOS in 10–15 tokens and all controls ended before the cap. Therefore
the 7/1 checker split uses complete captured checker outputs. Retrieval labels come
from current-info metadata and review labels from the existing no-rubric/low-
confidence path; capped prose is not represented as a complete answer.

## 146. Router features separate selected task-demand groups descriptively
Against their n=24 complements, checker-needed router entropy is higher (g=+1.896)
and expert concentration lower (g=-1.932); retrieval-needed router entropy is lower
(g=-1.370) and concentration higher (g=+1.276); review-needed router entropy is
lower (g=-1.017) and concentration higher (g=+0.892). Fixed-seed bootstrap mean-
difference intervals exclude zero for these effects. Checker decode entropy is
also lower (g=-1.064); retrieval/review logits intervals span zero.

## 147. Separation is not yet predictive value
Task category, prompt form, output length, and action-rule applicability remain
confounds. The labels are intentionally driven by trusted metadata/verifier scope,
so M23 proves same-run linkage and descriptive association, not generalization or
causality. Checker failure analysis is withheld because fail/pass is n=1/7, below
the frozen minimum of four per group. No policy or threshold was fit.

## 148. M23 public/private boundary
The public manifest contains public IDs and group names only. Public summary and
alignment reports contain aggregate counts, means/medians, effect sizes, and
bootstrap intervals only. Selected prompts, decoded outputs, token IDs/text, raw
tensors, paths, and all 32 detailed runtime/action/result/telemetry rows stay in
ignored locations. Candidate-only and production gates remain unchanged.

## 149. M23 tests and milestone completion
Six M23-related CPU/no-network tests cover the fixed balanced manifest, same-capture
telemetry/output association, full-output checker handoff before private preview
truncation, four-schema validation, resume/invalid capture detection, honest missing
telemetry, predeclared effect gating, and public no-ID/text/path/tensor reporting.
Chat-template capture also has a stub test. Full suite: 95/95 green.

## 150. M24 preregistration correction is preserved before holdout
The first 48-ID manifest referenced unavailable source IDs. Validation caught this
before any M24 model load or telemetry inspection. Git history preserves that
manifest and a transparent pre-run correction to 40 source-resolved, M23-disjoint
IDs (10/class). Model, feature sets, nearest-centroid recipe, and metrics did not
change. This is a preregistration correction, not post-result task selection.

## 151. Frozen M23 classifier protocol
Three classifiers use M23 mean/sample-SD standardization and balanced action-class
centroids: full five features, logits-only three, and router-only two. Squared
Euclidean prediction with lexical ties is fixed. Code fits all models from the 32
M23 private records before reading any M24 capture; holdout cannot update centroids,
scales, features, thresholds, or class priors.

## 152. M24 real holdout completes with honest cap/action drift
All 40 same-run Qwen captures expose logits and 24×60 router telemetry. Actual
actions are checker10/retrieval10/review11/no-action9 because one control fails its
correctness check and escalates. Eighteen rows reach 64 tokens (retrieval7/review10/
control1); every checker reaches EOS. Checker verdicts shift to 1 pass/9 fail, a
real candidate distribution shift not explained by truncation.

## 153. Router-only generalizes; logits-only collapses
On the untouched holdout, router-only accuracy is .700 (bootstrap [.550,.850]),
balanced accuracy .693, macro-F1 .700 versus majority baseline .275. Full features
reach .600 [.450,.750]/.602/.599. Logits-only reaches .225 [.100,.350]/.236/.199,
below majority. The added logits features hurt the frozen full model relative to
router-only. No alternative classifier or threshold was tried.

## 154. Remaining errors expose category/template confounds
Router-only recalls checker .80, retrieval .80, review .73, but no-action only .44.
Five no-action rows map to review; three review rows map to retrieval. The holdout
uses unseen IDs but shares category-specific prompt templates and verifier rules
with M23. Thus .70 supports a confound-controlled router study, not causal risk
prediction, user-level trust scoring, or production gating.

## 155. M24 public/private boundary
Public output contains run aggregates, class confusion/metrics, hashes, and frozen
protocol declarations only. Per-task predictions, decoded output, prompt/token
text, raw tensors, paths, centroids, and 40 detailed rows per schema stay private/
ignored. No tuning occurred; candidate-only and production gates remain.

## 156. M24 tests and milestone completion
Five CPU/no-network tests cover corrected balanced/disjoint manifest resolution,
frozen balanced-M23 fitting, full/logits/router predictions, lexical tie breaking,
deterministic bootstrap/confusion/per-class metrics, and public no-ID/centroid/text/
path reporting. Full repository suite: 100/100 green.

## 157. M25 preregisters an unobservable metadata counterfactual
Sixteen public-safe pairs are fixed before capture. Both members receive byte-
identical prompts, while trusted metadata alone changes checker/no-action or
retrieval/review applicability. The frozen M23 router-only model sees none of this
metadata. No feature, scale, centroid, threshold, or task is tuned after capture.

## 158. Identical prompts produce exact stored output/router equality
All 32 captures complete with real 24×60 router telemetry. Within all 16 pairs,
captured outputs are identical and both router entropy and expert concentration
have mean/max absolute difference exactly zero. Frozen predictions are identical
16/16 (divergence rate zero). There is no capture nondeterminism to qualify result.

## 159. Actual actions differ in every indistinguishable pair
Trusted verifier routing matches intended metadata labels 32/32, balanced 8/class.
All arithmetic outputs pass and end before cap. Topic outputs cap symmetrically for
both pair members; their current-info versus no-rubric explain labels remain
metadata-driven. Actual labels are discordant in 16/16 pairs despite equal signals.

## 160. Router-only hits the metadata observability ceiling
Frozen accuracy/balanced accuracy are .500, macro-F1 .413, bootstrap accuracy
[.3125,.6875] versus balanced majority .250. Every math pair maps checker, yielding
checker recall1/no-action0. Topic pairs share predictions (3 retrieval/5 review),
so exactly one member per pair can be correct. Telemetry cannot infer absent metadata.

## 161. M24 generalization was substantially template/category association
M25 falsifies the interpretation that router-only telemetry independently knows
workflow action requirements. M24's .70 holdout score benefited from action-specific
prompt templates/categories. A future router may include trusted metadata explicitly,
or telemetry can be studied against balanced within-category objective error labels;
neither supports deploying the current telemetry-only classifier.

## 162. M25 public/private boundary and branch gate
Public output contains only aggregate pair counts/differences and class metrics.
No pair/task IDs, prompt/output text, predictions, hashes, paths, tokens, tensors,
or detailed records are exposed outside the synthetic ID-only manifest. Candidate-
only and production gates remain. Current three-milestone autoloop must stop.

## 163. M25 tests and milestone completion
Five CPU/no-network tests cover manifest/private generator pair equality, metadata
discordance, frozen router prediction identity and 50% pair ceiling, exact-zero
feature differences, honest output-mismatch reporting, and public no-ID/text/
prediction/path output. Full repository suite: 105/105 green.

## 164. M26 preregisters the objective-error design before generation
The M26 manifest was committed before any task generation or capture. It fixes
one arithmetic category and prompt template, four difficulty bands, a per-ID
16/8 train/holdout split per band, seeded unique operand generation with all
tasks retained, the deterministic math_checker label rule, constant checker
applicability with drift as a stop condition, a holdout seal on M26 public
reporting, and the frozen M27 baseline and M28 ablation/calibration protocols.

## 165. Same-run capture holds action applicability constant at n=96
All 96 private tasks captured in one window with real logits and 24×60 router
telemetry; hidden stayed disabled. Every task carried task_category=math plus a
safe expression, and all 96 actual routed actions were checker_needed. The
metadata-observability failure mode falsified in M25 is therefore excluded by
construction: nothing about the label can hide in action applicability.

## 166. Difficulty bands produce objective errors without post-hoc selection
Train-split verdicts from the deterministic checker: band_a 16/0, band_b 16/0,
band_c 13/3, band_d 1/15 (pass/fail), totaling 46 pass/18 fail/0 undecided.
Every train answer reached EOS before the 64-token cap. The predeclared ≥8
per-class modeling minimum is met purely by ex-ante band design; no task was
regenerated, reselected, or relabeled after seeing outcomes.

## 167. Within-category train telemetry separates fails descriptively
On train rows, fails show higher decode-window entropy (g≈+3.0), more
high-entropy steps (g≈+2.4), higher expert concentration (g≈+1.9), lower
router entropy (g≈-1.9), more low-confidence steps (g≈+1.6), and a more
negative top-k margin trend (g≈-1.2); fixed-seed bootstrap mean-difference
intervals exclude zero for these. Difficulty band correlates with the label by
design, so this is association, not predictive value; M27's metadata-only
baseline exists precisely to price that shortcut.

## 168. M26 public/private boundary and holdout seal
Public artifacts contain band definitions, aggregate counts, and group
statistics only; no operands, prompts, outputs, per-task labels, predictions,
paths, tokens, or tensors. Holdout verdict counts and holdout telemetry
aggregates are sealed until the frozen M27 evaluation. Private tasks,
captures, telemetry/runtime/action/result records, and labels stay ignored.
Candidate-only and production gates remain.

## 169. M26 tests and milestone completion
Seven CPU/no-network M26 tests cover deterministic in-band generation with the
predeclared split, operand uniqueness, the checker-verdict label rule, holdout
sealing with honest shortfall reporting, train-only descriptive effects, and
public no-ID/text/expression/path output. Full repository suite: 123 tests
green (including pre-added M27/M28 protocol tests).

## 170. M27 evaluates the sealed holdout exactly once under a frozen protocol
The 32-task holdout was fixed per-ID before generation, sealed through M26,
and first read by the M27 evaluator. Classifiers were fit on the 64 train rows
only, with the classifier family, feature sets, tie break, bootstrap seeds,
and all six baselines predeclared in the M26 manifest. No refit, feature
change, or threshold tuning occurred after holdout rows were read.

## 171. Telemetry predicts within-category errors on the frozen holdout
Against 9 fail/23 pass holdout labels: majority .719; metadata-only band
shortcut .969; logits_only .969 (balanced .978); router_only .812;
router_plus_logits .906; full_telemetry 1.000. Logits-only telemetry recalls
all nine fails with one false positive and no metadata input, including a
within-band fail the band shortcut misses by construction. Unlike M24/M25,
action applicability and prompt family are constant, so this association
cannot come from the falsified metadata-observability channel.

## 172. The telemetry increment over the difficulty shortcut is not yet proven
The band shortcut alone reaches .969, so telemetry's headline advantage is one
task at n=32 with heavily overlapping bootstrap intervals. full_telemetry's
perfect score includes decode length/cap features that correlate with operand
size and hence with band difficulty, and a perfect prediction vector makes its
bootstrap interval degenerate [1.0, 1.0]. The claim licensed by M27 is
"telemetry recovers and slightly extends the difficulty signal within one
category", not "telemetry beats metadata".

## 173. Router-only over-flags errors within category
Router entropy/concentration alone recalls every fail but with .60 precision
(six false alarms among 23 passes), and adding logits to router features is
worse (.906) than logits alone (.969) under the frozen centroid family. The
within-category router signal is a blunt instrument for error detection here,
in contrast to its (falsified) apparent strength on the M24 action-routing
task.

## 174. M27 public/private boundary
Public output contains frozen synthetic holdout IDs, aggregate counts,
metrics/confusion matrices, and protocol flags only. Per-task predictions,
labels, operands, prompts, outputs, paths, tokens, and tensors remain
private/ignored. Candidate-only and production gates remain.

## 175. M27 tests and milestone completion
Six CPU/no-network M27 tests cover split/undecided handling, all-six-baseline
evaluation with frozen feature counts, majority tie-breaking, the predeclared
train-minimum stop, the frozen aggregate-only holdout manifest, and public
no-ID/text/prediction output. Full repository suite: 123 tests green.

## 176. M28 ablation localizes the error signal in decode-window entropy
Under the predeclared protocol, the count of high-entropy decode steps alone
reproduces the full ten-feature holdout score (1.000), with mean window
entropy at .938. Router features are weaker (expert concentration .844,
router entropy .781), final-token confidence features fall below the .719
majority baseline (.438), and windowed expert shift carries ~nothing (.312).
Wrong arithmetic answers are emitted with confident final tokens; the
uncertainty appears mid-window during decoding.

## 177. High-entropy count is not merely length
decode_step_count alone (pure length/cap behavior, correlated with operand
size) reaches only .844, well below high_entropy_count's 1.000, so the
entropy-count signal is not length in disguise, though it partially reflects
it. Leave-one-out ablation shows heavy redundancy: removing any one feature
costs at most .031 accuracy.

## 178. Calibration is excellent but saturated; threshold stays candidate-only
The predeclared softmax-distance p(fail) yields ECE .004 on 4 equal-count
holdout bins, with scores saturated near 0/1 — a property of this dataset's
separability that must be re-measured on harder distributions. The proposed
p(fail) ≥ 0.95 threshold was selected on the train split only (balanced
accuracy .934; holdout descriptive .944) and is labeled candidate-only and
not-for-production everywhere it appears. No production threshold exists.

## 179. M28 honesty boundaries
M28 decomposes a holdout already read once by M27, so its rankings are
descriptive, not fresh predictive tests; n=32 bootstrap intervals are wide and
overlapping outside the top feature. Verifier contradiction remains excluded
as a feature because the deterministic verifier defines the label. The scope
of every claim is one task category, one model, one decode protocol.

## 180. M28 tests and milestone completion
Five CPU/no-network M28 tests cover bounded/ordered fail probabilities,
full-coverage single-feature and leave-one-out ablations, equal-count
calibration bins with bounded ECE, complete aggregate FP/FN accounting, and a
public report that carries the candidate-only label with no IDs/text/paths.
Full repository suite: 123 tests green. The M26–M28 autoloop limit is reached.

## 181. M29 preregisters a powered increment test on fresh data
The M29 manifest was committed before generation: six multiplication bands
concentrated near the pass/fail boundary (384 tasks), a sealed per-ID
train/validation/holdout split (192/96/96), seven frozen baselines, a paired-
bootstrap incremental-value rule with an explicit claim threshold, validation-
only threshold/calibration fitting, and per-split power minimums. The spent
M27 holdout was not reused as a decision target, and the M28-motivated
window_entropy set was declared as such and tested on new data.

## 182. The scaled run meets every predeclared power requirement
384/384 captures completed with full logits/router telemetry in one window;
all actions checker_needed; zero undecided labels; zero capped rows. Split
labels: train 106 fail/86 pass, validation 54/42, holdout 51/45. Boundary
bands behaved as designed (band_2 ~12% fail, band_3 ~53%, band_5 ~66%,
band_4/6 ≥88%), giving the increment test its predeclared power without any
post-hoc selection.

## 183. Telemetry beats metadata point-wise but the increment is not established
On the once-read n=96 holdout: metadata_only .823, full_telemetry .885
[.823,.948], metadata_plus_telemetry .865. Paired bootstrap deltas over
metadata: full +.063 [−.021,+.146] (corrects 12 metadata errors, introduces
6), meta+tel +.042 [−.031,+.115], window_entropy +.010. Every 95% interval
includes zero, so under the predeclared rule telemetry's increment over the
difficulty shortcut is NOT established. The balanced-accuracy interval for
full telemetry ([−.006,+.153]) misses significance narrowly; honesty requires
calling that unproven, not "nearly proven".

## 184. M28's perfect single-feature score was a separability artifact
window_entropy (decode_window_entropy + high_entropy_count), which scored
1.000 on the easy/hard M27 holdout, scores .833 at boundary difficulty with
fail recall .706 and precision .973. Mid-window entropy is a high-precision,
moderate-recall failure flag — not a universal error detector. The scaled
boundary design did exactly the artifact-exposure it was built for.

## 185. Telemetry and metadata fail differently; their union does not help here
Metadata-only over-flags (fail recall .961, precision .766); logits-only
under-flags with high precision (.784/.930); full telemetry balances both
(.863/.917). Concatenating band one-hots onto telemetry (.865) is worse than
telemetry alone (.885) under the frozen centroid family: telemetry already
carries the difficulty signal, and the added indicators dilute the
standardized distance geometry rather than informing it.

## 186. Calibration degrades off the easy/hard split exactly as predicted
With mid-range reliability bins now populated, full-telemetry ECE is .059
(was .004 in M28) and metadata+telemetry .117; mid bins under-predict failure
(e.g. predicted .18 vs observed .33/.58). Validation-derived thresholds (.70
and .75 p(fail)) reach holdout balanced accuracy .859/.825 and remain
candidate-only. At the observed effect size a decisive increment test needs a
holdout near n≈200 — one more scaling step.

## 187. M29 tests and milestone completion
Seven CPU/no-network M29 tests cover deterministic in-band generation with
the sealed three-way split, three-split loading with undecided exclusion,
honest power flags, paired-delta bootstrap behavior (zero and positive
cases), seven-baseline evaluation with a synthetic established increment, an
uninformative-telemetry fixture that must report no established increment,
and public no-ID/text/path output with candidate-only labels. Full repository
suite: 130 tests green.

## 188. M30 preregisters the decisive confirmatory protocol
The operator-directed M30 manifest was committed before generation: 768 fresh
tasks in six boundary bands with a sealed 384/192/192 split, operand tuples
deterministically rejected against the committed M29 manifest's tuples, the
identical M29 centroid family, a single primary comparison (full_telemetry vs
metadata_only), an explicit three-way classification rule, per-split power
minimums, and validation-only threshold fitting. The holdout was read once.

## 189. The telemetry increment over difficulty metadata is ESTABLISHED
On the adequately powered n=192 holdout (103 fail/89 pass): metadata_only
.818, full_telemetry .917 [.875,.953]. The preregistered paired bootstrap
gives Δaccuracy +.099 with 95% CI [+.042,+.156] and Δbalanced-accuracy CI
[+.050,+.165] — both exclude zero — while telemetry corrects 27 of metadata's
holdout errors and introduces 8. Under the rule fixed before generation, the
telemetry-vs-metadata increment is classified established. This resolves the
question M29 left open, in the direction its point estimates suggested.

## 190. The established increment belongs to the full feature set
window_entropy alone gains only +.031 [−.042,+.104] over metadata — mid-decode
entropy remains a high-precision (.987) but low-recall (.728) partial flag.
router_only improved to .833 at this scale, and metadata_plus_telemetry
(.922, +.104 [+.057,+.156]) now edges out telemetry alone, reversing the M29
n=96 ordering. Error information is distributed across logits-window, router,
and length signals; no two-feature shortcut carries it.

## 191. Candidate calibration is usable for the intervention study
Validation-derived thresholds transfer to the holdout without degradation:
full_telemetry ECE .032 with balanced accuracy .916 at threshold .50;
metadata_plus_telemetry ECE .043 with .938 at threshold .75. These remain
candidate-only and production-gated, but they are adequate as the frozen
gating score for the operator-authorized M31 telemetry-triggered intervention
study (Branch 1).

## 192. M30 scope and boundaries
Established: a ~+10-point accuracy increment from internal telemetry over the
difficulty shortcut, within single-expression integer arithmetic, one model,
one greedy decode protocol, on a fresh sealed holdout read once. Not
established: transfer to other categories or models, causal mechanism, or any
production-readiness claim. Candidate-only and production gates remain.

## 193. M30 tests and milestone completion
Six CPU/no-network M30 tests cover deterministic generation with the sealed
split and M29-disjoint operands, three-split loading with honest power flags,
the three-way classification rule (established/not_established/negative), a
synthetic established verdict, an uninformative-telemetry fixture that must
not report established, and public no-ID/text/path candidate-only output.
Full repository suite: 136 tests green.

## 194. M31 preregisters the intervention protocol with a frozen trigger
The M31 manifest was committed before generation: 192 fresh M29/M30-disjoint
tasks, the M30 full_telemetry model refit deterministically and verified to
reproduce the published M30 holdout confusion exactly, the frozen .50
threshold, a seeded temperature-0.7 single-retry decode (added to the capture
script as an opt-in flag with the greedy path unchanged), four
replace-on-retry policies that never consult labels, and a fixed
useful/harmful/not-established rule.

## 195. The telemetry retry policy is NOT ESTABLISHED as useful
On 192 fresh tasks (90 pass/102 fail original), telemetry-triggered retry
reached .474 verified success vs .469 no-retry (+.005 [−.021,+.031]) and
.458 matched-compute random retry (+.016 [−.010,+.042]); both primary
intervals include zero. always_retry (.464) and random_retry were net
negative. No policy claim survives; no production retry policy exists.

## 196. The trigger replicated; the resample repair is the bottleneck
Only 11 of 99 telemetry-triggered retries were false alarms (~89% precision
on a third consecutive fresh task set), versus 43/99 for random gating. But a
single temperature-0.7 resample rescued only 4 of ~88 correctly-triggered
failures (~4.5%); the retry decode's overall pass rate (46.4%) matches greedy
(46.9%). Within-category arithmetic errors are systematic rather than
stochastic, so redrawing from the same distribution seldom repairs them.
Detection is validated; the repair operator is what failed.

## 197. Telemetry gating minimizes intervention damage
Replace-on-retry carries replacement risk: always-retry introduced 7 new
errors on originally-correct outputs and random gating 5, while telemetry
gating introduced 3 and avoided 79 of 90 potential false alarms at equal
compute to random. Even with a weak repair operator, gating strictly
dominates ungated retrying — the value shown is in *not* intervening on
likely-correct outputs.

## 198. Recovery traces exist but cannot yet support training
Four verified wrong→right rescues under the telemetry policy were stored as
private gitignored traces (aggregate count and schema public). Trace volume
is bounded by the repair operator's ~4.5% rescue rate, so scaling trace
generation before strengthening the repair operator would waste compute —
the next-step decision recorded for the operator gate.

## 199. M31 tests and milestone completion
Seven CPU/no-network M31 tests cover deterministic M29/M30-disjoint
generation, frozen-score verification accept/reject paths, zero and positive
paired success-delta bootstraps, shared-retry policy accounting with a
perfect-trigger fixture, uninformative and harmful fixtures mapping to their
verdicts, and aggregate-only policy reports. The capture-script sampling
addition leaves all greedy decode tests passing. Full repository suite: 143
tests green.

## 200. M32 structured repair was superseded before execution
The preregistered M32 structured-repair bakeoff (manifest 5f0edfe, module and
tests written, capture just started) was superseded by operator steer 9aaded9
before any result was inspected. The in-flight capture was killed and partial
private captures deleted; the manifest, module, and CPU tests are preserved
as never-executed historical artifacts. No M32 claim exists.

## 201. M32R phase-0 feasibility gate fails for both approved Agents-A1 paths
A meta-device audit from the official config (no weights downloaded) shows
InternScience/Agents-A1 (qwen3_5_moe, 40 layers, 256 experts, top-8) carries
32.21B of its 34.66B parameters in fused 3D expert tensors that bitsandbytes
cannot quantize, so the preferred NF4 research load is ~61.9 GiB and BF16 is
~64.6 GiB against a hard 44 GiB dual-3090 ceiling. The FP8 variant requires
compressed-tensors, which is not in the approved stack, and Ampere has no
FP8 kernel path. Per the protocol's Branch 4, M32R stopped before
preregistration or capture, with unblock options reported instead of a
silent model substitution. This reproduces and extends finding-era evidence
from the iteration-8 Qwen3.6-35B-A3B NF4 audit.

## 202. M32P built and verified a safe expert-route override for the proxy
A prepended router-gate hook edits only the last position's router logits and
rebuilds that row's selection with the router's own arithmetic, leaving
dispatch untouched; disabled, it is bit-identical to the normal path. CPU
tests on a tiny real qwen2_moe cover parity, swap validity, rejection, KV
branch independence, and privacy; the real smoke gate passed at 27.95 GiB
peak with a forced swap verifiably changing routing.

## 203. The proxy's multiplication frontier is carry-structured
A predeclared 288-row calibration sweep shows carry density, not digit count,
dominates difficulty: 2x2 passes .96 low-carry vs .42 carry-heavy, 3x2 .83 vs
.04, 4x2 .71 vs .00, with middle-zero (.375) and near-power-of-ten (.667)
mid-frontier. Frozen composition rules selected a 192-task benchmark (four
boundary cells x36 plus easy/hard anchors x12) with expected failures 90.

## 204. The frozen M30 trigger transfers imperfectly to the frontier
On the model-calibrated cell distribution the frozen detector's precision is
.766 and recall .738, down from ~.89 on band-based sets. Distribution shift
in task structure (carry-heavy and structured cells at matched digit counts)
weakens the telemetry trigger; reported as a finding without any tuning.

## 205. Counterfactual expert rerouting is falsified on the proxy
H1 NOT ESTABLISHED: on sealed-holdout triggered failures the heuristic route
families' oracle rescue rate (.125) is identical to matched-random search
(paired CI [0,0]); the all-route oracle ceiling is 11.9% of triggered
failures. Family statistics show telemetry-guided swaps rescue at the same
per-branch rate as random equal-compute perturbation (17 vs 21 rescues in
308 continuations) while introducing more regressions than rescues. H2 NOT
ESTABLISHED: the validation-frozen non-oracle policy exactly matches normal
routing (.5625). H3: no layer-expert soft-penalty candidate survived
discovery. Within this proxy and task family, systematic failures are not
route-reachable; the small recoverable fraction reflects decode-path
sensitivity to any perturbation, not expert misrouting.

## 206. M32P scope, hygiene, and track closure
All splits met predeclared power minimums (41/18/21 realized failures);
0 undecided; equal verifier/candidate budgets across arms; per-task routes,
expert tables, and branch records stay private; public artifacts aggregate-
only and commit-safe. Claims are proxy-scoped and say nothing about
Agents-A1. Per the preregistered Branch 3, the expert-routing autoloop stops
after this milestone: no router training, no expert blacklist, no production
change. Full repository suite: 166 tests green.
