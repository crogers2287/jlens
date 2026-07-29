# STEER ADDENDUM — Self-speculating tool calls, action-commit boundaries, and side-effect gates

Date: 2026-07-29
Parent remote head: `417317474a3762e6b9f967acb7df5640271fd65b`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no model retrieval, model execution, GPU use, telemetry capture,
Jacobian fitting, sealed evaluation, fine-tuning, reinforcement learning,
speculative tool execution, external-state mutation, early exit, retry, repair,
or production action.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q loader and
derivative admission. This addendum changes future agent-action telemetry,
self-speculation, asynchronous-I/O, adaptation, and production-control
requirements. It does not displace that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and
public-source engineering material may be committed. Prompts, outputs, tool
arguments, tool results, user identifiers, per-example predicted or executed
actions, hidden states, cache traces, router traces, sealed outcomes,
credentials, host paths, and private runtime facts remain prohibited.

## Triggering primary evidence

`Speculate While You Reason: Teaching Agents to Predict Their Next Tool Call via
Joint Agent-Speculator RL`, arXiv `2607.25816v1`, studies a single model operated
in two modes:

- agent mode produces the ordinary reasoning and tool-use trajectory;
- speculator mode receives a prefix immediately before an eventual tool call,
  plus a fixed speculation suffix, and predicts that future structured call;
- both modes reuse the same model weights and prefix KV cache;
- speculation targets are derived from the current agent's own rollouts; and
- alternating reinforcement-learning updates improve next-call agreement while
  attempting to preserve task performance.

The paper reports average exact next-call Hit@1 increasing from 44.1 to 61.2 for
Qwen3-4B and from 48.9 to 66.3 for Qwen3.5-4B under its reported matched-domain
experiments. It separately reports cross-domain conditions where next-call
agreement increases while end-task success decreases. This demonstrates that
agreement with the agent's later action and objective task success are separate
quantities.

The reported evaluation reconstructs prefixes at realized tool-call boundaries
and asks the model to predict the tool name and complete argument dictionary.
The environment executes only the agent's actual call during evaluation. Thus
the published Hit@1 result is retrospective action-agreement evidence, not a
production speculative-execution result.

The paper explicitly limits practical pre-execution to calls that do not mutate
external state. It identifies orders, messages, database writes, and irreversible
workflows as requiring dry-run, rollback, confirmation, or restriction to a
read-only phase.

No attributable immutable public implementation revision was admitted for this
correction.

## Bounded interpretation

The evidence supports this narrow correction:

> A model can be trained to predict its own later structured tool call from a
> partial trajectory, but predicted action, later emitted action, safely
> reusable execution, objective task outcome, and production authorization are
> separate scientific and executable objects.

A high self-speculation Hit@1 does not establish:

- that the predicted action is objectively correct;
- that the later agent action is objectively correct;
- that the action is safe to execute before commitment;
- that arguments are semantically equivalent under the tool's contract;
- that the environment remained unchanged between prediction and commitment;
- that the cached result is still valid when consumed;
- that the adaptation preserved out-of-domain agent competence;
- that the model has an explicit plan, intent variable, or semantic workspace;
- that hidden-state, router, expert, or Jacobian telemetry predicts success; or
- that the system reduces end-to-end latency after all branch and execution
  overhead.

Self-speculation changes the model when trained jointly. It is therefore a new
adapted checkpoint and policy, not a passive monitor attached to a fixed agent.

## Binding object-identity gate

Every future tool-call speculation study must freeze and report these objects
separately where they exist:

1. base model checkpoint and executable runtime;
2. adapted self-speculating checkpoint;
3. tokenizer, chat template, reasoning parser, and tool-call parser;
4. tool registry and exact schema revision;
5. trajectory prefix and environment snapshot at the speculation boundary;
6. speculation trigger and fixed suffix or mode identifier;
7. prefix KV cache and any branched cache state;
8. speculative decode settings and structured output;
9. parser result before canonicalization;
10. canonical tool name and canonical argument object;
11. later agent-mode reasoning continuation;
12. later emitted tool-call text and parsed structure;
13. committed action after policy and permission checks;
14. pre-executed action, if any;
15. external environment state before and after execution;
16. returned result, result identity, and freshness boundary;
17. cache admission, reuse, invalidation, and discard decision;
18. final task output;
19. independently verified task outcome;
20. irreversible side effects, rollback state, and audit record; and
21. complete systems cost and runtime identity.

