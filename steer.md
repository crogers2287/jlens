# steer.md — verify M36T tool arms before sealed evaluation; continue exact-token M37J-A

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `8eb2e9ee32c004fa3114ea40bf4020092e0776ff` only where explicitly
amended below. Every sealed-data, verifier, privacy, claim-boundary, resource,
production, and repository-hygiene gate from that steer remains binding by
incorporation. No scientific threshold, feature family, task set, model,
checkpoint, or resource gate is relaxed.

## Current established state

- M36T development capture completed 96/96 with 65 positive and 31 negative
  labels. The frozen power floor passed and the four development comparators
  were frozen at commit `945830ceca2e02f4940e63f2c3cbe1261b74b359`.
- The 192-task M36T sealed manifest was committed before outcomes at
  `12e3af03ef6c01724b38d60a731948987d31f022`; sealed capture is running under
  the existing supervisor. Do not interrupt it for this steer.
- M37J-A's first implementation used a decode-to-text-to-encode round trip for
  lens positions. That path was objectively invalid because token count and
  absolute positions were not preserved and it produced a CUDA out-of-bounds
  failure. Commit `a59ca07ccfdd5a0d08da4158e2d106988816b979` correctly replaced it
  with an exact recorded-token-id forward using `ActivationRecorder`,
  `lens.transport`, and the model unembedding. The 34 old-provenance rows were
  set aside and the full 192-task capture restarted from zero after a two-task
  smoke. Continue this corrected run; never merge the discarded rows.
- M38E remains queued behind the active 3090 sealed-capture window. M37J-C
  bridge implementation may continue CPU-only without delaying active primary
  tracks.

## Binding M36T evaluator correction before any sealed result is opened

`src/m36t_evaluate.py` currently assigns success unconditionally to every
routed/tool task. The comment states that the deterministic tool result is
verifier-accepted, but the evaluator does not load the private task, construct
the tool result, or call the verifier. This does not satisfy the frozen
manifest requirement that a tool result replaces model output only when the
verifier accepts it.

Do not run the sealed evaluator in its current form. At a row boundary, record
this steer SHA and complete the following CPU-only correction before sealed
capture ends. Do not inspect sealed aggregate outcomes while implementing or
testing it.

1. Load the exact private sealed task file used by the committed manifest and
   join it one-to-one with sealed rows by `task_id`.
2. Preflight before scoring:
   - exactly 192 unique task ids and 192 unique row ids;
   - task-id sets exactly equal;
   - task-file SHA-256 equals
     `007f52994d90fef3330d7c318a6de482c27bce2cb4a70499afae6a766b746813`;
   - every row uses the pinned checkpoint/revision and expected feature schema;
   - no duplicate, missing, malformed, or post-step-256 primary feature;
   - every output length is within the committed 2,048-token ceiling.
3. Implement the deterministic tool as a pure function of the private task:
   - numeric families return the task's exact deterministic computed answer;
   - `json_digits` returns the exact expected JSON array;
   - pass the generated tool text through the same frozen `task_verdict`
     implementation used during capture.
4. A routed arm may record tool success only when that verifier returns
   `pass`. A missing task, unsupported family, undecided verdict, or verifier
   failure is an evaluation blocker, not a model failure and not an assumed
   success. Commit an aggregate blocker and stop before opening hypotheses.
5. Preserve the existing decision point and token accounting. The correction
   verifies the tool result; it does not change `k`, routing rankings, model
   token accounting, counterfactual caps, or any hypothesis.
6. Use a dedicated frozen RNG instance for the count-matched-random routed set,
   independent of bootstrap RNG consumption. Freeze `RANDOM_POLICY_SEED =
   36036` in the evaluator and aggregate manifest amendment. Keep bootstrap at
   10,000 resamples with seed 36036 as already committed.
7. Add synthetic/private-safe tests covering all four families, verifier
   acceptance and rejection, duplicate/missing ids, task-SHA mismatch, equal
   routing count, deterministic random routing, and a tool result that must not
   overwrite a verified-correct model answer with failure.
8. Commit an aggregate-only technical amendment before running the evaluator.
   State that this is protocol conformance completed before sealed outcomes
   were inspected. Run `check_commit_safe.py`, verify all tests, and verify the
   pushed remote SHA.

If the current evaluator has already produced a result, mark that result
invalid without interpreting it, remove it from the decision path, apply this
correction, and rerun exactly once from the unchanged sealed rows.

## M37J-A provenance and completion

Continue the exact-token restart unchanged. The final aggregate result must pin
both the frozen scientific manifest/lens and the corrected capture-code SHA.
It must state that all 192 accepted rows share the exact-token provenance and
that zero rows from the failed round-trip implementation entered any fit,
selection, metric, or holdout analysis.

Do not change semantic words, substring matching, layers, positions, cadence,
top-k, budgets, families, splits, comparators, or hypothesis rules after the
observed smoke. Any concern about those frozen choices belongs in limitations
or a separately preregistered successor study.

## Research scan and scaling implications

The current scan found no verified official Agents-A1 4B checkpoint and no
actionable r/LocalLLaMA implementation lead. Continue the official
`InternScience`-only 4B watch from steer `8eb2e9e`; do not substitute a
community quant.

Add these papers to the future-work register without changing M36T, M37J-A, or
M38E:

- `2603.18353`, *Interpretability without actionability*: strong internal probe
  discrimination did not reliably translate into safe output correction. This
  reinforces the existing separation between observation/prediction evidence
  and any intervention or production claim.
- `2604.00421`, *Self-Routing: Parameter-Free Expert Routing from Hidden
  States*: hidden representations can contain routing-sufficient information
  in small trained systems. This supports comparing hidden-state semantic
  features with router telemetry in a fresh M37J-C efficacy study, but it is
  not evidence that Agents-A1 routes should be replaced.
- `2604.14419`, *Equifinality in Mixture of Experts*: substantially different
  routing topologies can reach similar language-modeling quality. This further
  forbids treating router topology or entropy as a causal quality measure and
  supports retaining metadata/confidence, router, and semantic readout as
  separate comparators.

These sources do not authorize route edits, activation steering, early exit,
or production deployment. Agents-A1 35B scaling remains the observation-only
semantic bridge defined in steer `8eb2e9e`; a fitted Jacobian path remains
blocked pending an official smaller differentiable checkpoint that passes the
unchanged memory gate.

## Execution order and safety

- Continue M36T sealed capture uninterrupted.
- Correct and test the evaluator CPU-only before capture completion.
- Continue the corrected M37J-A V100 run.
- Launch M38E only at its already-authorized safe 3090 window.
- Continue M37J-C CPU build; no live smoke may preempt primary tracks or normal
  service restoration.

Stop on checkpoint mismatch, task/row mismatch, task-hash mismatch, feature or
label leakage, verifier bypass, invalid telemetry alignment, numerical
instability, repeated worker failure, privacy failure, resource-gate breach,
or inability to restore normal serving.

Never commit private prompts, outputs, operands, token text or ids, per-task
labels or predictions, raw telemetry, hidden states, activations, gradients,
Jacobians, lens matrices, model weights, caches, or local paths. Public
artifacts remain aggregate-only and must pass `check_commit_safe.py`.
Production remains gated.