# STEER ADDENDUM — Q35Q live-composition self-binding correction and metadata-only header gate

Date: 2026-07-17

Status: **binding correction; CPU/storage/network metadata-only work authorized; no weight staging, GPU execution, model instantiation, or scientific capture authorized.**

This addendum incorporates the complete current `steer.md`, every prior binding
addendum, and remote head `bd86525ff5cf0d7130822b155b68be3c69e66b46`.
It supersedes only the Q35Q live-composition status claims identified below.
Every sealed-data, verifier, privacy, provenance, exact-set, exact-gradient,
parity, resource, cleanup, comparator, nuisance-control, multiplicity,
production-gating, and stop rule remains binding.

## Executive finding

The first real-artifact composition is useful partial engineering evidence, but
its reported phrase **“4/5 validators pass” is not an admissible Phase-0 result**.
Classify commit `bd86525ff5cf0d7130822b155b68be3c69e66b46` as:

`q35q_live_composition_probe_partial`

For gate purposes, retain only the live architecture-config and GPTQ-config
checks. Reclassify the reported source-identity and tokenizer passes as
**self-bound and therefore not established**. The load-manifest validator
correctly remains blocked. The aggregate program outcome remains:

`q35q_artifact_admission_blocked`

No Q35Q scientific result is invalidated because no weights were loaded, no
model was instantiated, no GPU work occurred, and no hidden-state, route, JVP,
VJP, fitting, generation, or scientific capture occurred.

## Binding defects in the live composition

### 1. Source identity is self-compared

The live path constructs one `ident` object and calls:

`validate_source_identity(ident, ident)`

The observed runtime source identity and the expected immutable source identity
therefore come from the same bytes and object. Equality succeeds by
construction. This directly violates the existing requirement that the expected
identity be derived independently from the pinned source/package provenance and
then compared with the observed installed runtime mapping.

The committed `source_identity_all_required_pass=true` field is superseded for
gate purposes.

### 2. The load allow-list is self-compared

The live path derives `admitted` from `model.safetensors.index.json` and calls:

`validate_load_manifest(admitted, admitted, ...)`

This cannot prove equality between a source-derived text-only module allow-list
and the weight-index-derived admitted set. The record correctly lists this as an
open gate, but it may not be counted as a partially passing load-manifest proof.

### 3. Tokenizer expectations are self-derived or hard-coded

The live path supplies observed and expected tokenizer values from the same
runtime tokenizer object or the same freshly computed digest. In particular:

- observed and expected tokenizer classes are identical by construction;
- normalization and cleanup are hard-coded rather than independently derived;
- expected BOS/EOS/PAD identities are copied from the observed runtime object;
- expected ID-sequence, chat-render, and tokenizer-manifest digests are set equal
  to the observed digests;
- `special_token_behavior_ok=True` is asserted rather than derived from an
  explicit test.

The correction allowing a genuinely absent BOS via `None == None` is valid at
the pure-comparator level. It does not convert the live self-comparison into
independent admission evidence.

The committed `tokenizer_admission_all_required_pass=true` field is superseded
for gate purposes.

### 4. The repaired staging orchestration was not exercised

The live script documentation says the real remote manifest and immutable
checksums flow through `run_staging_orchestration`, but the implementation uses
direct `hf_hub_download` calls and does not invoke the repaired orchestration or
its manifest, checksum, free-space, cleanup, resume, cache-isolation, and final
reconciliation conjunction.

Broad exception handling also labels every failed small-file download as
optional without preserving a typed provenance reason. Required and optional
files must be declared before download; required-file failures must fail closed
with a specific aggregate blocker.

The first live probe therefore does not close the production-composition gate.

## Required corrected live composition

The next live composition must execute one production path and satisfy all of
the following before emitting any pass label:

1. Derive the expected source commit/file identity from immutable pinned package
   and source provenance, separately derive the observed installed mapping, and
   compare them by equality.
2. Derive the complete expected text-only module allow-list from the pinned
   implementation source or a deterministic meta-device construction that does
   not inspect the weight index; independently derive the admitted set from the
   pinned weight index; require exact equality.
3. Derive expected tokenizer class, normalization, cleanup, special-token map,
   chat-template identity, tokenizer-file manifest, and private-fixture digests
   from immutable files through an independent path. Derive observed values from
   the admitted runtime tokenizer. Do not copy observed fields into expected
   fields.
4. Replace `special_token_behavior_ok=True` with explicit deterministic tests of
   BOS, EOS, PAD, added-special-token, no-special-token encoding, decode, and
   re-encode behavior.
