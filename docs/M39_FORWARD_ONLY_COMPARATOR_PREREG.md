# M39 — Forward-only Agents-A1 35B completed-error comparator (amended preregistration draft)

Status: **design-only amended preregistration draft. Capture is prohibited.** No
scientific row, pilot row, held-out row, or outcome-bearing telemetry may be
collected until M38E is finalized and a separate committed launch amendment
satisfies every pre-capture item below. This file is not launch authorization.

The original design commit `b2a76512a8fc92afead667aacc9a39e61639c1f1`
correctly froze the scope and claim boundary, but it did not yet freeze enough
statistical, leakage, provenance, telemetry, and input-ambiguity details to
support a confirmatory run. The first amendment closed the known
false-confirmation paths before any M39 scientific data existed. This amendment
adds a pre-generation ambiguity/aleatoric-uncertainty control required by
`The Role of Ambiguity in Error Prediction via Uncertainty Quantification`
(arXiv:2606.02093). It does not weaken M38E, M36V, M36T, M37J, sealed-data,
verifier, privacy, provenance, or production gates.

Steer basis: `550c27bafec69a9517d33a7524dff031f8ba17d6`
(incorporates `0e812c1` and predecessors). All raw tasks, answers, outputs,
tokens, routes, states, expert identities, expert outputs, per-example features,
predictions, labels, split assignments, ambiguity annotations, and secret-linked
provenance remain private and uncommitted.

## Question

Does any **forward-only, observation-only** telemetry feature block add stable,
calibrated, verifier-labeled incremental completed-error prediction on the
pinned Agents-A1 35B AWQ runtime beyond frozen nuisance and router baselines?

This is a post-completion prediction and measurement study. It is not a
Jacobian Lens, causal attribution, semantic-expert study, ambiguity-prediction
study, safe-stopping rule, early-exit policy, routing intervention,
activation-steering result, or production authorization.

## Model and runtime

The intended runtime remains:

- checkpoint `cyankiwi/Agents-A1-AWQ-INT4`, revision
  `3e522d4e46438c782789b73c8ff4503e0edd037c`, architecture `qwen3_5_moe`
  (40 routed text layers, 256 experts, top-8);
- isolated vLLM 0.24.0 telemetry runtime with an observation-only worker
  extension;
- normal Agents-A1 GGUF serving restored and verified after every capture.

The launch amendment must bind the exact model files, tokenizer, code commit,
Python executable, package/runtime identity, environment, tensor-parallel
configuration, worker extension, sampling parameters, output caps, task-set
digest, seed schedule, and private schema. Missing original evidence blocks the
run; it may not be reconstructed after outcomes are known.

## Prediction time and unit of analysis

- The primary prediction unit is **one completed task row**, not one token,
  layer, expert, route, or generation step.
- Token-, layer-, expert-, and path-level measurements must be reduced to the
  exact preregistered task-level features before modeling. They may not be
  treated as independent observations.
- The predictor is evaluated only after generation completes but before the
  verifier verdict is exposed to any feature pipeline.
- If a task has repeated generations, paraphrases, difficulty variants, shared
  templates, or a common source instance, every related row must remain in one
  split group. No source lineage may cross train, calibration, validation, or
  held-out boundaries.

## Feature blocks

Blocks must remain separately measurable so any increment is attributable.
Exact layer sets, reductions, normalizations, missing-value encodings, and
feature names must be frozen in the launch amendment.

1. **Nuisance baseline**
   - prompt/completion/output length;
   - finish reason;
   - task family and preregistered band/difficulty;
   - output cap and truncation status;
   - latency and fixed route-count summaries;
   - exact preregistered token-logprob/confidence summaries;
   - **verifier family/type assigned from the task manifest before generation
     only**;
   - **pre-generation ambiguity/determinacy stratum**, only when assigned by the
     frozen task manifest and verifier contract before model inference under the
     rules below.

   The following are labels and are absolutely prohibited from every feature,
   preprocessing step, imputation rule, split decision, model input, and feature
   selection procedure: verifier verdict; pass/fail/undecided; verifier
   confidence; evidence hash; failure subtype; whether verification succeeded;
   distance from the known answer; correct answer; expected value; accepted
   values; post-verification category; manual review outcome; ambiguity inferred
   after generation; ambiguity inferred from the model output, telemetry,
   verifier result, or output-versus-gold comparison; or any quantity derived
   from output-versus-gold comparison. The ambiguous phrase “verifier category”
   from the original draft is superseded by the pre-generation verifier-family
   definition above.

2. **Router block**
   - router-logit and selected top-k weight summaries;
   - top-k margins;
   - per-layer route/load/count summaries;
   - preregistered layer-to-layer transition summaries.

