# steer.md — finish M36T, then run M38E hard completed-error benchmark

`CODEX_AUTOSTEER.md` remains the operating contract. This is the current binding
directive. The detailed M36T protocol from steer commit `79878ab` remains binding
except where updated below.

Read and follow:

`docs/M38E_HARD_COMPLETED_ERROR_PROTOCOL.md`

## Established state

- M36V is complete and sealed.
- M36C is closed: 115 completed correct, 0 completed incorrect, and 81
  token-budget truncations. The completed-error study was not testable on that
  population.
- M36T Phase 0 passed with four candidate families and pooled positive prevalence
  0.604.
- M36T Phase 1 commit `97b62c590d9e06593241285719498634362bc4e7`
  launched 96 fresh tasks with one uninterrupted 2,048-token source run and
  prefix snapshots at 128, 256, and 384 tokens.
- M37J produced a finite fitted lens but used 31.18 GiB, exceeding its frozen
  30.0 GiB memory gate. No semantic result is established.

## Immediate directive

Do not interrupt a healthy M36T capture. Finish the current atomic task, flush
private progress, record this steer SHA, and continue using the committed task
order, feature alignment, labels, and resume rules.

M36T retains first priority on the dual-3090 host. CPU-only implementation and
unit tests for M38E may proceed in parallel, but live M38E model sweeps begin only
at a safe M36T stop or after the M36T result.

## M36T completion

Complete the 96-task development capture and freeze these step-256 comparators:

1. metadata only;
2. metadata plus token confidence;
3. metadata plus router summaries;
4. full approved prefix telemetry.

No feature created after token 256 may enter the primary prediction. Token 128
and 384 remain secondary lead-time analyses.

If development contains fewer than 24 positive or 24 negative labels, commit the
power failure and close M36T. Otherwise freeze the classifier, calibration,
feature schema, tool-call budget, seeds, metrics, hashes, and claim rules before
creating the fresh sealed manifest.

Test the existing M36T questions exactly as preregistered:

- full prefix telemetry versus metadata plus confidence;
- full jLens routing versus metadata routing and count-matched random at the same
  tool-call count;
- full jLens versus long 2,048-token decoding for verified success and token use.

Stop after the M36T result commit and record the scoped conclusion.

# M38E — completed-error baseline on harder tasks

M38E is a separate reliability track. It must find task families where Agents-A1
usually completes, but produces both objectively correct and objectively wrong
answers in meaningful numbers.

Do not hand-pick individual known failures. Use aggregate development results to
select a family and difficulty band, then create a fresh disjoint sealed set.

## Phase 0 — implementation

Implement and unit-test deterministic generators and verifiers for candidate
families listed in the M38E protocol. Prefer fresh procedural modular arithmetic,
symbolic algebra, logical deduction, and constrained-ordering tasks. Executable
code tasks may be used when an already-local public dataset and deterministic
unit tests are available. Public MATH/AIME-style material is secondary transfer
evidence only.

Record exact generator/data identity, revision, seed, verifier hash, and usage
basis. No silent dataset substitution.

## Phase 1 — bounded difficulty sweep

Commit the development manifest before capture. Run 24–32 fresh tasks per
family/difficulty band with enough output headroom that primary failures are
completed wrong answers rather than timeouts.

Eligible bands require:

- completion rate >= .90;
- truncation rate <= .10;
- raw verified pass rate from .20 through .80;
- at least 6 completed correct and 6 completed incorrect development examples;
- an objective verifier;
- sufficient unseen task space for a sealed holdout.

Require at least two eligible families and at least 48 completed incorrect
examples across development. If the bounded sweep cannot find that population,
commit `m38e_completed_error_frontier_not_found` and stop. Do not keep expanding
or choose individual questions for favorability.

## Phase 2 — frozen sealed benchmark

Follow `docs/M38E_HARD_COMPLETED_ERROR_PROTOCOL.md` in full. Commit the sealed
manifest before generating or opening outcomes. Choose N from 192, 240, or 288
using the frozen power rule and require at least 24 expected completed errors.

Primary population: completed, nontruncated answers only.

Freeze transparent comparators:

1. metadata only;
2. metadata plus output length and finish reason;
3. metadata plus token-confidence summaries;
4. metadata plus router summaries;
5. full approved jLens telemetry.

The correct answer and verifier result are labels only. They may not enter a
prediction feature.

Test whether full jLens improves completed-error prediction beyond metadata plus
confidence and router-only signals. On tasks with a trusted deterministic solver,
also test budget-matched repair routing against metadata and random selection.

Stop after the M38E result commit and request an operator decision.

# M37J — one refit inside the frozen memory gate

Do not retroactively raise the 30.0 GiB gate. Preserve the 31.18-GiB fit as a
blocked attempt with no semantic claim.

Commit one manifest amendment changing only `dim_batch` from 8 to 4. Keep the
same pilot model, corpus, sequence length, seeds, source/target layers,
`skip_first`, checkpoint cadence, and Jacobian-lens revision.

Refit once on the V100. If peak reserved memory is <= 30.0 GiB and Jacobians are
finite, perform the frozen validation and observation-only M37J-A evaluation. If
memory still exceeds the gate or validation fails, close M37J as blocked. Do not
continue tuning configurations.

## Scheduling and hygiene

Dual-3090 priority:

1. finish M36T;
2. run M38E development and sealed benchmark only if its eligibility gates pass.

M37J uses the separate V100 and may run in parallel.

Continue pushed 30-minute heartbeats while any track is active. Every heartbeat
must fetch and compare remote `steer.md`, report aggregate progress, and verify
that its pushed SHA is visible remotely.

Stop on checkpoint mismatch, sealed-data leakage, feature leakage, invalid
telemetry alignment, verifier misuse, numerical instability, repeated worker
failure, privacy failure, or inability to restore serving.

Never commit private prompts, outputs, operands, token text or ids, per-task
labels or predictions, raw telemetry, activations, gradients, Jacobians, lens
matrices, model weights, caches, or local paths. Public artifacts remain
aggregate-only. Production remains gated.