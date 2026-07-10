# M32R Agents-A1 counterfactual expert-routing autoloop

Status: operator-authorized replacement direction. This document defines a
bounded three-milestone telemetry loop centered on causal MoE routing tests.
`steer.md` is the execution source of truth and `CODEX_AUTOSTEER.md` remains
the operating contract.

## Supersession and research hygiene

The earlier M32 structured-repair protocol and its committed
`data/prompts/m32_repair_manifest.json` were preregistered but **never executed**.
They are preserved as historical artifacts and are superseded before any M32
generation, capture, or result inspection. Do not delete, edit, or report them
as completed evidence.

The new current milestone is **M32R**. It asks whether some verified failures
are caused by token/layer-level expert misrouting inside the frozen Agents-A1
MoE, and whether telemetry can trigger a better equal-compute route.

## Model and 48 GiB resource decision

Keep Agents-A1 as the research base. Approved official model identities:

1. `InternScience/Agents-A1`
   - official BF16 Hugging Face safetensors checkpoint;
   - use the existing `qwen3_5_moe` capture path;
   - preferred dual-RTX-3090 research load is runtime NF4 through bitsandbytes,
     `router_only`, short text-only contexts, and no hidden-state persistence.
2. `InternScience/Agents-A1-FP8`
   - official compressed-tensors FP8 safetensors checkpoint;
   - permitted only as a preflight candidate because RTX 3090/Ampere has no
     native FP8 tensor-core path;
   - use it only if the installed loader supports it without silently
     dequantizing beyond the memory ceiling and all routing hooks remain
     available.

Hard resource gate:

- total GPU pool: 2 x 24 GiB RTX 3090;
- peak combined allocated/reserved GPU memory must stay at or below 44 GiB,
  leaving at least 4 GiB aggregate headroom for decode activations, KV state,
  and intervention branches;
- no CPU/disk offload during causal timing measurements unless explicitly
  reported as a separate feasibility run;
- no model weights, caches, or local paths may be committed;
- if neither approved load path satisfies memory and routing-hook checks, stop
  before task capture and report the blocker.

The GGUF/Q8 Agents-A1 runtime remains the practical serving baseline, but GGUF
cannot be used for this experiment because it does not expose controllable
per-layer expert routes.

## What “an expert wobbles” means here

Do not treat router entropy as an intrinsic error score for one expert. Router
entropy describes uncertainty over a route. An expert can be helpful for one
token and harmful for another, and expert indices are layer-local: expert 17
in layer 4 is not the same module as expert 17 in layer 29.

Agents-A1 declares 40 text layers, 256 routed experts per MoE layer, and top-8
experts per token. The causal unit is therefore a **layer-expert-token** choice,
not a global expert id.

A layer-expert pair may be called harmful only after a counterfactual test shows
that suppressing or replacing it improves verified outcomes on fresh held-out
examples. Observational correlation alone may never create a blacklist.

## Global invariants for M32R-M34R

- Use only fresh decision tasks; M27/M29/M30/M31 data are spent.
- Preregister every split, route override, branch budget, seed, metric, and
  claim rule before real capture.
- Keep model weights frozen through M32R and M33R.
- Preserve top-8 active-expert compute for every equal-compute route.
- Renormalize route weights after any replacement.
- Never use the verifier or true answer to choose a deployable route; verifier
  access is allowed only for retrospective labels and explicitly named oracle
  ceilings.
- Keep prompts, outputs, operands, token ids/text, raw router tensors,
  per-task routes, and expert-level detailed records private and gitignored.
- Public artifacts remain aggregate-only.
- No production expert shutdown, permanent blacklist, or threshold unlock.
- No arbitrary model-output execution, live web retrieval, or new model family.

# M32R — counterfactual expert-routing feasibility and causal screen

## Primary questions

1. On telemetry-triggered verified failures, does a better equal-compute expert
   route already exist inside the frozen Agents-A1 model?
2. Can a non-oracle route rule choose better alternatives without seeing the
   answer or verifier label?
