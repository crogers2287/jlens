# M3 — Risk-Labeling Dataset & Calibrated Heads (plan)

Moves jlens from routing telemetry (M1/M2) to supervised risk modeling. This is
a PLAN; execution is gated on **human labels** — the loop stops here and hands
off. Do not fabricate labels or synthesize ground-truth risk outcomes.

## What M1/M2 established (feature evidence — read before designing features)
- Router signatures classify prompt domain strongly (r3 prefill 0.938 logreg;
  token-level 0.863 StratifiedGroupKFold vs 0.175 chance). The r3 head transfers
  to r4 prefill 16/16.
- **Routing drift is NOT a risk feature** — unweighted AND probability-weighted
  drift are ~0-correlated with output confidence (|r| ≤ 0.12). Drop it.
- **topk_mass (routing concentration) is the one useful routing feature**:
  r ≈ +0.165 with entropy, −0.157 with sel_prob (more concentrated routing →
  less confident token). Weak but real.
- **entropy_final_logits + selected_token_prob are the primary decode signal**:
  they spike at mode-boundary tokens (code fence, `<think>`, section breaks) in
  the first 1–2 generated tokens and dip on low-confidence factual tokens
  (e.g. ` NASA`).
- **Decode routing captures a code↔prose mode shift** (windowed, not per-token):
  routing looks like the `lang`/prose domain during `<think>`/explanation spans.

## Label taxonomy (10, multi-label — a prompt may carry several)
| label | meaning |
|---|---|
| answerable_from_memory | model can answer reliably from parametric knowledge |
| needs_current_info | requires post-training / real-time info → retrieval |
| needs_exact_citation | requires a verifiable source/quote |
| needs_math_verification | numeric/derivation that should be checked |
| needs_code_execution | code whose correctness needs running |
| needs_user_file_context | depends on user files/context not in the prompt |
| unsafe_or_high_stakes | medical/legal/financial/safety-critical |
| prompt_injection_present | prompt/context contains an injection attempt |
| unsupported_or_hallucinated | output makes unsupported factual claims |
| format_or_tool_mode_shift | output shifts mode (prose→code/JSON/tool call) |

Note: the first 8 are **prompt-time** labels (knowable before generation); the
last 2 (`unsupported_or_hallucinated`, `format_or_tool_mode_shift`) are
**generation-time** labels requiring the actual output.

## Dataset design
- **≥50 prompts per label family**, prompt-held-out splits only (never split a
  prompt's tokens across train/test — reuse StratifiedGroupKFold by prompt id).
- **Separate train/test prompt templates** so the head can't memorize surface
  form.
- Coverage per family: clean, adversarial, high-stakes, tool-needed, and
  deliberately unanswerable examples. Specifically include:
  - unanswerable factual questions (should trigger low-confidence / retrieval)
  - current-events questions requiring retrieval (`needs_current_info`)
  - code/math with KNOWN verifiable answers (gradable without human review)
  - documented prompt-injection strings in retrieved/document context
- Capture with the new router-only decode mode (`--router-only`,
  `--max-new-tokens` sized to the answer) for cheap, resumable runs.
- Scale beyond 32 prompts — every M2 caveat is "n=16/32". Target ≥500 prompts
  total so per-label families reach ≥50 with held-out test prompts.

## Risk-head feature set (from M2 evidence)
Per prompt, aggregate over the generated sequence:
- **Prefill**: domain prediction + max-proba/margin; prefill routing entropy stats.
- **Decode confidence** (primary): mean/min selected_token_prob; mean/max
  entropy_final_logits; count of low-confidence tokens (sel_prob < τ); count of
  high-entropy tokens.
- **Routing concentration**: mean/max topk_mass_or_margin; low-mass token count.
- **Windowed domain-shift**: fraction of decode tokens off prefill-domain
  (smoothed over a window), number of windowed switches, first-shift index.
- **Explicitly EXCLUDED**: drift_from_prefill / drift_from_previous (dead per
  M2 finding #18). Keep the raw fields in the schema for provenance but do not
  feed them to the head.

## Baselines (all calibrated)
- logistic regression + isotonic/Platt calibration
- linear SVM + calibration
- tiny MLP + calibration
- hand-score baseline (fixed weighted blend of entropy/sel_prob/topk_mass) —
  **for comparison only**, never the shipped policy.

## Metrics
- AUROC, AUPRC (per label; PR matters — risk labels are imbalanced)
- ECE (calibration — a risk score must be trustworthy, not just ranked)
- **false-low-risk rate** and **false-high-risk rate**, reported separately
- latency per prompt + per decode token (sidecar overhead budget)

## Policy priority (non-negotiable)
**False-low-risk is worse than false-high-risk** — missing a real risk (letting
an unsafe/hallucinated/injected generation through) costs more than an
unnecessary retrieval/verification. Do NOT optimize accuracy alone; tune the
operating point to bound false-low-risk first, then minimize false-high-risk.
Thresholds come from calibration on held-out labeled data, never hand-picked.

## Stop / hand-off
Execution requires operator-provided (or operator-approved) labels for the 10
families. The DecodeGuard loop stops at this document. Next action is **human**:
label a seed set (or approve a labeling protocol), then a future loop trains and
calibrates the heads against it.