3. **Routing-load block** (RouteScan-style; arXiv:2605.24817)
   - normalized per-expert load by layer;
   - active-expert fraction;
   - entropy and effective expert count;
   - coverage gap and concentration.

4. **Expert-contribution block** (arXiv:2604.02178)
   - selected-expert output norm after the expert transformation and before the
     routed weighted sum;
   - router weight and expert-output norm as separate features;
   - their preregistered product;
   - exact layer-level sums, maxima, dispersion, entropy, concentration,
     normalized contribution, change, and path summaries.

   The implementation must define precisely which tensor is called
   `expert_output`, whether shared-expert or residual terms are excluded, the
   norm dimension, accumulation precision, normalization denominator, epsilon,
   and treatment of dropped/padded/duplicated dispatch. An implementation-level
   ambiguity is a launch blocker.

5. **Hidden-state/control block**
   - exact preregistered residual-stream summaries;
   - router-visible and router-blind energy at a frozen layer set;
   - no raw hidden-state capture for feature discovery.

Every block must be summarized separately for prefill and autoregressive decode.
If exact phase separation is unavailable for a block, that block/phase is
unsupported and must be reported missing; phases may not be pooled after seeing
outcomes.

Only the minimum preregistered aggregate features may stream to private storage.
Full expert activation tensors must never be retained. Any expert IDs, route
paths, hidden summaries, per-task feature vectors, predictions, split labels,
ambiguity strata, or verifier labels remain private even when they are
lower-dimensional.

## Capture-feasibility and parity gates

The existing `jlens_vllm_telemetry` path captures router logits, top-k
weights/IDs, and dispatch identity through the `select_experts` and
`forward_modular` wrappers. The contribution block requires an on-device
reduction in the exact expert-output location defined above.

Before any scientific row, the launch amendment and implementation must pass a
non-outcome-bearing fixture/smoke protocol that freezes and verifies:

1. enabled-path and disabled-path output parity under the existing M36V envelope;
2. exact dispatch identity, including token, layer, selected expert, weight,
   padding, and duplicate-routing behavior;
3. exact prefill/decode attribution;
4. finite-value, dtype, accumulation, normalization, and missingness behavior;
5. memory, latency, disk-write, and telemetry-overhead ceilings;
6. proof that no full expert outputs or raw hidden states persist;
7. private schema validation and atomic/resumable write behavior;
8. cleanup and verified restoration of normal GGUF serving;
9. commit-safety and privacy scans.

A parity, provenance, resource, cleanup, or privacy failure blocks capture. A
smoke result cannot be counted as a scientific row or used to tune scientific
features.

## Labels and primary population

- Primary population: completed, nontruncated answers only.
- Primary label: verifier-backed completed error, encoded correct versus
  incorrect only after feature extraction is complete and sealed.
- Timeout and truncation prediction belongs to M36T and may not inflate M39.
- `undecided`, verifier errors, unsupported verifier cases, and missing labels
  require an exact preregistered exclusion or missingness rule. They may not be
  reassigned after inspecting telemetry.
- Candidate-only or heuristic verdicts may not silently become gold labels.

## Ambiguity and aleatoric-uncertainty control

Error-prediction signals can conflate reducible model error with irreducible
input ambiguity. M39 must not attribute that confounding to router, hidden-state,
or expert-contribution telemetry.

The launch amendment must choose and freeze exactly one primary policy before
any M39 outcome-bearing capture:

1. **Determinate-only primary population:** restrict the confirmatory primary
   population to tasks whose frozen authoring metadata and verifier contract
   establish a single determinate interpretation, while reporting all other
   strata separately as secondary or unsupported; or
2. **Stratified all-task primary population:** retain all eligible tasks, include
   the frozen pre-generation ambiguity/determinacy stratum in every nuisance
   baseline, enforce prospective information requirements within each required
   stratum, and preregister the exact pooled and stratified decision rules.

The stratum definition must be deterministic, versioned, and assigned before
model inference from task-construction metadata and the verifier contract only.
Permitted categories may include `single_determinate`,
`multiple_valid_or_underspecified`, `conflicting_evidence`, and `unknown`, but
the exact taxonomy and mapping must be frozen in the launch amendment. The
mapping may not inspect model outputs, telemetry, verifier outcomes, manual
post-generation review, or gold-comparison quantities. It may not expose answer
text, accepted values, or answer-set content to the feature pipeline.

`unknown` or mixed cases may not be silently folded into the most favorable
stratum after outcomes are observed. Predicted ambiguity derived from model
states, samples, semantic clusters, or outputs is outside the M39 confirmatory
feature set unless separately preregistered as a distinct study with its own
training/held-out boundary and multiplicity accounting.

