# STEER ADDENDUM — External hybrid-MoE Jacobian-lens artifact admission and Agents-A1 bridge gates

Date: 2026-07-29
Parent remote head: `3af1d447e23edf132416a41c07d4513e22936f09`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, Q35Q,
M37J, M39, and every later cumulative correction. It preserves every privacy,
sealed-data, verifier, provenance, exact-set, derivative, resource, retry,
intervention, repository-hygiene, and production-gating rule.

It does not admit Q35Q, authorize model-weight staging, authorize GPU use, reopen
M38E, permit private-row export, establish a Jacobian Lens for Agents-A1, or
permit early exit, retry, repair, route editing, activation steering, or
production control.

## Triggering public evidence

A public fitted Jacobian-lens artifact now exists for the hybrid-attention MoE
checkpoint `Qwen/Qwen3.6-35B-A3B`:

- artifact repository: `stanleytheli/qwen3.6-35B-A3B-jlens`;
- repository head observed during this review:
  `7a5dc7a6c770c272226a321409b30d7e6d773bba`;
- `lens.pt` upload commit:
  `fbcf80eb153a6ca50e473dea2e4ccd93c01402c2`;
- model-card commit:
  `eb8610ef00ced1c71b6de39edac97c3422edd35b`;
- stated reference implementation:
  `anthropics/jacobian-lens@581d398613e5602a5af361e1c34d3a92ea82ba8e`.

The public model card states that the main lens:

- was fitted on 1,000 WikiText-103 prompts of length 128;
- excludes source positions below 16;
- covers source layers 0 through 38 and target layer 39;
- has model width 2,048 and is stored in fp16;
- was fitted with `dim_batch=16` on eight H200 GPUs;
- used approximately 101 GiB peak memory per GPU and approximately 55 to 80
  seconds per prompt;
- merged shards by prompt-count-weighted mean; and
- differentiated through the sparse 256-expert MoE dispatch and hybrid gated
  linear-attention blocks using a pure-PyTorch Transformers execution path.

The repository also publishes a 100-prompt lens and states that it matches the
1,000-prompt lens within noise. The public evaluation reports ranks of the
model's own final output token under the J-lens and logit lens, plus qualitative
middle-hop token ranks on two-hop prompts.

The two published tensor files are approximately 327 MB each and are identified
by the hosting service as PyTorch pickle artifacts. They are not safe merely
because the host reports a small set of detected pickle imports.

This is author-supplied public evidence. It has not been independently
reproduced inside jLens. The exact base-model revision, complete fitting-corpus
manifest, ordered prompt hashes, runtime tuple, route traces, forward parity,
derivative parity, tensor-file cryptographic digests, and independent objective
labels were not established by the public model card.

## Binding interpretation

The public artifact materially strengthens one engineering conclusion:

> A full-width average-Jacobian transport artifact has reportedly been fitted
> through a 40-layer, 2,048-wide, 256-expert hybrid-attention MoE using an
> autograd-compatible eager PyTorch path at large-GPU scale.

It does not establish:

- correctness of the published tensor contents;
- safe deserialization;
- exact reproduction of the claimed fit;
- route- or recurrent-state derivative correctness;
- corpus robustness;
- objective correctness prediction;
- a semantic or global workspace;
- transfer to Qwen3.5, Qwen3.6 derivatives, quantized checkpoints, or Agents-A1;
- local dual-3090 feasibility; or
- safe intervention or production use.

The artifact is therefore an architecture-matched engineering reference and a
candidate reproduction target, not an admitted scientific result or a lens that
may be imported into Agents-A1.

## External lens artifact identity gate

Every externally supplied fitted lens must be treated as a separate executable
artifact and must bind at least:

- hosting repository and immutable revision;
- exact file path, byte length, cryptographic digest, and storage backend
  identity;
- upload commit and complete parent history relevant to the file;
- declared license and provenance;
- serialization format and deserialization code path;
- complete tensor-key schema, ordering, shapes, strides, dtypes, and devices;
- source-layer and target-layer identities;
- matrix orientation and application convention;
- normalization, centering, scaling, and accumulation conventions;
- base-model repository and immutable checkpoint revision;
- tokenizer, processor, vocabulary, final normalization, and unembedding
  identities;
