# STEER ADDENDUM — External-invariant checker and retrospective-localization gates

Date: 2026-07-18

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q, authorize scientific execution, or weaken any privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized.
- GitHub currently reports this repository as public. Commits remain restricted to aggregate program-control records and public-source engineering code or tests.

## New public evidence

Microsoft's **AgentRx: Diagnosing AI Agent Failures from Execution Trajectories** (`arXiv:2602.02475`) provides a concrete external-checking comparator for future agent-monitor work.

The public paper, benchmark, and implementation report:

1. A benchmark of 115 manually annotated failed trajectories spanning structured API workflows, incident management, and open-ended Web/file tasks.
2. A pipeline that normalizes a trajectory, synthesizes static and step-specific invariants, executes guarded checks, records evidence-backed violations, and asks an LLM judge to localize and classify the critical failure.
3. Reported absolute gains of `23.6` percentage points in failure-step localization and `22.9` percentage points in root-cause attribution over prompting baselines.
4. A grounded failure taxonomy covering plan adherence, invented information, invalid invocation, tool-output misinterpretation, intent-plan misalignment, underspecified intent, unsupported intent, guardrail blocks, system failure, and inconclusive cases.

The associated public repository was inspected at immutable commit:

`f228165bfec60a801fd5fedd9d8ffe0f9de0c69d`

Bounded code facts at that revision include:

- The step-by-step dynamic-invariant prompt receives the complete trajectory prefix through the current step, not future steps.
- The invariant generator can synthesize executable checks tied to a current trajectory step and earlier evidence.
- The final judge receives the complete trajectory as a conversation and predicts a failure index and category.
- The released benchmark is composed of failed trajectories; it is not a full-population online-control benchmark.

These are external public findings, not admitted results of this repository. AgentRx is primarily a retrospective diagnosis and localization system. It does not establish prospective correctness prediction, safe early exit, latent error awareness, causal expert localization, or transfer to Agents-A1.

## Binding correction: external contract checking is a required comparator

Tool-using agents expose many failures that can be detected without model-internal telemetry. Future Agents-A1 studies must compare internal monitoring against an admitted external checker stack whenever the relevant schemas, policies, preconditions, postconditions, or cross-tool relations are available.

The minimum comparator ladder is:

1. Tool-schema and argument validation.
2. Static policy, permission, capability, and ordering invariants.
3. Deterministic cross-tool provenance and relational checks.
4. Frozen prefix-conditioned dynamic invariants.
5. Violation-log classification or localization.
6. Metadata, confidence, and hidden-state monitors.
7. Router telemetry.
8. Jacobian-Lens features.
9. Frozen combinations of external and internal signals.

A hidden-state, router, or Jacobian feature cannot be called operationally necessary when an external deterministic checker catches the same failure class at lower total cost and with equal or better sealed utility.

## Diagnosis, prediction, and control are separate claims

The protocol now distinguishes:

1. **Retrospective diagnosis:** the full trajectory and terminal outcome are available.
2. **Retrospective localization:** the system identifies the first critical or unrecoverable failure after the episode is known to have failed.
3. **Prefix anomaly detection:** only information available through a stated boundary is used.
4. **Prospective failure prediction:** the system predicts eventual failure before the outcome is known.
5. **Online intervention:** the prediction changes execution and improves utility under a separately admitted policy.

Success at one level does not authorize a claim at a later level.

A critical-failure label is inherently retrospective when identifying unrecoverability requires observing later recovery attempts, side effects, or terminal failure. Such a label may be used for diagnosis but cannot be represented as an online stopping label without a prospectively defined decision-time target.

## Decision-boundary requirements

Every external or internal monitor must state exactly when its inputs become available:

- before action generation;
- during action-token generation;
- after action generation but before execution;
- after tool execution;
- after the round;
- after terminal outcome;
- during retrospective replay.

Only work occurring after the stated boundary may be credited as saved.

A full-trajectory judge is retrospective. A prefix-generated invariant can be prospective only if the invariant, its trigger, and every input used by the check are available before the protected action or decision.

## Failed-only benchmark limitation

A benchmark containing only failed trajectories can evaluate localization conditional on known failure. It cannot by itself establish:

- false-positive rates on successful episodes;
- calibration over the natural success/failure prevalence;
- valid abstention behavior;
- unnecessary intervention rates;
- right-to-wrong transitions caused by the monitor;
- complete policy utility.

