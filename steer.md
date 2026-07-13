# steer.md — close the M38E smoke-identity and explicit task-provenance false-pass paths before launch

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `dfcade72cf88181b3b27539a0e21871e587fc459` only where explicitly
amended below. The complete M36T interpretation, M38E protocol corrections,
sealed-data rules, verifier rules, privacy rules, resource limits, claim
boundaries, production gates, and stop conditions in that steer remain binding
by incorporation. No frozen result may be re-evaluated or tuned, and no M38E
task, family, band, seed, count, threshold, verifier, output-cap rule, power
gate, or production gate may be weakened.

## Current established state

- Remote head before this steer was
  `18f861e296b29912acf668df9ea7ec46c9bb3b76`.
- M36T remains interpreted exactly as recorded in steer `dfcade7`: T-H3 is
  established only as verifier-backed adaptive tool/compute allocation on the
  frozen deterministic population. T-H1 and T-H2 are not established. This is
  not evidence that router telemetry, hidden states, semantic readouts, or a
  Jacobian Lens caused the gain.
- M37J-C finalized with the frozen outcome
  `agents_a1_semantic_bridge_feasibility_blocked` at commit
  `0339c80044598a1cd55ad19a1f487adc7aba2b49`. Seven of eight gates passed:
  all-rank install conformance, dispatch identity, readout conformance,
  enabled-leg divergence, the 44 GiB resource gate, the 1.50x overhead gate,
  and cleanup. The disabled-path parity count gate failed: 11 of 16 prompts
  differed against the frozen absolute allowance of 7. The observed 11/16 rate
  matching the earlier 5/8 baseline is descriptive only. It does not convert
  the blocked result into a pass and does not authorize a rerun or a gate edit.
- M37J-C measured 40.04 GiB combined peak and 1.313x median generation
  overhead. These observations support continued technical work on a fresh
  protocol, but they do not establish semantic correctness, error prediction,
  causal attribution, safe stopping, intervention value, or production use.
- M38E pre-outcome hardening landed at
  `18f861e296b29912acf668df9ea7ec46c9bb3b76`; the commit reports 344 green
  tests, commit-safe clean, and zero official rows. The 2,048-to-4,096 cap
  escalation, exact Fraction gates, official-row provenance, and eligible-band
  counting changes are retained.

## Block M38E smoke and official launch on two remaining provenance defects

Source review of `18f861e` found two pre-outcome false-pass paths. No M38E
smoke or official row may be generated from that commit.

### 1. Smoke rows are currently indistinguishable from official rows

The smoke path writes to a separate file but calls capture with
`attempt_kind="official_2048"` and the same run identity used by the official
path. The test suite constructs an artificial `smoke_2048` row and proves that
such a marker is rejected, but the actual smoke implementation never emits
that marker. A smoke row copied, concatenated, redirected, or otherwise placed
in the official ledger can therefore satisfy `validate_rows` as an official
row when source and task identity match. This violates the frozen requirements
that smoke and official rows have zero shared rows, zero resume interaction,
and a named refusal path.

Correct this without changing any scientific setting:

- Give every smoke row an explicit nonofficial identity, including at minimum
  `run_kind="m38e_driver_smoke"` and an `attempt_kind` that cannot be accepted
  by the official ledger, such as `smoke_2048`.
- Give the official rows an explicit `run_kind="m38e_official_dev"` and require
  exact equality during resume.
- Make the official validator reject every missing, unknown, smoke, or foreign
  run-kind value before engine construction.
- Keep the smoke ledger physically separate, but do not rely on path separation
  as the identity boundary.
- Validate any existing smoke ledger before reuse. Foreign source commits,
  stale run ids, changed task hashes, duplicates, malformed rows, wrong caps,
  or rows outside the exact requested smoke subset must block. They may not be
  silently skipped and counted as a successful smoke.
- A smoke aggregate must report rows actually generated or exact-validated for
  that smoke identity. It may not report `len(plan)` merely because stale keys
  were present.

### 2. The ordered task identity does not explicitly bind seed and index

The current `task_identity()` records task id, family, band, prompt hash, and
answer hash. The task id encodes the index and the generator source hash covers
`M38E_SEED`, but the frozen steer required the ordered digest and each private
row to bind the index/seed identity explicitly rather than infer it from a
string convention.

Correct this without regenerating or changing any task:

- Add an explicit integer `task_index` to generated task metadata and to every
  row identity.
- Add an explicit stable generator seed identifier, for example
  `generator_seed_id="m38e-dev-v1"`, to the run identity, task-set digest, and
  each private row. Do not expose raw prompt or answer content.
- Require exact equality for both fields on resume.
- Recompute the pre-outcome run identity and technical amendment after the
  implementation commit. Because zero official rows exist, this is a legal
  pre-outcome provenance correction, not a scientific change.

## Required tests before any M38E execution

Add deterministic tests proving all of the following:

1. The real smoke capture path emits smoke-marked rows, not
   `official_2048` rows.
2. An actual smoke row inserted into the official ledger is rejected even when
   task id, hashes, source commit, model revision, and output cap otherwise
   match.
3. Missing or unknown `run_kind` values block.
4. A stale, foreign, duplicate, malformed, cross-cap, or out-of-subset smoke
   ledger blocks before engine construction.
