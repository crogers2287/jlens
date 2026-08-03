# STEER ADDENDUM — joint routing dependence, marginal invariance, and stochastic-Jacobian gates

Date: 2026-08-03
Parent remote head: `c19d5fc0a65284e1cd0392b8d1ba60d7e92ecaef`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every cumulative protocol correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, exact-gradient, numerical-parity, resource, commit-safety, intervention, rollback, action, and production-gating rule. It authorizes no model-weight retrieval, model execution, GPU use, hidden-state or router capture, Jacobian fitting, sealed evaluation, stochastic-route intervention, early exit, truncation, external action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains complete Q35Q production-path provenance, loader, packed-tensor-consumption, expert-order, forward, VJP, JVP, and finite-difference admission. This addendum changes a future MoE routing and derivative claim boundary; it does not displace that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and public-source engineering material may be committed. Prompts, outputs, token IDs, per-example routes, Gumbel draws, group assignments, hidden states, expert outputs, Jacobians, verifier labels, sealed outcomes, credentials, host paths, and private environment details remain prohibited.

## Triggering primary evidence

Richard Yi Da Xu, `Hierarchical Copula-Gumbel-Top-K Routing: Two-Sided Dependence Control for Frozen Mixture-of-Experts at Fixed Per-Token Routing Laws`, arXiv `2607.28670v1`, submitted 2026-07-25, studies stochastic Top-K routing under a constraint that each token's complete conditional routing law remains fixed.

The construction couples Gumbel perturbations across tokens. Within declared token groups, an exchangeable Gaussian copula introduces positive dependence. Across paired groups, an antithetic construction introduces tunable negative dependence. The paper proves, at one routing layer conditioned on the pre-routing logits, that these operations preserve each token's distribution over ordered Top-K expert lists, mixture weights, and expert-inclusion probabilities. Conditional expected expert traffic is therefore preserved.

The joint route law is nevertheless changed. Positive within-group coupling can increase route coherence and inflate realized expert-load variance relative to independent routing. Cross-group opposition can reduce load variance relative to flat coupling at the same within-group strength. The base model remains frozen, while a small controller over frozen features may set the dependence parameters using a score-function estimator. The reported pilot validates the mechanism and training route only; it does not establish task-level gains.

No attributable immutable public implementation was located during this review. No result has been independently reproduced in jLens. Nothing in the paper establishes correctness awareness, semantic expert identity, safe stopping, production utility, or transfer to Agents-A1.

## Binding interpretation

The evidence exposes a distinction not fully bound by per-token router, route-ancestry, occupancy, or counterfactual-route controls:

> A collection of fixed per-token routing laws does not identify the joint routing law across tokens, groups, layers, requests, or agent steps.

The following are separate scientific and runtime objects and may not be renamed into one another:

1. pre-routing logits for each token;
2. each token's conditional marginal distribution over ordered Top-K routes and weights;
3. the joint distribution of route choices across tokens;
4. within-group route dependence;
5. cross-group route dependence;
6. expected expert traffic;
7. realized expert-load variance and tail load;
8. route-set coherence or persistence;
9. capacity overflow, token dropping, dispatch, and communication effects;
10. objective task outcome and verifier outcome;
11. passive native router telemetry;
12. a dependence controller and its adapted parameters;
13. a route intervention or serving policy; and
14. any Jacobian or policy-gradient quantity.

Matching per-token expert frequencies, ordered-route marginals, mixture-weight marginals, or mean traffic does not establish matching path behavior, load tails, capacity behavior, communication, hidden-state lineage, task behavior, or derivative behavior.

## Joint-route artifact identity gate

Every future stochastic-routing, route-coupling, correlated-expert, marginal-preserving, copula, shared-noise, antithetic, or route-coherence study must freeze at minimum:

- exact model, checkpoint, tokenizer, template, adapter, and runtime identities;
- router input boundary, logits, transforms, temperature, Top-K, tie-breaking, shared-expert treatment, capacity, overflow, and fallback rules;
- stochastic-routing family and exact Gumbel or alternative noise construction;
- random-number generator, seed, stream partitioning, counter allocation, device, precision, and determinism controls;
- token grouping rule, group boundaries, ordering, overlap policy, semantic or trajectory metadata used by the grouping rule, and behavior for incomplete groups;
- within-group dependence family and parameters;
- cross-group pairing, opposition construction, and parameters;
- controller inputs, architecture, weights, optimizer, objective, score-function estimator, baselines, clipping, variance reduction, and stopping rule;
- batch construction, sequence packing, padding, positions, request mixing, scheduler, topology, expert placement, and communication backend;
- route sampling stage, prefill or decode stage, recurrent or cache state, and cross-layer lineage;
- exact statistics claimed to be invariant and exact statistics allowed to change; and
- complete latency, throughput, memory, communication, verification, and fallback cost.

A frozen backbone with a new stochastic coupling controller is a new executable condition. A controller trained over frozen features is an adapted artifact even when the base model weights do not change.

## Marginal-invariance admission gate

A claim of fixed per-token routing laws must identify the conditioning set and verify the complete claimed law, not only mean expert frequency.

