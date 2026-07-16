# steer.md — finalize completed M38E, then resume the architecture-matched Agents-A1 path

`CODEX_AUTOSTEER.md` remains the operating contract. This file is the current
source of truth for milestone selection. It incorporates the complete prior
`steer.md` blob `0c2587359ffc952e44270d5abfe4a3f730a19fd1` and every protocol or
steer addendum incorporated by that blob.

This directive supersedes prior steer only where explicitly stated below. Every
sealed-data, verifier, privacy, provenance, exact-set, cap-escalation, resource,
claim-boundary, retry, production-gating, repository-hygiene, dependency,
cleanup, commit-safety, comparator, nuisance-control, multiplicity, and stop
rule remains binding. No frozen scientific result, task, family, seed,
threshold, verifier, sampling setting, token cap, power gate, model, revision,
quantization, layer, feature, outcome rule, or production gate may be weakened,
retuned, substituted, or inferred.

## Current established state

- Remote head `9050252b3eda9c751e7ba5094c5ffd7c0ad573c1` committed the binding
  addendum
  `docs/STEER_ADDENDUM_2026-07-16_M38E_ORPHANED_POSTCOMPLETION_COMPUTE.md`.
- The latest committed operational observation remains heartbeat
  `c970d7add7c88f019f8eb739cedd9926d5126c5e`: the M38E ledger was
  byte-stable for approximately 30.5 hours, had no open writer, contained
  288/288 official rows, 94 required pilot rows, zero full-band 4096 rows, and
  382 total rows across all 12 frozen cells.
- That heartbeat also reported an M38E-driver-attributable process candidate and
  sustained GPU activity. It halted cleanup under an earlier conservative rule
  rather than signalling any process.
- The old pre-completion instruction in blob `0c258735…` to leave an active M38E
  process untouched is now superseded only for the exact bounded classification
  and cleanup sequence below. It remains binding if any identity, exact-set,
  writer, attribution, or artifact-activity condition cannot be verified.
- M38E is not formally finalized. The outcome
  `m38e_completed_error_frontier_not_found` remains pending the frozen
  finalization audit set. `provenance-blocked` or `inconclusive` remain the only
  narrower admissible terminal alternatives when required evidence cannot be
  verified.
- The dual-RTX-3090 window is not released. Q35Q GPU execution and M39 scientific
  capture remain prohibited until M38E cleanup, finalization, and serving
  restoration pass.
- No Jacobian Lens has been fitted or validated on Agents-A1. No completed-error
  predictor, safe truncation, early exit, causal repair, activation steering,
  route intervention, semantic controller, or production utility is
  established.

## Active milestone — M38E post-completion classification and finalization

The next host-capable cycle must read and execute, in order:

1. `docs/STEER_ADDENDUM_2026-07-16_M38E_ORPHANED_POSTCOMPLETION_COMPUTE.md`;
2. `docs/STEER_ADDENDUM_2026-07-16_M38E_POSTCOMPLETION_SHUTDOWN_AND_FINALIZATION.md`;
3. the frozen M38E protocols, validators, manifests, escalation rules, and
   finalization audit definitions named by those documents.

A process may be classified as `m38e_orphaned_postcompletion_compute` only when
all of the following are verified privately and simultaneously:

1. every ledger row validates against the frozen run identity, task-set digest,
   manifest digest, source commit, model revision, override hash, attempt kind,
   cap, task hash, and duplicate constraints;
2. exact set equality proves that all 288 official keys and every
   deterministically required pilot or full-band escalation key are present,
   with no unknown or extra attempt keys;
3. aggregate counts remain 288 official, 94 pilot, zero full-band 4096, and 382
   total, with all 12 frozen cell paths complete;
4. the ledger has no open writer and is byte-for-byte unchanged during a fresh
   bounded observation interval of at least ten minutes;
5. no authorized M38E task key remains missing under the frozen identities and
   escalation rules; row-count inference alone is insufficient;
6. the active GPU process group is privately attributable by parent-child or
   process-group identity to the top-level M38E driver, not to an unrelated
   server, finalizer, restoration process, or workload;
7. no authorized finalization, artifact, or serving-restoration write is active.

If any condition fails, signal nothing and commit only the narrow aggregate
state `m38e_postcompletion_classification_blocked` plus a public-safe blocker
class. Never commit process identifiers, command lines, host details, paths,
environment values, row evidence, or telemetry.

When every condition passes, the following one-shot sequence is mandatory:

1. record aggregate state `m38e_orphaned_postcompletion_compute`;
2. request graceful termination of the attributable M38E process group once;
3. allow a bounded 120-second teardown interval;
4. reconfirm privately that the ledger remains unchanged and has no writer;
5. if the attributable process group remains, terminate that process group
   forcibly once and record only `m38e_postcompletion_forced_cleanup`;
6. do not restart, resume, repair, retry, extend, or recover uncommitted
   in-memory output; the frozen validated ledger is the sole admissible record;
7. run the complete frozen finalization audit set: exact-set, escalation,
   verifier, provenance, execution-root, dependency/import/loader/native-library,
   model/revision, privacy, resource, cleanup, serving-restoration, and
   commit-safety;
8. commit `m38e_completed_error_frontier_not_found` only if every required audit
   passes;
9. otherwise commit only `provenance-blocked` or `inconclusive`, with the narrow
   aggregate blocker and no fabricated evidence;
10. release the dual-RTX-3090 window only after process cleanup, GPU-memory
    cleanup, Agents-A1 serving restoration, privacy checks, and commit-safety
    all pass.

