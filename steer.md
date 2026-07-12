# steer.md — finish M36 Agents-A1 benchmark; run M37J semantic-workspace pilot in parallel

M1 through M35 are complete. Do not reopen their sealed decision sets.
`CODEX_AUTOSTEER.md` remains the operating contract.

Detailed adjacent-research protocol:

`docs/M37J_JACOBIAN_LENS_SEMANTIC_WORKSPACE_AUTOLOOP.md`

Read it in full before beginning M37J work.

# Current established state

## M36V — Agents-A1 AWQ runtime and telemetry qualification: COMPLETE

Exact research model:

- checkpoint: `cyankiwi/Agents-A1-AWQ-INT4`;
- revision: `3e522d4e46438c782789b73c8ff4503e0edd037c`;
- runtime: isolated vLLM 0.24.0, compressed-tensors, tensor parallel 2;
- architecture: `qwen3_5_moe`, 40 routed text layers, 256 experts, top-8;
- full observation-only router telemetry validated against actual fused dispatch;
- zero expert-id mismatches and exact dispatch-weight identity in validation;
- stock and instrumented AWQ both passed 16/16 Phase-2 verifier checks;
- telemetry overhead in the controlled smoke was about 1.32x;
- normal Agents-A1 GGUF serving restored after every research run.

Do not repeat M36V. Preserve its artifacts as the runtime/telemetry qualification
for M36.

## M36C — calibration amendment and implementation status

The original 384-row fixed calibration sweep was stopped correctly at a safe
boundary after **88 completed private rows**. Those rows remain unchanged. The
normal serving stack was restored. Do not restart the original full sweep.

The first multiplication family showed a decode-budget cliff:

- 3x2 and 4x3 multiplication: about .94 pass;
- 5x4 and 6x5 multiplication: apparent .06/.00 pass, but .94/1.00 truncation at
  the 1,024-token cap;
- those hard cells are budget-bound, not established capability failures.

Commit `8066fe2` implements the approved M36C machinery:

- device-side summary telemetry for the four router features;
- bounded scalar RPC instead of per-prompt full tensor transfer;
- raw NPZ capture only for validation samples;
- summary-versus-raw equivalence testing at <= 1e-5 per feature;
- per-component harness profiling;
- adaptive four-row cell probes;
- staged 512 -> 1,024 -> 2,048 token rescue budgets;
- separate `truncated_budget` classification;
- frozen quota-driven selective expansion;
- retention cap for completed calibration rows.

# Primary operator decision — finish M36 efficiently

M36 remains the primary research program. Continue from the existing 88 rows and
the committed M36C machinery. Do not return to the 20-hour fixed sweep.

## M36C Phase 0 — profile and validate summary telemetry

Run the fixed eight-prompt profile before new adaptive rows.

Record aggregate median and p95 timing for:

- model generation;
- collector reset/install/fetch;
- worker RPC;
- telemetry serialization;
- feature derivation;
- verifier execution;
- result append/fsync.

Binding gates:

1. every device-summary router feature matches raw-NPZ recomputation within
   absolute difference <= 1e-5;
2. no request/telemetry alignment error;
3. no dispatch identity regression;
4. no public prompt/output/token/route/tensor/path leakage;
5. median non-generation harness overhead <= 25% of model generation time.

If gate 5 fails, optimize only the largest measured component once, then rerun
the profile. Microbatching 2-8 prompts is permitted only when per-request
telemetry alignment, feature identity, and verifier outcomes are regression-
tested. Do not optimize speculatively.

## M36C Phase 1 — adaptive frontier map

Keep all 88 completed rows. For untested cells, run deterministic four-row probes
using the committed task order.

Staged budget policy:

1. begin at 512 output tokens;
2. rerun at most two predetermined truncated rows per cell at 1,024;
3. rerun at most one predetermined still-truncated row per cell at 2,048;
4. never run an entire cell at 2,048.

