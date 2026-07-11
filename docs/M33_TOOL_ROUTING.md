# M33 — Telemetry-gated tool routing (RESULT: useful and efficient)

M33 asked whether routing telemetry-triggered checkable tasks to a
deterministic tool beats no-repair and count-matched random routing, and
whether the telemetry gate retains the full-tool uplift at materially fewer
invocations. This is product/runtime routing evidence, not a model
self-correction claim. Preregistration: manifest commit `5bfaf46`
(before any generation or capture); implementation `a4c2440`; steer `c10190e`.

## Design (frozen before capture)

- 384 fresh integer multiplication tasks, the M32 six-band structure, seed
  `m33-tool-routing-v1`, operands disjoint from everything M29-M32 generate
  (disjointness regression-tested against regenerated M32 tuples).
- One GPU phase: greedy 64-token originals. No repair prompts, no resampling.
- Gate: frozen M30 full-telemetry classifier at threshold 0.5, deterministic
  refit; preregistered reproduction gate precision >= .80 and recall >= .75
  on the fresh set, else stop with no H1/H2 claim.
- Tool: in-repo deterministic integer evaluator on the task's own predeclared
  expression (never model output), output passed through the same verifier;
  zero decode tokens, invocations counted as the compute unit.
- Policies, all verifier-first (a passing original is never replaced;
  asserted in code): no_repair, tool_on_every_task, random_trigger_tool
  (count-matched, seeded), telemetry_trigger_tool.
- H1 useful iff telemetry routing beats BOTH no_repair AND random routing
  (paired bootstrap 95% CIs strictly > 0). H2 efficient iff uplift retention
  >= .80 at invocation fraction <= .60.

## Results (`reports/telemetry/hf_m33_routing_evaluation.json`)

- Originals: 167 pass / 217 fail. **Reproduction gate PASSED** on the fresh
  set: precision .902, recall .889 (214 triggers, rate .557) — essentially
  identical to M32 in-band (.900/.887).
- Verified success: no_repair .435, random_trigger_tool .714,
  **telemetry_trigger_tool .938**, tool_on_every_task 1.000.
- **H1 = useful**: vs no_repair +.503 (CI [.453, .555]); vs random trigger
  +.224 (CI [.177, .271]). Both strictly positive.
- **H2 = efficient**: uplift retention .889 (CI [.846, .929]) at invocation
  fraction .557 — 170 of 384 tool invocations saved vs tool-on-every-task,
  at zero decode tokens either way. 21 false-alarm checks.
- Zero errors introduced in any arm (verifier-first held).
- Per-band (secondary, non-confirmatory): same shape as M32 — the trigger is
  weakest on the easy/mid frontier (band_2 precision .54) and near-ceiling on
  hard bands; rescues concentrate where failures concentrate.

## Interpretation

The M30 telemetry detector's value is now positively established in its
correct role: as a routing gate in front of deterministic tools. It reproduced
across two fresh decision sets (M32, M33) at ~.90 precision, and gating tool
calls on it retains ~89% of the full-tool uplift while skipping ~44% of
invocations. Combined with M31/M32/M32P this completes the arc: the telemetry
signal is real and useful for routing; model-side self-correction is not the
mechanism through which to spend it.

## Gating

Product/runtime evidence only. No training dataset from tool outputs; no
distillation defined. Aggregate-only public artifacts (check_commit_safe
passed); operands/prompts/outputs/per-task predictions private and gitignored.
Candidate-only; production remains gated.

## Next (per Branch 3)

M34 becomes a second-category transfer test of the frozen detector — steered
separately.