At minimum, where technically feasible, compare the coupled condition with independent routing at identical pre-routing logits for:

1. ordered Top-K expert-list probabilities;
2. unordered expert-set probabilities;
3. expert-inclusion probabilities;
4. rank-specific expert probabilities;
5. mixture-weight distributions conditional on selected experts;
6. tie and near-tie behavior;
7. shared-expert behavior;
8. capacity, overflow, and dropped-token behavior before and after physical serving constraints; and
9. expected traffic per expert.

The mathematical invariance claim applies at the declared routing layer conditioned on its pre-routing logits. It does not automatically survive finite precision, approximate Gaussian sampling, quantization, clipping, capacity truncation, load balancing, dropped tokens, cross-layer feedback, cache evolution, batching changes, or distributed dispatch.

Required tests include exact or exhaustive small-expert fixtures, distributional goodness-of-fit with prospectively frozen tolerances, multiple seeds, adversarial logits near ties, extreme dependence parameters, uneven groups, changed batch packing, and negative controls that deliberately perturb one marginal.

A failure of marginal invariance invalidates any interpretation as a pure joint-dependence intervention.

## Joint-dependence and load-distribution gate

Every compatible study must report the joint quantities that change while marginals are held fixed. At minimum, report where applicable:

- pairwise and higher-order route covariance;
- within-group expert-set overlap and ordered-path agreement;
- cross-group overlap and opposition;
- transition and persistence statistics across tokens and layers;
- expert-load mean, variance, quantiles, maximum, and threshold exceedances;
- capacity overflow, dropped-token, reroute, and fallback rates;
- expert-parallel traffic, all-to-all volume, synchronization, and straggler tails;
- request-level and episode-level clustering of route behavior;
- hidden-state, cache-state, later-router, token, parser, and verifier divergence; and
- objective outcomes and failure severity by dependence and load stratum.

Conditional expected traffic is not a serving-safety result. A method can preserve the mean while increasing variance, tail overload, cross-request interference, or failure concentration.

## Mandatory dependence-control matrix

Before assigning semantic, correctness, or systems value to joint route coherence, future compatible studies must compare, where technically feasible:

1. native deterministic or native stochastic routing;
2. independent Gumbel-Top-K routing;
3. positive within-group coupling at fixed per-token laws;
4. cross-group antithetic coupling at matched within-group strength;
5. multiple dependence strengths including zero;
6. random token grouping;
7. contiguous-position grouping;
8. task-, semantic-, tool-phase-, or trajectory-based grouping using training-only definitions;
9. shuffled group labels preserving group sizes and route marginals;
10. coupling parameters broken from their source example while preserving their distribution;
11. load-variance-matched nonsemantic controls;
12. fixed expert-load or capacity-aware serving controls;
13. matched random controllers and frozen untrained controllers; and
14. native full-compute, no-controller fallback.

Any grouping or controller that consumes semantic, difficulty, confidence, tool, verifier, future-token, or outcome information must be treated as a separate information channel. Future or sealed information may not enter an online dependence controller.

## Passive-telemetry and causal-claim boundary

Native route correlation may arise from shared token semantics, common hidden-state ancestry, batching, positions, recurrent state, scheduler state, or the router itself. Engineered correlated noise creates an additional cause.

Future router-monitor work must therefore distinguish:

- observed native joint dependence;
- dependence predicted by pre-router hidden states and public boundary metadata;
- dependence introduced by shared random state;
- dependence introduced by a learned controller;
- dependence introduced by serving capacity or dispatch constraints; and
- residual joint dependence after those controls.

A route-path feature that predicts correctness may be exploiting group membership, shared noise, load pressure, or controller state rather than model-native error information. Monitor comparisons must include the complete coupling state and grouping metadata available at the decision boundary.

Marginal-preserving coupling is a useful causal comparator because it can change joint route structure without intentionally changing each token's conditional routing law. It does not by itself establish that any changed outcome is semantically mediated; hidden-state, load, capacity, communication, and cross-token interference remain possible mediators.

## Statistical dependence gate

Layer-token route records remain dependent observations. Joint coupling makes ordinary token-level i.i.d. inference even less defensible.

The independent sampling unit, clustering structure, and randomization unit must be explicit. Confidence intervals and tests must account for task, episode, request, sequence, group, batch, and seed dependence as appropriate. Group or controller parameters selected on validation outcomes must be frozen before sealed evaluation.

Reports must include the number of independent tasks, episodes, requests, groups, and seeds, not only the number of tokens or routing events. Marginal-invariance tests and objective-outcome tests require separate multiplicity control.

## Stochastic-Jacobian and gradient boundary

The paper's controller is trained with a score-function estimator because route samples are discrete. This creates a derivative distinction directly relevant to Jacobian Lens.

The following derivatives are not interchangeable:

1. a fixed-route activation Jacobian with selected experts held constant;
2. a fixed-noise pathwise Jacobian through continuous operations away from Top-K boundaries;
3. a router-inclusive local Jacobian under one realized route and noise draw;
4. a conditional expectation derivative with respect to pre-routing logits;
5. a score-function gradient of expected objective with respect to dependence-controller parameters;
6. a finite intervention changing the joint route coupling while preserving per-token laws; and
7. a finite change crossing Top-K, capacity, overflow, parser, stopping, or action boundaries.

