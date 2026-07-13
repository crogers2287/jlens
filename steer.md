# steer.md — interpret M36T correctly and close M38E provenance, resume, and cap-escalation false-pass paths before launch

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `04920b0c40223f7559d3de99b5d6a0c6a2c7a2bf` only where explicitly
amended below. Every sealed-data, verifier, privacy, resource, claim-boundary,
production, and repository-hygiene gate from prior steers remains binding by
incorporation. No frozen M36T result may be re-evaluated or tuned, no in-flight
M37J-C scientific setting may be changed, and no M38E threshold, family, band,
seed, task count, verifier, or production gate may be weakened.

## Current established state

- M36T sealed capture completed 192/192 at 2026-07-13T17:11Z after 11.4 hours.
  The authorized evaluator `0285ec3531d40faac286424661f610ade677d3ec`
  ran exactly once after preflight, using verifier-checked deterministic tool
  answers. The aggregate result is committed at
  `3f5f1310753d5d25ec8d75c203bdb205702c8e71`.
- M36T T-H3 is established in its frozen scope: at the 256-token decision point,
  the budget-aware full policy improved verified success over `long_decode_2048`
  by 0.1919 with a 95% lower bound of 0.1346 while saving 716.2 mean model-output
  tokens per task with a lower bound of 618.0. It also beat count-matched random
  routing by 0.1562 with a lower bound of 0.0990.
- M36T T-H1 is not established. Router features improved sealed balanced accuracy
  over metadata by 0.0664 with a lower bound of 0.0040, but the preregistered
  average-precision lower bound was -0.0026, so the dual-bound rule failed.
- M36T T-H2 is not established. Full jLens policy improved verified success over
  metadata routing by only 0.0052 and its confidence interval spans zero.
- The arm means were `normal_512=0.4323`, `metadata_policy=0.9792`,
  `full_jlens_policy=0.9844`, `count_matched_random=0.8281`,
  `long_decode_2048=0.8125`, and `tool_all=1.0000`.
- Stock Agents-A1 serving was restored and verified after M36T, then unloaded for
  the already-authorized M37J-C 16-prompt smoke. At the latest pushed heartbeat
  `2c52b8badac78d2696be258b08b008d34dc69929`, that smoke was running from the
  audited harness and no operational blocker was reported.
- M38E development has not begun. Its frozen 288-task manifest and bounded driver
  are staged behind M37J-C finalization.

## Binding scientific interpretation of M36T

M36T establishes a verifier-backed compute-allocation result, not a Jacobian Lens
or telemetry result.

- The positive claim is limited to this frozen deterministic task population,
  fixed 256-token decision point, fixed tool budget, pinned Agents-A1 runtime,
  verifier-backed tools, and frozen comparators.
- Do not describe T-H3 as evidence that router telemetry, semantic readouts,
  hidden states, Jacobians, or the full jLens feature set caused the gain.
- The metadata policy achieved 0.9792 verified success and the full jLens policy
  achieved 0.9844 at the same budget; T-H2 did not establish an incremental jLens
  benefit. The supported mechanism is routing selected tasks to a trusted solver
  instead of spending a much larger decode budget on every task.
- Do not generalize `tool_all=1.0000` to open-ended agentic work. The M36T tools
  are deterministic solvers for the frozen procedural families and were accepted
  only through the frozen verifier.
- No production policy is authorized. The finding justifies continued research
  on verifier-backed adaptive compute and tool allocation, not deployment.
- M38E is now the critical confirmatory discriminator for the original jLens
  thesis: it must determine whether approved telemetry adds value for genuine
  completed-error detection after simpler metadata and confidence signals.

## Do not disturb the in-flight M37J-C smoke

The current M37J-C smoke must finish or block under the source commit and hashes
recorded at its start.

- Do not interrupt, restart, shorten, retune, pull into, checkout over, or mutate
  the running smoke environment because this steer appeared remotely.
- A newer remote steer commit alone is not a smoke source mismatch. Keep the
  smoke checkout at its start-pinned commit through technical artifact creation,
  cleanup, serving restoration, and finalization. Record this steer SHA
  separately as post-start operator direction if the runbook requires it.