- fitting-corpus manifest, prompt count, sequence lengths, token-position rule,
  masking, truncation, packing, seed, sharding, and merge rule;
- estimator source revision and exact formula;
- runtime, framework, kernel, precision, topology, batching, and cache identities;
- validation populations, metrics, uncertainty, and comparison rules; and
- all known deviations from the stated reference implementation.

A repository name, model card, filename, or compatible shape is insufficient.
Missing, mutable, contradictory, or unverifiable evidence produces
`external_lens_artifact_admission_blocked`.

## Untrusted serialization gate

No externally supplied `.pt`, `.pth`, pickle, joblib, or equivalent
code-capable serialization may be loaded directly in a privileged development,
production, connected-account, or private-data environment.

Before use, an external lens tensor file must pass a fail-closed quarantine
procedure:

1. Fetch only by immutable revision.
2. Verify independently obtained byte length and cryptographic digest.
3. Place the file in a disposable, unprivileged, no-network environment with no
   credentials, mounted secrets, repository write token, private datasets, or
   shared model cache.
4. Attempt restricted tensor-only loading, including `weights_only=True` where
   supported by the frozen PyTorch runtime.
5. Reject any required custom global, reducer, class import, executable hook, or
   unsupported object graph.
6. Validate exact keys, tensor count, shapes, dtypes, finite values, allowed
   metadata, and aggregate size before any conversion.
7. Convert only admitted tensors into a non-executable format such as
   safetensors plus a canonical JSON manifest.
8. Hash the converted artifact and commit only aggregate identities and schema,
   never raw lens tensors.
9. Reopen the converted artifact in a second clean process and prove exact
   tensor equality to the restricted-load result.
10. Destroy the disposable environment after conversion.

A hosting-service pickle scan is a hint, not a security admission. Failure of
restricted loading blocks the artifact; it does not authorize ordinary
`torch.load` as a workaround.

## Base-model and runtime closure gate

Application of an external lens requires exact closure over the base model and
execution path. Freeze and verify:

- base checkpoint revision and complete weight manifest;
- model class and text-decoder path;
- text-only versus multimodal wrapper identity;
- number and ordering of layers;
- hidden width and residual convention;
- routed and shared expert topology;
- router score, dispatch, mixture-weight, and expert-combine implementations;
- hybrid linear-attention and full-attention layout;
- recurrent state, convolution state, KV cache, positional state, and
  `use_cache` condition;
- tokenizer, BOS behavior, chat template, processor, and sequence construction;
- final normalization, output head, vocabulary ordering, and logit soft-cap;
- Transformers, PyTorch, CUDA, driver, kernel, topology, dtype, and sharding;
- hook locations and proof that observation preserves tokens and logits; and
- complete live-object source closure for every differentiated operation.

The reference adapter's ability to locate a residual stack by attribute path is
not evidence that the resulting execution matches the artifact's fit runtime.
The adapter mutates parameter `requires_grad`, may alter BOS behavior, and can
compile blocks; those settings are separate executable conditions.

Pure-PyTorch eager execution, vLLM, SGLang, llama.cpp, MLX, GPTQModel,
bitsandbytes, compiled PyTorch, and vendor fused kernels are distinct runtimes.
A lens fitted under one runtime may not be represented as runtime-invariant
without exact application and derivative evidence.

## Lens schema and orientation gate

Before any semantic inspection, prove the artifact's mathematical identity.
Required checks include:

- exact mapping from stored key to source layer;
- absence of missing, duplicate, reordered, or extra layers;
- source and target residual boundaries;
- matrix shape and whether rows or columns encode cotangent batches;
- whether application is `J @ h`, `h @ J.T`, or another convention;
- pre- or post-normalization residual identity;
- accumulation precision and final storage cast;
- merge weighting and denominator;
- final normalization and unembedding applied exactly once;
- tokenizer/vocabulary index equality; and
- finite, deterministic application under the admitted runtime.

An artifact that produces plausible words can still have a transposed,
misindexed, shifted-layer, wrong-normalization, or wrong-vocabulary defect.
Qualitative readability is not schema validation.

## Four-level reproduction ladder

External-artifact evidence must be labeled by the highest completed level:

### Level 0 — metadata only