A fixed-route Jacobian cannot characterize how the expected objective changes when joint coupling changes. A score-function controller gradient is not evidence that the base model contains a differentiable correctness direction. A route-marginal-preserving finite intervention can still produce discontinuous downstream route, load, cache, and output changes.

Any compatible stochastic-routing Jacobian study must freeze the noise realization or expectation estimand, route-conditioning rule, gradient estimator, baselines, sample count, variance estimates, finite-difference construction, and treatment of route changes. Exact forward, VJP, JVP, and finite-difference parity remains mandatory for every continuous branch claimed. Discrete-policy effects require separately admitted causal estimates.

## Privacy and covert-channel boundary

Joint route patterns, shared-noise state, group assignments, and controller outputs can encode task, token, tool, user, or outcome information. Correlation can increase reconstructability even when per-token marginals appear harmless.

Before any route-coupling telemetry leaves the admitted execution boundary, require a frozen reconstruction and covert-channel threat model, data minimization, membership and attribute-inference tests where applicable, cross-tenant isolation, retention limits, and aggregate-only publication. Per-example routes, groups, dependence parameters, random streams, controller features, and outcomes may not be committed to this public repository.

## Agents-A1 scaling consequence

The technically credible sequence is now:

1. Complete Q35Q exact-runtime provenance, strict loading, packed-tensor consumption, expert ordering, deterministic forward, persistent-state, VJP, JVP, and finite-difference admission.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, parser, state, tools, environment, verifier, and runtime; use it for non-MoE behavioral and hidden-state baselines only.
3. Admit Agents-A1-35B separately, including quantization, router, shared and routed experts, capacity, reduction order, caches, kernels, topology, batching, scheduler, and telemetry.
4. Characterize native per-token routing laws and native joint route dependence separately across layers, tokens, tool phases, requests, and episodes.
5. Establish cheaper confidence, hidden-state, trajectory, parser, tool-state, verifier, and route-history baselines before Jacobian fitting.
6. Use marginal-preserving route coupling only as a bounded intervention comparator after native route capture and stochastic execution are separately admitted.
7. Verify the claimed per-token invariances under the actual Agents-A1 runtime, including capacity, quantization, finite precision, and distributed dispatch.
8. Test whether changed joint dependence alters objective outcomes after controlling load variance, group semantics, batch composition, and serving interference.
9. Require any joint-route or controller feature to add sealed objective value beyond all transparent controls.
10. Add fixed-route and router-inclusive Jacobian features only after their exact estimands and parity are established; compare them with score-function and finite-intervention results without conflation.
11. Keep dependence-controller training, route intervention, capacity control, early exit, truncation, retry, external action, and production deployment under separate artifact and safety gates.
12. Preserve native full-compute execution and independent verification as fallback.

This gives the Agents-A1 program a sharper causal test: per-token route quality and cross-token route dependence can be varied and evaluated as different objects. It does not authorize correlated routing in Agents-A1.

## Current engineering blocker remains unchanged

Q35Q remains blocked on the complete Phase-0 conjunction:

1. resolve repository visibility versus destination-policy disagreement;
2. bind installed runtime files to immutable distribution ownership records;
3. derive complete executable-source closure from actual live runtime objects;
4. detect shadow imports, in-memory monkeypatching, runtime substitution, and process-global leakage in clean subprocesses;
5. bind the exact GPTQModel/Defuser loader and conversion entry;
6. freeze one immutable Transformers, GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, backend, launch, checkpoint-format, kernel, and reduction tuple;
7. run strict synthetic Qwen3.5-MoE quantized loading;
8. prove one-time packed-tensor consumption and exact expert/fusion ordering;
9. prove deterministic forward and persistent-state parity; and
10. prove activation-VJP, activation-JVP, and finite-difference parity.

No model-weight staging or GPU execution is authorized before the complete conjunction passes.

## Established versus unproven

Established only as bounded external public evidence:

- Per-token conditional Top-K routing laws do not uniquely determine the joint route law across tokens.
- Joint coupling can change route coherence and realized load variance while preserving each token's conditional ordered-route, mixture-weight, and inclusion-probability law in the paper's declared construction.
- Expected expert traffic and realized load variance are different objects.
- A dependence controller over a frozen backbone is a new controlled execution condition.
- Score-function controller gradients, fixed-route Jacobians, and finite route interventions are different estimands.

Unproven for this program:

- Independent reproduction of arXiv `2607.28670v1`.
- Exact marginal preservation under Q35Q, Qwen3.5/Qwen3.6, or Agents-A1 runtimes.
- Any task-level gain from hierarchical route coupling.
- Native joint-route dependence as a correctness or error signal.
- Incremental objective value from coupling, router telemetry, hidden states, semantic-workspace features, or Jacobians.
- Complete Q35Q admission.
- Agents-A1-4B or Agents-A1-35B admission.
- Safe stochastic routing, capacity control, early exit, truncation, retry, route intervention, external action, or production deployment.

The research program remains unfinished.
