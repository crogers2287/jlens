# M39 — Forward-only Agents-A1 35B completed-error comparator (preregistration)

Status: **preregistration draft. No scientific rows may be collected until
M38E is finalized (steer 550c27b, sequence item 1).** This document freezes
the design; a separate committed amendment authorizes any capture.

Steer basis: `550c27b` (incorporates `0e812c1` and predecessors). All
sealed-data, verifier, privacy, provenance, claim-boundary, and
production gates remain binding.

## Question

Does any **forward-only, observation-only** telemetry feature block add
**stable, calibrated, verifier-labeled** incremental completed-error
prediction on the pinned Agents-A1 35B AWQ runtime, beyond frozen
nuisance baselines? This is a prediction/measurement study, not a
Jacobian lens, causal attribution, stopping rule, or intervention.

## Model and runtime (unchanged, pinned)

- checkpoint `cyankiwi/Agents-A1-AWQ-INT4`, revision
  `3e522d4e46438c782789b73c8ff4503e0edd037c`, architecture `qwen3_5_moe`
  (40 routed text layers, 256 experts, top-8);
- isolated vLLM 0.24.0 telemetry runtime, observation-only worker
  extension; outputs must remain within the frozen M36V nondeterminism
  envelope (parity gate);
- normal Agents-A1 GGUF serving restored + verified after every capture.

## Feature blocks (measured separately so increment is attributable)

1. **nuisance baseline (frozen covariates):** output/prompt/completion
   length, finish reason, task family, band/difficulty, output cap,
   truncation status, latency, verifier category, route count, and
   token-confidence summaries.
2. **router block:** router logits, top-k weights, margins, per-layer
   route-count and transition summaries.
3. **routing-load block (RouteScan-style, arXiv:2605.24817):**
   normalized per-expert load by layer, active-expert fraction, entropy,
   effective expert count, coverage gap, concentration.
4. **expert-contribution block (arXiv:2604.02178):** selected-expert
   output norms `‖expert_output_i(l,t)‖₂`, the router-weighted
   contribution `router_weight_i·‖expert_output_i‖₂`, and per-layer sums,
   maxima, dispersion, entropy, and concentration of contributions;
   contribution changes and route transitions across layers; multi-layer
   contribution-path features. **Router weight, output norm, and their
   product are measured separately** so a predictive increment cannot be
   attributed to the wrong component.
5. **hidden-state block:** residual-stream summaries and
   router-visible/router-blind energy at the frozen layer set.

Every block is summarized **separately for prefill and autoregressive
decode** where the runtime permits exact phase separation. Only
preregistered aggregate features stream to private storage; unnecessary
full expert activations are not retained.

## Capture-feasibility note (aggregate)

The existing `jlens_vllm_telemetry` path already captures router logits,
top-k weights/ids, and exact dispatch identity via the
`select_experts`/`forward_modular` wrappers (M36V full_telemetry). The
expert-contribution block additionally requires **per-expert output-norm
reduction inside the `forward_modular` observation hook** — a bounded
scalar per (layer, expert, token) computed on-device and summed, never
storing full expert outputs. This is an additive observation-only
measurement; it must re-pass the M36V dispatch-identity and parity gates
before any scientific row.

## Labels and primary population

- primary population: **completed, nontruncated** answers only;
- label: verifier-backed completed-error (correct vs incorrect); the
  correct answer and verifier result are **labels only** and may never
  enter a prediction feature;
- timeout/truncation prediction belongs to M36T and may not inflate M39.

## Statistics (frozen)

- leakage-free **nested cross-validation**; all preprocessing and feature
  selection fit on train folds only;
- **family-aware splits** and a **locked held-out evaluation set**;
- frozen nuisance covariates entered first; report **raw and
  nuisance-residualized** predictive increment of each block over the
  nuisance baseline and over the router block;
- transparent models only (calibrated logistic regression / nearest
  centroid — the project's established classifiers); no large learned
  head, hidden-state raw capture, or sealed-set feature search;
- metrics: balanced accuracy, average precision, calibration; paired
  bootstrap with frozen seeds and lower-bound rules mirroring M36T/M37J-A.

## Confirmatory rule and stop conditions

- **Advance only if** a forward-only feature block adds stable,
  calibrated, verifier-labeled completed-error prediction beyond **all**
  frozen baselines (nuisance + router), with the preregistered paired
  lower bound strictly above zero on the held-out set.
- Semantic expert labels are **exploratory and sealed**; LLM-made expert
  labels may not be scientific predictors, stopping rules, or
  interventions without a separate preregistration and held-out
  validation.
- Privacy: run a project-specific leakage/inversion audit under the
  frozen threat model before any non-invertibility or privacy-safety
  claim; the RouteScan paper alone does not establish it.
- If no block clears the rule, record the scoped negative and stop.

## Boundary

A positive M39 result establishes only forward-only predictive increment
on this frozen population and runtime. It is not a Jacobian lens, causal
attribution, expert semantics, safe early exit, route-quality measure,
intervention value, or production authorization. Only after a forward-only
block clears may the sequence proceed to reduced-target VJP /
finite-difference Jacobian probes on a smaller comparable MoE or the
official Agents-A1 4B checkpoint if released — under separate frozen gates.
