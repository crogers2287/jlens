# Steer addendum — Q35Q AST dispatch and source-pin composition correction

Date: 2026-07-17

This addendum is binding program control. It preserves every existing privacy,
sealed-data, provenance, verifier, exact-set, resource, production-gating, and
claim-boundary rule. It does not authorize weight staging, tensor-payload retrieval,
model execution, GPU use, hidden-state or router capture, gradient work, or any
scientific claim.

## Trigger

Commit `2649e285c3742d6137bf3fa9616875f1bf844f65` replaces the prior substring
conversion-plan drift hint with an AST-based verifier. Commit
`86eed1969d50961ac45e5bffd6f6461f7ddaae88` adds a pure source-digest equality
helper. Both are useful partial engineering progress. Neither establishes the
claimed admission-grade structural/source conjunction.

The overall Q35Q outcome remains:

`q35q_artifact_admission_blocked`

Repository visibility is still reported by GitHub as `public`. The aggregate-only
repository boundary remains binding. No private prompts, outputs, token data,
telemetry arrays, hidden states, router traces, Jacobians, sealed labels, weights,
caches, credentials, host paths, or per-task predictions may be committed.

## AST verifier defects

The AST verifier does not yet prove the exact runtime-selected conversion plan.

1. It collects `qwen3_5_text` and `qwen2_moe` entries from any dictionary literal
   anywhere in the parsed file. It does not bind those entries to the exact mapping
   object selected by the admitted loader dispatch.
2. Its composition check accepts an assignment to any subscript target named
   `qwen3_5_moe_text` when the right-hand side references any subscripts named
   `qwen3_5_text` and `qwen2_moe`. The target and referenced objects are not required
   to be the same runtime mapping object.
3. It checks operation names but ignores constructor arguments. The prior binding
   requirement for exact dimensions is therefore not satisfied. A wrong
   `MergeModulelist(dim=...)` or `Concatenate(dim=...)` can pass.
4. It requires the expected source patterns to be present but does not require exact
   source-pattern equality. Extra or duplicate source patterns can pass.
5. It does not require exact converter multiplicity. Additional converters targeting
   the same packed expert tensors can coexist with one valid-looking converter and
   still produce a pass.
6. It does not prove absence of a later overwrite, mutation, conditional replacement,
   or alternate dispatch object after the inspected assignments.
7. The synthetic tests do not cover decoy entries in a different mapping object,
   wrong operation dimensions, extra source patterns, duplicate relevant converters,
   or a later overwrite of the selected mapping.

The reported `structural_pass=true` is therefore classified:

`q35q_conversion_ast_repair_partial`

It is not a conversion-plan admission pass.

## Source-pin composition defects

`bind_source_digests()` is a useful pure equality primitive, but the repository does
not contain a committed live composition that independently derives both sides of the
comparison.

1. Repository search finds the helper only in its implementation and unit tests.
   No production CLI reads the exact installed source files, hashes their raw bytes,
   loads frozen expected identities, and emits the aggregate conjunction result.
2. The committed telemetry record exposes only digest prefixes. It does not contain
   the complete expected SHA-256 identities or an immutable upstream blob/package
   reference from which they can be independently reproduced.
3. No committed evidence binds the expected identities to an exact upstream wheel,
   sdist, repository commit, blob path, and package build. Deriving expected hashes
   from the same installed bytes would remain self-binding.
4. The helper is not composed with package-version, module-path, import-origin,
   loader-entry-point, and runtime-dispatch admission in one production path.

The reported source-digest pin is therefore classified:

`q35q_runtime_source_pin_repair_partial`

It does not make the AST verification admission-grade.

## Required repair

Before the conversion-plan/source sub-gate may pass, the repository must contain one
committed production-path composition satisfying all of the following.

1. Freeze the exact upstream identities for Transformers and every source file used
   by the structural and model-construction verifiers. Bind package name, version,
   build, immutable repository commit or distribution artifact, canonical path, full
   SHA-256, module qualname, import origin, and selected loader entry point.
2. Derive expected full digests independently from the frozen upstream artifact or
   immutable blob. Do not derive expected values from the installed runtime bytes.
3. Read the installed source files through the exact runtime import path, hash the
   raw bytes, and compare observed values with the independently frozen identities.
4. Parse and verify the exact top-level runtime mapping object selected by the
   admitted dispatch. Decoy dictionaries, unrelated aliases, and alternate objects
   must not satisfy the check.
5. Require exact source-pattern lists, exact target patterns, exact converter counts,
   exact operation ordering, and exact constructor arguments, including merge and
   concatenation dimensions.
6. Prove that `qwen3_5_moe_text` is constructed from the admitted entries on that same
   mapping object and is not subsequently overwritten, conditionally replaced, or
   mutated before dispatch.
7. Add adversarial integration tests that fail on:
   - valid entries in a different mapping object;
   - wrong merge or concatenation dimensions;
   - extra or duplicate source patterns;
   - duplicate relevant converters;
   - a later mapping overwrite or mutation;
   - a valid AST paired with a wrong but well-formed source digest;
   - self-bound expected and observed source identities; and
   - a correct package version with a wrong import origin or loader entry point.
8. Execute the same production composition used by the tests against the admitted
   runtime and emit only aggregate, public-safe evidence.

The pure AST and digest helpers may remain as components, but neither may be labeled
complete or comprehensive until this composition passes.

## Runtime and scientific order

The next technically credible order remains:

1. complete exact source, package, dispatch, and conversion-plan admission;
2. freeze and admit the GPTQModel, Defuser, Optimum if present, Accelerate, PyTorch,
   CUDA, and selected backend tuple;
3. run the tiny synthetic Qwen3.5-MoE fixture through the real pinned
   GPTQModel/Defuser/`BACKEND.GPTQ_TORCH` path;
4. prove strict one-time quantization-tensor consumption, expert/fusion ordering,
   forward parity, activation VJP/JVP parity, finite-difference agreement,
   determinism, and right-to-wrong adversarial failures;
5. run the complete adversarial Phase-0 conjunction;
6. stage full weights only after that conjunction passes;
7. obtain a separately authorized GPU-resource transition; and
8. measure exact forward and derivative parity before fitting any Jacobian lens.

The absence of Optimum/GPTQModel in the currently reported environment is a runtime
blocker, not evidence that the quantized path is impossible. The unrelated GPU tenant
must remain untouched unless an explicit resource release is recorded.

## Claim boundary

M38E remains terminally closed at `inconclusive`. No Q35Q Phase-0 admission, strict
GPTQ load, exact quantized forward equivalence, activation JVP/VJP parity, local
fitting feasibility, Agents-A1 transfer, completed-error prediction, semantic
workspace correctness monitor, safe early exit or truncation rule, causal expert
localization, routing intervention, correction policy, activation steering, or
production utility is established.
