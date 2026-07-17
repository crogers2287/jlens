# steer.md — canonical Q35Q provenance and runtime-admission directive

`CODEX_AUTOSTEER.md` remains the operating contract. This file is the current
source of truth for milestone selection.

This directive consolidates every binding protocol, correction, and steering
addendum present through parent head
`7ca183e039ac9b4da45aee7bb3d88c3c404ad066`. It supersedes older milestone and
status routing where they conflict with the state below. It does not weaken,
reopen, retune, or replace any privacy, sealed-data, verifier, provenance,
exact-set, exact-gradient, parity, resource, cleanup, commit-safety,
comparator, nuisance-control, multiplicity, production-gating, or stop rule.

## Current program state

### M38E

M38E is terminally closed at commit
`3debb97f703c82419a6cb4dde37d7aedf8a93f90` with outcome `inconclusive` and
blocker class `serving_restoration_unavailable_due_unrelated_gpu_tenant`.

Do not restart, rerun, repair, extend, reinterpret, or replace any M38E task,
row, family, attempt, cap, seed, threshold, verifier, outcome, or audit. The
stronger `m38e_completed_error_frontier_not_found` claim did not pass and may
not be inferred.

### Q35Q

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

No Q35Q weight staging, model execution, GPU execution, generation,
hidden-state capture, router capture, JVP, VJP, Jacobian fitting, sealed
scientific evaluation, or production use is authorized.

### Repository visibility and data boundary

GitHub currently reports `crogers2287/jlens` as public. Until repository
visibility is corrected and independently verified, commits are restricted to
aggregate program-control records and public-source engineering code or tests.

Do not commit prompts, outputs, rendered chats, token IDs, per-task
predictions, verifier labels, hidden states, router arrays, expert traces,
Jacobian data, gradients, model weights, tensor payloads, caches, credentials,
host-local paths, environment dumps, or private logs. A later visibility change
does not waive sealed-data or verifier rules.

## Established bounded engineering evidence

The following may be treated as bounded engineering evidence only:

1. Immutable revisions have been recorded for the admitted Qwen3.5-35B-A3B
   base and GPTQ repositories.
2. Strict configuration and weight-index parsers exist, including duplicate-key
   rejection and immutable content-identity checks.
3. Metadata-only Safetensors range retrieval and format validation have been
   implemented and reportedly reconciled 14 shards and 124,611 tensor records
   without intentional tensor-payload retrieval.
4. The full 40-layer text-only `Qwen3_5MoeForCausalLM` source model has been
   enumerated on the meta device after configuration admission.
5. A coarse source-to-artifact module-name reconciliation exists, including
   vision/MTP omission and packed-versus-numbered expert normalization.
6. Transformers conversion-dispatch inspection has progressed from substring
   checks to structured checks and a live imported-dispatch adapter.
7. A frozen public reference is recorded for the Transformers 5.13.1 wheel,
   sdist, and source commit.
8. Pure helpers can verify supplied upstream wheel bytes and compare supplied
   source-digest maps.
9. GPTQModel's eager Torch quantized-linear path is a technically credible
   candidate for activation differentiation because it dequantizes through
   Torch operations and uses ordinary Torch matrix multiplication.
10. No scientific Q35Q result has been produced.

These facts do not constitute Phase-0 admission.

## Superseded or inadmissible stronger claims

The following are not established by the committed repository:

- `installed_source_bound_to_upstream=true` as a production-path result;
- a complete non-self-bound source-closure pass;
- exact imported-package ownership by the frozen upstream distribution;
- exact live loader-entry-point identity;
- exact GPTQ numbered-expert to runtime-module conversion;
- strict one-time consumption of every checkpoint tensor;
- exact forward equivalence or activation-gradient correctness;
- availability of the dual-3090 resource window;
- feasibility or transfer to Agents-A1.

