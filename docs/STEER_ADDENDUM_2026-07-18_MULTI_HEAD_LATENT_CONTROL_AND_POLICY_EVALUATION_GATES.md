# Steering Addendum — Multi-Head Latent Control and Policy-Evaluation Gates

Date: 2026-07-18

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `1905891dcb73121c5bc795f42e0de524836944bc`

## Scope

This addendum applies to any future hidden-state, router-telemetry,
Jacobian-lens, semantic-workspace, capability, clarification, tool-use,
abstention, escalation, retry, early-exit, truncation, model-routing, or
Agents-A1 control claim.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload retrieval,
model execution, GPU execution, hidden-state capture, attention capture, router
capture, Jacobian fitting, sealed scientific evaluation, or production use is
authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, cleanup, commit-safety, comparator, nuisance-control,
production-gating, and stop rule remains binding.

GitHub currently reports this repository as public. This document contains only
aggregate public-source program-control information. It does not authorize
committing prompts, outputs, token IDs, verifier labels, per-task predictions,
hidden states, router traces, Jacobians, weights, caches, credentials, local
paths, or private logs.

## New external evidence and narrow interpretation

Ghasemabadi, Chen, Rashidi, and Niu, “Multi-Head Latent Control: A Unified
Interface for LLM Agent Decision Making,” arXiv `2607.14277v1`, introduce two
lightweight heads over hidden-state trajectories from frozen LLM and VLM
backbones:

- a Capability Head for retaining control or escalating to a stronger model;
- a Resolution Head for clarification, tool use, abstention, or direct answer.

The associated public implementation was inspected at immutable commit
`a5a1fffc44158d5808d5c8cae4f18c4df675bc09` in
`Amirhosein-gh98/Multi-Head-Latent-Control`.

The paper reports experiments on Qwen3-VL, Qwen3.5, and Gemma variants from 2B
to 32B, including Qwen3.5-4B/9B capability heads and prefix-trained variants.
It reports routed score-cost gains, intervention-decision gains on WHEN2CALL,
web-search escalation results on TriviaQA, and a long-horizon AndroidWorld case
study.

The binding interpretation is narrow:

1. A frozen-backbone hidden-state control head is now a mandatory future
   comparator for escalation and resolution-policy claims when a technically
   compatible implementation can be constructed.
2. The result does not establish universal model self-awareness, causal error
   localization, safe control, or transfer to Agents-A1.
3. Full-trajectory capability scoring is retrospective unless the complete
   hidden-state descriptor and head output are produced in the original
   generation pass before the decision.
4. A prefix-200 result is an early-control lead only for a policy operating at
   the absolute 200-token boundary with no future-token access, full-trajectory
   preprocessing, replay-only advantage, or post-hoc selection.
5. Capability, resolution, correctness, expert misrouting, and causal repair are
   separate claims. Success on one does not establish another.

## Backbone, mode, processor, and head identity binding

The public release explicitly couples each capability head to a matching
backbone and generation mode. Future use must freeze and verify, at minimum:

- exact backbone repository and immutable revision;
- model class, configuration class, hidden width, layer count, and selected
  hidden-state layer;
- tokenizer, processor, chat template, multimodal serialization, and special
  token identities;
- instruct versus thinking mode and all generation parameters;
- exact control-head artifact, configuration, source, digest, and training
  regime;
- full-trajectory versus prefix-trained identity;
- prefix length, pooling, projection, masking, padding, and sequence-selection
  rules;
- precision, device, distributed layout, and instrumentation path.

A head trained for one backbone, hidden width, layer, model revision, processor,
chat template, or thinking mode may not be silently reused on another. Any
cross-model or cross-mode transfer requires a separately frozen transfer
protocol, target-blind calibration, and sealed target evaluation. Target-test
retuning is prohibited.

## Label-provenance and verifier-disagreement gate

The paper constructs capability labels by comparing generated answers with
reference answers using Qwen3-VL-30B-A3B as a judge, and constructs resolution
labels with an external judge over WHEN2CALL examples. Those labels are useful
training signals, not automatically canonical ground truth.

Future reproduction or adaptation must:

- freeze the judge model, revision, processor, prompt, sampling parameters, and
  parsing rules;
- use deterministic judging where technically possible;
- retain the original benchmark verifier or executable task outcome as the
  primary label when available;
- report judge-versus-canonical disagreement by task family, answer format,
  modality, and outcome class;
- quarantine unverifiable, ambiguous, malformed, or judge-disputed examples;
- prevent judge outputs, benchmark labels, or downstream outcomes from entering
  monitor features;
