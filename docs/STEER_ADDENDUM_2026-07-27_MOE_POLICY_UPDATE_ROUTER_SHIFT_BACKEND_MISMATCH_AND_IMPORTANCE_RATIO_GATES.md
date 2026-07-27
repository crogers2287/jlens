# STEER ADDENDUM — MoE policy-update router-shift, backend-mismatch, and importance-ratio gates

Date: 2026-07-27
Parent remote head: `0e14dead45a8440b482683cbe834593227540d4a`

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
upstream/runtime provenance composition. This addendum changes a future MoE
adaptation and training-stability claim boundary; it does not displace that
milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control
and public-source engineering material may be committed. Prompts, outputs,
token data, per-example outcomes, hidden states, router logits, expert paths,
importance-ratio traces, verifier records, model weights, optimizer state,
training batches, reward traces, caches, credentials, host paths, and private
environment details remain prohibited.

## Triggering primary evidence

Zhang et al., `Towards Stable and Effective Reinforcement Learning for
Mixture-of-Experts`, ACL 2026, Anthology `2026.acl-long.1165`, originally
arXiv `2510.23027`, studies off-policy reinforcement learning with verifiable
rewards on top-K-routed MoE language models.

The authors report:

- changes in expert routing between an old rollout policy and the current
  updated policy coincide with increasingly volatile importance-ratio signals,
  bursty clipping, entropy loss, and reward collapse;
- a per-token router-shift weight computed on experts activated by the old
  policy, detached from gradients and bounded below, can be multiplied into
  the policy importance ratio before clipping and aggregation;
- on Qwen3-30B-A3B, reported three-seed math average Pass@1 increased from
  `76.4` for GMPO to `77.1` for GMPO plus router shift, while code average
  increased from `82.5` to `85.2`;
- the same route-aware weighting acted as a stabilizing plug-in for several
  GRPO-style objectives in a Qwen2.5-MoE Countdown setting;
- freezing the router and replaying old routes were not satisfactory in the
  reported experiments because they restricted adaptation or exploration;
- the reported Qwen3-30B-A3B implementation reduced throughput by `20.8%`
  relative to GMPO and required approximately `1.5 GiB` of additional
  per-device route-state storage under the reported 48-layer, top-8,
  batch-128, 8192-token condition.

The paper is bounded evidence. Its principal large-scale model is
Qwen3-30B-A3B; it studies top-K routing and primarily rule-verifiable math and
code rewards. It does not establish generality to expert-choice routing,
dense or learned rewards, preference optimization, multimodal agents,
persistent tool use, arbitrary distributed runtimes, Qwen3.5/Qwen3.6, or
either Agents-A1 checkpoint. No attributable immutable implementation
sufficient for exact reproduction was located during this steering run.

Current NVIDIA NeMo RL documentation provides separate implementation
evidence that MoE policy training can also become unstable when rollout and
training backends disagree. It distinguishes:

- **algorithmic router shift**, produced by policy updates between rollout and
  optimization; and
- **backend mismatch**, where precision, kernels, parallel execution, or
  training-versus-generation implementations produce small log-probability
  differences that can flip top-K expert selection.

The documentation recommends pure-online updates as one way to remove
multi-epoch policy drift and route-aware importance-sampling filtering as one
way to contain backend disagreement. These are implementation practices, not
proof that one recipe is universally safe or optimal.

## Bounded interpretation

The triggering sources do not establish:

- that router shift is the only cause of MoE reinforcement-learning collapse;
- that a stable route is a correct, safe, or desirable route;
- that router-shift weighting estimates objective correctness;
- that routing volatility is an endogenous uncertainty or error signal;
- that down-weighting route-changing tokens preserves an unbiased policy
  objective;
- that token filtering, sequence filtering, clipping, replay, freezing, or
  pure-online updates are interchangeable;
- that generation-backend and training-backend log probabilities are
  mathematically equivalent;
- that a route-stable training run generalizes to a new runtime, precision,
  topology, batch scheduler, checkpoint, or task family;
