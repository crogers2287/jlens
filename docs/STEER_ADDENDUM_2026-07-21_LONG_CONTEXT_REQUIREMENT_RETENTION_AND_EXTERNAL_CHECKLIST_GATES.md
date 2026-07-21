# STEER ADDENDUM — Long-context requirement retention and external-checklist gates

Date: 2026-07-21

Parent remote head: `db594d64e6418870192cdfadb5c9b95d0c09df1c`

Status: binding future-protocol correction; no current execution authorization

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- GitHub currently reports this repository as public. Aggregate-only commit restrictions remain binding.
- No weight staging, tensor-payload retrieval, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized by this document.
- Every privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, cleanup, commit-safety, comparator, nuisance-control, production-gating, and stop rule remains binding.

## New primary evidence and narrow interpretation

Xue, **How Agent Skills Fail under Long Contexts: A White-Box Study in Code Auditing**, arXiv `2607.17937v1`, submitted 2026-07-20, studies whether procedural requirements loaded through an Agent Skill remain active during a long tool-using code-audit workflow.

The public paper reports the following bounded facts:

1. The task and twenty-four artifact checks were held fixed while the surrounding context was varied.
2. The study classified first-visible failures as lost requirements, editing drift, failed checking, or evaluator/runtime failures.
3. On one task, Codex with `gpt-5.4-mini` passed eight of ten runs with a 10,991-character clean context and three of ten runs under both a 299,140-character relevant context and an equal-length irrelevant context.
4. The resulting fifty-percentage-point difference was trend-level under the reported two-sided Fisher test (`p = 0.0698`), not conventionally significant at 0.05.
5. Requirement coverage remained above ninety-two percent in both long-context conditions, showing that a small number of omissions can invalidate an otherwise nearly complete artifact.
6. A second task passed every clean and long-context run, so the evidence does not establish a universal context-length threshold.
7. A detailed external checklist passed ten of ten runs, while a generic self-check passed five of ten (`p = 0.0325`).
8. Relevant and irrelevant long contexts produced the same reported pass count on the affected task, indicating that context volume or placement may matter independently of semantic relevance in this setting.

These are external single-study results. They do not establish a universal phenomenon called context rot, a model-independent token threshold, a general failure monitor, causal localization from hidden states, or transfer to Agents-A1. No attributable public implementation or immutable experiment package was located during this review.

## Binding correction: a loaded skill is not a persistent control state

Loading a skill, policy, checklist, or procedural instruction into the initial context does not prove that each requirement remains behaviorally active at later decision boundaries.

Future long-horizon agent studies must distinguish:

1. **Instruction availability:** the requirement text exists somewhere in the context or retrievable workspace.
2. **Instruction retrieval:** the requirement is selected into the current working set before the relevant action.
3. **Instruction retention:** the requirement remains represented or externally tracked across intervening actions.
4. **Instruction execution:** the action actually conforms to the requirement.
5. **Instruction verification:** a fresh check determines whether the resulting artifact or state satisfies the requirement.
6. **Outcome correctness:** the overall task succeeds under the canonical verifier.

Passing one level does not establish the next. An internal probe that predicts eventual failure does not prove which requirement was lost. A skill file present in the prompt does not prove the agent consulted it when editing or verifying.

## Context envelope is a required nuisance variable

The **context envelope** at a decision boundary consists of all information that can affect the model or harness, including:

- system, developer, user, and skill instructions;
- active tool schemas and descriptions;
- repository or workspace files loaded into context;
- tool observations and command output;
- generated reasoning or action history;
- summaries, memories, scratchpads, and checkpoints;
- retrieved examples and external documentation;
- ordering, position, duplication, and recency of requirements;
- truncation, compaction, eviction, and cache behavior;
- harness-injected metadata and hidden controller messages.

For every claimed long-horizon monitor or policy result, freeze and report aggregate context-envelope characteristics at each admitted boundary:

- prompt and generated-token counts;
- instruction, tool-output, code, document, memory, and summary proportions;
- requirement positions and distance from the decision boundary;
- number and size of active skills;
- compaction or summarization events;
- retrieval and eviction policy;
- context-window utilization;
- tool-schema count and aggregate size;
- interruption, retry, branch, and resume state.

Raw prompts, skills, tool outputs, code, private trajectories, and per-example context traces remain prohibited from this public repository. Only preregistered aggregate summaries may be committed.

## Mandatory context controls

Future agent-monitoring studies must include the following controls when technically compatible:

