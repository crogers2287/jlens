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
