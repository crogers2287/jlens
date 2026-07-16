# steer.md — repair the Q35Q Phase-0 orchestration before weights or GPU execution

`CODEX_AUTOSTEER.md` remains the operating contract. This file is the current
source of truth for milestone selection. It incorporates the complete prior
`steer.md` blob `2553634e1b67eca72e8f4c0d9f763a8cfb620b88`, every protocol and
addendum incorporated by that blob, and:

- `docs/STEER_ADDENDUM_2026-07-17_Q35Q_PHASE0_SECOND_CORRECTION_AND_M39_PREGEN_PROBE.md`.

This directive supersedes prior steer only where explicitly stated below. Every
sealed-data, verifier, privacy, provenance, exact-set, exact-gradient, parity,
resource, cleanup, commit-safety, comparator, nuisance-control, multiplicity,
production-gating, and stop rule remains binding. No frozen scientific result,
task, family, seed, threshold, verifier, sampling setting, token cap, power gate,
model, revision, quantization, layer, feature, outcome rule, or production gate
may be weakened, retuned, substituted, or inferred.

## Current established state

### M38E

M38E is terminally closed at commit
`3debb97f703c82419a6cb4dde37d7aedf8a93f90` with outcome `inconclusive` and
blocker class `serving_restoration_unavailable_due_unrelated_gpu_tenant`.

The frozen M38E record remains the sole admissible execution record:

- 288 official rows across 12 frozen cells;
- 94 pilot rows;
- zero full-band 4096 reruns;
- 382 total rows;
- no live M38E driver, ledger writer, or M38E-attributable GPU kernel;
- every frozen finalization audit passed except serving restoration;
- the stronger `m38e_completed_error_frontier_not_found` outcome was not
  committed because that gate did not pass.

Do not restart, rerun, repair, extend, reinterpret, or replace any M38E task,
row, family, attempt, cap, seed, threshold, verifier, outcome, or audit.

### Q35Q Phase-0 evidence

Commit `1123561ed4f360c14cf424bc0156842d2947b353` remains
`q35q_admission_staging_partial` only.

Commit `86538d44e133e6ae2b21c441d7c6dcfb3bab139f` is now classified as
`q35q_phase0_admission_repair_partial`, not a Phase-0 prerequisite pass.

Useful evidence retained from `86538d4...`:

- immutable revisions were resolved for the Qwen3.5-35B-A3B base and GPTQ
  repositories;
- selected public configuration and GPTQ fields match the expected values;
- the pinned GPTQ tokenizer loaded with `trust_remote_code=False`;
- deterministic IDs and an exact decode/re-encode result were observed on one
  neutral fixture;
- no weights, model instantiation, GPU execution, generation, hidden-state,
  router, JVP, VJP, fitting, or scientific capture occurred.

The committed `phase0_admission_prerequisites_pass=true` field is superseded for
gate purposes. `q35q_artifact_admission_blocked` remains active.

### Why the current Phase-0 pass is invalid

The binding second-correction addendum establishes six defects:

1. The actual staging path derives `admitted` only from files already present
   locally, so an expected remote file omitted by an interrupted download cannot
   reach the missing-file validator.
2. Expected and observed runtime checksums are both derived from the same local
   bytes, so artifact checksum reconciliation is self-referential.
3. Actual free space, temporary overhead, safety margin, partial cleanup,
   deterministic resume, and final reconciliation are absent from the overall
   conjunction.
4. Required pinned-source and admitted-load-manifest proofs remain absent for the
   text-only class, shared expert, Gated DeltaNet projections, final RMS norm,
   output head, vision omission, and MTP omission.
5. The tokenizer conjunction does not require chat-template identity, tokenizer
   manifest identity, normalization and cleanup settings, admitted special-token
   behavior, or model/tokenizer pairing.
6. Pure validator tests do not exercise the real orchestration path through
   remote enumeration, download, local discovery, checksum reconciliation,
   cleanup, resume, tokenizer admission, and final conjunction.

No scientific result is invalidated because no Q35Q scientific execution has
occurred.

### Resource boundary

The dual RTX 3090 resource boundary remains binding. Do not infer a free GPU
window from M38E closure or low utilization. Any transition away from an
unrelated tenant must be separately authorized and verified under the existing
resource and cleanup rules.

No Q35Q GPU work is permitted before complete artifact and runtime admission.

## Active milestone — Q35Q Phase-0 second repair

The next host-capable cycle must repair the orchestration, integration tests, and
aggregate record. CPU, storage, network, and repository-side work already
covered by the prior authorization may proceed. Weight staging and GPU work may
not proceed.

### 1. Independent expected manifest

