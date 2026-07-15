# Q35Q — Quantized Qwen3.5 MoE Jacobian feasibility and transfer protocol

## Purpose

Q35Q establishes a bounded, architecture-matched engineering path for fitting and
validating Jacobian Lens transport on a quantized Qwen3.5-35B-A3B MoE using the
local dual-RTX-3090 host. It exists because the smallest official Qwen3.5 MoE has
the same 35B-A3B scale as Agents-A1, while an official GPTQ INT4 checkpoint and
runtime NF4 loading may reduce the weight footprint enough for local backward
experiments.

Q35Q is an engineering-feasibility track. It may establish that a particular
quantized checkpoint supports exact autograd input gradients, bounded lens fitting,
and cross-checkpoint transport experiments. It cannot establish a BF16 Jacobian
Lens, Agents-A1 correctness prediction, causal interpretation, safe stopping,
intervention value, or production utility.

All existing privacy, sealed-data, verifier, provenance, resource, claim-boundary,
production, repository-hygiene, and stop rules remain binding. Q35Q may not use
M38E or M39 rows, labels, outcomes, feature discoveries, prompts, or task variants.

## Execution timing and resource isolation

- CPU-side implementation, manifests, synthetic tests, artifact-admission code,
  and download staging may begin while M38E is running.
- No Q35Q GPU process may contend with, interrupt, inspect, signal, reconfigure,
  or alter the active M38E host, process tree, model cache, environment, worktree,
  or private ledger.
- GPU execution is permitted only after M38E releases the dual-3090 window or on
  a separately proven independent host.
- Automatic retry is not authorized. Every failed GPU attempt stops and records
  an aggregate technical block pending operator review.

## Canonical model candidates

### Primary source model

`Qwen/Qwen3.5-35B-A3B-Base`

The exact immutable revision must be pinned before use. The admitted language
model must match the official Qwen3.5 MoE structure, including:

- 35B total / approximately 3B active parameters;
- hidden dimension 2048;
- 40 language-model layers;
- 256 routed experts;
- 8 routed experts plus 1 shared expert per token;
- expert intermediate dimension 512;
- hybrid Gated DeltaNet and Gated Attention layout;
- padded vocabulary/output dimension 248320.

The vision encoder must not be loaded unless the protocol is explicitly amended.
The text-only model class, omitted modules, and resulting parameter manifest must
be recorded and verified.

### Quantization paths

Q35Q evaluates two paths in this order:

1. **Official GPTQ INT4:**
   `Qwen/Qwen3.5-35B-A3B-GPTQ-Int4`, loaded only through a Transformers/eager
   path that exposes a genuine PyTorch autograd graph.
2. **Runtime NF4:** the admitted BF16 base checkpoint loaded with bitsandbytes
   NF4, frozen weights, explicit training-compatible multi-GPU placement, and a
   fully recorded quantization configuration.

The official GPTQ model's vLLM/SGLang `moe_wna16` serving kernels are inference
paths and are not authorized for Jacobian fitting unless an exact backward path
is independently demonstrated. A successful forward or generation is not an
autograd pass.

`device_map="auto"` is not accepted as evidence of a training-compatible shard
plan. Use an explicit, recorded placement or a separately validated distributed
training mechanism. Hidden CPU offload, disk offload, silent module replacement,
or fallback to a different model class blocks the primary fit.

GPTQ, NF4, AWQ, FP8, and BF16 are distinct mathematical models for claim purposes.
Rows, lenses, calibration, and power may not be pooled across quantizations.

## Artifact admission before GPU execution

Commit an aggregate-only admission amendment before any live backward call. It
must bind:

- exact repository and immutable revision;
- license and model lineage;
- complete configuration, tokenizer, processor, chat-template, generation, and
  custom-code identities;
- complete weight-file manifest and cryptographic hashes;
- exact text-only parameter manifest and omitted vision/MTP modules;
- Transformers, Accelerate, bitsandbytes/GPTQ backend, PyTorch, CUDA, driver, and
  kernel identities;
- quantization type, group size, scale/zero-point representation, compute dtype,
  storage dtype, double-quant setting, and skipped modules;
