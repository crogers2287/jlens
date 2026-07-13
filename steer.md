# steer.md — close remaining M37J-C false-pass paths before live Agents-A1 smoke

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `821e430e8abf9ee748ae2c0ed91c986ac9e7cce4` only where explicitly
amended below. Every sealed-data, verifier, privacy, claim-boundary, resource,
production, and repository-hygiene gate from steers `8eb2e9e`, `cccf40a`,
`fe6fcf2`, and `821e430` remains binding by incorporation. No scientific
threshold, feature family, prompt, task, checkpoint, cadence, top-k value,
resource ceiling, or production gate is relaxed.

## Current established state

- M36T development remains frozen at 96/96 with 65 positive and 31 negative
  labels. Its task sets, comparators, decision step, tool budget, hypotheses,
  verifier, power gate, and evaluator remain unchanged.
- At pushed heartbeat `2c119ef74c7e99c55125f158601a2a49e32409f0`,
  M36T sealed capture was healthy at 78/192, approximately 30 rows/hour, with
  52/52 fresh core tests and no operational blocker. Do not interrupt, split,
  migrate, or tune this capture.
- The only authorized M36T evaluator remains
  `0285ec3531d40faac286424661f610ade677d3ec`. It may run exactly once after all
  192 sealed rows are durably present and its full preflight succeeds.
- M37J-A remains closed: completed-error prediction was not established and the
  truncation arm was underpowered. Do not reopen or tune it.
- M37J-C tensor-parallel projection remains pinned to
  `290e7e8f7ea86a931dcbdd94069f2256006dbec8`. It is observation-only, bounded,
  and inert until explicitly enabled.
- Smoke-harness conformance commit
  `ed056c0b4426124400b6658b12bb91187401dc88` correctly added two-phase
  finalization, ordered cleanup, all-rank summaries, the frozen divergence
  floor, and authoritative-readout agreement. No live M37J-C prompt has run.
- A fresh source audit of that committed implementation found additional paths
  by which the smoke could miss a failure or accept an empty result. These are
  implementation blockers, not scientific outcomes.
- M38E remains queued behind the M36T sealed window and the bounded M37J-C
  feasibility smoke. Do not displace M36T.

## Binding corrections before any live M37J-C prompt

### 1. Dispatch identity must be checked for every prompt, not only the last

The current `run_leg` resets telemetry before each enabled prompt, but
`phase_smoke` fetches `jlens_fetch_summary` only once after all 16 prompts.
Therefore the identity gate currently observes only the final prompt; a routing
mismatch or missed dispatch on prompts 1–15 can be erased by the next reset.

Correct this without changing prompts or decoding:

- After each enabled prompt, fetch `jlens_fetch_summary` on every tensor-parallel
  rank before any subsequent reset.
- Require exactly the frozen rank identity set `{0, 1}` for every prompt, not
  merely two distinct arbitrary values.
- Require `id_mismatch_total == 0` and `dispatch_missed_total == 0` on every rank
  for every prompt.
- Require the expected prompt count, rank count, unique rank identities, and
  complete prompt-by-rank coverage.
- Publish only aggregate maxima, sums, and failure counts. Never publish
  per-prompt counters, routes, ids, weights, or traces.
- Any missing prompt summary, missing/duplicate/unexpected rank, nonzero counter,
  or summary exception blocks the smoke.

### 2. Empty authoritative readouts must fail

`check_authoritative` currently treats an authoritative rank with an empty
`readout` as finite because Python's `all()` over an empty sequence is true.
The collector can produce this state when no decoder hook sees a supported
single-token decode shape. That is precisely a feasibility failure the smoke is
required to detect.

For every prompt and every authoritative rank, require all of the following:

- `layers` equals the frozen `[4, 12, 20, 28, 36]` exactly;
- `cadence == 32` and `top_k == 10` exactly;
- exactly five `decode_steps`, `captured_slots`, and `dropped` counters;
- every layer has `decode_steps > 0` and a non-empty readout entry;
- every layer's `steps` and `token_ids` are non-empty, with
  `len(token_ids) == len(steps) * 10`;
