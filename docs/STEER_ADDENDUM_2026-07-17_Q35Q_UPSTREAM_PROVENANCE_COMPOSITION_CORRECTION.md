# Binding steer addendum: Q35Q upstream-provenance composition correction

Date: 2026-07-17

Status: binding program-control correction

Applies to commit `9e63862b3350d10349d75c3c6b8a4e85058b01f4` and supersedes any stronger interpretation of its source-provenance telemetry or heartbeat language.

## Executive classification

Commit `9e63862...` is classified as:

`q35q_upstream_provenance_reference_partial`

The aggregate Phase-0 outcome remains:

`q35q_artifact_admission_blocked`

The commit establishes a useful immutable reference artifact and a pure comparison helper. It does **not** establish production-path installed-runtime admission or a composed non-self-bound source-closure pass.

## Evidence retained as established

The following may be retained as bounded engineering evidence:

1. A frozen public identity is recorded for the Transformers 5.13.1 wheel, sdist, and source commit.
2. `verify_wheel_and_extract()` can verify supplied wheel bytes against the frozen wheel SHA-256 and derive member digests from those verified bytes.
3. `compare_installed_to_upstream()` can compare two caller-supplied digest maps and report missing, extra, and mismatched entries.
4. Synthetic unit tests exercise basic wheel-hash, missing-member, malformed-archive, and digest-map mismatch cases.
5. No weights, model payloads, model execution, GPU execution, hidden states, router traces, gradients, sealed labels, or per-example scientific records were committed or authorized.

## Superseded claims

The following claims are not admissible from the committed repository state:

- `installed_source_bound_to_upstream=true` as a production Phase-0 result.
- The expected-digest independence gate is fully resolved.
- A committed live CLI downloads the wheel and composes upstream extraction with installed-runtime hashing.
- The current runtime-conversion adapter has consumed the new independent expectations.

The repository contains no changed live adapter in commit `9e63862...`. The existing `scripts/q35q_conversion_admission.py` still emits `expected_digests_independent=false`, does not import the new provenance module, and does not call either new helper. The live execution reported in telemetry is therefore not reproducible through the committed production path and cannot satisfy the final conjunction.

## Additional fail-closed corrections

Before the provenance helper can participate in admission, repair all of the following:

1. Validate frozen SHA-256 strings as exact lowercase hexadecimal values, not length-only strings.
2. Reject duplicate ZIP member names before converting the archive member list to a set.
3. Reject duplicate requested member paths and require exact canonical relative POSIX member names.
4. Require the exact admitted source-closure set rather than an arbitrary caller-supplied nonempty list.
5. Bind the imported Transformers package to the exact installed distribution and its `dist-info` ownership records.
6. Derive the live closure from the actual imported dispatch callable, returned converters, nested operations, model/configuration classes, and eventual loader entry point using canonical import origins.
7. Obtain installed digests inside the same clean subprocess that obtains the live objects; do not accept caller-injected observed digests or an asserted independence boolean.
8. Download and verify the frozen upstream artifact inside the committed adapter, then compare independently derived expectations with those same live source bytes in one invocation.
9. Emit one aggregate evidence record from that invocation and keep full source digests, host paths, caches, credentials, and local environment details outside the public repository.
10. Add adversarial integration tests covering duplicate ZIP entries, non-hex pins, duplicate requested paths, shadow/editable distributions, wrong `dist-info` ownership, monkeypatched live objects, incomplete source closure, correct files reached through an unadmitted loader, and self-consistent forged digest bundles.

## Required next execution order

1. Compose upstream-wheel verification, installed-distribution ownership, live-object source closure, and exact digest equality in one committed clean-subprocess adapter.
2. Pass the adversarial production-path provenance conjunction.
3. Freeze the complete GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and `GPTQ_TORCH` runtime tuple.
4. Run the synthetic Qwen3.5-MoE strict-load fixture with one-time quantization-tensor consumption and expert/fusion ordering checks.
5. Prove quantized forward, activation-VJP, activation-JVP, and finite-difference parity.
6. Run the complete Phase-0 conjunction.
7. Stage weights only after every prerequisite passes.
8. Require a separately authorized GPU-resource transition before full-model work.
9. Begin Jacobian fitting only after exact derivative parity.

## Privacy and scientific boundaries

GitHub currently reports this repository as public. Until visibility is corrected and independently verified, only aggregate program-control records may be committed. Prompts, outputs, token IDs, per-task predictions, verifier labels, hidden states, router telemetry arrays, Jacobian data, weights, caches, credentials, and host-local paths remain prohibited.

M38E remains terminally closed at `inconclusive`. No preregistered gate is weakened or reopened. Detection remains separate from correction, retry, abort, truncation, routing intervention, activation steering, and production deployment.

## Research interpretation

No public source reviewed with this correction changes the scientific sequence. Current hidden-state, routing-telemetry, and early-exit work remains comparator or engineering evidence only. None establishes exact quantized Jacobian parity, Agents-A1 transfer, universal correctness awareness, safe truncation, or production utility.