After this steer is visible, the next operational commit must report exactly one
of these public-safe states:

- `m38e_postcompletion_classification_in_progress`;
- `m38e_postcompletion_classification_blocked`;
- `m38e_orphaned_postcompletion_compute`;
- `m38e_postcompletion_cleanup_in_progress`;
- `m38e_finalization_audits_in_progress`;
- `m38e_completed_error_frontier_not_found`;
- `provenance-blocked`;
- `inconclusive`;
- `host_execution_authority_unavailable`.

Do not return to `m38e_postcompletion_activity_detected`, `awaiting operator`, or
repeated unchanged status-only heartbeats after this source-of-truth update.
`host_execution_authority_unavailable` may be committed once by an agent that
cannot inspect or signal host processes; it does not authorize an indefinite
status loop.

## Program order after M38E closes

The primary technically credible scaling path remains architecture-matched,
exact-gradient feasibility before scientific outcome prediction:

1. finish and formally close M38E without changing its frozen program;
2. complete Q35Q artifact admission using exact immutable revisions and a real
   tokenizer record;
3. run only the frozen one-sequence exact residual-input VJP gate on the official
   Qwen3.5-35B-A3B GPTQ path, then the admitted NF4 fallback if GPTQ backward is
   unsupported;
4. require non-`None`, nonzero, finite, repeatable genuine-autograd VJPs, frozen
   weights, no hidden offload, exact hook/logit parity, admitted kernels and
   placement, and the existing 23.0 GiB-per-3090 / 46.0 GiB-total resource gate;
5. if a path passes, produce the aggregate-only route-regime, backward-cost,
   wall-time, storage, cleanup, provenance, privacy, and commit-safety artifact
   before the frozen eight-sequence micro-fit;
6. preregister any larger selected-layer quantized Qwen3.5 base-model fit before
   capture and use only deterministic horizontal prompt sharding with fp32
   weighted merging and cross-worker agreement smokes;
7. treat each quantized checkpoint as its own mathematical model; never call a
   quantized lens BF16 or call a transferred Qwen3.5 lens Agents-A1-native;
8. test transfer separately with route overlap, route-change frequency, margin
   distributions, identity transport, and standard logit-lens comparators;
9. admit and fit a native quantized Agents-A1 lens only under a separate frozen
   target-artifact and quantization protocol;
10. retain native BF16 Agents-A1 exact VJPs and fitting on admitted high-memory
    hardware as the final reference comparison.

The binding Q35Q documents remain:

- `docs/Q35Q_QUANTIZED_QWEN35_JACOBIAN_PROTOCOL.md`;
- `docs/STEER_ADDENDUM_2026-07-15_Q35Q_ROUTE_REGIME_AND_EXACT_SHARDING.md`.

The binding M39 monitoring design remains independent of Q35Q engineering and
must not borrow M38E or Q35Q outcomes, rows, difficulty observations, selected
features, layers, or thresholds. M39 may launch only after M38E is formally
closed and its complete launch amendment is committed. It must preserve:

- strict monitoring/control separation;
- fresh forward-only populations and preregistered power, nuisance,
  multiplicity, parity, provenance, privacy, and resource gates;
- train-fold-only nuisance residualization or an equivalent nested conditional
  comparison;
- behavioral self-assessment, router, confidence, and non-telemetry comparators;
- at most the separately admitted temporal hidden-state dynamics block;
- observation-only executed-route telemetry, including margins, loads,
  transitions, and entropy where available;
- no counterfactual routing, router updates, retries, tool invocation,
  truncation, early exit, intervention, or production control.

The binding M39 document remains:

- `docs/STEER_ADDENDUM_2026-07-15_M39_METACOGNITION_TEMPORAL_AND_EARLY_EXIT_BOUNDARY.md`.

## Exact-gradient and MoE claim boundary

An exact sparse-MoE VJP means the local autograd derivative through the executed
top-k route regime. It does not establish derivatives across counterfactual
expert assignments. Straight-through estimators, finite differences, detached
dequantize/requantize paths, fake gradients, manually substituted derivatives,
or route estimators may not be described as exact Jacobians.

Executed router margins, loads, transitions, entropy, confidence, hidden-state
dynamics, and behavioral self-assessment remain candidate monitoring features
until independently validated. They do not establish causality, safe stopping,
repair, or production utility.

## Privacy, production, and completion boundary

Treat the repository as publicly visible. Commit only aggregate states and
public repository object identities. Never commit raw tasks, corpus text,
prompts, answers, outputs, retrieved context, token IDs or text, hidden states,
activations, expert identities or outputs, routes, telemetry arrays, Jacobians,
VJPs, lens matrices, per-example scores or predictions, process evidence, model
weights or artifacts, caches, local paths, environment values, credentials, or
secret-linked provenance.

Stop on identity mismatch, dirty source provenance, exact-set failure,
unsupported backward, detached/zero/nonfinite gradients, approximate gradients
represented as exact, parity failure, hidden offload, model or quantization
substitution, device-placement mismatch, kernel mismatch, OOM, resource breach,
instability, artifact corruption, cleanup failure, serving-restoration failure,
privacy failure, or commit-safety failure.

No M38E, Q35Q, M39, Jacobian Lens, router-telemetry, semantic-workspace,
completed-error-prediction, truncation, early-exit, intervention, or production
claim is complete until its own preregistered gates pass and the corresponding
aggregate finalization commit is present. The research program is not complete
at this steer.