# STEER ADDENDUM — Frozen-controller assignment replay and actual-execution gates

Date: 2026-07-30

Parent remote head: `2f33b6612f163ebe8f01b59baf9f1fce0c2c1562`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no weight retrieval, model execution, GPU use, hidden-state or
router capture, Jacobian fitting, sealed evaluation, training run, policy
update, control action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains production-path upstream provenance
composition followed by exact-target-runtime Q35Q loader and derivative
admission. This addendum changes future controller, router, depth-routing, and
conditional-execution claim requirements; it does not displace that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control
and public-source engineering material may be committed. Prompts, outputs,
token identities, per-example predictions, verifier labels, hidden states,
controller tensors, router logits, expert paths, execution masks, cache state,
Jacobian data, gradients, model weights, credentials, host paths, private
runtime traces, and sealed outcomes remain prohibited.

## Triggering primary evidence

Li, Shang, and Luo, `Dynamic Parameterization Is Not Dynamic Inference`, arXiv
`2607.26192v1`, submitted 2026-07-28, separates three claims that are commonly
collapsed:

1. controller coefficients vary with the input;
2. the frozen model function depends on how those coefficients are assigned to
   inputs, tokens, positions, layers, or streams; and
3. the runtime conditionally omits computation.

The paper introduces Frozen-Controller Auditing (FCA): cache the complete
controller-coefficient tensor along an unperturbed trajectory, disable the
controller, and replay the frozen model with cross-input reassignment, token
shuffling, and static profiles estimated on an independent calibration set.
Because the coefficients are cached before intervention, replay effects measure
assignment dependence without controller feedback from perturbed hidden states.

The reported evidence is deliberately dissociative:

- across seven independently trained 76M FeatureGate Transformers and three
  504M models, static layerwise profiles retain 98.70% and 99.43% of the
  Correct-to-GlobalMean performance gap;
- layer identity explains 87% to 96% of coefficient variance;
- FeatureGate still executes every Transformer block and measured inference is
  30.8% slower than Dense;
- on the public MUDDPythia-1.4B checkpoint, cross-input reassignment and token
  shuffling increase NLL by 1.9067 and 2.9637, respectively; and
- MUDDPythia also executes every Transformer block.

No attributable immutable implementation revision was identified during the
triggering review. The source therefore enters this program as paper-level
methodological evidence, not as an admitted executable artifact or independent
reproduction.

## Why the existing dispatch controls are insufficient by themselves

The existing dispatch/weight addendum already requires preserved marginals with
broken example correspondence, score/bias counterfactuals, fixed-route
Jacobians, route-boundary strata, and physical runtime accounting. Those remain
binding.

A missing identification condition remains: if the controller is recomputed
after an activation or assignment perturbation, the observed effect combines:

1. dependence on the original coefficient assignment;
2. feedback through the controller's response to the perturbed trajectory;
3. secondary route, state, normalization, or cache changes; and
4. any actual conditional-execution change.

A cross-input or shuffled-controller test is therefore not interpretable as an
assignment-dependence test unless the complete coefficient object is captured
before the intervention and replayed without recomputation. This addendum adds
that gate.

## Binding object-identity separation

Every compatible study must freeze and report these objects separately where
they exist:

1. model checkpoint and immutable runtime;
2. controller checkpoint or controller parameters;
3. controller input activation boundary;
4. controller input population and temporal boundary;
5. raw controller outputs;
6. post-processed coefficient tensor;
7. coefficient axes, shape, dtype, precision, normalization, and broadcast
   semantics;
8. assignment map from coefficient entries to examples, tokens, positions,
   layers, streams, experts, residual branches, or depth sources;
9. cached pre-intervention coefficient tensor;
10. replay transformation and replay assignment map;
11. whether the controller is disabled, bypassed, recomputed, partially
    recomputed, or still consulted through a fused path;
12. mathematical modules whose parameters or activations are scaled, mixed,
    selected, or modulated;
13. logical execution mask;
14. physically dispatched kernels, experts, blocks, branches, communication,
    and memory movement;
