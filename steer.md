# steer.md — M36 adaptive Agents-A1 calibration, then raw-vs-jLens benchmark

M1 through M35 are complete. Do not reopen their sealed decision sets.
`CODEX_AUTOSTEER.md` remains the operating contract.

## Established state

M36V is complete on the exact pinned checkpoint:

- checkpoint: `cyankiwi/Agents-A1-AWQ-INT4`;
- revision: `3e522d4e46438c782789b73c8ff4503e0edd037c`;
- runtime: isolated vLLM 0.24.0, compressed-tensors, tensor parallel 2;
- architecture: `qwen3_5_moe`, 40 routed text layers, 256 experts, top-8;
- full observation-only router telemetry validated against actual fused dispatch;
- zero expert-id mismatches and exact dispatch-weight identity in validation;
- Phase-2 stock and instrumented AWQ both passed 16/16 verifier checks;
- telemetry overhead in the controlled smoke was about 1.32x;
- normal Agents-A1 GGUF serving was restored after every research run.

Do not repeat M36V. Preserve its artifacts and findings as the telemetry/runtime
qualification for M36.

## New calibration finding and immediate operator decision

The first 64/384 M36 calibration rows exposed a decode-budget cliff:

- 3x2 and 4x3 multiplication: about .94 pass;
- 5x4 and 6x5 multiplication: apparent .06/.00 pass, but .94/1.00 truncation at
  the 1,024-token cap;
- the hard cells are therefore budget-bound, not yet demonstrated capability
  failures.

The current sequential full-tensor calibration is also running at about 22
rows/hour, far below the model's raw serving throughput. Do **not** spend the
remaining 15-20 hours completing the original 384-row sweep unchanged.

At the next safe task boundary:

1. stop the current capture gracefully;
2. preserve every completed private row and capture;
3. record the exact completed count and last task id;
4. do not delete, relabel, or regenerate completed rows;
5. restore the serving stack before implementation work.

Calibration rows are not benchmark decision data, so the adaptive amendment
below is permitted. Record it publicly before generating any new calibration
rows.

# M36C — profiled, adaptive Agents-A1 calibration

The goal is to obtain enough **completed correct and completed incorrect**
examples to fit Agents-A1-specific policies without wasting most runtime on
repeated truncations or telemetry file handling.

## Phase 0 — profile the research harness

Before resuming the sweep, add per-task timing for:

- model generation;
- collector reset/install/fetch;
- worker RPC;
- telemetry serialization write and read;
- feature derivation;
- verifier execution;
- result append/fsync.

Profile a fixed private eight-prompt set spanning short, medium, and
truncation-prone outputs. Report aggregate medians and p95 values only.

Implement a benchmark-scale **summary telemetry path** that computes the frozen
12 approved scalar features in-process or on-device and returns only bounded
summaries. Full per-token/per-layer NPZ capture remains enabled only for a tiny
validation sample.

Required equivalence gate:

- on at least eight prompts, every summary-path feature must match the feature
  recomputed from the raw telemetry capture with maximum absolute difference
  <= 1e-5;
- selected expert ids and dispatch validation remain covered by the completed
  M36V evidence and need not be repeated for every calibration prompt;
- no raw token, prompt, output, route, tensor, or local path enters public
  artifacts.

Performance target:

- median non-generation harness overhead <= 25% of model generation time on the
  profile set.

If the target is missed, fix the largest measured component once before
continuing. Do not optimize speculatively. Microbatching of 2-8 prompts is
permitted only if request-to-telemetry alignment, per-request feature identity,
and verifier outcomes are regression-tested. Otherwise retain sequential
summary capture.

Commit profiling/optimization code and tests separately from calibration
results.

## Phase 1 — adaptive frontier map

Keep the completed 64 multiplication rows. For each of the remaining five
families and four strata, run a deterministic **four-row probe** using the
already-generated task order.

Use staged decode budgets:

1. start probes at 512 output tokens;
2. when a probe truncates, rerun at most two predetermined truncated examples
   from that cell at 1,024 tokens;
3. if those still truncate, rerun at most one predetermined example at 2,048
   tokens;
4. do not run a whole cell at 2,048 tokens.

For every cell, report separately:

- completed-correct rate;
- completed-incorrect rate;
- truncation rate at each tested cap;
- median and p95 output length;
- median generation time and telemetry overhead.

Never count a capped output as evidence that the model reasoned incorrectly.
Classify it as `truncated_budget`.

## Phase 2 — selective expansion

After the four-row probes, freeze the expansion rule before adding rows:

- **mixed completed frontier:** completed pass rate 0.20-0.80 and truncation
  <= .25 at the chosen cap -> expand that cell to 16 total rows;
- **high/low completed anchor:** completed pass rate > .80 or < .20 with
  truncation <= .25 -> retain or expand to 8 total rows;
- **budget-bound cell:** truncation > .50 at 1,024 tokens -> do not expand beyond
  the probe/rescue sample; keep it as a separate output-budget finding;
