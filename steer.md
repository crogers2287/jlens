# steer.md — post-M10 real workload steering

Read this first before continuing `jlens`.

M1 through M10 are complete. Do not redo benchmark ingestion, the M5 smoke test, PolicyEngine v0, the local shadow wrapper, outcome-review tooling, private-log workflow, or the autonomous supervisor.

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
M9: private real-use logging + safe aggregate/redaction workflow
M10: autonomous shadow supervisor + verifier-backed auto_outcome candidates
```

## Current model/runtime context

The current local model target is:

```text
InternScience/Agents-A1-Q8_0-GGUF
served through llama.cpp or another OpenAI-compatible local endpoint
Qwen-family / Qwen3-style agentic model assumptions
```

Important limitation:

```text
GGUF endpoint usage may not expose raw router logits or full internal telemetry.
When internal feature rows are unavailable, represent this honestly with
telemetry_missing=true and policy=null. Do not fabricate telemetry features.
```

## Current capability

`jlens` now has the full autonomous private shadow loop:

```text
local shadow wrapper
PolicyEngine v0 advisory scorer
autonomous supervisor
verifier adapters
auto_outcome schema
private log workflow
redaction/export tool
aggregate-only private summaries
commit-safe guard
review queue builder
safe outcome review CLI
reviewed-only calibration reports
human reviewer guide
tests for policy/runtime/review/private/autonomous workflow
```

Current behavior:

```text
- can run task queues against a local endpoint
- records auto_outcome candidates separately from human outcome fields
- applies cheap verifiers where task metadata supports them
- marks telemetry_missing honestly for GGUF/no-router-logit paths
- escalates low-confidence, contradictory, or high-impact cases
- keeps private logs local and gitignored
- produces aggregate-only summaries with no prompt/output text
- final thresholds remain gold/audit gated
```

Current interpretation:

```text
The autonomous supervisor exists.
The next proof is a real local workload run against Agents-A1.
We need an overnight-style run report: what ran, what failed, what escalated,
and what needs human review, without leaking private prompt/output text.
```

## Feature decision

Keep these feature groups when telemetry is available:

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

## Next milestone: M11 real Agents-A1 workload run + autonomous report

M11 should stop proving the harness with fixtures and run a real local batch through the Agents-A1 endpoint. The goal is a private overnight-style shadow run with aggregate-only reporting and a review queue for escalated items.

Suggested command:

```text
/jlens-m11-agents-a1-overnight-shadow-run
```

Read first:

```text
steer.md
reports/FINDINGS.md
docs/AUTONOMOUS_SHADOW_SUPERVISOR.md
docs/PRIVATE_SHADOW_WORKFLOW.md
docs/SHADOW_OUTCOME_REVIEW.md
config/autonomous_supervisor_v0.json
src/autonomous_shadow_supervisor.py
src/verifiers.py
src/autonomous_outcome_report.py
src/private_outcome_summary.py
src/check_commit_safe.py
schema/auto_outcome_v1.json
schema/shadow_outcome_v1.json
```

M11 objectives:

```text
1. Add or update a local run config for the actual Agents-A1 GGUF endpoint.
2. Add a safe task-batch format for real local workloads.
3. Include public smoke tasks plus optional private local-only task queues.
4. Run a bounded real batch: start with 25-100 tasks, not thousands.
5. For each task: call endpoint, record output locally, run verifiers, create auto_outcome, and escalate when needed.
6. Generate an aggregate-only run report with no prompt/output text.
7. Generate a local review queue containing only escalated records.
8. Add run metadata: model name, endpoint alias, config hash, task count, started_at/finished_at, duration, failure counts, escalation counts.
9. Add a resume/retry-safe mode so a long run can continue after interruption.
10. Add docs for how to run the workload locally and how to review the escalated subset.
11. Keep all private raw logs gitignored.
12. Update STATE.md and reports/FINDINGS.md with public-safe summaries only.
```

Recommended run artifacts:

```text
reports/shadow/private/agents_a1_run_*.jsonl       # local only, gitignored
reports/shadow/private/agents_a1_review_*.jsonl    # local only, gitignored
reports/outcomes/agents_a1_run_summary_sample.json # public-safe aggregate sample only
```

Recommended aggregate fields:

```text
run_id
model
endpoint_alias
n_tasks
n_completed
n_failed
n_telemetry_missing
level_distribution
recommended_action_distribution
auto_verdict_distribution
escalation_count
escalation_rate
verifier_distribution
auto_needed_retrieval_count
auto_needed_checker_count
auto_was_wrong_count
human_reviewed_count
auto_vs_human_agreement
privacy_check_status
```

M11 guardrails:

```text
- Do not commit private raw logs.
- Do not commit prompt/output text from real local workloads.
- Do not overwrite human outcome fields with auto_outcome.
- Do not treat auto_outcome as gold.
- Do not run arbitrary shell commands as verifier tests; fixture-only unless explicitly configured.
- If endpoint telemetry is missing, keep telemetry_missing=true.
- If the endpoint fails, record failure counts and continue when safe.
- Production thresholds remain gold/audit gated.
```

M11 deliverables:

```text
config/agents_a1_shadow_run.json
src/run_agents_a1_shadow_batch.py or wrapper around autonomous_shadow_supervisor.py
src/make_escalation_review_queue.py or equivalent
reports/outcomes/agents_a1_run_summary_sample.json
docs/AGENTS_A1_SHADOW_RUN.md
tests for run config validation, resume behavior, aggregate no-text report, and escalation queue generation
updated STATE.md and reports/FINDINGS.md
```

M11 stop condition:

```text
Agents-A1 endpoint config exists
bounded real/smoke batch path exists
private raw records are written only to gitignored private paths
aggregate report contains no prompt/output text
escalation review queue is generated locally
resume/retry behavior is tested or documented
check_commit_safe passes public artifacts
production thresholds remain gold/audit gated
```

## Parallel track after M11

After a real local workload run exists, review a small escalated subset and compare:

```text
auto_outcome vs human outcome
escalation quality
false-low-risk
false-high-risk
retrieval-needed misses
checker-needed misses
```

Then decide whether M12 should be:

```text
M12A: calibration from reviewed Agents-A1 workload records
M12B: broader benchmark scale run
M12C: add missing-label dataset converters
```

## Later data expansion for remaining labels

After the first real Agents-A1 workload report, add second-wave converters to cover remaining labels:

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
AutoSupervisor: autonomous task runs + verifier-backed auto_outcome candidates
RunOps: bounded real workload runs, resumable private records, aggregate reports
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, private prompts, sensitive logs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
