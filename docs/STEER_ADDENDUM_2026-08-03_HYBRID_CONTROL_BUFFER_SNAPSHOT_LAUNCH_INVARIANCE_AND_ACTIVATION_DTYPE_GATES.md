# STEER ADDENDUM — hybrid control-buffer snapshot, launch-invariance, and activation-dtype gates

Date: 2026-08-03
Parent remote head: `6ce2ea38d3549ae5f329df0ac3a34d952ceb859b`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, the Q35Q protocol, and every later cumulative correction. It preserves every privacy, sealed-data, provenance, verifier, exact-set, exact-gradient, numerical-parity, resource, intervention, rollback, action, and production-gating rule. It authorizes no model-weight retrieval, model execution, GPU use, hidden-state or router capture, Jacobian fitting, sealed evaluation, intervention, external action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active milestone remains exact-target-runtime Q35Q provenance, loader, tensor-consumption, expert-order, forward, persistent-state, activation-VJP, activation-JVP, and finite-difference admission. This addendum narrows the evidence required for hybrid-state and quantized-runtime admission. It does not displace that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and public-source engineering material may be committed. Prompts, questions, answers, tokens, request identities, routes, hidden states, recurrent states, Jacobians, verifier labels, private paths, credentials, weights, and sealed outcomes remain prohibited.

## Triggering primary evidence

vLLM merged two runtime corrections on 2026-08-03.

Commit `c2881ce60302b5455867d2c29cdfae5fbeddecac`, `[Bugfix][Hybrid] Fix cross-block race on num_accepted in MRv2 align prefix cache (#50432)`, corrected a Model Runner V2 hybrid-state kernel that used the same accepted-token tensor as both a read source and an in-place write target across independently scheduled Triton programs. One program reset the value while other layer/state programs could still read it. Depending on launch waves, SM availability, and the number of hybrid states, different layers could therefore compute different copy decisions for the same request and leave recurrent state inconsistent across layers. The correction snapshots the full non-contiguously indexed decision tensor and writes updates to a distinct destination.

Commit `0b37d8389f4b8378adab0d3dfa1beffbb152e303`, `fix: NVFP4 quantization out_dtype should match model dtype, not torch default (#48861)`, corrected quantized linear methods whose output dtype came from process-global `torch.get_default_dtype()` instead of the admitted model configuration. The previous path commonly emitted FP32 into a BF16 or FP16 model. Some downstream paths tolerated the mismatch, while LoRA exposed it as a hard dtype failure. A separate LoRA kernel defect remained outside that correction.

These are upstream engineering results, not jLens admission artifacts. They establish neither Agents-A1 compatibility nor Q35Q parity. They expose two protocol boundaries that require explicit binding:

1. a runtime can appear stable in one launch condition while containing a cross-program read/write race that changes persistent state under another launch shape; and
2. nominal model dtype and checkpoint quantization do not determine actual activation dtype when a kernel or module consults mutable process-global defaults.

## Binding interpretation

The following objects may not be renamed into one another:

1. immutable per-step decision input, mutable decision output, and reusable scratch storage;
2. request-level accepted-token count and per-layer recurrent-state update;
3. Python sequencing, CUDA-stream sequencing, program-instance ordering, and launch-global ordering;
4. deterministic output in one occupancy condition and launch-shape-invariant execution;
5. model-config dtype, parameter-storage dtype, dequantization dtype, kernel-input dtype, accumulator dtype, kernel-output dtype, residual dtype, and process-global default dtype;
6. token agreement, logit agreement, hidden-state agreement, persistent-state agreement, and derivative agreement;
7. capture-disabled execution, observation-only capture, speculative execution, and changed numerical execution; and
8. runtime compatibility, scientific equivalence, and production authorization.

A buffer that participates in a control decision is part of executable state. A dtype chosen by ambient process state is part of executable provenance. Neither may be inferred from a checkpoint label alone.

## Hybrid control-buffer alias and snapshot gate

Every hybrid, recurrent, speculative, prefix-cache, route, acceptance, or truncation kernel used by an admitted path must declare its complete read set, write set, aliasing relationships, and synchronization assumptions.

The production path must prove that:

- no independently scheduled program can observe a value overwritten by another program in the same logical decision unless the algorithm prospectively specifies and proves that atomic communication;
- read-before-write control tensors are immutable for the complete consuming launch;
- updates use a distinct destination or an equivalently proven synchronization construction;
- non-contiguous request-to-state mappings snapshot the full reachable logical index domain, not merely a contiguous active prefix;
- scratch reuse cannot overwrite a source before all readers finish;
- stream and event dependencies order snapshot, kernel read, kernel write, copy-back, and subsequent consumption;
- cancellation, retry, preemption, prefix reuse, cache recycling, and worker restart invalidate or transfer ownership correctly;
- every layer and state type applies the same request-level acceptance decision unless an explicitly different rule is frozen; and
- no stale, partial, duplicated, or wrong-request control state can be interpreted as current.

