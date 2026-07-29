# STEER ADDENDUM — MLA bottleneck, content/position, causal-patch, and compression-rank gates

Date: 2026-07-29
Parent remote head: `610c9181336cbb144d4daa3cb8514ae30c7cdd14`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no weight retrieval, model execution, GPU use, hidden-state or cache
capture, Jacobian fitting, sealed evaluation, training run, policy update,
control action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q loader and
derivative admission. This addendum changes future attention-state,
representation, attribution, and intervention identity requirements; it does
not displace that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control and
public-source engineering material may be committed. Prompts, outputs, token
data, per-example outcomes, hidden states, compressed attention states, query,
key, value, or RoPE tensors, caches, verifier records, model weights,
credentials, host paths, and private environment details remain prohibited.

## Triggering primary evidence

Dhruvil S, Fenil Sojitra, and Ravirajsinh Chauhan, `Through the Bottleneck: How
Multi-head Latent Attention Separates Content from Position in Language
Models`, arXiv `2607.23054v1`, submitted 2026-07-25, studies one 24-layer,
114.1M-parameter Multi-head Latent Attention model under one training seed.
The model uses a 512-dimensional residual stream, a 128-dimensional shared
`c_KV` bottleneck, a separate 16-dimensional RoPE key path, eight attention
heads, and TinyStories-distribution analysis inputs after broader pretraining.

The paper reports:

- linear probe accuracy on `c_KV` of 95.5% for a binary entity label at one
  reported layer, matching the residual-stream probe in that condition;
- near-chance-to-low absolute position-bin accuracy from `c_KV`, while the
  residual-stream position probe is also far from ceiling;
- all five threshold-detected induction heads in the single model appearing at
  one layer;
- mean 99%-energy effective rank of 58.8 for the 128-dimensional `W_DKV`
  compression matrix, with a maximum of 88 at one layer; and
- a disruption-attribution score that multiplies clean/corrupt `c_KV` cosine
  dissimilarity by one trial-level drop in the probability of a selected target
  token.

The paper explicitly states that the disruption-attribution procedure is
correlational, not activation patching: it does not replace the corrupted
`c_KV` before `W_UK` and `W_UV` consume it and then re-propagate the model. It
also states that the work has no matched MHA baseline, no multi-seed
replication, one small model, a narrow analysis distribution, and linear probes
only.

The attributable implementation is pinned for this correction at:

`Dhruvil-sr24/Small-Language-Model-From-Scratch@83af99c0b1d9a914b17825453a41eb8a99ac0eff`

The implementation exposes a material evidence/label mismatch:

- `interp/activation_patching.py` describes the experiment as causal activation
  patching and states that it proves `c_KV` causally determines output;
- `PatchableModel.patched_run` reaches a `pass` after recognizing that the
  replacement must occur before the layer consumes `c_KV`;
- `InterventionModel.run_with_intervention` constructs `mixed_ckv`, `k_diff`,
  and `v_diff` but does not apply those tensors to the attention computation or
  residual stream; and
- `causal_trace` performs no inline patch. It records representation drift and
  scales it by a run-level probability drop. Its batch runner chooses the clean
  model's own argmax token as the `correct_token`, not an independent task
  verifier label.

A function name, docstring, plot label, or paper-adjacent repository does not
establish that a causal intervention was executed. Reachable dataflow and
verified output effects control the scientific classification.

## Bounded interpretation

The triggering evidence supports only this narrow correction:

> Compressed attention state, separate positional state, linear decodability,
> weight-matrix spectrum, representation disruption, restored computation, and
> independently verified objective outcome are separate scientific objects.

In the reported single model and analysis distribution, selected content labels
are linearly decodable from `c_KV`, while coarse absolute position labels are
weakly linearly decodable. This does not establish that `c_KV` is semantically
pure, that it contains no nonlinear or relative-position information, that the
model does not reconstruct position from context, or that the result transfers
across seeds, scales, corpora, architectures, checkpoints, or runtimes.

A high singular-value effective rank is not a semantic-hub label. A low
weight-matrix effective rank is not proof that cache dimensions can be removed
without retraining or objective loss. Corruption sensitivity is not causal
necessity. Linear probe success is not evidence that the native downstream
model uses the decoded feature. Probe failure is not evidence that the
information is absent.

## Binding MLA and compressed-attention identity gate

Every compatible study must freeze and report separately, where the
architecture contains them:

