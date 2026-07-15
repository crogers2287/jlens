# STEER ADDENDUM — Q35Q route-regime diagnostics and exact prompt sharding

Status: **binding Q35Q design amendment; not GPU execution authorization.**

This addendum amends `docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md` before
any Q35Q live backward call. It does not alter M38E, authorize GPU contention,
permit outcome-bearing M39 capture, weaken exact-VJP, memory, parity, privacy,
provenance, commit-safety, sealed-data, verifier, production, or stop gates, or
change the frozen GPTQ-then-NF4 candidate order.

## Evidence and implementation boundary

The following evidence motivates a narrower and more technically credible path
to Agents-A1-scale Jacobian fitting:

- `anthropics/jacobian-lens` commit
  `581d398613e5602a5af361e1c34d3a92ea82ba8e` states that exact fitting costs
  one forward and `ceil(d_model / dim_batch)` backward passes per prompt. Its
  reference implementation explicitly supports disjoint prompt shards followed
  by an `n_prompts`-weighted `JacobianLens.merge`.
- `Routers Learn the Geometry of Their Experts` (arXiv:2605.12476v1) derives
  and measures coupling between router scores and selected-expert computation.
  Its repository at commit
  `530434bf9c0f873ace187cca8b0a4c73dd6cae5f` is only a code placeholder and
  is not an executable dependency.
- `When Are Experts Misrouted? Counterfactual Routing Analysis in
  Mixture-of-Experts Language Models` (arXiv:2605.07260v1) reports that
  executed top-k routes can be least informative on fragile reasoning tokens
  in several open MoEs. Its intervention results do not transfer to Q35Q and do
  not authorize counterfactual routing here.
- `Code Correctness Signals in LLM Hidden States` is now arXiv:2606.14530v2,
  with public repository head
  `fcef83755c09f66f948e9cc4b009616dd88bee77` at review time. The paper and
  repository changed materially across versions, reinforcing the existing rule
  that borrowed methods must pin both paper version and immutable code commit.
- `Jacobian Scopes` (arXiv:2601.16407v1; repository
  `AntonioLiu97/JacobianScopes` commit
  `ffbfe96ebb7a24c25c0d34b70a494e134e1f5ed9`) studies token-input attribution.
  It is not the residual-to-final-basis average transport implemented by
  Jacobian Lens and is not adopted as a substitute.

These sources do not establish an Agents-A1 lens, route mechanism, correctness
predictor, or safe intervention.

## Exact local derivative claim boundary

A standard autograd VJP through a sparse top-k MoE is a local derivative through
the **executed route regime**. The discrete top-k membership decision is not a
continuous path through alternative experts. Therefore a passing Q35Q VJP may
be described only as an exact autograd derivative of the admitted quantized
model at the executed route regime.

It may not be described as:

- a derivative over counterfactual expert assignments;
- evidence that the selected experts were optimal;
- evidence that the Jacobian remains valid across a route-boundary crossing;
- evidence that architecture equality alone makes transport portable across
  checkpoints or quantizations.

No straight-through route estimator, soft-router replacement, finite-difference
route search, sampled alternative route, or router update is authorized inside
Q35Q.

## Mandatory route-regime engineering artifact

Before the Phase-2 micro-fit, the Phase-1-passing path must produce an
aggregate-only route-regime artifact from the same one-sequence gate. The
artifact and formulas must be committed before collection and must bind:

1. exact router module and tensor identities for every observed MoE layer;
2. top-k value, routed/shared expert conventions, routing bias convention, and
   whether reported scores are pre-bias, post-bias, pre-softmax, or post-softmax;
3. repeated-forward selected-route parity under identical inputs and runtime;
4. aggregate quantiles of the selected-boundary margin, defined as the score of
   the kth selected expert minus the score of the highest unselected expert;
5. a preregistered numerical-near-boundary threshold derived from dtype/runtime
   precision before seeing route margins, plus the aggregate fraction below it;
6. aggregate route-load and route-transition summaries needed to verify that
   the hook observes the executed router without changing output;
7. exact token parity, logit parity, hook overhead, memory, cleanup, privacy,
   and source hashes.

Raw router logits, expert identities, token-level routes, per-layer-by-token
matrices, prompts, and per-example margins remain private and uncommitted.

A route-regime artifact is diagnostic. It does not replace the exact-VJP gate.
Near-boundary routing does not permit retuning the prompt, layer, threshold,
quantization, or runtime after observation. It narrows claims and may block a
mechanistic portability claim while leaving a purely descriptive technical
result reportable.

