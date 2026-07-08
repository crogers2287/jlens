# steer.md — post-M6 integration steering

Read this first before continuing `jlens`.

M1 through M6 are complete. Do not redo benchmark ingestion, the M5 smoke test, or the PolicyEngine v0 runtime.

## Completed milestones

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
M4: benchmark-gold ingestion foundation
M5: end-to-end benchmark telemetry smoke prototype
M6: PolicyEngine v0 advisory/shadow runtime
```

## Current capability

`jlens` now has:

```text
config/policy_engine_v0.json
src/policy_engine.py
src/risk_runtime.py
docs/POLICY_ENGINE_V0.md
tests/test_policy_engine.py
reports/shadow/shadow_log.jsonl
```

PolicyEngine v0 scores existing feature rows, emits a level plus recommended action, and writes shadow-log entries. It is advisory only and uses prototype thresholds only.

Current interpretation:

```text
Telemetry has real ranking signal.
The sample is tiny.
Thresholds are prototype-only.
Calibration remains the main blocker.
The runtime is ready for real-use shadow integration.
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

## Next milestone: M7 local inference wrapper + real-use shadow logs

M7 should connect the existing advisory runtime to a local inference flow so `jlens` starts producing real-use shadow logs.

Suggested command:

```text
/jlens-m7-local-shadow-integration-loop
```

Read first:

```text
steer.md
reports/FINDINGS.md
docs/POLICY_ENGINE_V0.md
config/policy_engine_v0.json
src/policy_engine.py
src/risk_runtime.py
reports/risk_heads_prototype.json
reports/benchmark_m5_join.json
reports/features/benchmark_m5_features.jsonl
schema/risk_labels_v2.json
```

M7 objectives:

```text
1. Build a local inference wrapper or adapter around an OpenAI-compatible local endpoint.
2. Keep the first integration simple: accept prompt, call model, attach feature row when available, call PolicyEngine, write shadow log.
3. Support an offline mode that scores precomputed feature rows and records associated prompt/output metadata.
4. Define a runtime record schema for real-use shadow logs.
5. Add outcome fields for later review: user_agreed, was_wrong, needed_retrieval, needed_checker, notes.
6. Keep recommendations advisory only for normal chat.
7. For tool/file/GitHub workflows, emit require_confirmation as a recommendation only; do not perform actions directly.
8. Add docs showing how to run the wrapper against a local endpoint.
9. Add tests using fixtures or a fake local endpoint.
10. Update STATE.md and reports/FINDINGS.md.
```

Recommended runtime output:

```json
{
  "prompt_id": "realuse_...",
  "model": "local-model-name",
  "feature_source": "...",
  "policy": {
    "level": "low|medium|high|critical",
    "recommended_action": "answer_locally|verify|retrieve|run_checker|ask_user|require_confirmation",
    "scores": {},
    "explanation": "..."
  },
  "outcome": {
    "user_agreed": null,
    "was_wrong": null,
    "needed_retrieval": null,
    "needed_checker": null,
    "notes": null
  }
}
```

M7 deliverables:

```text
src/local_shadow_wrapper.py or equivalent
runtime/shadow log schema doc
example config for local OpenAI-compatible endpoint
fixture-based tests
README/docs for running shadow mode
sample small log if safe and non-sensitive
updated STATE.md and reports/FINDINGS.md
```

M7 stop condition:

```text
local wrapper can run in dry-run or fixture mode
PolicyEngine v0 is invoked by the wrapper
shadow recommendation is logged with prompt/output metadata
outcome fields exist for later review
normal chat remains advisory
no private prompts or sensitive logs are committed
no raw captures or model weights are committed
```

## Parallel track after M7

After the real-use shadow wrapper exists, continue scaling and calibration.

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

After the runtime exists and the two covered labels are exercised in real-use shadow mode, add second-wave converters to cover the remaining labels:

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
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, private prompts, sensitive logs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
