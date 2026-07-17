# Steer addendum — Q35Q live-adapter distribution and operation-origin correction

Date: 2026-07-17

This addendum is binding program control. It preserves every existing privacy,
sealed-data, provenance, verifier, exact-set, resource, production-gating, and
claim-boundary rule. It does not authorize weight staging, tensor-payload retrieval,
model execution, GPU use, hidden-state or router capture, gradient work, or any
scientific claim.

## Trigger

Commit `8d83197880ca63a743147691537c71aca5836b60` adds a committed CPU-only
conversion/source/dispatch adapter and hardens converter-count checks. This is useful
partial engineering progress. Its reported `installed_runtime_admission_pass=true`
does not establish an independently bound installed runtime.

The overall Q35Q outcome remains:

`q35q_artifact_admission_blocked`

GitHub still reports the repository as `public`. The aggregate-only repository
boundary remains binding. No private prompts, outputs, token data, telemetry arrays,
hidden states, router traces, Jacobians, sealed labels, weights, caches, credentials,
host paths, or per-task predictions may be committed.

## Usable evidence

The new work establishes only the following:

1. A committed adapter now imports the installed Transformers runtime and invokes
   `get_checkpoint_conversion_mapping("qwen3_5_moe_text")` directly.
2. The returned list is checked for exactly three objects, exactly one prefix change,
   exactly two weight converters, exact selected source/target patterns, and selected
   operation names and dimensions.
3. Three locally selected source files are read and hashed.
4. The adapter honestly keeps the independent-upstream digest gate false and retains
   `q35q_artifact_admission_blocked`.

This is legitimate live-observation progress. It is not package, source-closure,
class-origin, loader-entry, or upstream-provenance admission.

## Remaining defects in the live adapter

1. **The imported package is not bound to the installed distribution.**
   `pkg_root` is derived from `transformers.__file__`, while the version is obtained
   independently through `importlib.metadata.version("transformers")`. A shadowed,
   editable, alternate-root, or locally substituted `transformers` import can remain
   internally contained under its own root while the metadata query returns version
   `5.13.1` from a different installed distribution.
2. **The claimed exact source-file set is tautological.**
   `files` is constructed with the same three literal keys as `PINNED`, so
   `set(files) == set(PINNED)` is true by construction. It does not enumerate the
   actual source closure used by the live dispatch, converter classes, nested
   operation classes, model construction, or loader entry point.
3. **Two source paths are constructed rather than resolved from the live objects.**
   `core_model_loading.py` and the Qwen3.5 model file are joined under `pkg_root`.
   The adapter does not use the import specification or `inspect.getsourcefile()` to
   prove that those are the files defining the live callable and classes.
4. **Nested operation classes are not origin-bound.**
   `class_modules_bound` checks only `type(o).__module__` for the three top-level
   mapping objects. `MergeModulelist` and `Concatenate` operation objects are reduced
   to class names and `dim` values; their module, qualname, source file, and digest are
   not checked. A shadow operation class with the expected name and dimension can
   pass.
5. **Converter identity is underbound.**
   The adapter checks converter `__module__` but not exact class qualname, source file,
   source digest, distribution ownership, or object identity. A different class in
   the admitted module with the same extracted attributes can pass.
6. **The dispatch callable and loader entry point are not bound.**
   The identity, import origin, source digest, and qualname of
   `get_checkpoint_conversion_mapping` are not checked. The eventual GPTQ loader
   entry point is not part of this conjunction.
7. **Source-byte integrity and live-object integrity are separable.**
   Genuine package files can hash correctly while the imported callable, returned
   objects, or nested operation classes are monkeypatched in memory. A clean,
   isolated import and direct live-object source binding are still required.
8. **Installed artifact provenance is absent.**
   Version equality and local source hashes do not identify the exact wheel, sdist,
   editable checkout, build, installation record, or file ownership that supplied the
   imported runtime.
9. **The documentation overstates operation binding.**
   The live-status record says converter/operation classes are module-bound, but the
   implementation binds only top-level mapping-object classes.

Commit `8d831978...` is therefore classified:

`q35q_live_runtime_adapter_repair_partial`

Its `installed_runtime_admission_pass` field is usable only as a local observation
conjunction, not as Phase-0 runtime admission.

## Independently resolvable upstream identity

The Transformers 5.13.1 PyPI release is now concretely identifiable and must be used
rather than deriving expectations from installed bytes:

- wheel: `transformers-5.13.1-py3-none-any.whl`
- wheel SHA-256: `53f0ea8aa397e29244c2377ba981bcaf0c87adcf44fbdd447ef6306522afcacd`
- sdist: `transformers-5.13.1.tar.gz`
- sdist SHA-256: `1e2452d6778a7482158df5d5dacf6bf775d5b2fdcfce33caaf7f6b0e5f3e3397`
- attested source commit: `4626421dc6b741a329300682a6408246ee465490`

These public identities make independent derivation feasible. Their existence is not
an admission pass. The production path must determine which exact artifact supplied
the installed runtime and fail if that provenance cannot be established.

## Required repair

Before this sub-gate may pass, one committed production adapter must satisfy all of
the following.

1. Download exactly one frozen upstream PyPI artifact through a pinned manifest,
   verify its complete SHA-256 and publication identity, and extract the expected
   source bytes without consulting the installed package.
2. Determine the installed distribution with `importlib.metadata.distribution()`,
   bind its canonical root, `dist-info`, `WHEEL`, `METADATA`, and `RECORD`, and prove
   that the imported `transformers` package is owned by that distribution. Reject
   editable installs, path injection, namespace confusion, and alternate roots unless
   separately preregistered and immutably bound.
3. Require exact correspondence between the admitted upstream artifact and the
   installed distribution. Version equality alone is insufficient.
4. Derive the live source closure from the actual imported objects using import specs
   and source inspection. Bind the exact module, qualname, canonical path,
   distribution ownership, and complete digest for:
   - `get_checkpoint_conversion_mapping`;
   - every top-level returned converter object;
   - every nested operation object;
   - the Qwen3.5-MoE model/configuration classes used by the admitted path; and
   - the selected quantized loader and Defuser entry points once that tuple is frozen.
5. Replace the tautological literal-key check with exact equality between the frozen
   upstream source manifest and the independently observed live source closure.
6. Verify exact converter and operation class identities, not names alone. Require
   exact module qualnames, constructor/state schemas, source/target patterns,
   operation order, dimensions, and total multiplicity.
7. Execute the admission in a clean subprocess with controlled `sys.path`, disabled
   user-site injection, and no pre-imported Transformers modules. Detect and reject
   in-memory monkeypatching or object/source disagreement.
8. Bind the actual loader entry point and the dispatch callable in the same
   conjunction; a correct mapping reached through an unadmitted loader path must fail.
9. Add adversarial integration tests rejecting:
   - an imported shadow package paired with genuine distribution metadata;
   - an editable or alternate-root package with version `5.13.1`;
   - a hardcoded three-key map that does not match the live source closure;
   - constructed paths that differ from the live object source files;
   - a shadow `MergeModulelist` or `Concatenate` class;
   - a same-module wrong converter class or wrong class qualname;
   - a monkeypatched dispatch function with unchanged on-disk bytes;
   - a genuine mapping reached through the wrong loader entry point;
   - a valid wheel hash paired with an installed sdist/editable build; and
   - a same-version distribution whose `RECORD` or source bytes differ.
10. Emit only aggregate, public-safe evidence. Do not commit local paths, environment
    identifiers, caches, credentials, tensor data, model data, or per-example records.

## Runtime and scientific order

The technically credible order remains:

1. complete independently bound Transformers package/source/dispatch admission;
2. freeze and admit an exact GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA,
   and `GPTQ_TORCH` backend tuple at immutable versions or commits;
3. execute the tiny synthetic Qwen3.5-MoE strict-load fixture through that exact
   runtime;
4. prove one-time quantization-tensor consumption, expert and fusion ordering,
   forward parity, activation VJP/JVP parity, finite-difference agreement,
   determinism, and adversarial right-to-wrong failures;
5. run the complete Phase-0 conjunction;
6. stage full weights only after the complete conjunction passes;
7. obtain a separately authorized GPU-resource transition; and
8. measure exact forward and derivative parity before fitting any Jacobian lens.

## Research-program claim boundary

M38E remains terminally closed at `inconclusive`. No Q35Q Phase-0 admission, strict
GPTQ load, exact quantized forward equivalence, activation JVP/VJP parity, local
fitting feasibility, Agents-A1 transfer, completed-error prediction, semantic
workspace correctness monitor, safe early exit or truncation rule, causal expert
localization, routing intervention, correction policy, activation steering, or
production utility is established.
