# Steer addendum — Q35Q packer saturation and fixture independence gates

Date: 2026-07-23

This addendum is binding program control. It preserves every existing privacy,
sealed-data, verifier, provenance, exact-set, exact-gradient, parity, resource,
cleanup, commit-safety, comparator, nuisance-control, production-gating, and stop
rule. It does not authorize weight staging, tensor-payload retrieval, model
execution, GPU use, hidden-state or router capture, gradient work, scientific
evaluation, intervention, or production use.

## Trigger

GPTQModel commit `3c458297c9bdaefed40739fcd1d2b8adfe9a5335`, dated
2026-07-23, corrects a pack-time numerical defect. Its Python block packer,
original packer, GPU pack path, and CPU extension now clamp reconstructed integer
quantization codes to `[0, 2**bits - 1]` before integer conversion and bit
packing. The accompanying regression test covers 2-, 3-, 4-, and 8-bit codes and
requires identical packed weights across the admitted implementations.

The upstream correction explains the failure mode: an unchecked rounded code
outside the representable range can wrap modulo `2**bits` during bit packing,
turning a small boundary reconstruction error into a full-range weight error.

This is material to the planned synthetic Qwen3.5-MoE differentiable-runtime
fixture because a fixture produced through a packer can appear internally
consistent while testing the wrong integer codes. It does not establish that the
currently preferred immutable GPTQModel candidate is unsafe for consuming an
already valid prepacked checkpoint, and it does not authorize silently moving the
runtime pin to GPTQModel `main` or to the corrective commit.

## Binding object separation

The Q35Q admission program must treat the following as separate artifacts:

1. the quantization-code producer and calibration procedure;
2. the code-to-bitstream packer;
3. the prepacked checkpoint artifact;
4. the loader and tensor-mapping path;
5. the dequantizer and eager `GPTQ_TORCH` forward path; and
6. the independently implemented reference decoder.

A pass by one object cannot be used as evidence for another. In particular:

- packer round-trip agreement does not prove loader provenance or strict tensor
  consumption;
- loader success does not prove that the packed integer codes represent the
  intended synthetic weights;
- dequantized forward parity against a reference derived from the same packer is
  self-consistent evidence, not independent evidence; and
- an upstream fix on `main` does not modify or certify an older immutable runtime
  candidate.

## Synthetic-fixture construction gate

Before the tiny Qwen3.5-MoE fixture can support strict-load, forward, VJP, JVP,
or finite-difference admission, its packed tensors must be generated and checked
under one prospectively frozen method:

1. Freeze the exact producer and packer identities, including commit, source
   digest, implementation path, bit width, pack dtype, group size, symmetry
   convention, zero convention, scale convention, `g_idx`, shape, ordering, and
   endianness.
2. Record the intended integer code tensor before packing and require every code
   to satisfy the frozen representable range.
3. Prefer direct construction from a small explicit integer-code tensor followed
   by an independently implemented packer. If an upstream packer is used, the
   independent reference must decode the emitted bitstream without importing or
   calling the same packer or dequantizer implementation.
4. Require exact equality between the intended integer codes and the independently
   decoded integer codes before any floating-point dequantization comparison.
5. Require exact equality of packed outputs across every implementation claimed
   equivalent, including pure Python, CPU extension, and GPU packers when those
   paths are in scope.
6. Keep the fixture's producer/packer evidence separate from the real loader's
   one-time consumption evidence for `qweight`, `qzeros`, `scales`, and `g_idx`.
7. Prohibit deriving the reference floating-point weights by dequantizing the same
   packed output through the same runtime under test.

A fixture that only proves `pack -> dequantize -> expected` through one shared
implementation is not independently admitted.

## Boundary-code adversarial tests

The fixture and packer admission suite must include prospectively frozen cases
covering:

- exact minimum and maximum representable codes;
- one-code underflow and overflow before packing;
- large finite underflow and overflow;
- every admitted bit width;
- asymmetric and symmetric zero conventions when supported;
- nontrivial `g_idx` ordering and repeated groups;
- group-boundary and word-boundary transitions;
- negative, zero, subnormal, and extremely small scales under the admitted scale
  policy;
- pure Python, CPU-extension, and GPU implementation disagreement; and
- a deliberately wrapping legacy packer that must fail the independent-code
  equality check.

When the frozen packer semantics specify saturation, out-of-range reconstructed
codes must saturate before integer conversion and bit packing. When the artifact
contract instead requires rejecting out-of-range codes, the packer must fail
closed. Silent modular wraparound is never admissible.

## Runtime-candidate consequence

The preferred bounded candidate remains:

`GPTQModel + Defuser + BACKEND.GPTQ_TORCH eager activation-autograd path`

The previous inspected commit
`d2945a35397e2892abc3df45e0a95236058c55a0` remains an engineering lead, not a
frozen admitted runtime. Commit `3c458297c9bdaefed40739fcd1d2b8adfe9a5335`
becomes an additional candidate only after the complete runtime tuple,
distribution ownership, live source closure, loader identity, strict-load,
forward, activation-VJP, activation-JVP, finite-difference, determinism, and
adversarial gates pass.

The program may also retain an older consumer commit if the admitted real
checkpoint is prepacked and the consumer never invokes the affected pack paths,
but that fact must be established from complete live source closure and execution
tracing. It may not be assumed from API names or intended usage.

## Agents-A1 scaling consequence

This correction does not change the established order:

`Q35Q provenance -> strict loading -> forward/VJP/JVP/finite-difference parity ->
sealed cheaper-monitor comparisons -> Agents-A1-4B bridge -> minimal
Agents-A1-35B route telemetry -> sparse/transcoder comparisons -> Jacobian Lens`

It adds one requirement to the bridge: every synthetic or converted MoE fixture
must bind its integer-code producer, packer, packed artifact, loader, dequantizer,
and independent reference separately. Derivative parity on a self-consistent but
incorrectly packed fixture cannot support transfer to Agents-A1 or any comparable
large MoE.

## Claim boundary and current state

Established:

- GPTQModel corrected a real pack-time saturation defect in its current upstream
  branch.
- Unchecked out-of-range reconstructed codes can wrap during bit packing.
- The planned Q35Q synthetic fixture therefore requires code-level independent
  validation in addition to floating-point round-trip tests.

Not established:

- that the admitted Q35Q checkpoint contains out-of-range reconstructed codes;
- that the older inspected GPTQModel consumer misloads valid prepacked tensors;
- that the corrective commit passes Q35Q loader, forward, or derivative admission;
- strict Q35Q tensor consumption, expert ordering, forward parity, VJP parity,
  JVP parity, finite-difference parity, or scale feasibility; or
- transfer to Agents-A1, safe early exit, truncation, routing intervention,
  activation steering, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`
