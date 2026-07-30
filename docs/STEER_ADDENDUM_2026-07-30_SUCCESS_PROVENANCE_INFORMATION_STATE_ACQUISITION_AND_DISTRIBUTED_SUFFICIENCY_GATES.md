# Steering Addendum — Success Provenance, Information-State Acquisition, and Distributed-Sufficiency Gates

Date: 2026-07-30

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `02d4a5140b12d5f7c64a86db32cf6ae391c0eff1`

## Scope and inherited restrictions

This addendum applies to every future agent benchmark, hidden-state outcome
monitor, router-telemetry readout, Jacobian-Lens readout, semantic-workspace
claim, correctness or error probe, early-exit or truncation predictor, retry or
repair predictor, retrieval or tool-acquisition policy, memory study, subagent
study, and Agents-A1 evaluation.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No model-weight staging, tensor-payload
retrieval, model execution, GPU execution, hidden-state capture, router capture,
cache capture, JVP, VJP, Jacobian fitting, sealed scientific evaluation,
intervention, or production use is authorized by this document.

Every existing privacy, sealed-data, canonical-verifier, provenance, exact-set,
exact-gradient, parity, nuisance-control, multiplicity, resource-accounting,
cleanup, commit-safety, intervention, and production gate remains binding.

GitHub reports this repository as public. Only aggregate public-source program
control is recorded here. Prompts, completions, benchmark items, target values,
retrieved passages, tool arguments or results, memory contents, subagent
messages, per-example condition assignments, per-example scores, verifier
labels, token IDs, hidden states, router arrays, expert paths, KV caches,
Jacobians, gradients, model weights, credentials, host paths, private runtime
facts, and sealed outcomes remain prohibited from this repository.

## New primary evidence

Luo and Peng, “Success Is Not Self-Explanatory: Auditing Success Provenance in
Agent Evaluation,” arXiv `2607.24054v1`, submitted 2026-07-27, identifies a
missing evaluation object once an agent can change its information state during
an evaluation: whether success was supported by the benchmark-authorized
information state or depended on acquiring a target-sufficient value during the
run.

The paper introduces matched interventions within the same task identity,
model, target, action channel, and scorer:

- `CLEAN`: benchmark-authorized information only;
- `GOLD`: the correct target value is made available through the tested surface;
- `SHAM`: the same source structure and exposure opportunity are retained while
  a matched incorrect target value is supplied.

The paper defines `GOLD - CLEAN` as the total score response to correct-target
availability and `GOLD - SHAM` as the part that tracks target correctness beyond
generic source exposure. It reports `GOLD - SHAM` effects of 19.1 to 25.9
percentage points in the direct single-source setting. Under a distributed
two-source sufficiency condition, it reports retained `GOLD - SHAM` effects of
11.8 and 14.6 percentage points while a single-source colocation probe fails in
the intended direction, with AUROC 0.376 and 0.142. The paper also reports a
supported 5.0-point `CLEAN` model gap compressing to a raw `GOLD` difference of
-0.6 points without establishing a rank inversion.

Primary source:

- https://arxiv.org/abs/2607.24054v1

No attributable immutable public implementation revision was identified during
this review. The evidence is therefore paper-level only and is not an admitted
reproduction artifact.

## Binding interpretation

The new evidence supports only the following bounded claims:

1. Final correctness alone does not identify why an agent succeeded after the
   agent has been allowed to retrieve, call tools, consult memory, delegate, or
   otherwise alter its information state.
2. Detecting that a source was exposed is different from showing that the
   correct target carried by that source caused the score change.
3. `CLEAN`, `GOLD`, and `SHAM` answer different questions and may not be pooled
   into one undifferentiated benchmark score.
4. A detector scoped to one source can fail while the agent remains behaviorally
   dependent on target information distributed across multiple sources.
5. Model rankings can change numerically across information states; a ranking
   inversion is not established unless the paired contrast and its uncertainty
   support that claim.
6. These results do not establish natural benchmark contamination prevalence,
   dishonest behavior, malicious acquisition, model-native introspection, a
   semantic workspace, causal use of a hidden-state feature, or a safe control
   direction.
7. The results do not establish transfer to Qwen3.5, Qwen3.6, Agents-A1,
   architectural MoEs, long-horizon tool environments, or production systems.

## Required success-provenance identity

Every future compatible study must bind the following objects separately:

1. **Task identity:** exact source item, task revision, prompt template, target,
   parser, scorer, verifier, and environment snapshot.