## Transfer route compatibility

Every Phase-4 cross-checkpoint transfer must add, at identical private tokens
and layers:

- selected-route overlap aggregated across tokens and layers;
- selected-boundary margin distributions for source and target;
- aggregate frequency of route changes between source and target;
- separate summaries for routed and shared expert contributions where exposed;
- unchanged forward-output parity with observation enabled.

Architecture and tokenizer compatibility remain necessary but are not sufficient
for a route-conditioned Jacobian portability claim. Low route overlap or a
material concentration of near-boundary tokens must be reported as a route-
regime limitation. It may support `q35q_transfer_not_established`; it may not be
hidden by pooling quantizations or choosing a different target after outcomes.

## Mandatory exact-cost projection after Phase 1

Phase 1 must record enough aggregate timing to project the bounded fit before
Phase 2 or Phase 3 begins:

- admitted `d_model` and `dim_batch`;
- exact backward passes per prompt,
  `ceil(d_model / dim_batch)`;
- measured forward, first-backward, steady-backward, and cleanup time;
- projected wall time for the frozen Phase-2 and Phase-3 prompt counts;
- projected peak storage for running sums, checkpoints, and final lens files;
- the assumptions and uncertainty margin used by the projection.

The projection is an engineering gate, not an outcome. If the frozen Phase-3
attempt is projected to exceed its 24-hour wall-clock ceiling on one worker, the
program must not begin a knowingly impossible single-worker fit and then retune
it after partial results.

## Exact horizontal prompt sharding

After a successful Phase-2 micro-fit, Phase 3 or the later native Agents-A1 fit
may use horizontal prompt sharding only under a separately committed pre-outcome
manifest. Sharding is permitted because the official reference estimator forms
an arithmetic mean over independent prompt Jacobians and its merge operation is
an `n_prompts`-weighted mean.

The shard manifest must freeze:

1. total prompt count, ordered prompt hashes, deterministic shard assignment,
   worker count, and merge order;
2. identical model revision, quantization, tokenizer, source/target layers,
   estimator reduction, `dim_batch`, sequence length, skip positions, package
   versions, kernel identities, and numerical precision on every worker;
3. per-worker hardware, device placement, memory gate, runtime ceiling, privacy
   boundary, and artifact hashes;
4. no adaptive shard reassignment, prompt deletion, worker substitution, or
   precision change after any lens value or validation result is visible;
5. a synthetic exact-merge test and a duplicated-neutral-prompt cross-worker
   numerical agreement smoke before scientific shards begin;
6. private atomic shard checkpoints and public aggregate-only completion,
   numerical-health, timing, and hash records;
7. a deterministic fp32 accumulation and weighted merge implementation that
   verifies source-layer sets, `d_model`, prompt counts, and all frozen identities
   before merging.

Horizontal sharding changes wall-clock parallelism only. It may not reduce the
frozen corpus, omit output dimensions, replace exact VJPs with sketches, change
power, or pool different checkpoints, quantizations, kernels, or estimator
formulas. The existing 24-hour wall-clock ceiling, total prompt count, validation
set, privacy rules, and claim boundaries remain unchanged.

If identical admitted workers are unavailable, the program records the bounded
resource block and retains the separately frozen high-memory BF16 path. It does
not weaken the fit.

## Program-order effect

The Q35Q order is now:

1. finish M38E and all frozen audits unchanged;
2. complete CPU-only Phase 0, including fail-closed loader/admission tests;
3. commit the model-specific admission and route-regime artifact schemas;
4. run the one-sequence exact-VJP and route-regime gates after GPU release;
5. commit aggregate timing and exact-cost projection;
6. run the frozen eight-sequence micro-fit only if the exact path and bounded
   resource projection remain viable;
7. before Phase 3, commit either a single-worker fit manifest that clears the
   24-hour projection or an exact horizontal-shard manifest satisfying this
   addendum;
8. retain M39 as the independent observation-only correctness-monitoring study;
9. retain native BF16 Agents-A1 fitting as the final reference comparison under
   a separate frozen protocol.

## Completion boundary

This amendment establishes only a stricter engineering and claim framework. No
Q35Q live VJP has passed. No route-regime artifact has been captured. No
quantized Qwen3.5 or Agents-A1 lens has been validated. No transfer, correctness,
stopping, routing, repair, or production utility is established. The research
program remains incomplete.
