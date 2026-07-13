# steer.md — close M37J-C smoke gate and restoration holes before live run

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `fe6fcf2f69a30ad60e4dd7f1a02b31d8a817a153` only where explicitly
amended below. Every sealed-data, verifier, privacy, claim-boundary, resource,
production, and repository-hygiene gate from steers `8eb2e9e`, `cccf40a`, and
`fe6fcf2` remains binding by incorporation. No scientific threshold, feature
family, task set, checkpoint, or resource ceiling is relaxed.

## Current established state

- M36T development completed 96/96 with 65 positive and 31 negative labels. Its
  comparators, task sets, decision step, tool budget, hypotheses, and power gate
  remain frozen.
- The 192-task M36T sealed capture is healthy and must not be interrupted. At
  pushed heartbeat `e94fb4c30eb831ebbd3c2084fc7107b2c6039066` it was 49/192,
  producing about 26 rows/hour, with no operational blocker.
- The corrected M36T evaluator at `0285ec3531d40faac286424661f610ade677d3ec`
  remains the only authorized evaluator. Tool answers are constructed from the
  exact private task and accepted only through the frozen verifier.
- M37J-A is closed. Its frozen holdout did not establish completed-error
  prediction and its truncation arm was underpowered. Do not reopen or tune it.
- M37J-C tensor-parallel projection was corrected before live prompts at
  `290e7e8f7ea86a931dcbdd94069f2256006dbec8`; 79/79 tests were green at the
  latest heartbeat. The bridge remains observation-only and inert until enabled.
- The 16-prompt M37J-C smoke driver was staged at
  `90f361deb08e90516ca78cc5bed8260efdda7010`, but it is not authorized to run
  unchanged because its gate-finalization logic is incomplete.
- M38E remains queued behind the M36T sealed window. Do not displace M36T for
  M37J-C or M38E.

## Binding M37J-C smoke-harness correction before any live prompt

The staged smoke driver claims eight mandatory gates, but the implementation can
currently report `outcome: passed` without actually satisfying all eight. This
is an implementation blocker, not a scientific result.

### 1. Restoration gate must be a real boolean gate

`serving_restored_and_verified` is currently stored as a string and the pass
calculation includes only boolean values. Therefore the driver can mark the
smoke passed before normal Agents-A1 serving has been restored or verified.

Correct this before execution:

- The smoke phase may produce only `technical_gates_passed_pending_restore` after
  gates 1–7 pass.
- A separate finalization step must restore the stock serving configuration,
  issue the frozen public-safe verification request, verify normal response and
  process health, and then write gate 8 as the boolean `true`.
- Only that finalizer may write final `outcome: passed`.
- Restore failure, verification failure, or missing finalization must write
  `agents_a1_semantic_bridge_feasibility_blocked` and keep production gated.
- The final aggregate artifact must identify the exact projection commit, smoke
  driver commit, runtime override hash, and restoration verification record.

### 2. Cleanup must be exception-safe

The driver currently has no guaranteed cleanup path. Wrap installation and
execution in `try/finally` so every rank is commanded, in order, to:

1. disable bridge capture;
2. disable telemetry capture;
3. uninstall bridge hooks;
4. uninstall telemetry hooks;
5. release the temporary engine before the external serving restore.

Cleanup RPC results must be checked across all ranks. Any false result, RPC
exception, lingering installed state, or inability to release the engine blocks
the smoke. Cleanup is required even when projection, decoding, telemetry,
privacy, memory, or parity checks fail.

### 3. Dispatch identity must be checked on every tensor-parallel rank

The staged driver currently reads only element `[0]` from
`jlens_fetch_summary`. That is insufficient because mismatch counters are
rank-local.

- Fetch all rank summaries.
- Require `id_mismatch_total == 0` and `dispatch_missed_total == 0` on every rank.
- Require the expected rank count and unique rank identities.
- Record only aggregate maxima/sums and rank-count conformance publicly.
- Any missing rank or nonzero counter blocks the smoke.

### 4. Enforce the exact frozen nondeterminism envelope

The M36V artifact freezes both `margin_prompts: 2` and
`first_divergence_floor: 8`. The staged driver imports the prompt margin but
ignores the floor and instead compares against the baseline minimum divergence
of 13. That does not implement the frozen envelope exactly.

- Read and hash the complete parity-envelope object from the pinned M36V
  artifact.
- For both A-vs-B and B-vs-C, require differing prompts no greater than baseline
  plus the frozen margin and first divergence no earlier than the frozen floor.
- Do not retune the envelope after observing M37J-C outputs.
- Fail preflight if the expected envelope fields or source artifact hash differ.

### 5. Authoritative global readout conformance must not silently select one rank

