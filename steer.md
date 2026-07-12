# steer.md — close M36 completed-error track; run M36T pre-truncation routing; continue M37J-A

`CODEX_AUTOSTEER.md` remains the operating contract. This file is the current
binding directive. Older M36 benchmark instructions are superseded where they
conflict with this steer.

## Established state

M36V remains complete and sealed on the exact Agents-A1 AWQ checkpoint.
Do not repeat it.

M36C adaptive calibration completed at 23:03 UTC with the protocol-valid outcome
`completed_failure_frontier_not_found`:

- 115 completed-correct rows;
- 0 completed-incorrect rows;
- 81 `truncated_budget` rows;
- 145 new captures in the adaptive run;
- 0 completed-failure families;
- 0 mixed completed-error cells.

This does **not** establish that Agents-A1 never produces wrong completed answers.
It establishes only that the frozen M36C task families, strata, checkpoint,
runtime, and decode policy did not produce the completed-error population needed
for the planned detector benchmark. Every observed operational failure in M36C
was decode-budget truncation.

M37J Phase 0 passed all seven V100 feasibility gates. Its pre-fit manifest was
committed before fitting, and the M37J-A fit is allowed to continue on the V100.
Nothing from M37J is an Agents-A1 result.

## Immediate closeout of M36C

At the next safe boundary:

1. fetch the remote default branch and reread this steer;
2. restore and verify normal Agents-A1 serving;
3. commit the already-written aggregate M36C result and frontier artifacts;
4. record the exact scoped finding above in STATE/findings;
5. preserve all private rows unchanged;
6. do not fit a completed-error detector from zero positive examples;
7. do not create or run the superseded M36 raw-vs-jLens completed-error manifest;
8. do not post-hoc shop for a harder task set under the M36 claim.

The old M36-H1/H2/H3 efficacy questions are closed as **not testable on the
frozen M36C population**, not passed and not falsified. Router/logit telemetry has
not yet established incremental completed-error prediction on Agents-A1.

# M36T — pre-truncation prediction and budget-aware routing

M36T is a new, narrower operational study. Its question is:

> From an early, observation-only prefix of an Agents-A1 generation, can jLens
> predict whether the run will finish within the normal decode budget and use
> that prediction to choose `continue` versus `trusted tool` more efficiently
> than metadata, ordinary confidence signals, or random routing?

This is a truncation/compute-allocation claim only. Do not describe it as
hallucination detection, hidden error awareness, or completed-answer repair.

## Phase 0 — feasibility from existing calibration only

Use only aggregate/cell-level M36C results to identify candidate cells. Before
new capture, require:

- at least two task families with useful budget variation;
- primary development label prevalence between .20 and .80 for
  `needs_more_than_512_tokens`;
- most long-cap completions verifiable by the existing deterministic verifier;
- no cell selected solely because it makes jLens look favorable.

If those conditions cannot be met from the frozen M36C evidence, commit
`m36t_budget_frontier_not_identifiable` and close M36T. Do not manufacture a
benchmark.

## Phase 1 — prefix capture and development

Create fresh, disjoint, deterministic tool-checkable tasks. Exclude all M29-M36C
operands and prompts. Use a committed generator seed and task-family mix.

Run one uninterrupted greedy Agents-A1 generation per task with a 2,048-token
ceiling. From that single run, record private prefix snapshots at fixed decode
steps 128, 256, and 384 and the final finish state. The **primary decision point
is step 256**. The 128/384 points are secondary lead-time analyses.

A single long run defines these outcome classes without rerunning the model:

1. verified completion by 512 tokens;
2. verified completion from 513-1,024;
3. verified completion from 1,025-2,048;
4. still truncated, malformed, or verifier-failing at 2,048.

Do not use any feature computed after the decision checkpoint to predict that
checkpoint's label. Do not expose prompt text, generated text, token ids, raw
routes, tensors, or per-task predictions publicly.

Use a bounded development set sufficient to freeze the feature schema,
checkpoint, detector, tool budget, and label definition. Development tasks are
never sealed decision data.

Freeze these prefix comparators:

1. `metadata_only` — family/stratum and prompt-length metadata;
2. `metadata_plus_logprob` — metadata plus prefix token-confidence summaries;
3. `metadata_plus_router` — metadata plus prefix router summaries;
4. `full_prefix_telemetry` — all approved prefix logprob and router summaries.

