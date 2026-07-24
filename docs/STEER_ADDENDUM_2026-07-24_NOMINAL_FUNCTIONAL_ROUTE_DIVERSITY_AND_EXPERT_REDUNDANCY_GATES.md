# Steering Addendum — Nominal/Functional Route Diversity and Expert-Redundancy Gates

Date: 2026-07-24

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `e83b15c18b5e0f568afd370ed4002516b6af2f29`

## Scope

This addendum applies to every future claim involving MoE route diversity,
expert specialization, route compression, expert redundancy, effective expert
count, temporal route contraction, reasoning-stage routing, route-based error
prediction, route-regret prediction, expert pruning or masking, router
adaptation, sparse-feature or transcoder comparisons, Jacobian Lens, and
scaling to Agents-A1 or a comparable large MoE.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload retrieval,
model execution, GPU execution, hidden-state capture, router capture, expert
profiling, pruning, masking, route intervention, Jacobian fitting, sealed
scientific evaluation, or production use is authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-set, exact-gradient,
parity, resource, cleanup, commit-safety, comparator, nuisance-control,
multiplicity, production-gating, and stop rule remains binding.

GitHub currently reports this repository as public. This document contains only
aggregate public-source program-control information. It does not authorize
committing prompts, outputs, token IDs, per-task predictions, verifier labels,
hidden states, router logits, expert identities, expert profiles, route arrays,
Jacobians, gradients, model weights, tensor payloads, caches, credentials,
local paths, or private logs.

## New external evidence and narrow interpretation

Tsao, Lin, and Wang, “Is MoE Routing a Huffman Code? Discovering the
Frequency-Diversity Law in Chain-of-Thought,” arXiv `2607.20427v1`, report that
route-set diversity varies with their estimated operation rarity in
Phi-3.5-MoE and Gemma-4-27B-A4B, while the same relationship is not measurable
in Qwen3.5-35B-A3B under their original expert identities.

Their analysis uses the union of selected experts across tokens in a
newline-delimited reasoning step as a code-length surrogate. The semantic
operation variable contains four keyword-classified categories. The headline
rank correlation therefore has only four operation-level points and is
conditional on that segmentation, classifier, task mixture, correct-trajectory
selection, model, layer aggregation, and route-diversity definition.

For Qwen3.5-35B-A3B, the authors build per-expert co-activation profiles from
correct reasoning traces using operation-type and normalized-trajectory-stage
features. They report high within-layer similarity among those profiles and
interpret this as functional redundancy. Their proposed Subset Difference
Pruning greedily identifies similar experts and masks selected router logits at
inference time before top-k selection.

No attributable immutable public implementation was located during this
review. These are external author-reported findings, not admitted results of
this repository.

The defensible correction is narrower than the paper’s universal coding claim:

1. Distinct expert indices need not represent distinct functions.
2. Nominal route diversity and functional route diversity are different
   scientific objects.
3. Any estimated effective expert count depends on a frozen descriptor,
   population, similarity rule, clustering or counting rule, layer, stage,
   checkpoint, runtime, and serving condition.
4. Token frequency, operation frequency, surprisal, task family, trajectory
   phase, segmentation, and output length can explain route diversity without
   implying correctness awareness.
5. Runtime expert masking is an intervention even when stored weights are not
   edited.
6. Preserved accuracy on one benchmark does not establish redundant experts,
   route equivalence, safe pruning, or Agents-A1 transfer.

The paper is directly relevant because it studies Qwen3.5-35B-A3B, the nearest
public base-family large-MoE comparator for Agents-A1-35B. It does not establish
results on either Agents-A1 checkpoint.

## Required object separation

Every compatible study must bind these objects separately:

1. **Router state:** pre-top-k logits or probabilities at an exact token, layer,
   stage, cache state, runtime, and serving condition.
2. **Executed route:** selected expert identities, weights, order, capacity
   disposition, dispatch, gather, and shared-expert behavior.
3. **Nominal diversity:** identity-based counts, sets, unions, transitions, or
   path statistics over the architecture’s declared expert indices.
4. **Functional descriptor:** the exact observation used to characterize an
   expert, such as co-activation, output response, activation response,
   intervention response, gradient response, or task-conditioned behavior.
5. **Functional similarity:** the metric, normalization, matching population,
   threshold, and uncertainty used to compare experts.
6. **Effective expert count:** the exact estimator that converts descriptors
   and similarities into a scalar or partition.
7. **Functional diversity:** diversity after prospectively frozen functional
   equivalence or similarity treatment.
8. **Objective outcome:** the independent correctness, safety, artifact, tool,
   or environment endpoint.
9. **Monitor score:** any nominal-route, functional-route, hidden-state,
   sparse-feature, transcoder, directional-JVP, or Jacobian-derived score.