A field called `predicted_tool`, `next_action`, `hit`, `exact_match`, `cache_hit`,
`safe_call`, `task_success`, or `latency_saved` does not satisfy this gate without
proving which object and boundary it represents.

## Retrospective-label and temporal-boundary gate

The agent's eventual tool call is future information at the earlier speculation
boundary. It may be used as a supervised or reinforcement-learning target on
nonsealed training data. It may not enter online features at that boundary.

Every study must freeze:

- the exact boundary immediately before prediction;
- which tokens and tool observations are available at that boundary;
- whether the target is the first later tool call, next parsed call, next
  committed action, or another object;
- handling of trajectories with no later call, malformed calls, retries,
  parallel calls, cancellations, or policy rejection;
- train, calibration, validation, and sealed trajectory partitions;
- rollout-policy revision used to generate targets; and
- regeneration rules when the adapted policy changes.

A target derived from the current policy is policy-relative. As the policy
changes, the label distribution changes. Improved agreement may reflect greater
self-consistency, reduced action diversity, template regularization, or action
collapse rather than improved task reasoning.

Required controls include:

- frozen-agent targets versus on-policy targets;
- action-frequency and template-only baselines;
- same tool name with wrong arguments;
- right arguments under the wrong tool;
- semantically equivalent versus byte-identical arguments;
- independently verified optimal or acceptable action sets where available;
- trajectories with multiple valid next actions;
- wrong-but-self-consistent actions; and
- correct actions that differ from the agent's realized choice.

## Action-agreement versus objective-outcome gate

Next-call agreement is not an outcome verifier.

Future evaluations must report separately:

1. tool-name agreement;
2. argument-field agreement;
3. canonical exact agreement;
4. semantic contract agreement where prospectively defined;
5. committed-action agreement;
6. tool execution success;
7. environment-state correctness;
8. downstream task success;
9. newly introduced regressions; and
10. independently verified prohibited or unsafe outcomes.

A self-speculator that predicts an agent's wrong action perfectly is a successful
behavioral predictor and a failed correctness monitor.

Cross-domain evaluation is mandatory for any generality claim. The triggering
paper's reported cross-domain result, where agreement improves while task success
falls, is direct evidence that these metrics can dissociate.

## Parser, schema, and canonicalization gate

Tool-call exact match depends on parser and schema identity.

Every admitted condition must freeze:

- raw generated bytes;
- reasoning-content and tool-call separation;
- parser implementation and revision;
- schema version and required/optional fields;
- default insertion;
- key ordering and duplicate-key handling;
- numeric, string, boolean, null, list, and object normalization;
- Unicode, whitespace, escaping, and case handling;
- enum aliases and tool-name aliases;
- omitted versus explicit default arguments;
- extra-field behavior;
- invalid-output and partial-parse behavior; and
- canonical serialization used for equality and cache keys.

Byte equality, parsed-object equality, semantic equivalence, and safe result reuse
are separate claims. A parser change can alter Hit@1 without changing model
behavior. A schema change can make a previously valid cached result invalid.

Required adversarial cases include malformed XML or JSON, duplicate fields,
unknown fields, optional-parameter variation, long-context parser boundaries,
parallel calls, mixed reasoning/tool output, parser fallback, and ambiguous
canonicalization.

## Read-only and external-side-effect gate

Speculative execution is prohibited by default.

A call may enter a prospective speculative-execution study only after its tool
contract is classified into one of these categories:

1. pure deterministic local computation;
2. read-only external query with stable identity;
3. read-only but time-varying or metered query;
4. reversible state mutation with proven transaction semantics;
5. state mutation requiring human confirmation;
6. irreversible or externally consequential action; or
7. unknown or insufficiently specified behavior.

Categories 4 through 7 may not be pre-executed without a separately admitted
transaction, rollback, confirmation, and production-control protocol. Category 6
remains prohibited for speculative execution.

A nominally read-only call may still have side effects through billing, rate
limits, audit logs, access notifications, privacy exposure, cache warming,
provider state, or anti-abuse systems. These effects must be included in the
classification.

The allowlist must be explicit and fail closed. Tool descriptions generated by a
model do not establish safety classification.

## Snapshot, freshness, and result-reuse gate

Exact action agreement does not by itself make an early result reusable.

Result reuse requires proof that:

- the committed action matches the admitted canonical speculative action;
- authorization and credentials are unchanged;
- the user, tenant, namespace, and permission scope are identical;
- the relevant environment snapshot has not changed;
- tool and schema revisions match;
- result freshness remains within a prospectively frozen bound;
- nondeterministic seeds and locale/timezone identities match where relevant;
- no intervening action invalidated the result;
- the result was not exposed to the agent before the ordinary commitment point;
  and
