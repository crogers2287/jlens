# steer.md — M32 structured-repair reactivation

M1 through M31 and M32P are complete. M32R stopped at the Agents-A1 resource
gate. M32P completed the model-calibrated Qwen proxy expert-routing study and
closed that track under its preregistered Branch 3: guided equal-compute expert
swaps did not beat matched-random perturbations, no deployable rerouting policy
worked, and no soft expert penalty generalized.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Operator decision

The operator selects post-M32P option A: **reactivate and execute the preserved,
preregistered M32 telemetry-gated structured-repair bakeoff**.

The supersession notice on M32 is lifted for execution only. The existing
preregistration remains immutable:

- protocol: `docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`
- manifest: `data/prompts/m32_repair_manifest.json`
- implementation: `src/m32_structured_repair.py`
- tests: `tests/test_m32_structured_repair.py`
- preregistration commit: `5f0edfeff15a20e848d99b164774c092697d1a90`

Do not rewrite, regenerate, rebalance, or replace the task set, repair prompts,
candidate order, budgets, thresholds, seeds, selectors, controls, or H1/H2 claim
rules after the fact. The manifest was committed before any M32 generation or
capture and must now be executed exactly as written.

The operator authorizes a bounded autoloop of up to three milestone completions
beginning with this M32 execution, subject to the normal four-hour and blocker
limits. Use separate result and steer commits for each completed milestone.

## Why M32 is now the correct next test

The detector is real but the tested repair operators have failed:

- M30 established that full internal telemetry predicts deterministic arithmetic
  failure better than difficulty metadata on a fresh sealed holdout.
- M31 reproduced a high-precision trigger, but a temperature-0.7 resample rescued
  only about 4.5% of correctly triggered failures.
- M32P found that equal-compute expert-route perturbations had an oracle rescue
  ceiling of only about 11.9%, with guided swaps exactly matching random swaps
  on sealed holdout and more regressions than rescues.

The remaining untested model-side question is whether a genuinely different
reasoning procedure can repair systematic errors:

- independent deliberate/decomposition re-solve;
- checker-guided regeneration that reveals failure but not the answer;
- diagnose-then-repair with a private intermediate plan;
- verifier-first candidate selection;
- deterministic computation as a product ceiling only.

This separates “the model repeated or rerouted the same bad computation” from
“the model can recover when forced onto a different explicit procedure.”

## Current milestone — execute M32 exactly

### Frozen data and detector

1. Generate the 384 manifest-defined fresh multiplication tasks across six
   bands, deterministically disjoint from M29, M30, and M31.
2. Retain every generated task. Stop on tuple exhaustion or action-applicability
   violation; do not reselect.
3. Recreate the frozen M30 full-telemetry nearest-centroid detector from private
   M30 train records and require the existing protocol/hash/confusion-matrix
   reproduction checks to pass.
4. Use the frozen p(fail) >= 0.50 trigger on the original greedy decode only.
   No M32 outcome may affect triggering.

### Shared repair candidates

For the exact tasks and budgets frozen in the manifest, capture:

- `resample_t07` — the M31 seeded resample baseline;
- `independent_deliberate` — fresh-context digit/decomposition re-solve;
- `checker_guided_repair` — candidate failed, correct answer withheld;
- `diagnose_then_repair` — private diagnosis/plan followed by recomputation;
- `tool_upper_bound` — trusted deterministic arithmetic, ceiling only.

Do not reveal the correct answer or numeric error to any model-side repair arm.
The model/checkpoint remains frozen. No LoRA, weight update, activation steering,
new model, or new dependency is authorized.

### Policies and selectors

Evaluate the preregistered shared-candidate policies with equal candidate budget
and equal verifier access:

- no repair;
- always structured bundle;
- trigger-count-matched random structured bundle;
- telemetry-triggered structured bundle;
- telemetry-triggered resample-only;
- telemetry-triggered tool upper bound.

Primary selector: first verifier-passing structured candidate in the frozen
order, retaining the original when none pass. A verifier-passing original must
never be replaced by a verifier-failing candidate; any violation is a stop
condition.

Secondary descriptive selectors remain exactly as preregistered:

- frozen-telemetry/CLUE-style candidate reranking;
- numeric majority/consensus.

### Primary verdicts

H1 — repair operator improvement:

- On the same correctly triggered original failures, the structured model-side
  bundle must rescue more errors than `resample_t07`.
- Classify `repair_improved` only when the paired 95% bootstrap CI for the
  rescue-rate delta is strictly above zero.

H2 — end-to-end policy usefulness:

- The telemetry-triggered structured bundle must improve final verified success
  over both no repair and trigger-count-matched random structured repair.
- Classify `useful` only when both paired 95% success-rate delta intervals are
  strictly above zero.

The deterministic tool arm is a ceiling/product reference and cannot satisfy H1
or H2 for model self-correction.

## M32P distribution-shift finding

M32P found that the frozen M30 detector dropped to precision .766 / recall .738
on a carry-structured capability frontier. Record detector performance and
carry/difficulty subgroup metrics descriptively during M32, but do not alter the
immutable M32 task generator, trigger, threshold, policies, or primary claim
rules. Any carry-stratified analysis is secondary and explicitly non-confirmatory.

## Recovery traces

Write private gitignored traces for every model-generated wrong-to-right repair,
including failed repairs and regressions in the private corpus. Public artifacts
remain aggregate-only. Do not call the corpus training-ready unless the original
M32 recovery-data gates are met; no weight training is authorized in this loop.

## Result-driven continuation

After M32, follow only the branches already defined in
`docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`:

- H1 improved and H2 useful: proceed to M33 trajectory-aware candidate
  verification/reranking; M34 recovery-dataset work is eligible only if all
  volume, diversity, provenance, and privacy gates are met.
- H1 improved but H2 not established: proceed to M33 threshold, candidate
  selection, retain-original, and compute-allocation study; do not merely scale.
- Model-side repair not improved but the deterministic-tool ceiling is large:
  proceed to M33 telemetry-gated tool routing, then use the remaining milestone
  for detector transfer/robustness rather than claiming model self-correction.
- Harmful result, detector reproduction failure, unequal verifier/compute access,
  privacy failure, test failure, or other protocol blocker: stop immediately and
  report the exact blocker.

## Required reporting

At the stop, report:

- latest commit SHA and milestones completed;
- M32 H1 and H2 verdicts;
- frozen-trigger precision/recall;
- per-operator rescue and regression rates;
- best model-side operator and cost per verified rescue;
- structured-policy deltas versus no repair and matched-random;
- deterministic-tool ceiling;
- private recovery-trace count intentionally not committed;
- tests and commit-safety result;
- exact next branch and operator decision, if any.

## Repository hygiene

Do not commit model weights, caches, local model paths, prompts, outputs,
operands, diagnoses, per-task predictions/labels/triggers, token ids/text, raw
router tensors, or detailed recovery records. Public reports remain
aggregate-only. No candidate becomes gold and production remains gated until
explicit audited unlock criteria are defined.
