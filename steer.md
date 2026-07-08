# steer.md — post-M7 calibration steering

Read this first before continuing `jlens`.

M1 through M7 are complete. Do not redo benchmark ingestion, the M5 smoke test, PolicyEngine v0, or the local shadow wrapper.

## Completed milestones

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
M4: benchmark-gold ingestion foundation
M5: end-to-end benchmark telemetry smoke prototype
M6: PolicyEngine v0 advisory/shadow runtime
M7: local shadow wrapper + real-use log schema
```

## Current capability

`jlens` now has a local shadow runtime:

```text
config/policy_engine_v0.json
src/policy_engine.py
src/risk_runtime.py
src/local_shadow_wrapper.py
docs/POLICY_ENGINE_V0.md
docs/M7_SHADOW_RUNTIME.md
tests/test_policy_engine.py
tests/test_local_shadow_wrapper.py
reports/shadow/shadow_log.jsonl
reports/shadow/realuse_sample.jsonl
```

Current behavior:

```text
- scores telemetry feature rows when available
- can run dry-run or optional live endpoint wrapper
- logs prompt/output previews, policy recommendation, and outcome fields
- keeps outcome fields null until reviewed
- advisory/shadow only
- no production safety claims
- final thresholds remain gold/audit gated
```

Current interpretation:

```text
Telemetry has real ranking signal.
PolicyEngine v0 can produce advisory recommendations.
The local wrapper can produce real-use shadow records.
The next useful work is annotation + calibration, not another wrapper.
```

## Feature decision

Keep these feature groups:

```text
entropy_final_logits
selected_token_prob
topk_mass_or_margin
prefill domain prediction and margin
windowed decode-domain shift
low-confidence and high-entropy counts
```

Do not use these as model features:

```text
drift_from_prefill_signature
drift_from_previous_token
drift_from_prefill_weighted
drift_from_previous_token_weighted
```

Drift remains provenance/debug only.

## Next milestone: M8 outcome annotation + calibration loop

M8 should turn shadow logs into reviewed calibration data.

Suggested command:

```text
/jlens-m8-outcome-calibration-loop
```

Read first:

```text
steer.md
reports/FINDINGS.md
docs/POLICY_ENGINE_V0.md
docs/M7_SHADOW_RUNTIME.md
reports/shadow/realuse_sample.jsonl
reports/shadow/shadow_log.jsonl
reports/risk_heads_prototype.json
reports/benchmark_m5_join.json
reports/features/benchmark_m5_features.jsonl
schema/risk_labels_v2.json
```

M8 objectives:

```text
1. Define an outcome annotation schema for shadow logs.
2. Add a tool that copies shadow records into a review queue.
3. Add a safe CLI/editor flow for marking outcome fields.
4. Validate reviewed logs: null is allowed, but invalid types or missing required fields fail.
5. Add a coverage report for reviewed outcomes.
6. Add calibration analysis that compares policy recommendation to reviewed outcome fields.
7. Report false-low-risk and false-high-risk using reviewed outcomes where possible.
8. Keep production thresholds gated until enough reviewed outcomes exist.
9. Add docs for how a human reviews shadow records.
10. Update STATE.md and reports/FINDINGS.md.
```

Outcome fields to preserve:

```text
user_agreed
was_wrong
needed_retrieval
needed_checker
notes
```

Recommended additional review metadata:

```text
reviewer
reviewed_at
review_source
review_confidence
```

M8 deliverables:

```text
schema/shadow_outcome_v1.json
src/build_review_queue.py
src/review_shadow_log.py or equivalent
src/outcome_report.py
reports/shadow/review_queue_sample.jsonl
reports/outcomes/outcome_coverage.json
reports/outcomes/calibration_notes.md
docs/SHADOW_OUTCOME_REVIEW.md
tests for schema validation and report generation
updated STATE.md and reports/FINDINGS.md
```

M8 stop condition:

```text
shadow records can be queued for review
reviewed records validate against schema
coverage report summarizes reviewed outcomes
calibration notes compare recommendations to outcomes
production thresholds remain gated
no private prompts or sensitive logs are committed
```

## Parallel track after M8

Continue collecting real-use shadow logs locally. Keep private logs out of git unless explicitly scrubbed and approved.

For benchmark scaling:

```text
64-128 prompts for quick calibration check
200-500 prompts if runtime is acceptable
```

Report:

```text
AUROC
AUPRC
ECE
false-low-risk
false-high-risk
latency
threshold behavior
```

## Later data expansion for remaining labels

After the review/calibration loop exists, add second-wave converters to cover the remaining labels:

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
PolicyEngine: advisory/shadow v0 now, calibrated route decisions later
ReviewLoop: human/audit outcome labels from shadow logs
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, private prompts, sensitive logs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