2. **Authorized information state:** all information permitted at the monitoring
   boundary, including system context, user context, files, retrieval corpus,
   memory, tools, subagents, caches, and prior-turn state.
3. **Acquisition surface:** the exact retrieval, tool, memory, subagent,
   workspace, environment, or communication path through which new information
   can enter.
4. **Acquired payload identity:** source, revision, timestamp, provenance,
   freshness, permissions, position, serialization, and whether it contains,
   implies, or composes into target-sufficient information.
5. **Exposure event:** whether the payload was reachable, retrieved, returned,
   parsed, stored, injected, attended to, or consumed at the executed boundary.
6. **Target-sufficiency relation:** whether the acquired information alone or in
   combination with other information is sufficient to determine the scored
   target under the frozen verifier.
7. **Agent dependence:** whether changing the target-bearing content while
   preserving source exposure changes the agent’s action or outcome.
8. **Supported success:** success under the prospectively authorized information
   state without target-sufficient acquisition beyond the allowed benchmark
   contract.
9. **Acquisition-supported success:** success whose probability changes because
   correct target-sufficient information was made available during evaluation.
10. **Objective outcome:** independently verified task result, kept separate from
    source exposure, target sufficiency, detector output, and model self-report.
11. **Monitor output:** the exact exposure, dependence, correctness, utility, or
    policy target predicted by any transparent or internal-state monitor.
12. **Complete cost and risk:** tokens, latency, money, permissions, private-data
    reachability, provider exposure, attack surface, side effects, and verifier
    burden introduced by acquisition.

A benchmark artifact identity is incomplete without its authorized information
state and acquisition surfaces. A run under a different corpus, memory state,
tool catalog, permission set, subagent graph, cache, or environment snapshot is
a different scientific condition.

## Matched information-state intervention gate

Whenever an agent can acquire information that may contain or compose into the
scored target, the evaluation must include a prospectively frozen matched audit
using `CLEAN`, `GOLD`, `SHAM`, or a formally equivalent construction.

The matched unit must hold fixed, as technically compatible:

- source-item or qid identity;
- reference target and verifier;
- model checkpoint, tokenizer, templates, parser, and decoding policy;
- runtime, tool harness, memory policy, subagent topology, and environment;
- action channel and scorer;
- acquisition surface and source presentation structure;
- exposure opportunity, payload length, format, timing, and position;
- compute, retry, context, and tool-call budgets;
- all non-target content and downstream execution policy.

The conditions must be defined as follows:

1. **CLEAN:** only the prospectively authorized benchmark information is
   available. The condition may include ordinary retrieval or tools only when
   their admissible corpus and target-exclusion contract are frozen in advance.
2. **GOLD:** the correct target or a target-sufficient payload is made available
   through the tested acquisition surface.
3. **SHAM:** the acquisition surface, source structure, exposure opportunity,
   carrier, and non-target content are matched while the target-bearing value is
   replaced by a plausible incorrect value that does not accidentally encode the
   correct target.

Required reporting includes:

- `GOLD - CLEAN` with source-group-clustered uncertainty;
- `GOLD - SHAM` with source-group-clustered uncertainty;
- `SHAM - CLEAN` as the effect of generic source exposure and incorrect target
  content;
- condition-specific task success, parser validity, action validity, tool use,
  retries, and verifier outcomes;
- per-surface and pooled effects, with a prospectively declared pooling rule;
- heterogeneity by task family, source type, horizon, model, and acquisition
  topology;
- missingness, invalid outputs, timeouts, and blocked acquisitions as failures or
  separately frozen outcomes rather than silently removed rows;
- all inspected conditions, contrasts, subgroup analyses, and multiplicity
  corrections.

`SHAM` is not a no-information baseline. `GOLD - CLEAN` does not isolate
correct-target dependence when generic exposure changes behavior. `GOLD - SHAM`
does not estimate the natural frequency of target acquisition. Neither contrast
alone establishes malicious intent, policy violation, or benchmark leakage.

All matched conditions for one source item must remain in the same train,
calibration, validation, or sealed partition. Threshold, layer, feature, source,
surface, and contrast selection must occur without sealed condition outcomes.

## Target construction and sham-validity gate

A sham payload must preserve the tested source mechanism without creating a
second easier detection task.

Future studies must freeze and validate:

- target-value substitution procedure;
- plausibility and formatting of the sham value;
- lexical, numerical, structural, and semantic distance from the gold value;
- whether either value appears elsewhere in the prompt, corpus, memory, tool
  output, cache, or environment;
