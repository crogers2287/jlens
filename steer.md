# steer.md — post-M34 decision gate

M1 through M34 are complete. The bounded M32–M34 autoloop is finished and
must not continue automatically. Do not redo the M32 structured-repair study,
the M33 telemetry-gated tool-routing study, or the M34 second-category transfer
test. Their decision sets are spent.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Autoloop status

The operator-authorized three-milestone loop completed:

1. M32 — structured model-side repair
2. M33 — telemetry-gated deterministic tool routing
3. M34 — second-category detector transfer

The loop budget is exhausted. Stop until the operator selects a new direction.

## Current evidence

### M32 — structured model-side repair: negative

- 384 preregistered fresh multiplication tasks with the frozen M30 trigger.
- Structured prompting operators rescued fewer triggered failures than the
  M31 resample baseline: .0056 versus .0333; H1 CI [-.0556, 0].
- The telemetry-gated structured bundle did not establish an improvement over
  no repair or matched-random triggering; H2 CI [0, .0078].
- The frozen trigger reproduced in-distribution at precision .900 and recall
  .887.
- The deterministic tool ceiling reached .940 verified success versus .471 for
  the original model answers.

Conclusion: deliberate re-solve, checker-guided prompting, and
 diagnose-then-repair did not fix the proxy model's systematic arithmetic
failures. Model-side self-repair is not supported by this evidence.

### M33 — telemetry-gated tool routing: positive in mixed competence

- Fresh disjoint multiplication set with a mixed model-competence regime.
- Frozen trigger reproduced at precision .902 and recall .889.
- Verified success:
  - no repair: .435
  - matched-random tool routing: .714
  - telemetry-triggered tool routing: .938
  - tool on every task: 1.000
- Telemetry routing beat both no repair and matched-random routing with paired
  confidence intervals strictly above zero.
- It retained .889 of the full-tool uplift [CI .846, .929] while invoking the
  tool on .557 of tasks.
- Verifier-first semantics introduced zero new errors.

Conclusion: when the model has mixed competence, telemetry can allocate a
trusted deterministic tool substantially better than random while saving
roughly 44% of tool calls versus tool-on-every-task.

### M34 — frozen detector transfer: failed

- Fresh 384-task category shift from `a*b` to `a*b+c`.
- The proxy model collapsed: 18 pass / 366 fail (95.3% failure).
- Frozen trigger precision .966 was trivial at that failure base rate; recall
  fell to .612 and missed 39% of failures.
- Telemetry-triggered tool routing .630 versus matched-random .617; paired CI
  [-.060, .083]. H1 not established.
- Uplift retention .612 at invocation fraction .604; H2 not established.
- Zero errors introduced.

Conclusion: the M30 detector is real but distribution-bound. Selective gating
has value only where the model has a meaningful mixture of successes and
failures. When nearly everything fails, the correct policy is tool-on-every-
task rather than attempting to predict individual failures.

## Closed research branches

- Naive resampling: ineffective (M31, about 4.5% rescue).
- Structured model-side prompting repair: ineffective (M32).
- Counterfactual expert rerouting on the Qwen proxy: no advantage over matched
  random perturbation (M32P); expert-routing track closed for this model.
- Agents-A1 expert-routing execution remains blocked by checkpoint memory
  geometry on the dual-3090 research hardware. The Phase-0 feasibility record
  remains valid and must not be reframed as a causal result.

## Research position

The strongest supported jLens architecture is now hierarchical:

1. **Category/regime competence gate** — decide whether the model is operating
   in a high-competence, mixed-competence, or near-total-failure regime.
2. **Telemetry risk gate** — inside a mixed-competence regime, identify which
   individual answers should be checked or routed to a tool.
3. **Verifier-first action** — never replace an already verified-correct answer
   with a failing repair.
4. **Direct tool policy** — bypass selective gating when category-level evidence
   shows the model fails almost universally.

Telemetry should not be treated as a universal, model-independent threshold.
Feature capture and control infrastructure may generalize, but calibration,
thresholds, and competence priors must be validated per model, task family,
and decode protocol.

## Required operator decision before M35

Choose exactly one direction:

### A. Hierarchical competence router (recommended)

Build and preregister a category/regime-level controller that chooses among:

- model answer with no tool;
- telemetry-gated selective tool use;
- tool-on-every-task.

Use several deterministic task families spanning high, mixed, and near-total
failure regimes. Freeze category features, competence thresholds, policies,
and sealed evaluation splits before decision capture. Primary question: can a
hierarchical controller retain near-full verified uplift while using fewer
resources than tool-on-every-task and avoiding the M34 transfer failure?

### B. Detector robustness and recalibration

Develop a detector designed to transfer across task structure rather than
reusing the frozen M30 score. Include carry structure, task-family indicators,
normalized telemetry, and category-specific calibration. Compare global,
per-category, and hierarchical detectors on fresh sealed holdouts. No claim of
model-independent telemetry unless transfer is actually established.

### C. Productize the M33 policy in shadow mode

Wire telemetry-gated verifier/tool routing into the practical supervisor as an
advisory-only shadow policy on real local workloads. Record aggregate compute
savings, verifier outcomes, false alarms, misses, and category-level competence
statistics. No production action or threshold unlock without reviewed audit
criteria.

### D. End the telemetry research program

Document M30–M34 as the final research result and return exclusively to the
practical supervisor, retrieval, verifier, review, model-comparison, CLI, and
release tracks.

Do not begin M35 until the operator selects A–D. A new autoloop requires an
explicit new authorization and fresh milestone limit.

## Operator decision (2026-07-11)

The operator selects **A, B, and C in parallel**, consulting Codex as needed
during design. Execution constraints:

- A (hierarchical competence router) and B (transfer-robust detector) run as
  one shared multi-family capture campaign with predeclared, disjoint sealed
  splits: B's detector fitting/calibration data must never touch A's router
  evaluation split, and neither may touch the other's holdout. Both manifests
  are preregistered before any task generation or capture, after an external
  design consult.
- C (M33 policy in supervisor shadow mode) is advisory-only integration work:
  no GPU research claims, aggregate-only logging, no production action or
  threshold unlock without reviewed audit criteria.
- GPU captures serialize on the research hardware; C proceeds concurrently on
  CPU.
- The M32/M33/M34 decision sets remain spent and are not reused for any M35
  primary claim.

## Repository hygiene

Do not commit model weights, caches, local paths, prompts, outputs, operands,
per-task predictions/labels/triggers, token ids/text, raw tensors, detailed
counterfactual records, or private tool results. Public artifacts remain
aggregate-only. Candidate outputs remain candidates, no tool output becomes a
training label without a future audited protocol, and production remains gated.