10. **Intervention:** expert deletion, checkpoint surgery, router-logit masking,
    expert substitution, route forcing, expert skipping, merging, distillation,
    retry, truncation, or early exit.
11. **Decision policy:** any threshold, ranking, selection, fallback, escalation,
    or production rule.

Evidence about one object does not admit another. High nominal diversity does
not establish high functional diversity. High functional similarity under one
descriptor does not establish interchangeable experts. Interchangeability for
one local output does not establish full-continuation or task-level equivalence.

## Nominal-versus-functional diversity gate

Every future route-diversity result must report nominal and functional variants
separately where technically feasible.

Minimum nominal reporting includes:

- selected expert count per token and layer;
- unique expert union per frozen event unit;
- route entropy, margin, occupancy, transition, and ancestry statistics;
- shared-expert and dense-path treatment;
- top-k, capacity, overflow, drop, renormalization, and dispatch semantics;
- event segmentation and aggregation rules.

Minimum functional reporting requires at least two meaningfully different
families where feasible:

1. a usage or co-activation descriptor; and
2. a response-based descriptor measured on matched hidden-state inputs.

Additional admissible descriptor families include:

- expert output-vector similarity on a prospectively frozen input population;
- expert-output covariance, CKA, canonical-correlation, or effective-rank
  summaries;
- matched single-expert swap, ablation, patch, or substitution effects;
- local logit, hidden-state, route-lineage, and full-continuation effects;
- task-, language-, modality-, tool-state-, and trajectory-stage-conditioned
  response profiles;
- activation-JVP or VJP response only after exact derivative admission.

A co-activation profile establishes similarity in where experts are selected,
not similarity in what they compute. Weight similarity alone establishes
neither usage nor functional equivalence. One local output metric cannot be
silently promoted to complete behavioral equivalence.

## Effective-expert-count identifiability gate

`E_eff` is not an architecture constant unless the estimator is explicitly
defined and admitted.

Every effective-count claim must freeze:

- target model, checkpoint, quantization, runtime, kernel, topology, and serving
  state;
- layer and expert population, including shared, routed, dense, MTP, vision, and
  modality-specific paths;
- calibration tasks, prompts, trajectories, event units, and sampling weights;
- whether only correct, only completed, or mixed trajectories are included;
- functional descriptor and its normalization;
- distance or similarity metric;
- threshold, clustering, graph, rank, entropy, participation-ratio, or other
  estimator;
- seed, solver, tie handling, stopping rule, and complete parameter curve;
- train, calibration, certification, and sealed-evaluation populations.

Required sensitivity analysis includes:

- multiple similarity thresholds or rank criteria;
- multiple descriptor families;
- seed and sample-size stability;
- task-, family-, language-, modality-, stage-, and checkpoint-disjoint tests;
- random-expert, frequency-matched, occupancy-matched, and layer-matched nulls;
- expert-index permutations;
- comparisons before and after quantization, defusion, pruning, masking, or
  runtime conversion;
- uncertainty on the resulting partition or scalar effective count.

A claimed redundancy trap that disappears under a response-based descriptor or
a held-out population is descriptor-specific evidence, not a stable property of
the model.

## Frequency, rarity, and surprisal controls

A route-diversity relationship may reflect token statistics or task construction
rather than semantic operation or reasoning quality.

Future studies must prospectively freeze and report, where applicable:

- tokenizer and subword identity;
- token frequency from a named immutable reference corpus;
- prompt-side and generation-side token frequency separately;
- same-boundary token surprisal, entropy, margin, rank, and probability;
- task, benchmark, language, modality, and domain frequency;
- semantic-operation ontology and classifier;
- classifier accuracy, abstention, and confusion matrix on an independent set;
- prompt length, completion length, event-unit token count, and token budget;
- trajectory position, normalized position, phase, retries, tests, tool calls,
  verifier feedback, and remaining budget;
- punctuation, newline, formatting, answer-scaffold, code, and numeric-token
  indicators;
- correctness, confidence, self-judgement, and objective outcome.

Mandatory cheap comparators include:

1. token-frequency-only and surprisal-only models;
2. event-length and trajectory-position models;
3. task-family, language, modality, and formatting models;
4. occupancy, parent-route, route-transition, and expert-frequency models;
5. same-boundary logits, confidence, and entropy;
6. raw hidden-state and bounded trajectory summaries;
7. deterministic external checks and verifiers.

The primary monitor claim must be sealed incremental objective-outcome value
after these controls. Otherwise the result is classified as token-statistics,
trajectory-phase, workload, or routing-process telemetry.

## Operation-label and segmentation gate

Reasoning-step and operation-type labels are analysis artifacts.

Every study must freeze:

- the event boundary: token, sentence, newline block, tool event, edit, test,
  verifier event, or other unit;
