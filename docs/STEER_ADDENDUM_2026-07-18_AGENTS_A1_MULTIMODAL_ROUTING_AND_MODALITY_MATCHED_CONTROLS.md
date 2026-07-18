# Steering Addendum — Agents-A1 Multimodal Routing and Modality-Matched Controls

Date: 2026-07-18

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `780b8d811aed4a7f7c41a76a2384f8a38854651f`

## Scope

This addendum applies to any future transfer, monitor, router-telemetry,
Jacobian-lens, hidden-state, semantic-workspace, early-exit, truncation,
retry, abstention, or intervention claim involving Agents-A1 or another
multimodal Mixture-of-Experts model.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload
retrieval, model execution, GPU execution, hidden-state capture, router
capture, Jacobian fitting, sealed scientific evaluation, or production use
is authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, cleanup, commit-safety, comparator, nuisance-control,
production-gating, and stop rule remains binding.

## New external evidence and narrow interpretation

Xu et al., “Seeing but Not Thinking: Routing Distraction in Multimodal
Mixture-of-Experts,” ACL 2026, DOI `10.18653/v1/2026.acl-long.1438`, reports
that semantically equivalent image and text inputs can produce materially
different routing behavior in multimodal MoE models. The reported divergence
is concentrated in middle layers, where image-conditioned routing can fail to
activate task-relevant reasoning experts despite adequate visual perception.
The authors report routing-guided intervention gains across three multimodal
MoE models and six benchmarks.

The binding interpretation is narrow:

1. Router telemetry in a multimodal MoE is not modality-invariant by default.
2. A routing-based correctness signal can be confounded by modality, visual
   tokenization, perception burden, encoder behavior, or modality-specific
   expert allocation.
3. Text-only evidence cannot establish transfer to image-conditioned agent
   trajectories.
4. Routing intervention evidence from other models does not authorize forced
   routing, repair, or production intervention in Agents-A1.

The paper does not establish universal causal expert localization, safe
routing intervention, target-blind correctness monitoring, Jacobian-lens
incremental value, or transfer to Agents-A1.

## Binding modality-matched evaluation requirements

Any future Agents-A1 scientific protocol must include semantically matched
cross-modal pairs whenever the task can be represented in more than one
modality.

At minimum, construct and freeze:

- text-only task instances;
- image-conditioned instances containing the same task information;
- image-plus-transcribed-text controls;
- text controls matched for token count and information content where
  feasible;
- perception-only controls that test extraction without downstream
  reasoning;
- reasoning-only controls supplied with a verified textual transcription of
  the visual facts.

The protocol must report within-pair differences for correctness, confidence,
hidden-state features, Jacobian-lens features, route paths, route margins,
expert concentration, router entropy, tool decisions, latency, and finish
reason.

A pooled result across modalities is inadmissible unless the within-modality
and matched-pair results are also reported.

## Required nuisance controls

In addition to existing family, answer, length, difficulty, tool-count,
latency, and finish-reason controls, future multimodal analyses must freeze and
control or stratify at least:

- modality and modality combination;
- visual token count;
- image resolution and aspect ratio;
- OCR requirement and OCR difficulty;
- object-count and scene-complexity proxies;
- vision-encoder or projector path;
- prompt-template differences introduced by multimodal serialization;
- placement of images relative to text and tool observations;
- presence of redundant textual descriptions;
- perception success versus downstream reasoning success;
- model refusal or malformed multimodal input handling.

No router, hidden-state, geometric, sparse-feature, transcoder, or
Jacobian-lens feature may be described as a correctness signal if it primarily
separates modality or perception burden.

## Failure taxonomy correction

Future Agents-A1 results must separate at least:

1. perception or extraction failure;
2. cross-modal alignment failure;
3. routing-distraction or expert-allocation failure;
4. completed reasoning error after correct perception;
5. tool-selection or tool-argument failure;
6. truncation or premature-stop failure;
7. malformed-output failure;
8. verifier or benchmark-label failure.

A correct textual transcription paired with an incorrect image-conditioned
answer is evidence of a modality-conditioned failure. It is not by itself
evidence that the router caused the failure.

Causal language requires an independently frozen intervention protocol with
negative controls, equal-compute route alternatives, right-to-wrong and
wrong-to-right accounting, degeneration checks, and cross-task replication.

## Comparator requirements

For multimodal Agents-A1 monitoring, evaluate separately:

- final logits and calibrated confidence;
- prompt-final and decision-point hidden-state probes;
- text-only and multimodal hidden-state deltas;
- simple route counts, router entropy, margins, and full cross-layer paths;
- modality-classification baselines using the same telemetry;
- perception-success baselines;
- metadata and tool/action baselines;
- Jacobian-lens readouts, only after exact derivative parity exists;
- sparse-feature or transcoder baselines when a frozen compatible feature
  model exists.

A routing or Jacobian-lens monitor must show sealed incremental value over a
modality classifier and a perception-success classifier. Failure to beat
those baselines blocks any claim of reasoning-error detection.

## Transfer boundary from Q35Q

Q35Q is a text-only derivative-admission and feasibility stage. A successful
Q35Q result may establish only that the admitted quantized text path supports
correct forward and activation-derivative computation under its frozen
protocol.

It cannot establish:

- multimodal derivative parity;
- vision-projector or cross-modal source closure;
- modality-invariant Jacobian geometry;
- multimodal router-telemetry validity;
- Agents-A1 monitor transfer;
- safe multimodal early exit, truncation, retry, abstention, routing, or
  steering.

Before Agents-A1-native scientific capture, separately admit the complete
multimodal runtime, processor, tokenizer, vision encoder, projector,
serialization path, routing outputs, and derivative path. Repeat forward,
VJP, JVP, and finite-difference parity for every instrumented modality path.

## Intervention boundary

Observation and intervention remain separate phases.

No routing-guided enhancement, expert forcing, route replacement, retry,
truncation, abstention, activation steering, or output rewriting may begin
until a target-blind detection result passes sealed, family-disjoint,
modality-matched evaluation with positive incremental value over all simpler
baselines.

Any later intervention must report:

- wrong-to-right transitions;
- right-to-wrong transitions;
- unchanged outcomes;
- malformed or degenerate outputs;
- latency and memory cost;
- tool-use regressions;
- modality-specific regressions;
- calibration and distribution-shift behavior;
- privacy and reconstruction risk from stored telemetry.

## Program status after this addendum

Established:

- multimodal MoE routing can differ materially between semantically matched
  image and text inputs in published experiments;
- modality is therefore a mandatory confound and transfer boundary for future
  Agents-A1 work;
- text-only Q35Q evidence cannot directly authorize multimodal claims.

Unproven:

- that Agents-A1 exhibits the same routing-distraction mechanism;
- that route divergence predicts correctness within modality;
- that Jacobian-lens features add value beyond modality, perception,
  hidden-state, confidence, metadata, and route-path baselines;
- that any routing intervention is safe or useful in Agents-A1;
- that multimodal early exit, truncation, retry, abstention, or steering is
  production-ready.

The active engineering blocker remains production-path upstream/runtime
provenance composition as defined in `steer.md`. This addendum changes future
scientific controls only and does not authorize advancement past the current
gate.
