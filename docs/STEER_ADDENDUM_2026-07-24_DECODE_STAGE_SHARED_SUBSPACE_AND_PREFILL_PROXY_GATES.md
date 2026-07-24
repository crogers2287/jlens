# Steering Addendum — Decode-Stage Shared-Subspace and Prefill-Proxy Gates

Date: 2026-07-24

Status: binding future-protocol correction; no current execution authorization

Parent remote head: `32bcd97b9d286baf49be1c517de46b54691298b5`

## Scope

This addendum applies to every future claim involving decode-time hidden states,
prefill hidden states, task-general or shared subspaces, semantic-workspace
monitoring, activation steering, projection removal, patching, direct or logit
lenses, sparse features, transcoders, router telemetry, directional JVPs,
Jacobian Lens, early exit, truncation, retry, escalation, or Agents-A1.

It does not change the active Q35Q milestone. Q35Q remains
`q35q_artifact_admission_blocked`. No weight staging, tensor-payload retrieval,
model execution, GPU execution, hidden-state capture, router capture, JVP, VJP,
Jacobian fitting, sealed scientific evaluation, intervention, or production use
is authorized by this document.

Every privacy, sealed-data, verifier, provenance, exact-set, exact-gradient,
parity, resource, cleanup, commit-safety, comparator, nuisance-control,
multiplicity, production-gating, and stop rule remains binding.

GitHub currently reports this repository as public. This document contains only
aggregate public-source program-control information. It does not authorize
committing prompts, outputs, token IDs, per-task predictions, verifier labels,
hidden states, router arrays, expert traces, Jacobians, gradients, model
weights, tensor payloads, caches, credentials, local paths, or private logs.

## New external evidence and narrow interpretation

Shao et al., “DecodeShare: Tracing the Shared Subspace of LLM Decode-Time
Decisions,” arXiv `2607.20469v1`, report a compact task-general subspace in
KV-cached decode-time hidden states and test its causal role by removing the
estimated subspace only during decoding.

The inspected public implementation is `Zishan-Shao/decodeshare` at immutable
commit `89ed6a36603d81d024b0bd5438048a93d3fff2ac`. The released estimator uses:

- task-balanced calibration states;
- task-centered pooled PCA/SVD;
- no feature-wise standardization before PCA; and
- decode-time projection removal in the raw hidden-state coordinate system.

The repository’s paper-aligned rerun summaries report:

1. On Qwen2.5-7B-Instruct, layer 10, nine tasks, 16 calibration prompts per
   task, and 32 decode calibration tokens per prompt, 161 fully shared
   components were recovered from a 920-dimensional cross-task PCA space. The
   reported permutation-null p-value is `0.001996`; the task-scramble-null
   p-value is `0.047619`.
2. In a leave-one-task-out QASC evaluation with 512 examples, baseline accuracy
   was `82.0%`, decode-only removal of the shared basis reduced accuracy to
   `59.8%`, and a variance-matched random-basis removal produced `81.8%`.
3. In the released prefill/decode geometry check, the full-basis mean cosine was
   `0.314`, the dimension-matched mean cosine was `0.133`, decode-basis energy
   on decode states was `0.749`, and prefill-basis energy on decode states was
   `0.074`.

The evidence materially changes the future claim boundary and minimum
comparator set:

1. Prefill and decode representations are not interchangeable measurement
   stages.
2. A prefill-derived basis, score, steering proxy, or validation result cannot
   be assumed to transfer to KV-cached decoding.
3. A task-general decode subspace can be causally important without being a
   correctness, safety, planning, intent, or error subspace.
4. Projection removal is an in-path intervention and cannot be represented as
   passive monitoring.
5. Decode-stage validation is a mandatory comparator for any monitor or
   steering policy intended to operate during decoding.
6. The reported evidence is from dense models and does not establish MoE,
   Qwen3.5/Qwen3.6, Agents-A1, router, quantized-runtime, or Jacobian-specific
   transfer.

## Required object separation

Every compatible study must bind these objects separately:

1. **Prefill state population:** hidden states produced while consuming the
   prompt or context before autoregressive decode.
2. **Decode state population:** hidden states produced at prospectively frozen
   decode positions under an exact cache and generation policy.
3. **Serving state:** KV or recurrent state, attention mask, cache indices,
   batching, topology, precision, quantization, kernels, and scheduler state.