- cells between these rules may expand to 8 only when needed to meet the class
  quotas below.

Stop adaptive calibration when all are true:

- at least 48 completed-correct rows;
- at least 48 completed-incorrect rows;
- at least three task families represented among completed failures;
- at least two mixed-frontier cells;
- total retained calibration rows <= 192, excluding capped reruns of the same
  calibration prompt.

If the quotas cannot be reached within 192 rows, stop and report
`completed_failure_frontier_not_found`; do not manufacture a benchmark dominated
by timeouts.

Split retained completed rows deterministically within cell into detector
`D` (two thirds) and policy calibration `R` (one third). Truncated rows remain a
separate budget-policy dataset and are never silently mixed into the completed
wrong-answer label.

# Detector and policy freeze

Fit Agents-A1-specific components only from M36C data.

## Operational black-box policy

The black-box controller may use:

- family/stratum metadata;
- output length;
- explicit finish reason/truncation flag;
- deterministic verifier availability and outcome.

A truncated or verifier-failing output may be routed directly to the trusted
 tool. This is practical supervisor behavior and must be reported separately
from telemetry prediction.

## Internal telemetry detector

Fit the full detector on completed outputs using router/logit telemetry.
`decode_step_count` may be retained for operational scoring, but internal
telemetry increment is not established merely by recognizing the token cap.

Freeze and report these comparators:

1. metadata only;
2. metadata + output length;
3. metadata + output length + logit features;
4. metadata + output length + router features;
5. full approved telemetry.

For the future H2 telemetry claim, the binding population is **completed,
nontruncated outputs**, and full telemetry must beat the metadata+length
black-box baseline at the same tool budget. Truncation detection is useful, but
it is not evidence of model-internal error awareness.

Freeze detector/policy hashes before creating the decision manifest.

# M36 paired Agents-A1 benchmark

After the M36C result and freeze commits, preregister fresh decision tasks.
Calibration prompts and all M29-M35 decision tuples remain excluded.

## Benchmark composition

Use the existing predeclared power rule to choose N from 192, 240, or 288 with
expected raw operational failures >= 24.

Choose a fixed benchmark decode cap from calibration such that confirmatory
cells have estimated truncation <= .10. Do not include a truncation-heavy cell
in the primary completed-error claim merely to inflate jLens uplift.

Target composition:

- 60-70% mixed completed-error frontier cells;
- 15-20% high-competence anchors;
- 15-20% low-competence but mostly completed anchors;
- a separate small budget-bound secondary set, non-confirmatory, for timeout
  policy measurement.

Freeze the exact checkpoint, vLLM version, telemetry override hash, task
families, generators, split, decode settings, seeds, feature schema, detector
and policy hashes, tool budget, bootstrap seeds, family weights,
non-inferiority margin, and claim rules before decision capture.

## Paired arms

Generate one AWQ original per decision task. Every arm starts from that same
original and capture:

1. `raw_awq`;
2. `black_box_jlens` — competence, finish reason, verifier-first tools;
3. `full_jlens` — AWQ telemetry detector plus verifier-first tools;
4. `count_matched_random`;
5. `tool_on_every_eligible_task`.

No arm may replace a verified-correct original with a failing result.

## Confirmatory questions

- **H1 practical value:** selected jLens policy improves paired verified success
  over raw AWQ with the 95% lower confidence bound strictly above zero.
- **H2 telemetry increment:** on completed, nontruncated outputs, full jLens beats
  black-box jLens and count-matched random at the frozen budget with both lower
  confidence bounds strictly above zero.
- **H3 efficiency:** selected jLens is non-inferior to tool-all within the frozen
  success margin while using significantly fewer tool calls.

Report primary operational results and completed-only results separately. Also
report truncation rescues, wrong-answer rescues, misses, false alarms,
regressions, tool fraction, calls saved, output tokens, model/tool/total
latency, telemetry overhead, and compute per corrected answer.

# Result branches

- H1 + H3 pass: freeze an Agents-A1-AWQ jLens candidate for extended shadow
  evaluation; production remains gated.
- H1 passes and H2 fails: retain black-box jLens and stop claiming router/logit
  telemetry adds incremental value.
- H1 fails: close the Agents-A1 efficacy track without checkpoint shopping or
  post-hoc benchmark changes.
- Stop after the M36 result in every branch and request a fresh operator
  decision.

# Stop conditions and hygiene

Stop immediately on checkpoint/revision mismatch, invalid telemetry, sealed-set
leakage, verifier-first violation, unbounded memory, test failure, privacy or
commit-safety failure, or inability to restore the serving stack.

Do not commit weights, caches, local paths, prompts, outputs, operands, per-task
labels/predictions/scores, token ids/text, raw logits, router tensors, or expert
traces. Public artifacts remain aggregate-only. Candidate outputs stay
candidates; no tool output becomes training data without a future audited
protocol, and production remains gated.