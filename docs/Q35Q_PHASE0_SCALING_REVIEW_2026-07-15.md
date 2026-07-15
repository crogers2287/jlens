# Q35Q Phase-0 scaling review — 2026-07-15

Status: **implementation hardening only; no GPU execution or scientific capture.**

This review follows the 2026-07-15T04:05Z aggregate heartbeat. It does not
change `steer.md`, alter M38E, authorize Q35Q GPU contention, weaken any frozen
scientific gate, or establish a Jacobian Lens result.

## Reference-implementation finding

The pinned `anthropics/jacobian-lens` implementation returns a separate
`d_model x d_model` Jacobian for every selected source layer in one prompt
calculation, accumulates a per-layer running sum, and merges disjoint prompt
fits by an `n_prompts`-weighted mean for every layer.

The first Q35Q Phase-0 scaling primitives did not fully preserve that contract:

1. `project_storage_bytes` projected one transport matrix rather than the full
   selected-source-layer set. For the frozen Phase-3 design, that would omit the
   multiplicative storage cost of layers `[4, 12, 20, 28, 36]`.
2. Sharded wall time used average prompts per worker. A deterministic shard set
   with a non-divisible prompt count is bounded by the most-loaded worker,
   `ceil(n_prompts / workers)`, not the average.
3. `ShardPartial` carried one matrix while declaring a source-layer set. That
   could not represent or verify the frozen multi-layer Phase-3 lens and could
   permit a nominally successful merge that omitted four of five matrices.

## Scaling corrections committed

- `f318a62a4ccb7b47cfbaa4b289245d5afec72b6c` — storage now multiplies by the
  complete source-layer count; wall time uses the most-loaded worker; workers
  may not exceed prompts; malformed timing inputs fail closed.
- `367bf48bb13c0d37e3631f715539104b6259a41e` — cost tests cover five-layer
  storage, non-divisible sharding, strict types, and conservative ceiling use.
- `be52d379e191bbc8f9e7c9a4415c0cd18faf641f` — shard artifacts now carry an
  exact source-layer-to-fp32-partial-sum mapping; all identities, keys, shapes,
  dtypes, finiteness, accumulation, and normalization are checked before a
  complete per-layer merge is returned.
- `734e63c3799b7135bed21f11a5c5a15440340b4f` — merge tests cover multi-layer
  exactness, cross-worker agreement at every layer, malformed identities,
  incomplete layer maps, overflow, and aggregate health.

An isolated CPU harness for the cost and merge modules passed 48/48 tests. This
is not a repository-wide result.

## Route-regime schema review

The concurrently landed route-regime artifact schema was directionally correct
but did not yet fail closed on all bindings required by the steering addendum:

- module identities, tensor identities, and observed layers were not bound
  one-to-one;
- duplicate or reordered observed layers could pass;
- architecture counts accepted numerically equal non-integer values;
- quantile keys and route-summary formulas were not frozen;
- threshold preregistration was represented by a boolean rather than a committed
  manifest digest;
- unknown fields could be ignored instead of rejected;
- source hashes were length-checked but not restricted to canonical lowercase
  SHA-256.

The following corrections were committed:

- `f8269fa9668c0d3bde655ab4e7cde99d21a11cf2` — exact ordered
  layer/module/tensor bindings, strict architecture integer identities,
  canonical hash validation, threshold-manifest binding, frozen margin
  quantiles, frozen route-load and transition summaries, unknown-field
  rejection, and a public aggregate binding digest.
- `d9ae6bcd959607b1f55c5670cebb9f5dad30ab80` — fail-closed tests for one-to-one
  bindings, duplicates, ordering, private/unknown fields, strict hashes,
  quantile monotonicity, fixed summaries, numerical ranges, and strict booleans.

The hardened route-regime files have not yet received a fresh repository-wide
test and commit-safety heartbeat. The earlier green result predates these two
commits and must not be attributed to the current head.

## Binding execution consequence

Before Q35Q Phase 1 or any shard manifest can be admitted:

- the full repository suite and commit-safety checks must pass at a head that
  contains all corrections in this review;
- every storage projection must bind the exact frozen source-layer count;
- every sharded wall-time projection must use the maximum assigned prompt
  count, not an average;
- every worker artifact must contain exactly one finite fp32 matrix for every
  frozen source layer;
- the merge must fail closed on missing, extra, reordered, malformed, or
  identity-mismatched layer state;
- every route-regime artifact must bind one immutable router module and tensor
  identity to every ordered observed layer;
- its near-boundary threshold must be linked to a pre-margin committed manifest;
- its quantiles and summary formulas may not be changed after collection.

## Claim boundary

No Q35Q VJP has run. GPTQ and NF4 exact backward support remain unproven. No
micro-fit, quantized Qwen3.5 lens, Agents-A1 transfer, native Agents-A1 lens,
correctness prediction, stopping policy, intervention, or production utility
is established. All raw matrices, routes, prompts, activations, and per-example
artifacts remain private and uncommitted.
