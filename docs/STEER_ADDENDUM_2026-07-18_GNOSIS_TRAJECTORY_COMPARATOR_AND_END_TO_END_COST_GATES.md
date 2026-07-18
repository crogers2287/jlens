# Steering Addendum — Gnosis Trajectory Comparator and End-to-End Cost Gates

Date: 2026-07-18

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `e4f0ff57f8dfae124d3aa30cdd7bacd150e73a4a`

## Scope

This addendum applies to any future hidden-state, attention, router-telemetry,
Jacobian-lens, semantic-workspace, correctness, early-error, early-exit,
truncation, retry, abstention, escalation, or Agents-A1 monitoring claim.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload retrieval,
model execution, GPU execution, hidden-state capture, attention capture, router
capture, Jacobian fitting, sealed scientific evaluation, or production use is
authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-gradient, parity,
resource, cleanup, commit-safety, comparator, nuisance-control,
production-gating, and stop rule remains binding.

## New external evidence and narrow interpretation

Ghasemabadi and Niu, “Can LLMs Predict Their Own Failures? Self-Awareness via
Internal Circuits,” arXiv `2512.20578v2`, introduce Gnosis, a roughly five
million parameter correctness head over frozen-model trajectory signals. The
reported design compresses final-layer hidden states and attention maps into
fixed-budget descriptors and reports strong correctness discrimination across
math reasoning, TriviaQA, and MMLU-Pro on Qwen3 and GPT-OSS backbones from 1.7B
to 20B parameters. The paper also reports sibling-model transfer and
zero-shot scoring of partial generations, with near-peak performance after
roughly forty percent of the generated trajectory in two evaluated domains.

The associated public implementation was inspected at immutable commit
`1417f2103174d5ab00ed1fd48c8aa562365103ab`.

The binding interpretation is narrow:

1. Full-trajectory hidden-state plus attention summaries are a serious future
   correctness-monitor comparator and cannot be omitted from an incremental
   Jacobian-lens or router-telemetry claim when a compatible frozen
   implementation can be constructed.
2. The published result does not establish that the monitor is online,
   single-pass, causally available before a stopping decision, or negligible
   in end-to-end serving cost.
3. The result does not establish safe early exit, truncation, escalation, or
   abstention.
4. Attention maps are not MoE router telemetry. “Attention routing” and expert
   routing must remain separate feature families and causal hypotheses.
5. The reported transfer is within related model families and is explicitly
   sensitive to generation style. It does not establish transfer to Agents-A1.

## Public-code cost and timing correction

The inspected public demo first generates an answer and then performs a
separate full scoring forward over `prompt + answer`. That scoring call uses
`use_cache=False`, requests attentions, obtains the final hidden state, applies
the language-model head over the sequence, constructs token-probability
features, and only then invokes the Gnosis correctness head.

The public batch-evaluation script follows the same pattern. Its timing block
labelled `Stop Mechanism` begins after the backbone forward, attention
extraction, language-model head, and token-probability construction. Therefore
that timer measures the auxiliary head, not the complete monitoring path.

Accordingly, no repository protocol may cite the reported approximately 25 ms
head latency as end-to-end monitor overhead. A fixed-size auxiliary descriptor
does not make the acquisition of its source traces independent of sequence
length, memory traffic, attention implementation, or serving architecture.

## Binding end-to-end cost accounting

Every future monitor comparison must report costs for the complete executable
path, not only the final classifier or descriptor encoder.

At minimum, measure separately and jointly:

- baseline generation latency and throughput with no instrumentation;
- hidden-state extraction and retention;
- attention-summary or attention-map extraction;
- router-logit, route-path, and expert-statistic extraction;
- any additional full or partial backbone forward;
- cache disabling, replay, or prefix recomputation;
- language-model-head and token-probability construction;
- descriptor compression and monitor-head execution;
- device memory, host memory, transfer volume, and interconnect cost;
- persistent storage volume and privacy exposure, if any telemetry is stored;
- synchronization, batching, prefix-cache, speculative-decoding, and
  distributed-serving regressions.

Report both absolute cost and delta from the identical uninstrumented serving
path. A monitor is not “negligible,” “constant-cost,” or “production-ready”
unless the complete online path supports that claim under the frozen target
runtime and workload.

## Feature-time and early-detection gate

Feature time, label time, decision time, and intervention time must remain
explicitly separate.

An early-detection claim is admissible only when all monitor inputs are
available at or before the stated decision boundary without access to future
tokens, completed-answer structure, final parse status, verifier output, or a
post-hoc full-sequence replay.

For every prefix checkpoint:

- freeze both absolute token checkpoints and fractional checkpoints;
- evaluate the same underlying trajectories at every checkpoint;
- report response-length, prompt-length, task-family, difficulty, answer-format,
  and finish-reason controls;
- prevent future-token leakage through pooling, padding, masks, caches,
  serialization, or precomputed full-trajectory tensors;
- distinguish a streaming one-pass monitor from a second-pass prefix replay;
- include an equal-compute baseline permitted the same replay or extra forward;
- report AUROC, error-positive AUPR, Brier skill, calibration, coverage, and
  selective risk at each checkpoint;
- report right-to-wrong, wrong-to-right, unchanged, malformed, refusal, and
  premature-stop outcomes for any later control policy.