5. A smoke followed by an official run under the same source commit causes the
   official path to generate all required official rows and reuse zero smoke
   rows.
6. Smoke completion accounting cannot be satisfied by stale existing keys or
   row count alone.
7. `task_index` and `generator_seed_id` are included in the ordered task-set
   digest and every row; changing either blocks resume.
8. The official ledger still rejects unknown, duplicate, extra, missing,
   tampered, cross-cap, and malformed rows and still uses exact-set completion.
9. The existing deterministic cap-pilot, exact-denominator, eligible-band,
   privacy, and frontier-completeness tests remain green.
10. All public artifacts pass the recursive aggregate-only audit and
    `check_commit_safe.py`.

Commit the implementation, tests, and a replacement aggregate-only M38E
technical amendment. The amendment must state that the correction is
pre-outcome, that zero official rows existed, and that no task content,
scientific setting, threshold, family, band, cap rule, verifier, or gate
changed.

## Execution order

1. Do not launch the M38E driver smoke or official sweep from `18f861e`.
2. Implement the two provenance corrections above offline.
3. Run the full private-safe test suite and commit-safety audit.
4. Commit the corrected implementation and aggregate-only amendment, then push
   and verify the exact remote head.
5. Run a separate nonofficial driver smoke. Verify its rows are smoke-marked,
   its subset is exact, and the official ledger remains absent or byte-for-byte
   unchanged.
6. Restore and verify stock Agents-A1 serving after the smoke if the local
   harness requires a service window.
7. Launch the official M38E development sweep exactly once. Resume only under
   the exact validated official run identity.
8. Execute every frozen 2,048 band and every triggered deterministic 4,096
   pilot/full-band path. Never mix caps in a primary band estimate.
9. If the frontier gates fail, commit only the aggregate
   `m38e_completed_error_frontier_not_found` result and stop that branch.
10. If the gates pass, fit and freeze transparent comparators only on eligible
    completed, nontruncated development rows; complete the preregistered power
    calculation; commit the sealed manifest before generating sealed outcomes.
11. Stop after the M38E result for operator-level scientific interpretation.
    Do not promote a policy automatically.

## Agents-A1 scaling and research scan

- As of 2026-07-13, the official InternScience Hugging Face organization still
  lists only the 35B Agents-A1 BF16/FP8/GGUF variants. The official repository
  still says the 4B model is coming, but no official 4B Agents-A1 checkpoint is
  available. Do not substitute Agents-K1, an unofficial distillation, or a
  different model under the Agents-A1 name.
- The credible near-term full-model path remains observation-only telemetry on
  the pinned 35B runtime plus M38E's verifier-backed incremental prediction
  test. Full backward/Jacobian fitting remains blocked by the official smaller
  checkpoint not being released and by the unchanged local fitting-memory
  ceiling.
- PUMA (`arXiv:2605.17672`, `giovanni-vaccarino/PUMA`) is relevant only as a
  future verified stopping comparator. Its public repository currently states
  that the released implementation is offline and that the online version is
  still being prepared. It does not justify semantic-only early exit.
- Hidden Error Awareness (`arXiv:2605.09502`) supports diagnostic hidden-state
  prediction while explicitly separating it from successful intervention.
- When Are Experts Misrouted? (`arXiv:2605.07260`) supports testing router
  telemetry empirically but shows standard routes can be least informative on
  fragile reasoning tokens.
- The Myth of Expert Specialization in MoEs (`arXiv:2604.09780`) reinforces that
  expert identities should not be assigned human semantic meaning and that
  prompt-level routing does not reliably predict rollout routing.
- IG-Lens (`arXiv:2606.29693`, `anhnda/IGLens`) is a lightweight additive
  probability-attribution comparator with no backward call. It is not a
  Jacobian Lens, and its current public repository is a minimal implementation.
  Evaluate it only in a fresh preregistered comparator study after M38E.
- No actionable r/LocalLLaMA implementation lead was found. Reddit remains a
  lead source only and cannot alter protocol or claims without primary-source
  verification.

After M38E, a fresh M37J-D protocol may characterize disabled-path
nondeterminism using an independently calibrated, prompt-count-aware parity
criterion or a deterministic backend. It must be preregistered before new live
outputs and must preserve M37J-C as blocked. Do not retroactively normalize the
11/16 result, reuse its prompts for threshold calibration and evaluation, or
relax its frozen gate.

## Privacy and production boundary

GitHub currently reports this repository as public. Treat every committed byte
as externally visible. Never commit private prompts, answers, operands,
outputs, token text or ids, per-task labels or predictions, raw telemetry,
hidden states, activations, gradients, Jacobians, lens matrices, model weights,
caches, stack traces, local paths, private task ids, or cap-pilot membership.
Public artifacts remain aggregate-only and must pass `check_commit_safe.py`.

Stop on dirty or changed source provenance, model revision mismatch, task-set or
row mismatch, smoke/official contamination, unsupported resume, cap-ledger
mixing, incomplete escalation, malformed counters, verifier bypass, non-finite
values, rank disagreement, cleanup failure, serving restoration failure,
privacy failure, resource-gate breach, or repeated worker failure.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, semantic monitor, or early-exit rule is authorized for
production by this directive.