- operation ontology and exclusivity rules;
- classifier implementation, prompt, model, commit, threshold, and abstention;
- annotation source, adjudication, and inter-annotator agreement where humans are
  used;
- handling of multi-operation events;
- handling of code, formulas, tool calls, observations, retries, summaries, and
  malformed traces;
- segmentation and label stability under paraphrase, formatting, and newline
  changes.

Required controls include shuffled labels, frequency-preserving label
permutations, alternative segmentations, length-matched events, lexical-feature
baselines, and a human- or rule-audited held-out sample.

A rank correlation over a small number of operation categories is descriptive
and must report the number of categories, uncertainty, category construction,
and multiplicity. It cannot establish a universal coding law without
prospective replication across richer ontologies, task families, models, and
runtimes.

## Population and correct-only selection gate

Route structure measured only on verified-correct trajectories is conditional
on successful generation.

Future studies must separately report:

- correct, incorrect, mixed, abstained, truncated, malformed, and
  verifier-unavailable populations;
- natural-prevalence and prevalence-matched results;
- task-clustered uncertainty;
- route statistics before and after the first independently localized error;
- trajectories matched on task, length, stage, surprisal, and confidence;
- fixed-common-population analyses across horizons and interventions.

A pattern found only on successful traces cannot establish prospective error
prediction, natural-population route efficiency, or safe control.

## Expert-masking and pruning boundary

Router-logit masking is a runtime intervention, not passive telemetry and not
identical to static checkpoint pruning.

Every masking or pruning study must bind separately:

- base checkpoint and immutable tensor identities;
- expert-profile fitting population and selection rule;
- exact experts masked or removed per layer;
- router-logit mutation, renormalization, capacity, overflow, and fallback;
- shared-expert and dense-path handling;
- cache, future-route, and continuation effects;
- static artifact surgery versus runtime hook behavior;
- quantization, defusion, kernels, topology, batch, and serving state;
- complete cost of profiling, selection, conversion, recertification, and
  fallback.

Required comparisons include:

1. unmodified full model;
2. full model at equal deployable memory through quantization;
3. random expert masking or retention at the same ratio;
4. frequency-, occupancy-, and layer-matched controls;
5. the proposed functional-similarity rule;
6. at least one alternative functional descriptor;
7. static pruning and runtime masking reported separately;
8. zero-mask or zero-prune equivalence;
9. full-population and frozen off-domain evaluation;
10. verifier-backed repair under a frozen equal-cost policy where compatible.

Any masked or pruned model is an adapted execution path requiring fresh
artifact, forward, route, calibration, safety, derivative, rollback, and
production admission. “No weights modified” does not preserve model identity
when executed expert selection is changed.

Preserved aggregate accuracy on one benchmark does not establish expert
interchangeability, lossless pruning, preserved long-horizon agent behavior, or
safe production use.

## Counterfactual functional-equivalence gate

Functional redundancy claims require counterfactual evidence beyond
co-occurrence where feasible.

At a frozen token, layer, hidden state, cache state, and continuation policy,
compare:

- executed expert output;
- candidate expert output;
- residual update after matched scaling;
- downstream hidden-state and logit divergence;
- later route and expert-path divergence;
- future-token and full-continuation divergence;
- objective task outcome;
- latency, memory, communication, and tail cost.

Single-expert substitutions, pair substitutions, and cluster-level substitutions
must be reported separately. A locally substitutable expert pair may diverge
later through residual, cache, attention, routing, or tool-state feedback.

The phrase `functional duplicate` is permitted only with the exact admitted
functional scope attached, such as `co-activation-profile-similar` or
`locally-output-substitutable`. Universal interchangeability requires full
continuation and outcome evidence across the intended population.

## Monitor and Jacobian comparator gate

After direct Agents-A1-35B route capture is separately admitted, future route
monitor studies must include:

- nominal expert identities and weights;
- expert-frequency, occupancy, entropy, margin, ancestry, and transition
  features;
- token frequency, surprisal, length, phase, and semantic-operation controls;
- functional-cluster or effective-count features fitted only on training data;
- nominal diversity and cluster-collapsed functional diversity;
- raw hidden states and matched hidden-state differences;
- direct/logit-lens, confidence, self-judgement, and trajectory baselines;
- dense-sibling representations from separately admitted Agents-A1-4B;
- deterministic checks and external verifiers;
- prospective route-regret predictors after their own admission;
- sparse-feature or transcoder comparators where admitted.

Router or Jacobian features must demonstrate sealed incremental objective-outcome
value over this complete stack at equal end-to-end cost.

A Jacobian feature that primarily distinguishes near-duplicate expert indices
is route-identity sensitivity, not evidence of semantically distinct computation
or hidden correctness awareness. Jacobian comparisons should therefore include
both original expert coordinates and prospectively frozen functional-cluster or
quotient representations where technically feasible.