- all recorded steps are in range, strictly increasing, and the final recorded
  step equals `decode_steps - 1`;
- the final position appears once. If the final decode step is already a cadence
  checkpoint, do not append a duplicate final slot;
- every top-k id is a valid global-vocabulary id and every finiteness flag is
  true;
- semantic-group aggregates are present, finite, and computed from the same
  authoritative readout;
- multiple authoritative ranks agree exactly on metadata, steps, top-k ids,
  finiteness, and semantic-group aggregates;
- non-authoritative ranks emit no readout, token ids, or semantic scores;
- projection-call, decode-step, captured-slot, and dropped-count vectors agree
  across all ranks.

Any empty, malformed, duplicate-final, incomplete, non-finite, shard-local, or
cross-rank-disagreeing result blocks the smoke. This correction preserves the
frozen layers, cadence, final-position rule, top-k, and semantic groups.

### 3. Installation conformance must be all-rank and exact

The current bridge install path selects result `[0]` and does not validate the
other rank's bridge or telemetry installation metadata.

Before leg B:

- validate every bridge-install result and every telemetry-install result;
- require the exact rank set `{0, 1}`;
- require identical bridge layers, hidden size, decoder-layer count, MoE-layer
  count, expert count, and top-k metadata where exposed;
- reject any `error`, already-installed state, missing field, rank disagreement,
  unexpected decoder depth, or unexpected MoE runner count;
- record only aggregate conformance booleans and counts.

Installation conformance is a technical gate and must be included in the
pending-restore pass calculation.

### 4. Finalization must verify an internally consistent technical artifact

The current finalizer accepts a substring match for the serving reply and can
promote any artifact whose `outcome` string says pending, even if its gate map is
missing or inconsistent.

Before issuing the restore probe, require:

- exact schema version and `run_kind`;
- exact projection commit, committed smoke-driver SHA, frozen override hash, and
  frozen envelope hash fields;
- a complete, exact gate-key set for the smoke phase;
- every technical gate is the boolean `true`;
- `outcome == technical_gates_passed_pending_restore`;
- no pre-existing gate 8 or final `passed` state;
- aggregate-only privacy status and no forbidden keys or payload classes;
- a SHA-256 of the pre-finalization technical artifact recorded in the final
  aggregate artifact.

The production reply must equal `SERVING-OK` after only surrounding-whitespace
normalization. Substring containment is forbidden. Require the exact expected
model id in the model list and successful process/endpoint health checks. Any
artifact inconsistency, reply mismatch, model mismatch, timeout, or health
failure writes the blocked outcome.

### 5. Every exception path must leave a blocker artifact and complete lifecycle cleanup

The current smoke can raise before its gate variables are assigned, resulting in
cleanup but no aggregate blocker artifact. It also starts the GPU sampler and
constructs the engine outside the protected lifecycle.

- Put sampler start, engine construction, installation, all three legs, fetches,
  gate calculation, engine release, and sampler shutdown under one explicit
  lifecycle state machine.
- Continue ordered cleanup through all cleanup errors and record aggregate step
  status.
- Stop and join the peak sampler on every path, including engine-construction
  failure.
- Avoid references to unassigned locals when a leg or RPC fails.
- On any exception, write an aggregate-only
  `agents_a1_semantic_bridge_feasibility_blocked` artifact containing only the
  exception class, lifecycle stage, cleanup aggregates, and privacy status.
- Never include prompt text, output text, token ids, readouts, hidden states,
  routes, local paths, or stack traces in the public blocker.

### 6. Add synthetic tests and commit before execution

Add tests covering at minimum:

- a mismatch on enabled prompt 1 followed by a clean prompt 2 still fails;
- exact rank set enforcement rejects `{0, 2}`, `{None, 0}`, duplicates, and
  missing ranks;
- an authoritative empty readout fails rather than passing vacuously;
- missing one frozen layer, zero decode steps, empty ids, bad id count,
  non-monotone steps, duplicate final step, or non-finite semantic aggregate
  fails;
- cross-rank metadata/counter disagreement fails;
- a rank-local install error or metadata disagreement fails;
- finalizer rejects substring replies such as `NOT SERVING-OK`;
- finalizer rejects pending artifacts with false, missing, extra, non-boolean, or
  inconsistent gates;