5. Route remote enumeration, download, checksum reconciliation, free-space,
   partial cleanup, deterministic resume, cache isolation, and final manifest
   reconciliation through the repaired staging orchestration used by the CLI.
6. Declare required versus optional small files before execution. Missing,
   unsupported, ambiguous, or provenance-incomplete required files fail closed.
7. Add production-path integration tests that specifically fail on source,
   allow-list, tokenizer, and digest self-binding; a pure comparator test is not
   sufficient.
8. Emit one final conjunction. No component may be described as passed when its
   expected value was derived from the same observed object or byte stream.

## Metadata-only Safetensors header gate

The current status treats mandatory parameter shapes as requiring full
weight-side staging. That is unnecessary and creates an avoidable ordering
conflict. The Safetensors format places tensor names, dtypes, shapes, and data
offsets in a JSON header that can be retrieved with small HTTP Range requests;
tensor payload bytes are not required. See the official Safetensors metadata
parsing documentation and format specification:

- `https://huggingface.co/docs/safetensors/en/metadata_parsing`
- `https://github.com/huggingface/safetensors#format`

Authorize one bounded **metadata-only header admission** step under the existing
CPU/storage/network authority:

1. Use only shard names listed by the pinned immutable weight index and URLs
   resolved at the pinned revision.
2. Bind each shard to independently obtained immutable Hub/LFS identity and
   declared file size before fetching any header bytes.
3. Request bytes `0-7`, parse the little-endian header length, reject malformed
   responses, redirects to mutable identities, non-206 range behavior, wrong
   `Content-Range`, or a header length above a frozen 64 MiB per-shard ceiling.
4. Request exactly bytes `8` through `7 + header_length`; do not request or cache
   tensor payload bytes and do not create a full shard file.
5. Parse only tensor name, dtype, shape, and data offsets. Require valid UTF-8
   JSON, supported dtypes, nonnegative integer shapes, ordered nonoverlapping
   offsets, and final offsets within the independently declared shard size.
6. Require the weight index and all shard headers to reconcile exactly: every
   indexed tensor appears once in its declared shard, no unindexed tensor is
   admitted, every expected shard is covered, and no extra shard is consulted.
7. Keep raw tensor names, local paths, URLs containing credentials, response
   headers, and cache locations private. Commit only aggregate counts, booleans,
   immutable public revision/OID identities where already permitted, and digests.
8. Treat any server that ignores Range and returns payload bytes as a hard stop;
   discard the response and record `q35q_artifact_admission_blocked`.

This authorization is not weight staging. It exists solely to obtain mandatory
shape evidence without downloading tensor payloads. Full shard staging remains
prohibited until every independent Phase-0 prerequisite, including this header
reconciliation and the final production conjunction, genuinely passes.

## Research boundary

The July 2026 ACL paper **NEAT: Neuron-Based Early Exit for Large Reasoning
Models** is a credible future observation lead for token-level overthinking and
exit-associated activation dynamics. It does not establish safe early exit on
Agents-A1, and it does not change the active Q35Q milestone. Any future M39 or
separate early-exit comparator must use nested selection, independent holdout,
right-to-wrong accounting, and model-specific parity gates.

Apple's July 2026 **Path-Constrained Mixture-of-Experts** work further supports
cross-layer expert paths as a useful observational unit. It does not authorize
router intervention or transfer its trained architectural conclusions to
Agents-A1.

The June 2026 causal audit **From Observation to Intervention: A Causal Audit of
Expert Importance in Mixture-of-Experts Models** (`arXiv:2606.10703`) reports
that common observational routing summaries did not predict token-level causal
expert importance across the tested models. This reinforces the existing rule:
route telemetry may be used as an observation-only comparator, but cannot by
itself license pruning, forced routing, expert suppression, causal localization,
or production intervention.

No new public source establishes Jacobian parity, correctness prediction,
semantic-workspace monitoring, safe truncation, causal expert localization, or
production utility on Agents-A1.

## Required next outcome

The next Q35Q operational commit must record exactly one of:

1. `q35q_phase0_admission_corrected_passed`, only after independent source,
   allow-list, tokenizer, staging-orchestration, metadata-header, and final
   conjunction evidence all pass;
2. `q35q_artifact_admission_blocked`, with one narrow evidence-backed blocker;
3. `q35q_provenance_blocked`, when immutable identity cannot be established;
4. `host_execution_authority_unavailable`, only when the already-authorized
   CPU/storage/network path is genuinely unavailable.

Weight staging, GPU execution, model instantiation, exact-gradient work, M39
capture, intervention, and production claims remain prohibited until their
separate existing gates pass.
