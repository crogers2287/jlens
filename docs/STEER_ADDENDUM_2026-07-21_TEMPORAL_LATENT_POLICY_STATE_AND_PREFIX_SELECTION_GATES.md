# Steering Addendum — Temporal Latent Policy State and Prefix-Selection Gates

Date: 2026-07-21

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `bf0f17e07a9a95b406e0030e589694ac1f427929`

## Scope

This addendum applies to any future hidden-state trajectory, latent-state,
reasoning-stage, process-monitor, failure-prefix, retry, rollout-pruning,
trajectory-selection, activation-steering, router-telemetry, Jacobian-lens, or
Agents-A1 claim.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload retrieval,
model execution, GPU execution, hidden-state capture, router capture, Jacobian
fitting, sealed scientific evaluation, intervention, or production use is
authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, cleanup, comparator, nuisance-control, production-gating, and stop
rule remains binding. GitHub reports this repository as public, so only
aggregate public-source program-control information may be committed.

## New external evidence and narrow interpretation

Harrasse et al., “Reasoning Fine-Tuning Induces Persistent Latent Policy
States,” arXiv `2607.18532v1`, model sentence-level residual-stream trajectories
as a switching dynamical system. The method trains a time-aware CEBRA encoder,
fits a low-cardinality discrete regime model by EM, and analyzes persistence,
transition structure, state utilization, and mixing.

The public implementation was inspected at immutable commit
`3b7f8dc95a9787025e866f2251f49be7491ce086` in `withmartian/mi-cot`.

The paper reports:

- paired base and reasoning-specialized dense models from 1.5B to 32B;
- four explicit-chain-of-thought benchmarks;
- sentence-final activations from one selected layer per model;
- stronger differentiated transition structure after reasoning fine-tuning;
- temporal-order, correctness, representation-learning, and persistence-prior
  controls;
- state-swap and residual-stream transplantation interventions;
- PrefixGuard, which ranks four 25%-budget partial rollouts using a fixed
  combination of learned CEBRA/SDS signals, continues one prefix, adds restart
  trajectories, and applies a final hybrid selector;
- reported improvement over self-consistency in 11 of 12 model-dataset
  settings, with a maximum reported gain of 12.5 percentage points.

The binding interpretation is narrow:

1. Discrete temporal latent-state models are a serious future trajectory
   comparator and cannot be omitted from a claimed Jacobian-lens or router
   advantage when technically compatible.
2. A regime that is functionally predictive or intervention-sensitive is not
   automatically a correctness state, an error state, or a semantic workspace.
3. PrefixGuard is a multi-rollout candidate-allocation and selection policy,
   not token-level early exit and not truncation of one committed trajectory.
4. The reported results concern dense models, explicit sentence-segmented CoT,
   math and knowledge tasks, and specially constructed hard subsets. They do
   not establish tool-use, multimodal, long-horizon, MoE, or Agents-A1 validity.
5. The public release provides code but omits model weights, activation
   datasets, and raw generations. Independent reproduction remains unproven.

## Required object separation

Future studies must bind and evaluate these as separate objects:

1. backbone model and generation policy;
2. trajectory segmentation rule;
3. hidden-state capture layer, position, and normalization boundary;
4. representation encoder or projection;
5. discrete regime model and model-order rule;
6. offline state smoother;
7. online state filter or approximating estimator;
8. state-outcome utility estimator;
9. prefix or trajectory scoring rule;
10. candidate-generation and restart policy;
11. final candidate selector;
12. intervention or activation-edit policy;
13. independent objective verifier;
14. fail-closed fallback.

Improvement from the complete system may not be attributed solely to the hidden
representation, latent regimes, or state transition model unless each other
component is held fixed and ablated.

## Artifact and runtime identity

Every temporal latent-state study must freeze, at minimum:

- exact backbone repository, immutable revision, model class, processor,
  tokenizer, chat template, and reasoning mode;
- generation parameters, stop rules, token budget, sampling count, and seeds;
- serving backend, precision, attention implementation, cache behavior,
  batching, topology, and hidden-state capture path;
- sentence or step segmentation code, punctuation rules, special-token rules,
  empty-segment behavior, and position mapping;
- selected layer, token position, pre/post-normalization boundary, pooling,
  dtype, and downcasting;
- encoder architecture, training objective, temporal-positive and negative
  construction, normalization, optimizer, seeds, and artifact digest;
- regime family, state count, prior, initialization, EM implementation,
  convergence rule, BIC or other model-order criterion, and artifact digest;
- online state-estimation rule, centroids, transition matrix, decoder, and any
  approximation to the offline posterior;
- state-utility labels, score formula, threshold, candidate pool, restart
  policy, final selector, and verifier identities.

A fitted encoder, scaler, regime model, state utility table, centroid set,
transition matrix, or decoder is a learned artifact and requires the same
provenance, serialization-safety, privacy, and admission controls as any other
monitor head.