1. residual-stream input to the attention block;
2. pre-normalization input to the KV down-projection;
3. exact KV down-projection matrix and bias semantics;
4. pre- and post-normalization compressed KV state;
5. cached compressed-state boundary;
6. non-positional key up-projection;
7. value up-projection;
8. separate positional-key projection;
9. RoPE or other positional transformation and its coordinates;
10. query down-projection and normalization, if present;
11. per-head query and key composition;
12. attention logits, masks, scaling, and numerical precision;
13. per-head value aggregation;
14. attention output projection and gate;
15. residual-combine boundary;
16. prefill, decode, prefix-reuse, paging, compression, quantization, and
    eviction condition; and
17. independently verified objective outcome.

A tensor called `c_KV`, `latent_kv`, `compressed_cache`, or `attention_state`
does not satisfy this identity gate without proving its exact position in the
executed dataflow. Pre-normalization and post-normalization states are distinct.
A stored cache representation and a recomputed training-time representation
are distinct until numerical parity is proved.

For architectures that do not implement MLA, MLA names may not be imposed on
native recurrent, linear-attention, GQA, MQA, or ordinary KV-cache states.
Scientific comparison must occur at matched functional boundaries rather than
by renaming different mechanisms.

## Content-versus-position claim gate

A claim that one branch contains content and another contains position requires
prospectively frozen tests that separate at least:

- absolute position;
- relative position and distance;
- order and direction;
- local and long-range displacement;
- token identity and lexical frequency;
- entity identity and entity role;
- syntax and part of speech;
- semantic class and topic;
- repeated-token, shuffled-content, and content-free sequences;
- RoPE phase, scale, and extrapolation regime;
- context length and position distribution;
- prefill versus decode state; and
- fresh-prefill versus reused-cache execution.

Required controls include label permutation, token-frequency matching,
context-position matching, class-balanced metrics, multiple position
resolutions, matched random projections, untrained-model controls, residual
stream controls, branch-swapped controls where technically admissible, and
nonlinear probes with capacity and regularization matched across compared
representations.

Failure of a linear absolute-position probe does not prove absence of position.
High entity-probe accuracy does not prove a pure content representation. The
term `content-only` is prohibited unless a prospectively defined and
sufficiently broad exclusion suite fails to decode or causally use every frozen
position family while preserving admitted content outcomes.

## Probe and retention gate

Every probe result must freeze:

- representation boundary;
- layer and token population;
- tokenizer and context construction;
- train, calibration, validation, and sealed-test partitioning;
- class distribution and chance baseline;
- probe family, width, regularization, optimizer, seed, and budget;
- hyperparameter-selection population;
- metric and confidence interval;
- multiple-comparison correction across layers, labels, and probes;
- capacity-matched random-feature and random-label controls; and
- whether downstream native computation is tested separately.

A ratio such as `probe_accuracy(compressed) / probe_accuracy(residual)` may not
be called information retention without absolute accuracy, chance level,
ceiling or strong reference performance, uncertainty, and task difficulty.
Ratios can look large when both probes are weak. Ratios above 100% do not imply
that the compressed branch created information.

Probe decodability remains an observation-only result. It does not authorize
feature deletion, cache compression, activation editing, early exit, or
production monitoring.

## Compression-rank and capacity gate

Weight-matrix spectrum, activation covariance, cache-state intrinsic dimension,
probe dimension, downstream sensitivity, and safe deployable compression are
separate quantities.

Every effective-rank result must freeze:

- matrix or activation population being decomposed;
- centering and normalization;
- singular-value or eigenvalue convention;
- energy definition;
- threshold, including 90%, 95%, or 99%;
- numerical precision and decomposition method;
- layer-selection and reporting rule;
- uncertainty across seeds or bootstrap populations; and
- comparison to matched random, untrained, dense-attention, and architecture
  controls.

A low effective rank of `W_DKV` does not prove low effective rank of produced
`c_KV` activations. A low activation rank does not prove the discarded
subspace is unimportant under distribution shift. A rank spike does not prove a
semantic hub. Correlation between rank and disruption score does not establish
causal mediation.

Any proposed heterogeneous bottleneck or cache-rank reduction is a new model or
runtime condition. It requires matched training or adaptation identity,
objective and regression evaluation, long-context and cache-reuse testing,
latency, throughput, memory, and numerical accounting, plus independent
verification of every claimed retained capability. Post-hoc dimension removal
without those gates is prohibited.

