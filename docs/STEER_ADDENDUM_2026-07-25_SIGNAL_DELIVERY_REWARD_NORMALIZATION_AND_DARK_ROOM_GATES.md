# STEER ADDENDUM — signal-delivery, reward-normalization, and dark-room gates

Date: 2026-07-25
Parent remote head: `aa156f4f4054880d5db48cac43bb95046377a5fc`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no weight retrieval, model execution, GPU use, hidden-state or
router capture, Jacobian fitting, sealed evaluation, training run, policy
update, control action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains complete production-path
upstream/runtime provenance composition. This addendum changes a future
scientific claim boundary and intervention-admission requirement; it does not
displace that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control
and public-source engineering material may be committed. Prompts, outputs,
token data, per-example outcomes, hidden states, router traces, Jacobians,
verifier records, model weights, optimizer state, training batches, reward
traces, caches, credentials, host paths, and private environment details remain
prohibited.

## Triggering primary evidence

Wang, `The Dark Room in the Reward Channel: Dense Prediction Rewards Collapse
GRPO-Trained LLM Agents -- and What Actually Works`, arXiv `2607.21273v1`,
submitted 2026-07-23, studies dense next-observation-prediction shaping in GRPO
agents on ALFWorld using Qwen3-1.7B, Qwen3-4B, and Qwen3-8B.

The author reports:

- potential-based dense prediction reward drove the reported GRPO runs toward
  prediction accuracy near one while task success fell to zero and episode
  length remained at the horizon;
- removing only standard-deviation normalization changed the reported outcome
  from collapse to baseline parity;
- in all-fail groups, z-scored advantages can become invariant to the nominal
  shaping coefficient, so a bounded raw shaping term does not imply bounded
  update pressure;
- an identical signal delivered through an auxiliary-loss channel improved the
  reported task result by roughly twenty percentage points while reward-channel
  delivery was neutral or harmful; and
- a shuffled-gold auxiliary-loss placebo matched the true-gold arm in the
  reported endpoint, so semantic label correctness was not established as the
  active ingredient.

The endpoints are single-seed. Seed replication and group-size controls were
reported as preregistered and incomplete. No immutable attributable public code
repository sufficient to reproduce the complete result was located during this
steering run. The source is therefore preliminary primary methodological
evidence, not an independently reproduced result in this repository.

## Bounded interpretation

The source does not establish:

- universal GRPO failure;
- collapse under every dense reward, normalizer, group size, model, task, or
  implementation;
- semantic usefulness or uselessness of next-observation prediction;
- causal sufficiency of the proposed variance-profile explanation outside the
  reported setting;
- replication across seeds;
- long-horizon coding, research, multimodal, or production-agent transfer;
- transfer to Qwen3.5, Qwen3.6, Agents-A1-4B, or Agents-A1-35B;
- hidden-state, router, workspace, sparse-feature, transcoder, directional-JVP,
  or Jacobian correctness signals;
- safe training from an internal monitor; or
- safe online control or production utility.

The material protocol consequence is narrower:

> Signal content, signal delivery channel, optimizer transformation, and
> resulting policy update are separate scientific and production objects.

A signal that is benign or useful as an auxiliary prediction target can be
catastrophic when injected into normalized policy advantages. Conversely,
performance from an auxiliary objective does not establish that its labels are
semantically informative when a shuffled-label placebo performs similarly.

## Binding endpoint and artifact separation

Every future compatible training or intervention study must freeze and report
at least the following as distinct objects:

1. **Source signal:** the raw scalar, vector, label, score, residual, prediction,
   verifier result, hidden-state feature, router feature, workspace feature,
   sparse feature, directional derivative, or Jacobian-derived quantity.
2. **Semantic target:** the event or property the source signal is claimed to
   represent.
3. **Delivery channel:** reward, advantage shaping, auxiliary loss, supervised
   target, prompt/context injection, replay priority, sampling weight, route
   policy, activation intervention, sidecar decision, or another mechanism.
4. **Transformation:** clipping, centering, standardization, whitening,
   normalization, ranking, temperature, discounting, bootstrapping, aggregation,
   or calibration applied before consumption.