## Temporal segmentation and boundary gate

Sentence-final states are not a neutral measurement choice. Future work must
compare or control:

- sentence, clause, token, semantic-step, tool-action, and fixed-interval
  boundaries when technically compatible;
- punctuation and formatting changes;
- chain-of-thought verbosity and sentence length;
- answer-format and language changes;
- reasoning-token, tool-result, observation, and final-answer boundaries;
- malformed, unterminated, or single-sentence traces.

A state discovered under one segmentation may not be described as an intrinsic
model policy state without stability under prospectively frozen alternative
segmentations. Segmentation selected after observing state coherence,
correctness, or intervention outcomes is leakage.

## Offline smoothing versus online filtering

Offline forward-backward smoothing can use future trajectory states. It is not
available at a real-time decision boundary.

Every online claim must therefore report separately:

- offline smoothed-state performance;
- causal forward-filter performance using only the prefix;
- any nearest-centroid or one-step approximation;
- the gap between offline and online state assignments;
- state latency, decision latency, and the exact information set at each
  boundary;
- behavior when the prefix is too short, state uncertainty is high, or no
  admitted state can be assigned.

A controller selected or evaluated using smoothed future-conditioned state
assignments cannot support an online early-warning, pruning, or intervention
claim. The fail-closed default under unavailable or uncertified online state is
to preserve all candidates and continue the frozen baseline policy.

## State-model identification and non-uniqueness

Discrete regime labels are permutation-invariant and may be unstable across
seeds, layers, datasets, state counts, and checkpoints.

Future studies must report:

- BIC or other model-order curves, not only one selected state count;
- seed-to-seed state alignment and uncertainty;
- state splitting, merging, disappearance, and occupancy collapse;
- stability across layers and admissible segmentations;
- held-out one-step predictive gain over linear AR, PCA, HMM, clustering, and
  non-switching temporal baselines;
- temporal-order, randomized-positive-pair, and shuffled-label controls;
- whether functional labels were assigned before or after outcome inspection.

State names such as `verification`, `uncertainty`, `failure`, `detour`, or
`planning` are descriptive hypotheses until prospectively tested against
frozen annotations and matched lexical, positional, temporal, and correctness
controls.

## Correctness and process-state separation

A latent regime can be causally involved in reasoning while remaining
uninformative about objective correctness. Future studies must separately test:

- next-state or next-activation prediction;
- reasoning-stage classification;
- self-judgement, confidence, commitment, and answerability;
- objective final outcome;
- step-local recoverable error;
- irreversible failure onset;
- verifier acceptance;
- intervention utility.

State utilities estimated from final correctness are outcome-associated
statistics, not proof that the state locally caused failure. Required residual
controls include task family, difficulty, prompt and response length, position,
trajectory progress, lexical stage markers, answer format, self-judgement,
confidence, verifier history, and model-family identity.

Any latent-state signal that loses incremental objective-outcome value after
conditioning on those variables must be classified as process or trajectory
telemetry rather than hidden correctness awareness.

## Candidate-pool and hard-subset gate

The reported actionable experiments use problems for which eight base-model
samples were all wrong. This is a selected hard subset, not the natural task
population.

Future rollout-selection studies must report separately:

- the complete preregistered population;
- prospectively defined difficulty strata;
- the hard subset and its exact construction cost;
- candidate-pool coverage and oracle accuracy;
- correct-candidate prevalence at each budget;
- settings with zero, one, or multiple correct candidates;
- failures introduced by the selector when a correct candidate exists;
- cases where every candidate is wrong;
- all costs used to identify or construct the hard subset.

Outcome-based hard-subset membership, candidate correctness, oracle identity,
and eventual selected trajectory may not enter representation training, layer
selection, state-count selection, score design, threshold tuning, or
certification.

## Mandatory equal-budget comparators

Every technically compatible trajectory-pruning or candidate-selection study
must compare at equal total generation, monitor, verifier, and selection cost:

- one ordinary rollout;
- self-consistency with the same candidate budget;
- best-of-N by final log probability or calibrated confidence;
- random prefix selection;
- prompt and metadata ranking;
- output-only and prefix-logit ranking;
- passive hidden-state prefix probes;
- a fixed-budget recurrent or temporal hidden-state encoder;
- a Gnosis-style trajectory comparator when compatible;
- non-switching linear dynamical and clustering baselines;
- the temporal latent-regime model without outcome utilities;
- the same state model with outcome utilities;
- PrefixGuard-style prefix allocation and final selection;
- router/path summaries for MoE models;
- Jacobian-lens features only after exact derivative parity.

All policies must receive the same prompts, candidate budget, token budget,
restart allowance, verifier access, and final-answer selector. A method cannot
claim pruning efficiency when it generates more partial or restart trajectories
than the baseline without charging their full cost.

## Intervention and causal-claim boundary

