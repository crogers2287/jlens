# Steer addendum — Q35Q dynamic GPTQ loader and repository-visibility correction

Date: 2026-07-17

This addendum is binding program control. It preserves every existing sealed-data,
privacy, provenance, verifier, exact-set, resource, production-gating, and claim-
boundary rule. It does not authorize weight staging, tensor-payload retrieval,
model execution, GPU use, hidden-state or router capture, gradient work, or any
scientific claim.

## Trigger

Commit `42a7b243b62ec340113dd9d6cd0c24bb043e0a13` correctly established two
narrow facts for the installed source class and the pinned checkpoint metadata:

- Transformers 5.13.1 constructs Qwen3.5-MoE routed experts as packed 3-D
  parameters; and
- the admitted GPTQ artifact exposes numbered per-expert quantized tensors.

The commit then classified the branch as a hard load-manifest blocker because no
model-local `_checkpoint_conversion_mapping`, state-dict pre-hook,
`_load_from_state_dict`, or equivalent conversion hook was found. That inference is
premature. The actual GPTQ loading path is not limited to model-local hooks.

Public primary-source inspection at immutable commits shows:

1. Transformers has a global dynamic weight-conversion layer outside the model
   class. `src/transformers/conversion_mapping.py` contains `WeightConverter`,
   `MergeModulelist`, and `Concatenate` machinery for converting individual MoE
   experts into packed 3-D parameters. The exact current `qwen3_5_moe_text`
   conversion chain still requires runtime-specific audit; absence of a model-local
   hook does not establish absence of a loader-level transformation.
2. Transformers' GPTQ quantizer delegates pre-quantized model conversion to
   `optimum.gptq.GPTQQuantizer.convert_model()` before weight loading. The exact
   installed Optimum/GPTQModel implementation and generated conversion plan were
   not inspected by commit `42a7b243`.
3. GPTQModel release 5.8.0 explicitly added Qwen3.5-MoE support and automatic
   defusing of fused models. At public commit
   `d2945a35397e2892abc3df45e0a95236058c55a0`, its Qwen3.5-MoE definition exposes
   numbered `gate_proj`, `up_proj`, and `down_proj` experts; its loader invokes
   Defuser before module discovery and QuantLinear replacement, then loads the
   quantized checkpoint into that converted model. Its tests include a Qwen3.5-MoE
   quantize-and-evaluate path.

These public sources do not prove that the locally installed package set strictly
loads the admitted checkpoint, preserves exact forward behavior, or supports exact
autograd. They do prove that the prior search boundary was incomplete and that the
quantized branch may not be terminated solely from absence of a model-local hook.

A separate administrative trigger exists: the GitHub repository API currently
reports `crogers2287/jlens` as `visibility=public`, despite the program being handled
as a private repository. Until repository visibility is independently verified and,
if necessary, restored, this is a privacy blocker for any non-public artifact.

## Binding classification

Reclassify commit `42a7b243b62ec340113dd9d6cd0c24bb043e0a13` from a hard branch
termination to:

`q35q_load_manifest_runtime_path_unresolved`

The following evidence remains usable:

- the pinned artifact and the directly instantiated Transformers 5.13.1 source
  class use different pre-conversion expert representations;
- no model-class-local numbered-to-packed conversion hook was found;
- coarse module-set equality does not establish strict tensor loadability;
- no exact local runtime identity or conversion plan has passed admission.

The following are not established:

- that no supported loader-level transformation exists;
- that the exact installed Optimum/GPTQModel/Defuser path cannot load the artifact;
- that a current, immutable GPTQModel runtime cannot reproduce the intended
  numbered-expert representation;
- that any such runtime preserves exact forward or derivative semantics;
- that the Q35Q quantized branch is scientifically viable.

The overall outcome remains:

`q35q_artifact_admission_blocked`

## Required runtime-path audit

Before the load-manifest gate may pass or the quantized branch may be terminated:

1. Freeze the complete candidate runtime tuple: Transformers package build and
   source commit, Optimum, GPTQModel, Defuser, Accelerate, PyTorch, CUDA, kernel
   backend, architecture dispatch, configuration classes, and loader entry point.
2. Inspect the exact runtime path actually selected by the admitted checkpoint,
   including Transformers global conversion mappings, the GPTQ quantizer's
   `convert_model()` call, GPTQModel model-definition dispatch, Defuser fused-block
   replacement/materialization, QuantLinear replacement, and checkpoint loading.
3. Produce an aggregate-only conversion-plan manifest before tensor payloads are
   staged. For every numbered expert and each `qweight`, `qzeros`, `scales`, and
   `g_idx` tensor, identify the exact target module, expected shape and dtype,
   ordering, fusion/defusion operation, and backend owner. Require zero ambiguous,
   missing, extra, duplicated, ignored, or silently synthesized entries.
4. Add a synthetic production-path integration fixture that uses the real pinned
   loader stack on a tiny Qwen3.5-MoE-shaped model. It must prove numbered expert
   conversion, quantization-auxiliary loading, expert ordering, gate/up identity,
   strict key consumption, deterministic output, and backward behavior for the
   operations that Q35Q intends to differentiate.
5. If the installed Transformers-plus-Optimum route fails, evaluate the immutable
   GPTQModel-plus-Defuser route already documented as supporting Qwen3.5-MoE. This
   is runtime admission, not permission to improvise a conversion or inspect weight
   values to design one.
6. If every pinned supported route fails the synthetic and metadata conjunction,
   then close the GPTQ branch as `q35q_quantized_runtime_unavailable` with exact
   package/commit identities and failing evidence. Do not infer branch failure from
   source representation alone.
7. Preserve a separate exact-forward and VJP/JVP parity gate after strict loading.
   Successful inference loading is not autograd admission.

## Repository privacy gate

While the repository API reports public visibility:

1. Do not commit task text, prompts, operands, outputs, token IDs, telemetry arrays,
   hidden states, router traces, Jacobian data, weights, caches, credentials, local
   paths, sealed labels, per-task predictions, or any reversible derivative of
   those artifacts.
2. Permit only aggregate program-control records already allowed by the frozen
   status/privacy rules.
3. Record repository visibility as unresolved until an independent GitHub metadata
   read reports `private` or the operator explicitly establishes that public
   visibility is intentional and compatible with the program's data boundary.
4. No later scientific phase may begin while repository visibility and artifact
   destination controls disagree.

## Execution boundary

Continue in this order:

1. verify repository visibility and preserve the aggregate-only write boundary;
2. complete the frozen runtime-path and conversion-plan audit;
3. prove strict synthetic load behavior through the real loader stack;
4. run the single adversarial Phase-0 conjunction;
5. stage weights only after that conjunction passes;
6. obtain an independently authorized and verified GPU-resource transition;
7. prove exact quantized forward and VJP/JVP parity before fitting;
8. only then proceed to a confound-controlled correctness-monitor benchmark and a
   separate Agents-A1-native transfer phase.

M38E remains terminally closed at `inconclusive`. No completed-error predictor,
semantic-workspace correctness monitor, safe early-exit or truncation rule,
causal expert localization, routing intervention, correction policy, activation
steering result, Agents-A1 transfer, or production utility is established.