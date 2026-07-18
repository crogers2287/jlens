# STEER ADDENDUM — Cross-layer routing ancestry and route-semantic confound gates

Date: 2026-07-18

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q, authorize scientific execution, or weaken any privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized.
- GitHub currently reports this repository as public. Commits remain restricted to aggregate program-control records and public-source engineering code or tests.

## New public evidence

The ICLR 2026 paper **Understanding Cross-layer Contributions to Mixture-of-Experts Routing in LLMs** studies four open MoE language models by recursively decomposing router inputs into upstream component contributions. Its bounded public findings include:

1. MoE-layer outputs usually contribute more than attention-layer outputs to routing decisions in subsequent layers.
2. Routing decisions exhibit cross-layer persistence or "MoE entanglement": earlier MoE activity can consistently promote or inhibit later expert selection.
3. Some upstream components influence routing across many later layers rather than only the immediately following router.
4. The range and sign of these effects differ across model architectures.

The public RouterInterp work, **RouterInterp: Understanding Superposed Specialisation in Mixture of Experts Routing**, uses sparse-autoencoder features to predict expert selection on GPT-OSS-20B. The public report states approximately 81% expert-routing recall compared with approximately 55% for its token-statistics baseline. Its core interpretation is that experts can represent a superposition of fine-grained features rather than one coherent semantic domain.

These are public external results, not admitted results of this repository. They establish neither correctness prediction nor causal error localization. They do establish that route telemetry can be strongly explained by prior model computation and semantic feature content.

## Binding correction: routing records are a dependent trajectory

Future router-monitor studies must not treat layer-by-token route observations as independent samples.

The sampling and inference unit must be explicit. At minimum, account for dependence within:

- tokens from the same completion;
- layers from the same token;
- repeated rollouts of the same task or template;
- steps from the same agent episode;
- semantically matched or paraphrased prompts;
- repeated tool states or environment states.

Required statistical controls include:

1. Episode-, task-, or cluster-level train/validation/sealed-test splitting.
2. Task- or episode-clustered confidence intervals.
3. Block, hierarchical, or cluster bootstrap procedures where ordinary i.i.d. resampling is unsupported.
4. Reporting of the number of independent tasks or clusters, not only the number of layer-token records.
5. No p-value, confidence interval, or effective-sample-size claim based on treating every layer-token record as independent.

## Parent-route and hidden-state controls

A later route can be predictable because it inherits earlier MoE computation. A later route association with correctness therefore does not establish a new late-layer error signal.

For every proposed route feature at layer `l`, the comparator stack must include, where available:

- the route identity and margin at layer `l-1`;
- a short frozen history of prior route identities, margins, and entropies;
- selected hidden-state projections or norms immediately before the router;
- token identity or token class, position, and generation phase;
- task, modality, language, action type, and tool-state metadata available before the decision;
- output-logit and confidence baselines available at the same boundary.

Primary route claims must report both raw and conditional value. Required conditional analyses include at least one preregistered form of:

- route innovation: observed route statistic minus a frozen predictor from prior route/history and boundary metadata;
- transition surprise or conditional negative log-likelihood under a training-only route-transition model;
- residualized route margins or entropy;
- conditional mutual information or equivalent nested-model improvement with task-clustered uncertainty;
- ablation of current-layer route features while preserving parent-route and hidden-state controls.

A route feature that loses sealed incremental value after parent-route or hidden-state conditioning must be classified as inherited or redundant telemetry, not as independent error localization.

## Cross-layer attribution is not correctness attribution

A decomposition showing that an earlier MoE output contributes to a later router establishes a computational ancestry relation only under the method's assumptions. It does not establish that:

- the earlier expert caused a reasoning error;
- the later route is suboptimal;
- changing either route repairs the answer;
- a persistent route path represents one stable semantic concept;
- a high-contribution component is safe to intervene on.

Future cross-layer routing work must separate four claims:

1. **Predictive ancestry:** an earlier component predicts a later route.
2. **Mechanistic contribution:** the component contributes to the later router logit under a frozen decomposition.
3. **Correctness association:** the route or contribution correlates with a sealed outcome.
4. **Causal utility:** an intervention changes the outcome beneficially under independent controls.

Passing one level does not authorize the next.

## Route-semantic confound controls

RouterInterp-style results make semantic predictability a mandatory nuisance baseline. Route telemetry may identify topic, token class, language, modality, formatting, tool type, or trajectory phase rather than correctness.

Before describing router telemetry as an error monitor, compare it against frozen predictors of:

