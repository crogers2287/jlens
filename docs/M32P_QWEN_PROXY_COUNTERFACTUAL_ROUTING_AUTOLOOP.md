# M32P Qwen proxy counterfactual-routing autoloop

Status: operator-authorized protocol, amended before preregistration or decision
capture. This supersedes the stopped Agents-A1 M32R execution path without
changing or deleting its Phase-0 feasibility record. All claims from this loop
must be scoped to the already-local `Qwen1.5-MoE-A2.7B-Chat` research proxy.

`steer.md` is the execution source of truth and `CODEX_AUTOSTEER.md` remains the
operating contract.

## Why the benchmark is being rewritten

The proxy is much smaller than Agents-A1. Reusing an Agents-A1-oriented task
frontier would risk producing mostly trivial passes or capacity-bound failures.
Neither is useful for causal routing research:

- trivial tasks provide no failures to recover;
- impossible tasks make every alternative route fail;
- a benchmark dominated by either case can make routing look better or worse
  for the wrong reason.

M32P therefore begins with a private, calibration-only capability-frontier
sweep. That sweep chooses a multiplication benchmark where the frozen proxy has
mixed pass/fail outcomes before any discovery, validation, or holdout task is
generated. Calibration rows are never decision data and cannot support a claim.

The causal question remains:

> When this frozen proxy fails near its own capability frontier, does an
> equal-compute alternative expert route inside the same model produce a better
> answer, and can a non-oracle policy choose that route without seeing the
> answer?

This loop does not establish anything about Agents-A1 expert routing. It builds
and validates the method for later transfer.

## Scope and invariants

- Model: already-local `Qwen1.5-MoE-A2.7B-Chat` only.
- Expected architecture: `qwen2_moe`, 24 routed layers, 60 experts per routed
  layer, top-4 active experts per token. Stop on mismatch.
- No model download, new model family, weight update, LoRA, or new dependency.
- Keep the M30 detector and p(fail) threshold frozen. Reproduce its published
  confusion matrix/hash before decision capture.
- Primary task family remains exact integer multiplication because the detector
  was validated there and `math_checker` provides deterministic labels.
- Fresh tasks only. M27, M29, M30, M31, abandoned M32, stopped M32R, and the
  capability-frontier sweep are excluded from decision data.
- Never reveal the correct answer to the route-selection policy.
- Preserve exactly top-4 active experts and equal expert compute in every
  counterfactual route. Renormalize selected routing weights.
- Disabled route override must reproduce the normal forward path within a
  preregistered numerical tolerance and identical greedy tokens on the smoke set.
- No global expert blacklist or permanent shutdown from observational counts.
- Private prompts, outputs, operands, token ids/text, raw router tensors,
  per-task routes, expert tables, labels, calibration rows, and counterfactual
  records stay gitignored.
- Public reports remain aggregate-only. Production remains gated.

# M32P — route-override feasibility and model-calibrated causal screen

## Phase 0A — safe route-override hook

Implement an opt-in proxy-only route controller around the supported sparse MoE
forward path. It accepts a per-forward override keyed by generated step and
routed layer and replaces selected expert ids/weights after router scoring but
before expert dispatch.

Required behaviors:

1. `override=None` follows the original model path.
2. A replacement keeps exactly four active experts.
3. No duplicate expert ids.
4. Weights finite, nonnegative, and renormalized.
5. Default path remains compatible with telemetry capture and KV cache.
6. Counterfactual continuations use the modified forward result and modified KV
   cache from the intervention point onward.
7. A one-layer/one-token override automatically removes itself afterward.

Tests before real capture:

- fake-MoE dispatch and weight-renormalization;
- no-op exact-path parity;
- selected-expert/rank-next replacement;
- duplicate/out-of-range/nonfinite rejection;
- KV-cache continuation;
- telemetry remains available under override;
- privacy/no-route-table public output.

Real smoke gate:

- load the local proxy inside existing hardware limits;
- verify architecture and top-k;
- normal and disabled-override decodes match on a tiny private smoke set;
- one forced equal-compute swap can alter forward telemetry/output;
- restore the normal model path after the smoke.

Stop on architecture, hook placement, no-op parity, cache, telemetry, or memory
failure.

## Phase 0B — calibration-only capability-frontier sweep

This phase occurs before preregistration. It is benchmark engineering, not a
result. Generate a deterministic private sweep, disjoint from every prior set,
covering candidate multiplication cells such as:

- 2-digit x 1-digit;
- 2-digit x 2-digit, split into low-carry and carry-heavy cells;
- 3-digit x 1-digit;
- 3-digit x 2-digit, low-carry and carry-heavy;
- 4-digit x 1-digit;
- 4-digit x 2-digit, low-carry and carry-heavy;
- 3-digit x 3-digit as a likely hard anchor;
- structured cases with zeros, repeated digits, or near-powers-of-ten.

Definitions for carry-heavy/low-carry and structured cells must be deterministic
and committed before the sweep runs. Use a fixed seed and a small equal sample
per cell. Report only aggregate cell counts and pass rates publicly.

The sweep may choose benchmark cells only from original greedy pass rate and
predeclared structural diversity. It must not select cells because the frozen
telemetry trigger, a route heuristic, or an expert happens to perform well.

Target benchmark composition:

- 70-80% boundary cells with calibration pass rates between 20% and 80%;
- 10-15% easy anchors with pass rate above 85%, to measure regressions/false
  alarms;
- 10-15% hard anchors with pass rate below 15%, to measure route-recovery
  ceiling without allowing them to dominate the verdict;
- at least three structurally distinct boundary cells;
- no single digit-length/carry cell above 35% of the decision benchmark.

The calibration phase must freeze, before decision task generation:

- selected cells and exact generator rules;
- task count chosen from 192, 240, or 288 based on a predeclared power table and
  expected number of original failures, never on route results;
- discovery/validation/holdout proportions of 1/2, 1/4, 1/4;
- minimum expected original failures: 40 discovery, 20 validation, 20 holdout;
- easy/hard anchor weights and all structural metadata fields.

If the sweep cannot identify a mixed capability frontier satisfying these
rules, stop and report `benchmark_frontier_not_found`. Do not silently broaden
the task family or use an all-fail benchmark.

## Preregistered decision design

After Phase 0B, commit `data/prompts/m32p_proxy_routing_manifest.json` before
creating any decision task. The manifest freezes:

- the selected model-calibrated benchmark cells and exact task count;
- deterministic rejection against all prior and calibration tuples;
- discovery/validation/sealed-holdout ids and generators;
- original greedy decode protocol;
- frozen M30 detector reconstruction and threshold;
- fragile-window and implicated-layer rules;
- candidate-route families and exact branch budgets;
- seeds, tie breaks, bootstrap seeds, multiplicity correction;
- H1/H2/H3 rules and minimum realized class counts;
- all tasks retained, including anchors, with no post-hoc cell/operator deletion.

If realized decision counts miss 30/15/15 original failures across discovery,
validation, and holdout, classify the causal test underpowered and report it.
Do not regenerate or reselect tasks after seeing decision outcomes.

## Fragile-window and layer targeting

Do not screen all 1,440 layer-expert modules globally. Use original-decode
telemetry only:

- choose up to the top two generated steps by the frozen window-risk score;
- at each step choose up to four routed layers using a frozen combination of
  router entropy, top-4/rank-5 margin, concentration, and trajectory deviation;
- no label, verifier result, or correct answer may influence targeting.

Report controls for digit lengths, carry count, output length, task cell, and
baseline difficulty so route effects are not confused with benchmark structure.

## Equal-compute route families

For each selected step/layer evaluate shared candidates:

1. `normal_route`;
2. `lowest_weight_to_rank5`;
3. `each_selected_to_rank5` — four one-at-a-time swaps;
4. bounded `selected_to_rank6` alternatives;
5. discovery-only `diversity_swap`;
6. fixed-seed `matched_random_swap` with equal branch count;
7. validation-frozen `soft_penalty_route`, applied only in fragile windows;
8. `oracle_best_tested`, verifier ceiling only and never deployable.