- Finalize only through the existing two-phase gate after exact cleanup and stock
  serving restoration. If any gate blocks, preserve only the aggregate blocked
  artifact, restore serving, and do not rerun without a fresh directive.
- A pass can establish only bounded technical observability of semantic readouts
  on the quantized Agents-A1 runtime with parity, dispatch identity, finite
  values, resource compliance, privacy, cleanup, provenance, and restoration.
  It cannot establish semantic correctness, error prediction, causal attribution,
  safe early exit, intervention value, or production utility.

After M37J-C finalization and verified serving restoration, pull this steer and
apply the M38E corrections below before launching any official M38E development
row.

## Block official M38E development until the staged driver is corrected

The current `src/m38e_dev_sweep.py` does not fully execute the frozen protocol.
It can mix smoke and official rows, resume rows produced under a different model
or source state, accept unknown or duplicate rows, gate on rounded and
completed-only rates, count completed errors from ineligible bands, and declare
frontier failure without executing the preregistered 4,096-token escalation
path. These are pre-outcome conformance defects. Correct them without changing
frozen task content or weakening any gate.

### 1. Separate smoke execution from the official development ledger

- Remove `--limit` from the official-row path or make it write to a distinct
  private smoke file and an aggregate artifact whose `run_kind` is explicitly
  `m38e_driver_smoke`.
- A smoke run may never create, append to, mark complete, or satisfy a gate for
  `m38e_dev_rows.jsonl`.
- The official driver must refuse to start if the official row file contains a
  smoke marker, a different run id, a different manifest digest, or any row not
  proven to belong to the exact official run.
- Tests must demonstrate that a smoke followed by an official run produces zero
  shared rows and zero resume interaction.

### 2. Bind every official row and resume decision to exact provenance

Before engine construction, derive and verify rather than trust caller input:

- the exact full Git source commit;
- the SHA-256 of `src/m38e_dev_sweep.py`, `src/m38e_families.py`,
  `reports/telemetry/m38e_dev_manifest.json`, the capture implementation and
  worker override used by `m36c_adaptive`, and the deterministic verifier source;
- the exact pinned Agents-A1 repository and immutable revision from the frozen
  M36C/M36T configuration;
- the runtime version, tensor-parallel configuration, override hash, sampling
  parameters, and output cap;
- an ordered digest of the complete expected task set, including task id, family,
  band, seed/index, prompt hash, and known-answer hash. Prompt text and answers
  remain private.

For each private row, record the run id, manifest digest, task-set digest, task
identity hashes, exact model revision, source commit, runtime/override hashes,
output cap, and attempt kind. Do not expose these rows publicly.

On resume:

- recompute the expected 288-task set from the frozen generator and require exact
  digest equality;
- require every existing row to match all run-level provenance fields;
- reject unknown task ids, duplicate task ids, duplicate attempts in the active
  cap ledger, missing identity hashes, changed task hashes, model mismatch,
  runtime mismatch, source mismatch, cap mismatch, or malformed rows;
- define completion as exact set equality with the expected task ids, never
  `len(rows) >= len(tasks)`;
- refuse arbitrary `--model-ref` values. A CLI value may only repeat the exact
  frozen model revision and must be checked against it.

Commit an aggregate-only technical amendment containing the hashes and exact
run identity before official capture. It must contain no prompts, answers,
outputs, task ids, telemetry arrays, local paths, or per-task labels.

### 3. Implement the frozen 2,048-to-4,096 cap-escalation rule

The protocol already allows an entire band to move to 4,096 only when truncation
exceeds 0.10 and a bounded pilot shows material reduction. The current driver
never performs that pilot and can therefore issue a false
`m38e_completed_error_frontier_not_found` result.

Freeze and implement this rule before any development outcome is generated:

1. Run the complete frozen 24-task band at 2,048 tokens.
2. If exact truncation is at most 0.10, evaluate the band only at 2,048.
3. If exact truncation exceeds 0.10, order the truncated task ids by
   `SHA256("m38e-4096-pilot-v1:" + task_id)` and select the first eight, or all
   truncated tasks when fewer than eight exist. This ordering is private.
4. Rerun only that deterministic pilot subset at 4,096. Pilot rows are cap-choice
   evidence only and may not enter classifier fitting, band counts, or sealed
   planning.