4. **Subspace estimator:** centering, balancing, normalization, PCA/SVD or other
   fitting rule, rank-selection rule, seed, and numerical implementation.
5. **Estimated basis:** the exact layer-, stage-, model-, task-, runtime-, and
   checkpoint-specific basis artifact.
6. **Readout or score:** any projection energy, coordinate, classifier,
   direct/logit-lens output, route statistic, sparse feature, transcoder output,
   JVP, or Jacobian-derived score.
7. **Intervention:** projection removal, patchback, directional addition,
   activation replacement, route forcing, early exit, retry, or truncation.
8. **Validation proxy:** prefill metric, decode metric, local logit change,
   steering score, verifier score, or objective task outcome.
9. **Objective outcome:** the independently frozen correctness, safety,
   artifact, tool, or environment endpoint.
10. **Decision policy:** any threshold, ranking, vector selection, intervention,
    escalation, or production rule.

Evidence about one object does not admit another. In particular, a stable basis
does not establish a valid score; a valid score does not establish a safe
intervention; and a causal intervention effect does not establish objective
monitor value.

## Stage-identity gate

Every hidden-state or subspace result must freeze the exact computational stage.
At minimum record:

- prompt-completion boundary;
- prefill token positions and pooling rule;
- first decode input and first generated token boundary;
- every sampled or evaluated decode position;
- whether the state is before or after attention, MoE, residual addition,
  normalization, or output readout;
- whether the forward pass consumes prompt tokens, generated tokens, tool
  results, retrieved context, verifier feedback, or compacted context;
- cache initialization, cache reuse, cache mutation, prefix-cache reuse,
  paging, eviction, retry, resume, and recomputation behavior;
- decoding algorithm, temperature, top-p/top-k, beam or speculative policy,
  stopping rules, and token budget;
- model, checkpoint, tokenizer, template, precision, quantization, runtime,
  kernels, hardware topology, batch composition, and serving scheduler.

The terms `prefill`, `decode`, `generation`, `last token`, and `current state`
are insufficient without these identities.

Scores or bases from different stages may not be pooled, averaged, aligned, or
used as substitutes unless a prospective transfer test is passed.

## Stage-matched estimation and validation gate

A monitor or steering policy intended for decode-time use must be estimated,
calibrated, and validated on decode-time states under the intended cache and
serving semantics.

Mandatory comparisons, when technically compatible, include:

1. prefill-derived basis evaluated on prefill states;
2. prefill-derived basis evaluated on decode states;
3. decode-derived basis evaluated on decode states;
4. decode-derived basis evaluated on prefill states;
5. a dimension-matched random basis;
6. an energy- or variance-matched random basis;
7. a task-scrambled or label-scrambled basis;
8. a nonshared or task-specific basis;
9. raw hidden-state and matched hidden-state-difference baselines;
10. direct/logit-lens and confidence baselines at the same stage;
11. external deterministic checks and objective verifiers;
12. route, sparse-feature, transcoder, directional-JVP, and Jacobian comparators
    only after their own admission.

A prefill proxy may support decode deployment only if its stage-transfer rule is
frozen before sealed evaluation and passes held-out task-family, position,
length, cache, runtime, and serving-state tests.

Failure of prefill-to-decode transfer is not evidence that the concept is absent
from the model. It establishes that the chosen prefill instrument is not
validated for the decode condition.

## Subspace-estimator identity and leakage gate

Every subspace claim must freeze:

- task balancing and sample weighting;
- per-task, global, or no centering;
- feature-wise standardization or its explicit absence;
- token and sequence pooling;
- PCA, SVD, CCA, regression, dictionary, or alternative estimator;
- rank-selection criterion and complete rank curve;
- numerical precision, solver, tolerance, seed, and deterministic settings;
- layer and position selection procedure;
- task, family, prompt, trajectory, and checkpoint splits;
- fitting, rank selection, calibration, intervention selection, certification,
  and sealed evaluation populations.

The held-out task or task family may not contribute states to a basis used to
claim cross-task causal value on that held-out population. Future tokens,
completed outputs, verifier results, objective outcomes, and post-intervention
states are excluded from prospective monitor fitting unless the analysis is
explicitly retrospective.

Same-prompt, paraphrase-family, repository, base-commit, trajectory, user,
environment, and benchmark-template clusters must remain together across
splits where shared structure would otherwise leak.