Future evaluation must preserve the complete outcome population, including successful trajectories, recoverable mistakes, terminal failures, malformed actions, tool failures, guardrail blocks, valid abstentions, invalid refusals, timeouts, and verifier failures.

Required reporting includes both:

1. Conditional localization metrics on genuinely failed trajectories.
2. Full-population detection and policy metrics at the natural or prospectively frozen deployment prevalence.

## Invariant-synthesis leakage controls

Invariant generation is model selection and may encode task-specific information. The following must be frozen before outer-validation or sealed labels are opened:

- tool schemas and policy documents;
- invariant-generator model and immutable revision;
- generator prompts and examples;
- static versus dynamic generation mode;
- trajectory prefix available to the generator;
- invariant taxonomy and allowed check types;
- trigger rules, step windows, and relation scopes;
- checker runtime and exception behavior;
- violation aggregation and thresholding;
- judge model, prompt, taxonomy, and calibration.

The generator may not receive terminal outcomes, canonical answers, verifier labels, future steps, hidden sealed annotations, or post-intervention evidence unavailable at the proposed decision boundary.

Per-example invariant generation on a sealed trajectory is admissible only as a prospectively frozen online algorithm, with the same generator, prompt, context boundary, cost, latency, and failure handling used in deployment. It cannot be silently performed offline with access to later events and then represented as online monitoring.

## Deterministic and language-model checks must be separated

Future reports must disaggregate:

- schema checks;
- deterministic executable checks;
- natural-language checks;
- LLM-judge classification;
- internal latent features.

A language-model-generated invariant is not deterministic merely because its emitted checker is executable. The generator's stochasticity, prompt sensitivity, code quality, and model drift remain part of the system.

Required controls include:

- frozen deterministic hand-written checks;
- generated checks with the outcome and failure taxonomy removed;
- random or irrelevant checks matched for execution cost;
- generator ablation;
- judge ablation;
- violation-log-only baselines;
- schema-only and policy-only baselines;
- repeated generation under fixed and varied seeds where applicable.

## Generated-check execution safety

LLM-produced executable checks require a separate code-execution admission boundary.

They must run in a constrained environment with:

- no network access;
- no filesystem access except an explicitly admitted read-only input object;
- no credentials or environment secrets;
- no process creation;
- no dynamic imports;
- bounded CPU, memory, output, and wall time;
- immutable allowed builtins and libraries;
- deterministic serialization of inputs and outputs;
- explicit exception and timeout semantics;
- source retention sufficient for audit without exposing sealed trajectory data.

A generated check that crashes, times out, accesses an unadmitted capability, or cannot be reproduced must fail to `monitor_unavailable`, not silently pass and not automatically classify the agent as incorrect.

## Coverage and residual-error accounting

External invariants are naturally strong for some failure classes and weak for others.

Future studies must report performance separately for:

- malformed or schema-invalid tool calls;
- missing required arguments;
- capability and permission violations;
- ordering and confirmation failures;
- arithmetic and relational inconsistencies;
- unsupported claims relative to prior tool output;
- semantic reasoning errors not expressible as a frozen invariant;
- premature stopping;
- latent planning errors before an observable violation;
- verifier or benchmark-label failures.

Internal monitor value must be measured on both:

1. The full population.
2. The residual population not already detected by admitted external checks.

A latent feature that merely reproduces schema or policy violations visible in the trace is redundant telemetry, not evidence of internal correctness awareness.

## Verifier and label separation

The existing verifier-blind boundary remains binding.

Canonical answers, terminal success labels, test results, human root-cause annotations, and judge outputs may be used to construct labels only after monitor features and external-check outputs for the stated boundary are frozen.

Violation logs may be monitor inputs only if they are generated from information available at the decision boundary. A violation inferred using future steps or final outcome is label-side evidence and may not enter a prospective monitor.

Judge-versus-canonical disagreement, inter-annotator disagreement, ambiguous root causes, multiple simultaneous failures, and recoverability disagreements must be reported rather than forced into a single clean label.

## Cost and latency accounting

External checking is not free. Future comparisons must include:

- policy and schema preparation;
- invariant synthesis;
- code validation and sandbox startup;
- deterministic checker execution;
- LLM-judge calls;
- trajectory normalization and serialization;
- telemetry storage and retrieval;
- privacy filtering;
- latency, accelerator-seconds, CPU time, memory, and network use;
- repeated checks across long horizons;
- maintenance and recertification after tool or policy changes.

