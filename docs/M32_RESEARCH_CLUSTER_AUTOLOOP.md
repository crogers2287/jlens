# M32 research-cluster telemetry autoloop

Status: operator-authorized plan. This file defines a bounded three-milestone
telemetry loop beginning at M32. `steer.md` remains the current execution source
of truth and `CODEX_AUTOSTEER.md` remains the operating contract.

## Why M32 changes the repair operator

M30 established that the frozen full-telemetry score predicts objective
arithmetic failure better than difficulty metadata. M31 then separated
detection from recovery:

- the frozen trigger again found real failures with about 89% precision;
- a single temperature-0.7 resample rescued only about 4.5% of correctly
  triggered failures;
- always-retry and matched-random retry were net negative;
- telemetry gating was the only non-losing policy.

The next blocker is therefore not failure detection. It is the repair operator.
M32 must keep the detector frozen and test stronger, literature-informed repair
methods without changing the target after results are visible.

## Research ideas being reused

This plan borrows method-level ideas, not unreviewed source code. Do not import
paper repositories without checking license and dependency impact.

1. **Reinforcement Inference** — arXiv:2602.08520
   - use internal uncertainty to allocate a second, more deliberate attempt;
   - do not treat a generic "you were uncertain, think harder" prompt as the
     whole method;
   - compare selective intervention with always-intervene and matched-compute
     controls.

2. **Gnosis** — arXiv:2512.20578
   - correctness information can be distributed over a generation trajectory;
   - use fixed-budget temporal summaries rather than only a final-token score;
   - preserve a later path to partial-generation detection and early control.

3. **CLUE** — arXiv:2510.01591
   - summarize generation trajectories and compare them with success/failure
     experience using a simple nearest-centroid verifier;
   - use this idea for candidate reranking, while keeping the M30 detector
     frozen for M32's primary causal comparison.

4. **What Am I Missing?** — arXiv:2605.31561
   - diagnosis can be predictive without making correction reliable;
   - include a diagnostic/decomposition repair arm, but explicitly measure
     right-to-wrong damage and do not assume self-reflection helps.

5. **SCoRe** — arXiv:2409.12917
   - offline correction traces can suffer distribution mismatch and behavior
     collapse;
   - collect only on-policy, verifier-grounded recovery traces;
   - do not fine-tune in this loop and do not call traces training-ready merely
     because they exist.

6. **Inference-Time Intervention** — arXiv:2306.03341
   - internal signals can eventually become control inputs, not only alarms;
   - direct activation steering is out of scope for M32 because it would change
     both detector and intervention mechanism at once. Preserve it as a future
     research branch after repair baselines are established.

7. **Doomed from the Start** — arXiv:2607.06503
   - partial-trajectory probes can support recall-controlled early stopping;
   - reserve this for M33 only after M32 closes the repair-operator question.

8. **Code Correctness Signals in LLM Hidden States** — arXiv:2606.14530
   - control for simple confounds such as prompt/response length;
   - any new trajectory feature must be compared with length-only and metadata
     baselines, with residualized or matched analyses where practical.

## Global invariants for M32-M34

- Keep the M30 full-telemetry detector and p(fail) >= 0.50 trigger frozen for
  M32. Refit only by the existing deterministic reproduction path and require
  the published M30 confusion matrix/hash check to pass.
- Fresh decision data only. M27, M29, M30, and M31 sets are spent.
- Preregister each milestone before generation or capture.
- No post-hoc task selection, feature selection, operator deletion, threshold
  tuning, or claim-rule changes after decision data are read.
- The deterministic verifier may be used as an explicit runtime component only
  in arms preregistered as verifier-guided. Matched controls receive identical
  verifier access and candidate budgets.
- Never reveal the true arithmetic answer in a repair prompt.
- Keep detailed prompts, outputs, operands, token data, per-task labels,
  predictions, and recovery traces private and gitignored.
- Public artifacts are aggregate-only.
- Candidate outputs and recovery traces are not gold labels.
- Production remains gated.
- No model download, new model, activation steering, live web retrieval, or
  arbitrary code execution from model output in this loop.

# M32 — telemetry-gated structured repair bakeoff

## Primary question

Can the already-validated frozen telemetry trigger become operationally useful
when it gates a stronger structured repair bundle instead of a naive resample?

## Preregistered data design

Before generation, create `data/prompts/m32_repair_manifest.json` containing:

- 384 fresh multiplication tasks: six existing boundary bands x 64 tasks;
- deterministic rejection of every tuple generated by M29, M30, and M31;
- one intervention split; no M32 fitting of the detector;
- all tasks retained;
- constant `checker_needed` applicability;
- original decode: existing greedy protocol;
- all repair prompts, seeds, token caps, candidate order, policy semantics,
  bootstrap seeds, and claim rules.