Source-lineage grouping still controls every split. Split construction must also
preserve the frozen ambiguity policy, and the launch amendment must specify
minimum correct/incorrect counts for every stratum required by the primary
decision. Failure to meet those counts produces `underpowered/inconclusive`, not
post-hoc pooling or relaxation.

## Required launch amendment

Before authorization, a committed amendment must freeze all of the following
without access to M39 outcome-bearing telemetry:

1. exact task manifest, generator/source lineage, counts, family/band balance,
   inclusion/exclusion rules, and immutable task-set digest;
2. exact sampling parameters, caps, seed schedule, repetition policy, and
   expected row set;
3. immutable split-group construction, split seed, train/calibration/validation/
   held-out proportions, and locked held-out digest;
4. exact feature schema, formulas, layer set, phase treatment, normalization,
   precision, and missingness handling;
5. exact pre-generation ambiguity/determinacy taxonomy, mapping version, primary
   population policy, stratum handling, and stratum-specific information gates;
6. one primary endpoint; all secondary metrics and plots must be labeled
   secondary;
7. exact classifier definitions, hyperparameter grids, preprocessing,
   calibration method, nested-CV folds, and train-fold-only feature selection;
8. exact paired-resampling unit, bootstrap/permutation method, seed, replicate
   count, confidence level, and minimum effect-size threshold;
9. family-wise multiplicity control across all confirmatory blocks,
   comparisons, phases, ambiguity strata, and endpoints, or a fully specified
   hierarchical gate;
10. prospective power/minimum-information rules, including minimum correct and
    incorrect counts overall and within required split groups and ambiguity
    strata;
11. failure, interruption, resume, insufficient-class, unsupported-phase,
    ambiguity-unknown, and provenance-blocked outcomes;
12. private artifact locations, schemas, digests, retention rules, leakage
    audit, and public aggregate reporting template;
13. exact advance/stop decision table.

If any item remains qualitative, references “mirroring” an earlier study without
copying the exact rule, or is chosen after outcome-bearing telemetry exists,
M39 is not confirmatory and must not launch.

## Statistical boundary

- All preprocessing, imputation, normalization, residualization, calibration,
  feature selection, and hyperparameter selection occur inside training folds.
- Family/source-lineage grouping applies to every nested-CV and held-out split.
- The frozen ambiguity policy and required stratum representation apply to every
  nested-CV, calibration, validation, and held-out split.
- Confirmatory increment must be evaluated at the task-row level against the
  nuisance baseline and the nuisance-plus-router baseline.
- A lower confidence bound merely above zero is not sufficient unless the
  launch amendment also freezes a nontrivial minimum effect size and the
  multiplicity rule.
- Balanced accuracy, average precision, calibration, and any other metrics do
  not all become co-primary by being listed. Exactly one primary endpoint must
  be named before capture.
- No sealed or held-out outcomes may influence task selection, feature formulas,
  layer selection, phase pooling, ambiguity mapping, exclusions, classifier
  choice, or threshold selection.
- If prospective information or class-balance requirements are not met, report
  `underpowered/inconclusive`; do not pool families or ambiguity strata, alter
  labels, relax the effect threshold, or search extra feature variants after the
  fact.

## Confirmatory rule and stop conditions

Advance only if a prespecified forward-only block clears the complete frozen
decision table: parity, provenance, privacy, power, calibration, minimum-effect,
multiplicity-adjusted paired lower bound, nuisance increment, router-baseline
increment, frozen ambiguity-policy requirements, and locked-held-out
replication.

If no block clears, record the scoped negative and stop. A positive result
establishes only forward-only completed-error predictive increment on the exact
frozen population, runtime, and ambiguity policy.

Semantic expert labels remain exploratory and sealed. LLM-generated expert
labels may not be predictors, stopping rules, interventions, or scientific
claims without a separate preregistration and independent held-out validation.
RouteScan’s published privacy result does not establish privacy here; a
project-specific leakage and inversion audit remains mandatory.

## Boundary and sequence

M39 cannot establish a Jacobian Lens, causal mechanism, expert semantics,
ambiguity prediction, route quality, safe truncation, early exit, correction,
intervention, steering, or production value.

Only after a forward-only block clears every M39 gate may the program proceed to
separately preregistered full-Jacobian, reduced-target VJP, or bounded
finite-difference probes on a smaller comparable MoE or an official Agents-A1 4B
checkpoint if one is released. The later 35B backward step remains limited first
to a frozen one-sequence high-memory technical smoke with no scientific claim.
