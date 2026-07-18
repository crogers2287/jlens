# Steering Addendum — Recall-Controlled Agent Abort and Sequential Certification Gates

Date: 2026-07-18

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `fde209c6110c01550dcdc55d62dd50015b9b3537`

## Scope

This addendum applies to any future claim involving hidden-state, router-telemetry,
Jacobian-lens, semantic-workspace, trajectory, confidence, or metadata signals
used to abort, truncate, retry, escalate, abstain from, or otherwise stop an LLM
agent episode before its ordinary terminal state.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload retrieval,
model execution, GPU execution, hidden-state capture, router capture, Jacobian
fitting, sealed scientific evaluation, or production use is authorized by this
document.

Every privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, cleanup, commit-safety, comparator, nuisance-control,
production-gating, and stop rule remains binding.

GitHub currently reports this repository as public. This document contains only
aggregate public-source program-control information. It does not authorize
committing prompts, outputs, token IDs, verifier labels, per-task predictions,
hidden states, router traces, Jacobians, weights, caches, credentials, local
paths, or private logs.

## New external evidence and narrow interpretation

Ruan et al., “Doomed from the Start: Early Abort of LLM Agent Episodes via a
Recall-Controlled Probe Cascade,” arXiv `2607.06503v2`, report that lightweight
per-round linear probes over one selected residual-stream hidden state can
predict eventual episode failure early in TextCraft, WebShop, and a limited
ALFWorld stress test.

The method places gates at the first six interaction rounds, searches a vector
of per-round success-survival budgets, and optionally certifies the frozen
cascade on an independent sample using a one-sided Clopper–Pearson lower bound
on episode-level success recall. The paper reports generated-token savings of
up to 60.2% on TextCraft and 54.9% on WebShop at a nominal 90% global success
recall target across Qwen-2.5-7B, Llama-3.2-3B, and Qwen3-1.7B.

The public paper states that code will be released; no attributable immutable
implementation was located during this review. Therefore the result is a
methodological and comparator lead, not an independently reproduced system.

The binding interpretation is narrow:

1. Per-round hidden-state probes are now a mandatory future comparator for
   Agents-A1 episode-failure prediction when technically compatible.
2. Sequential abort policies must control the cumulative episode-level harm of
   all gates. Per-gate recall, AUC, or false-abort rates are insufficient.
3. The reported evidence is model-, environment-, layer-, harness-, and
   distribution-specific. It does not establish Agents-A1 transfer.
4. The reported efficiency measure is generated-token savings. Wall-clock,
   accelerator, memory, storage, and dollar-cost savings remain unestablished.
5. The result does not establish Jacobian-lens superiority, causal expert
   localization, safe retries, or production utility.

## Decision-boundary and feature-timing gate

The reported probe reads the selected-layer residual-stream state at the final
token of the agent action generated in round `r`. That is a post-action,
pre-next-round decision boundary.

Future work must distinguish at least:

1. pre-action prediction before any action token is emitted;
2. intra-action token-level prediction;
3. post-action prediction before the action is executed;
4. post-execution prediction after environment feedback;
5. post-round prediction before another model call;
6. retrospective replay after the full episode is known.

A feature captured after an external action executes cannot be credited with
preventing that action. For tool use, file mutation, network access, purchases,
messages, code execution, or other irreversible effects, the monitor must prove
that its decision occurs before the protected action boundary.

For every gate, freeze and report:

- exact round and token boundary;
- whether action text has been generated;
- whether the action has been parsed, validated, or executed;
- whether environment feedback is available;
- hidden-state layer and token-selection rule;
- cache state and any synchronization point;
- whether an additional forward or replay occurs;
- permitted policy action at that boundary.

Do not relabel a post-action or post-execution cascade as token-level early exit.

## Episode-level sequential-risk gate

A successful episode must survive every active gate. False-abort risk therefore
accumulates over the gate sequence and depends on which successful episodes
remain alive at each round.

Any future multi-gate policy must preregister and report:

- the complete gate schedule;
- the risk set at every gate;
- per-gate successful-episode survival conditional on reaching that gate;
- global successful-episode survival through all gates;
- the joint pattern of false aborts across gates;
- the number and fraction of successful episodes exposed to each gate;
- early natural termination and censoring rules;
- the exact global recall or risk target;
- the confidence level and finite-sample procedure;
- the no-op disposition when the target cannot be certified.

