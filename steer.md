# steer.md — M33 telemetry-gated tool routing

M1 through M32 are complete. M32 closed the model-side repair question: the
structured operator bundle rescued .0056 vs resample .0333 on correctly
triggered failures (H1 CI [-.0556, 0]) and the telemetry-gated bundle was not
established over no-repair or a count-matched random trigger (H2 CI
[0, .0078]). Three operator families are now negative (M31 resampling, M32P
expert rerouting, M32 structured prompting). The frozen M30 trigger reproduced
in-band at precision .900 / recall .887, and the deterministic tool ceiling was
.940 verified success vs .471 no-repair.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Operator decision

Per the preregistered Branch 3 of `docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`
("model-side repair not improved, tool upper bound large"), the autoloop
continues with **M33: tool-grounded repair adapter**. The bounded autoloop
budget authorized at M32 reactivation covers up to two further milestone
completions: M33 (this steer) and M34 (second-category detector transfer,
steered separately after M33 closes).

M33 is product/runtime evidence about routing, never a model self-correction
claim. Do not generate a model-training dataset from tool outputs; no
distillation rules are defined in this loop.

## M33 protocol

Predeclare `data/prompts/m33_tool_routing_manifest.json` BEFORE any task
generation or capture, in its own commit, then execute it exactly as written.

- Fresh decision set: 384 integer multiplication tasks, the M32 six-band
  structure (64 per band), operands drawn from a new seed and disjoint from
  everything the committed M29, M30, M31, and M32 manifests generate. The M32
  decision set must NOT be reused for M33 primary claims — its tool upper
  bound has already been published.
- One GPU capture phase only: greedy originals (64-token cap), same capture
  and validity rules as M32. No repair prompts, no resampling.
- Gate: the frozen M30 full-telemetry classifier at threshold 0.5, refit
  deterministically from private M30 records with the published confusion
  matrix reproduced exactly. Immutable; no M33 labels may influence triggering.
- Tool: the in-repo deterministic integer evaluator applied to the task's own
  predeclared expression; its output passes through the same verifier as model
  output. Tool invocations cost zero decode tokens; count invocations as the
  compute unit and record per-policy decode plus invocation totals.
- Policies (verifier-first; a passing original is never replaced):
  `no_repair`, `tool_on_every_task`, `random_trigger_tool` (count-matched to
  the telemetry trigger, seeded), `telemetry_trigger_tool`.
- H1 routing usefulness: `telemetry_trigger_tool` beats BOTH `no_repair` AND
  `random_trigger_tool` on verified success, each paired bootstrap 95% CI
  strictly above zero (2000 iterations, seeds predeclared in the manifest).
- H2 routing efficiency: `telemetry_trigger_tool` retains at least 80% of the
  `tool_on_every_task` uplift over `no_repair` while invoking the tool on at
  most 60% of tasks. Both conditions must hold on point estimates, with the
  uplift-retention bootstrap 95% interval reported alongside.
- Detector reproduction gate: if in-band trigger precision falls below .80 or
  recall below .75 on the fresh set, stop and report before any H1/H2 claim.
- Report per-band trigger and routing metrics descriptively (aggregate-only),
  as in M32; secondary and non-confirmatory.

## Stop conditions

Stop immediately and report the exact blocker on: detector reproduction
failure per the gate above, any policy arm replacing a passing original,
privacy/commit-safety failure, test failure, tuple exhaustion during
generation, or capture invalidity that cannot be resumed idempotently.

## Required reporting

At the M33 stop, report: commit SHAs (manifest, implementation, result, steer);
fresh-set trigger precision/recall; verified success per policy; H1 CIs; H2
uplift retention and invocation fraction; compute saved versus
tool-on-every-task (invocations and decode tokens); per-band descriptives;
tests and commit-safety results; and the M34 decision.

## Repository hygiene

Unchanged from M32: no model weights, caches, local model paths, prompts,
outputs, operands, per-task predictions/labels/triggers, token ids/text, or
raw router tensors in public artifacts. Aggregate-only public reports;
`src/check_commit_safe.py` must pass on anything staged under `reports/`.
Candidate-only; production remains gated; no weight training.