- that passive router telemetry is safe to use as reward, sample weight,
  replay priority, or adaptation target; or
- transfer to Agents-A1-35B.

The material protocol consequence is narrower:

> In a sparsely routed policy, the rollout policy, current policy, router state,
> generation backend, training backend, importance-ratio estimator, route-shift
> estimator, filtering rule, and resulting adapted artifact are distinct
> scientific and production objects.

A scalar reward or policy ratio cannot certify that the same conditional
expert computation was executed. Conversely, a route difference does not by
itself establish a harmful or incorrect policy update.

## Binding rollout, policy, route, and backend separation

Every compatible MoE training study must freeze and report at least the
following as separate identities:

1. **Rollout policy:** exact checkpoint, optimizer step, adapters, router
   parameters, expert parameters, tokenizer, chat template, and generation
   policy used to sample each trajectory.
2. **Current training policy:** exact parameter state against which each loss
   and importance ratio is evaluated.
3. **Reference-policy lifecycle:** update cadence, lag, snapshot method,
   refit/refresh rule, rollout reuse count, mini-batch epochs, and staleness.
4. **Generation backend:** implementation, version, kernels, attention path,
   quantization, precision, topology, batching, cache behavior, and sampling
   state.
5. **Training backend:** implementation, version, kernels, precision,
   parallelism, recomputation, activation checkpointing, and log-probability
   path.
6. **Router contract:** router module identity, input boundary, normalization,
   temperature, top-K, tie-breaking, capacity, overflow/drop policy, shared
   experts, masks, auxiliary biases, and expert ordering.
7. **Old route state:** exact indices and probabilities or logits retained from
   the rollout policy, including layer, token, sequence, and route ancestry.
8. **Current route state:** exact route quantities recomputed by the current
   policy under the training backend.
9. **Policy importance ratio:** numerator, denominator, token/sequence
   aggregation, clipping, masking, correction, and undefined-case handling.
10. **Router-shift statistic:** support set, direction, normalization, layer
    aggregation, floor, clipping, stop-gradient boundary, and missing-route
    handling.
11. **Consumed training weight:** the actual post-transformation scalar or mask
    entering the loss, distinct from the raw reward, advantage, policy ratio,
    and route statistic.
12. **Adapted artifact:** exact policy, router, experts, optimizer state, and
    runtime produced by the update.
13. **Independent objective outcome:** task, safety, verifier, recoverability,
    and irreversible-action outcomes on fresh populations.

Reconstructing old routes from the current policy is not an old-policy route
measurement. Replaying old indices through new expert weights is not the same
execution as replaying the complete old policy. Evaluating the same checkpoint
through two backends is a backend-parity condition, not a policy-update
condition.

## Algorithmic-shift versus backend-mismatch gate

Before a route-aware stabilization result is interpreted, the study must
prospectively separate at least these conditions where technically feasible:

1. same checkpoint, same backend, deterministic replay;
2. same checkpoint, different generation and training backends;
3. updated checkpoint, same backend for rollout and training evaluation;
4. updated checkpoint, different rollout and training backends;
5. router-frozen updates;
6. expert-frozen/router-only updates;
7. pure-online single-update-per-rollout training;
8. multi-epoch or otherwise off-policy rollout reuse;
9. old-index replay and old-logit/probability replay; and
10. no route-aware weighting.

The minimum report must distinguish:

- route changes caused by parameter updates;
- route changes caused by backend or precision differences;
- route changes caused by stochastic sampling, batching, cache state, or
  nondeterministic kernels;
- route changes caused by quantization or distributed reductions; and
- combined interactions.

A successful same-backend experiment does not certify a split
training/serving stack. A successful split-backend run does not establish that
backend mismatch was absent; it may only show that a filter suppressed the
observed damage.

## Router-state and route-lineage identity gate

Compatible MoE studies must preserve route lineage at the token and layer
boundaries required by the claimed estimator. The frozen identity includes:

- token and prefix identity;
- sequence position and generation stage;
- checkpoint and optimizer step;
- router input activation boundary;
- router logits before and after bias, normalization, temperature, and masks;
- selected expert indices, order, probability, weight, and tie state;
- shared-expert and routed-expert contributions;
- capacity overflow, dropped-token, and fallback behavior;
- expert-parallel rank and physical placement;
- dispatch, all-to-all, combine, and synchronization semantics;
- quantization, precision, and accumulator types;
- batch composition, padding, sequence packing, and scheduler state; and
- deterministic seed and kernel controls.

Nominal expert index equality is insufficient when expert weights, fusion,
physical placement, runtime kernels, or combine order differ. Route equality
is not functional-expert equality. Functional equality requires separately
admitted output or intervention evidence.

## Importance-ratio and estimand gate

Policy importance ratios, backend-correction ratios, router-shift ratios, and
reward-normalized advantages must remain separately reported.

Every compatible study must freeze:

- whether ratios are computed per token or per sequence;
- arithmetic versus geometric aggregation;
- numerator and denominator backend identities;
- whether rollout log probabilities are stored or recomputed;
- clipping bounds and asymmetric clipping;
- token masks, sequence masks, truncation, flooring, and zero handling;
- stop-gradient boundaries;
- treatment of invalid, missing, underflowed, overflowed, or nonfinite values;
- normalization populations and distributed reduction semantics;
- whether route weights multiply ratios before or after clipping;
- whether filtering changes the objective population; and
- the exact loss normalization after tokens or sequences are removed.

Dropping, masking, clipping, or down-weighting route-shifted samples changes the
consumed training population and may change the estimand. Such a condition may
not be represented as unbiased policy optimization without a separate proof.

A low average route-shift value may hide a small high-severity tail. A low
average importance ratio may hide sequence-local spikes. Endpoint reward may
not substitute for complete distribution and tail reporting.

## Mandatory diagnostics

Future compatible MoE policy-update studies must report at least:

- old-versus-current top-K overlap by layer, position, task family, and outcome;
- ordered path agreement and route-edit distance across layers;
- router-distribution divergence on the old support and on the full support
  where available;
- route-shift mean, quantiles, maximum, and threshold-exceedance fractions;
- expert-load, capacity-overflow, and dropped-token distributions;
- policy log-ratio and backend-correction-ratio distributions;
- clipping, flooring, token-mask, sequence-mask, and undefined-case fractions;
- retained-population coverage after every filter;
- reward, verifier score, objective success, and failure severity for retained
  and rejected strata;
- policy entropy, route entropy, action diversity, repetition, truncation,
  timeout, and horizon saturation;
- gradient norms and update contributions by route-shift stratum where
  technically available;
- checkpoint-by-checkpoint trajectories, collapse alarms, and rollback events;
- multiple seeds and task-clustered uncertainty; and
- complete training throughput, memory, communication, cache, storage, and
  recertification cost.

A route-aware method that improves aggregate reward while disproportionately
removing difficult, long, rare, unsafe, or failure-recovery trajectories has
not established general policy improvement.

## Mandatory comparator and placebo matrix

Before assigning causal value to a router-shift statistic, future compatible
studies must compare, under matched data and complete cost:

1. the dense or non-routed sibling where available;
2. no route-aware correction;
3. pure-online single-update training;
4. matched off-policy rollout reuse;
5. router freezing;
6. router-only and expert-only updates;
7. old-index replay and old-logit/probability replay;
8. token-level and sequence-level policy-ratio aggregation;
9. token masking, sequence masking, clipping, and soft weighting;
10. matched random weights or masks;
11. position-, length-, entropy-, confidence-, and difficulty-matched weights;
12. route weights with preserved marginals but broken example correspondence;
13. same-backend and split-backend execution;
14. matched precision and deliberately perturbed precision conditions; and
15. multiple seeds with prospectively frozen aggregation.

A router-shift arm that does not beat matched nonsemantic or difficulty-based
weighting establishes at most an optimization or curriculum effect. It does
not establish route-specific correctness information.

## Selection, coverage, and successful-episode survival gate

