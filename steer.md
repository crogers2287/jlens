# steer.md — post-M9 autonomous calibration steering

Read this first before continuing `jlens`.

M1 through M9 are complete. Do not redo benchmark ingestion, the M5 smoke test, PolicyEngine v0, the local shadow wrapper, outcome-review tooling, or the private-log workflow.

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
```

## Current model/runtime context

The current autonomous local model target is:

```text
InternScience/Agents-A1-Q8_0-GGUF
served through llama.cpp or another OpenAI-compatible local endpoint
Qwen-family / Qwen3-style agentic model assumptions
```

Important limitation:

```text
GGUF endpoint usage may not expose raw router logits or full internal telemetry.
When internal feature rows are unavailable, policy can still log agent actions,
outputs, checks, verifier results, and outcome signals. Mark policy=null or
telemetry_missing rather than fabricating features.
```

## Current capability

`jlens` now has the full private shadow feedback loop:

```text
local shadow wrapper
PolicyEngine v0 advisory scorer
private log workflow
redaction/export tool
aggregate-only private summary
commit-safe guard
review queue builder
safe outcome review CLI
outcome schema
reviewed-only calibration reports
human reviewer guide
tests for policy/runtime/review/private workflow
```

Current behavior:

```text
- scores telemetry feature rows when available
- logs advisory recommendations
- keeps private logs local and gitignored
- redacts prompt/output/notes text when exporting
- summarizes reviewed outcomes without committing private text
- computes calibration only from reviewed records
- stays advisory/shadow only
- final thresholds remain gold/audit gated
```

Current interpretation:

```text
The safety and privacy plumbing is built.
The remaining bottleneck is not more manual tooling; it is autonomous use.
M10 should build an autonomous supervisor loop that runs tasks, judges outcomes,
records evidence, and escalates only uncertain cases.
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

## Next milestone: M10 autonomous shadow supervisor

M10 should remove the manual bottleneck without pretending the system is production-calibrated. Build an autonomous loop that can run local tasks, collect outputs, apply cheap verifiers, create auto-outcome candidates, and escalate ambiguous/high-impact cases for later review.

Suggested command:

```text
/jlens-m10-autonomous-shadow-supervisor-loop
```

Read first:

```text
steer.md
reports/FINDINGS.md
docs/POLICY_ENGINE_V0.md
docs/M7_SHADOW_RUNTIME.md
docs/SHADOW_OUTCOME_REVIEW.md
docs/PRIVATE_SHADOW_WORKFLOW.md
schema/shadow_outcome_v1.json
src/local_shadow_wrapper.py
src/policy_engine.py
src/private_outcome_summary.py
src/redact_shadow_log.py
src/check_commit_safe.py
```

M10 objectives:

```text
1. Add an autonomous supervisor config for a local OpenAI-compatible endpoint.
2. Support the current Agents-A1 GGUF model target explicitly.
3. Run a task queue from public fixtures and local private queues.
4. For each task: call model, capture output, attach telemetry if available, call PolicyEngine if possible, and write a private shadow record.
5. Add verifier adapters for cheap checks: exact-answer match, regex/schema check, math checker, code/test command stub, retrieval-required heuristic, and self-consistency sample comparison.
6. Add an auto-outcome candidate layer separate from human outcome fields.
7. Never overwrite human-reviewed outcome fields with auto judgments.
8. Assign confidence to auto-outcomes and escalate low-confidence, contradictory, or high-impact cases.
9. Produce aggregate-only autonomous run summaries with no prompt/output text.
10. Add tests using fake endpoints and public fixtures only.
```

Separate human and autonomous fields:

```text
outcome:
  user_agreed
  was_wrong
  needed_retrieval
  needed_checker
  notes

auto_outcome:
  auto_judged
  auto_was_wrong
  auto_needed_retrieval
  auto_needed_checker
  verifier_names
  verifier_confidence
  verifier_evidence_hash
  escalate_for_review
  auto_notes_redacted
```

Verifier guidance:

```text
exact-answer tasks:
  compare final answer against known answer

math tasks:
  extract answer and verify with deterministic calculation when possible

code tasks:
  run fixture tests only; do not run arbitrary untrusted commands by default

retrieval/current-info tasks:
  mark auto_needed_retrieval=true when task category or heuristic requires freshness/citation

self-consistency:
  run small N samples and flag disagreement, not as proof of wrongness but as escalation signal
```

Autonomy guardrails:

```text
- Autonomous review may create auto_outcome candidates.
- Human outcome fields remain null until reviewed by a human or explicit trusted process.
- Production thresholds remain gated.
- No private prompt/output text in committed files.
- No real tool execution beyond approved fixture commands.
- If telemetry is missing from GGUF serving, log telemetry_missing honestly.
- Do not count auto_outcome as gold unless a later audit promotes it.
```

M10 deliverables:

```text
config/autonomous_supervisor_v0.json
src/autonomous_shadow_supervisor.py
src/verifiers.py
schema/auto_outcome_v1.json
src/autonomous_outcome_report.py
docs/AUTONOMOUS_SHADOW_SUPERVISOR.md
reports/outcomes/autonomous_summary_sample.json
fixture tests for fake endpoint, verifier adapters, auto_outcome schema, and aggregate-only summaries
updated STATE.md and reports/FINDINGS.md
```

M10 stop condition:

```text
autonomous supervisor runs fixture tasks end-to-end
local endpoint config supports Agents-A1 GGUF style serving
auto_outcome candidates are recorded separately from human outcomes
aggregate summaries contain no private text
telemetry_missing is represented honestly when needed
ambiguous cases are escalated for review
production thresholds remain gold/audit gated
```

## Parallel track after M10

After the autonomous supervisor exists, run a local private workload and accumulate:

```text
auto_outcome candidates
human-reviewed subset
aggregate-only summaries
calibration notes
escalation counts
```

Benchmark scale targets remain:

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
review escalation rate
auto-vs-human agreement where reviewed
```

## Later data expansion for remaining labels

After autonomous shadow supervision exists, add second-wave converters to cover remaining labels:

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
HiddenLens: future phase only after the risk governor baseline is validated
```

## Repository hygiene

Do not commit raw captures, private prompts, sensitive logs, caches, local environments, model weights, raw datasets, or large generated artifacts unless explicitly intended.