- reuse cannot leak information across users, tasks, or sealed populations.

A result produced under stale state must be discarded even when the call text is
identical. A discarded speculative result may still have consumed budget or
revealed private data to an external provider; discard is not equivalent to no
effect.

## Branched-cache and state-lineage gate

Self-speculation reuses a prefix cache and branches generation. That creates
separate state lineages.

Future studies must distinguish:

- the shared prefix state;
- the speculator branch state;
- the continuing agent branch state;
- any recurrent or linear-attention state;
- tool-parser state;
- speculative result state;
- cache merge or discard behavior; and
- resumed agent state after commitment.

The speculator branch may not contaminate the agent branch in an observation-only
condition. Required parity includes native agent tokens, parsed actions, hidden
and recurrent state, router and expert route where applicable, final outputs, and
verifier outcomes.

If speculation tokens, suffix tokens, branch activations, or speculative tool
results influence the continuing agent before the ordinary commitment boundary,
the condition is an intervention and a different agent policy.

## Adaptation and dual-mode interference gate

Joint agent-speculator SFT or RL creates a new checkpoint. The following must be
frozen:

- base and adapted checkpoint digests;
- training trajectory source and policy revision;
- successful-trajectory selection rule;
- speculation-example construction;
- agent and speculator rewards;
- shaping and normalization;
- optimizer state and reset policy;
- update schedule and mode-switch cadence;
- rollout count, seeds, precision, topology, and stopping rule;
- task and domain mixture;
- parser and schema during training; and
- complete training and inference cost.

Required evaluations include:

- matched-domain task success;
- cross-domain task success;
- no-tool reasoning tasks;
- tool-available but tool-unnecessary tasks;
- long-context and multi-turn tasks;
- malformed and adversarial tool schemas;
- action diversity and collapse;
- calibration of abstention or no-call predictions;
- monitor gaming and shortcut acquisition; and
- base-versus-adapted hidden-state, router, expert, and cache drift where those
  measurements are admitted.

Preserved average task success is insufficient when individual domains regress.
Every material regression must remain visible.

## Observation-only monitoring boundary

Predicted next action may later be evaluated as passive telemetry, but it does not
become a correctness feature because it anticipates the agent's behavior.

Any hidden-state, router, expert, Jacobian, or semantic-workspace claim must show
sealed incremental objective-outcome value beyond:

- action-frequency priors;
- logits and tool-name probability;
- argument-token probability;
- parser confidence;
- trajectory length and position;
- current tool availability;
- task and domain identity;
- previous action pattern;
- direct self-speculation output;
- ordinary hidden-state and spectral baselines; and
- independent verifier features.

M39 and all current monitoring milestones remain observation-only. They may not
pre-execute tools, alter action selection, expose results early, stop reasoning,
retry, repair, or mutate external state.

## Systems and latency-accounting gate

Reported Hit@1 is not latency reduction.

End-to-end evaluation must report:

- speculation trigger frequency;
- branch-generation tokens and time;
- cache-copy or branch-management overhead;
- tool-call latency distribution;
- speculative hit and miss rates;
- calls issued, cancelled, completed, and discarded;
- duplicate external calls;
- provider billing and rate-limit cost;
- result-validation and canonicalization cost;
- rollback or confirmation cost;
- privacy and audit overhead;
- p50, p95, p99, and maximum task latency;
- throughput and concurrency effects;
- peak memory and KV-cache footprint; and
- independently verified task outcome.

Required controls include no speculation, oracle next-call speculation,
frequency/template prediction, smaller external speculator, same-model prompted
self-speculation, cache-only replay, random matched-call speculation, and a
fully synchronous baseline.

A method is not a systems win when branch and duplicate-call costs exceed hidden
latency. Benefits under slow read-only search do not transfer to low-latency local
tools, stateful APIs, code execution, or multi-user contention.

## Jacobian and causal-analysis consequences

A self-speculating adapted checkpoint is a new mathematical function.

Jacobians fitted on the base agent do not transfer to the adapted checkpoint.
Future derivative work must separately admit:

- agent mode and speculator mode;
- the exact speculation suffix;
- prefix and branch cache lineage;
- parser and schema identities;
- fixed versus changed tool registry;
- fixed-route and route-boundary strata for MoE variants;
- forward, VJP, JVP, and finite-difference parity; and
- objective-outcome evaluation beyond action agreement.