1. A minimal clean context containing only the task, required tools, and frozen procedural contract.
2. A semantically relevant long-context condition.
3. A length-matched irrelevant-context condition.
4. A position-matched condition that moves the same requirements earlier or later without changing their text.
5. A duplication control that repeats requirements without adding new substance.
6. A progressive-disclosure condition that loads requirements only when their preconditions become active.
7. A bounded working-set condition that externalizes inactive material.
8. A context-compaction or summary condition with immutable summary provenance.
9. A no-skill condition.
10. A skill-present but checklist-disabled condition.

Task, model, checkpoint, harness, tools, decoding, verifier, seed policy, and outcome taxonomy must be matched across conditions. Repeated runs from the same task, template, repository, or environment are clustered observations rather than independent examples.

A context-length effect that disappears under position, tool-output, or working-set controls must be described as a context-envelope effect rather than a universal length effect.

## External checklist and requirement-ledger comparator

A detailed external checklist is now a mandatory future comparator for tasks with enumerable requirements.

The comparator must:

- be derived from the task contract, skill, policy, or admitted specification before outcomes are observed;
- assign immutable requirement identifiers;
- bind each requirement to an allowed evidence source and verification procedure;
- record `pass`, `fail`, `not_applicable`, `blocked`, or `verifier_unavailable` without silently converting missing evidence to pass;
- execute checks at frozen decision boundaries;
- preserve failed and disputed checks for final outcome accounting;
- distinguish a generic self-review prompt from a deterministic or explicitly structured external checklist;
- remain mutation-isolated from the artifact unless a separately admitted repair policy is under study.

When deterministic verification is impossible, the checklist may use a separately admitted judge, but judge identity, prompt, temperature, context boundary, output schema, disagreement handling, and cost must be frozen. Judge output remains model evidence rather than ground truth until validated against canonical outcomes.

A hidden-state, router, workspace, sparse-feature, transcoder, or Jacobian monitor cannot be called operationally necessary when an external requirement ledger achieves equal sealed utility at lower total cost.

## Requirement-loss localization and outcome taxonomy

Future evaluations must separate at least:

1. requirement unavailable or omitted from the active context;
2. requirement available but not retrieved;
3. requirement retrieved but ignored;
4. correct plan followed by editing or execution drift;
5. artifact correct before a later destructive edit;
6. failed or incomplete checking;
7. checker false positive or false negative;
8. evaluator, tool, runtime, or environment failure;
9. recoverable intermediate violation;
10. irreversible external action or terminal artifact failure;
11. complete success.

A final task failure label cannot identify the first failed requirement or the first irreversible boundary. Retrospective localization, prefix anomaly detection, eventual-failure prediction, and pre-action intervention remain separate claims.

Requirement-level coverage must be reported alongside task-level pass rate. High average coverage cannot substitute for complete satisfaction when the contract is conjunctive.

## Checklist leakage and selection controls

The checklist, requirement ontology, evidence rules, checking order, decision boundaries, aggregation rule, thresholds, and fallback policy must be frozen before outer validation, certification, or sealed outcomes are opened.

The checklist may not receive:

- canonical patch or answer information unavailable in deployment;
- future trajectory steps;
- post-intervention evidence;
- sealed verifier labels;
- private production outcomes outside an authorized boundary;
- failure-specific hints produced after inspecting sealed errors.

Checklist additions prompted by a failure require a new training or development cycle and a fresh sealed population. Failed sealed cases cannot be patched into the checklist and rescored as if prospectively specified.

## Internal-monitor residual-value gate

Internal signals must be evaluated both on the complete population and on the residual failures not already detected by the admitted external checklist and deterministic controls.

Required matched comparisons include:

- task and context metadata only;
- generic self-check;
- detailed external checklist;
- requirement ledger plus deterministic verifier;
- confidence and logit summaries;
- passive hidden-state probes;
- fixed-budget trajectory summaries;
- peer-model representations where admitted;
- minimal conditional router telemetry for MoEs;
- sparse-feature or transcoder streams;
- Jacobian-Lens streams only after exact derivative parity.

Every comparator must receive the same task partition, decision boundaries, outcome taxonomy, and allowed information. Internal-monitor value that disappears after conditioning on context-envelope variables, checklist failures, requirement position, or verification history must be classified as context or process telemetry rather than privileged correctness information.

## Long-horizon recertification and drift

No context-retention result transfers automatically across:

- model or checkpoint revisions;
- quantization or precision policies;
- dense and MoE architectures;
- system prompts, skills, or harness versions;
- tool schemas or tool counts;
- context-window sizes;
- compaction, memory, or retrieval policies;
- task families, repositories, modalities, or languages;
- single-agent and multi-agent execution;
- serving backends, caching, batching, or resume behavior.

