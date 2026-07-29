# STEER ADDENDUM — Dispatch/weight separation, latent-MoE boundaries, and depth-routing gates

Date: 2026-07-29
Parent remote head: `7a4da4cbe4a03457c93b899c47896ffdc5b9f03f`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and every
cumulative steering correction. It preserves every privacy, sealed-data,
verifier, provenance, exact-set, exact-gradient, numerical-parity, resource,
commit-safety, cleanup, intervention, production-gating, and stop rule. It
authorizes no weight retrieval, model execution, GPU use, hidden-state or
router capture, Jacobian fitting, sealed evaluation, training run, policy
update, control action, or production deployment.

The aggregate Q35Q outcome remains:

`q35q_artifact_admission_blocked`

The active engineering milestone remains exact-target-runtime Q35Q loader and
derivative admission. This addendum changes future architecture and telemetry
identity requirements; it does not displace that milestone.

GitHub reports `crogers2287/jlens` as public. Only aggregate program-control
and public-source engineering material may be committed. Prompts, outputs,
token data, per-example outcomes, hidden states, router logits, dispatch
scores, expert paths, expert weights, depth-routing weights, recurrent states,
KV caches, verifier records, model weights, credentials, host paths, and
private environment details remain prohibited.

## Triggering primary evidence

Kimi Team, `Kimi K3: Open Frontier Intelligence`, arXiv `2607.24653v1`,
submitted 2026-07-27, describes a 2.8T-parameter MoE with 104B activated
parameters, 93 layers, 69 Kimi Delta Attention layers, 24 Gated MLA layers,
Stable LatentMoE, Attention Residuals, 896 routed experts, 16 routed experts
selected per token, two shared experts, a 1,048,576-token context window, and
MXFP4-weight/MXFP8-activation quantization-aware training.

The attributable public repository is pinned for this correction at:

`MoonshotAI/Kimi-K3@7c5be9599120d7993748de66a76128614f15f210`

The report's Quantile Balancing construction materially separates quantities
that are often collapsed under the word `router`:

- the router produces un-biased sigmoid scores `s_i`;
- dispatch uses top-k selection over `s_i + b_i`, where `b_i` is an
  expert-specific balancing bias;
- mixture weights are computed from the un-biased `s_i`, not from `s_i+b_i`;
- the balancing bias can therefore change the executed expert set without
  entering the reported mixture-weight formula or ordinary router-gradient
  path; and
- the top-(k+1) cutoff statistic is used to update dispatch bias.

Stable LatentMoE also introduces a lower-dimensional routed-expert branch,
normalization around the routed latent aggregate, projection back to model
width, and separate full-width shared experts. Attention Residuals select from
prior depth sources rather than representing depth only as a fixed sequential
residual chain. KDA recurrent state, Gated MLA KV state, Attention-Residual
source weights, and MoE expert routes are distinct state and routing objects.

The evidence is architectural and implementation-facing. It does not establish
that Kimi K3's routes are semantically interpretable, that balancing bias
contains correctness information, that depth-source weights form a semantic
workspace, that any telemetry transfers to Agents-A1, or that the released
weights and serving paths satisfy jLens admission requirements.

## Bounded interpretation

The triggering evidence supports the following narrow correction:

> Dispatch selection, mixture weighting, routed-expert computation,
> shared-expert computation, latent aggregation, depth-source selection,
> recurrent attention state, and objective outcome are separate scientific and
> production objects.

The same executed expert indices can carry different mixture weights. The same
un-biased scores can produce different routes under different dispatch biases.
The same routed aggregate can be changed by normalization or projection. The
same MoE route can coexist with different Attention-Residual depth routes,
recurrent states, KV caches, shared-expert outputs, and final outcomes.

Balanced utilization is not semantic specialization. A dispatch bias is not a
correctness score. A selected depth source is not evidence of conscious access,
episodic recall, or a global semantic workspace. Architectural sparsity is not
causal attribution.

## Binding dispatch-score and mixture-weight identity gate

Every compatible MoE study must freeze and report these quantities separately
where they exist:

1. router input activation boundary;
2. router projection and pre-activation value;
3. router nonlinearity and un-biased score;
4. auxiliary dispatch bias or offset;
5. biased dispatch score;
6. capacity, mask, temperature, tie, and overflow transformations;
7. top-k and top-(k+1) cutoff values and margins;
8. selected expert indices and ordering;
9. mixture-weight source score;
10. mixture-weight normalization, flooring, clipping, and precision;
11. whether dispatch bias enters mixture weights;
12. whether dispatch bias receives gradient;
13. routed expert inputs, outputs, and combine order;
14. shared-expert inputs, outputs, gates, and combine order;
15. post-combine normalization and projection;
16. physical dispatch, communication, kernel, topology, and scheduler; and
17. independently verified objective outcome.

A field named `router_logits`, `routing_weights`, `expert_scores`, or
`selected_experts` does not satisfy this gate without proving which object it
contains. A framework may expose a post-bias dispatch tensor while another
exposes pre-bias weights. Nominally matching field names are not semantic or
numerical parity.