## Disruption-attribution classification gate

The following objects must remain separate:

1. corruption applied to source inputs or embeddings;
2. change in a measured internal representation;
3. change in target-token probability or another model score;
4. independently verified task outcome;
5. clean-state restoration at one exact internal boundary;
6. recovered downstream computation after restoration; and
7. policy or production action.

A statistic formed by multiplying internal-state drift by a trial-level output
change is a disruption/outcome association. It is not localized causal
attribution because the outcome scalar is shared across all measured layers
and positions and because no internal state is restored.

The terms `causal trace`, `activation patch`, `causal importance`, `recovery`,
or `mediation` require an executed clean/corrupt/patched triplet in which:

- the clean state is inserted inline before the exact downstream consumers;
- downstream computation is re-executed from the intervention boundary;
- the patched tensor is proven to enter the executed key/value or native state
  path;
- identical corruption noise or a frozen paired corruption seed is used;
- patch and no-patch paths differ only at the admitted intervention;
- output recovery and independently verified objective recovery are measured;
- random-state, mean-state, wrong-example, wrong-layer, wrong-position,
  neighboring-subspace, and norm-matched controls are included;
- regressions and off-target effects are reported; and
- intervention cost and runtime identity are frozen.

If the implementation computes replacement tensors but does not consume them,
the intervention is a no-op and must fail admission. If the patch occurs after
the original state has already been consumed, it does not answer the claimed
within-layer causal question.

## Target and verifier identity gate

A clean model argmax token is not automatically the correct token. Target-token
probability, model self-consistency, reference-answer probability, and
independently verified task correctness are separate endpoints.

Future work must freeze whether the target is:

- the observed corpus token;
- a deterministic verifier-approved answer token;
- the clean model argmax;
- the final generated answer;
- a task-level outcome; or
- another prospectively specified endpoint.

Self-selected targets may measure preservation of the model's existing
behavior, including existing errors. They cannot establish correctness,
safety, or repair without an independent verifier.

## Implementation-reachability gate

Repository admission requires more than public availability or paper linkage.
For every claimed observation or intervention, the frozen revision must prove:

- the invoked CLI or entry point reaches the claimed function;
- the claimed branch is not dead, bypassed, shadowed, or guarded off;
- replacement tensors are consumed by the executed downstream operations;
- hooks observe the named boundary without silently observing a stale field;
- clean and corrupt caches are not overwritten before comparison;
- generated plots and tables derive from the admitted path;
- deterministic synthetic tests detect a deliberately broken patch;
- a no-op patch fails the test suite;
- the exact model checkpoint and analysis artifact are bound; and
- public claims are limited to the behavior of that immutable revision.

Comments, docstrings, filenames, variable names, and plot titles are not
execution evidence. When paper text and repository labels differ, the executed
code and explicitly bounded paper method control classification.

## Semantic-hub and circuit-topology gate

No layer may be called a `semantic hub`, `workspace`, `integration center`, or
`causal bottleneck` from a rank peak, probe peak, attention taxonomy, or
corruption association alone.

Such a claim requires, at minimum:

- multi-seed replication;
- matched architecture controls trained on the same data and budget;
- cross-domain and cross-context replication;
- prospectively frozen layer-selection rules;
- true inline restoration and targeted ablation;
- feature-specific and task-specific controls;
- necessity and sufficiency tests where technically feasible;
- comparison against residual, attention-output, MLP, recurrent-state, and
  cache baselines; and
- independently verified objective effects.

Co-location of threshold-detected head types in one model does not prove the
architecture forced that topology. Head-taxonomy thresholds, prompt
population, sequence length, and comparison model must be frozen before the
claim is evaluated.

## Jacobian consequence

A Jacobian taken at the compressed state answers a boundary-specific local
question. It does not automatically include the separate RoPE path, query path,
cache-construction path, discrete kernel choices, recurrent state, MoE routes,
or later cache reuse.

Future compressed-attention Jacobian work must specify whether the derivative
endpoint is:

- pre-normalization `c_KV`;
- post-normalization `c_KV`;
- non-positional key component;
- value component;
- combined key after positional concatenation;
- attention output;
- cache entry as stored;
- cache entry as reconstructed; or
- downstream residual state.