- task family and benchmark source;
- semantic topic or domain;
- language and modality;
- token identity, token class, and position;
- answer-opening, delimiter, tool-call, argument, observation, and finish phases;
- tool identity and environment state;
- perception or extraction success in multimodal conditions.

Required evaluation includes:

1. Within-family and within-phase correctness prediction.
2. Family-disjoint and template-disjoint sealed tests.
3. Semantically matched correct/incorrect pairs where technically feasible.
4. Performance after residualizing or adversarially controlling task-family and phase information.
5. A frozen SAE/transcoder or other semantic-feature comparator when compatible with the model and runtime.
6. Explicit reporting when such a comparator is unavailable; absence is not evidence of Jacobian-Lens or router superiority.

High expert-selection predictability is not evidence of high error predictability.

## Path compression and feature selection

For Agents-A1-scale work, full route matrices across all tokens and layers are not the default admissible representation.

After runtime admission and only under an authorized capture protocol, prioritize compact, prospectively frozen summaries:

- route innovations relative to a parent-route baseline;
- transition surprise;
- top-k margin and entropy changes;
- expert persistence and switch counts;
- sparse cross-layer influence summaries;
- decision-boundary path prefixes;
- route-path features selected through nested training-only procedures.

Any cross-layer influence matrix, lag window, retained layer set, route-transition model, semantic nuisance model, or compression rule is model selection and must be frozen before outer-validation or sealed labels are opened.

Required negative controls include:

- shuffled layer order;
- shuffled route histories within matched task families;
- random expert relabeling preserving frequency;
- frequency-matched synthetic routes;
- parent-route-only models;
- hidden-state-only models;
- semantic-feature-only models;
- equal-capacity combinations excluding Jacobian features.

## Privacy and covert-channel boundary

Route paths can encode semantic, task, language, modality, or token information. Cross-layer persistence can increase reconstructability by creating repeated correlated observations.

The existing privacy boundary remains binding. Raw per-token route arrays, per-example route paths, prompts, outputs, token IDs, hidden states, Jacobians, verifier labels, and reconstruction artifacts must not be committed to this public repository.

Before any Agents-A1 route telemetry leaves the admitted execution boundary, require:

1. A frozen threat model for prompt, token, task, tool, and outcome reconstruction.
2. Membership and attribute-inference tests where relevant.
3. Covert-channel and intentional route-encoding tests.
4. Data minimization and retention limits.
5. Aggregate-only repository records.
6. A separate authorization for any external telemetry store.

A monitor's predictive utility does not override privacy or sealed-data controls.

## Agents-A1 scaling directive

The technically credible route-monitor sequence is now:

1. Complete Q35Q runtime provenance and derivative admission.
2. Establish sealed metadata, logit/confidence, and selected hidden-state baselines.
3. Capture minimal route identity, margin, and entropy at frozen decision boundaries.
4. Fit a parent-route transition baseline using training data only.
5. Test route innovation and transition-surprise features for sealed incremental correctness value.
6. Add route-semantic nuisance predictors and within-family controls.
7. Add compact cross-layer ancestry summaries only if they improve over parent-route, hidden-state, and semantic baselines.
8. Add Jacobian-Lens features only after exact derivative parity and capture-cost validation.
9. Test combined hidden-state, route-innovation, and Jacobian models under equal-compute comparisons.
10. Keep early exit, abort, retry, escalation, forced routing, expert intervention, and activation steering under separate policy and safety gates.

This sequence tests whether inexpensive conditional route telemetry provides value before authorizing all-layer capture or Jacobian-scale instrumentation.

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
11. Run sealed detection-only comparisons with the dependency and semantic-confound gates above.
12. Begin Agents-A1-native instrumentation only if Q35Q establishes incremental monitor value.

## Established versus unproven

Established only as external public evidence:

- Later MoE routing can be strongly influenced by earlier MoE computation.
- Cross-layer routing effects can persist across multiple layers.
- The sign and range of cross-layer effects differ across architectures.
- Sparse semantic features can predict expert selection substantially better than simple token statistics in one reported GPT-OSS-20B study.
- Route telemetry is therefore plausibly dependent on both prior route history and semantic content.

Unproven for this program:

- Q35Q admission or derivative parity.
- The cross-layer routing ancestry structure of Qwen3.5-MoE or Agents-A1.
- That route innovation predicts correctness after hidden-state and semantic controls.
- That RouterInterp-style features transfer to Agents-A1.
- Incremental correctness value of route telemetry over logits, metadata, hidden states, trajectory summaries, or sparse features.
- Safe early exit, abort, retry, escalation, forced routing, expert intervention, steering, or production utility.
