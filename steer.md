# steer.md — post-M5 steering

Read this first before continuing `jlens`.

M1, M2, M3, M4, and M5 are complete. Do not restart benchmark-gold ingestion or the 16-prompt M5 smoke test.

## Current state

Completed:

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
M4: benchmark-gold ingestion foundation
M5: end-to-end benchmark telemetry smoke prototype
```

M5 delivered:

```text
src/build_benchmark_prompts.py
data/prompts/benchmark_m5_sample.jsonl
router-only decode capture for 16 benchmark prompts
reports/schema/benchmark_m5_decode.jsonl
reports/features/benchmark_m5_features.jsonl
src/join_labels_features.py
reports/benchmark_m5_join.json
real prototype training/eval path in src/train_risk_heads.py
reports/risk_heads_prototype.json
updated STATE.md and reports/FINDINGS.md
```

M5 result:

```text
answerable_from_memory:
  LOO smoke AUROC about 0.875 on n=8

unsupported_or_hallucinated:
  LOO smoke AUROC about 0.844 best ranking model on n=12
```

Interpretation:

```text
The telemetry carries real ranking signal.
The operating thresholds are not production-ready.
The sample is tiny.
Calibration and false-low-risk remain the main blockers.
```

Important caveats:

```text
- M5 uses only 16 prompts.
- Labels are prompt-level benchmark proxies, not final graded target-model outputs.
- answerable_from_memory is currently confounded with domain/source mix.
- unsupported_or_hallucinated ranking signal is promising, but default thresholds are bad.
- final mode remains gold/audit gated.
```

## Working features

Keep these feature groups:

```text
entropy_final_logits
selected_token_prob
topk_mass_or_margin
prefill domain prediction and margin
windowed decode-domain shift
low-confidence and high-entropy counts
```

Exclude these from model features:

```text
drift_from_prefill_signature
drift_from_previous_token
drift_from_prefill_weighted
drift_from_previous_token_weighted
```

Reason: M2 showed drift does not track confidence. Keep drift only for provenance/debugging.

## Next milestone: M6 scale benchmark telemetry + calibration

M6 should scale the proven M5 path before adding too many new labels.

Suggested command:

```text
/jlens-m6-scale-telemetry-loop
```

Read first:

```text
steer.md
reports/FINDINGS.md
reports/risk_heads_prototype.json
reports/benchmark_m5_join.json
reports/features/benchmark_m5_features.jsonl
reports/coverage/benchmark_coverage.json
schema/risk_labels_v2.json
data/registry/benchmark_sources.json
GOLD_DATASET_SOURCE_PLAN.md
M3_RISK_LABELING.md
LABELING_HANDOFF.md
```

M6 objectives:

```text
1. Scale the benchmark prompt sample from 16 to a balanced larger set.
2. Focus first on the two labels already proven end-to-end:
   - answerable_from_memory
   - unsupported_or_hallucinated
3. Avoid source/domain confounds where possible.
4. Capture router-only decode telemetry for the larger sample.
5. Export v3 decode records and risk features.
6. Join labels to feature rows by prompt_id.
7. Train/evaluate with a real held-out split where possible, not only leave-one-out.
8. Report AUROC, AUPRC, ECE, false-low-risk, false-high-risk, latency, and threshold behavior.
9. Tune prototype operating points for low false-low-risk.
10. Keep final threshold calibration gold/audit gated.
```

Sampling guidance:

```text
First target:
  200-500 total prompts if runtime is acceptable

Smoke target if runtime is tight:
  64-128 total prompts

Do not capture all 23k benchmark records yet.
```

Recommended M6 sample design:

```text
answerable_from_memory true:
  TruthfulQA correct / stable QA

answerable_from_memory false:
  GSM8K math prompts and/or other non-recall tasks

unsupported_or_hallucinated true:
  TruthfulQA incorrect / FEVER refutes

unsupported_or_hallucinated false:
  TruthfulQA correct / FEVER supports
```

Guardrails:

```text
- Preserve prompt_id linkage from labels to telemetry features.
- Do not use drift fields as model features.
- Do not treat null as false.
- Do not commit raw captures, raw data caches, model weights, or transient output stubs.
- Do not report production claims from smoke metrics.
- If a metric improves, also report false-low-risk and threshold behavior.
```

## M6 deliverables

```text
data/prompts/benchmark_m6_sample.jsonl
capture command docs or script for benchmark_m6
reports/schema/benchmark_m6_decode.jsonl or equivalent
reports/features/benchmark_m6_features.jsonl
reports/benchmark_m6_join.json
reports/risk_heads_m6.json
calibration/threshold report
updated STATE.md and reports/FINDINGS.md
```

M6 stop condition:

```text
larger benchmark telemetry set captured
labels and features join cleanly
prototype heads train/evaluate on larger data
threshold behavior is reported honestly
false-low-risk is explicitly measured
final mode remains gold/audit gated
raw captures and raw datasets remain uncommitted
```

## After M6: data expansion for the remaining labels

Once the two covered labels are scaled and calibrated, add second-wave converters to cover the remaining labels:

```text
HumanEval or MBPP -> needs_code_execution
GAIA or BrowseComp -> needs_current_info
SWE-bench -> needs_user_file_context
BFCL -> format_or_tool_mode_shift
prompt-injection benchmark -> context_attack_present
BeaverTails or PKU-SafeRLHF -> high_stakes_or_sensitive
stable closed-book QA -> needs_exact_citation false examples
non-math stable QA -> needs_math_verification false examples
```

## Final architecture

```text
RouterGuard: prefill routing signatures and domain priors
DecodeGuard: entropy, selected-token confidence, router concentration, windowed mode shift
PolicyEngine: calibrated risk heads and route decisions
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, logs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