- explicit device placement and cross-device transport mechanism;
- deterministic tokenization and text-only load fixtures;
- source commit and hashes of every Q35Q driver and validation file;
- public-artifact privacy and `check_commit_safe.py` status.

Missing, mutable, contradictory, or unverifiable evidence produces
`q35q_artifact_admission_blocked`.

## Phase 0 — CPU-only implementation and synthetic validation

Before model loading, implement and test:

- exact revision and file-manifest verification;
- explicit model/config architecture checks;
- explicit device-map validation;
- quantization-configuration serialization and equality;
- detection of CPU/disk offload and unapproved module substitution;
- detection of inference-only or missing autograd kernels;
- exact source/target layer validation;
- finite-gradient, nonzero-gradient, parity, and resource artifact schemas;
- aggregate-only privacy scanning;
- atomic, resumable private checkpoints for later fitting.

No model-generated scientific row is produced in Phase 0.

## Phase 1 — one-sequence exact VJP feasibility gate

Run one deterministic text-only sequence with:

- sequence length 32;
- batch size 1;
- `use_cache=False`;
- MTP/speculative decoding disabled;
- all model parameters frozen and weight gradients absent;
- one fixed source layer, initially layer 20;
- final language-model residual target, initially layer 39;
- one scalar target and `dim_batch=1`;
- deterministic eager execution where supported.

A path passes only if all gates pass:

1. the source residual is connected to the target through genuine autograd;
2. `torch.autograd.grad` returns a non-`None`, nonzero, finite VJP;
3. no straight-through estimator, detached dequantize/requantize approximation,
   fake gradient, or finite-difference substitute is represented as exact VJP;
4. every frozen parameter has no retained gradient;
5. repeated VJPs are stable within a preregistered numerical tolerance;
6. observation hooks preserve generated token IDs exactly and preserve final
   logits within the frozen one-compute-quantum tolerance;
7. peak reserved memory is at most 23.0 GiB on each RTX 3090 and at most 46.0 GiB
   in aggregate;
8. no CPU or disk offload occurs in the passing primary path;
9. the exact model, quantization, source, target, package, kernel, and placement
   identities match the admission amendment;
10. cleanup releases hooks, graphs, tensors, and GPU allocations and leaves the
    normal runtime verifiably restorable.

If GPTQ fails because its exact kernels lack backward support, record
`q35q_gptq_autograd_unsupported` and proceed to the already-admitted NF4 path.
Do not patch in approximate gradients and call the path exact.

If NF4 also fails, Q35Q stops as `q35q_local_exact_vjp_blocked`. This does not
reject BF16 Jacobian fitting on rented high-memory hardware.

## Phase 2 — bounded micro-fit

Only a Phase-1-passing path may run a micro-fit. Freeze before outcomes:

- 8 deterministic neutral-corpus sequences, length 32;
- 6 fit and 2 validation sequences;
- exact corpus revision, seed, ordered sequence hashes, tokenizer, and positions;
- source layer 20 to target layer 39;
- `dim_batch=1`;
- checkpoint after every fit sequence;
- same memory, parity, finiteness, cleanup, and provenance gates as Phase 1.

Validation must report, aggregate-only:

- finite Jacobian and transport statistics;
- bitwise or tolerance-bounded repeat application;
- exact token-output invariance with observation enabled;
- application latency and peak memory;
- next-token ranking/coherence against identity transport and standard logit lens;
- lens and corpus cryptographic hashes.

A micro-fit pass establishes only that the quantized source model supports the
complete local lens pipeline.

## Phase 3 — selected-layer quantized base-model lens

Only after a passing micro-fit, commit a separate fit manifest before capture.
The default bounded design is:

- 120 deterministic neutral-corpus sequences of length 128;
- 100 fit / 20 validation;
- source layers `[4, 12, 20, 28, 36]` mapped independently to target layer 39;
- `dim_batch=1` unless a pre-outcome memory smoke proves a larger value within the
  unchanged per-GPU gate;
- atomic checkpointing at least every five sequences;
- hard 24-hour wall-clock ceiling for the bounded fit attempt;
- exact standard-logit-lens and identity-transport comparators;
- no M38E/M39 data, labels, outcomes, or task-derived corpus selection.