A passing generation or token-parity test is insufficient. The private synthetic fixture must compare the complete per-layer persistent state after every admitted transition.

## Launch-shape and occupancy invariance gate

For fixed inputs, seeds, runtime identity, and declared nondeterminism, an admitted kernel must produce the same decision and state transition across prospectively varied launch conditions.

The adversarial ladder must vary, where applicable:

- request count and batch compaction;
- accepted-token counts, including aligned and non-aligned boundaries;
- number of hybrid layers and state types;
- block size and prefix-cache alignment;
- sparse and non-contiguous request-state mappings;
- chunked-prefill boundaries;
- eager versus CUDA-graph execution;
- speculative draft length and verification outcome;
- stream scheduling and deliberately delayed neighboring work;
- SM occupancy and competing admitted synthetic kernels;
- tensor, pipeline, context, and expert parallel shape;
- device model and topology used by the claimed condition; and
- repeated execution under frozen and deliberately perturbed scheduling conditions.

Required comparisons include control decisions, copy offsets, cache or recurrent-state indices, every layer's persistent state, logits, tokens, parser state, tool state, verifier outcome, and VJP/JVP/finite-difference results wherever derivative claims are intended.

A nondeterminism envelope must be estimated from the uninstrumented admitted reference before the candidate path is examined. It may not be widened after a launch-dependent failure. A kernel whose correctness depends on all programs reading before one program writes is blocked unless an explicit memory-model guarantee enforces that ordering.

Static alias analysis, compiler diagnostics, race-checking tools, and source inspection are supporting evidence only. They do not replace adversarial execution through the exact production kernel.

## Quantized activation-dtype provenance gate

Every admitted quantized or mixed-precision module must have a frozen boundary-level dtype contract. At minimum, bind:

- model-config dtype;
- parameter and packed-weight storage dtype;
- scale, zero-point, index, and auxiliary-tensor dtype;
- dequantized compute dtype;
- kernel input dtype;
- multiplication and accumulation dtype;
- kernel output dtype;
- router-logit and route-weight dtype;
- shared-expert and routed-expert output dtype;
- normalization, residual-add, attention, recurrent-state, cache, adapter, and unembedding dtype;
- autocast state and policy;
- compiler and kernel promotion rules; and
- every explicit cast before and after the measured boundary.

The expected contract must come from the immutable model/runtime configuration and source identity, not from the live tensor being checked and not from `torch.get_default_dtype()` unless the exact experiment explicitly declares the process-global default as part of its mathematical model.

The exact production path must record actual boundary dtypes on private synthetic fixtures and fail closed on any undeclared cast, promotion, demotion, fallback, or output dtype.

## Process-global default-dtype adversarial gate

Run the exact loader and synthetic forward in clean subprocesses under prospectively selected process-global defaults. At minimum test the ordinary default and one conflicting default that would expose accidental dependence without invoking an unsupported model configuration.

The admitted model must retain the same configured module contracts, actual boundary dtypes, forward results, persistent state, and derivatives across those subprocesses unless a specific component is explicitly contract-bound to the global default.

The fixture must detect:

- constructors that capture the global default before the model configuration is installed;
- lazy modules that consult the global default on first use;
- tensors created without explicit dtype in loaders, adapters, routers, expert paths, caches, and telemetry code;
- quantized kernels whose output dtype differs from the model dtype;
- reference implementations that share the same ambient-dtype defect as the candidate path; and
- global dtype mutations that leak between tests, requests, workers, or model instances.

A candidate and reference agreeing because both consumed the same wrong process-global default is not independent parity evidence.

## Adapter, router, and downstream-consumer gate

A quantized layer can appear functional when tolerant downstream modules silently cast or promote its output. Admission therefore requires explicit downstream checks for every enabled path, including:

- residual addition;
- normalization;
- attention and recurrent-state updates;
- router scoring and Top-K selection;
- shared and routed experts;
- LoRA or other adapters;
- tensor/expert-parallel collectives;
- cache writes and reads; and
- final normalization and output head.

For each boundary, compare actual dtype, shape, device, stride or layout where kernel-relevant, numerical output, and declared promotion behavior. Enabling an adapter, alternate attention backend, fused MoE kernel, or speculative path creates a separate executable condition unless complete parity is established.

A crash-free base-model generation does not admit the adapter path. Token identity does not admit hidden-state, cache, route, or derivative identity.

## Forward and derivative parity consequence

