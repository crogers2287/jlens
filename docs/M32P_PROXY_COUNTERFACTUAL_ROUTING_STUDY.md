# M32P proxy counterfactual expert-routing study

M32P asked the causal routing question on the local Qwen1.5-MoE-A2.7B-Chat
research proxy: when the frozen model fails near its own capability frontier,
does an equal-compute alternative expert route already inside the model
produce a better answer — and can a non-oracle policy find it?

**Verdicts under the preregistered rules: H1 not established, H2 not
established, H3 no candidate survived. Telemetry-guided expert swaps rescued
exactly as many failures as matched-random swaps.** Every claim here is
proxy-scoped; nothing transfers to Agents-A1.

## Phase 0A — route-override hook

A prepended forward hook on one layer's `Qwen2MoeTopKRouter` edits only the
last position's router logits and rebuilds that row's scores/indices with the
router's own arithmetic; dispatch and the shared expert run unchanged. Swap
semantics keep exactly top-4 active experts with no duplicates. Six CPU tests
on a tiny real qwen2_moe cover no-op bit-parity, swap correctness, invalid
plans, penalties, KV-cache branch independence, and plan privacy. The real
smoke gate passed: architecture verified (24 routed layers × 60 experts,
top-4), disabled-override greedy parity, a forced swap changes routing, peak
memory 27.95 GiB.

## Phase 0B — model-calibrated benchmark

A predeclared 288-row calibration sweep (12 cells, frozen structure
definitions and seeds, disjoint from all prior sets) mapped the proxy's
frontier:

| Cell | Pass rate | Class |
|---|---:|---|
| 2×1 | 1.000 | easy |
| 2×2 low-carry | .958 | easy |
| 2×2 carry-heavy | .417 | **boundary** |
| 3×1 | .917 | easy |
| 3×2 low-carry | .833 | (gap) |
| 3×2 carry-heavy | .042 | hard |
| 4×1 | .958 | easy |
| 4×2 low-carry | .708 | **boundary** |
| 4×2 carry-heavy | .000 | hard |
| 3×3 | .083 | hard |
| middle-zero 3×2 | .375 | **boundary** |
| near-power-of-ten 3×2 | .667 | **boundary** |

Carry structure — not digit count — dominates the proxy's multiplication
difficulty. The frozen rules chose N=192: four boundary cells × 36 (75%), two
easy anchors × 12, two hard anchors × 12; expected failures 90.

## Decision run (one window, 34 minutes, peak 28.3 GiB)

- 192 fresh decision tasks (disjoint from M29/M30/M31/abandoned-M32 and the
  sweep); realized failures 41 discovery / 18 validation / 21 holdout — every
  predeclared power minimum met; 0 undecided.
- Frozen M30 trigger on original telemetry: rate .401, precision .766, recall
  .738 — measurably degraded from ~.89 on the earlier band-based
  distributions. The detector transfers imperfectly to the model-calibrated
  frontier; reported as a finding, not tuned.
- Causal screen: 7,204 one-step counterfactual screens and 616 full branched
  continuations across telemetry-fragile steps and implicated layers, with
  identical budgets for heuristic and matched-random arms.

## Results

### H1 — route recoverability: NOT ESTABLISHED

On sealed-holdout triggered true failures (n=16), the heuristic route
families' oracle rescue rate was .125 — *identical* to matched-random search
(.125; paired 95% CI [0, 0]: the same tasks were rescued). Across all
triggered failures the oracle-tested recoverable fraction was 11.9%.

### Route families behave like noise

| Family | Full continuations | Rescues | Regressions |
|---|---:|---:|---:|
| each_selected→rank5 | 181 | 13 | 18 |
| lowest_weight→rank5 | 31 | 0 | 4 |
| selected→rank6 | 39 | 1 | 4 |
| diversity swap | 57 | 3 | 6 |
| matched random | 308 | 21 | 32 |

Heuristic targeting (telemetry-fragile steps, implicated layers, structured
swap choices) rescued at the same per-branch rate as random equal-compute
perturbation, and every family introduced more regressions than rescues on
triggered-passing tasks.

### H2 — deployable rerouting: NOT ESTABLISHED

The validation-frozen non-oracle policy (top-screened heuristic branch)
produced holdout success .5625 — exactly normal routing's .5625 and exactly
the matched-random policy's .5625. Deltas span zero.

### H3 — soft penalties: NO CANDIDATE SURVIVED

No layer-expert pair met even the discovery gates (support ≥5, net rescues
≥2). There is nothing to penalize that generalizes.

## Interpretation (proxy-scoped)

Within this proxy, task family, and decode protocol, systematic
multiplication failures are **not** caused by locally poor top-4 expert
choices at telemetry-fragile tokens. A small (~12%) fraction of failures can
be jolted into passing by *any* equal-compute route perturbation — random
works as well as guided — which is best read as decode-path sensitivity, not
expert misrouting. Combined with M31 (resampling rescues ~4.5%), the evidence
now points consistently away from within-model stochastic/routing repair and
toward the two remaining repair directions: structured prompting operators
and telemetry-gated tool routing.

Per the preregistered branch rules (Branch 3), the expert-routing track stops
here. No router training, no expert blacklist, no production change.

## Privacy

Public artifacts contain aggregate cell rates, counts, family statistics, and
intervals only — no operands, prompts, outputs, per-task routes, expert
identities tied to tasks, paths, tokens, or tensors. Calibration rows, branch
records, and route tables stay gitignored.

Public artifacts:

- `data/prompts/m32p_frontier_sweep_config.json`
- `data/prompts/m32p_proxy_routing_manifest.json`
- `reports/telemetry/hf_m32p_proxy_routing_feasibility.json`
- `reports/telemetry/hf_m32p_proxy_benchmark_frontier.json`
- `reports/telemetry/hf_m32p_proxy_routing_run_summary.json`
- `reports/telemetry/hf_m32p_proxy_routing_evaluation.json`
