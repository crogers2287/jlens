# steer.md — M32P model-calibrated Qwen proxy routing

M1 through M31 are complete. M32 structured repair was superseded before
execution and remains a never-executed historical artifact. M32R Agents-A1
counterfactual routing stopped at Phase 0 before preregistration or capture
because official Agents-A1 safetensors cannot fit the current 44 GiB research
ceiling with the installed loader stack.

`CODEX_AUTOSTEER.md` remains the operating contract.

The current amended protocol is:

`docs/M32P_QWEN_PROXY_COUNTERFACTUAL_ROUTING_AUTOLOOP.md`

Read it in full before implementation. This amendment was made before M32P
preregistration or decision capture.

## Operator decision

Use the already-local `Qwen1.5-MoE-A2.7B-Chat` as an explicit research proxy to
answer the causal expert-routing question. All claims remain proxy-scoped and
must not be presented as Agents-A1 results.

Because the proxy is much smaller than Agents-A1, do not reuse an
Agents-A1-oriented benchmark frontier. M32P must first calibrate the proxy's own
capability boundary and then preregister fresh decision tasks around that
boundary.

The operator authorizes a bounded autoloop of up to three milestone completions
beginning with M32P, subject to normal time and blocker limits. Use separate
hook, benchmark-calibration, preregistration, result, and steer commits where the
protocol requires them.

## Why the benchmark must change

A useful routing benchmark needs recoverable mistakes:

- tasks that are too easy provide no failures;
- tasks that are too hard test missing capacity rather than routing;
- an all-fail or all-pass benchmark cannot show whether alternate experts help.

The benchmark must therefore concentrate on the proxy's mixed pass/fail
frontier while retaining small easy and hard anchor sets to measure regressions
and the maximum possible recovery ceiling.

## Standing evidence

- M30 established that full telemetry predicts this proxy's multiplication
  failures better than task-difficulty metadata: +.099 accuracy with 95% CI
  [+.042,+.156] on a fresh n=192 holdout.
- M31 reproduced about 89% precision for the frozen trigger, but a generic
  temperature resample repaired only about 4.5% of correctly triggered errors.
- Agents-A1 route intervention is blocked by checkpoint memory geometry, not by
  a negative routing result.
- The proxy fits current hardware and exposes router logits and expert dispatch.

## Current milestone — M32P

### Phase 0A: route-override hook and smoke gate

1. Verify `qwen2_moe`, 24 routed layers, 60 experts per layer, top-4.
2. Implement an opt-in route override after router scoring and before dispatch.
3. Preserve exactly four experts and renormalized finite weights.
4. `override=None` must reproduce the normal greedy path.
5. Counterfactual continuations must use the modified forward result and cache.
6. Add fake-MoE, parity, invalid-route, cache, telemetry, and privacy tests.
7. Stop on hook, architecture, parity, cache, telemetry, or memory failure.

### Phase 0B: rewrite the benchmark around the proxy

Before preregistration, run a private deterministic capability-frontier sweep
across multiplication cells including:

- 2-digit x 1-digit;
- 2-digit x 2-digit low-carry and carry-heavy;
- 3-digit x 1-digit;
- 3-digit x 2-digit low-carry and carry-heavy;
- 4-digit x 1-digit;
- 4-digit x 2-digit low-carry and carry-heavy;
- 3-digit x 3-digit hard anchor;
- structured zero/repeated-digit/near-power-of-ten cases.

Freeze cell definitions and sweep seeds before running it. Calibration rows are
private, disjoint, never decision data, and support no routing claim.

Choose the final benchmark from original greedy pass rates and structural
diversity only—not from trigger quality, route performance, expert identities,
or verifier-selected counterfactuals.

Target composition:

- 70-80% boundary cells with 20-80% calibration pass rates;
- 10-15% easy anchors above 85% pass;
- 10-15% hard anchors below 15% pass;
- at least three distinct boundary cells;
- no one digit/carry cell above 35% of tasks.

Choose 192, 240, or 288 total decision tasks using the protocol's predeclared
power table, with 1/2 discovery, 1/4 validation, 1/4 sealed holdout. Freeze the
choice before generating decision rows. Stop with
`benchmark_frontier_not_found` if no mixed frontier exists.

### Preregister before causal capture

Commit `data/prompts/m32p_proxy_routing_manifest.json` freezing:

- selected model-calibrated cells and exact task count;
- disjoint task generators and split ids;
- the frozen M30 trigger and reconstruction check;
- fragile-step and implicated-layer rules;
- equal-compute route families and branch budgets;
- seeds, tie breaks, bootstrap seeds, and multiplicity correction;
- minimum realized original failures and H1/H2/H3 rules;
- no post-hoc task, cell, layer, expert, feature, or operator selection.

Do not regenerate if realized class counts miss the frozen minimums; report the
causal study as underpowered.

### Causal screen

At telemetry-fragile steps and implicated layers only, compare:

- normal routing;
- lowest-weight selected expert replaced by rank-5;
- each selected top-4 expert replaced one at a time by rank-5;
- bounded rank-6 alternatives;
- discovery-only diversity swaps;
- matched-random equal-compute swaps;
- validation-frozen soft layer-expert penalties;
- oracle best tested route as a ceiling only.

Do not globally test or disable every expert. The causal unit is a
layer-expert-token choice. No hard blacklist or permanent shutdown is
authorized.

## Primary verdicts

H1 — route recoverability:

A tested equal-compute route family must recover more frozen-trigger failures
than matched-random route search with a paired 95% bootstrap interval strictly
above zero on sealed holdout.

H2 — deployable rerouting:

A validation-frozen non-oracle policy using only telemetry/router/task-cell
information must beat both normal and matched-random routing on sealed holdout,
with both paired success-rate intervals strictly above zero.

H3 — generalized soft penalties:

Any layer-expert penalty must originate on discovery, repeat on validation,
freeze before holdout, survive multiplicity correction, and avoid a significant
increase in right-to-wrong regressions. Otherwise it remains exploratory.

## Result-driven continuation

- H1 + H2 established: M33P router-bias/router-only-adapter comparison on fresh,
  model-calibrated data; then eligible M34P early rerouting and transfer.
- H1 established but H2 not: M33P non-oracle route-selection research.
- H1 not established: stop expert routing and return to structured repair or
  telemetry-gated tools.
- hook/resource/benchmark-frontier/protocol failure: stop with the exact blocker.

## Boundaries and hygiene

Do not commit model weights, caches, local model paths, prompts, outputs,
operands, calibration rows, per-task routes, layer/expert identities tied to
private tasks, token ids/text, raw router tensors, predictions, labels, or
detailed counterfactual records. Public artifacts remain aggregate-only. No
candidate becomes gold, no proxy result becomes an Agents-A1 claim, and
production remains gated.
