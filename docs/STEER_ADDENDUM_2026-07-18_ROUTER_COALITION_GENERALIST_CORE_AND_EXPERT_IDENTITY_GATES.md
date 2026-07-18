# STEER ADDENDUM — Router-coalition, generalist-core, and expert-identity gates

Date: 2026-07-18

Status: binding protocol addendum. This file does not reopen M38E, advance Q35Q, authorize scientific execution, or weaken any privacy, sealed-data, verifier, provenance, exact-gradient, parity, resource, production, or stop rule.

## Program state remains unchanged

- M38E remains terminally closed at `inconclusive`.
- Q35Q remains `q35q_artifact_admission_blocked`.
- The active engineering milestone remains production-path upstream/runtime provenance composition.
- No weight staging, model execution, GPU execution, hidden-state capture, router capture, Jacobian fitting, sealed evaluation, intervention, or production use is authorized.
- GitHub currently reports this repository as public. Commits remain restricted to aggregate program-control records and public-source engineering code or tests.

## New public evidence

The ACL 2026 paper **The Illusion of Specialization: Unveiling the Domain-Invariant "Standing Committee" in Mixture-of-Experts Models** introduces COMMITTEEAUDIT, a post-hoc group-level routing analysis applied to OLMoE, Qwen3-30B-A3B, and DeepSeek-V2-Lite.

Its bounded public method and findings include:

1. It records full router distributions, rather than only executed Top-k identities, and aggregates expert routing weight into task-conditioned profiles.
2. It analyzes MMLU subjects grouped into nine broad domains.
3. It defines cross-domain consensus candidates from repeated Top-k appearance and then identifies a Pareto-optimal committee using average expert rank and cross-domain rank variability.
4. It reports a compact, domain-invariant coalition of routed experts that captures a large share of routing mass across domains, layers, and routing budgets.
5. Its qualitative interpretation is a core-periphery organization: committee members support recurring reasoning or syntactic structure, while peripheral experts contribute more domain-specific content.

These are external public findings, not admitted results of this repository. The paper is post hoc, benchmark-specific, primarily aggregate, and not a correctness-monitor study. It does not establish that a committee member is causally necessary, that a peripheral expert is an error source, that the same structure exists in Qwen3.5-MoE or Agents-A1, or that manipulating committee membership improves outcomes.

## Binding correction: expert IDs are not independent semantic atoms

Future routing studies must not assume that an individual expert index is the natural or sufficient unit of interpretation.

The comparator hierarchy must include, where technically available:

1. Individual-expert identity and margin features.
2. Frequency- and occupancy-normalized individual-expert features.
3. Group or coalition features derived on training data only.
4. Generalist-core versus peripheral routing mass.
5. Parent-route, hidden-state, semantic, task-family, modality, phase, and confidence controls already required by prior addenda.

A result that appears only at the individual-expert level but disappears after occupancy normalization or coalition conditioning must be classified as frequency, generalist-core, or group-structure telemetry rather than expert-specific error localization.

## Generalist-core confound

A stable high-occupancy expert coalition may track generic language processing, syntax, reasoning phase, answer construction, or shared computational demand. It may therefore correlate with difficulty or correctness without identifying an error mechanism.

Before describing committee or expert telemetry as an error signal, future studies must compare against frozen predictors of:

- token position and generation phase;
- answer-opening, delimiter, tool-call, argument, observation, and finish states;
- task family, semantic topic, language, and modality;
- prompt and completion length;
- same-boundary logits, confidence, entropy, and hidden-state summaries;
- expected committee occupancy under matched correct examples;
- expected committee occupancy under matched task and phase controls.

Primary claims must report within-family and within-phase correctness value after these controls. High committee occupancy, high persistence, or high cross-domain stability is not evidence of correctness awareness.

## Coalition features and normalization

When group-level telemetry is evaluated, the admissible low-cost candidate set includes:

- total routing mass assigned to a training-frozen core coalition;
- peripheral routing mass;
- core-to-periphery and periphery-to-core transition counts;
- committee overlap across adjacent layers or decision boundaries;
- committee-mass innovation relative to a parent-route and task-conditioned baseline;
- transition surprise under a training-only coalition-state model;
- concentration, effective coalition size, and occupancy-normalized margins;
- sparse core-periphery summaries at frozen agent decision boundaries.

Raw coalition mass must not be treated as novel information until compared with expert frequency, route entropy, Top-k margin, prior-route history, task family, and boundary hidden states.

## Committee discovery is model selection

The following choices must be made using training data only and frozen before outer validation or sealed labels are opened:

- task grouping or domain ontology;
- token or decision boundary used for routing capture;
- use of full softmax distributions versus executed Top-k routes;
- consensus threshold;
- routing budget and Top-k definition;
- ranking, stability, clustering, or Pareto criteria;
- layer or depth-block selection;
- committee size and retained coalition members;
- core-periphery threshold;
- aggregation and normalization rules;
- downstream classifier, threshold, and calibration procedure.

Required negative controls include:

1. Frequency-matched random coalitions.
2. Random expert relabeling preserving occupancy.
3. Layer-shuffled coalitions.
4. Task-label permutations performed inside the training partition.
5. Equal-size peripheral coalitions.
6. Occupancy-only and entropy-only baselines.
7. Parent-route-only and hidden-state-only models.
8. Broad task-agnostic cores compared with task-conditioned groups.

