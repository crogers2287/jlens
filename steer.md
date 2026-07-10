# steer.md — M32 research-cluster structured repair autoloop

M1 through M31 are complete. Do not redo the M30 decisive detector test or the
M31 naive-resample intervention study. The M27/M29/M30 holdouts and M31 task
set are spent as decision targets.

`CODEX_AUTOSTEER.md` remains the operating contract. The detailed operator
protocol for this loop is `docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`; read it in
full before implementation.

## Operator decision

The operator selected post-M31 option A: keep the validated frozen telemetry
trigger and replace the failed resample intervention with stronger,
literature-informed repair operators.

The operator authorizes a new bounded autoloop of up to three milestone
completions beginning with M32, subject to the normal 4-hour and blocker limits.
Use separate implementation and steer commits for every milestone.

## Current evidence

### M30 — detector increment ESTABLISHED

- Powered n=192 once-read holdout: full_telemetry .917 vs metadata .818.
- Paired delta accuracy +.099 with 95% CI [+.042,+.156]; both accuracy and
  balanced-accuracy intervals exclude zero.
- 27 metadata errors corrected vs 8 introduced.
- The increment requires the distributed full feature set; window entropy
  alone is insufficient.

### M31 — trigger works; naive repair does not

- 192 fresh tasks; frozen M30 detector reproduced exactly; p(fail) >= .50.
- Of 99 telemetry triggers, 88 hit real original failures (~89% precision),
  replicating the detector on a third fresh set.
- A seeded temperature-0.7 retry rescued only 4 of those failures (~4.5%).
- telemetry-triggered success .474 vs no-retry .469 and matched-random .458;
  primary confidence intervals crossed zero, so usefulness was not established.
- always-retry and random-retry were net negative; telemetry gating was the
  only non-losing policy.
- Four private verified recovery traces exist, far too few for training use.

## Research position

Failure detection is validated within the controlled arithmetic/model/decode
scope. The open blocker is recovery: systematic arithmetic errors are not fixed
by drawing again from the same distribution.

M32 must isolate the repair question by keeping the M30 detector frozen while
comparing structured repair methods, matched controls, and an explicit trusted-
tool upper bound. It must not tune the detector on M32 data.

The M32 design intentionally incorporates method-level lessons from:

- Reinforcement Inference (arXiv:2602.08520): selective deliberate second pass;
- Gnosis (arXiv:2512.20578): trajectory-level internal descriptors;
- CLUE (arXiv:2510.01591): experience-centroid candidate verification;
- What Am I Missing? (arXiv:2605.31561): diagnosis/recovery gap;
- SCoRe (arXiv:2409.12917): on-policy trace collection and offline-SFT risks;
- Inference-Time Intervention (arXiv:2306.03341): future control direction;
- Doomed from the Start (arXiv:2607.06503): later partial-trajectory gating;
- Code Correctness Signals (arXiv:2606.14530): confound controls.

Borrow ideas, not unreviewed source code. Do not import a paper repository
without license/dependency review.

## M32 — current milestone

Execute `docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md` section:
**M32 — telemetry-gated structured repair bakeoff**.

Core requirements:

1. Preregister before generation:
   - 384 fresh tasks, six existing boundary bands x 64;
   - deterministic disjointness from M29, M30, and M31;
   - frozen prompts, seeds, candidate order, budgets, controls, metrics, and
     claim rules.
2. Recreate and verify the frozen M30 full-telemetry score and .50 threshold.
3. Capture the original greedy decode for every task.
4. Compare the preregistered repair candidates:
   - exact M31 temperature-0.7 resample baseline;
   - independent deliberate/decomposition re-solve;
   - checker-guided repair that reveals failure but never the correct answer;
   - diagnose-then-repair two-stage intervention;
   - deterministic tool computation as an upper-bound reference only.
5. Evaluate shared-candidate policies with equal compute and verifier access:
   - no repair;
   - always structured repair;
   - matched-random structured repair;
   - telemetry-triggered structured repair;
   - telemetry-triggered resample-only;
   - telemetry-triggered tool upper bound.
6. Primary structured bundle: verifier-first-passing candidate, otherwise keep
   the original. A known-correct original must never be replaced by a failing
   candidate.
7. Secondary selectors:
   - frozen-telemetry candidate reranking, CLUE-inspired;
   - numeric majority/consensus.
8. Primary preregistered verdicts:
   - H1 repair improvement vs the same-task resample baseline;
   - H2 end-to-end telemetry policy usefulness vs both no-repair and matched-
     random structured repair.
9. Store all detailed recovery traces privately and gitignored. Public output
   stays aggregate-only. No fine-tuning or production unlock.

Required deliverables and stop conditions are defined in the detailed M32
protocol file and are mandatory.

## Result-driven continuation

After M32, follow only the branch rules in
`docs/M32_RESEARCH_CLUSTER_AUTOLOOP.md`:

- H1 improved + H2 useful: M33 trajectory-aware candidate verification and
  reranking, then eligible M34 partial-gating/recovery-dataset work.
- H1 improved but H2 not established: M33 threshold/selection/compute study;
  do not simply scale M32.
- model repair not improved but tool ceiling large: M33 tool-grounded runtime
  repair, then M34 second-category detector transfer.
- negative/harmful result or detector reproduction failure: stop immediately.

A recovery-dataset milestone requires at least 50 verifier-confirmed,
model-generated wrong-to-right traces and all provenance/diversity/privacy gates
listed in the autoloop document. No weight training is authorized in this loop.

## Repository hygiene

Do not commit private prompts/outputs, operands, diagnoses, per-task labels or
predictions, token IDs/text, raw tensors, file-system paths, model weights,
caches, or detailed recovery records. Public reports remain aggregate-only.
No candidate becomes gold and production remains gated until explicit audited
unlock criteria are defined.