Performance at forty percent of each realized final response can be reported as
retrospective fractional-prefix evidence. It is not by itself an online stopping
rule because the final response length is unknown at the decision boundary.

## Parsed-answer and abstention correction

The Gnosis paper and public evaluation path report primary correctness metrics
on generations with valid, parsable answers while filtering no-answer,
refusal, empty, or otherwise unparsed cases from that binary evaluation.

That convention is inadmissible as the sole primary evaluation for this
program. Future monitoring must preserve at least these outcome classes:

1. correct parsed answer;
2. incorrect parsed answer;
3. valid abstention or explicit uncertainty;
4. invalid refusal;
5. empty or truncated output;
6. malformed or unparsable output;
7. tool-call or argument failure;
8. verifier or benchmark-label failure.

Report both conditional metrics on parsed answers and unconditional metrics on
the complete preregistered population. Excluding failures that a production
monitor must handle is selection bias and cannot support a safe early-exit,
abstention, or escalation claim.

## Required trajectory-monitor comparators

After Q35Q derivative parity and before any Jacobian-lens superiority claim,
include separately frozen variants of:

- final logits, entropy, mean token probability, and calibrated confidence;
- prompt-final and decision-point hidden-state probes;
- pooled full-trajectory hidden-state baselines;
- a fixed-budget temporal hidden-state encoder;
- attention-statistic and fixed-budget attention-summary baselines when the
  target runtime can expose them without violating cost or privacy gates;
- a Gnosis-style hidden plus attention trajectory head when technically
  compatible;
- metadata and tool/action baselines;
- router counts, entropy, margins, and cross-layer route paths for MoE models;
- sparse-feature or transcoder baselines when a frozen compatible feature
  model exists;
- Jacobian-lens readouts only after exact derivative parity passes.

Ablate hidden-only, attention-only, confidence-only, router-only, and fused
variants. Incremental value must be measured on a sealed family-disjoint outer
test, not inferred from separate papers or unmatched datasets.

## Attention and MoE-router separation

Do not label transformer attention maps as router telemetry. For MoE models,
record and analyze these as separate objects:

- self-attention or cross-attention summaries;
- expert-router logits or scores;
- selected expert IDs and ordering;
- route margins and entropy;
- cross-layer expert paths;
- expert output norms or other admitted expert-activation summaries.

Any fused attention-plus-router monitor must show incremental value over each
component separately. An attention signal cannot establish expert
misallocation, and an expert-route signal cannot establish an attention
failure without a separately frozen causal protocol.

## Agents-A1 scaling priority

A direct full-attention-map monitor is not the default path for Agents-A1.
Long-context, multimodal, distributed execution makes all-layer, all-head
attention capture and replay a potentially dominant memory, bandwidth, and
privacy cost even when the downstream descriptor is fixed-size.

The priority order for Agents-A1-native observation remains:

1. tool/action and finish metadata;
2. calibrated output confidence and final-logit summaries;
3. selected decision-boundary hidden-state projections;
4. compact online router/path summaries and route margins;
5. streaming fixed-budget trajectory aggregates that do not require replay;
6. Jacobian-lens features only after exact derivative parity and bounded
   capture cost;
7. full attention maps or full attribution graphs only under a separate
   resource, privacy, and scaling amendment.

A Gnosis-style trajectory head is a comparator architecture, not an instruction
to store raw full trajectories. Any Agents-A1 implementation must aggregate
online, retain only preregistered bounded summaries, and pass reconstruction and
privacy-risk tests before sealed capture.

## Transfer boundary

Cross-scale or sibling transfer must freeze and report:

- backbone family and exact model identities;
- hidden width, layer count, attention-head structure, and feature alignment;
- tokenizer and chat-template identity;
- thinking versus instruct generation mode;
- response-format and reasoning-length distributions;
- task-family overlap and contamination checks;
- calibration transfer without target-test retuning.

A head trained on a small related Qwen model does not establish transfer to a
large multimodal Agents-A1 MoE. Unavailable compatible transfer evidence must
be reported as unproven, not treated as negative or positive evidence for
Jacobian Lens.

## Program status after this addendum

Established:

- a public fixed-budget hidden-state plus attention correctness head has shown
  strong retrospective detection results on several 1.7B–20B backbones;
- the public implementation performs a separate scoring forward over the
  prompt-completion sequence in its demonstrated path;
- its reported head timer excludes the backbone scoring forward and therefore
  is not end-to-end monitor latency;
- parsed-only evaluation excludes outcome classes required for abstention and
  production-control claims;
- trajectory hidden-state and attention summaries are mandatory future
  comparators when technically compatible.

Unproven:

- online single-pass detection at the claimed cost;
- safe early termination or escalation;
- end-to-end latency and memory advantage over simpler in-path baselines;
- transfer to unrelated architectures, multimodal paths, or Agents-A1;
- incremental Jacobian-lens value over a Gnosis-style trajectory monitor;
- incremental router-telemetry value over hidden, attention, confidence, and
  metadata baselines;
- production utility, privacy safety, or causal error localization.

The active engineering blocker remains production-path upstream/runtime
provenance composition as defined in `steer.md`. This addendum changes future
scientific comparator, timing, cost, and selection-bias controls only and does
not authorize advancement past the current gate.