- preserve verifier independence and sealed-label access controls;
- prohibit relabeling after observing sealed monitor performance.

A control head trained on judge-derived labels may be reported as predicting
that frozen judge only until agreement with the canonical outcome is
established.

## Full-trajectory versus online policy boundary

The public release distinguishes full-trajectory heads from prefix-200 heads.
The default full-trajectory system waits for the weaker model to finish before
applying the Capability Head. That design can support post-generation routing,
retry, or answer replacement, but it is not an early-exit result.

Future reports must separate:

1. post-generation retrospective scoring;
2. post-generation retry or replacement;
3. second-pass prefix replay;
4. single-pass streaming prefix scoring;
5. token-level early stopping;
6. step-level agent handoff;
7. episode-level model selection.

For every claimed decision boundary, record exactly which tokens and states
exist, which cache entries exist, whether generation is paused, whether an
additional backbone pass occurs, and whether the fallback receives the original
prompt, the partial trajectory, a summary, or the complete failed answer.

A fractional prefix defined using the eventual final response length remains
retrospective. An absolute 200-token boundary is admissible only if examples
shorter than 200 tokens, already-finished examples, malformed outputs, and
stop-token behavior are handled under frozen rules rather than excluded.

## End-to-end cost and quality accounting

The paper’s reported paid API cost treats the locally run primary model as free
and counts fallback-model API usage. That is a valid deployment-specific price
proxy, not complete compute cost.

Every future policy comparison must report:

- primary-model prompt and generation tokens before the decision;
- discarded or duplicated primary-model work after escalation;
- fallback input construction and all fallback tokens;
- hidden-state capture, projection, pooling, transfer, and head-execution cost;
- cache retention, replay, synchronization, batching, and serving regressions;
- wall-clock latency, time to first token, time to decision, and time to final
  accepted result;
- accelerator-seconds, peak device memory, host memory, interconnect traffic,
  storage, and energy where measurable;
- paid API cost under an explicit dated pricing model;
- score, calibration, coverage, selective risk, and failure severity.

Report at least these equal-budget baselines:

- always-primary;
- always-fallback;
- prompt-only router;
- calibrated confidence or entropy router;
- surface self-abstention;
- decision-point hidden-state probe;
- fixed-budget trajectory head;
- router/path telemetry head for MoE backbones;
- Jacobian-lens head only after derivative parity;
- random and prevalence-matched routing policies.

A policy is not cheaper because the auxiliary head is small. The complete
primary-plus-monitor-plus-fallback path must be cheaper under the frozen
workload and resource model.

## Capability-policy evaluation gate

A scalar adequacy score becomes a control policy only after a threshold,
fallback, and handoff representation are specified. Freeze those choices before
sealed evaluation.

Report:

- ROC-AUC, both-class AUPR, Brier score, calibration error, and reliability
  curves for the raw capability score;
- score-cost and risk-coverage curves over the full preregistered threshold
  range;
- the frozen deployment operating point and the rule used to choose it;
- false-retain and false-escalate rates by task family, modality, difficulty,
  answer type, trajectory length, and failure class;
- right-to-wrong and wrong-to-right changes caused by routing;
- fallback failure, correlated failure, and cases where the primary is correct
  but the fallback is wrong;
- out-of-distribution calibration and threshold stability;
- episode- and user-level clustering with confidence intervals.

Do not select a threshold on the sealed test, on AndroidWorld success, or on the
same trajectories used to report final policy utility.

## Resolution-policy evaluation gate

Clarification, tool use, abstention, and direct answering are not symmetric
classes and cannot be summarized only by aggregate F1 or accuracy.

Future Resolution Head evaluation must include:

- a complete mutually exclusive action ontology, including malformed or
  unavailable actions;
- per-action precision, recall, calibration, support, and confusion matrices;
- action-conditioned utility and cost;
- unnecessary-tool, missed-required-tool, invalid-tool, wrong-tool, and
  malformed-argument rates;
- unnecessary-clarification and missed-clarification rates;
- valid abstention, invalid refusal, and answerable-task abandonment rates;
- direct-answer errors that should have triggered another action;
- tool availability, permission, latency, timeout, and failure controls;
- cost-sensitive regret against the best frozen feasible action;
- comparison with the backbone’s native action, prompt-only classifiers, and
  simple metadata or confidence policies.

A changed action or improved class score is not evidence that the final task
outcome improved. Detection quality and policy utility must both pass.