5. **Reference population:** the group, batch, trajectory, task cluster, replay
   buffer, or running statistics used by the transformation.
6. **Optimizer and update rule:** objective, coefficients, optimizer, learning
   rate, gradient accumulation, clipping, KL term, entropy term, value loss,
   update epochs, and stopping rule.
7. **Adapted artifact:** the exact model, policy, router, monitor, sidecar, skill,
   or controller produced by the update.
8. **Objective outcome:** the independent task, safety, artifact, or environment
   result.
9. **Policy utility:** objective benefit and harm under the complete frozen
   execution and intervention policy.

A positive result in one delivery channel may not be represented as evidence
that another delivery channel is safe or effective. The same source signal in a
new channel creates a new intervention condition and, when parameters or policy
state change, a new adapted artifact.

## Reward-normalization and group-construction gate

Any reward-, return-, or advantage-based use of a dense monitor or prediction
signal must prospectively freeze:

- exact raw task reward and shaping equations;
- reward timing, potential function, discount, horizon, and terminal handling;
- reward coefficient and complete coefficient schedule;
- advantage estimator and baseline;
- centering and variance normalization rules;
- epsilon, clipping, and zero-variance handling;
- group construction, group size, sampling policy, and task composition;
- treatment of all-success, mixed, all-fail, aborted, timed-out, and undefined
  groups;
- cross-device and distributed-statistics behavior;
- optimizer, KL controller, entropy term, gradient clipping, update count, and
  effective batch size;
- implementation identity, runtime, precision, seeds, and determinism controls;
  and
- every fallback used when statistics are degenerate or missing.

A bounded raw reward, small coefficient, or annealed coefficient may not be
represented as bounded optimization pressure. Studies must report the realized
transformed advantage and gradient contribution, not only the raw reward.

## Mandatory diagnostics

Training studies that consume a dense internal or external signal must report,
at minimum:

- raw task reward and raw shaping signal distributions;
- within-group mean, variance, and prevalence of zero-variance groups;
- prevalence of all-fail and all-success groups;
- transformed advantage distributions by outcome stratum;
- shaping-to-task gradient norm ratio and update-direction agreement where
  technically available;
- policy entropy, action diversity, repeated-action rate, refusal/no-op rate,
  episode length, timeout rate, and horizon saturation;
- source-signal accuracy or fit separately from task success;
- objective success, failure severity, recoverability, and irreversible-action
  outcomes;
- checkpoint-by-checkpoint trajectories rather than endpoint-only reporting;
- seed-level results, task-clustered uncertainty, and failed runs; and
- complete compute, latency, memory, data, and recertification cost.

High source-signal accuracy with falling objective success is a collapse alarm,
not monitor validation. Stable task reward with rapidly increasing auxiliary
fit is insufficient without objective-outcome and behavior diagnostics.

## Mandatory delivery-channel and placebo matrix

Before claiming that signal semantics improve agent behavior, future compatible
studies must compare, under matched task populations and cost:

1. no added signal;
2. the signal as a logged observation-only diagnostic;
3. the signal as an auxiliary loss isolated from the policy reward;
4. the signal as reward or advantage shaping;
5. the reward channel without standard-deviation normalization where compatible;
6. coefficient and group-size sweeps;
7. sparse versus dense delivery where compatible;
8. true labels versus shuffled, random, constant, frequency-matched, and
   prevalence-matched placebo labels;
9. signal values with preserved marginal distributions but broken
   example-to-label correspondence;
10. task-progress and terminal-outcome baselines;
11. simple regularization or representation-learning controls with matched
    parameter count and compute; and
12. multiple seeds with prospectively frozen aggregation.

A true-label arm that does not beat a shuffled-label placebo establishes at
most channel-level regularization or optimization value. It does not establish
semantic monitoring, error awareness, memory, planning, or correctness
prediction.

## All-fail-group and variance-profile stress gate

Every group-normalized agent-training proposal must include controlled
populations with varying task difficulty and all-fail-group prevalence. It must
measure whether the source signal's within-group variance:

- persists after the task reward becomes uninformative;
- decays, remains constant, or grows as the auxiliary prediction is mastered;
- changes with group size and task mixture;
- is dominated by episode length, position, timeout, or action repetition; and
- creates transformed advantages whose scale or sign is insensitive to the
  nominal signal coefficient.

The paper's proposed variance-profile criterion is an external hypothesis, not
an admitted theorem for jLens. It must be tested prospectively on the exact
optimizer, task distribution, and model artifact before it can support any
safety or channel-selection claim.

## Internal-monitor-to-training boundary

No jLens hidden-state, router, workspace, sparse-feature, transcoder,
directional-JVP, Jacobian, confidence, or external-verifier score may be used as
reward, advantage shaping, auxiliary supervision, replay priority, sampling
weight, route target, or adaptation target merely because it predicts an
outcome passively.

Before such use, the signal must separately pass:

1. its existing artifact, provenance, numerical, leakage, calibration, and
   sealed incremental-value gates;
2. observation-only evaluation on a fresh population;
3. delivery-channel and placebo comparisons from this addendum;
4. exact adapted-artifact admission;
5. objective-versus-evaluator divergence and monitor-gaming tests;
6. collapse, tail-risk, recoverability, and irreversible-action evaluation;
7. privacy and sealed-data review for training inputs and optimizer state;
8. rollback and fail-closed recovery admission; and
9. a separate production decision.

Passive predictive value does not authorize training. Training benefit does not
establish natural legibility in the original representation. A trained policy
that becomes better at the monitor objective is not thereby better at the
independent task objective.

## Agents-A1 consequence

After every existing Q35Q and model-artifact gate passes, the minimum relevant
Agents-A1 sequence is:

1. freeze objective outcomes, evaluator policies, irreversible-action
   boundaries, signal semantics, and sealed-data partitions;
2. establish deterministic, executable, confidence, self-judgement,
   trajectory, memory, and passive hidden-state baselines on the separately
   admitted Agents-A1-4B artifact;
3. evaluate any proposed dense signal observation-only before adaptation;
4. if adaptation is scientifically justified, run the complete delivery-channel,
   normalization, group-size, placebo, and multi-seed matrix first on 4B under a
   separately admitted training artifact;
5. require objective task improvement beyond shuffled-label and generic
   auxiliary-regularization controls;
6. separately admit Agents-A1-35B and repeat optimizer, normalization,
   group-construction, and adapted-artifact validation rather than transferring
   coefficients or thresholds;
7. capture minimal router and expert-path telemetry only after passive cheaper
   comparators are frozen;
8. require route signals to add sealed objective-outcome value before any
   router-targeted training proposal;
9. add sparse-feature or transcoder comparisons;
10. add Jacobian-Lens only after exact derivative parity and sealed incremental
    value over every cheaper comparator; and
11. keep reward shaping, auxiliary training, router adaptation, early exit,
    retry, repair, truncation, forced routing, activation steering, quarantine,
    and production enforcement under separate intervention and production
    gates.

No reward-channel experiment on Agents-A1-35B is authorized by a positive 4B
result. Scale, sparsity, routing, quantization, batching, serving state, and
optimizer dynamics require separate admission.

## Current blocker remains unchanged

The next admissible engineering progress remains complete production-path
upstream/runtime provenance composition:

1. verify the frozen Transformers wheel and installed-distribution bytes in the
   same controlled subprocess;
2. enforce controlled import state and reject shadow packages, editable
   installs, pre-imported modules, and in-memory monkeypatching;
3. execute the complete adversarial provenance conjunction in the target
   runtime;
4. freeze the exact GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` tuple;
5. bind the actual GPTQModel/Defuser loader entry and its complete live-object
   source closure;
6. run the strict synthetic Qwen3.5-MoE loading fixture;
7. prove one-time packed-tensor consumption and exact expert/fusion ordering;
8. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
9. complete Phase-0 admission before weight staging or GPU authorization.

This addendum authorizes none of those later actions by itself.