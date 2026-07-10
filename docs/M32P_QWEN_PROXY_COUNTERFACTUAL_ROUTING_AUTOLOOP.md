# M32P Qwen proxy counterfactual-routing autoloop

Status: operator-authorized protocol. This supersedes the stopped Agents-A1
M32R execution path without changing or deleting its Phase-0 feasibility record.
All claims from this loop must be scoped to the already-local
`Qwen1.5-MoE-A2.7B-Chat` research proxy.

`steer.md` is the execution source of truth and `CODEX_AUTOSTEER.md` remains the
operating contract.

## Why this proxy path exists

M32R established, before any decision capture, that official Agents-A1
safetensors cannot be loaded inside the current 44 GiB research ceiling with
the installed stack. The proxy model is already local, already produced the
M26-M31 telemetry evidence, exposes real MoE router logits, and can answer the
causal-method question now:

> When the model fails, does an equal-compute alternative expert route inside
> the same frozen model produce a better answer, and can a non-oracle policy
> choose that route without seeing the answer?

This loop does **not** establish anything about Agents-A1 expert routing. It
builds and validates the method on the proxy so it is ready for Agents-A1 when
a viable checkpoint or hardware path exists.

## Scope and invariants

- Model: already-local `Qwen1.5-MoE-A2.7B-Chat` only.
- Expected architecture: `qwen2_moe`, 24 routed layers, 60 experts per routed
  layer, top-4 active experts per token. Verify from the loaded config and stop
  on mismatch.
- No model download, new model family, weight update, LoRA, or new dependency.
- Keep the M30 detector and p(fail) threshold frozen. Reproduce its published
  confusion matrix/hash before decision capture.
- Fresh tasks only. M27, M29, M30, M31, abandoned M32, and stopped M32R records
  are not decision data.
- Never reveal the correct answer to the route-selection policy.
- Preserve exactly top-4 active experts and equal expert compute in every
  counterfactual route. Renormalize selected routing weights.
- Disabled route override must reproduce the normal forward path within a
  preregistered numerical tolerance and produce identical greedy tokens on the
  smoke set.
- No global expert blacklist or permanent shutdown from observational counts.
- Private prompts, outputs, token ids/text, raw router tensors, per-task routes,
  expert tables, labels, and counterfactual records stay gitignored.
- Public reports remain aggregate-only. Production remains gated.

# M32P — route-override feasibility and causal screen

## Phase 0 — safe route-override hook

Implement an opt-in proxy-only route controller around the supported sparse MoE
forward path. It must accept a per-forward override plan keyed by generated
step and routed layer and be able to replace selected expert ids/weights after
router logits are computed but before expert dispatch.

Required behaviors:

1. `override=None` follows the original model code path.
2. A replacement keeps exactly four active experts.
3. No duplicate expert ids are permitted.
4. Routing weights are finite, nonnegative, and renormalized.
5. The default path remains compatible with telemetry capture and KV cache.
6. Counterfactual continuations use the modified forward result and modified KV
   cache from the intervention point onward; do not splice a changed token into
   an unchanged cache.
7. The hook can be enabled for exactly one layer-token choice and automatically
   removed afterward.

Tests before real capture:

- fake-MoE dispatch and weight-renormalization tests;
- no-op exact-path test;
- selected-expert/rank-next replacement test;
- duplicate/out-of-range/nonfinite rejection tests;
- KV-cache continuation test;
- telemetry capture remains available under override;
- privacy/no-route-table public-output test.

Real smoke gate:

- load the already-local proxy within the existing hardware limits;
- verify architecture and top-k;
- run normal and disabled-override decodes on a tiny private smoke set;
- run one forced equal-compute swap and verify output/telemetry can differ;
- restore the normal model path after the smoke.

Stop if architecture, hook placement, no-op parity, cache correctness, or
telemetry availability cannot be verified.

## Preregistered decision design

Before task generation or causal capture, commit
`data/prompts/m32p_proxy_routing_manifest.json` with:

- 192 fresh multiplication tasks over the existing six boundary bands;
- deterministic tuple rejection against M29, M30, M31, and abandoned M32;
- 96 discovery / 48 validation / 48 sealed holdout;
- original greedy decode protocol;
- frozen M30 detector reconstruction and threshold;
- fragile-window rule;
- implicated-layer rule;
- candidate-route families and exact branch budgets;
- random seeds, tie breaks, bootstrap seeds, multiple-testing correction;
- H1/H2/H3 claim rules;
- all tasks retained and no post-hoc operator deletion.

## Fragile-window and layer targeting

Do not screen all 1,440 layer-expert modules globally. Screen causal choices
only where the original generation shows elevated risk.

Freeze a deterministic rule using original-decode telemetry only, such as:

- choose up to the top two generated steps by the frozen window-risk score;
- at each chosen step, choose up to the top four routed layers by a predeclared
  combination of router entropy, top-4/rank-5 margin, concentration, and
  deviation from the task's earlier routing trajectory;
- no verifier label or correct answer may influence step/layer selection.

Report sensitivity to length and difficulty metadata so route effects are not
mistaken for task-complexity effects.