Per-gate guarantees may not be multiplied, averaged, or otherwise treated as a
global guarantee unless the required dependence assumptions are proven. The
primary safety quantity for abort is the fraction of counterfactual successful
episodes that the complete frozen policy allows to finish.

## Certification-unit and dependence gate

An exact binomial certificate requires a defensible sampling unit and exchangeability
or independence conditions for that unit. Multiple rollouts from the same task,
template, environment state, user goal, seed family, or benchmark item can be
correlated even when task groups do not cross train and test partitions.

Before describing a recall bound as exact or distribution-free, future work
must:

- identify the certification sampling unit;
- state the target deployment population;
- prevent the same task or near-duplicate task from contributing to selection
  and certification;
- quantify repeated-rollout and within-task dependence;
- certify at the independent task or cluster level when episode independence is
  not justified;
- use cluster-aware, hierarchical, or worst-case bounds when appropriate;
- report both episode-weighted and task-weighted success recall;
- report confidence intervals under the declared dependence model;
- preserve all failed resets, malformed episodes, and unavailable actions under
  frozen inclusion rules.

Counting correlated successful rollouts as independent certification successes
is prohibited unless independence is established. A task-grouped split alone
does not prove episode-level binomial independence.

## Selection, calibration, certification, and sealed-test separation

The following objects are adaptive and must be frozen before certification:

- backbone, revision, processor, tokenizer, chat template, and harness;
- generation mode and sampling parameters;
- hidden-state layer and token-selection rule;
- feature standardization and projection;
- probe family, regularization, and training seed rules;
- number and location of gates;
- threshold-calibration method;
- per-round budget grid or optimizer;
- validation feasibility margin;
- global recall target;
- cost function and savings accounting;
- abort, abstain, retry, and fallback actions.

Use separate data roles:

1. training or cross-fitting;
2. layer and feature selection;
3. threshold calibration;
4. cascade or budget search;
5. independent post-selection certification;
6. sealed scientific evaluation.

Certification data may be opened once for the frozen policy and may not be used
to alter the layer, probe, gates, thresholds, budgets, margin, feature set, or
cost model. A failed certificate produces a no-abort disposition for that
frozen candidate; it does not authorize retuning on the certification sample.

The sealed scientific test remains separate from the certification set when the
same result is used to claim predictive generalization or comparative
superiority.

## Outcome and recoverability gate

Binary terminal success recall protects only one outcome axis. Agents-A1 tasks
can contain partial success, recoverable mistakes, catastrophic actions,
verifier failures, malformed outputs, tool faults, timeouts, and policy-induced
retries.

Future abort studies must maintain a frozen outcome ontology including:

- ordinary success;
- ordinary failure;
- partial or graded success;
- recoverable failure;
- irrecoverable environment corruption;
- unsafe or unauthorized action;
- malformed action or output;
- tool or infrastructure failure;
- timeout or resource exhaustion;
- verifier or benchmark-label failure;
- valid abstention;
- false abort of a counterfactual success.

Report outcome severity and counterfactual policy effects, not only binary
recall. A cascade that preserves nominal success recall can still be harmful if
it preferentially aborts high-value, rare, long-horizon, or recoverable
successes.

Retries, fallback models, and alternative actions are separate policies. Saved
compute may not be assumed to improve reward when reallocated. Any retry or
escalation experiment must report right-to-wrong and wrong-to-right transitions,
correlated failures, duplicated work, and complete end-to-end cost.

## Online-equivalence and systems-cost gate

The paper’s offline feature path uses teacher-forced replay over logged
trajectories. The proposed online path uses selected-layer hidden-state
instrumentation during inference. Those are not automatically equivalent.

Before using an offline probe as an online controller, prove:

- exact tokenization, prompt construction, action serialization, and cache
  equivalence;
- hidden-state equality or a preregistered numerical tolerance at the selected
  decision boundary;
- no future-token, terminal-outcome, or replay-only leakage;
- deterministic feature extraction under the admitted serving stack;
- bounded overhead for hidden-state retention, transfer, projection, and probe
  execution;
