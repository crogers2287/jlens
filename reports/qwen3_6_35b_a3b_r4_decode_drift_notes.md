# r4 decode drift — interpretation notes

Manual read of `reports/qwen3_6_35b_a3b_r4_decode_drift.json` (Qwen3.6-35B-A3B,
16 prompts × 32 greedy-decoded tokens = 512 records, 8 domains). Answers the
questions in steer.md step 4. **Verdict: unweighted routing drift is
INCONCLUSIVE→WEAK as a risk signal; entropy/confidence is the real decode-time
signal.**

## Q: Do high-drift tokens correspond to visible mode shifts?
**No.** The top `drift_from_prefill` tokens are `An`, `,`, `\n`, `1`,
` thinking`, ` Input` — every one has entropy ≈ 0.000 and selected-token prob =
1.000. The highest-drift tokens are the model's **most confident** tokens, not
mode boundaries. `drift_from_previous` is dominated by a repeated ` thinking`
scaffold token (dV≈0.956 across code_rust_01 / reason_01 / reason_02 at index 6)
— a template-boundary artifact, again at p=1.000. Drift marks
template/positional routing differences, not uncertainty.

## Q: Do mode-shift tokens (code fence / JSON / language / math / factual) show up?
**Yes — in ENTROPY, not drift.** The top entropy spikes are structure-open
tokens at the very start of generation:
- `` ``` `` — code fence (code_py_01 @t1, H=2.85, p=0.39)
- `<think>` — reasoning-mode open (code_py_02/03 @t1, H≈2.4–2.5, p≈0.4–0.55)
- `\n\n` — paragraph/section break (code_py_01/03 @t0, H≈2.2–2.3)
The model is genuinely uncertain **which output mode to enter**, and that shows
up as final-logit entropy, while routing drift for these same tokens is
unremarkable (~0.72, the corpus mean).

## Q: Do entropy spikes overlap drift spikes?
**No — 0 of 8 overlap** between the top-entropy and top-drift(prefill) token
sets. Decisive: the two signals are measuring different things.

## Q: Do low selected-token-prob tokens overlap drift spikes?
**No.** Lowest-confidence tokens are a mix of format markers and *factual-content*
tokens: `**` (markdown bold, fact_01 @t8, p=0.28), ` NASA` (fact_01, p=0.35),
` in`/` to` (fact_01/02 function words in factual sentences), and a Chinese
content word (lang_zh_01, p=0.31). None are high-drift. Notably ` NASA` inside a
factual answer is a low-confidence content token — the kind of place a
hallucination-risk head should look — and drift there is *below* average (0.58).

## Q: Is first-token drift systematically high (and thus less useful)?
**No — the opposite.** `drift_from_prefill` at t0 is 0.653, slightly *below* the
0.723 corpus mean, and it never trends. It's **entropy** that has the
first-token effect: H(t0)=0.75, H(t1)=1.05, then it collapses (H(t3)=0.12,
H(t4)=0.08). Uncertainty concentrates in the first 1–2 generated tokens (the
mode-selection decision), then the model commits.

## Q: Does drift stabilize after the first few tokens?
Drift has nothing to stabilize *from* — it is flat at ~0.65–0.80 across all 32
positions (structural offset: decode routes one token at a time vs prefill's
whole-prompt pass). **Entropy** stabilizes fast: high for ~2 tokens, low
thereafter, with occasional mid-sequence bumps on content-heavy tokens.

## Correlations (512 tokens)
- drift_prefill × entropy = −0.078, × sel_prob = +0.056
- drift_prev × entropy = −0.108, × sel_prob = +0.118
All ≈ 0. Unweighted routing drift does not track output confidence.

## Verdict & consequences
- **Unweighted routing drift is NOT a usable risk feature** on this evidence
  (flat, uncorrelated, spikes on confident template tokens).
- **Entropy_final_logits + selected_token_prob ARE the decode-time signal**:
  they spike at mode-boundary tokens (code fence, `<think>`, section breaks) in
  the first 1–2 tokens, and dip on some factual-content tokens.
- Open question this motivates: does **probability-weighted** drift (step 6)
  recover signal the count-based version washes out? If weighted drift is also
  flat/uncorrelated, drop drift from the risk-head feature set and lead with
  entropy/confidence + the domain-shift probe (step 7).
- Caveat: 16 prompts / 512 tokens. Directional, not definitive; do not treat any
  single token's entropy as a hallucination label without the M3 labels.