Required diagnostics include exact JVP/VJP parity at the named boundary,
finite-difference checks, pre/post-normalization controls, separate content and
positional-path perturbations, fresh-prefill versus reused-cache strata, and
independently verified objective effects. A derivative through one branch may
not be presented as the derivative of the complete attention mechanism.

## Agents-A1 scaling consequence

Agents-A1-35B is identified by its released configuration as
`Qwen3_5MoeForConditionalGeneration` with a hybrid sequence architecture:
linear-attention layers alternate with periodic full-attention layers. It is
not an MLA model. No `c_KV`, induction-head layer, semantic-hub layer, rank, or
content/position result from the triggering model transfers to Agents-A1.

The technically credible sequence is:

1. Complete Q35Q exact-target-runtime provenance, strict loading,
   packed-tensor consumption, expert ordering, deterministic forward, VJP,
   JVP, and finite-difference admission.
2. Admit Agents-A1-4B as the tractable dense bridge under its exact checkpoint,
   tokenizer, layer types, recurrent or linear-attention state, full-attention
   cache, harness, verifier, and runtime.
3. Establish deterministic task-statistic, confidence, trajectory,
   hidden-state, spectral, memory, program-state, and external-verifier
   baselines before any compressed-state interpretation.
4. For each native attention family, identify exact pre/post state-update,
   query/key/value, positional, cache, gate, and residual boundaries rather
   than importing MLA names.
5. Test content, position, order, distance, entity, syntax, and objective labels
   with frozen probes and matched controls at each native boundary.
6. Complete observation-only evaluation before any state patching, cache
   rewriting, rank reduction, early exit, or routing intervention.
7. Separately admit Agents-A1-35B's checkpoint, quantization, router, routed and
   shared experts, hybrid attention, recurrent state, full-attention cache,
   kernels, topology, batching, scheduler, and capture path.
8. Measure attention-state, expert-route, hidden-state, and objective-outcome
   dissociations without assuming that one state is a semantic workspace.
9. Require router telemetry to add sealed value beyond native attention-state,
   confidence, trajectory, spectral, memory, program-state, and verifier
   controls.
10. Add Jacobian features only after exact derivative parity and sealed
    incremental value over the complete cheaper comparator stack.
11. Treat Gated MLA systems such as Kimi K3 only as separately admitted
    architecture comparators, not as implementation bridges into Agents-A1.
12. Keep patching, cache editing, rank reduction, early exit, retry, repair,
    forced routing, activation steering, and production control separately
    preregistered and gated with full-compute, no-intervention fallback.

## Current blocker and execution order

The current blocker is unchanged:

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

No MLA experiment, probe, cache capture, activation patch, compression change,
or Agents-A1 scaling run is authorized before the applicable artifact,
privacy, verifier, derivative, and resource gates pass.

## Established by this correction

The following are now binding program controls:

- compressed KV state and separate positional state are distinct identities;
- linear decodability is not native use, purity, or causal importance;
- probe-retention ratios cannot replace absolute calibrated metrics;
- weight-matrix rank, activation rank, semantic content, and safe compression
  are separate objects;
- disruption/outcome association is not activation patching;
- causal terminology requires an inline, consumed, re-propagated patch;
- model argmax is not an independent correctness verifier;
- comments and function names are not execution evidence;
- semantic-hub and circuit-topology claims require matched and replicated causal
  evidence;
- MLA findings do not transfer to Agents-A1's hybrid linear/full-attention
  architecture; and
- no privacy, sealed-data, verifier, provenance, derivative, GPU,
  intervention, or production gate is weakened.

## Not established

This correction does not establish:

- independent reproduction of arXiv `2607.23054v1`;
- robustness across seeds, corpora, scales, or production MLA models;
- a pure content representation in `c_KV`;
- absence of nonlinear or relative-position information;
- architectural causation of induction-head co-location;
- a semantic hub or global workspace;
- safe heterogeneous rank allocation or additional cache compression;
- a working causal patch in the pinned repository revision;
- objective correctness from target-token probability;
- transfer to Qwen3.5, Qwen3.6, Agents-A1, Kimi K3, or another large MoE;
- incremental router or Jacobian-Lens value beyond cheaper comparators;
- complete Q35Q runtime, loader, tensor-consumption, ordering, forward, or
  derivative admission; or
- safe patching, cache rewriting, rank reduction, early exit, truncation,
  retry, repair, forced routing, activation steering, or production deployment.

The research program remains unfinished.
