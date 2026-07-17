# Steer addendum — Q35Q differentiable GPTQ Torch backend priority

Date: 2026-07-17

This addendum is binding program control. It preserves every existing privacy,
sealed-data, provenance, verifier, exact-set, resource, production-gating, and
claim-boundary rule. It does not authorize weight staging, tensor-payload retrieval,
model execution, GPU use, hidden-state or router capture, gradient work, or any
scientific claim.

## Trigger

Commit `7f6f7c9422e9be6fba80c5b34ef641b1483215c8` correctly narrows the
Transformers 5.13.1 global conversion mapping: its standard numbered-expert merge
covers `.weight` tensors but does not by itself consume the admitted GPTQ artifact's
per-expert `qweight`, `qzeros`, `scales`, and `g_idx` tensors. The commit remains
useful partial source inspection and correctly leaves the aggregate outcome
`q35q_artifact_admission_blocked`.

Two further controls are now binding.

First, the committed `verify_conversion_plan_present()` function is a textual
substring check. It can report success when the expected strings exist in comments,
unrelated mappings, dead code, or separate objects without proving that the pinned
`qwen3_5_moe_text` dispatch actually composes those operations. Its result is a
non-admission drift hint only. It may not satisfy source identity, runtime dispatch,
or conversion-plan admission without an independently pinned source digest and
structural inspection of the exact selected mapping objects.

Second, public primary-source inspection of GPTQModel at immutable commit
`d2945a35397e2892abc3df45e0a95236058c55a0` identifies a technically credible
activation-autograd candidate that should be evaluated before optimized inference
kernels:

- `TorchLinear` declares `SUPPORTS_TRAINING = True`;
- its eager forward path dequantizes the fixed GPTQ weights and applies ordinary
  `torch.matmul` to the activation tensor; and
- GPTQModel's Qwen3.5-MoE path uses Defuser to expose numbered expert linears before
  quantized-module replacement.

This does not establish strict loading, exact forward equivalence, derivative parity,
or scale feasibility. It does establish a bounded candidate path for VJP/JVP with
respect to activations. Jacobian Lens does not require gradients with respect to the
quantized integer weight buffers; it requires correct differentiation through the
model computation with weights treated as constants.

## Binding classification

Commit `7f6f7c9422e9be6fba80c5b34ef641b1483215c8` remains classified:

`q35q_runtime_conversion_plan_partial`

Its substring-based version-drift result is not an admission pass. The overall Q35Q
outcome remains:

`q35q_artifact_admission_blocked`

The preferred quantized runtime candidate is now:

`GPTQModel + Defuser + BACKEND.GPTQ_TORCH eager activation-autograd path`

This is a priority for bounded admission testing, not a frozen runtime selection and
not a scientific result.

## Required source and dispatch binding

Before the conversion-plan sub-gate may pass:

1. Freeze immutable identities for GPTQModel, Defuser, Transformers, Optimum if
   present, Accelerate, PyTorch, CUDA, and the selected loader entry point.
2. Bind the installed bytes to those expected identities.
3. Resolve the actual model-type dispatch and exact Qwen3.5-MoE model definition.
4. Inspect the actual conversion objects or parsed syntax tree for the selected
   mapping. Do not infer composition from global string presence.
5. Require exact mapping membership, operation ordering, source patterns, target
   patterns, dimensions, and dispatch association.
6. Add adversarial tests containing all expected strings in comments, dead code,
   unrelated model mappings, reordered operations, and duplicate shadow mappings;
   each must fail.

## Required differentiable-runtime fixture

Before any full checkpoint staging or GPU scientific work, construct a tiny synthetic
Qwen3.5-MoE-shaped fixture through the real pinned GPTQModel/Defuser loader stack.
The fixture must use synthetic public-safe tensors only and must prove all of the
following:

1. fused source experts are deterministically defused into canonical numbered
   `gate_proj`, `up_proj`, and `down_proj` modules;
2. every synthetic `qweight`, `qzeros`, `scales`, and `g_idx` entry is consumed once
   by the intended module, with zero missing, unexpected, ignored, duplicated,
   ambiguous, or synthesized keys;
3. expert numbering, gate/up identity, expert order, shapes, dtypes, group size,
   packing format, symmetry convention, and activation function are preserved;
4. the selected backend is the pure Torch GPTQ backend and the tested path is the
   eager dequantize-plus-matmul path;
5. streaming, look-ahead prefetch, detached weight cache, Triton dequantization,
   custom fused kernels, and compile-time graph replacement are disabled for the
   initial derivative admission test;
6. forward outputs match an independently dequantized reference within frozen
   tolerances;
7. activation-input VJP and JVP match the independently dequantized reference within
   frozen absolute and relative tolerances;
8. central finite differences agree with the analytic activation directional
   derivative on a preregistered synthetic direction;
9. repeated CPU runs are deterministic before any GPU parity attempt; and
10. right-to-wrong adversarial fixtures fail when expert order, gate/up order,
    quantization auxiliaries, or group metadata are perturbed.

Weight-gradient support is neither required nor sufficient. The admitted claim is
limited to derivatives with respect to activations and other explicitly selected
floating-point internal states while quantized weights remain constants.

## Scaling implication

If the synthetic fixture passes, the credible scaling path is:

1. complete the full Phase-0 provenance and strict-load conjunction;
2. stage the admitted Q35Q weights only after that aggregate pass;
3. obtain a separately authorized GPU-resource transition;
4. run bounded forward and activation VJP/JVP parity on Q35Q using the pure Torch
   backend before considering any faster kernel;
5. measure peak VRAM, host RAM, expert dequantization traffic, backward latency, and
   route-conditioned active-expert cost;
6. test optimized kernels only behind an independent parity gate; and
7. proceed to lens fitting only if exact derivative and resource gates pass.

The route is potentially relevant to Agents-A1 because sparse execution may limit
per-token expert computation, but no memory, throughput, backward-cost, or transfer
claim follows from the existence of the eager Torch path. Full-model scale remains
unproven.

## Research boundary

Public GPTQModel support establishes an engineering candidate, not Jacobian-Lens
validity. Recent hidden-state correctness and router-telemetry studies remain future
comparators only. Detection must independently beat metadata, confidence,
hidden-state, answer-identity, route/path, and nuisance baselines under sealed,
family-disjoint evaluation before retry, abort, early-exit, truncation, routing,
steering, or production experiments are authorized.

M38E remains terminally closed at `inconclusive`. No completed-error predictor,
semantic-workspace correctness monitor, safe early-exit or truncation rule, causal
expert localization, routing intervention, correction policy, activation steering,
Agents-A1 transfer, or production utility is established.