The staged driver takes the first authoritative readout and ignores any others.
Correct this without changing layers, cadence, top-k, or semantic groups:

- Require at least one authoritative global-vocabulary result for every prompt.
- If multiple ranks receive global logits, require their bounded top-k readouts,
  step indices, finiteness flags, and semantic-group scores to be identical.
- Require non-authoritative ranks to emit no token ids or semantic scores.
- Require identical projection-call counts and captured-slot counts across all
  ranks for each prompt.
- Publish only aggregate conformance booleans and counts, never token ids or
  per-prompt readouts.

### 6. Add tests and commit before execution

Add synthetic tests covering:

- restoration represented as a required boolean and excluded-until-finalized;
- technical-pass/pending-restore versus final-pass state transitions;
- exception-path cleanup and all four cleanup RPCs;
- rank-local dispatch mismatch on a nonzero rank causing failure;
- missing or duplicate rank summaries causing failure;
- exact use of `first_divergence_floor: 8` from the pinned envelope;
- multiple authoritative ranks agreeing and disagreeing;
- non-authoritative rank leaking ids causing failure;
- restoration failure preserving the blocked outcome.

Commit the corrected driver, tests, and an aggregate-only technical amendment
before any live M37J-C prompt. Run the full private-safe test suite and
`check_commit_safe.py`; verify the pushed remote SHA.

This correction changes only conformance, cleanup, and finalization needed to
execute the already-frozen feasibility smoke. It does not authorize new prompts,
semantic words, layers, positions, cadence, top-k, thresholds, route edits,
activation interventions, or outcome-driven tuning.

## M36T sealed completion remains binding

Continue capture unchanged. After all 192 rows are durably present, run only the
corrected evaluator exactly once:

- execute task/row identity, task-file SHA-256, checkpoint, schema,
  feature-timing, uniqueness, and token-ceiling preflight before scoring;
- construct deterministic tool output from each private task and require the
  frozen verifier to return `pass`;
- preserve all six arms, rankings, token accounting, caps, hypotheses, paired
  bootstrap procedure, and dedicated random-policy seed;
- on any preflight or verifier failure, commit only the aggregate blocker and
  stop before opening hypotheses;
- do not tune on the sealed result.

## Research scan and scaling boundary

- The official PUMA repository is now verifiable, but the released code is the
  offline pipeline; its online early-exit implementation is explicitly not yet
  released. PUMA also couples semantic redundancy with answer-level
  verification. It is future comparator evidence, not code to insert into the
  frozen Agents-A1 smoke or a basis for unverified early stopping.
- Recent MoE work reports that prompt-level routing does not reliably predict
  rollout-level routing and that deeper expert activation can look similar for
  semantically unrelated reasoning inputs. Router statistics remain empirical
  features, not human-interpretable expert semantics.
- Recent early-exit evaluation reports lower layer-exit potential for MoEs than
  dense transformers. This further blocks any production early-exit claim from
  the current observation-only work.
- Counterfactual-routing results remain evidence that fragile reasoning tokens
  may contain router-reachable alternatives, but do not authorize route edits in
  Agents-A1.
- No verified official Agents-A1 4B checkpoint and no actionable r/LocalLLaMA
  implementation lead were found. The full-Jacobian Agents-A1 path remains
  blocked by checkpoint availability and the unchanged 30 GiB fit gate.

The technically credible near-term scale path remains:

1. finish M36T sealed capture and run its corrected evaluator once;
2. correct the M37J-C smoke harness before any live prompt;
3. restore normal Agents-A1 serving and verify it;
4. run the bounded 16-prompt observation-only bridge smoke;
5. finalize pass only after post-smoke serving restoration succeeds;
6. release the dual-3090 window to M38E under its frozen protocol.

M37J-C can establish only that bounded semantic readouts are observable on the
full Agents-A1 runtime within parity, dispatch-identity, numerical, memory,
latency, privacy, cleanup, and restoration gates. It cannot establish a Jacobian
lens on Agents-A1, error prediction, causal attribution, expert semantics, route
quality, safe early exit, intervention value, or production utility.

Stop on checkpoint mismatch, task/row mismatch, task-hash mismatch, feature or
label leakage, verifier bypass, tensor-parallel collective mismatch, shard-local
readout, cross-rank readout disagreement, invalid telemetry alignment, numerical
instability, cleanup failure, restoration failure, privacy failure, resource-gate
breach, or repeated worker failure.

Never commit private prompts, outputs, operands, token text or ids, per-task
labels or predictions, raw telemetry, hidden states, activations, gradients,
Jacobians, lens matrices, model weights, caches, or local paths. Public artifacts
remain aggregate-only and must pass `check_commit_safe.py`.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, or early-exit rule may be promoted by this directive.