## Answerability-versus-correctness factorization and dual-risk certification

Wagner, “Two Axes of LLM Abstention: Answer Correctness and Question
Answerability,” arXiv `2607.08456v1` dated 2026-07-09, evaluates five dense
instruction-tuned models from 2B to 14B. On the same questions it separates
correct-and-answerable, wrong-but-answerable, and unanswerable outcomes. The
reported geometry is crossed rather than a strict double dissociation: ordinary
answer confidence primarily separates successful from unsuccessful attempts,
while a prompt-boundary hidden-state readout primarily separates answerable from
unanswerable questions.

The strongest natural-data evidence is on CREPE false-presupposition questions.
The paper reports ordinary answer-confidence and trained output readouts near
chance for answerability, while hidden-state readouts remain moderately above
chance. It also reports a factorized acceptance policy with separately calibrated
correctness and answerability thresholds and separately certified wrong-answer
and unanswerable-answer risk budgets. The paper’s own controls show that
SelfAware contains substantial surface lexical signal, that natural-data
separability is materially lower, and that certificate issuance varies across
random resplits. These are dense-model question-answering results, not an
Agents-A1 or long-horizon agent result.

Future abstention, escalation, direct-answer, tool-use, or task-acceptance studies
must therefore treat at least these as separate endpoints:

1. **admissibility or answerability:** whether the task, request, premise, action,
   or proposed tool operation should be attempted under the available evidence,
   permissions, tools, environment state, and policy;
2. **execution correctness:** whether an admissible attempted answer or action is
   likely to succeed or be correct;
3. **resolution choice:** which permitted action should be taken when the first
   two endpoints are uncertain or fail.

A single scalar confidence, capability, workspace, route, or Jacobian score may
replace this factorization only after a preregistered sealed comparison shows
that it controls each endpoint’s risk separately without losing required
coverage. Aggregate abstention accuracy, pooled selective risk, or one combined
false-abort rate is insufficient.

For each study, freeze the outcome ontology and denominators before labels are
opened. At minimum distinguish correct-answerable, wrong-answerable,
unanswerable or inadmissible, malformed, permission-blocked, tool-unavailable,
insufficient-evidence, false-premise, recoverable, and terminal outcomes where
applicable. Do not relabel a wrong answer as unanswerable merely because the model
failed, and do not treat an answerable task as inadmissible merely because the
available model is weak.

The answerability and correctness heads, layers, token boundaries, features,
thresholds, calibration rules, and policy conjunction must be selected on
training and tuning data only. Use disjoint probe-training, threshold-tuning,
post-selection certification, and sealed-test partitions. A failed certificate
may not be used to retune on the certification split. Certification must follow
the existing cluster-aware and sequential-risk rules when tasks, templates,
episodes, users, or repeated rollouts are dependent.

Report separate risk budgets, confidence levels, empirical test risks, coverage,
and certificate-issuance rates for:

- answering or acting on inadmissible inputs;
- wrong execution on admissible inputs;
- unnecessary abstention, escalation, clarification, or tool use;
- abandonment of answerable or solvable tasks;
- right-to-wrong and wrong-to-right changes caused by the policy.

Prompt-only, bag-of-words or equivalent surface, task-family, template, modality,
tool-availability, permission, and environment-state baselines are mandatory.
Within-family and family-disjoint tests must determine whether an answerability
probe is reading semantic admissibility or merely task source, wording, format,
or benchmark construction. Surface-available signal remains a valid operational
comparator but cannot be represented as uniquely internal model awareness.

Decision timing remains explicit. A prompt-boundary answerability head may support
a pre-generation admissibility claim only from information available at that
boundary. A post-answer correctness score is retrospective. A step-level agent
head must not use later observations, tool results, verifier outcomes, or future
trajectory states. The conjunction of scores inherits the latest information
boundary used by any component and may claim savings only for work occurring
after that boundary.

For Agents-A1, add a cheap frozen admissibility or answerability head beside the
confidence and capability baselines before route telemetry or Jacobian-Lens
features. Evaluate it on both the separately admitted Agents-A1-4B dense sibling
and Agents-A1-35B MoE under matched tasks and separate calibration. Shared
answerability effects are general agent-family or task evidence; route-only
incremental effects remain MoE-specific and must pass the existing occupancy,
semantic, parent-route, topology, and equal-cost controls. This addition changes
the minimum future comparator decomposition but does not authorize model
execution, telemetry capture, abstention, escalation, tool suppression, routing,
or production control.