## Mandatory dispatch/weight counterfactuals

Before assigning predictive or causal value to router telemetry, future work
must test, where technically feasible:

1. fixed un-biased scores with changed balancing bias;
2. fixed balancing bias with changed un-biased scores;
3. unchanged selected set with changed selected order;
4. unchanged selected set and order with changed mixture weights;
5. changed selected set with matched aggregate mixture-weight statistics;
6. perturbations around the k-th versus (k+1)-th cutoff;
7. deterministic tie and near-tie cases;
8. matched random or permuted bias vectors;
9. preserved expert-load marginals with broken example correspondence;
10. same logical route under different precision, kernels, batching, and
    expert-parallel placement; and
11. same telemetry summary with different independently verified outcomes.

If a signal loses value after score margin, position, token frequency,
confidence, length, load, or difficulty matching, it has not established
route-specific correctness information.

## Quantile-balancing state gate

Any balancing method based on moving quantiles, cutoffs, histograms, load
statistics, or online bias updates must freeze:

- update cadence and clock;
- population and window used for the statistic;
- per-device versus globally reduced semantics;
- exact reduction and synchronization order;
- warm-up and initialization;
- stale, missing, duplicate, and out-of-order update handling;
- clipping, smoothing, decay, and numerical precision;
- treatment of padding, packed sequences, multimodal tokens, and generated
  versus prefill tokens;
- checkpoint, restart, reshard, and replica-recovery semantics; and
- whether evaluation freezes or continues updating the balancing state.

A balancing state that changes during evaluation is part of the executable
artifact. Two runs with identical model weights but different bias state are
not the same model condition.

## Stable-LatentMoE boundary gate

For a latent-width MoE, compatible studies must distinguish at least:

1. full-width block input;
2. router input;
3. latent down-projection input and output;
4. per-expert latent input;
5. per-expert latent output;
6. weighted routed latent aggregate before normalization;
7. routed latent aggregate after normalization;
8. latent-to-model-width up-projection;
9. each shared-expert branch;
10. shared-expert gates and aggregate;
11. routed-plus-shared combination;
12. final block contribution; and
13. downstream residual state.

Fused kernels may combine several objects physically. A fused implementation
does not eliminate their scientific identity. Observation at one exposed
boundary may not be represented as observation of an unexposed intermediate.

Expert selection alone cannot establish expert contribution. Expert output
norm alone cannot establish downstream effect. Routed contribution alone
cannot establish block attribution when shared experts are always active.

## Depth-routing and Attention-Residual identity gate

Architectures that dynamically select, weight, or retrieve prior depth sources
must treat depth routing separately from token attention and MoE expert routing.
The frozen identity includes:

- candidate source blocks and embedding source;
- source-value boundary and normalization;
- pseudo-query or source-score computation;
- source mask, bias, temperature, normalization, and precision;
- selected or weighted source set;
- dense versus sparse depth aggregation;
- source ordering and residual-combine rule;
- cross-device placement and communication;
- whether source activations are recomputed, cached, quantized, compressed, or
  offloaded; and
- the exact downstream map used for any derivative.

Required controls include fixed sequential residuals, uniform source weights,
matched random weights, source-label permutation, neighboring-depth placebos,
matched source-count conditions, preserved source-weight marginals with broken
example correspondence, and ablations that separate source identity from
source content.

An Attention-Residual weight is not a semantic relevance label. High source
weight does not establish causal necessity. A depth-route change does not
imply an MoE expert-route change, and an expert-route change does not imply a
depth-route change.

## Hybrid attention-state and cache-lineage gate

For models mixing recurrent or linear attention with KV attention, future work
must freeze and report separately:

- KDA or other recurrent-state identity and update boundary;
- Gated MLA or other KV-cache identity;
- Attention-Residual depth-source state;
- prefill versus decode state construction;
- chunked-prefill, prefix-cache, paging, eviction, compression, and offload;
- multimodal encoder and cross-modal token boundaries;
- state dtype, quantization, accumulator, and kernel;
- batch, sequence packing, scheduler, topology, and synchronization; and
- reset, reuse, fork, rollback, and failure-recovery semantics.

A hidden-state or Jacobian result conditioned on one recurrent/cache state does
not transfer to another state construction. Prefix-cache reuse, fresh prefill,
and resumed persistent state are separate executable conditions until parity is
proved at every claimed observable and intervention boundary.

## Derivative and intervention consequences

For Jacobian-Lens work, the downstream map must include the exact frozen
combination of depth-source routing, attention state, dispatch bias, selected
experts, mixture weights, shared experts, latent normalization, projection,
cache state, and runtime.

A derivative holding discrete routes fixed answers a conditional local
question. It does not estimate the effect of crossing a top-k boundary. A
finite perturbation that changes expert or depth selection is a hybrid
discrete-continuous intervention and must be reported separately.

Required derivative diagnostics include:

- distance to every relevant top-k and depth-route boundary;
- fixed-route JVP/VJP parity;
- boundary-crossing finite differences;
- route-unchanged and route-changed strata;
- shared-expert and routed-expert contribution controls;
- latent pre/post-normalization and pre/post-projection controls; and
- independently verified outcome changes rather than telemetry changes alone.

Forced routing, bias editing, expert suppression, source-weight editing,
recurrent-state editing, cache rewriting, activation addition, early exit,
retry, and production control remain prohibited until separately preregistered
and admitted.

## Privacy-preserving telemetry gate

Prospective telemetry design for large MoEs must minimize collection before any
sealed evaluation. Publicly retain only prospectively frozen aggregates such
as, where justified:

- score entropy and top-k margin summaries;
- bias displacement and route-turnover rates;
- top-(k+1) cutoff summaries;
- shared-versus-routed aggregate energy ratios;
- latent pre/post-normalization norm summaries;
- depth-source entropy and turnover summaries;
- KDA/MLA state-norm summaries; and
- capture cost, dropped-event, and synchronization statistics.

Raw prompts, outputs, token identities, router vectors, per-token expert paths,
per-example depth weights, hidden states, cache entries, recurrent states,
expert outputs, predictions, verifier labels, and sealed outcomes remain
private and may not be committed. Aggregate telemetry must still undergo
membership, reconstruction, linkage, and rare-stratum risk review before any
release.

## Agents-A1 scaling consequence

The technically credible sequence is:

1. Complete Q35Q exact-target-runtime provenance, strict loading, packed-tensor
   consumption, expert ordering, deterministic forward, VJP, JVP, and
   finite-difference admission.
2. Admit Agents-A1-4B as a dense bridge under its exact checkpoint, tokenizer,
   hybrid-attention state, cache, harness, verifier, and runtime.
3. Establish deterministic, confidence, trajectory, hidden-state, spectral,
   memory, program-state, and external-verifier baselines.
4. Separately admit Agents-A1-35B's checkpoint, quantization, router, routed and
   shared experts, hybrid attention, cache, kernels, topology, batching,
   scheduler, and capture path.
5. Prove the exact distinction between raw router scores, dispatch-adjusted
   scores, selected experts, and consumed mixture weights in the admitted
   Agents-A1 runtime.
6. Capture bounded aggregate route, shared/routed contribution, attention-state,
   and cache-lineage summaries at prospectively frozen boundaries.
7. Test expert-route, attention-state, and objective-outcome dissociations
   without assuming that one route is an algorithm or semantic workspace.
8. Require router telemetry to add sealed value beyond all cheaper controls and
   beyond load, margin, confidence, position, length, and difficulty features.
9. Add Jacobian features only after exact derivative parity and sealed
   incremental value over the complete dispatch-, weight-, shared-expert-,
   attention-state-, cache-, and verifier-aware comparator stack.
10. Keep stopping, retry, repair, forced routing, bias editing, activation
    steering, reward shaping, and deployment separately gated with full-compute
    fallback.

Kimi K3 is a frontier architecture comparator, not a tractable bridge or an
Agents-A1 substitute. No layer, head, expert, threshold, bias statistic,
depth-routing rule, monitor, or intervention transfers from Kimi K3 to
Agents-A1 without prospective evidence and separate artifact admission.

## Current blocker and outcome

The active blocker remains exact-target-runtime Q35Q admission:

1. execute the composed Transformers provenance adapter in the exact target
   runtime using aggregate evidence only;
2. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
3. bind the actual GPTQModel/Defuser loader and complete executable source
   closure;
4. run strict synthetic Qwen3.5-MoE loading;
5. prove one-time packed-tensor consumption and exact expert/fusion ordering;
6. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
7. complete the Phase-0 conjunction before weight staging or GPU authorization.

Established by this correction:

- dispatch score and mixture weight are separate identities;
- balancing state is part of the executable artifact;
- selected experts and expert contribution are separate identities;
- routed and shared expert branches require separate attribution;
- latent pre/post-normalization and projection boundaries are distinct;
- depth routing, token attention, and expert routing are separate objects;
- recurrent state, KV cache, and depth-source state require separate lineage;
- fixed-route derivatives do not cover discrete route-boundary changes; and
- no existing privacy, sealed-data, verifier, provenance, derivative, GPU,
  intervention, or production gate is weakened.

Unproven:

- independent reproduction of Kimi K3's architecture or reported scaling;
- semantic meaning or correctness value of Kimi K3 routes or depth weights;
- transfer of any Kimi K3 mechanism to Qwen3.5, Qwen3.6, or Agents-A1;
- incremental router or Jacobian-Lens value beyond cheaper comparators;
- complete Q35Q runtime, loader, tensor-consumption, ordering, forward, or
  derivative admission; and
- safe early exit, truncation, retry, repair, forced routing, bias editing,
  cache/state intervention, activation steering, reward shaping, or production
  deployment.

The research program remains unfinished.
