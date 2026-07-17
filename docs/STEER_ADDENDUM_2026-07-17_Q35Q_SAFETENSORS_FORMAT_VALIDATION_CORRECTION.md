# STEER ADDENDUM — Q35Q Safetensors format-validation correction

Date: 2026-07-17

Status: **binding correction; CPU/storage/network metadata-only repair authorized; no weight staging, GPU execution, model instantiation, scientific capture, or production claim authorized.**

This addendum incorporates the complete current `steer.md`, every prior binding
addendum, and remote head `33159e6d31c1bfa262879bcb65973f3d8cdb0cc5`.
It supersedes only the Q35Q metadata-header admission claims identified below.
Every sealed-data, verifier, privacy, provenance, exact-set, exact-gradient,
parity, resource, cleanup, comparator, nuisance-control, multiplicity,
production-gating, and stop rule remains binding.

## Executive finding

Commit `f57354b930866d471560a5be3c9eaa670c5221fb` is useful metadata-retrieval and
index-to-header reconciliation work, but its live result may not be classified as
complete Safetensors shape admission. Classify it as:

`q35q_phase0_metadata_header_reconciliation_partial`

The following aggregate observations may be retained as descriptive evidence:

- 14 pinned shard headers were reached without intentionally requesting tensor
  payload ranges;
- 124611 header tensor names reconciled to the pinned weight index and declared
  shard assignment;
- no extra or missing indexed tensor name was reported by that run.

The reported tensor shapes, dtypes, offsets, and full-file format integrity are
not yet admissible evidence because the parser accepts internally inconsistent
or noncanonical Safetensors headers. The overall program outcome remains:

`q35q_artifact_admission_blocked`

No scientific result is invalidated because no weights were loaded, no runtime
model was instantiated, no GPU work occurred, and no hidden-state, route, JVP,
VJP, fitting, generation, or scientific capture occurred.

## Binding defects in the metadata-header parser

### 1. Shape and dtype are not bound to the tensor byte span

The parser records `dtype`, `shape`, and `data_offsets` independently but never
requires:

`END - BEGIN == element_count(shape) * bytes_per_element(dtype)`

Consequently, a header can claim an arbitrary public architecture shape while
pointing to a much smaller or larger byte span and still pass. The committed unit
tests themselves construct examples with deliberately impossible shape-to-span
relationships and classify them as valid. This defeats the stated purpose of
obtaining independent shape evidence.

The repair must use an explicit, frozen dtype-size table and exact integer
arithmetic. Byte-aligned admitted dtypes must match their exact span. Empty
tensors must have a zero-byte span. Scalar tensors must have one element.
Unsupported or sub-byte dtypes must fail closed unless a separate exact packing
rule is committed and tested before use.

### 2. The byte buffer is not required to be entirely indexed

The current overlap check allows:

- a gap before the first tensor;
- gaps between tensors;
- unused trailing bytes after the final tensor.

The Safetensors format requires the byte buffer to be entirely indexed and to
contain no holes. After sorting spans, the parser must require the first nonempty
span to start at zero, every subsequent span to start at the prior end, and the
final end to equal the complete declared data-region length. Zero-length tensors
may share the current cursor only when their shape and dtype imply zero bytes.

### 3. Duplicate JSON keys are not rejected

Plain `json.loads` silently keeps one value when duplicate object keys are
present. Safetensors disallows duplicate keys. Parse with a duplicate-detecting
object-pairs hook and fail closed on duplicate tensor names, duplicate fields,
or duplicate `__metadata__` entries.

### 4. Header and metadata grammar are incompletely validated

The repair must require:

- the first header byte to be `{` exactly, before JSON parsing;
- only permitted trailing space padding after the JSON object;
- `__metadata__`, when present, to be a string-to-string map;
- each tensor record to contain exactly one valid `dtype`, `shape`, and
  `data_offsets` field, with no ambiguous duplicate fields;
- tensor names to be nonempty strings and not equal to the reserved metadata key.

### 5. Python booleans pass as integers

`bool` is a subclass of `int`. The current `isinstance(value, int)` checks admit
`True` and `False` as shape dimensions and offsets. All dimensions, offsets,
header lengths, and declared sizes must use strict integer checks that explicitly
reject booleans.

## Required repair and rerun

Before any header-gate pass label is restored, the production parser and tests
must satisfy all of the following:

1. Bind each dtype and shape to the exact byte-span length under a frozen dtype
   table and exact overflow-safe arithmetic.
2. Require complete hole-free coverage of the declared data region.
3. Reject duplicate JSON keys at every object level.
4. Enforce the Safetensors header-start, padding, record, and metadata grammar.
5. Reject booleans wherever an integer is required.
6. Add adversarial tests for wrong shape/right span, right shape/wrong span,
   leading/intermediate/trailing holes, duplicate tensor names, duplicate record
   fields, leading whitespace, invalid metadata values, boolean dimensions, and
   boolean offsets.
7. Preserve the existing index-to-shard exact-name reconciliation tests.
8. Rerun the metadata-only live gate against the same pinned immutable artifact
   and emit a new aggregate record. Do not reuse the previous pass field.
9. Continue to enforce exact HTTP Range status and `Content-Range`, immutable
   shard identity and size, no payload-range request, and no full-shard cache.
10. Emit only aggregate counts, booleans, permitted public architecture shapes,
    and permitted immutable public identities. Raw tensor names, local paths,
    credentials, response headers, cache locations, and environment values remain
    private and uncommitted.

Only a fresh repaired run may emit:

`q35q_phase0_metadata_header_gate_passed`

## Status of the source-derived allow-list commit

Commit `33159e6d31c1bfa262879bcb65973f3d8cdb0cc5` is retained as useful partial
engineering evidence that the observed installed text-only class can be
constructed on the meta device without weights or GPU memory and can provide a
module template independent of the weight index. It does not yet close admission.
The remaining requirements include:

- immutable expected source/package identity versus observed installed source;
- a frozen, tested packed-source to numbered-GPTQ expert representation map;
- exact source-derived versus artifact-derived module reconciliation;
- non-self-bound tokenizer expectations and explicit special-token behavior;
- repaired staging-orchestration composition;
- one production-path final conjunction with self-binding and provenance failure
  tests.

## Scientific boundary

This correction changes no scientific claim. Public work on Jacobian-space
readouts, hidden-state correctness probes, neuron-level early exit, semantic
convergence, and MoE routing remains comparator or design evidence only. No
public source currently establishes exact quantized Jacobian parity, completed-
error prediction, semantic-workspace correctness monitoring, safe truncation,
causal expert localization, repair, or production utility on Agents-A1.

## Required next outcome

The next Q35Q operational commit must record exactly one of:

1. `q35q_phase0_metadata_header_gate_passed`, only after the repaired parser and
   fresh live rerun satisfy every format, provenance, range, privacy, and
   reconciliation requirement above while all other Phase-0 gates remain
   separately tracked;
2. `q35q_artifact_admission_blocked`, with one narrow evidence-backed blocker;
3. `q35q_provenance_blocked`, when immutable identity cannot be established;
4. `host_execution_authority_unavailable`, only when the already-authorized
   CPU/storage/network path is genuinely unavailable.

Weight staging, GPU execution, runtime model instantiation, exact-gradient work,
M39 capture, intervention, and production claims remain prohibited until their
separate existing gates pass.