The repository, model card, revisions, and file identities are recorded. No
file is loaded and no result is reproduced.

### Level 1 — application reproduction

A safely converted artifact is applied to the exact admitted base model. The
study proves deterministic lens logits, unchanged model tokens and final logits,
and the stated layer coverage. This establishes only that the artifact can be
applied.

### Level 2 — derivative spot reproduction

For prospectively selected prompts, layers, positions, and cotangents, compare
stored transport against fresh exact VJPs or JVP-equivalent contractions and
finite differences under the admitted fit runtime. Report route-unchanged and
route-changed strata separately. This establishes bounded consistency, not the
full fit.

### Level 3 — independent micro-refit

Fit a fresh, small, prospectively frozen lens under the same estimator and an
independently sampled same-corpus population. Compare matrix geometry,
conditioning, token ranks, and objective readout metrics against a seed null.
This establishes limited reproducibility.

### Level 4 — independent full refit

Reproduce the complete fit with independently frozen data, runtime, sharding,
merge, and validation. Compare the full map, not only selected token ranks or
one scalar summary.

No lower level may be described as a full reproduction.

## Route and hybrid-state derivative gate

A derivative through a sparse hybrid MoE must distinguish:

- fixed-route local derivatives;
- derivatives near top-k route boundaries;
- realized changes in selected experts and mixture weights under finite
  perturbations;
- routed-expert versus shared-expert contributions;
- linear-attention recurrent state and convolution state;
- full-attention KV-cache state;
- fresh prefill versus resumed or reused state;
- source position and target-position aggregation; and
- topology- and kernel-dependent dispatch behavior.

Autograd returning a nonzero tensor is insufficient. Required evidence includes
exact VJP/JVP parity, finite-difference checks, deterministic replay, proof that
all intended operations remain connected, and explicit route-boundary analysis.

The public claim that gradients flowed through sparse dispatch and hybrid blocks
is useful feasibility evidence. It does not prove exact derivatives for every
route regime, recurrent-state construction, quantization, or serving runtime.

## Evaluation-semantics gate

Ranking the model's own final output token measures retrospective agreement with
that model output. It does not establish objective correctness, factuality,
reasoning completeness, safety, or useful early exit.

Future evaluation must keep separate:

- final-output-token rank;
- externally defined answer-token rank;
- independently verified objective correctness;
- intermediate entity or relation labels;
- hidden-state monitor discrimination;
- route telemetry;
- calibration and false-alarm behavior;
- early-warning lead time; and
- intervention utility.

A middle-hop token must be defined independently of the lens output and final
model output. Prompt author expectations, model argmax, and post-hoc selection
are not independent verifiers.

Claims that an answer `crystallizes`, depth is `unused`, or a layer exposes
`early-exit headroom` remain heuristic unless full execution from that boundary
is replaced by a separately trained or admitted continuation mechanism and
objective outcomes are preserved under a prospectively frozen stopping policy.

## Sample-saturation gate

The statement that a 100-prompt lens matches a 1,000-prompt lens within noise
cannot establish general sample saturation without:

- exact prompt identities and independent samples;
- multiple same-corpus seeds;
- a prospectively frozen map-distance metric;
- layerwise and whole-map uncertainty;
- conditioning and singular-spectrum comparisons;
- readout performance with confidence intervals;
- cross-corpus sensitivity;
- task-trajectory and deployment-population checks; and
- a frozen acceptable-equivalence region.

A single 100-versus-1,000 comparison does not justify reducing future Q35Q or
Agents-A1 fit populations after viewing outcomes.

## Resource and scaling gate

The reported H200 fit cost is a runtime-specific observation, not a portable
budget. Future planning must separately account for:

- model and lens storage;
- parameter, activation, graph, cotangent-batch, and optimizer-free memory;
- expert dispatch and all-to-all communication;
- recurrent and attention state;
- source and target position counts;
- `dim_batch`;
- sequence length and packing;
- number of prompts, layers, and shards;
- checkpoint and merge I/O;
- compilation and warm-up;
- topology, interconnect, and utilization; and
- retries, validation, and independent refits.

The public result weakens the claim that hybrid-MoE fitting is inherently
impossible. It does not establish affordability or feasibility on the local
dual-3090 host.