The current upstream-provenance helper is not composed into the committed live
conversion adapter. The current live adapter still lacks one clean-process
conjunction that independently derives upstream expectations and observed live
runtime identities.

## Active milestone — production-path upstream provenance composition

Complete one committed, reproducible, CPU-only, clean-subprocess adapter that
binds the actual imported Transformers runtime to independently verified
upstream artifacts and the live conversion dispatch.

### 1. Frozen upstream artifact admission

Require exact immutable identities for the admitted Transformers artifact.

- Validate every SHA-256 as exactly 64 lowercase hexadecimal characters.
- Download or receive the frozen wheel through an explicitly pinned public
  identity and verify the complete wheel bytes before reading members.
- Reject duplicate ZIP member names before any set or dictionary conversion.
- Reject duplicate requested member paths.
- Require canonical relative POSIX archive member names with no traversal,
  absolute paths, alternate separators, or ambiguous normalization.
- Derive expected source digests only from the independently verified upstream
  artifact. Do not derive expected values from installed bytes.

### 2. Imported distribution ownership

Bind the imported `transformers` package to the exact installed distribution.

- Resolve the live module import specification and canonical real path.
- Resolve the owning distribution and canonical distribution root.
- Require the imported package to belong to that distribution, not merely to a
  path ending in an expected suffix.
- Admit and hash the corresponding `dist-info` `WHEEL`, `METADATA`, and
  `RECORD` ownership records.
- Reject editable installs, shadow packages, namespace collisions, alternate
  distributions, and mismatched package metadata.

### 3. Live source closure

Derive the required source-file closure from the actual live objects used in
that same subprocess, including at minimum:

- the imported conversion-dispatch callable;
- every returned converter object;
- every nested operation object;
- the selected Qwen3.5-MoE model and configuration classes;
- the loader entry point that will construct, defuse, replace, and load the
  quantized model;
- any source module whose executable definitions determine expert conversion,
  tensor mapping, quantized-linear replacement, or loading behavior.

Bind each live object to exact module name, qualified name, canonical source
path, owning distribution, and full source digest. Do not accept a caller-
injected arbitrary file list or caller-injected observed digest map.

### 4. Exact live dispatch admission

Call the admitted conversion dispatch directly inside the production adapter.
Require exact structural equality, not class-name resemblance.

- Require the exact total converter count.
- Require exact prefix-converter multiplicity.
- Require exact source and target pattern lists with no extra or duplicate
  alternatives.
- Require exact operation types, defining modules, qualified names, dimensions,
  ordering, and composition.
- Reject later overwrite, mutation, monkeypatching, shadow classes, wildcard
  mappings, or mappings returned through an unadmitted callable.
- Bind the eventual GPTQModel/Defuser loader entry point separately from the
  Transformers checkpoint-name conversion mapping.

### 5. One non-self-bound conjunction

In one clean subprocess with controlled import paths:

1. verify the frozen upstream artifact;
2. derive expected source identities from that artifact;
3. resolve the actual imported distribution and live-object source closure;
4. derive observed source identities from those live objects;
5. invoke and inspect the actual live conversion dispatch;
6. compare exact expected and observed identities and structures;
7. emit one aggregate evidence record.

An asserted `expected_digests_independent` boolean is not evidence. A mutually
consistent caller-supplied identity bundle is not evidence.

### 6. Required adversarial integration tests

Exercise the same production adapter and reject at least:

- non-hex or wrong upstream hashes;
- duplicate ZIP entries;
- duplicate or noncanonical requested members;
- incomplete or extra source closure;
- shadow packages and editable installs;
- wrong `dist-info` ownership;
- package-version metadata from a different installation;
- monkeypatched dispatch callables or nested operations;
- correct-looking classes from wrong modules or distributions;
- wrong operation dimensions or ordering;
- extra, missing, duplicate, or wildcard converters;
- correct conversion mappings reached through an unadmitted loader;
- self-consistent forged expected and observed digest maps.