The full model may be simple: calibrated logistic regression, nearest centroid,
or another already-used transparent classifier. No large learned head, hidden
state capture, or post-hoc feature search is authorized.

## Phase 2 — preregistered paired benchmark

Commit the decision manifest **before** generating or opening decision outcomes.
Freeze:

- exact checkpoint and revision;
- vLLM and telemetry override hashes;
- task generators, families, cell mix, and seeds;
- 2,048-token source-run ceiling;
- primary 256-token decision point;
- 512-token normal budget;
- feature schema and detector hashes;
- tool-call budget chosen only on development/calibration data;
- bootstrap seeds, metrics, confidence intervals, and stop rules.

Use at least 192 fresh decision tasks if the predeclared power check supports it.
If expected positive labels are below 24, stop before capture and report the
power failure.

Every policy arm is evaluated counterfactually from the same single source run:

1. `normal_512` — no tool, generation limited to the first 512 tokens;
2. `metadata_policy` — metadata/logprob baseline routes selected tasks to tool at
   step 256, otherwise continues to 512;
3. `full_jlens_policy` — full prefix telemetry routes at the identical frozen
   tool-call budget;
4. `count_matched_random` — same number of tool calls;
5. `long_decode_2048` — no tool, accuracy/compute ceiling;
6. `tool_all` — deterministic-tool ceiling, reported but not a realistic budgeted
   comparator.

A trusted tool result may replace the model result only when the verifier accepts
the tool result. No arm may turn a verified-correct answer into a failing one.

## Confirmatory M36T questions

- **T-H1 prefix prediction:** on the sealed set, `full_prefix_telemetry` improves
  balanced accuracy and average precision for `needs_more_than_512_tokens` over
  `metadata_plus_logprob`, with both paired 95% lower confidence bounds > 0.
- **T-H2 budgeted routing:** at the exact same frozen tool-call count,
  `full_jlens_policy` improves verified success over `metadata_policy` and
  `count_matched_random`, with both paired lower bounds > 0.
- **T-H3 compute efficiency:** `full_jlens_policy` is non-inferior to
  `long_decode_2048` within an absolute verified-success margin of .02 while
  using significantly fewer model output tokens, with the paired token-saving
  lower bound > 0.

Report prediction metrics, completion-by-budget curves, verified success,
truncation rescues, misses, false alarms, tool fraction, model tokens, model/tool
latency, total latency, telemetry overhead, and compute per rescued completion.

If T-H1 fails, do not claim internal telemetry adds value; retain only any
supported metadata policy. If T-H2 fails, close budgeted routing as not
established. If T-H3 fails, report that long decoding remains the better policy.
Stop after the M36T result commit and request an operator decision.

# M37J-A — continue observation-only Jacobian-lens pilot

Do not interrupt a healthy checkpointed fit merely to adopt this steer. Finish
the current atomic fit unit, record the new steer SHA, and continue under the
already-committed M37J manifest and protocol.

After fitting:

1. validate lens readout and forward invariance;
2. commit the aggregate fit/validation result;
3. run the frozen 192-task observation-only semantic-workspace evaluation;
4. test J-H1/J-H2 exactly as preregistered;
5. do not begin temporary intervention unless J-H1 or J-H2 passes;
6. stop on the first negative or blocking branch.

No permanent weight edits, exported altered checkpoints, safety bypasses, or
production behavior changes are authorized.

# Heartbeats and hygiene

Continue pushed 30-minute heartbeats while M36T or M37J is active. Each heartbeat
must fetch and compare the remote `steer.md`, report aggregate progress, and
verify its pushed SHA is visible remotely.

Stop immediately on checkpoint mismatch, sealed-data leakage, invalid prefix
alignment, post-checkpoint feature leakage, verifier-first violation, numerical
instability, unbounded memory, privacy failure, or inability to restore serving.

Never commit prompts, outputs, operands, token ids/text, per-task labels or
predictions, raw logits, router tensors, expert traces, residual activations,
gradients, Jacobians, lens matrices, steering vectors, weights, caches, or local
paths. Public artifacts remain aggregate-only. Production remains gated.