Selecting a committee on the scientific test set and then reporting its correctness association is inadmissible.

## Expert identity and checkpoint portability

Expert indices are checkpoint-specific labels. Their numerical identities have no presumed semantic alignment across:

- model families;
- checkpoints or training steps;
- quantizations;
- conversion and defusion paths;
- expert packing layouts;
- tensor-parallel or expert-parallel sharding;
- runtime implementations;
- fine-tuning, RL, merging, pruning, or distillation.

Cross-checkpoint transfer requires a prospectively frozen alignment method based on admitted observable behavior or immutable parameter provenance. Post-hoc expert matching using sealed outcomes is prohibited.

Every claimed transfer must separately report:

1. Exact source and runtime identities.
2. Expert-index and packing correspondence.
3. Committee membership stability.
4. Occupancy and route-mass stability.
5. Sign and calibration stability.
6. Correctness value after re-establishing all nuisance controls.

A committee discovered in Qwen3-30B-A3B, OLMoE, DeepSeek-V2-Lite, or Q35Q does not establish a committee in Agents-A1.

## Full-distribution versus executed-route boundary

COMMITTEEAUDIT uses full routing distributions. Production telemetry may expose only executed Top-k experts, selected weights, margins, or aggregate counters.

Future work must distinguish:

- full pre-Top-k router distributions;
- executed Top-k identities and weights;
- post-capacity or post-load-balancing assignments;
- expert outputs actually consumed by the forward path;
- reconstructed or approximate routing distributions.

Evidence derived from full router softmax vectors cannot be claimed available online when the admitted production path exposes only executed routes. Any additional capture path requires separate provenance, parity, cost, privacy, and production admission.

## Attribution and intervention remain separate

A standing committee can be structurally dominant without being safely manipulable.

Committee membership, high routing mass, or cross-domain persistence does not authorize:

- committee forcing;
- peripheral-expert suppression;
- expert ablation;
- routing-logit modification;
- load-balancing changes;
- expert pruning;
- activation steering;
- early exit or truncation.

Any later intervention requires a separate causal protocol with equal-compute controls, random and occupancy-matched interventions, wrong-to-right and right-to-wrong transitions, degeneration checks, task-family transfer, latency and memory accounting, and independent safety authorization.

## Privacy and sealed-data boundary

Coalition summaries may be lower-dimensional than raw route matrices, but repeated core-periphery paths can still encode task, topic, phase, tool, modality, and outcome information.

The existing privacy boundary remains binding. Raw per-token route arrays, full softmax vectors, per-example coalition paths, prompts, outputs, token IDs, hidden states, Jacobians, verifier labels, and reconstruction artifacts must not be committed to this public repository.

Any future external route telemetry requires a frozen reconstruction threat model, data minimization, retention limits, membership and attribute-inference testing where relevant, and separate authorization for the telemetry store.

## Agents-A1 scaling directive

The technically credible route-monitor sequence is now:

1. Complete Q35Q runtime provenance and derivative admission.
2. Establish sealed metadata, confidence, and selected hidden-state baselines.
3. Capture only minimal executed-route identity, weight, margin, and entropy at frozen decision boundaries.
4. Estimate individual-expert occupancy and parent-route transition baselines using training data only.
5. Test frequency-normalized route innovation for sealed correctness value.
6. Derive a training-only generalist-core or coalition representation only if it reduces dimensionality or improves stability.
7. Compare individual, occupancy-normalized, coalition, semantic, hidden-state, and combined models under equal compute.
8. Add Jacobian-Lens features only after exact derivative parity and after cheaper route summaries fail the incremental-value gate.
9. Re-establish committee and expert alignment separately for every Agents-A1 checkpoint, runtime, quantization, and modality path.
10. Keep abort, truncation, retry, escalation, forced routing, expert suppression, pruning, and activation steering under separate policy and safety gates.

This sequence tests whether a compact core-periphery representation captures the useful route signal without assuming that raw expert IDs are stable semantic modules.

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
11. Run sealed detection-only comparisons with coalition, occupancy, dependency, and semantic-confound controls.
12. Begin Agents-A1-native instrumentation only if Q35Q establishes incremental monitor value.

## Established versus unproven

Established only as external public evidence:

- Stable co-activated expert coalitions can appear across broad domains in several open MoE models.
- Group-level routing structure can differ from conclusions drawn from individual expert frequencies.
- A compact generalist core can coexist with explicit shared experts and more task-specific peripheral experts.
- Full router distributions can expose structure not present in executed Top-k identities alone.

Unproven for this program:

- Q35Q admission or derivative parity.
- A standing committee in Qwen3.5-MoE or Agents-A1.
- Stability of any committee across checkpoint, quantization, runtime, or modality changes.
- Correctness prediction from committee mass, core-periphery transitions, or coalition surprise.
- Incremental coalition value over frequency, entropy, logits, metadata, hidden states, route innovations, trajectory summaries, or sparse semantic features.
- Safe early exit, abort, retry, escalation, forced routing, expert suppression, pruning, steering, or production utility.
