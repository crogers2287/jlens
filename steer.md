# steer.md — repair Q35Q artifact admission before weights or GPU execution

`CODEX_AUTOSTEER.md` remains the operating contract. This file is the current
source of truth for milestone selection. It incorporates the complete prior
`steer.md` blob `52227ac18f3f1712b0909e2b8c282d12cf7dfc91` and every protocol or
steer addendum incorporated by that blob, including:

- `docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md`;
- `docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md`;
- `docs/STEER_ADDENDUM_2026-07-16_Q35Q_PHASE0_STAGING_AND_EXACT_JVP_CROSSCHECK.md`;
- `docs/STEER_ADDENDUM_2026-07-16_Q35Q_PHASE0_ADMISSION_CORRECTION_AND_TP_RUNTIME.md`.

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

### Q35Q Phase-0 staging

Commit `1123561ed4f360c14cf424bc0156842d2947b353` produced useful partial
CPU/storage/network-only staging for
`Qwen/Qwen3.5-35B-A3B-GPTQ-Int4` at immutable revision
`3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b`.

Established from that commit only:

- the pinned GPTQ tokenizer genuinely loaded with `trust_remote_code=False`;
- deterministic token IDs were observed for one neutral private fixture;
- small public admission files were staged;
- no weights were loaded;
- no model was instantiated;
- no GPU, generation, hidden-state, router, JVP, VJP, backward, fitting, transfer,
  or scientific outcome capture occurred.

Commit `8fecb7a9463508af6beb7da14e94dd7949a25abf` correctly supersedes the
stronger admission labels from that staging run. The prior architecture boolean
was incomplete, the tokenizer test was too weak, the manifest boundary was not
proven deterministic, and the base repository plus storage/checksum requirements
were absent.

Therefore:

- classify `1123561…` only as `q35q_admission_staging_partial`;
- do not treat its architecture or tokenizer labels as a binding Phase-0 pass;
- keep `q35q_artifact_admission_blocked` active;
- do not stage weights until the corrected prerequisite record below passes.

### Resource boundary

The dual RTX 3090s remain assigned to an unrelated llama.cpp/llama-swap and MCP
workload. The Q35Q GPU window is not released. Do not signal, inspect,
reconfigure, pause, or displace that workload. No Agents-A1 serving restoration
or Q35Q GPU availability may be inferred from M38E closure.

## Active milestone — corrected Q35Q Phase-0 admission

The next host-capable cycle must repair the Phase-0 implementation and synthetic
tests, then produce one honest aggregate rerun. No additional operator ruling is
required for the CPU-, storage-, network-, and repository-side work below.

### 1. Immutable repository identity

Pin immutable revisions for both:

- `Qwen/Qwen3.5-35B-A3B-Base`;
- `Qwen/Qwen3.5-35B-A3B-GPTQ-Int4`.

Reject mutable refs, unresolved identities, repository mismatch, tokenizer/model
mismatch, or unreviewed remote code.

### 2. Deterministic public-file manifests

Enumerate admitted files from the pinned public repository manifests. Hash only
explicitly admitted public files. Exclude caches, lock files, downloader
metadata, timestamps, temporary or partial files, host-specific paths, and
symlinks or path escapes outside the staging root.

Synthetic tests must prove fail-closed behavior for:

- cache or downloader metadata contamination;
- extra unapproved files;
- missing files;
- mutable revisions;
- path escapes;
- hash mismatch;
- interrupted or partial downloads.

Commit only public repository identities, aggregate counts, public relative-path
manifest digests, total public byte counts, and pass/fail.

### 3. Exact text-only architecture admission

The overall architecture conjunction must fail unless every required field in
`Q35Q_PHASE0_ADMISSION_CORRECTION_AND_TP_RUNTIME.md` passes independently,
including:

- exact Qwen3.5 MoE text model classes and model types;
- hidden size 2048 and 40 text layers;
- padded language-model output width 248320;
- 256 routed experts, top-8 routing, and MoE intermediate size 512;
- the shared-expert path and its width verified from pinned implementation
  source, not inferred from a missing configuration field;
- the exact 40-layer hybrid linear-attention/full-attention schedule and Gated
  DeltaNet projection identities;
- final RMS normalization and untied output head;
- vision modules present in the repository but omitted from the admitted
  text-only path;
- MTP metadata present but MTP modules excluded from the admitted execution path;
- exact GPTQ identity, bit width, group size, and skipped/dynamic module rules.

Do not collapse this into a small subset boolean. Missing, contradictory,
inferred, or source-unverified fields record `q35q_artifact_admission_blocked`.

### 4. Binding tokenizer admission

Using the immutable tokenizer files and neutral private fixture, bind:

- repository revision and tokenizer-file manifest digest;
- tokenizer class and `trust_remote_code` setting;
- normalization and cleanup settings;
- explicit no-special-token encoding plus separately tested admitted special-token
  behavior;
- BOS, EOS, PAD, and chat-template identities;
- deterministic encoded length and private token-ID-sequence digest;
- exact deterministic decode/re-encode behavior under the preregistered
  normalization rule;
- deterministic chat-template rendering digest.

Substring reconstruction is not a roundtrip pass. Synthetic tests must reject
changed normalization, special-token behavior, chat templates, repository
identity, model/tokenizer pairing, or nondeterministic IDs.

Raw fixture text, rendered chat text, and token IDs remain private and
uncommitted.

### 5. Storage, checksum, and resumability gate

