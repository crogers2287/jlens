# STEER ADDENDUM — Q35Q range provenance and reproducible live-adapter correction

Date: 2026-07-17

Status: **binding correction; CPU/storage/network metadata-only repair authorized; no weight staging, GPU execution, model instantiation, scientific capture, early-exit action, routing intervention, or production claim authorized.**

This addendum incorporates the complete current `steer.md`, every prior binding
addendum, and remote head `05daef44a9272431f52f90a956f40c9aac9af251`.
It supersedes only the Q35Q range-provenance and metadata-header sub-gate claims
identified below. Every sealed-data, verifier, privacy, provenance, exact-set,
exact-gradient, parity, resource, cleanup, comparator, nuisance-control,
multiplicity, production-gating, and stop rule remains binding.

## Executive finding

Commit `05daef44a9272431f52f90a956f40c9aac9af251` contains useful fail-closed
range-response helpers and a useful live metadata observation, but it does not
establish the claimed complete, independently reproducible Phase-0 metadata-header
sub-gate pass. Classify it as:

`q35q_phase0_metadata_header_gate_repair_partial`

The overall outcome remains:

`q35q_artifact_admission_blocked`

The format-hardened Safetensors parser from commit
`f94eae09be8d7bf2d4757e57c0b625db316ddea6` remains useful engineering evidence.
The following observations from the live run may remain descriptive, aggregate-only
evidence:

- 14 pinned shard requests reportedly returned ranged responses;
- 124611 tensor records reconciled to the pinned weight index;
- the embedding and language-model-head shapes were reported as `[248320, 2048]`;
- no tensor payload range was intentionally requested;
- no GPU, model instantiation, hidden-state, routing, JVP, VJP, fitting, generation,
  or scientific capture occurred.

These observations are not yet a complete admission sub-gate because the committed
production path does not prove the claimed identity conjunction and cannot reproduce
the live run from repository code alone.

## Binding defects

### 1. Wildcard or absent total size passes

`parse_content_range()` maps `Content-Range: bytes START-END/*` to `total=None`.
`verify_range_response()` compares total size only when both the observed total and
declared size are non-`None`. A wildcard total or missing declared size therefore
passes, despite the claim that the exact response total is required to equal an
independently declared immutable shard size.

A complete range-provenance gate must reject `*`, missing totals, missing declared
sizes, booleans, zero, negative, or non-integer size evidence.

### 2. OID shape is checked, not immutable identity equality

`_bind_oid()` accepts any lowercase 64-hex string and records it in
`bound_oids`. The value is not compared with an independently resolved expected
OID inside a committed production composition, is not tied to an exact repository,
revision, and shard path tuple, and does not constrain the HTTP request or response.
A fabricated but correctly shaped digest passes the helper.

The gate may not describe this as per-shard immutable-OID binding until an expected
Hub/LFS identity is independently derived and equality-bound to the exact shard
descriptor used by the live path.

### 3. The requested pinned URL is not an exact artifact descriptor

The URL check requires only a `/resolve/<40-hex>/` substring. It does not require
exact equality for:

- repository identity;
- the frozen revision;
- the requested shard path;
- the expected OID and declared size associated with that path.

A URL for another repository, another immutable commit, or another shard can satisfy
the regex. Downstream index reconciliation may detect many such substitutions, but
artifact identity must fail at the provenance boundary rather than rely on a later
semantic mismatch.

### 4. Redirect claims are not observable in the committed interface

The injected `http_get` returns only `(status, headers, body)`. It does not return
the final response URL or redirect history. The implementation therefore cannot
establish its documented claim that a redirect which drops or changes immutable
identity is rejected. Only the pre-request URL is inspected.

The repaired implementation must either expose and validate the redirect chain or
narrow its claim to evidence it actually verifies. It may not infer final-response
identity from an unobserved redirect path.

### 5. The live adapter is uncommitted and not reproducible

The commit adds `src/q35q_range_fetch.py` and synthetic tests, but no committed live
CLI/adapter composes:

1. immutable Hub repository metadata;
2. exact repository/revision/path/OID/size descriptors;
3. the real ranged HTTP transport;
4. the format-hardened header parser;
5. index-to-header reconciliation;
6. aggregate evidence emission.

The reported live rerun therefore cannot be reproduced, audited, or adversarially
exercised from the repository at the inspected head. A shell-session result is not
production-path admission evidence.

### 6. Adversarial coverage is incomplete

The committed tests do not require failure for:

- wildcard `Content-Range` total;
- missing declared size;
- boolean, zero, or negative declared sizes;
- wrong repository with a valid 40-hex revision;
- wrong immutable revision with a valid shape;
- wrong shard path;
- arbitrary valid-shaped but incorrect OID;
- redirect or final-URL identity mismatch;
- a live adapter that self-binds expected and observed descriptors.

## Required repair

### A. Freeze an exact expected shard descriptor

Before any header request, independently derive and freeze one descriptor per shard:

`{repo_id, revision, path, lfs_oid_or_blob_identity, declared_size}`

Requirements:

- `revision` is the exact admitted immutable commit;
- `path` is an exact member of the pinned weight index and remote manifest;
- OID/blob identity and size come from immutable public repository metadata, not
  from downloaded local bytes and not from the observed HTTP response;