For each cell report separately:

- completed-correct rate;
- completed-incorrect rate;
- truncation rate by budget;
- median/p95 output tokens;
- generation and harness time.

Never label a capped output as a completed wrong answer.

## M36C Phase 2 — selective expansion

Use the already-frozen expansion rules:

- mixed completed frontier: pass rate .20-.80 and truncation <= .25 -> expand
  to 16 completed rows;
- high/low completed anchor: pass rate outside that range and truncation <= .25
  -> retain or expand to 8;
- budget-bound: truncation > .50 at 1,024 -> no broad expansion;
- ambiguous cells may expand to 8 only to meet quotas.

Stop when all are met or the retention cap is exhausted:

- >=48 completed-correct rows;
- >=48 completed-incorrect rows;
- completed failures from >=3 task families;
- >=2 mixed-frontier cells;
- <=192 retained completed calibration rows.

If these cannot be met, report `completed_failure_frontier_not_found`; do not
construct a benchmark dominated by timeouts.

Split completed calibration rows deterministically within cell into detector D
(two thirds) and policy R (one third). Keep truncation rows as a separate budget-
policy dataset.

## Agents-A1 detector and policy freeze

Fit only from fresh Agents-A1 AWQ calibration data. Do not import proxy
thresholds, centroids, priors, or score scales.

Freeze these comparators:

1. metadata only;
2. metadata + output length/finish reason;
3. metadata + length + logit features;
4. metadata + length + router features;
5. full approved telemetry.

The operational black-box controller may route explicit truncations and verifier
failures directly to a trusted deterministic tool. Report this separately from
internal telemetry prediction.

The binding internal-telemetry claim population is completed, nontruncated
outputs. Full telemetry must add value beyond metadata plus output length at the
same tool budget. Detecting the token cap is useful but is not evidence of
model-internal error awareness.

Freeze detector and policy hashes before creating the decision manifest.

# M36 — paired Agents-A1 AWQ raw versus jLens

After M36C result and freeze commits, preregister fresh, disjoint decision tasks.
Calibration prompts and M29-M35 decision tuples remain excluded.

Use the committed power rule to select N from 192, 240, or 288 with expected raw
operational failures >=24.

Primary benchmark composition:

- 60-70% mixed completed-error frontier cells;
- 15-20% high-competence anchors;
- 15-20% low-competence but mostly completed anchors;
- separate small non-confirmatory budget-bound set.

Choose a fixed decode cap whose primary cells have estimated truncation <=.10.
Do not use timeout-heavy cells to inflate apparent jLens uplift.

Every policy arm starts from the same single AWQ original and telemetry capture:

1. `raw_awq`;
2. `black_box_jlens` — competence, finish reason, verifier-first tools;
3. `full_jlens` — Agents-A1 telemetry detector plus verifier-first tools;
4. `count_matched_random`;
5. `tool_on_every_eligible_task`.

No arm may replace a verified-correct answer with a failing result.

Confirmatory questions:

- **M36-H1 practical value:** selected jLens improves verified success over raw
  AWQ with paired 95% lower confidence bound >0;
- **M36-H2 telemetry increment:** on completed, nontruncated outputs, full jLens
  beats black-box jLens and count-matched random at the frozen budget, both lower
  bounds >0;
- **M36-H3 efficiency:** selected jLens is non-inferior to tool-all within the
  frozen success margin while using significantly fewer calls.

Report operational and completed-only results separately, including truncation
rescues, wrong-answer rescues, misses, false alarms, regressions, tool fraction,
calls saved, tokens, latency, telemetry overhead, and compute per correction.

Stop after the M36 result commit and print the required report. Any further
Agents-A1 efficacy work requires a new operator decision.

# Adjacent track — M37J Jacobian-lens semantic workspace

The operator authorizes the detailed M37J protocol as a **parallel, model-scoped
pilot**, not as a replacement for M36.

## Scheduling and hardware