A derivative that predicts the later action does not establish that the action is
correct, safe, necessary, or already committed. A local derivative through a
fixed parser-free model path does not represent discrete parser, schema,
permission, transaction, or environment-state boundaries.

## Agents-A1 scaling consequence

The technically credible sequence is:

1. Complete Q35Q exact-target-runtime provenance, strict loading, packed-tensor
   consumption, expert ordering, deterministic forward, VJP, JVP, and
   finite-difference admission.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, tool template,
   parser, hybrid state, cache, harness, verifier, and runtime.
3. Establish deterministic, confidence, trajectory, hidden-state, spectral,
   memory, program-state, tool-parser, and verifier baselines.
4. Build an observation-only next-action prediction benchmark from nonsealed
   trajectories, with independently verified acceptable-action sets where
   feasible.
5. Separate prediction of the agent's realized action from prediction of an
   objectively acceptable action and final task success.
6. Test same-model prompting before any adaptation. Treat every suffix, schema,
   parser, and boundary as an immutable condition.
7. If adaptation is studied, admit the adapted Agents-A1-4B checkpoint separately
   and run matched-domain, cross-domain, no-tool, long-context, and regression
   suites.
8. Prohibit live speculative execution during monitor development. Use replay or
   sandboxed read-only tools with no external side effects.
9. Separately admit Agents-A1-35B's quantization, router, experts, hybrid state,
   cache, kernels, topology, batching, scheduler, parser, and tool harness.
10. Revalidate next-action telemetry under Agents-A1-native routes, shared
    experts, recurrent state, cache lineage, and long agent trajectories.
11. Require router and Jacobian features to add sealed objective-outcome value
    beyond direct self-speculation and the complete cheaper comparator stack.
12. Study real asynchronous tool execution only after a separate action-safety,
    transaction, privacy, and production-control preregistration passes.
13. Restrict any initial systems experiment to explicitly allowlisted,
    replayable, read-only tools with full synchronous fallback.
14. Preserve ordinary committed-action execution as the fail-safe path.

Self-speculating tool calls are a credible future systems comparator for
Agents-A1-4B. They are not evidence that Agents-A1-35B has a semantic workspace,
that MoE routes encode intent, or that a predicted call is safe to execute.

## Current blocker

The active blocker remains exact-target-runtime Q35Q admission:

1. Execute the composed Transformers provenance adapter in the exact target
   runtime.
2. Freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple.
3. Bind the actual GPTQModel/Defuser loader and complete executable source
   closure.
4. Run strict synthetic Qwen3.5-MoE loading.
5. Prove one-time packed-tensor consumption.
6. Prove exact expert and fusion ordering.
7. Prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity.
8. Pass the complete Phase-0 conjunction before weight staging or GPU
   authorization.

This evidence resolves none of those gates.

## Established by this correction

- Predicted, emitted, committed, pre-executed, and reused tool actions are
  separate binding identities.
- Agreement with a later agent action is not objective correctness.
- Cross-domain action agreement can improve while task success degrades.
- Retrospective next-call labels are unavailable at the earlier online boundary.
- Joint self-speculation training creates a new checkpoint and policy.
- Parser, schema, canonicalization, permission, environment snapshot, and result
  freshness are part of action identity.
- Discarding a speculative result is not equivalent to avoiding all side effects.
- Read-only classification must include billing, privacy, rate-limit, audit, and
  provider-state effects.
- Shared-prefix speculation creates separate cache and state lineages.
- Existing privacy, sealed-data, verifier, provenance, derivative, GPU,
  intervention, and production gates remain intact.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of arXiv `2607.25816v1`.
- Immutable admission of a public implementation, data recipe, checkpoints, and
  dependency closure.
- Safe speculative execution in any state-changing environment.
- Stable result reuse under changing permissions, schemas, or external state.
- Generalization beyond the reported 4B models and task families.
- Preservation of broad agent competence after dual-mode adaptation.
- Transfer to Qwen3.5-MoE, Qwen3.6, or Agents-A1.
- Objective correctness or failure-prediction value from self-speculation.
- Incremental router, expert, hidden-state, semantic-workspace, or Jacobian value
  beyond direct action prediction and cheaper controls.
- Complete Q35Q runtime and derivative admission.
- Safe early exit, retry, repair, speculative tool execution, external-state
  mutation, forced routing, activation steering, or production deployment.

The research program remains unfinished.