Do not silently reduce the corpus, skip difficult dimensions, change layers,
increase memory ceilings, or change quantization after viewing results. A bounded
resource failure is reported as blocked, not tuned away.

Lens matrices, Jacobian samples, hidden states, and raw validation sequences remain
private and uncommitted. Public artifacts contain aggregate metrics and hashes
only.

## Phase 4 — architecture-matched transfer tests

After a native quantized base-model lens passes validation, a fresh transfer
manifest may compare it unchanged on:

1. the official post-trained `Qwen/Qwen3.5-35B-A3B` checkpoint;
2. another admitted Qwen3.5-35B-A3B derivative;
3. the pinned Agents-A1 35B checkpoint.

Transfer requires exact field-by-field compatibility for layer count, hidden
width, layer ordering, normalization, vocabulary/tokenizer, routed/shared expert
layout, attention/DeltaNet layout, residual conventions, and target readout.
Incompatibility blocks direct transfer rather than triggering an adapter chosen
after outcomes.

For every target checkpoint:

- use the target model's own final normalization and unembedding/output head;
- never reuse the source model's vocabulary head;
- compare transferred transport against target-native identity transport and
  standard logit lens at identical tokens and layers;
- record source and target quantization separately;
- keep target prompts and all per-example readouts private;
- make no correctness, stopping, repair, or production claim.

A positive result establishes quantized cross-checkpoint transport portability
only. It is not an Agents-A1-native Jacobian Lens.

## Phase 5 — native quantized Agents-A1 lens

After the Qwen3.5 base path passes and the exact Agents-A1 artifact and chosen
quantization path are admitted, a native quantized Agents-A1 Phase-1 and Phase-2
sequence may run under the same gates. A Phase-3-scale Agents-A1 fit requires a
separate pre-outcome manifest.

This path may establish a Jacobian Lens for the exact quantized Agents-A1
checkpoint. It cannot establish the BF16 model's Jacobian. Quantization portability
must be measured later against a native BF16 lens or exact BF16 VJPs on rented
high-memory hardware.

## Relationship to M39 and later BF16 work

Q35Q engineering feasibility may be staged before M39 and may execute after M38E
releases the GPU window because it uses a neutral corpus and no correctness labels.
It does not replace M39.

- M39 remains the confirmatory forward-only test of whether internal telemetry
  predicts completed errors beyond nuisance and router baselines.
- Q35Q correctness-prediction or stopping evaluation is prohibited until M39's
  independent-population launch and claim gates permit it.
- A successful Q35Q path may replace an unrelated MoE as the primary
  architecture-matched instrumentation surrogate.
- An unrelated open MoE remains useful only where Qwen3.5 quantized kernels make a
  specific expert/dispatch intervention technically impossible.
- Native BF16 Agents-A1 fitting remains the reference target and still requires a
  separately frozen high-memory smoke and fit protocol.

## Required aggregate outcomes

Use one of the following exact scoped outcomes:

- `q35q_gptq_exact_vjp_passed`
- `q35q_gptq_autograd_unsupported`
- `q35q_nf4_exact_vjp_passed`
- `q35q_local_exact_vjp_blocked`
- `q35q_microfit_passed`
- `q35q_microfit_blocked`
- `q35q_quantized_base_lens_validated`
- `q35q_transfer_feasible`
- `q35q_transfer_not_established`
- `q35q_native_quantized_agents_lens_validated`
- `q35q_artifact_admission_blocked`
- `q35q_provenance_blocked`

None of these outcomes authorizes production use.

## Stop and privacy boundaries

Stop on model/revision mismatch, dirty or changed source provenance, unsupported
autograd, detached/zero/nonfinite gradients, fake or approximate gradients
presented as exact, output-parity failure, unapproved offload, hidden model
substitution, quantization mismatch, device-map mismatch, kernel mismatch, OOM,
resource-ceiling breach, repeated instability, checkpoint corruption, cleanup
failure, privacy failure, or commit-safety failure.

Never commit raw prompts, corpus text, outputs, token IDs/text, hidden states,
activations, expert outputs, routes, Jacobians, VJPs, lens matrices, per-example
scores, model weights, caches, local paths, environment values, process evidence,
or secret-linked provenance. Treat the repository as publicly visible.