3. Are any harmful layer-expert effects stable enough across fresh splits to
   justify a dynamic soft penalty rather than a permanent shutdown?

## Phase 0 — loader and route-override feasibility

Before generating decision data:

1. Load one approved Agents-A1 safetensors path under the 44 GiB gate.
2. Verify `qwen3_5_moe`, 40 text layers, 256 experts, and top-8 routing.
3. Verify real `output_router_logits` on prefill and decode.
4. Add an opt-in route-override hook that can, for a specified decode token and
   layer:
   - mask one selected expert;
   - insert a specified unselected expert;
   - preserve exactly eight active routed experts;
   - renormalize weights;
   - leave the normal path bit-for-bit unchanged when disabled.
5. Support prefix/KV branching so counterfactual continuations begin at the
   intervention token rather than recomputing the entire prefix where the
   architecture permits it.
6. Add deterministic fake-MoE tests before any real model capture.

Stop if the hook changes baseline outputs while disabled, changes active expert
count, cannot reproduce an identical no-op route, or violates the memory gate.

## Preregistered decision data

Create `data/prompts/m32r_expert_routing_manifest.json` in a dedicated
preregistration commit before capture:

- 192 fresh multiplication tasks across the existing six bands, 32 per band;
- deterministic rejection of all M29/M30/M31 tuples and any abandoned M32
  manifest tuples;
- sealed split: 96 discovery, 48 validation, 48 holdout, balanced by band;
- all tasks retained and constant `checker_needed` applicability;
- standard greedy original decode and frozen M30-style telemetry descriptor;
- a trigger threshold fixed before M32R capture;
- exact fragile-window selection, implicated-layer selection, route candidates,
  branch counts, seeds, bootstrap seeds, and claim rules.

If the frozen M30 detector cannot be reproduced on the Agents-A1 safetensors
research load because the previous detector used a different checkpoint or
precision, do not pretend it transfers. Preregister a short calibration split
and a fresh sealed M32R trigger holdout, label the detector as Agents-A1-specific,
and keep the old M30 claim scoped to its original model.

## Fast causal screen

The broad “test each expert” idea is implemented hierarchically so it remains
computationally bounded.

For every telemetry-triggered original failure:

1. Rank decode steps by the frozen trajectory-risk contribution and keep the
   predeclared top fragile steps.
2. Rank layers at those steps using router entropy, concentration, route
   instability, and expert-usage deltas; keep the predeclared top layers.
3. At each selected layer/step, perform leave-one-selected-expert-out swaps:
   mask each of the eight selected experts one at a time and insert the next
   highest-ranked unselected expert, preserving top-8 compute.
4. Use cheap one-step counterfactual statistics to rank those swaps, then run
   full branched continuations only for the predeclared top route variants.
5. Deterministically verify final answers after the branch completes.

This produces two distinct outputs:

- an **oracle route ceiling**: whether any tested equal-compute route repairs
  the failure;
- a **deployable non-oracle score**: whether telemetry/router-only information
  can select a useful route without consulting labels.

## Counterfactual route families

Freeze these before decision capture:

1. `normal_route` — untouched top-8 router route.
2. `selected_expert_swap_next` — replace one selected expert with rank-9.
3. `lowest_weight_swap` — replace the lowest-weight selected expert with the
   highest-ranked unselected expert.
4. `diversity_boost_swap` — replace one selected expert to reduce route
   concentration under a fixed deterministic rule.
5. `history_soft_penalty` — discovery-fit, validation-selected layer-expert bias
   table; holdout only after freezing.
6. `matched_random_swap` — equal branch count and active-expert budget.
7. `oracle_best_tested_route` — retrospective ceiling only, never a deployable
   result.

Do not globally turn off an expert in M32R. Any suppression is local to one
layer/token branch.

## Per-layer expert evidence table

Private records may track, for each layer-expert pair:

- activation count on pass/fail originals;
- conditional failure association;
- counterfactual suppressions attempted;
- wrong-to-right rescues;
- right-to-wrong regressions;
- no-change count;
- average telemetry-risk delta;
- discovery, validation, and holdout provenance.