## Agents-A1 scaling consequence

After every existing Q35Q gate passes, the minimum Agents-A1 sequence is now:

1. Freeze task contracts, outcomes, irreversible-action boundaries, event
   clocks, token-frequency references, route semantics, cache semantics,
   verifier rules, and serving conditions.
2. Separately admit Agents-A1-4B and establish deterministic, logit, confidence,
   self-judgement, hidden-state, trajectory, program-state, and external-guard
   baselines.
3. Separately admit Agents-A1-35B hidden-state, router, expert-path, cache,
   multimodal, quantized, topology, and serving capture.
4. Establish nominal route identity, occupancy, ancestry, transition, entropy,
   margin, token-frequency, surprisal, and trajectory-phase baselines.
5. Fit training-only expert functional descriptors using at least one usage-based
   and one response-based family.
6. Estimate effective expert count only under prospectively frozen estimators and
   report complete threshold, rank, seed, population, and descriptor sensitivity.
7. Compare nominal route diversity with cluster-collapsed or otherwise admitted
   functional route diversity on held-out and sealed populations.
8. Require either representation to add objective-outcome value beyond the full
   Agents-A1-4B, external-verifier, hidden-state, trajectory, and nuisance stack.
9. Run bounded counterfactual expert-substitution and route-regret audits only on
   training and validation populations before any prospective sealed monitor
   claim.
10. Add sparse-feature or transcoder comparators.
11. Add Agents-A1-35B Jacobian Lens only after exact derivative parity and sealed
    incremental value over every cheaper nominal and functional route comparator.
12. Keep masking, pruning, expert substitution, route forcing, router adaptation,
    early exit, retry, repair, truncation, activation steering, and production
    control under separate intervention and safety gates.

This sequence prevents nominal expert-index diversity, token rarity, trajectory
position, or load-balancing artifacts from being misreported as semantic
specialization or hidden error awareness.

## Active blocker and execution order remain unchanged

The active blocker remains production-path upstream/runtime provenance
composition:

1. verify the frozen upstream Transformers artifact;
2. bind the live import to its owning installed distribution and `RECORD`;
3. derive complete live-object source closure for dispatch, converters, nested
   operations, model/configuration classes, and loader objects;
4. reject shadow packages, editable installs, monkeypatches, forged identities,
   incomplete closure, incorrect ownership, and unadmitted loaders in a clean
   subprocess;
5. invoke and bind the actual GPTQModel/Defuser loader entry point;
6. freeze the complete immutable GPTQ runtime tuple;
7. pass the full adversarial integration conjunction;
8. emit only the permitted aggregate result.

After that remain packer-independent fixture validation, strict quantized-tensor
consumption and expert ordering, forward/VJP/JVP/finite-difference parity, Q35Q
Phase-0 admission, weight staging, and a separately authorized GPU transition.

## Established

Established only as external public evidence:

- Route-set diversity can vary with operation frequency and trajectory phase in
  the reported Phi-3.5-MoE and Gemma-4-27B-A4B experiments.
- The reported raw frequency-diversity relationship is not measurable in the
  unmodified Qwen3.5-35B-A3B analysis.
- Qwen3.5-35B-A3B experts can appear highly similar under the paper’s
  operation-and-stage co-activation descriptor.
- Runtime masking based on that descriptor changes Qwen3.5-35B-A3B route
  topology in the reported experiment.
- Nominal and functional route diversity are now bindingly separate scientific
  objects.
- Effective expert count, functional descriptor, similarity, segmentation,
  operation labeling, population, and intervention identities are now mandatory
  future controls.
- Existing privacy, sealed-data, verifier, provenance, derivative, intervention,
  and production gates remain intact.

## Unproven

- Independent reproduction of arXiv `2607.20427v1`.
- An attributable immutable public implementation of the reported experiments.
- A universal Huffman or MDL law governing MoE routing.
- Functional duplication beyond the paper’s co-activation descriptor.
- Stable effective expert count across tasks, descriptors, thresholds, layers,
  checkpoints, quantizations, runtimes, or serving conditions.
- Natural-population or incorrect-trajectory frequency-diversity behavior.
- Full-continuation interchangeability of the identified experts.
- Safe static pruning, runtime masking, expert substitution, or router changes.
- Transfer to Agents-A1-4B or Agents-A1-35B.
- Incremental nominal-route, functional-route, sparse-feature, transcoder, or
  Jacobian-Lens value over every cheaper comparator.
- Complete Q35Q provenance, strict loading, tensor consumption, expert ordering,
  forward parity, or derivative admission.
- Safe early exit, retry, repair, truncation, route intervention, activation
  steering, or production deployment.

The research program remains unfinished.