- whether source metadata, timestamps, ordering, length, confidence labels, or
  parser behavior reveal the condition;
- whether the sham value accidentally supports another accepted answer;
- whether the verifier has multiple acceptable targets;
- whether the task can be solved without the tested payload;
- whether model behavior reflects condition classification rather than target
  use.

Required controls include condition-label prediction, source-only prediction,
payload-format prediction, target-free carrier controls, answer-option and
presentation-order permutations, and a no-acquisition execution path.

A monitor that identifies `GOLD` formatting or source metadata without predicting
objective supported success has not passed this gate.

## Distributed-sufficiency and observation-unit gate

Target-sufficient information may be distributed across retrieval passages,
separate tool results, memory entries, subagent messages, turns, caches, files,
or environment observations. No individual source need contain the full target.

Future studies must therefore define the maximum admissible composition unit and
must test, where technically compatible:

- direct single-source sufficiency;
- two-source and multi-source compositional sufficiency;
- retrieval plus tool output;
- memory plus current observation;
- subagent message plus local context;
- cross-turn or cross-episode accumulation;
- stale, replayed, swapped, and partially missing components;
- source-order, timing, and position permutations;
- same-total-information but differently partitioned controls;
- independently useful components versus components useful only jointly;
- a matched condition in which source exposure remains but target composition is
  broken.

A source-local detector may only support source-local conclusions. Failure to
detect a target in one passage, one message, one tool result, one cache row, one
expert route, or one token window does not establish absence from the complete
information state.

The monitor observation unit must be at least as broad as the acquisition and
composition path named in the claim. When that is infeasible, the claim must be
restricted to the observed unit rather than generalized to whole-agent success
provenance.

## Outcome evidence, exposure detection, and dependence gate

The following are separate endpoints and must be reported separately:

1. final task success;
2. presence of outcome evidence after the run;
3. source reachability;
4. source exposure;
5. payload retrieval or return;
6. receiver consumption;
7. target sufficiency;
8. dependence on correct target content;
9. policy acceptability of the acquisition;
10. supported success under the authorized information state;
11. privacy, permission, or side-effect violations;
12. safe deployment admission.

A correct final artifact does not identify the acquisition path. An audit log
showing that a source was accessed does not establish target dependence. A
hidden-state or router signal that predicts source exposure does not establish
objective correctness. A successful `GOLD - SHAM` audit does not establish that
natural `CLEAN` successes used the same mechanism.

## Model comparison and ranking gate

Model comparisons must be information-state conditional.

Future reports must provide, for every compared model:

- `CLEAN`, `GOLD`, and `SHAM` scores under identical matched units;
- paired model differences within each condition;
- paired differences in `GOLD - CLEAN` and `GOLD - SHAM`;
- uncertainty clustered by source item;
- condition-by-model interaction tests;
- acquisition frequency, exposure, tool use, retries, and complete cost;
- parser, verifier, and invalid-output rates;
- supported-success ranking under `CLEAN` separately from acquisition-supported
  performance.

A raw score difference across unequal information states is inadmissible. A
numerical crossing is not a ranking inversion unless the prospectively declared
paired contrast and uncertainty support it. A model that is better at exploiting
provided target values is not thereby better at benchmark-authorized reasoning.

## Monitor, router, hidden-state, and Jacobian boundary

Success-provenance labels create transparent baselines that every internal-state
claim must beat.

Future compatible monitor studies must include, where available:

- source-reachability and source-access indicators;
- retrieval overlap and target-string or target-semantic overlap;
- tool, memory, subagent, cache, and environment-access metadata;
- exposure position, time, length, confidence, and source-identity features;
- parser validity, logits, entropy, margin, verbalized confidence, and trajectory
  features;
- deterministic target-sufficiency and provenance checks;
- external verifier and policy-check features;
- condition-identity prediction as a nuisance-control task.

Router, expert, hidden-state, semantic-workspace, or Jacobian features must show
prospective sealed incremental value for the exact frozen target after these
comparators. At minimum, distinguish:

1. prediction of `CLEAN`, `GOLD`, or `SHAM` condition;
2. prediction of source exposure;
3. prediction of target sufficiency;
4. prediction of dependence on correct target content;
5. prediction of objective task success;
6. prediction of supported success under `CLEAN`;
7. prediction of marginal utility from additional acquisition;
8. prediction of policy or privacy violation.

A feature that primarily identifies target exposure, retrieval overlap, source
identity, later verifier evidence, or tool usage cannot be relabeled as generic
`correctness awareness`, `metacognition`, `semantic workspace`, or `reasoning
quality`.