Q35Q forward, activation-VJP, activation-JVP, and finite-difference checks must execute under the exact frozen dtype contract. The dequantized reference must use explicit dtypes and must not inherit an undeclared process-global default.

Required evidence includes:

- per-boundary dtype equality to the frozen manifest;
- deterministic or preregistered-tolerance forward agreement;
- persistent-state agreement after every hybrid transition;
- activation-VJP and activation-JVP agreement;
- finite-difference agreement at prospectively selected coordinates and step sizes;
- repeatability across the admitted launch-shape ladder; and
- fail-closed behavior when a dtype, alias, mapping, snapshot, or synchronization assumption is violated.

A fixed-route or fixed-state Jacobian is scoped to the exact admitted state transition and dtype condition. It cannot be reported as the derivative of a race-dependent or ambient-dtype-dependent runtime.

## Agents-A1 scaling sequence

The technically credible sequence is now:

1. Complete Q35Q installed-distribution ownership, live executable-source closure, clean-subprocess mutation detection, loader-entry binding, and immutable runtime-tuple admission.
2. Add synthetic per-module dtype-contract checks and process-global-default perturbation before any model-weight staging.
3. Add hybrid control-buffer alias, snapshot, and launch-shape tests to the strict synthetic Qwen3.5-MoE loader path.
4. Prove exact packed-tensor consumption, expert ordering, forward, persistent-state, VJP, JVP, and finite-difference parity under the frozen dtype and synchronization contracts.
5. Admit Agents-A1-4B under one immutable local runtime and repeat the complete dtype and launch-invariance ladder; use it only as an engineering bridge.
6. Establish cheap behavioral, logit, confidence, trajectory, parser, tool, memory, verifier, direct-hidden-state, and router baselines before Jacobian fitting.
7. Admit Agents-A1-35B independently under its exact quantization, hybrid-state implementation, routed/shared experts, adapters, kernels, topology, batching, scheduler, and dtype contract.
8. Treat every speculative, prefix-cache, continuous-batching, adapter, and distributed mode as a separately admitted execution condition until parity is proved.
9. Require route, hidden-state, semantic-workspace, and Jacobian features to add sealed objective value beyond cheaper controls under the same admitted runtime.
10. Preserve native full-compute execution and independent verification as fallback. No telemetry channel may authorize early exit, truncation, routing changes, expert dropping, retry, escalation, external action, or production deployment without its separate gates.

## Current blocker and execution order

This addendum does not change the active blocker. Q35Q remains blocked until the complete conjunction passes:

1. resolve public repository visibility versus the declared private destination;
2. bind installed runtime files to immutable distribution ownership records;
3. derive complete executable-source closure from actual live runtime objects;
4. detect shadow imports, monkeypatches, runtime substitution, ambient global-state drift, and process leakage in clean subprocesses;
5. bind the exact GPTQModel/Defuser loader and conversion entry;
6. freeze one immutable Transformers, GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, backend, launch, checkpoint-format, kernel, topology, reduction, and dtype tuple;
7. run strict synthetic Qwen3.5-MoE quantized loading;
8. prove one-time packed-tensor consumption and exact expert/fusion ordering;
9. prove deterministic forward and complete persistent-state parity across the admitted launch ladder; and
10. prove activation-VJP, activation-JVP, and finite-difference parity.

No model-weight staging or GPU execution is authorized before the full conjunction passes.

## Established versus unproven

Established only as external public engineering evidence:

- a hybrid-state kernel can contain a launch-dependent cross-program race when a decision tensor aliases its update destination;
- same-wave execution can conceal a defect that appears under different wave partitioning or occupancy;
- snapshotting the decision source and separating the write destination removes that specific alias in the corrected vLLM path;
- quantized linear output dtype can accidentally follow mutable process-global PyTorch state rather than the model configuration; and
- crash-free or token-correct execution in tolerant downstream paths does not prove a correct activation-dtype contract.

Unproven for this program:

- independent reproduction of either upstream correction;
- presence or absence of the same defects in the frozen Q35Q or Agents-A1 runtime;
- launch-shape-invariant Qwen3.5 or Agents-A1 persistent state;
- complete per-boundary activation-dtype provenance for the chosen GPTQ, AWQ, NF4, FP8, or NVFP4 path;
- exact forward, hidden-state, route, cache, persistent-state, VJP, JVP, and finite-difference parity;
- complete Q35Q, Agents-A1-4B, or Agents-A1-35B admission;
- incremental correctness, continuation-utility, tool-utility, or episode-success value from router, hidden-state, or Jacobian telemetry;
- a natural semantic workspace; and
- safe early exit, truncation, adaptive routing, expert dropping, retry, escalation, external action, or production deployment.

The research program remains unfinished.