5. Define material reduction as both: at least half of pilot truncations become
   nontruncated, and at least two pilot tasks become nontruncated.
6. If the pilot passes, rerun all 24 tasks in that band at 4,096 and use only the
   complete 4,096 band ledger for eligibility, development labels, and later
   fitting. Preserve the 2,048 and pilot ledgers separately for aggregate cap
   reporting; never mix caps inside a primary band estimate.
7. If the pilot fails, the band is ineligible because the allowed escalation did
   not materially reduce truncation. Do not expand the sweep or choose another
   pilot subset.

The model, sampling, prompt, verifier, family, band, and task identities must be
identical across cap attempts. Only the output cap changes.

### 4. Make eligibility arithmetic match the frozen wording exactly

- Use integer counts and unrounded rational values for every gate. Round only
  fields displayed in aggregate reports.
- Report both `raw_verified_pass_rate = completed_correct / n` and
  `completed_pass_rate = completed_correct / completed_n`.
- The frozen eligibility phrase is "verified raw pass rate between .20 and .80";
  therefore gate the 0.20–0.80 interval on `raw_verified_pass_rate`, inclusive.
  Do not silently substitute the completed-only denominator.
- Completion and truncation gates use the final single-cap band ledger selected
  by the escalation rule.
- The minimum six completed-correct and six completed-incorrect gates continue to
  use completed, nontruncated rows.
- Count the overall minimum of 48 completed-incorrect examples only from eligible
  bands. Ineligible all-fail, over-truncated, or otherwise invalid bands may not
  satisfy the overall power gate.
- Require at least two distinct eligible families exactly as frozen. Report the
  eligible bands and their family mapping in aggregate only.
- A frontier-not-found outcome is legal only after all 2,048 bands and every
  triggered deterministic 4,096 pilot/full-band path are complete and all row,
  provenance, privacy, and exact-set checks pass.

### 5. Preserve verifier-backed tool-arm integrity for later M38E phases

Before any M38E sealed policy or repair arm is authorized:

- construct actual deterministic tool answers for each eligible procedural
  family;
- pass every tool answer through the same frozen family verifier used for model
  outcomes;
- treat missing tasks, unsupported families, solver exceptions, malformed tool
  answers, or verifier rejection as blocking failures, never automatic success;
- use a dedicated deterministic random-policy seed and exact count matching;
- prohibit correct answers, known answers, verifier outcomes, tool outputs, and
  post-hoc task difficulty from entering prediction features;
- report right-to-wrong regressions explicitly even if the deterministic tool is
  expected to be exact.

This is an implementation prerequisite, not authorization to begin sealed
M38E evaluation. Development eligibility, feature fitting, comparator freeze,
power calculation, and sealed manifest must still occur in order.

### 6. Required tests and prelaunch artifact

Add deterministic tests covering at minimum:

- smoke rows cannot enter or resume the official ledger;
- arbitrary model references and changed source/runtime hashes fail before engine
  construction;
- unknown, duplicate, extra, missing, stale, cross-cap, and malformed rows block;
- exact-set completion cannot be satisfied by row count alone;
- 2,048 bands below the truncation threshold do not escalate;
- off-threshold bands trigger the exact deterministic pilot set;
- pilot pass reruns the whole band at 4,096 and excludes all 2,048/pilot rows from
  primary estimates;
- pilot failure leaves the band ineligible and does not select a second subset;
- raw-pass and completed-pass denominators are reported separately and only raw
  pass is used for the frozen interval gate;
- rounded values cannot change a gate decision;
- completed errors from ineligible bands cannot satisfy the overall minimum;
- frontier-not-found cannot be emitted while any required cap path is incomplete;
- later tool arms construct and verifier-check real tool answers rather than
  assigning success directly;
- all public artifacts pass the recursive aggregate-only privacy audit and
  `check_commit_safe.py`.

Commit the corrected driver, tests, and aggregate-only technical amendment;
run the full private-safe suite; verify the pushed remote head; then launch the
official M38E development sweep exactly once with resumability only under the
validated run identity.

## Execution order

1. Let the already-running M37J-C smoke finish under its start-pinned source and
   execute its existing cleanup, restoration, and finalization path.
2. Restore and verify stock Agents-A1 serving regardless of smoke outcome.
3. Pull this steer and correct M38E offline. Do not issue an official M38E prompt
   until every required test and the technical amendment are committed.