15. recurrent state, KV cache, prefix cache, and branch lineage;
16. output logits, generated action, parser result, and verifier outcome; and
17. complete end-to-end systems cost.

A tensor named `gate`, `router`, `weight`, `importance`, `halting`, `skip`,
`depth`, `mixture`, or `coefficient` does not identify which of these objects it
contains. A coefficient near zero does not prove that the associated module was
not executed. A top-k index does not prove that an unselected module incurred no
compute, transfer, synchronization, or memory cost.

## Three-claim reporting gate

Every claim of `dynamic inference`, `conditional computation`, `adaptive
computation`, `input-dependent routing`, `dynamic depth`, `efficient routing`,
or equivalent language must report three results separately.

### Claim A — Coefficient variation

Report whether controller coefficients vary across examples, tokens, positions,
layers, streams, experts, or time. At minimum include:

- total and axis-wise variance;
- variance attributable to layer, position, token identity, example identity,
  sequence length, batch placement, and runtime state;
- within-example and between-example variation;
- temporal autocorrelation and route persistence;
- coefficient entropy, sparsity, concentration, and margin;
- calibration-set versus evaluation-set drift; and
- precision, clipping, saturation, ties, and numerical determinism.

Coefficient variation alone establishes neither functional necessity nor
conditional execution.

### Claim B — Frozen-model assignment dependence

Report whether a fixed model function depends on the correspondence between a
precomputed coefficient tensor and the input trajectory. This claim requires the
frozen-controller replay gate below.

Assignment dependence may establish that content-conditioned correspondence
matters to the frozen mathematical function. It does not establish that the
coefficient semantics are human-interpretable, that the controller predicts
correctness, that the model omits computation, or that the mechanism saves
latency, memory, energy, or money.

### Claim C — Actual conditional execution

Report whether the admitted runtime physically omits work conditional on the
input. This requires direct execution evidence and end-to-end systems
measurement. Soft scaling, dense mixing, dynamic parameter generation, or
content-dependent weighting while executing every candidate module is not
conditional execution.

No paper, artifact, benchmark, or implementation may use evidence for one claim
as evidence for either of the other two.

## Frozen-controller replay gate

A replay study may be interpreted as assignment dependence only if all of the
following pass.

### Pre-intervention capture

1. Run the admitted baseline trajectory without perturbation.
2. Capture the complete coefficient tensor at the prospectively frozen boundary.
3. Capture every shape, axis, broadcast, mask, tie, normalization, and precision
   transformation needed to replay it exactly.
4. Bind the tensor to the exact input, model, controller, runtime, state, cache,
   seed, batch, and execution identity.
5. Complete capture before changing activations, assignments, routes, inputs,
   or state.

### Controller disablement

During replay:

- disable the controller through the actual executed path;
- prove that no fused kernel, wrapper, fallback, cache, compiled graph, or
  downstream normalization recomputes or modifies the controller output;
- fail closed if the controller is called;
- fail closed if any coefficient is synthesized, defaulted, clipped, normalized,
  or broadcast differently from the registered replay transformation; and
- preserve all non-controller model parameters and baseline runtime conditions.

A caller-supplied boolean such as `controller_disabled=true` is not evidence.
Use call counters, graph inspection, hooks, deterministic sentinels, or equivalent
adversarial checks on the actual runtime path.

### Replay transformations

Where technically meaningful, the minimum comparator set is:

1. exact same-input replay;
2. cross-input reassignment within a matched stratum;
3. complete random reassignment with matched coefficient marginals;
4. token-position shuffling within an example;
5. token-identity-matched shuffling across examples;
6. layer-label permutation;
7. stream-label or branch-label permutation;
8. expert-label or depth-source-label permutation;
9. static global mean estimated only from an independent calibration set;
10. static layerwise profile estimated only from an independent calibration set;
11. static positionwise profile estimated only from an independent calibration
    set where position is a registered factor;
12. matched random coefficients preserving norm, sparsity, entropy, and marginal
    distribution;