Construct the expected admitted-name set from the pinned remote public manifest
before inspecting local presence. Require every expected admitted file to exist
locally. Never remove a missing name from the expected set merely because the
local file is absent.

Exclude only preregistered cache, lock, downloader metadata, timestamp,
temporary, partial, and host-specific paths. Reject unexpected public files,
path escapes, symlinks outside the staging root, and mutable identities.

### 2. Immutable checksum reconciliation

Bind expected checksums from immutable public repository metadata where
available, including LFS object identities. Compare them with locally computed
hashes. A missing, unsupported, ambiguous, or contradictory required checksum
identity records `q35q_provenance_blocked` or
`q35q_artifact_admission_blocked`; it is not a pass.

### 3. Storage and resumability gate

Before weight staging, record aggregate-only evidence for:

- actual free bytes at the isolated staging root;
- expected weight bytes for both repositories;
- temporary download overhead;
- a declared safety margin;
- partial-file detection and cleanup;
- deterministic interrupted-download resume;
- final immutable manifest and checksum reconciliation;
- cache and runtime isolation from unrelated workloads.

GPU memory ceilings are not storage-headroom evidence.

### 4. Exact source and load-manifest admission

Pin and review the exact model implementation source. The overall architecture
conjunction must include independent proof of:

- the admitted text-only `Qwen3_5MoeForCausalLM` class and source mapping;
- hidden size 2048, 40 layers, output width 248320, 256 routed experts, top-8,
  routed-expert width 512, and shared-expert width 512;
- shared-expert construction from pinned implementation source;
- exact hybrid linear-attention/full-attention schedule;
- Gated DeltaNet projection identities;
- final RMS normalization and untied language-model head;
- vision modules present in the repository but omitted from the admitted load
  manifest;
- MTP metadata present but MTP modules omitted from the admitted execution and
  load manifests;
- exact GPTQ identity, bit width, group size, and dynamic skip rules.

Configuration metadata alone is not source or load-manifest proof.

### 5. Complete tokenizer admission

Bind the tokenizer verdict to the immutable tokenizer-file manifest and model
identity. The final conjunction must require:

- tokenizer class and `trust_remote_code` setting;
- normalization and cleanup settings;
- explicit no-special-token encoding;
- separately tested admitted BOS, EOS, PAD, and special-token behavior;
- deterministic encoded length and private ID-sequence digest;
- exact deterministic decode/re-encode behavior;
- deterministic chat-template identity and rendering digest;
- exact model/tokenizer repository and revision pairing.

Raw fixture text, rendered chat text, and token IDs remain private and
uncommitted.

### 6. Orchestration-level tests

Add deterministic integration tests using a fake pinned repository and fake
downloader. Force each condition through the same orchestration used by the CLI:

- missing expected file;
- partial or interrupted download;
- stale cache metadata;
- extra unapproved file;
- wrong checksum;
- mutable or mismatched revision;
- path escape or external symlink;
- insufficient free space;
- cleanup failure;
- resume mismatch;
- missing chat template or special-token mismatch;
- architecture source or load-manifest mismatch.

A pure unit test of a validator is not proof that the production orchestration
can reach and enforce that validator.

### 7. Required operational outcome

Run fresh repository tests, privacy scans, artifact no-text checks, provenance
checks, and commit-safety checks.

The next Q35Q operational commit must record exactly one of:

1. `q35q_phase0_admission_corrected_passed`, with every binding prerequisite in
   the final overall conjunction;
2. `q35q_artifact_admission_blocked`, with one narrow evidence-backed blocker;
3. `q35q_provenance_blocked`, when immutable source or artifact identity cannot
   be established;
4. `host_execution_authority_unavailable`, once, only if the executing agent
   genuinely lacks the already-authorized CPU/storage/network path.

Do not publish unchanged status-only heartbeats in place of executing this
milestone. Do not stage weights before a genuine pass.

## Tensor-parallel runtime gate

Before any future dual-GPU execution, pin and review an immutable Transformers
runtime containing the equivalent of upstream commit
`259711a042c5858d8c48edf04aa97b7021fee4b3`, including the five Qwen3.5-MoE
Gated DeltaNet tensor-parallel plan entries:

- `in_proj_qkv`;
- `in_proj_z`;
- `in_proj_b`;
- `in_proj_a`;
- `out_proj`.

The eventual runtime must pin exact Transformers source, package build, PyTorch,
CUDA, model-source, quantization, kernel, and generated-configuration identities.
The explicit dual-3090 plan must account for the required full-channel all-gather
before depthwise convolution and remain within 23.0 GiB per GPU and 46.0 GiB
total.

A missing TP entry, source mismatch, hidden offload, model or kernel substitution,
OOM, placement mismatch, or resource breach is a hard stop. Do not use
`device_map="auto"`, approximation, or a weaker memory gate as proof.