- M36 retains priority on the dual 3090 machine.
- Use the separate 32 GiB V100 host for M37J when it is reachable.
- Do not stop, slow, or alter an active M36 run to fit a Jacobian lens.
- If the V100 is unavailable, implementation and CPU tests may proceed, but real
  fitting waits for non-conflicting GPU capacity.
- Use an isolated environment pinned to an exact
  `anthropics/jacobian-lens` revision.

## Claim boundary

The official Jacobian lens reads intermediate residual representations by
fitting average layerwise Jacobian transports. It requires differentiable
backward passes. The current Agents-A1 AWQ/vLLM path is inference-oriented and
is **not** approved for direct lens fitting.

M37J therefore begins on a differentiable Qwen pilot model. Preferred order:

1. already-local `Qwen1.5-MoE-A2.7B-Chat` if a 128-token backward smoke fits
   within 30 GiB on the V100;
2. otherwise an already-local dense Qwen decoder <=4B, selected and committed
   before fitting.

No silent model-family change is allowed. All claims name the exact pilot model.
Nothing from M37J is an Agents-A1 result.

Community claims that J-space modification replaces LoRA are unverified and out
of scope. No permanent weight edit, exported altered checkpoint, personality
edit, safety bypass, or production behavior modification is authorized.

## Authorized bounded autoloop

Authorize at most two M37J milestones:

### M37J-A — fit and semantic-monitor evaluation

Follow the detailed protocol:

- feasibility/backward gate;
- 100 fit plus 20 lens-validation sequences of 128 tokens;
- exact lens/environment hash;
- 192 fresh tasks split 96 discovery / 48 validation / 48 sealed holdout;
- four outcome classes: completed correct, completed incorrect, short-cap
  truncation rescued at long cap, and truncation at both caps;
- fixed semantic groups for completion, continuation, verification,
  error/conflict, and uncertainty;
- discovery-only sparse J-readout features frozen before holdout;
- compare metadata+length, current telemetry, J-space features, and combined.

Primary M37J-A claims:

- **J-H1 semantic increment:** on completed nontruncated outputs, J-space plus
  current telemetry beats current telemetry alone in accuracy and balanced
  accuracy with both paired lower confidence bounds >0;
- **J-H2 budget-state prediction:** among short-cap truncations, J-space predicts
  long-cap successful completion better than metadata, length, and ordinary
  telemetry, lower bound >0.

If neither passes, stop the Jacobian-lens track.

### M37J-B — temporary workspace intervention

Run only if J-H1 or J-H2 passes and observation-only validation is clean.

Test frozen temporary activation interventions only:

- no intervention;
- matched-norm random sham;
- completion steering;
- verification-then-completion steering;
- optional bounded continuation ablation only after numerical smoke gates.

No correct answer or verifier result may select an intervention.

Primary intervention claim:

- **J-H3 efficiency:** reduce median output tokens or truncation versus no-op and
  random sham with paired lower bounds >0 while verified accuracy is non-
  inferior within absolute margin .02.

Forcing an early wrong answer is a failure. Track right-to-wrong regressions,
malformed outputs, activation norms, and numerical instability.

Stop after M37J-B or the first negative/blocking branch. Request an operator
decision before any attempt to port a lens or intervention to Agents-A1.

# Shared stop conditions and hygiene

Stop immediately on checkpoint/revision mismatch, invalid telemetry/readout,
sealed-set leakage, verifier-first violation, unbounded memory, numerical
instability, test failure, privacy/commit-safety failure, or inability to restore
the serving stack.

Do not commit weights, caches, local paths, prompts, outputs, operands, per-task
labels/predictions/scores, token ids/text, raw logits, router tensors, expert
traces, residual activations, gradients, Jacobians, lens matrices, or steering
vectors. Public artifacts remain aggregate-only and must pass
`check_commit_safe`. Production remains gated; no tool or lens output becomes
training data without a future audited protocol.
