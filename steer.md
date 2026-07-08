# steer.md — post-M8 real-use calibration steering

Read this first before continuing `jlens`.

M1 through M8 are complete. Do not redo benchmark ingestion, the M5 smoke test, PolicyEngine v0, the local shadow wrapper, or the outcome-review tooling.

## Completed milestones

```text
M1: RouterGuard feasibility
M2: DecodeGuard telemetry and feature discovery
M3: risk-labeling scaffold and training gate
M4: benchmark-gold ingestion foundation
M5: end-to-end benchmark telemetry smoke prototype
M6: PolicyEngine v0 advisory/shadow runtime
M7: local shadow wrapper + real-use log schema
M8: outcome review + calibration loop
```

## Current capability

`jlens` now has the full shadow feedback loop:

```text
local shadow wrapper
PolicyEngine v0 advisory scorer
shadow logs
review queue builder
safe outcome review CLI
outcome schema
outcome coverage report
calibration notes from reviewed-only data
human reviewer guide
tests for policy/runtime/review tooling
```

Current behavior:

```text
- scores telemetry feature rows when available
- logs advisory recommendations
- queues shadow records for review
- lets a reviewer mark outcome fields explicitly
- computes calibration only from reviewed records
- stays advisory/shadow only
- final thresholds remain gold/audit gated
```

Current interpretation:

```text
The technical loop is now complete.
The next bottleneck is real reviewed data.
Do not fabricate outcomes.
Do not tune thresholds from unreviewed logs.
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

## Next milestone: M9 private real-use logging + review workflow

M9 should move from public samples and fixtures into a local-only real-use workflow. The goal is to collect private shadow logs locally, review them, and produce calibration summaries without committing sensitive content.

Suggested command:

```text
/jlens-m9-private-shadow-review-loop
```

Read first:

```text
steer.md
reports/FINDINGS.md
docs/POLICY_ENGINE_V0.md
docs/M7_SHADOW_RUNTIME.md
docs/SHADOW_OUTCOME_REVIEW.md
schema/shadow_outcome_v1.json
src/local_shadow_wrapper.py
src/build_review_queue.py
src/review_shadow_log.py
src/outcome_report.py
reports/shadow/realuse_sample.jsonl
reports/outcomes/calibration_notes.md
```

M9 objectives:

```text
1. Add a local-only private log directory convention that is gitignored.
2. Add scripts or docs for running real prompts through the wrapper into local private logs.
3. Add a redaction/export tool that can produce scrubbed review samples if explicitly requested.
4. Add a local review workflow for marking outcomes on private logs.
5. Add aggregate-only reports that can be safely committed: counts, rates, calibration summaries, no prompt text.
6. Add checks that refuse to commit private logs or unredacted prompt/output text.
7. Add examples using public fixture logs only.
8. Keep production thresholds gated until enough reviewed real-use records exist.
9. Update STATE.md and reports/FINDINGS.md.
```

Outcome fields to preserve:

```text
user_agreed
was_wrong
needed_retrieval
needed_checker
notes
```

Review metadata:

```text
reviewer
reviewed_at
review_source
review_confidence
```

M9 deliverables:

```text
local/private-log path documented and gitignored
src/redact_shadow_log.py or equivalent
src/private_outcome_summary.py or equivalent
docs/PRIVATE_SHADOW_WORKFLOW.md
reports/outcomes/private_summary_sample.json
fixture tests for redaction and aggregate reports
updated STATE.md and reports/FINDINGS.md
```

M9 stop condition:

```text
private real-use logs can be generated locally
review queue can be built locally
reviewed outcomes can be summarized without committing private text
redaction/export path exists for safe sharing
aggregate-only reports are commit-safe
production thresholds remain gated
```

## Parallel track after M9

Continue benchmark scaling only after the private real-use workflow exists.

Benchmark scale targets:

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

After the private review workflow exists, add second-wave converters to cover the remaining labels:

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
PrivateOps: local-only private logs + safe aggregate reporting
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, private prompts, sensitive logs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