## Sharedness and null-model gate

A `shared`, `task-general`, `global`, or `workspace` label requires prospective
null models and stability analysis.

Required controls include:

- permutation and task-scramble nulls;
- task-balanced versus unbalanced fits;
- leave-one-task and leave-one-family-out fits;
- rank and layer sweeps with multiplicity correction;
- seed and sample-size stability;
- prompt-format, answer-label, language, length, and token-position controls;
- lexical, numeric, punctuation, answer-scaffold, and newline controls;
- model-, checkpoint-, runtime-, and quantization-specific replication;
- comparison against generic high-variance and output-aligned directions;
- comparison against task difficulty, confidence, trajectory phase, and context
  pressure.

A direction shared across tasks may encode generic decode mechanics, output
formatting, token statistics, confidence, or autoregressive control rather than
a semantic workspace.

The strongest allowed label must match the evidence. `Cross-task decode
subspace` is admissible when supported. `Global workspace`, `reasoning bus`,
`intent channel`, `correctness channel`, or `safety channel` requires separate
prospective evidence.

## Causal-intervention boundary

Projection removal, activation replacement, patchback, directional addition,
and steering are in-path interventions.

Every intervention study must report:

- the exact intervention point and coordinate system;
- projection rank, norm, energy, and per-token perturbation magnitude;
- matched random, nonshared, prefill, decode, and task-specific interventions;
- full-population objective outcomes and per-example outcome flips;
- correct-to-incorrect and incorrect-to-correct transitions;
- downstream hidden-state, logit, cache, route, and expert-path divergence;
- future-token and full-sequence divergence;
- tool-call, artifact, verifier, and environment effects where applicable;
- off-target task-family and capability regressions;
- latency, memory, throughput, retries, fallback, and tail costs;
- deterministic replay and fail-closed behavior when the basis or stage identity
  cannot be certified.

A large behavioral drop after shared-basis removal establishes causal dependence
on the removed channel under that intervention. It does not establish that the
basis is unique, minimal, semantically pure, sufficient, or naturally used as a
monitorable correctness signal.

Patchback can strengthen localization but does not by itself establish semantic
identity, objective correctness, or safe control.

## Steering-vector overlap and selection gate

Candidate steering vectors can overlap a task-general decode channel. A vector
selected using a prefill proxy may therefore rank differently under decode-time
behavior.

Future steering studies must decompose and compare, where feasible:

1. the original steering vector;
2. its projection onto the admitted decode-shared basis;
3. its component orthogonal to that basis;
4. its projection onto a prefill-derived basis;
5. random and norm-matched vectors;
6. task-specific and nonshared components.

Vector selection, scale selection, layer selection, and stopping rules must be
frozen outside sealed evaluation. Report held-out decode utility, worst-group
utility, sign flips, rank correlation, regret, off-target effects, and complete
cost.

A decode-aligned vector ranking is an intervention-selection result. It is not
evidence that the selected direction predicts objective correctness or that a
shared subspace should be removed in production.

## Semantic-workspace claim boundary

A compact, cross-task, causally important decode subspace is compatible with
several explanations:

- generic autoregressive decision machinery;
- shared output formatting or answer scaffolding;
- confidence or uncertainty processing;
- token-selection control;
- task-general reasoning operations;
- a limited broadcast-like workspace;
- a mixture of these factors.

The evidence does not by itself establish:

- conscious access or self-awareness;
- a complete global workspace;
- explicit plans or intentions;
- hidden knowledge of objective correctness;
- error awareness;
- evaluator awareness or reward seeking;
- causal sufficiency for reasoning;
- safe early exit, retry, repair, or steering.

Semantic labels require prospectively frozen target concepts, positive controls,
matched counterfactuals, nuisance controls, held-out task families, and
incremental objective-outcome value over cheaper observables.

## MoE and route-telemetry boundary

Hidden-state sharedness and router sharedness are different objects.

For MoEs, future studies must separately capture and compare:

- prefill and decode hidden-state bases;
- prefill and decode router logits and selected experts;
- parent-route and cross-layer expert-path state;
- route occupancy, load, entropy, margin, and transition features;
- hidden-state changes with route held fixed where feasible;
- route changes with matched hidden-state controls where feasible;
- dense-sibling representations under matched tasks;
- serving topology, expert placement, batching, cache, and communication state.