13. identity or no-modulation condition where mathematically defined; and
14. independently generated nuisance-only profiles based on length, position,
    token frequency, batch location, or other transparent variables.

The replay policy must freeze tie handling, missing entries, padding, packed
sequences, prefill/decode separation, recurrent state, cache lineage, and
out-of-range behavior.

### Same-input replay parity

Exact same-input replay must preserve, within prospectively frozen tolerances:

- coefficient tensors;
- route identities and weights;
- logical execution masks;
- expert and branch outputs;
- recurrent and cache state;
- logits and generation;
- parser and tool-call outputs;
- verifier outcomes;
- VJP, JVP, and finite-difference behavior at claimed boundaries; and
- physical execution path where replay is claimed to be observationally
  equivalent.

Failure of same-input replay invalidates the cross-input and static-profile
interpretation.

## Independent calibration-profile gate

A static profile is an estimated artifact. Freeze separately:

- calibration population and exclusion rules;
- source-group split and independence from evaluation and sealed data;
- aggregation estimator;
- layer, position, stream, expert, or branch grouping;
- weighting for sequence length, padding, packed tokens, and batch composition;
- dtype, precision, accumulation order, and distributed reduction;
- handling of rare or unseen strata;
- profile revision and drift policy; and
- immutable content identity of the resulting profile.

A profile estimated on the evaluation set, sealed set, paired test input, or any
future information is inadmissible. A layerwise profile that performs well may
show that layer identity carries most of the useful modulation. It does not prove
that all input-conditioned variation is useless on other populations, targets,
or runtimes.

## Feedback and trajectory-lineage gate

The following are separate experiments:

1. frozen coefficients replayed on the original unperturbed trajectory;
2. frozen coefficients replayed while hidden states evolve under reassignment;
3. controller coefficients recomputed from the perturbed hidden states;
4. controller coefficients recomputed only at selected layers or times;
5. routes or execution masks changed while coefficient values are held fixed;
6. recurrent or cache state carried from baseline into a perturbed branch; and
7. recurrent or cache state recomputed entirely under the perturbed branch.

Each condition must bind its own branch ancestry, controller call history,
coefficient lineage, hidden-state lineage, route lineage, cache lineage, and
verifier outcome. Results from one may not be relabeled as another.

## Actual-execution proof gate

A conditional-execution claim requires direct evidence that work is physically
omitted in the admitted runtime.

At minimum, report:

- candidate modules and the registered skip condition;
- logical execution masks;
- module-entry and module-exit counters;
- dispatched kernels and kernel durations;
- expert dispatch and communication;
- matrix-multiplication shapes and counts;
- memory reads, writes, and transfers;
- synchronization and launch overhead;
- controller, sorting, masking, compaction, and scheduler overhead;
- padding and static-shape waste;
- fallback, overflow, capacity, and miss behavior;
- prefill and decode separately;
- batch size, sequence length, concurrency, topology, and cache regime;
- FLOPs or equivalent operation accounting;
- peak and resident memory;
- throughput, mean latency, and tail latency; and
- energy or monetary cost where claimed.

Required controls include:

1. dense or full-compute baseline;
2. same architecture with a static independently calibrated profile;
3. same logical mask under a runtime that still executes all modules;
4. matched random masks or routes;
5. oracle conditional execution where tractable;
6. controller-disabled execution;
7. controller-only overhead with no skip;
8. fully resident and transfer-bound conditions for MoE systems;
9. cold, warm, and hot caches; and
10. identical-output or equal-quality comparison under the registered verifier.

A theoretical FLOP count does not establish runtime savings. A reduced active
parameter count does not establish fewer physical operations. A sparse logical
mask implemented through dense kernels does not establish conditional execution.
A speedup that disappears after controller and scheduling overhead is not a
runtime benefit.

## Router and MoE telemetry consequence

For an architectural MoE, distinguish:

1. router-score variation;
2. assignment dependence of the frozen routed model;
3. selected expert identities and mixture weights;
4. expert execution and communication;
5. capacity, overflow, padding, and fallback;
6. balancing-state updates;
7. expert residency, prefetch, and transfer;
8. end-to-end runtime cost; and
9. objective outcome.

Selected experts normally imply conditional expert execution only after the
native runtime path is proven. Router-score variation does not prove expert
specialization, semantic routing, correctness awareness, or a global workspace.
Preserved expert-load marginals with broken example correspondence remain a
mandatory control, but must now be implemented through pre-intervention frozen
router/controller replay when the claim is assignment dependence.

M39 remains fixed-routing and observation-only. It may measure prospectively
frozen aggregate telemetry under the admitted native route. It may not replay,
permute, force, replace, suppress, expand, shrink, or otherwise alter routing,
expert cardinality, mixture weights, computation, stopping, retry, repair, or
production behavior.

## Early-exit, truncation, and adaptive-depth consequence

A halting probability, depth weight, confidence coefficient, or intermediate
readout may vary without causing a physical early exit. Future studies must
separate:

- a readable stopping score;
- dependence of the final model on that score's assignment;
- a logical depth-selection policy;
- physical nonexecution of later blocks;
- cache and residual-state consequences;
- objective correctness and continuation utility; and
- end-to-end cost under full fallback accounting.

A score that predicts the model's later output or stable action does not prove
that stopping is safe. A depth controller that scales every block does not skip
blocks. A runtime that evaluates all branches before choosing one is not
conditional execution even if only one branch is consumed downstream.

## Jacobian and derivative boundary

For a controller-modulated model, these are different downstream maps:

1. controller coefficients fixed at the baseline cached tensor;
2. cached coefficients reassigned through a registered replay map;
3. controller coefficients recomputed from the evolving hidden state;
4. discrete route or execution mask fixed;
5. discrete route or execution mask permitted to change; and
6. physical runtime changed while the mathematical function is intended to
   remain equivalent.

A Jacobian with coefficients and routes fixed measures a conditional local map.
It excludes controller feedback and discrete boundary crossings. A Jacobian that
differentiates through the controller measures a different map and still does
not represent physical module omission or a discrete skip transition.

Required derivative diagnostics include:

- same-input replay forward parity;
- fixed-coefficient VJP and JVP parity;
- controller-included VJP and JVP parity;
- finite differences that remain within one assignment and route stratum;
- finite differences that cross coefficient, top-k, halting, or execution-mask
  boundaries;
- route-unchanged versus route-changed strata;
- execution-mask-unchanged versus execution-mask-changed strata; and
- objective outcome changes rather than telemetry changes alone.

No derivative result authorizes controller editing, forced routing, early exit,
adaptive depth, expert suppression, retry, repair, activation steering, cache
rewriting, or production control.

## Semantic-workspace and monitor boundary

Input-conditioned coefficients may encode useful information while remaining
mostly explained by layer, position, token identity, length, or other nuisance
structure. Assignment dependence may show that correspondence matters without
showing what the coefficients represent. Conditional execution may save compute
without exposing a correctness or process-quality signal.

Any claim of semantic workspace, introspection, error awareness, process quality,
metacognition, causal expert specialization, or objective correctness must still
beat prospectively frozen transparent comparators including:

- layer and position identity;
- token frequency and token identity;
- prompt and response length;
- logits, entropy, margin, and perplexity;
- direct hidden-state probes;
- route frequency and load;
- static independent calibration profiles;
- trajectory, parser, memory, program-state, and tool-state features;
- external verifier features; and
- matched nuisance-only controller profiles.

Detection remains separate from continuation utility, intervention, and
production control.

## Agents-A1 scaling consequence

The technically credible sequence is:

1. Complete Q35Q production-path provenance, exact loader, strict quantized
   tensor-consumption, expert-ordering, forward, VJP, JVP, and finite-difference
   admission.
2. Admit Agents-A1-4B under its exact checkpoint, tokenizer, template, parser,
   hybrid-attention state, cache, harness, verifier, environment, and runtime.