## Long-horizon and AndroidWorld leakage controls

For step-level or long-horizon evaluation:

- split by complete episode, environment state, application, task template, and
  user goal rather than individual steps;
- prohibit steps from the same episode or near-duplicate task from crossing
  train, validation, and sealed test partitions;
- freeze state serialization, screenshot handling, observation history,
  previous actions, tool outputs, and retry history;
- report per-episode and per-step metrics separately;
- model correlated errors and repeated decisions within an episode;
- include failure recovery, compounding error, loop, premature termination, and
  state-corruption outcomes;
- compare fresh fallback handoff with continuation from the partial trajectory;
- include the cost and risk of transferring potentially incorrect intermediate
  state to the fallback.

AndroidWorld or other agent success does not establish general correctness
monitoring. It is one policy evaluation under one environment and execution
stack.

## Detection-before-intervention boundary

The existing observation-before-intervention rule remains binding.

Before a control head may drive retry, abstention, tool use, clarification,
routing, truncation, or early exit, its underlying detection signal must pass a
sealed family-disjoint evaluation with nuisance controls and incremental value
over simpler baselines.

The subsequent policy experiment must be separately preregistered and must
report:

- the frozen signal and threshold;
- allowed actions and fallback identities;
- right-to-wrong and wrong-to-right transitions;
- selective risk and calibration;
- latency, memory, cost, privacy, and degeneration;
- policy failures under distribution shift;
- rollback and production-gating disposition.

No policy result authorizes activation steering, expert forcing, router updates,
or production deployment.

## Agents-A1 scaling consequence

A Multi-Head-Latent-Control-style hidden-state policy is now a required future
Agents-A1 comparator when technically compatible. It is a more direct and
cheaper hypothesis than Jacobian fitting and must be evaluated first at the same
decision boundaries.

The preferred Agents-A1-native sequence remains:

1. metadata and action-history baselines;
2. calibrated logits and confidence;
3. selected decision-boundary hidden-state projections;
4. a frozen prompt-boundary admissibility or answerability head;
5. a frozen fixed-budget capability or correctness head;
6. compact online route paths, margins, entropy, and cross-layer path summaries;
7. a frozen multi-action resolution head;
8. streaming trajectory summaries that require no replay;
9. Jacobian-lens features only after exact derivative parity and capture-cost
   validation;
10. policy evaluation only after detection passes;
11. full attention maps, attribution graphs, steering, or router intervention
    only under separate amendments.

For Agents-A1 or comparable large multimodal MoEs, additionally control model
parallelism, expert placement, dropped tokens, route capacity, modality, visual
token count, processor identity, tool schema, action space, context compaction,
checkpoint/restart behavior, and harness version.

No full raw trajectory retention is implied. Use online bounded summaries,
privacy audits, prompt-reconstruction attacks, membership-inference checks, and
sealed-data controls before capture.

## Program status after this addendum

Established:

- public hidden-state Capability and Resolution Head implementations exist for
  several frozen Qwen3.5, Qwen3-VL, and Gemma variants;
- full-trajectory capability routing is primarily post-generation in the
  released default design;
- separately trained prefix-200 heads provide a concrete early-routing lead;
- the paper reports useful routed-system and tool-decision results across
  several benchmarks and an AndroidWorld case study;
- each released head is coupled to a specific backbone and mode;
- hidden-state capability and multi-action policy heads are mandatory future
  comparators when technically compatible;
- correctness and answerability are distinct selective-decision endpoints in the
  reported dense-model question-answering experiments;
- a separately calibrated two-axis policy is a mandatory future abstention and
  task-acceptance comparator when technically compatible.

Unproven:

- exact independent reproduction of the reported results;
- canonical-label agreement for judge-derived training targets;
- leakage-free episode-disjoint AndroidWorld training and evaluation;
- low-overhead single-pass monitoring in the target serving stack;
- stable calibration under workload, model, mode, or harness drift;
- robust answerability separation after surface, family, modality, tool, and
  environment controls on agent trajectories;
- dual-risk certificate stability under clustered long-horizon episodes;
- transfer to Agents-A1 or another large multimodal MoE;
- incremental Jacobian-lens value over answerability, capability, correctness,
  and resolution heads;
- safe early exit, routing, tool use, clarification, abstention, retry, or
  production deployment.

The active engineering blocker remains production-path upstream/runtime
provenance composition as defined in `steer.md`. This addendum changes future
comparator, label, timing, cost, calibration, and policy-evaluation controls only
and does not authorize advancement past the current gate.