Before weight staging, produce honest aggregate projections for:

- expected public weight bytes for both repositories;
- required free space and temporary download overhead;
- checksum procedures and immutable manifest reconciliation;
- interrupted-download cleanup and deterministic resume behavior;
- isolated cache placement that cannot modify or depend on the unrelated GPU
  tenant's runtime state.

Do not stage weight files until corrected Phase-0 steps 1 through 5 pass.

### 6. Tests and required operational outcome

Run fresh repository tests, privacy scans, artifact no-text checks, provenance
checks, and commit-safety checks.

The next Q35Q operational commit must record exactly one of:

1. `q35q_phase0_admission_corrected_passed` with every required field and
   prerequisite passing, after which storage-only weight staging may begin;
2. `q35q_artifact_admission_blocked` with one narrow evidence-backed blocker
   class;
3. `q35q_provenance_blocked` when immutable source or artifact identity cannot be
   established;
4. `host_execution_authority_unavailable` once if the executing agent genuinely
   lacks the already-authorized CPU/storage/network access.

Do not repeat the superseded architecture or tokenizer admission pass. Do not
publish unchanged status-only heartbeats in place of executing this milestone.

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

The eventual runtime must also pin exact Transformers, PyTorch, CUDA, package,
model-source, quantization, kernel, and generated-configuration identities. The
explicit dual-3090 plan must account for the required full-channel all-gather
before depthwise convolution and remain within 23.0 GiB per GPU and 46.0 GiB
total.

A missing TP entry, source mismatch, hidden offload, model or kernel
substitution, OOM, placement mismatch, or resource breach is a hard stop. Do not
use `device_map="auto"`, approximation, or a weaker memory gate as proof.

## Program order after corrected Phase 0

1. Correct and pass Phase-0 admission.
2. Stage and verify weight artifacts using CPU, storage, and network only.
3. Wait until the dual-3090 window is legitimately available and the resource
   transition is verified without displacing an unrelated workload.
4. Run only the frozen one-sequence exact residual-input VJP gate on the admitted
   GPTQ path.
5. Record `q35q_gptq_autograd_unsupported` honestly before attempting the admitted
   NF4 fallback.
6. Require genuine autograd, non-`None`, nonzero, finite, repeatable VJPs, frozen
   weights, no hidden offload, output/hook parity, admitted routing regime,
   admitted runtime, and the existing memory ceilings.
7. After a reverse-mode VJP passes, the separately preregistered exact JVP/VJP
   adjoint cross-check may run. Finite differences and approximate fallbacks are
   prohibited.
8. Produce aggregate route-regime, backward-cost, wall-time, storage, cleanup,
   provenance, privacy, and commit-safety evidence before the frozen
   eight-sequence micro-fit.
9. Preregister any larger selected-layer quantized Qwen3.5 base-model fit before
   capture and use only deterministic horizontal prompt sharding with fp32
   weighted merging and cross-worker agreement smokes.
10. Test transfer separately against identity transport and standard logit-lens
    comparators, including route overlap, route changes, and margin distributions.
11. Admit and fit a native quantized Agents-A1 lens only under a separate frozen
    target-artifact and quantization protocol.
12. Retain native BF16 Agents-A1 exact VJPs and fitting on admitted high-memory
    hardware as the final reference comparison.

Every quantized checkpoint is its own mathematical model. A quantized Qwen3.5
lens is not a BF16 lens and a transferred Qwen3.5 lens is not Agents-A1-native.

## M39 and control boundary

M39 remains independent and may not borrow M38E or Q35Q rows, outcomes,
difficulty observations, selected examples, features, layers, or thresholds.
M39 scientific capture requires its complete committed launch amendment, fresh
population, admitted serving path, and every power, nuisance, multiplicity,
parity, provenance, privacy, resource, verifier, and leakage gate.

M39 remains observation-only. Executed-route margins, loads, transitions,
entropy, confidence, hidden-state dynamics, behavioral self-assessment, and
possible hardware routing footprints remain candidate comparators. No
counterfactual routing, router update, retry policy, tool invocation, truncation,
early exit, intervention, activation steering, or production control is
permitted.

## Privacy, claims, and completion boundary

Treat the repository as publicly visible. Never commit raw tasks, corpus or
fixture text, prompts, answers, outputs, retrieved context, token IDs or text,
hidden states, activations, expert identities or outputs, routes, router logits,
telemetry arrays, Jacobians, JVPs, VJPs, lens matrices, per-example scores or
predictions, process evidence, model weights or artifacts, caches, local paths,
environment values, credentials, or secret-linked provenance.

Stop on identity mismatch, dirty source provenance, exact-set failure,
unsupported backward, detached/zero/nonfinite gradients, approximate gradients
represented as exact, parity failure, hidden offload, model or quantization
substitution, device-placement mismatch, kernel mismatch, OOM, resource breach,
instability, artifact corruption, cleanup failure, privacy failure, or
commit-safety failure.

Established now: M38E is closed, one genuine GPTQ tokenizer load occurred, and
partial public metadata staging exists.

Not established: corrected Q35Q artifact admission, weight admission, an
admissible GPU runtime, any exact GPTQ or NF4 JVP/VJP, any fitted Qwen3.5 or
Agents-A1 Jacobian Lens, transfer, completed-error prediction, semantic-workspace
monitoring, safe truncation, early exit, routing intervention, privacy, or
production utility.

The research program is not complete.