State-swap degradation establishes that fitted dynamics help predict the next
representation under the tested model. Residual-stream transplantation shows
that an activation edit can change behavior. Neither result alone establishes
that the named state is a naturally occurring causal mechanism, that the edit
improves objective outcomes on the full population, or that the intervention
is safe.

Any future activation transplant, state forcing, prefix discard, retry, or
trajectory replacement requires a separately admitted intervention protocol
covering:

- frozen target state and intervention strength;
- no-op, random-direction, matched-norm, wrong-state, and sham controls;
- right-to-wrong and wrong-to-right transitions;
- malformed, refusal, loop, timeout, and tool-failure outcomes;
- full-population utility and tail-risk analysis;
- reversibility, incumbent preservation, and fail-closed fallback;
- privacy, serving, synchronization, and total-cost effects.

No passive-monitor study authorizes activation steering, route forcing, early
exit, trajectory deletion, retry, escalation, or production control.

## Privacy and sealed-data boundary

Raw prompts, chain-of-thought, hidden states, token IDs, per-step state
assignments, state trajectories, correctness labels, verifier outputs,
activation edits, candidate pools, and per-task selector decisions may not be
committed to this public repository.

Only preregistered aggregate counts, metrics, uncertainty summaries, immutable
public artifact identities, and aggregate pass/fail receipts are permitted.
Private activation and trajectory datasets require tenant isolation, bounded
retention, access control, reconstruction and membership-inference review, and
verified cleanup.

## Agents-A1 scaling consequence

The technically credible order is now:

1. Complete Q35Q production-path provenance and exact derivative admission on a
   frozen static runtime.
2. Freeze long-horizon task contracts, objective outcomes, decision boundaries,
   and irreversible-action boundaries.
3. Establish external checks, metadata, confidence, self-judgement,
   peer-representation, hidden-state, and fixed-budget trajectory baselines.
4. On separately admitted Agents-A1-4B, test passive sentence/step-level
   trajectory encoders and non-switching temporal baselines.
5. Only then fit a low-cardinality latent-regime comparator using training-only
   layers, segmentations, state counts, and temporal-pair rules.
6. Evaluate offline smoothing and causal online filtering separately.
7. Evaluate passive prefix ranking before any candidate deletion or
   activation intervention.
8. Re-admit capture and refit or prospectively test transfer on Agents-A1-35B;
   do not assume dense-sibling state or coordinate portability.
9. Add minimal direct router/path telemetry and test residual value over the
   complete temporal hidden-state stack.
10. Add sparse-feature or transcoder streams.
11. Add Jacobian-lens streams only after exact parity and sealed incremental
    objective-outcome value over every cheaper comparator.
12. Keep prefix pruning, retry, trajectory replacement, activation steering,
    route forcing, early exit, and production use under separate intervention
    and production gates.

Because Agents-A1 uses long, tool-mediated trajectories, sentence-level CoT
regimes are at most a starting comparator. Tool calls, observations, verifier
feedback, retries, branches, context compaction, multimodal inputs, and serving
state must become explicit event types and nuisance variables before an
Agents-A1 latent-policy claim is admissible.

## Current blocker and program status

The active engineering blocker remains production-path upstream/runtime
provenance composition:

1. bind the live import to its installed distribution and `RECORD`;
2. derive complete live source closure for dispatch, converters, nested
   operations, model/configuration classes, and loader objects;
3. reject shadow packages, editable installs, and monkeypatching in a clean
   subprocess;
4. bind the actual GPTQModel/Defuser loader entry point;
5. freeze the complete immutable runtime tuple;
6. pass the full adversarial integration conjunction;
7. emit only the permitted aggregate result.

After that remain strict synthetic loading, exact quantization-tensor
consumption and expert ordering, forward/VJP/JVP/finite-difference parity,
Phase-0 admission, weight staging, and a separately authorized GPU transition.

Established after this addendum:

- temporal latent-state models provide a credible trajectory comparator;
- reasoning fine-tuning is reported to reorganize latent transition structure
  across several dense model pairs;
- the reported PrefixGuard system combines a learned representation and regime
  model with multi-prefix generation, outcome-associated state utilities,
  restarts, and a final selector;
- offline smoothing, online filtering, process-state prediction, correctness
  prediction, candidate selection, and intervention are now bindingly separate;
- the temporal latent-regime comparator and its equal-budget controls are now
  mandatory when technically compatible.

Unproven:

- independent reproduction of the paper or public pipeline;
- stable latent-state identity across seeds, layers, segmentations, domains,
  checkpoints, quantizations, or runtimes;
- objective error-onset localization;
- online filtering performance equivalent to offline smoothing;
- full-population advantage over equal-cost self-consistency and simpler
  trajectory heads;
- extension to tool use, multimodal agents, MoEs, or either Agents-A1 model;
- safe prefix deletion, retry, trajectory replacement, activation steering,
  route forcing, early exit, or production deployment;
- completion of Q35Q provenance, strict loading, forward parity, or derivative
  admission.