## Equal-compute route families

For each selected step/layer, evaluate shared counterfactual candidates:

1. `normal_route` — unchanged router output.
2. `lowest_weight_to_rank5` — replace the lowest-weight selected expert with
   the highest-ranked unselected expert.
3. `each_selected_to_rank5` — four one-at-a-time swaps, one for each selected
   expert, using rank-5 as replacement.
4. `selected_to_rank6` — bounded secondary swaps fixed in the manifest.
5. `diversity_swap` — replace the selected expert most redundant with the other
   selected experts using a discovery-only expert-output similarity summary.
6. `matched_random_swap` — same number of swaps, chosen from eligible unselected
   experts with fixed seeds.
7. `soft_penalty_route` — discovery-fit layer-expert penalties applied only in
   fragile windows, validation-frozen before sealed holdout.
8. `oracle_best_tested` — verifier-best tested branch, ceiling only and never a
   deployable policy.

The normal, heuristic, random, and oracle arms must receive the same full-
continuation budget. A cheap one-step screen may rank branches only if the
screening rule and full-continuation count are preregistered and identical
across heuristic and random controls.

## Outcomes and primary hypotheses

Deterministic `math_checker` verdicts define pass/fail after full continuation.
Undecided and capped cases are reported and excluded only according to the
manifest.

### H1 — route recoverability exists

Among frozen-trigger true failures, tested equal-compute counterfactual routes
recover more errors than matched-random route search.

Classify `route_recoverability_established` only if the paired 95% bootstrap CI
for the oracle-tested-family rescue-rate delta over matched-random is strictly
above zero on the sealed holdout. Oracle results are capability evidence only.

### H2 — a deployable route policy works

A validation-frozen non-oracle route policy improves verified success over both
normal routing and matched-random routing on the sealed holdout.

Classify `deployable_rerouting_established` only if both paired 95% success-rate
delta intervals are strictly above zero. The policy may use original telemetry,
router ranks/margins, and discovery/validation summaries, but never task labels,
correct answers, or candidate verifier results.

### H3 — expert penalties generalize

Any proposed layer-expert soft penalty must:

- be proposed from discovery only;
- repeat directionally on validation;
- be frozen before holdout;
- improve holdout outcomes after the preregistered multiplicity correction;
- avoid a significant right-to-wrong regression increase.

Otherwise classify it as exploratory only. No hard shutdown is authorized.

## Required aggregate metrics

- architecture and no-op parity checks;
- task counts, original pass/fail, trigger precision/recall;
- fragile steps and implicated layers per task;
- number of causal swaps and full continuations;
- route-family rescue and regression rates;
- unique versus shared recoveries by route family;
- oracle recoverable fraction;
- non-oracle policy success, rescue, regression, and compute cost;
- matched-random comparisons and paired bootstrap intervals;
- layer-level and expert-level aggregate effects with corrected intervals;
- length/difficulty confound controls;
- private counterfactual and recovery-trace counts.

## M32P deliverables

- route-override implementation with fake and real-smoke tests;
- `data/prompts/m32p_proxy_routing_manifest.json` in a separate preregistration
  commit before decision capture;
- `src/m32p_proxy_counterfactual_routing.py` and tests;
- `reports/telemetry/hf_m32p_proxy_routing_feasibility.json`;
- `reports/telemetry/hf_m32p_proxy_routing_evaluation.json`;
- `docs/M32P_PROXY_COUNTERFACTUAL_ROUTING_STUDY.md`;
- private gitignored route/counterfactual/recovery records;
- updated `STATE.md` and `reports/FINDINGS.md`;
- full suite and commit-safety checks green.

# Result-driven autoloop

The operator authorizes up to three milestone completions beginning with M32P,
subject to the normal four-hour and blocker limits.

## Branch 1 — H1 and H2 established

Proceed to M33P: freeze the successful non-oracle policy and compare a compact
router-bias table with a router-only trainable adapter on fresh data. Any
training must be router-only, explicitly approved by the existing protocol,
and evaluated on a sealed holdout. Then M34P may test partial-generation early
rerouting and a second deterministic task category.

## Branch 2 — H1 established, H2 not established

Proceed to M33P route selection: improve non-oracle selection using trajectory
summaries, CLUE-style centroids, and validation-frozen thresholds. Do not claim
oracle recoverability is deployable.

## Branch 3 — H1 not established

Stop the expert-routing track. Return to structured repair or telemetry-gated
tool routing. Do not spend another milestone tuning expert selection when equal-
compute alternatives do not provide a useful recovery ceiling.

## Branch 4 — hook/resource/protocol failure

Stop immediately with the exact blocker. Do not silently change model, task
set, top-k, compute budget, or causal unit.

# Required stop report

Print:

- latest commit SHA and milestones completed;
- hook/no-op parity verdict;
- model architecture and peak memory;
- H1/H2/H3 verdicts;
- oracle recoverable fraction;
- best non-oracle policy and matched-random delta;
- regressions and compute per rescue;
- tests passed and public artifacts;
- private artifacts intentionally not committed;
- exact next operator decision.