Filtering or down-weighting route-unstable tokens can preferentially remove the
parts of a trajectory where recovery, exploration, correction, tool use, or
rare expert access occurs.

Every compatible study must therefore report:

- sample, token, and sequence retention rates;
- successful-episode survival through the complete filtering cascade;
- objective success on the original full population;
- outcome-conditioned and family-conditioned retention;
- retention of rare experts, rare routes, long contexts, tool boundaries,
  recovery steps, and irreversible-action precursors;
- behavior when the retained population becomes too small or unrepresentative;
  and
- exact full-path fallback when route evidence is undefined or coverage gates
  fail.

A filtered training run may not claim improved reliability merely because its
remaining updates are stable. Stable optimization on a selectively easier
population is a distinct result.

## Internal-monitor-to-MoE-training boundary

No passive jLens router, hidden-state, workspace, sparse-feature, transcoder,
confidence, directional-JVP, Jacobian, or external-verifier score may be used
as a route-shift weight, policy-ratio correction, training mask, reward,
advantage, replay priority, sampling weight, route target, or adaptation target
merely because it predicts an outcome.

Before such use, the signal must separately pass:

1. all existing artifact, provenance, numerical, leakage, calibration, and
   sealed incremental-value gates;
2. observation-only evaluation on a fresh population;
3. the complete delivery-channel and placebo matrix;
4. the algorithmic-shift versus backend-mismatch decomposition in this
   addendum;
5. exact adapted-artifact and optimizer admission;
6. objective-versus-evaluator divergence and monitor-gaming tests;
7. collapse, coverage, tail-risk, recoverability, and irreversible-action
   evaluation;
8. privacy and sealed-data review for route traces and optimizer state;
9. rollback and fail-closed recovery admission; and
10. a separate production decision.

Passive predictive value does not authorize route-aware training. Stable
training does not establish passive legibility. Router adaptation does not
establish that the original model naturally represented correctness in its
routes.

## Agents-A1 consequence

After every existing Q35Q and model-artifact gate passes, the minimum relevant
Agents-A1 sequence is:

1. establish deterministic, executable, confidence, trajectory, memory,
   program-state, and simple hidden-state baselines on the separately admitted
   Agents-A1-4B artifact;
2. treat the 4B result as a dense/small-model baseline only, not as validation
   of MoE-specific policy-update behavior;
3. admit a tractable top-K MoE bridge condition on the exact proposed training
   and rollout stack to validate route capture, old-policy snapshots,
   backend-parity diagnostics, importance ratios, filtering, and rollback;
4. separately admit Agents-A1-35B checkpoint, router, expert-path, cache,
   quantized, topology, serving, and training-backend identities;
5. perform observation-only route-shift and backend-mismatch characterization
   before any Agents-A1-35B parameter update;
6. run same-backend, split-backend, pure-online, off-policy, frozen-router,
   replay, mask, clipping, and soft-weight controls on a bounded preregistered
   population;
7. require objective gains beyond random, difficulty-, confidence-, length-,
   entropy-, and trajectory-matched weighting controls;
8. preserve successful-episode, rare-route, recovery, and irreversible-action
   coverage;
9. require route telemetry to add sealed objective-outcome value beyond every
   cheaper external, logit, confidence, trajectory, raw-state, and verifier
   comparator;
10. add sparse-feature or transcoder comparisons;
11. add Jacobian-Lens only after exact derivative parity and sealed incremental
    value over the complete route-aware comparator stack; and
12. keep reward shaping, auxiliary training, router adaptation, early exit,
    retry, repair, truncation, forced routing, activation steering, quarantine,
    and production enforcement under separate intervention and production
    gates.

No Agents-A1-35B adaptation is authorized by a positive result on Agents-A1-4B
or another MoE. Scale, expert count, top-K, route geometry, quantization,
precision, backend mismatch, topology, batching, context length, task family,
and optimizer dynamics require separate admission.

## Current blocker remains unchanged

The next admissible engineering progress remains complete production-path
Q35Q provenance and runtime admission:

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