A Jacobian-Lens analysis must separately bind the differentiated map, activation
source, output token or objective, route condition, cache state, information
condition, and acquisition boundary. Large sensitivity to target-bearing content
does not establish supported success, causal necessity, or a safe intervention.

## Intervention and production boundary

This addendum authorizes no intervention.

Using success-provenance predictions to suppress retrieval, remove tools, erase
memory, terminate reasoning, select a subagent, alter routing, drop experts,
rewrite caches, retry, repair, or steer activations creates a new policy and a new
information state. It requires separate prospective admission, exact-compute and
counterfactual-utility controls, safety and privacy evaluation, rollback, and the
admitted full-information or full-compute fallback.

A policy that reduces target acquisition may also remove legitimate evidence and
lower objective success. A policy that increases acquisition may increase
privacy exposure, provider logging, attack surface, cost, and side effects. Those
tradeoffs must be measured rather than inferred from a provenance detector.

## Agents-A1 scaling consequence

The technically credible path is now:

1. Complete Q35Q production-path provenance, strict quantized loading,
   tensor-consumption, ordering, forward, VJP, JVP, and finite-difference
   admission.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, templates, parser,
   hybrid state, cache, tool harness, memory policy, subagent topology,
   environment, verifier, and runtime.
3. Freeze the benchmark-authorized information state and every acquisition
   surface before fitting a monitor.
4. Build a nonsealed source-group-disjoint `CLEAN`/`GOLD`/`SHAM` audit across
   retrieval, tools, memory, subagents, files, and environment observations.
5. Establish supported-success, source-exposure, target-sufficiency, and
   acquisition-dependence labels as separate targets.
6. Test direct, two-source, and multi-source sufficiency and ensure the monitor
   observation unit matches the claimed acquisition path.
7. Establish transparent provenance, text, logit, confidence, trajectory,
   parser, memory, tool, subagent, and verifier baselines before internal-state
   fitting.
8. Fit passive observation-only hidden-state monitors on Agents-A1-4B before any
   acquisition, early-exit, retry, repair, routing, or steering intervention.
9. Separately admit Agents-A1-35B quantization, router, shared and routed experts,
   hybrid attention, recurrent state, cache, kernels, topology, scheduler,
   telemetry path, tool harness, memory, subagents, and verifier.
10. Repeat the complete information-state audit under native 35B routing and
    serving conditions.
11. Require router and expert telemetry to add sealed target-specific value
    beyond the full transparent success-provenance comparator stack.
12. Add Jacobian features only after exact derivative parity and require separate
    incremental value for supported success, target dependence, and marginal
    acquisition utility.
13. Keep initial studies replayable, observation-only, production-disconnected,
    and free of irreversible external actions.
14. Preserve the admitted `CLEAN` full-compute path and the prospectively safe
    acquisition policy as fallback.

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

The new evidence resolves none of these gates.

## Established

- Outcome success and success provenance are separate evaluation objects.
- Authorized information state is part of benchmark identity.
- Source exposure and dependence on correct target content are separate claims.
- `GOLD - CLEAN` and `GOLD - SHAM` estimate different contrasts.
- A single-source detector can miss distributed target sufficiency.
- Supported success and acquisition-supported success must be reported
  separately.
- Model rankings are information-state conditional.
- Router, expert, hidden-state, semantic-workspace, and Jacobian features must be
  tested against transparent provenance controls.
- No privacy, sealed-data, verifier, provenance, derivative, GPU, intervention,
  or production gate is weakened.
- Q35Q remains blocked.

## Unproven

- Independent reproduction of arXiv `2607.24054v1`.
- Immutable admission of its implementation, datasets, condition assignments,
  model revisions, result artifacts, dependencies, and runtime closure.
- Natural prevalence of target acquisition in existing agent benchmarks.
- Generality across domains, languages, models, horizons, acquisition surfaces,
  and serving systems.
- Whether any particular Agents-A1 success is supported or acquisition-supported.
- A semantic workspace, generic correctness variable, metacognitive state, or
  model-native provenance representation.
- Objective success-provenance value from router, expert, hidden-state, or
  Jacobian features beyond transparent controls.
- Transfer to Agents-A1-4B, Agents-A1-35B, Qwen3.5, Qwen3.6, or comparable MoEs.
- Complete Q35Q runtime and derivative admission.
- Safe early exit, truncation, retrieval suppression, tool removal, memory
  editing, retry, repair, routing intervention, steering, external action, or
  production deployment.

The research program remains unfinished.