If tuple-space exhaustion or another design failure occurs, stop before capture
rather than changing the task distribution silently.

## Frozen trigger

- Recreate the M30 full-telemetry nearest-centroid score from private M30 train
  records.
- Verify the protocol hash and exact reproduction of M30's published holdout
  confusion matrix.
- Use the frozen validation threshold p(fail) >= 0.50.
- Score only the original greedy generation when deciding whether to repair.
- No M32 labels may affect triggering.

## Repair candidates

Generate candidates only for tasks selected by the policy being evaluated.
Every policy must receive the same candidate budget and candidate captures.

1. `resample_t07`
   - exact M31 seeded temperature-0.7 baseline;
   - retained so stronger methods are compared on the same tasks.

2. `independent_deliberate`
   - fresh context containing the original problem but not the original answer;
   - instruct the model to recompute independently using an explicit
     digit/decomposition method and return only the final number;
   - deterministic greedy decode with a preregistered larger repair cap.

3. `checker_guided_repair`
   - include the original problem, original candidate answer, and only the
     verifier fact that the candidate failed;
   - do not reveal the correct result or numeric difference;
   - instruct the model to locate the likely arithmetic mistake, use a
     different computation path, and return a replacement final number.

4. `diagnose_then_repair`
   - two-stage, fixed-budget intervention inspired by question/diagnosis work;
   - stage A privately generates a compact diagnosis or verification plan;
   - stage B receives that plan and recomputes the answer;
   - the plan and output remain private.

5. `tool_upper_bound`
   - deterministic trusted arithmetic computation;
   - reported only as an upper-bound/product reference, never as evidence of
     model self-correction and never mixed into model-generated trace counts.

The existing model remains fixed. No repair LoRA or weight update is permitted
in M32.

## Candidate selectors

Evaluate selectors separately so the experiment distinguishes candidate
quality from candidate selection.

1. `operator_standalone`
   - one policy result per model-side operator;
   - replace the original only when the preregistered verifier-guided semantics
     allow it.

2. `verifier_first_pass_bundle` — primary repair bundle
   - evaluate structured candidates in frozen order;
   - select the first verifier-passing candidate;
   - retain the original when no candidate passes;
   - because the verifier is exact for this category, this arm should not
     introduce a known wrong answer. Any violation is a stop condition.

3. `telemetry_rerank_bundle` — secondary, CLUE-inspired
   - capture the same supported telemetry for every repair candidate;
   - rank candidates by the frozen M30 pass-risk geometry without consulting
     candidate labels;
   - compare with first-candidate and majority/consensus baselines;
   - mark distribution-shift limitations because repair prompts differ from
     the M30 training prompt.

4. `majority_bundle` — secondary self-consistency baseline
   - numeric majority across model-side candidates with deterministic tie
     breaking fixed in the manifest;
   - no verifier consultation for selection.

## Policy controls

Run all policies on identical original tasks and shared candidate captures:

- `no_repair`
- `always_structured_bundle`
- `random_trigger_structured_bundle`, fixed-seed and trigger-count matched
- `telemetry_trigger_structured_bundle`
- `telemetry_trigger_resample_only`, direct M31 replication baseline
- `telemetry_trigger_tool_upper_bound`, product ceiling only

For verifier-guided arms, all matched controls receive the same verifier and
candidate access. Do not compare a verifier-guided telemetry arm against a
control denied the verifier.

## Primary hypotheses and claim rule

Preregister two primary hypotheses:

### H1 — repair operator improvement

On the same correctly-triggered original failures, the structured model-side
bundle rescues more errors than `resample_t07`.

Classification:

- `repair_improved` only if the paired 95% bootstrap CI for rescue-rate delta
  is strictly above zero;
- `repair_worse` only if the upper bound is strictly below zero;
- otherwise `repair_not_established`.

### H2 — end-to-end policy usefulness

The telemetry-triggered structured bundle improves final verified success over
both `no_repair` and trigger-count-matched random structured repair.

Classification:

- `useful` only if both paired success-rate delta 95% CIs are strictly above
  zero;
- `harmful` if the delta versus no-repair has a 95% CI strictly below zero;
- otherwise `not_established`.

Do not substitute tool-upper-bound results for either hypothesis.

## Required metrics

Report aggregate-only:

- original pass/fail/undecided/cap counts;
- trigger count, rate, precision, recall, false alarms;
- per-operator candidate pass rate;
- wrong-to-right rescues and right-to-wrong introductions;
- final verified success by policy;
- retries/candidates/tokens used and cost per verified rescue;
- paired bootstrap CIs for all preregistered primary deltas;
- candidate overlap: which operators rescue unique versus shared failures;
- telemetry-rerank accuracy and calibration versus candidate labels;
- tool upper-bound ceiling;
- private verified recovery-trace count.

## Recovery trace schema

