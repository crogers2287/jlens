# steer.md — M32P Qwen proxy counterfactual routing

M1 through M31 are complete. M32 structured repair was superseded before
execution and remains a never-executed historical artifact. M32R Agents-A1
counterfactual routing stopped at Phase 0 before preregistration or capture
because official Agents-A1 safetensors cannot fit the current 44 GiB research
ceiling with the installed loader stack.

`CODEX_AUTOSTEER.md` remains the operating contract.

The current protocol is:

`docs/M32P_QWEN_PROXY_COUNTERFACTUAL_ROUTING_AUTOLOOP.md`

Read it in full before implementation.

## Operator decision

The operator selects former option C: use the already-local
`Qwen1.5-MoE-A2.7B-Chat` as an explicit research proxy to answer the causal
expert-routing question now.

All claims must be scoped to the proxy. Do not imply that an effect transfers
to Agents-A1. The goal is to build and validate the complete route-override,
counterfactual-screen, and non-oracle selection methodology so it can later be
reused unchanged on Agents-A1 when a viable checkpoint or hardware path exists.

The operator authorizes a bounded autoloop of up to three milestone completions
beginning with M32P, subject to the normal four-hour and blocker limits. Use
separate implementation, preregistration, result, and steer commits where the
protocol requires them.

## Why this is the selected path

- M30 established that full internal telemetry predicts objective arithmetic
  failure better than task-difficulty metadata.
- M31 reproduced about 89% precision for the frozen trigger, but a generic
  temperature resample repaired only about 4.5% of correctly triggered errors.
- Agents-A1 route intervention is blocked by checkpoint memory geometry, not by
  a failed routing hypothesis.
- The local Qwen proxy is the same model family used for the existing telemetry
  evidence, fits the current hardware, and exposes controllable router logits.
- This is the fastest path to learning whether wrong answers are sometimes
  caused by poor layer-expert-token choices rather than missing model capacity.

## Current milestone — M32P

Execute the M32P phase of the proxy-routing protocol.

### Phase 0: route-override hook and smoke gate

1. Verify the loaded proxy architecture from config:
   - `qwen2_moe`;
   - 24 routed layers;
   - 60 experts per routed layer;
   - top-4 active experts per token.
2. Implement an opt-in route override after router scoring and before expert
   dispatch.
3. Preserve exactly four active experts and renormalize routing weights.
4. Ensure `override=None` follows the original path and reproduces greedy smoke
   outputs within the preregistered numerical tolerance.
5. Ensure a changed route produces a genuinely changed forward result and that
   continuation uses the modified KV cache rather than splicing into the
   original trajectory.
6. Add fake-MoE, no-op parity, invalid-route, cache, telemetry, and privacy
   tests before decision capture.
7. Stop rather than improvising if hook placement, no-op parity, cache
   correctness, architecture, telemetry, or memory cannot be verified.

### Preregister before causal decision capture

Commit `data/prompts/m32p_proxy_routing_manifest.json` before generating or
capturing decision data. It must freeze:

- 192 fresh multiplication tasks over the existing six bands;
- deterministic disjointness from M29, M30, M31, and abandoned M32;
- 96 discovery / 48 validation / 48 sealed holdout;
- the frozen M30 trigger and reconstruction check;
- fragile-step and implicated-layer selection rules;
- equal-compute route families and branch budgets;
- random seeds, tie breaks, bootstrap seeds, and multiplicity correction;
- H1/H2/H3 claim rules;
- no post-hoc task, layer, expert, feature, or operator selection.

### Causal screen

At telemetry-fragile steps and implicated layers only, compare:

- normal routing;
- lowest-weight selected expert replaced by rank-5;
- each selected top-4 expert replaced one at a time by rank-5;
- bounded rank-6 alternatives;
- discovery-only diversity swap;
- matched-random equal-compute swaps;
- validation-frozen soft layer-expert penalties;
- oracle best tested branch as a ceiling only.

Do not globally test or disable every expert. The causal unit is a
layer-expert-token choice. An expert can help one token and hurt another. No
hard expert shutdown or global blacklist is authorized.

### Primary verdicts

H1 — route recoverability:

A tested equal-compute route family must recover more frozen-trigger failures
than matched-random route search with a paired 95% bootstrap interval strictly
above zero on the sealed holdout.

H2 — deployable rerouting:

A validation-frozen non-oracle policy using only telemetry/router information
must beat both normal routing and matched-random routing on sealed holdout, with
both paired success-rate intervals strictly above zero.

H3 — generalized soft penalties:

Any proposed layer-expert penalty must originate on discovery, repeat on
validation, be frozen before holdout, survive the preregistered multiplicity
correction, and avoid a significant increase in right-to-wrong regressions.
Otherwise it remains exploratory.

## Result-driven continuation

Follow only the branches in the M32P protocol:

- H1 + H2 established: M33P frozen router-bias/router-only-adapter comparison,
  then eligible M34P partial-generation rerouting and transfer testing.
- H1 established but H2 not established: M33P route-selection research using
  trajectory summaries and validation-frozen non-oracle policies.
- H1 not established: stop expert-routing work and return to structured repair
  or telemetry-gated tools.
- hook/resource/protocol failure: stop immediately with the exact blocker.

## Standing evidence and boundaries

- M30 detector increment remains established only for the proxy model,
  controlled arithmetic category, and fixed decode protocol.
- M31 trigger precision remains candidate-only and production-gated.
- The Agents-A1 Phase-0 feasibility result remains valid and must not be
  overwritten or reframed as a causal-routing result.
- No proxy result may be reported as an Agents-A1 result.
- No production policy, weight training, global expert shutdown, or model
  substitution is authorized in M32P.

## Repository hygiene

Do not commit model weights, caches, local model paths, prompts, outputs,
operands, diagnoses, per-task routes, layer/expert identities tied to private
tasks, token ids/text, raw router tensors, predictions, labels, or detailed
counterfactual records. Public artifacts remain aggregate-only. No candidate
becomes gold and production remains gated until explicit audited unlock
criteria are defined.