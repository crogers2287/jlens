# Steer addendum — Q35Q runtime-composition provenance correction

Date: 2026-07-17

This addendum is binding program control. It preserves every existing privacy,
sealed-data, provenance, verifier, exact-set, resource, production-gating, and
claim-boundary rule. It does not authorize weight staging, tensor-payload retrieval,
model execution, GPU use, hidden-state or router capture, gradient work, or any
scientific claim.

## Trigger

Commit `bec1f4f5c7738e0f2a40dfa3163cace6cb915afc` adds a dispatch-object
inspection helper. Commit `df02bd7f9492f1227ed66332e260d1496759d866` adds a
single pure conjunction over package-version, import-origin, source-digest, and
conversion-plan inputs. These are useful partial engineering repairs. They do not
establish the claimed live production-path admission.

The overall Q35Q outcome remains:

`q35q_artifact_admission_blocked`

GitHub still reports the repository as `public`. The aggregate-only repository
boundary remains binding. No private prompts, outputs, token data, telemetry arrays,
hidden states, router traces, Jacobians, sealed labels, weights, caches, credentials,
host paths, or per-task predictions may be committed.

## Usable evidence

The new work establishes only the following:

1. A structured representation of the currently expected Qwen3.5-MoE conversion
   entries can be checked for selected target patterns, selected source patterns,
   operation ordering, and operation dimensions.
2. A pure conjunction can fail closed when injected test values disagree.
3. The synthetic tests exercise several wrong-version, wrong-digest, wrong-origin,
   wrong-dimension, and duplicate-converter cases.

This is legitimate logic-level progress. It is not live runtime admission.

## Dispatch-verifier defects

1. `verify_dispatch_conversion()` receives an already extracted caller-supplied list.
   It does not itself invoke the admitted loader entry point or prove that the list
   came from `get_checkpoint_conversion_mapping("qwen3_5_moe_text")` in the admitted
   runtime.
2. The verifier does not require exact total mapping equality. It requires one
   gate/up converter, one down converter, and at least one matching prefix change,
   but does not require exactly one prefix change or exactly three total converters.
   Additional converters that do not use the two exact target-list values can pass.
3. A broader, wildcard, aliased, or differently represented converter capable of
   affecting the same packed expert tensors is not rejected by the exact-list
   `packed_targeting` filter.
4. Converter and operation identity is reduced to Python class names and `dim`
   attributes. A shadow class with the same name and attributes can satisfy the
   extracted representation unless its module origin and source identity are bound.
5. The claim that the checked object is the final live dispatch object is not proven
   by the pure verifier. That provenance must be established by the production
   adapter that obtains and immediately verifies the object.

Commit `bec1f4f5...` is therefore classified:

`q35q_dispatch_conversion_repair_partial`

## Unified-composition defects

1. Repository search finds `run_runtime_conversion_admission()` only in its
   implementation and synthetic tests. No committed live CLI or adapter invokes the
   real runtime import path, loader dispatch, source-byte reader, and verifier in one
   reproducible execution.
2. The function accepts every observed value from its caller: package version,
   import origin, observed digests, expected digests, and the extracted dispatch
   mapping. A mutually self-consistent synthetic bundle can pass without touching
   the installed runtime.
3. `expected_digests_independent=True` is a declarative boolean, not evidence of
   independence. The function does not bind the expected map to a frozen upstream
   wheel, sdist, repository commit, blob path, artifact checksum, or signed manifest.
4. Import-origin admission uses string suffix matching. A shadow or alternate path
   ending in `transformers/conversion_mapping.py` can pass. Canonical realpath,
   admitted distribution root, import spec, package metadata, and file identity are
   not jointly checked.
5. The source-digest binder accepts any nonempty equal key set. The production
   conjunction does not require exact equality with the frozen
   `PINNED_SOURCE_FILES` set, so an arbitrary one-file map can pass.
6. The documented loader-entry-point binding is absent from the function signature
   and conjunction.
7. Package-version equality alone does not bind the wheel/build/source identity.
   Two distributions or editable installs with the same version string can differ.
