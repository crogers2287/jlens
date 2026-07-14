# Steering addendum — Agents-A1 4B release announcement and artifact-admission gate

Date: 2026-07-14

Status: **binding program-control addendum; no scientific capture authorized**.

This addendum incorporates `steer.md`, `CODEX_AUTOSTEER.md`, the M38E frozen
protocol, the amended M39 preregistration draft, and every existing sealed-data,
verifier, privacy, provenance, exact-set, cap-escalation, power, multiplicity,
retry, production, repository-hygiene, and stop rule. Nothing here changes an
active M38E process, row, task, family, band, seed, cap, threshold, verifier,
eligibility rule, comparator gate, or production gate.

## New external fact

Official repository commit
`InternScience/Agents-A1@3be929bb3c7471469dc7dd98cc3c856fc23e99dd`
added the dated statement: **“2026.7.14: The 4B model has been released.”**

At the time of this review, the official Hugging Face Agents-A1 collection and
the InternScience organization model listing did not expose an identifiable
Agents-A1 4B artifact. They continued to expose the 35B Agents-A1 variants and a
separate 4B `Agents-K1` model. `Agents-K1` is not Agents-A1 and may not be used as
an Agents-A1 substitute.

The program status is therefore:

`official-release-announced / exact-artifact-unresolved`

The old statement that no official 4B release had been announced is superseded.
The release announcement alone does not establish that a downloadable,
immutable, architecture-compatible, research-ready checkpoint has been
identified.

## Binding artifact-admission gate

No Agents-A1 4B scientific row, Jacobian, VJP, finite-difference probe, hidden
state, router trace, expert trace, fit, calibration result, or performance claim
may be collected until a separate committed admission record freezes and
verifies all of the following from primary artifacts:

1. exact hosting organization and repository/model identifier;
2. immutable revision or commit SHA and complete file manifest;
3. cryptographic digests for every weight shard, configuration, tokenizer,
   tokenizer configuration, generation configuration, chat template, and custom
   modeling-code file used;
4. license and model-card provenance, including the relationship to the released
   Agents-A1 35B model;
5. exact architecture and `model_type`, including whether the checkpoint is
   dense or MoE;
6. layer count, hidden size, intermediate size, vocabulary, context limit,
   attention design, routed and shared expert counts, top-k, router
   normalization, dispatch behavior, and residual/expert combination semantics;
7. exact tokenizer and chat-template parity or documented incompatibility with
   the pinned 35B Agents-A1 runtime;
8. supported `transformers`, vLLM, llama.cpp, or other execution path, including
   all required remote/custom code and package revisions;
9. finite-value load smoke, deterministic tokenization fixtures, and
   output-disabled metadata inspection performed without outcome-bearing study
   rows;
10. proof that no raw weights, private paths, environment data, secret-linked
    digests, process evidence, or private scientific artifacts enter the public
    repository.

A mutable branch name, model-card announcement, collection entry, filename,
unofficial quantization, mirror, community conversion, or guessed repository
name is insufficient. Missing or contradictory evidence produces
`artifact-admission-blocked`, not an inferred pass.

## Comparability and claim boundary

The admitted 4B artifact must be classified before any study is designed:

- **Architecture-matched MoE:** it may serve as the smaller-model engineering
  platform for separately preregistered Jacobian/VJP/finite-difference
  approximation work after the forward-only M39 gate is satisfied.
- **MoE with materially different routing or expert topology:** it may be used
  only as a bounded engineering surrogate. Transfer to 35B requires separate
  architecture-stratified validation and cannot be assumed.
- **Dense or otherwise non-comparable model:** it may test generic Jacobian
  tooling and memory arithmetic only. It cannot validate MoE routing claims,
  expert-level semantics, Agents-A1 35B transfer, or production behavior.

No result on the 4B model may be described as a result on the 35B model. No
cross-model pooling may satisfy power, class-balance, calibration, minimum-effect,
or replication gates. Layer, expert, hidden-size, and feature definitions may not
be copied mechanically across models when their tensors or semantics differ.

## Program sequence remains unchanged

1. Continue and finalize M38E unchanged, or record its frozen blocked/negative
   outcome honestly.
2. Keep M39 as the forward-only, observation-only **35B** completed-error
   comparator. The 4B announcement does not authorize replacing the pinned M39
   model, collecting M39 rows early, or using 4B outcomes to select M39 features,
   layers, thresholds, classifiers, or task families.
3. Advance beyond M39 only if a prespecified forward-only block clears every
   frozen M39 parity, provenance, privacy, power, calibration, minimum-effect,
   multiplicity, nuisance-increment, router-increment, ambiguity, independence,
   and locked-holdout gate.
4. After that gate, admit the exact 4B artifact under this addendum and commit a
   separate approximation-study preregistration.
5. Compare full Jacobians where feasible against reduced-target VJPs and bounded
   finite differences; require approximation-error, rank-stability,
   finite-value, phase-localized parity, memory, runtime, privacy, and predictive
   increment gates.
6. Only after the smaller-model approximation gate passes may the program run
   the frozen one-sequence 35B backward high-memory technical smoke. That smoke
   carries no scientific claim.

## Current claim boundary

- The official 4B release announcement is established.
- The exact official 4B research artifact, architecture, and immutable revision
  are not yet established by the inspected primary listings.
- No Agents-A1 4B Jacobian, VJP, approximation, router, hidden-state, expert, or
  error-prediction result exists in this program.
- M38E remains incomplete and has no finalized scientific outcome.
- M39 remains design-only and capture-prohibited.
- No safe truncation, early exit, semantic correctness, causal repair, routing
  intervention, activation steering, or production utility is established.
- The research program is not complete.