- finalizer records the technical-artifact SHA-256;
- engine-construction, leg, fetch, cleanup, and sampler exceptions each produce
  a blocked aggregate artifact without forbidden content.

Commit the corrected driver, bridge logic if needed, tests, and a new
aggregate-only technical amendment before any live M37J-C prompt. Run the full
private-safe suite and `check_commit_safe.py`; verify the pushed remote SHA.

These corrections are conformance-only. They do not authorize changing the
frozen prompts, model, checkpoint, decoding cap, layers, cadence, top-k,
semantic words, divergence envelope, memory limit, latency limit, route logic,
or production configuration.

## Execution order remains unchanged

1. Continue M36T sealed capture unchanged to 192/192.
2. Land the corrections above while capture continues; issue no live M37J-C
   prompt.
3. Run only the corrected M36T evaluator exactly once after its full preflight.
4. Restore and verify stock Agents-A1 serving.
5. Run the corrected bounded M37J-C smoke and finalize it only after the
   post-smoke production restore passes exact verification.
6. Release the dual-3090 window to M38E under its frozen protocol.

The latest capture pace implies the sealed run is unlikely to finish within the
remaining short monitoring window. Do not shorten the sealed set, lower the
2048-token ceiling, parallelize onto a non-identical runtime, or bypass any gate
to meet a wall-clock target.

## Research scan and scaling boundary

- `Hallucination Is Linearly Decodable from Mid-Layer Hidden States in Quantized
  LLMs` reports strong mid-layer linear separability on 4-bit 7B–8B models. This
  supports the technical plausibility of observing useful signals after
  quantization, but it does not establish transfer to Agents-A1 AWQ, long-horizon
  reasoning, or this semantic vocabulary.
- `Where Does Reasoning Break?` reports that trajectory-geometry features can
  localize first reasoning errors while a distilled deployable detector can
  collapse under distribution shift. If M37J-C is technically feasible, a fresh
  future protocol should compare trajectory dynamics against static semantic
  counts and must evaluate cross-family and cross-model shift explicitly. Do not
  add this to the frozen smoke.
- `IG-Lens` remains a plausible post-smoke attribution comparator because it
  provides exact additive probability accounting without a backward pass. It is
  not a Jacobian lens and does not replace the frozen standard logit-lens
  feasibility baseline.
- PUMA still requires semantic redundancy plus answer-level verification; its
  public implementation is not a basis for unverified Agents-A1 early exit.
- Counterfactual-routing work still shows that router behavior can be weak on
  fragile reasoning tokens. It supports comparison with hidden-state evidence,
  not route edits or causal claims.
- No verified official Agents-A1 4B checkpoint and no actionable r/LocalLLaMA
  implementation lead were found. The full-Jacobian Agents-A1 path remains
  blocked by official checkpoint availability and the unchanged 30 GiB fit gate.

M37J-C can establish only that bounded semantic readouts are technically
observable on the full quantized Agents-A1 runtime while preserving output
parity, dispatch identity, numerical validity, memory, latency, privacy, cleanup,
and production restoration. It cannot establish a Jacobian lens on Agents-A1,
error prediction, semantic correctness, causal attribution, expert meaning,
route quality, safe early exit, intervention value, or production utility.

Stop on checkpoint mismatch, task/row mismatch, task-hash mismatch, feature or
label leakage, verifier bypass, incomplete prompt-by-rank identity coverage,
empty readout, malformed layer/step metadata, tensor-parallel collective
mismatch, shard-local id leakage, cross-rank disagreement, numerical instability,
cleanup failure, sampler/engine lifecycle failure, restoration failure, privacy
failure, resource-gate breach, or repeated worker failure.

Never commit private prompts, outputs, operands, token text or ids, per-task
labels or predictions, raw telemetry, hidden states, activations, gradients,
Jacobians, lens matrices, model weights, caches, stack traces, or local paths.
Public artifacts remain aggregate-only and must pass `check_commit_safe.py`.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, or early-exit rule may be promoted by this directive.