A shared hidden-state channel does not establish a shared expert path. A shared
route pattern does not establish a shared semantic channel. Route or Jacobian
features must add sealed objective-outcome value beyond stage-matched hidden
states, direct readouts, confidence, trajectory features, deterministic checks,
and external verifiers.

## Agents-A1 scaling consequence

After every existing Q35Q gate passes, the minimum Agents-A1 sequence is:

1. Freeze task contracts, objective outcomes, irreversible-action boundaries,
   event clocks, cache semantics, tool schemas, verifier rules, and serving
   conditions.
2. Separately admit Agents-A1-4B artifact, processor, runtime, forward path, and
   derivative behavior.
3. Establish deterministic checks, logits, confidence, self-judgement, visible
   trajectory features, and simple hidden-state baselines on Agents-A1-4B.
4. Capture prefill and decode hidden states under stage-matched KV-cache and tool
   event semantics.
5. Compare prefill-derived and decode-derived task-general bases, raw-state
   differences, direct/logit lenses, random controls, and held-out-task
   interventions on Agents-A1-4B.
6. Treat any shared-subspace result as dense same-family representation evidence,
   not MoE evidence or objective correctness awareness.
7. Separately admit Agents-A1-35B hidden-state, router, expert-path, cache,
   multimodal, quantized, topology, and serving capture.
8. Repeat prefill/decode basis estimation and transfer tests rather than carrying
   over ranks, layers, thresholds, or coordinates from Agents-A1-4B.
9. Establish executed-route, ancestry, occupancy, semantic, and serving-state
   baselines at both prefill and decode stages.
10. Require route features to add sealed objective-outcome value beyond the
    stage-matched dense-sibling, hidden-state, confidence, trajectory,
    deterministic-check, and verifier stack.
11. Add sparse-feature or transcoder comparators under the same stage-identity
    and held-out-task rules.
12. Add Agents-A1-35B Jacobian Lens only after exact derivative parity and sealed
    incremental value over every cheaper stage-matched comparator.
13. Keep projection removal, steering, retry, abort, truncation, early exit,
    forced routing, quarantine, and production control under separate gates.

This adds a decode-stage shared-subspace comparator before route and Jacobian
claims. It does not authorize any current Agents-A1 execution.

## Active blocker and execution order

The active blocker remains production-path upstream/runtime provenance
composition:

1. bind the live import to its owning installed distribution and `RECORD`;
2. derive complete live-object source closure for dispatch, converters, nested
   operations, model/configuration classes, and loader objects;
3. reject shadow packages, editable installs, monkeypatches, forged identities,
   incomplete closure, incorrect ownership, and unadmitted loaders in a clean
   subprocess;
4. invoke and bind the actual GPTQModel/Defuser loader entry point;
5. freeze the exact immutable GPTQ runtime tuple;
6. pass the complete adversarial integration conjunction; and
7. emit only the permitted aggregate result.

After that remain packer-independent fixture validation, strict packed-tensor
consumption and expert ordering, forward/VJP/JVP/finite-difference parity, Q35Q
Phase-0 admission, weight staging, and a separately authorized GPU transition.

## Established by this correction

- Prefill and decode hidden-state subspaces are bindingly separate scientific
  objects.
- Decode-time deployment requires stage-matched estimation and validation.
- Prefill-to-decode transfer is an empirical claim, not an assumption.
- Decode-shared subspaces are mandatory future comparators for semantic-workspace,
  steering, route, and Jacobian claims where technically compatible.
- Cross-task sharedness, causal importance, semantic identity, objective monitor
  value, and policy utility are bindingly separate.
- Existing privacy, sealed-data, verifier, provenance, derivative, intervention,
  and production rules remain intact.
- Q35Q remains blocked.

## Not established

- Independent reproduction of DecodeShare’s complete GPU experiments.
- Unique or complete semantic-workspace identity of the reported subspace.
- Objective-error, safety, planning, or intent prediction from the shared basis.
- Transfer to Qwen3.5/Qwen3.6 MoE, quantized runtimes, tool-using agents, or either
  Agents-A1 checkpoint.
- Stage-invariant layer, rank, coordinate, or threshold transfer.
- Incremental router, sparse-feature, transcoder, directional-JVP, or
  Jacobian-Lens value after stage-matched hidden-state comparators.
- Safe projection removal, steering, early exit, retry, repair, truncation,
  routing intervention, or production deployment.