- effects on chunked prefill, paged KV cache, batching, speculative decoding,
  expert parallelism, and distributed scheduling;
- no prohibited persistence or reconstruction of sensitive trajectories.

Efficiency claims must include:

- original generation and tool-execution cost;
- monitoring and synchronization overhead;
- naturally terminated episodes that never reach later gates;
- discarded work before abort;
- fallback or retry cost;
- wall-clock latency and time to decision;
- accelerator-seconds, device memory, host memory, interconnect, and storage;
- amortized data collection, replay, fitting, calibration, and certification
  cost;
- break-even deployment volume.

Generated-token savings alone may be reported only as generated-token savings.

## Distribution-shift and recertification gate

A recall certificate is attached to the frozen policy and the sampled deployment
distribution. It does not transfer automatically across:

- model family, revision, precision, or quantization;
- hidden-state layer or representation path;
- environment or task family;
- tool schema or permissions;
- prompt and observation format;
- modality and processor;
- harness, cache, batching, or serving backend;
- generation mode or sampling parameters;
- episode horizon or gate schedule;
- base success rate or failure taxonomy.

Any material change invalidates the prior operational certificate unless a
predeclared invariance test passes. Refreshing the probe, threshold, layer, or
budget requires a new independent certification sample. Continuous drift
monitoring must not consume sealed labels or silently retune the deployed
policy.

Report family-disjoint, environment-disjoint, and temporal-shift results before
claiming general agent-failure awareness.

## Comparator and Agents-A1 scaling consequence

For future Agents-A1 work, a recall-controlled per-round hidden-state cascade is
a required comparator after the repository reaches the scientific execution
phase. It is a substantially cheaper hypothesis than Jacobian fitting and must
be tested first at the same decision boundaries.

The preferred Agents-A1-native sequence is:

1. action, tool, finish-reason, latency, and trajectory-length metadata;
2. calibrated logits, entropy, and action-token confidence;
3. one frozen selected-layer final-action-token hidden-state probe per gate;
4. a globally recall-controlled hidden-state abort cascade;
5. compact online route paths, margins, entropy, expert persistence, and
   cross-layer path summaries under the identical cascade;
6. combined hidden-state and router probes only after each standalone signal is
   measured;
7. Jacobian-lens features only after exact derivative parity and capture-cost
   validation;
8. policy evaluation only after sealed detection and sequential-risk control
   pass;
9. retries, fallback routing, expert forcing, activation steering, or production
   deployment only under separate amendments.

Every Jacobian-lens or router-telemetry claim must show sealed incremental value
over the frozen hidden-state cascade at equal gate locations, equal calibration
and certification machinery, and complete end-to-end cost.

For Agents-A1 or comparable large multimodal MoEs, additionally stratify or
control task family, modality, visual-token count, tool count, horizon, base
success rate, model parallelism, expert placement, capacity and dropped-token
behavior, context compaction, checkpoint/restart state, and harness version.

## Current program status after this addendum

Established:

- arXiv `2607.06503v2` provides primary-source evidence that simple per-round
  hidden-state probes can predict eventual agent-episode failure in several
  small dense-model and text-environment settings;
- distributing recall budgets over sequential gates can outperform a selected
  single-gate baseline in reported generated-token savings;
- episode-level success recall is the relevant cumulative harm quantity for a
  multi-gate abort cascade;
- independent post-selection certification is a technically credible control
  pattern when its sampling assumptions and data independence hold;
- the reported offline feature path uses teacher-forced replay and the paper
  does not report realized wall-clock or dollar-cost savings;
- a recall-controlled hidden-state cascade is now a mandatory future Agents-A1
  comparator when technically compatible.

Unproven:

- independent reproduction of the paper;
- availability or identity of the promised code release;
- exact online equivalence between replayed and serving-time hidden states;
- exact finite-sample certification under repeated-rollout or task-cluster
  dependence;
- category-, environment-, model-, modality-, or temporal-shift robustness;
- low-overhead deployment on a large multimodal MoE;
- transfer to Agents-A1;
- incremental router or Jacobian-lens value over the simple hidden-state
  cascade;
- safe abort, retry, escalation, truncation, expert intervention, activation
  steering, or production utility.

The active Q35Q milestone remains production-path upstream/runtime provenance
composition. This addendum does not authorize any later phase.