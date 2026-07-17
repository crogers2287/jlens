# Steering addendum — transcoder comparator and feature-selection leakage gates

Date: 2026-07-17

This addendum is binding for any future semantic-workspace, hidden-state,
Jacobian-lens, sparse-feature, transcoder, deception, correctness, truncation,
retry, abstention, routing, or Agents-A1 monitoring experiment. It does not
change the active Q35Q production-path provenance milestone, authorize weights
or GPUs, reopen M38E, or weaken any privacy, sealed-data, verifier, parity,
resource, or production gate.

## New primary-source evidence

The public preprint `Transcoders for Investigating Deception in Language
Models` (arXiv:2607.14791, submitted 2026-07-16) applies pretrained per-layer
transcoders to Qwen3-4B and uses `decoderesearch/circuit-tracer` to construct
attribution graphs and intervene on selected features.

Public implementation inspected at immutable repository head:

- repository: `decoderesearch/circuit-tracer`
- commit: `eb0e0f9347a521d7634b7ccbe95756f46f1df2a1`

The implementation is a credible future comparator because it supports
feature-level attribution graphs, explicit error nodes, output-logit
attribution, and feature intervention. Public pretrained Qwen3 transcoders are
available only for substantially smaller dense models, including Qwen3 0.6B,
1.7B, 4B, 8B, and 14B. This does not establish an Agents-A1-scale transcoder,
MoE-wide feature dictionary, correctness monitor, or production intervention.

## Binding interpretation of the preprint

The paper is exploratory mechanism evidence, not a sealed detector result.

1. The experiment uses one model family and one 4B model.
2. The prompt set contains 100 templated secret-withholding examples.
3. Feature identification is manual and begins from deception-related seed
   tokens and concepts.
4. Features are retained partly because steering them changes outputs.
5. The top recurring features are then evaluated on the same 100-prompt set.
6. No family-disjoint, model-disjoint, or independently sealed outer test is
   reported.
7. The fixed steering coefficient is not tuned or validated across models.
8. The paper acknowledges dependence on one pretrained transcoder set and
   human feature-selection bias.

Therefore the result may support the narrow claim that selected transcoder
features and feature circuits correlate with and can influence the demonstrated
secret-withholding behavior in Qwen3-4B. It does not establish target-blind
deception detection, completed-error prediction, general correctness
awareness, cross-family transfer, Agents-A1 transfer, safe intervention, or
incremental value over simpler activation probes.

## Required comparator expansion

Any future monitor benchmark must include the following separately:

1. final-logit and output-confidence baselines;
2. prompt-final and decision-point hidden-state probes;
3. raw-layer or logit-lens readouts;
4. Jacobian-lens readouts;
5. sparse-autoencoder or transcoder feature activations when a frozen,
   independently admitted feature model exists;
6. transcoder attribution or circuit summaries when computable without sealed
   label access;
7. router/path telemetry and metadata baselines;
8. combinations fitted only on the training partition.

A Jacobian-lens or router-telemetry claim requires positive sealed incremental
value over sparse-feature/transcoder baselines as well as the simpler baselines
already required by prior steering.

Absence of a scalable transcoder for Agents-A1 must be reported as a comparator
availability limitation, not treated as evidence that Jacobian-lens features
are superior.

## Feature-discovery and selection-leakage gate

All feature discovery must be confined to the training partition.

The following must be frozen before any validation or sealed test labels are
opened:

- transcoder or sparse-feature model identity and training corpus;
- feature dictionary and feature explanations;
- seed tokens, seed concepts, graph targets, attribution thresholds, and graph
  pruning rules;
- feature-selection algorithm and retained feature IDs;
- aggregation windows, layer ranges, circuit summaries, and monitor threshold;
- any steering direction, sign, coefficient, or intervention schedule.

It is prohibited to identify features on an example, validate them by changing
that example's output, and then count performance on the same example as
held-out evidence. Steering-based feature validation and detector evaluation
must use disjoint data, with a separately sealed outer test.

Manual semantic inspection is permitted only on the training partition and
must be recorded as target-conditioned exploratory analysis. A manually named
or seed-token-derived feature set may not be reported as target-blind
detection.

## Attribution and causal-claim separation

Attribution-graph edges, transcoder reconstruction, and feature occurrence do
not by themselves prove a causal mechanism. Feature steering establishes only
that an intervention changed model behavior under the tested intervention.

Any later causal claim must separately measure:

- reconstruction and replacement error;
- feature and circuit stability across prompts, seeds, and model families;
- matched random-feature and magnitude-matched direction controls;
- downstream output quality and degeneration;
- wrong-to-right and right-to-wrong transitions;
- calibration, latency, and privacy effects;
- robustness to paraphrase, lexical controls, and task-family shift.

A changed output string, suppression of a literal token, or successful behavior
flip is not correctness, safety, repair, or production utility.

## Agents-A1 scaling interpretation

Transcoders are a later comparator track, not a bypass around Q35Q admission or
derivative parity. The technically credible order remains:

`runtime provenance -> strict synthetic GPTQ loading -> quantized forward and
activation-gradient parity -> Q35Q fitting -> sealed detection benchmark ->
small-model sparse-feature/transcoder comparator -> Agents-A1-native telemetry`

For Agents-A1, prioritize low-overhead observational summaries that can be
captured at frozen agent decision boundaries: route paths, route margins,
selected hidden-state projections, tool/action metadata, and verifier-blind
trajectory summaries. Full-model transcoders or attribution graphs may be
investigated only after their runtime, storage, privacy, and feature-training
costs are independently bounded.

## Program status

The active milestone remains production-path upstream/runtime provenance
composition for Q35Q. The aggregate status remains:

`q35q_artifact_admission_blocked`

No weight staging, model execution, GPU execution, hidden-state capture, router
capture, Jacobian fitting, transcoder fitting, sealed scientific evaluation, or
production use is authorized by this addendum.