## Agents-A1 bridge decision

The external Qwen3.6 artifact creates a technically credible additional bridge,
not a transfer shortcut.

The revised sequence is:

1. Keep the active Q35Q exact-target-runtime admission blocker unchanged.
2. In parallel, implement CPU-only metadata and quarantine-admission tooling for
   external lens artifacts without downloading model weights or loading pickle
   in the repository environment.
3. Pin and safely convert the Qwen3.6 lens only after immutable file digests are
   independently obtained.
4. Admit the exact Qwen3.6 base checkpoint, text stack, tokenizer, pure-PyTorch
   runtime, hybrid state, router, experts, topology, and hook boundaries.
5. Complete Level-1 application reproduction with model-output invariance.
6. Complete prospectively selected Level-2 derivative spot checks, including
   route-boundary and hybrid-state strata.
7. Complete a bounded Level-3 native Qwen3.6 micro-refit with independent
   same-corpus and shifted-corpus controls.
8. Use the admitted Qwen3.6 implementation only as an architecture-matched
   engineering and cost comparator for Agents-A1.
9. Separately admit `InternScience/Agents-A1` at immutable model revision
   `55100f11160f545dc45545c677699ace74f6bd10` or a later explicitly reviewed
   revision, including its multimodal wrapper and exact text-only omission rule.
10. Prove Agents-A1-native forward, VJP, JVP, finite-difference, route, recurrent-
    state, cache, and hook parity before fitting any native lens.
11. Fit an Agents-A1-native lens on prospectively frozen pretraining-like and
    agent/tool-trajectory populations with same-corpus seed nulls.
12. Establish deterministic, confidence, trajectory, memory, program-state,
    hidden-state, spectral, router, expert-path, and verifier comparators before
    testing incremental Jacobian-Lens value.
13. Keep stopping, retry, repair, truncation, forced routing, state rewriting,
    activation steering, and production enforcement separately gated with full-
    compute fallback.

The Qwen3.6 artifact may justify a separately authorized rented-H200 BF16
reproduction path if the local quantized Q35Q path remains blocked. It does not
authorize bypassing Q35Q's provenance findings or representing a Qwen3.6 lens as
an Agents-A1 lens.

## Current engineering blocker remains unchanged

The active blocker remains exact-target-runtime Q35Q admission:

1. execute the composed Transformers provenance adapter in the exact target
   runtime using aggregate evidence only;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and complete executable source
   closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption;
6. prove exact expert and fusion ordering;
7. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
8. pass the complete Phase-0 conjunction before weight staging or GPU
   authorization.

No public lens artifact resolves these gates.

## Established by this correction

- A public full-width Jacobian-lens artifact is reported for a 40-layer,
  2,048-wide, 256-expert hybrid-attention MoE.
- External fitted lenses are executable artifacts requiring immutable admission,
  not passive metadata files.
- Code-capable tensor serialization requires quarantine and safe conversion.
- Base-model, runtime, route, hybrid-state, lens-schema, and vocabulary identities
  must all match before application evidence is valid.
- Model-output-token rank is not objective correctness.
- Public sample-saturation and cost claims do not transfer without independent
  controls.
- Qwen3.6 can serve as an architecture-matched engineering comparator for
  Agents-A1 only after separate admission and reproduction.
- No privacy, sealed-data, verifier, provenance, derivative, resource,
  intervention, GPU, or production gate is weakened.

## Still unproven

- Cryptographic and schema admission of the public tensor files.
- Safe restricted deserialization and exact non-executable conversion.
- Exact base-model revision and runtime used for the published fit.
- Independent application, derivative, micro-refit, or full-refit reproduction.
- Route-boundary and hybrid-state derivative correctness.
- Corpus robustness or 100-prompt sample saturation.
- Objective correctness, error-awareness, or semantic-workspace prediction.
- Transfer to Qwen3.5, quantized Qwen3.6, or Agents-A1.
- Local dual-3090 feasibility.
- Incremental router or Jacobian-Lens value beyond cheaper comparators.
- Complete Q35Q runtime, loader, tensor-consumption, expert-ordering, forward, or
  derivative admission.
- Safe early exit, retry, repair, truncation, forced routing, state rewriting,
  activation steering, reward shaping, or production deployment.
