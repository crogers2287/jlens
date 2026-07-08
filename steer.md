# steer.md — post-M5 runtime steering

Read this first before continuing `jlens`.

M1 through M5 are complete. Do not redo the M4 benchmark ingestion or the 16-prompt M5 smoke test.

## Completed milestones

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
M4: benchmark-gold ingestion foundation
M5: end-to-end benchmark telemetry smoke prototype
```

## M5 result

```text
answerable_from_memory:
  LOO smoke AUROC about 0.875 on n=8

unsupported_or_hallucinated:
  LOO smoke AUROC about 0.844 best ranking model on n=12
```

Interpretation:

```text
Telemetry has real ranking signal.
The sample is tiny.
Current thresholds are not production-ready.
Calibration remains the main blocker.
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

## Next milestone: M6 PolicyEngine v0 + shadow testing

M6 should implement the first usable runtime layer now. Do not wait for perfect calibration before building the interface.

Default posture:

```text
advisory first
shadow mode by default
log every recommendation
prototype thresholds only
no production claims yet
```

Suggested command:

```text
/jlens-m6-policyengine-shadow-loop
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
1. Build src/policy_engine.py.
2. Add a runtime scorer that loads the existing prototype report/config.
3. Return a small result object: level, scores, recommended_action, explanation.
4. Add a config file for prototype thresholds and actions.
5. Add shadow logging for prompt_id, feature source, scores, recommendation, and outcome note.
6. Keep ordinary chat advisory-only.
7. Keep final mode and production thresholds gold/audit gated.
8. Add tests for config loading, score parsing, action mapping, and log writing.
9. Add docs showing how to score an existing feature JSONL row.
10. Preserve the M5 metrics and training path.
```

Recommended v0 actions:

```text
answer_locally
verify
retrieve
run_checker
ask_user
require_confirmation
```

M6 deliverables:

```text
src/policy_engine.py
src/risk_runtime.py or equivalent CLI wrapper
config/policy_engine_v0.json
policy output schema docs
shadow log schema docs
tests for scoring and logging
updated STATE.md and reports/FINDINGS.md
```

M6 stop condition:

```text
PolicyEngine v0 can score a feature row
recommendation is produced
recommendation is logged
ordinary chat remains advisory
final mode remains gold/audit gated
raw captures and raw datasets remain uncommitted
```

## Parallel track after PolicyEngine v0

After the runtime layer exists, continue scaling the M5 path.

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

## Final architecture

```text
RouterGuard: prefill routing signatures and domain priors
DecodeGuard: entropy, selected-token confidence, router concentration, windowed mode shift
PolicyEngine: advisory/shadow v0 now, calibrated route decisions later
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, logs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