Write private gitignored JSONL for model-generated wrong-to-right recoveries:

- trace schema version;
- model/checkpoint and decode-protocol hashes;
- task/category id and private prompt reference;
- original output reference and original verifier verdict;
- original telemetry descriptor and frozen trigger score;
- repair operator id and repair prompt-template hash;
- diagnosis/plan reference when applicable;
- candidate output reference, candidate telemetry, verifier verdict;
- selector id and final selection result;
- whether the trace was a rescue, no-change, or regression;
- provenance and split id.

Do not include raw private content in public reports. Do not label these traces
training-ready until later distribution, diversity, and audit checks pass.

## M32 deliverables

- `data/prompts/m32_repair_manifest.json` in a preregistration commit
- repair-capture support with greedy behavior unchanged
- `src/m32_structured_repair.py`
- tests for deterministic prompts/seeds, shared-candidate accounting, verifier
  isolation, paired metrics, and privacy
- `reports/telemetry/hf_m32_repair_run_summary.json`
- `reports/telemetry/hf_m32_repair_evaluation.json`
- `docs/M32_STRUCTURED_REPAIR_STUDY.md`
- private recovery JSONL, gitignored
- updated `STATE.md`, `reports/FINDINGS.md`, and full suite green

## M32 stop conditions

Stop and report rather than improvising if:

- the M30 detector cannot be reproduced exactly;
- any candidate/control receives unequal compute or verifier access;
- verifier-first-pass replaces a verifier-passing original with a failing
  candidate;
- private trace content would need to be committed;
- a new model/dependency/hardware decision is required;
- the full suite or commit-safety checks fail.

# Autoloop continuation after M32

The operator authorizes up to three milestone completions beginning with M32,
subject to the normal four-hour and blocker limits in `CODEX_AUTOSTEER.md`.
Use separate implementation and steer commits for every milestone.

## Branch 1 — M32 H1 improved and H2 useful

Proceed to M33: trajectory-aware candidate verification and reranking.

- Keep the successful M32 repair bundle frozen.
- On fresh tasks/candidates, compare:
  - existing M30 full telemetry;
  - CLUE-inspired trajectory-delta nearest centroids;
  - Gnosis-inspired fixed-budget temporal pooling over supported hidden,
    attention, router, and logit streams;
  - final-token/logit, length-only, metadata-only, and majority baselines.
- Hidden/attention features are optional only when existing approved hooks expose
  them. Mark unsupported honestly; do not download a new model or fabricate.
- Use nested or sealed train/validation/holdout splits and control for length.
- Primary question: can trajectory-aware scoring select a verifier-passing
  repair candidate better than the frozen M30 score without consulting the
  verifier at selection time?

Then, if M33 establishes an increment and loop budget remains, proceed to M34:
partial-trajectory gating and recovery-dataset packaging.

## Branch 2 — M32 H1 improved but H2 not established

Proceed to M33 with the same candidate-verifier study, but focus on threshold,
compute allocation, and retain-original semantics. Do not simply scale M32.
M34 may package traces only if at least 50 diverse verified recoveries exist.

## Branch 3 — M32 model-side repair not improved, tool upper bound large

Proceed to M33: tool-grounded repair adapter.

- Keep telemetry as the gate.
- Route triggered checkable tasks to deterministic computation.
- Measure compute saved versus tool-on-every-task and verified success versus
  no-repair/random routing.
- Treat this as product/runtime evidence, not model self-correction.
- Do not generate a model-training dataset from tool outputs unless a later
  steer explicitly defines distillation and audit rules.

M34 then becomes a second-category transfer test of the detector, not trace
scaling.

## Branch 4 — M32 negative/harmful or detector reproduction fails

Stop the autoloop. Do not proceed to M33. Report the failure and preserve all
gates.

# M34 recovery dataset gate

A recovery-dataset milestone is allowed only when all are true:

- at least 50 verifier-confirmed model-generated wrong-to-right traces;
- at least two repair operators contribute nontrivial unique rescues;
- no duplicate task instances across decision sets;
- every trace has model/decode/operator/provenance hashes;
- regressions and failed repairs are retained in the private corpus, not hidden;
- a public aggregate manifest passes privacy checks;
- no weight training occurs in this autoloop.

M34 may create schema validators, deduplication, balance reports, private split
manifests, and a future-training handoff. It must explicitly incorporate the
SCoRe warning about offline distribution mismatch: the dataset is evidence and
infrastructure for later on-policy training, not proof that ordinary SFT will
produce self-correction.

# Required final stop report

At the end of the loop, print:

- latest commit SHA and milestone count;
- M32 H1 and H2 verdicts;
- trigger precision and repair rescue rates;
- best model-side repair operator and compute per rescue;
- whether M33/M34 ran and why;
- public artifacts created;
- private traces intentionally not committed;
- tests passed;
- exact next operator decision.