8. The returned label `q35q_runtime_conversion_admission_pass` is therefore too
   strong for this injected pure function. It may describe a unit-level conjunction
   pass only, not runtime admission.

Commit `df02bd7...` is therefore classified:

`q35q_runtime_admission_composition_partial`

## Required repair

Before this sub-gate may pass, one committed production adapter must satisfy all of
the following without caller-supplied observed identity fields.

1. Load a frozen public manifest that identifies the exact package/distribution,
   version, build or immutable upstream artifact, repository commit or blob,
   canonical relative paths, complete SHA-256 values, module qualnames, and loader
   entry point.
2. Establish expected-digest independence from that immutable upstream artifact.
   Independence must be derived and reproducible; it may not be asserted by a
   boolean supplied to the verifier.
3. Resolve the actual installed distribution through package metadata and the
   runtime import system. Canonicalize real paths and require containment under the
   admitted distribution root. Reject editable, shadowed, namespace-confused, or
   alternate-origin imports unless explicitly preregistered and independently bound.
4. Require the exact frozen source-file key set, including every file used by model
   construction, conversion mapping, dispatch, Defuser integration, and the selected
   quantized loader path. Reject missing and extra keys.
5. Hash the actual imported source bytes and compare them with the independently
   frozen complete identities.
6. Invoke the exact admitted loader dispatch inside the production adapter, obtain
   `get_checkpoint_conversion_mapping("qwen3_5_moe_text")`, extract it immediately,
   and pass that extraction directly to the verifier without an injectable
   intermediate representation in the live path.
7. Require exact total converter count, exact prefix-converter multiplicity, exact
   converter and operation module qualnames, exact source and target lists, exact
   operation order and arguments, and rejection of every unrecognized converter or
   alias capable of touching the admitted expert tensors.
8. Bind the actual loader entry point, package import origin, dispatch function,
   returned mapping object, and all inspected class definitions in the same
   conjunction.
9. Add adversarial integration tests that reject:
   - a forged self-consistent injected identity bundle;
   - a true independence boolean paired with locally derived expected digests;
   - an arbitrary equal one-file digest map;
   - a shadow path with the correct suffix;
   - a same-version different wheel or editable install;
   - a shadow converter or operation class with the expected class name;
   - an extra prefix converter;
   - an extra unrelated or wildcard converter capable of touching expert tensors;
   - a valid extracted list not obtained from the live admitted dispatch; and
   - a correct conversion mapping reached through the wrong loader entry point.
10. Emit only aggregate, public-safe evidence. Full public source hashes may be kept
    only when already authorized by the aggregate-only policy; no host paths or
    private environment identifiers may be committed.

## Runtime and scientific order

The technically credible order remains:

1. complete this independently bound live source/package/dispatch admission;
2. freeze and admit an exact GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA,
   and `GPTQ_TORCH` backend tuple at immutable versions or commits;
3. run the tiny synthetic Qwen3.5-MoE fixture through that exact loader stack;
4. prove strict one-time quantization-tensor consumption, expert and fusion ordering,
   forward parity, activation VJP/JVP parity, finite-difference agreement,
   determinism, and adversarial right-to-wrong failures;
5. run the complete Phase-0 conjunction;
6. stage full weights only after the complete conjunction passes;
7. obtain a separately authorized GPU-resource transition; and
8. measure exact forward and derivative parity before fitting any Jacobian lens.

Current GPTQModel development has continued beyond the earlier Qwen3.5-MoE release,
so a moving `main` branch or broad version range is not admissible. The runtime tuple
must use exact immutable package and source identities.

## Claim boundary

M38E remains terminally closed at `inconclusive`. No Q35Q Phase-0 admission, strict
GPTQ load, exact quantized forward equivalence, activation JVP/VJP parity, local
fitting feasibility, Agents-A1 transfer, completed-error prediction, semantic
workspace correctness monitor, safe early exit or truncation rule, causal expert
localization, routing intervention, correction policy, activation steering, or
production utility is established.