Material changes require renewed calibration and sealed evaluation. There is no universal safe context length unless independently established across the claimed deployment distribution.

## Cost and privacy accounting

Long-context and checklist comparisons must include:

- input, output, replay, and summary tokens;
- retrieval, reranking, and context-construction cost;
- repeated skill loading or requirement refresh;
- checklist and verifier execution;
- tool calls and failed attempts;
- memory, KV cache, latency, throughput, and accelerator-seconds;
- context compaction and state checkpointing;
- storage, retention, access control, and privacy filtering;
- fallback and recovery work after a missed requirement.

A reduced failure rate obtained by repeatedly reinjecting the entire private trajectory is not a low-cost or privacy-preserving result. The minimum retained state must be justified, and raw requirement traces or per-example compliance histories remain outside this public repository.

## Agents-A1 scaling directive

Agents-A1 is explicitly a long-horizon agent family, so context-envelope and requirement-retention controls precede expensive internal instrumentation.

The technically credible sequence is:

1. Complete Q35Q production-path provenance and exact derivative admission on one frozen static runtime.
2. Define matched long-horizon task contracts and immutable requirement ledgers without sealed-outcome access.
3. Establish minimal-context, relevant-long-context, irrelevant-length-matched, position, compaction, and progressive-disclosure controls.
4. Establish deterministic external checks and detailed checklist baselines.
5. Evaluate the separately admitted Agents-A1-4B dense sibling under the same context envelopes and requirement contracts.
6. Evaluate confidence, passive hidden-state, and bounded trajectory summaries on full-population and residual failures.
7. Capture minimal executed-route telemetry on Agents-A1-35B only after context and checklist nuisance controls are fixed.
8. Compare route features against requirement position, checklist state, verification history, and dense-sibling representations.
9. Add sparse-feature or transcoder streams when admitted.
10. Add Jacobian-Lens features only after exact derivative parity and sealed incremental value over every cheaper comparator.
11. Keep context compaction, memory rewriting, requirement reinjection, abort, retry, truncation, tool suppression, forced routing, activation steering, and production deployment under separate intervention gates.

A monitor that predicts failures caused by preventable requirement omission may still be useful, but it does not justify Jacobian or router instrumentation when a cheaper external requirement ledger prevents or detects the same failures.

## Current blocker and execution order

This addendum does not change the active blocker.

The next admissible engineering work remains one clean-subprocess, fail-closed production adapter that:

1. verifies the frozen upstream Transformers artifact;
2. binds the live import to its owning installed distribution and `RECORD`;
3. derives complete live source closure for dispatch, converters, nested operations, model/configuration classes, and loader objects;
4. rejects shadow packages, editable installs, monkeypatches, forged identities, incomplete closure, wrong ownership, and unadmitted loaders;
5. invokes and binds the actual GPTQModel/Defuser loader entry point;
6. freezes the complete immutable runtime tuple;
7. passes the full adversarial integration conjunction;
8. emits only the permitted aggregate result.

After that remain strict synthetic loading, exact quantization-tensor consumption and expert-ordering proof, forward/VJP/JVP/finite-difference parity, Phase-0 admission, weight staging, and a separately authorized GPU transition.

## Established versus unproven

Established only as external public evidence:

- In one reported code-audit task, a short clean context produced more passing runs than two much longer context conditions.
- Relevant and irrelevant length-matched long contexts produced the same reported pass count on that task.
- Requirement coverage remained high despite task-level failures, indicating that a few omissions can dominate conjunctive artifact success.
- A detailed external checklist outperformed a generic self-check in the reported runs.
- A second task showed no degradation, so the result does not establish a universal context threshold.
- Context-envelope and external-checklist controls are therefore mandatory future comparators for compatible long-horizon monitoring claims.

Unproven for this program:

- independent reproduction or an immutable public experiment package;
- a universal context-length threshold or general context-rot law;
- transfer beyond the tested model, harness, tasks, and code-audit workflow;
- requirement-loss prediction from hidden states, routes, workspace features, or Jacobians;
- causal localization of the first omitted requirement;
- checklist completeness under open-ended tasks;
- stable retention across Agents-A1-4B or Agents-A1-35B;
- incremental router or Jacobian-Lens value after context and checklist controls;
- safe context compaction, requirement refresh, early exit, retry, escalation, expert intervention, activation steering, or production deployment.

The research program remains unfinished. Q35Q remains blocked at production-path upstream/runtime provenance composition.