- expected and observed values are produced by separate code paths and compared by
  equality;
- missing, ambiguous, unsupported, contradictory, or self-bound identity evidence
  fails closed as `q35q_provenance_blocked` or
  `q35q_artifact_admission_blocked`.

### B. Require exact numeric range totals

For every ranged response require:

- status exactly `206`;
- exact requested start and end;
- a present positive integer total, rejecting wildcard `*`;
- total exactly equal to the frozen declared size;
- body length exactly equal to the requested length;
- strict integer validation rejecting booleans.

### C. Bind request identity and observable transport behavior

The live adapter must construct the request from the frozen descriptor and require
exact repository, revision, and path equality before transport. If redirects are
followed, the transport result must expose enough history to validate the permitted
redirect policy. HTTPS downgrade, unexpected host class, changed request path before
the immutable resolver, or unobservable redirect behavior is a block, not a pass.

Do not claim that ranged header bytes cryptographically verify the entire shard
payload. The permitted claim is narrower: immutable Hub metadata, exact descriptor
binding, exact ranged-response provenance, valid Safetensors header format, and
index/header reconciliation.

### D. Commit and test the real live composition

Add a repository CLI/adapter that uses the same composition in tests and live work.
It must:

- resolve immutable descriptors independently;
- reject self-binding;
- use the provenance range fetcher;
- invoke the format-hardened parser and index reconciliation;
- emit only aggregate, public-safe evidence;
- preserve no-payload, no-weight, no-GPU, and cache-isolation boundaries.

Add production-path tests for every defect above, including wrong-but-valid-shaped
identities and a deliberately self-bound descriptor provider.

### E. Fresh rerun and allowed outcome

After repair, run the full repository test suite, privacy/no-text checks,
provenance checks, and commit-safety checks. A fresh live rerun may record exactly
one of:

1. `q35q_phase0_metadata_header_gate_passed`, only when the complete committed
   production path and independent identity conjunction pass;
2. `q35q_artifact_admission_blocked`, with the narrow failing condition;
3. `q35q_provenance_blocked`, when immutable public identity cannot be established;
4. `host_execution_authority_unavailable`, only if the already-authorized
   CPU/storage/network path is genuinely unavailable.

Until then, the metadata-header gate is partial and weight staging remains
prohibited.

## Remaining Q35Q order

After a genuine metadata-header sub-gate pass, the existing order remains:

1. freeze and verify the packed-source to numbered-GPTQ expert representation map;
2. prove exact source-derived versus artifact-derived module-set equality;
3. complete non-self-bound tokenizer and source/package identity admission;
4. route remote enumeration, checksum, storage, cleanup, resume, and cache isolation
   through the repaired staging orchestration;
5. compose one final Phase-0 conjunction with adversarial production-path tests;
6. stage weights only after the genuine aggregate Phase-0 pass;
7. wait for a separately authorized and verified dual-3090 transition;
8. pin the exact TP/autograd runtime before any exact JVP/VJP work.

No current GPU tenant may be signalled, stopped, displaced, or treated as released
from low utilization.

## External-evidence boundary

Current primary-source evidence supports future transparent comparators, not a
change to the active Q35Q execution order:

- EACL 2026, *Look Before You Leap: A Lookahead Reasoning Quality Gate for
  Speculative Decoding*, uses base-model hidden-state geometry to score draft
  prefixes. It supports a future decision-point geometry comparator under frozen
  calibration and right-to-wrong regression accounting; it does not establish safe
  truncation or transfer to Agents-A1.
- ACL 2026, *Trajectory Signatures of Deception in Large Language Models*, reports
  lightweight trajectory-geometry signals at uncertain decision points, with strong
  model- and behavior-type dependence. It supports a low-dimensional trajectory
  comparator, not a general correctness monitor.
- Findings of ACL 2026, *Knowing When to Quit: Diagnosing and Training LLMs to Abort
  Futile Reasoning*, changes model behavior through capability-aligned training. It
  is intervention evidence and does not authorize an observation-only monitor to
  abort, retry, refuse, or repair.
- ACL 2026, *Masked by Consensus: Disentangling Privileged Knowledge in LLM
  Correctness*, finds domain-specific privileged correctness information for factual
  tasks but no consistent self-representation advantage for mathematical reasoning.
  This reinforces task/family stratification and prohibits assuming a universal
  Agents-A1 correctness signal.

A future M39 launch amendment may preregister prompt-final, decision-point geometry,
trajectory, confidence, metadata, and route-path comparators with train-fold-only
preprocessing, nested selection, family-disjoint outer evaluation, nuisance
controls, and explicit right-to-wrong accounting. No paper-supplied layer,
threshold, direction, performance number, or intervention policy transfers to
Agents-A1.

Reddit remains lead-only. No r/LocalLLaMA claim located in this cycle supplied
independently reproducible exact-gradient parity, frozen evaluation, or
Agents-A1-scale evidence.

## Claims that remain prohibited

No exact GPTQ/NF4 autograd, quantized Jacobian/JVP/VJP parity, Agents-A1 transfer,
completed-error prediction, semantic-workspace correctness monitoring, safe early
exit, safe truncation, dynamic abstention, causal expert localization, forced
routing, correction policy, activation steering, or production utility is
established.