Normal, heuristic, random, and oracle arms receive the same full-continuation
budget. A one-step screen may rank branches only if its rule and continuation
count are frozen and identical across heuristic and random controls.

## Outcomes and primary hypotheses

`math_checker` defines pass/fail after full continuation. Undecided/capped rows
are handled only as frozen in the manifest.

### H1 — route recoverability exists

Among frozen-trigger true failures, tested equal-compute counterfactual routes
recover more errors than matched-random route search.

Classify `route_recoverability_established` only if the paired 95% bootstrap CI
for oracle-tested-family rescue-rate delta over matched-random is strictly above
zero on sealed holdout. Oracle results are capability evidence only.

### H2 — a deployable route policy works

A validation-frozen non-oracle route policy improves verified success over both
normal and matched-random routing on sealed holdout.

Classify `deployable_rerouting_established` only if both paired 95% success-rate
delta intervals are strictly above zero. The policy may use original telemetry,
router ranks/margins, task-cell metadata, and discovery/validation summaries,
but never labels, correct answers, or candidate verifier results.

### H3 — expert penalties generalize

Any layer-expert soft penalty must originate on discovery, repeat directionally
on validation, freeze before holdout, survive multiplicity correction, and avoid
a significant right-to-wrong increase. Otherwise it is exploratory. No hard
shutdown is authorized.

## Required aggregate metrics

- hook/no-op parity and architecture;
- calibration cell counts/pass rates and final benchmark composition;
- decision task counts and original pass/fail by split and cell;
- trigger precision/recall and false alarms;
- fragile steps/layers and branch counts;
- route-family rescue/regression rates and unique/shared recoveries;
- oracle recoverable fraction;
- non-oracle success, rescue, regression, and compute cost;
- matched-random paired intervals;
- layer/expert aggregate effects with corrected intervals;
- digit-length/carry/output-length/cell confound controls;
- private counterfactual and recovery-trace counts.

## M32P deliverables

- route-override implementation with fake and real-smoke tests;
- private calibration sweep plus aggregate-only frontier report;
- `data/prompts/m32p_proxy_routing_manifest.json` in a separate preregistration
  commit;
- `src/m32p_proxy_counterfactual_routing.py` and tests;
- `reports/telemetry/hf_m32p_proxy_benchmark_frontier.json`;
- `reports/telemetry/hf_m32p_proxy_routing_feasibility.json`;
- `reports/telemetry/hf_m32p_proxy_routing_evaluation.json`;
- `docs/M32P_PROXY_COUNTERFACTUAL_ROUTING_STUDY.md`;
- private gitignored calibration/route/counterfactual/recovery records;
- updated `STATE.md` and `reports/FINDINGS.md`;
- full suite and commit-safety checks green.

# Result-driven autoloop

The operator authorizes up to three milestone completions beginning with M32P,
subject to normal time and blocker limits.

- H1 and H2 established: M33P freezes the successful non-oracle policy and
  compares a compact router-bias table with a router-only adapter on fresh,
  model-calibrated data; M34P may test partial-generation rerouting and a second
  deterministic category.
- H1 established, H2 not: M33P studies non-oracle route selection using
  trajectory summaries and validation-frozen thresholds.
- H1 not established: stop expert routing and return to structured repair or
  telemetry-gated tools.
- hook/resource/benchmark-frontier/protocol failure: stop with the exact blocker.

# Required stop report

Print:

- latest commit and milestones completed;
- hook/no-op parity, architecture, peak memory;
- calibration frontier and chosen benchmark composition;
- realized split class counts;
- H1/H2/H3 verdicts;
- oracle recoverable fraction;
- best non-oracle policy and matched-random delta;
- regressions and compute per rescue;
- tests/public artifacts/private artifacts withheld;
- exact next operator decision.