4. Run a separate nonofficial driver smoke that cannot touch official rows.
5. Launch the exact official M38E development sweep, including only the frozen
   cap-escalation paths described above.
6. If the frontier gates fail, commit the aggregate
   `m38e_completed_error_frontier_not_found` outcome and stop that branch.
7. If they pass, fit and freeze the transparent comparators only on eligible
   completed, nontruncated development rows; complete the preregistered power
   calculation; commit the sealed manifest before generating sealed outcomes.
8. Stop after the M38E result for operator-level scientific interpretation. Do
   not promote a policy automatically.

## Research scan and technically credible Agents-A1 scaling path

- The official Agents-A1 repository announced on 2026-07-08 that a 4B model was
  coming in the next few days. The official Hugging Face collection was updated
  on 2026-07-13 but still lists only 35B BF16, FP8, and GGUF variants. The full
  backward/Jacobian path remains blocked by official smaller-checkpoint
  availability and the unchanged 30 GiB fitting ceiling.
- The Agents-A1 report describes a 35B MoE trained on verifier-rich long-horizon
  trajectories averaging roughly 45K tokens. That architecture makes
  verifier-backed compute allocation a credible target, but it does not imply
  that router states or semantic readouts predict correctness.
- `Stop When Reasoning Converges` / PUMA (arXiv:2605.17672,
  `giovanni-vaccarino/PUMA`) combines semantic redundancy with answer-level
  verification. It supports a future verified stopping comparator, not
  semantic-only early exit and not a change to frozen M37J-C or M38E.
- `Hidden Error Awareness in Chain-of-Thought Reasoning` (arXiv:2605.09502)
  reports strong hidden-state error diagnostics while four attempted
  interventions fail. Continue to separate prediction evidence from causal or
  corrective claims.
- `When Are Experts Misrouted?` (arXiv:2605.07260) finds ordinary routes can be
  weak exactly on fragile reasoning tokens. Router telemetry remains an empirical
  feature, not a trusted semantic or route-quality label.
- `The Myth of Expert Specialization in MoEs` (arXiv:2604.09780) reports that
  routing largely reflects hidden-state geometry, prompt-level routing does not
  predict rollout routing, and deep expert activations can look similar across
  unrelated reasoning inputs. Do not assign human semantic meaning to experts.
- `IG-Lens` (arXiv:2606.29693, `anhnda/IGLens`) is a no-backward, additive
  probability-attribution comparator that may be evaluated only in a fresh
  post-smoke protocol. It is not a Jacobian lens and does not establish error
  prediction or safe stopping.
- No actionable r/LocalLLaMA implementation lead was found in the current scan.

The highest-credibility path within the remaining window is therefore:

1. complete the full-model observation-only M37J-C feasibility smoke;
2. execute a contamination-proof M38E completed-error benchmark to test whether
   approved telemetry has incremental predictive value over metadata and
   confidence;
3. treat M36T's established outcome as evidence for verifier-backed adaptive
   tool/compute allocation, not as evidence for jLens internals;
4. only after M37J-C and M38E, preregister a small fresh comparator study of
   standard logit lens versus IG-Lens-style semantic attribution versus router
   telemetry, with verifier-required stopping or routing and explicit
   cross-family shift tests;
5. watch only official InternScience sources for a 4B checkpoint and pin its exact
   immutable revision before any full backward/Jacobian feasibility smoke.

## Stop conditions, privacy, and production boundary

Stop on dirty or changed source provenance, model revision mismatch, task-set or
row mismatch, verifier bypass, official/smoke ledger contamination, unsupported
resume, cap-ledger mixing, incomplete escalation, malformed counters, non-finite
values, rank disagreement, cleanup failure, serving restoration failure, privacy
failure, resource-gate breach, or repeated worker failure.

Never commit private prompts, answers, operands, outputs, token text or ids,
per-task labels or predictions, raw telemetry, hidden states, activations,
gradients, Jacobians, lens matrices, model weights, caches, stack traces, local
paths, private task ids, or cap-pilot membership. Public artifacts remain
aggregate-only and must pass `check_commit_safe.py`.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, semantic monitor, or early-exit rule may be promoted by
this directive.