3. Establish deterministic, logit, confidence, hidden-state, spectral,
   trajectory, memory, parser, program-state, tool-state, and external-verifier
   baselines before any controller or Jacobian claim.
4. Use Agents-A1-4B to validate the frozen-controller replay harness on a
   tractable dense bridge only where a genuine controller-modulated object
   exists; do not invent a router analogue for a dense model.
5. Separately admit Agents-A1-35B's checkpoint, quantization, router, routed and
   shared experts, hybrid state, cache, kernels, topology, batching, scheduler,
   capture path, tool harness, and verifier.
6. Prove the exact identities of raw router scores, dispatch transformations,
   selected experts, mixture weights, capacity behavior, physical expert
   execution, communication, and runtime cost.
7. Establish observation-only native router telemetry under fixed routing before
   any replay or intervention.
8. In a separate nonsealed, preregistered study, capture complete router and
   coefficient tensors before intervention and perform same-input replay,
   cross-input reassignment, token shuffling, layer/expert permutations, and
   independent static-profile controls.
9. Keep controller recomputation disabled for the assignment-dependence arm and
   evaluate recomputed-controller feedback as a distinct condition.
10. Measure actual expert execution, communication, memory movement, throughput,
    latency tails, and controller overhead rather than inferring efficiency from
    score sparsity or active-parameter counts.
11. Require router telemetry to add sealed target-specific objective value beyond
    the complete transparent, hidden-state, trajectory, verifier, and static-
    profile comparator stack.
12. Add Jacobian features only after exact derivative parity, with fixed-route,
    controller-included, and boundary-crossing conditions reported separately.
13. Require a separate counterfactual-utility study before early exit, retry,
    repair, adaptive routing, expert suppression, depth allocation, or steering.
14. Preserve the admitted native full-compute/fixed-routing runtime as fallback.

This paper supplies a methodological audit for future Agents-A1 routing claims.
It is not a transfer bridge, an admitted implementation, evidence that Agents-A1
routes are semantic, or evidence that Agents-A1 can safely omit reasoning or
expert computation.

## Established by this correction

The following are now binding distinctions:

- coefficient variation is not assignment dependence;
- assignment dependence is not conditional execution;
- conditional execution is not objective correctness;
- controller recomputation after perturbation confounds assignment effects with
  feedback;
- pre-intervention coefficient caching and controller disablement are required
  for frozen assignment replay;
- static profiles are fitted artifacts requiring independent calibration and
  immutable identity;
- soft scaling, dense mixing, and zero-like weights do not prove module
  nonexecution;
- logical sparsity, theoretical FLOPs, active parameters, and physical runtime
  are separate objects;
- fixed-controller and controller-included Jacobians are different maps; and
- no privacy, sealed-data, verifier, provenance, derivative, resource,
  intervention, or production gate is weakened.

## Not established

The following remain unproven:

- independent reproduction of arXiv `2607.26192v1`;
- immutable admission of its implementation, data, checkpoints, profiles, and
  dependency closure;
- generality of its reported results beyond FeatureGate and MUDDPythia;
- semantic interpretation of any controller coefficient;
- objective correctness or error-prediction value from coefficient variation;
- safe or useful conditional execution in Agents-A1;
- transfer of FCA results to Qwen3.5, Qwen3.6, Agents-A1, or other architectural
  MoEs;
- incremental router or Jacobian-Lens value beyond cheaper controls;
- complete Q35Q runtime and derivative admission; and
- safe early exit, truncation, retry, repair, adaptive routing, forced routing,
  activation steering, cache rewriting, or production deployment.

## Active blocker remains unchanged

The active blocker remains exact-target-runtime Q35Q admission:

1. execute the composed Transformers provenance adapter in the exact target
   runtime;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and complete executable source
   closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption;
6. prove exact expert and fusion ordering;
7. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
8. pass the complete Phase-0 conjunction before weight staging or GPU
   authorization.

The triggering evidence resolves none of these gates. `docs/LIVE_STATUS.md` must
not record operational progress from this protocol-only correction.