Public reports may expose only aggregate distributions and minimum-support
counts. Use shrinkage/minimum-support rules fixed in the manifest. Never rank
an expert as harmful from raw failure correlation alone.

## M32R primary hypotheses

### H1 — route-recoverable failures exist

Among correctly triggered verified failures, the oracle best tested
counterfactual route has a higher rescue rate than the matched-random route
budget.

Classify `route_recoverable_established` only if the paired 95% bootstrap CI for
rescue-rate delta is strictly above zero.

### H2 — non-oracle rerouting is useful

A frozen non-oracle reroute policy improves final verified success over both
`normal_route` and `matched_random_swap` on the sealed holdout, with no verifier
consultation during route choice.

Classify `routing_policy_useful` only if both paired success-rate delta 95% CIs
are strictly above zero. Classify harmful if the CI versus normal is strictly
below zero; otherwise not established.

### H3 — a suppressible layer-expert effect generalizes

A layer-expert pair may be labeled `candidate_soft_penalty` only if:

- discovery minimum support is met;
- the causal rescue-minus-regression effect remains positive on validation;
- the exact frozen penalty improves or does not harm the sealed holdout under a
  predeclared multiplicity correction;
- the finding is layer-specific and context-gated.

No hard shutdown is authorized.

## Required M32R metrics

Report aggregate-only:

- model load path, quantization mode, peak GPU memory, and hook status;
- original pass/fail counts and trigger precision/recall;
- fragile steps/layers examined and total route branches;
- oracle route-recoverable failure fraction;
- rescue and regression rates by route family;
- paired confidence intervals for H1/H2;
- route-selection accuracy for non-oracle heuristics;
- number of layer-expert pairs meeting discovery/validation/holdout gates;
- compute, tokens, and wall time per verified rescue;
- private verified counterfactual recovery-trace count.

## M32R deliverables

- `data/prompts/m32r_expert_routing_manifest.json` preregistration commit;
- opt-in route override in the HF capture path, normal path unchanged;
- `src/m32r_counterfactual_routing.py`;
- deterministic fake-MoE and privacy tests;
- `reports/telemetry/hf_m32r_routing_run_summary.json`;
- `reports/telemetry/hf_m32r_routing_evaluation.json`;
- `docs/M32R_COUNTERFACTUAL_ROUTING_STUDY.md`;
- private counterfactual routes/traces, gitignored;
- updated `STATE.md` and `reports/FINDINGS.md`;
- full suite and commit-safety checks green.

# Autoloop continuation

The operator authorizes up to three milestones beginning with M32R, subject to
the normal four-hour and blocker limits.

## Branch 1 — H1 and H2 established

Proceed to M33R: frozen lightweight router correction.

- Fit only a small router-bias table or router-only adapter from discovery data.
- Freeze on validation and evaluate once on entirely fresh sealed tasks.
- Compare with normal routing, matched random swaps, and the M32R heuristic.
- Keep all experts and base-model weights frozen.

Then, if M33R succeeds and loop budget remains, proceed to M34R:
partial-trajectory online gating and second-category transfer.

## Branch 2 — H1 established, H2 not established

Proceed to M33R candidate-selection research:

- improve route scoring from trajectory summaries;
- test learned route utility without changing experts;
- do not scale brute-force oracle search as if it were a deployable policy.

## Branch 3 — H1 not established

Stop the expert-routing autoloop. Return to structured repair/tool routing. Do
not train a router or blacklist experts.

## Branch 4 — resource or hook failure

Stop immediately and report the exact loader, memory, architecture, or hook
blocker. Do not switch models silently.

# Required stop report

At each stop print:

- latest commit SHA and milestone count;
- exact Agents-A1 safetensors load path and quantization;
- peak GPU memory;
- H1/H2/H3 verdicts;
- oracle recoverable fraction and non-oracle policy delta;
- candidate layer-expert penalty count;
- tests passed;
- public artifacts created;
- private artifacts intentionally not committed;
- exact next operator decision.