## Program order after a genuine Phase-0 pass

1. Stage and verify weight artifacts using CPU, storage, and network only.
2. Admit the exact immutable runtime and text-only load manifest.
3. Wait for a legitimate, verified dual-3090 resource transition.
4. Run only the frozen one-sequence exact residual-input VJP gate on the admitted
   GPTQ path.
5. Record `q35q_gptq_autograd_unsupported` honestly before attempting the
   admitted NF4 fallback.
6. Require genuine autograd, non-`None`, nonzero, finite, repeatable VJPs, frozen
   weights, no hidden offload, output/hook parity, admitted routing regime,
   admitted runtime, and existing memory ceilings.
7. After a reverse-mode VJP passes, run only the separately preregistered exact
   JVP/VJP adjoint cross-check. Finite differences and approximate fallbacks are
   prohibited.
8. Produce aggregate route-regime, backward-cost, wall-time, storage, cleanup,
   provenance, privacy, and commit-safety evidence before the frozen
   eight-sequence micro-fit.
9. Preregister any larger selected-layer quantized Qwen3.5 base-model fit before
   capture and use deterministic horizontal prompt sharding with fp32 weighted
   merging and cross-worker agreement smokes.
10. Test transfer separately against identity transport and standard logit-lens
    comparators, including route overlap, route changes, and margin distributions.
11. Admit and fit a native quantized Agents-A1 lens only under a separate frozen
    target-artifact and quantization protocol.
12. Retain native BF16 Agents-A1 exact VJPs and fitting on admitted high-memory
    hardware as the final reference comparison.

Every quantized checkpoint is its own mathematical model. A quantized Qwen3.5
lens is not a BF16 lens and a transferred Qwen3.5 lens is not Agents-A1-native.

## M39 research-design boundary

M39 remains independent and may not borrow M38E or Q35Q rows, outcomes,
difficulty observations, selected examples, fitted directions, features, layers,
or thresholds. Scientific capture requires a complete committed launch amendment,
a fresh population, an admitted serving path, and every power, nuisance,
multiplicity, parity, provenance, privacy, resource, verifier, and leakage gate.

Current external evidence supports adding a future observation-only comparator,
not launching capture:

- arXiv:2606.14530 v2 and `CarloDiCicco/ReasoningLab` report strong nested-CV
  prediction of subsequent code correctness from a prompt-final hidden state in
  Qwen3-4B-Instruct, including train-fold-only prompt-length residualization;
- arXiv:2606.02628 reports strong mid-layer linear hallucination decodability in
  several 4-bit 7B-8B models;
- arXiv:2605.07260 supports executed-route margins and route utility as MoE
  observation leads, not intervention authority;
- arXiv:2603.23701 continues to disfavor prioritizing layer-wise early exit in
  large modern MoE models before model-specific intrinsic-exit and parity gates.

The future M39 launch amendment should preregister a **prompt-final
pre-generation hidden-state comparator** alongside frozen metadata, confidence,
route, and trajectory comparators. It must use train-fold-only preprocessing,
nested layer and regularization selection, task/family-disjoint outer evaluation,
and explicit residualization or matched controls for prompt length, task family,
difficulty metadata, and other frozen nuisance variables.

No paper-supplied layer, threshold, direction, or performance claim transfers to
Agents-A1. Reddit remains lead-only and produced no primary-source-backed change
in this cycle.

M39 remains observation-only. No counterfactual routing, router update, retry,
repair, tool invocation, truncation, early exit, intervention, activation
steering, or production control is permitted.

## Claims and privacy boundary

Established:

- M38E is terminally closed at `inconclusive`;
- the current Q35Q Phase-0 record is partial evidence, not an admission pass;
- the TP-plan source requirement is a credible engineering gate;
- prompt-final and mid-layer hidden-state probes are credible future comparators
  requiring independent validation.

Not established:

- Q35Q artifact or runtime admission;
- GPTQ or NF4 exact VJPs or JVPs;
- quantized Qwen3.5 or Agents-A1 Jacobian Lens validity;
- transfer from Qwen3.5 to Agents-A1;
- completed-error prediction or semantic-workspace monitoring;
- causal expert localization;
- safe truncation or early exit;
- routing intervention, correction policy, activation steering, privacy, or
  production utility.

Treat the repository as publicly visible. Never commit raw prompts, fixture text,
token IDs or text, outputs, hidden states, activations, expert identities, routes,
router logits, telemetry arrays, Jacobians, JVPs, VJPs, lens matrices, per-example
scores, process evidence, weights, caches, local paths, environment values,
credentials, or secret-linked provenance.