A small checker-runtime number is not end-to-end monitor cost when invariant generation, trajectory replay, normalization, or judge execution occurs elsewhere.

## Drift and recertification

External-check evidence does not transfer automatically across:

- tool-schema revisions;
- policy revisions;
- changed harness serialization;
- new tools or actions;
- new environment states;
- model or agent revisions;
- changed modalities;
- different trajectory horizons;
- different judge or generator models;
- changed failure prevalence.

Material changes require invariant revalidation, false-positive testing, coverage measurement, and policy recertification.

## Privacy and retention

Trajectory diagnosis systems can contain user instructions, tool arguments, tool outputs, proprietary data, policy documents, credentials, code, file contents, verifier evidence, and outcome labels.

The public-repository boundary remains binding. Raw trajectories, generated per-example invariants, violation logs, prompts, outputs, tool payloads, labels, hidden states, router traces, Jacobians, credentials, and proprietary policies must not be committed.

Any future external telemetry store requires a frozen purpose, minimization policy, access control, retention limit, deletion procedure, reconstruction threat model, and separate authorization.

## Agents-A1 scaling directive

The technically credible comparator-first sequence is now:

1. Complete Q35Q runtime provenance and derivative admission.
2. Establish tool/action metadata, finish-reason, confidence, and selected hidden-state baselines.
3. Admit deterministic tool-schema, permission, ordering, and cross-tool provenance checks.
4. Evaluate a frozen prefix-conditioned dynamic-invariant checker at explicit pre-action and post-action boundaries.
5. Measure full-population false positives, residual failure coverage, and end-to-end cost.
6. Add a retrospective AgentRx-style localization system only as a diagnosis comparator, not an online monitor.
7. Evaluate compact router telemetry on the residual failures not already caught externally.
8. Compare external-only, hidden-state-only, router-only, and combined systems under equal total cost.
9. Add Jacobian-Lens features only after exact derivative parity and after cheaper external and internal approaches fail the sealed incremental-value gate.
10. Keep abort, retry, escalation, truncation, tool suppression, forced routing, expert intervention, and activation steering under separate policy and safety gates.

This sequence prioritizes cheap, auditable, action-grounded controls before expensive large-MoE derivative instrumentation while preserving a path for Jacobian features to prove genuinely residual value.

## Current blocker and execution order

This addendum does not change the active blocker. The required order remains:

1. Production-path upstream/runtime provenance composition.
2. Freeze the complete GPTQModel/Defuser/Optimum/Accelerate/PyTorch/CUDA/backend tuple.
3. Run a strict synthetic Qwen3.5-MoE GPTQ loader fixture.
4. Prove exact tensor consumption, expert ordering, and fusion identity.
5. Prove forward, activation-VJP, activation-JVP, and finite-difference parity.
6. Pass the complete adversarial Phase-0 conjunction.
7. Stage weights only after admission.
8. Obtain a separately authorized GPU-resource transition.
9. Prove full-model derivative parity.
10. Fit Q35Q under the frozen protocol.
11. Run sealed detection-only comparisons including admitted external-checker baselines.
12. Begin Agents-A1-native instrumentation only if Q35Q establishes incremental monitor value.

## Established versus unproven

Established only as external public evidence:

- Constraint synthesis and guarded invariant checking can improve retrospective failure-step localization and root-cause attribution in the reported benchmark.
- Some dynamic invariants can be generated from a trajectory prefix through the current step.
- The released final judge uses the complete trajectory and is therefore retrospective.
- The released benchmark contains failed trajectories and does not establish full-population false-positive or intervention utility.
- External schema, policy, provenance, and relational checks are a credible low-cost comparator class for tool-using agents.

Unproven for this program:

- Q35Q admission or derivative parity.
- Independent reproduction of AgentRx.
- Online latency and false-positive behavior of generated invariants on Agents-A1.
- Safety and determinism of generated executable checks under production constraints.
- Prospective prediction of eventual failure from AgentRx features.
- Transfer of AgentRx's taxonomy, checks, or localization accuracy to Agents-A1.
- Incremental hidden-state, router, or Jacobian-Lens value after admitted external invariants.
- Safe abort, retry, escalation, truncation, tool suppression, routing intervention, activation steering, or production utility.