Pure unit tests of injected values do not satisfy this milestone.

### 7. Required outcome

After fresh tests, privacy scans, no-text checks, provenance checks, and
commit-safety checks, record exactly one of:

1. `q35q_runtime_provenance_composed_passed`, only if the full production-path
   conjunction passes;
2. `q35q_runtime_provenance_blocked`, with one narrow evidence-backed blocker;
3. `host_execution_authority_unavailable`, once, only if the already-authorized
   CPU/network/repository path is genuinely unavailable.

Do not publish unchanged status-only heartbeats in place of executing the
milestone.

## Required sequence after provenance composition

No step may be skipped or merged with a later scientific claim.

1. Freeze the complete GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA,
   and `GPTQ_TORCH` runtime tuple by immutable package/source identities.
2. Run a tiny synthetic Qwen3.5-MoE fixture through the exact pinned loader
   stack.
3. Prove strict one-time consumption of every synthetic `qweight`, `qzeros`,
   `scales`, and `g_idx` tensor, exact expert order, gate/up fusion identity,
   group metadata, shapes, dtypes, and zero missing, ignored, duplicated,
   ambiguous, or silently synthesized tensors.
4. Prove deterministic forward parity against an independently dequantized
   reference.
5. Prove activation-input VJP and JVP parity plus finite-difference agreement.
   Weight gradients are not required.
6. Run the complete adversarial Q35Q Phase-0 conjunction.
7. Stage full weights only after every Phase-0 prerequisite passes.
8. Require a separately authorized and verified GPU-resource transition.
9. Prove full-model quantized forward and derivative parity before Jacobian
   fitting.
10. Fit and evaluate Q35Q only under the frozen scientific protocol.
11. Run a separate detection-only correctness-monitor benchmark with
    family-disjoint evaluation and nuisance controls.
12. Design Agents-A1-native scaling only after Q35Q derivative parity and
    incremental monitor value are established.

## Agents-A1 scaling constraints

The technically credible path is:

`artifact/runtime admission -> synthetic strict-load proof -> quantized
forward/VJP/JVP parity -> Q35Q fitting -> sealed detection benchmark ->
Agents-A1-native instrumentation`

For any future Agents-A1 or comparable large-MoE monitor:

- use route paths and decision-point summaries as observational comparators;
- include prompt-final hidden-state, output-confidence, metadata, and simple
  geometric baselines;
- vary correct answers and truth labels within each family;
- use family-disjoint outer evaluation;
- residualize prompt length, response length, answer identity/format,
  difficulty, tool count, latency, finish reason, and task family;
- report per-family effects and sign reversals;
- separate tool-call errors, completed reasoning errors, truncation, malformed
  output, and verifier failures;
- require incremental predictive value over all baselines;
- keep detection separate from retry, abort, truncation, forced routing,
  correction, activation steering, and production deployment.

No public evidence currently establishes universal correctness awareness, safe
early exit, causal expert localization, Agents-A1 transfer, or production
utility.

## Resource and execution boundaries

The dual RTX 3090 boundary remains binding. Low utilization is not resource
release. Do not evict, pause, replace, or interfere with an unrelated tenant
without separate authorization and verified restoration/cleanup controls.

Before the provenance, strict-load, and derivative-parity gates pass:

- no full weight staging;
- no model instantiation with tensor payloads;
- no GPU kernels;
- no hidden-state or router capture;
- no Jacobian, JVP, or VJP capture on the full model;
- no scientific fitting or evaluation.

## Definition of completion

The research program is not complete while any claim above remains unproven.
A future terminal completion record must identify exact immutable runtime and
model identities, frozen protocols, sealed evaluation outcomes, passed privacy
and verifier audits, production-gating disposition, and the exact final remote
head. Failure or inconclusive outcomes count as completion only when the
preregistered stop rule explicitly permits terminal closure without replacing
or weakening the failed gate.
