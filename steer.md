# steer.md — finish M35, then benchmark Agents-A1 with and without jLens

M1 through M34 are complete. M35 tracks A, B, and C are active under
`docs/M35_PARALLEL_TRACKS_PROTOCOL.md`. The shared campaign has completed
capture and extraction:

- 1,536 / 1,536 rows extracted;
- zero undecided outcomes;
- D 576 / R 288 / B-test 288 / A-test 384;
- the sealed B-test and A-test splits remain unopened;
- realized family failure rates span .041 to .953, providing high-, mixed-,
  and near-total-failure regimes;
- track C is implemented in advisory-only shadow mode and executes no actions.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Operator decision

Complete M35 exactly as preregistered, then move directly to a controlled
Agents-A1 raw-versus-jLens benchmark. Do not wait for a perfect internal
telemetry path before measuring practical product value.

The operator also explicitly authorizes a bounded Agents-A1 Hugging Face
CPU-offload telemetry preflight using the available 48 GiB aggregate VRAM and
128 GiB system RAM. CPU spill is permitted for this research pilot even though
it will be slow. It is not permitted to silently change model identity,
checkpoint family, prompts, or claim scope.

## Immediate milestone — finish M35 A/B evaluation

Follow the frozen split discipline in `docs/M35_PARALLEL_TRACKS_PROTOCOL.md`.

### Track B — detector robustness

1. Use D only for feature selection, normalization, detector fitting,
   calibration, thresholds, and all model selection.
2. Run the full preregistered leave-one-family-out pipeline, refitting every
   preprocessing and detector component for each withheld family.
3. Freeze the selected global, per-family, and hierarchical detector variants
   before opening B-test.
4. Open B-test once, evaluate the preregistered transfer claims, and do not use
   B-test outcomes to tune track A.

### Track A — hierarchical competence router

1. Use only the already-frozen track-B detector components plus R to fit family
   competence priors and the three-way controller:
   - trust the model answer;
   - telemetry-gated selective tool use;
   - tool on every eligible task.
2. Freeze the router, thresholds, fixed tool budget, family weights, and
   non-inferiority policy before opening A-test.
3. Open A-test once and evaluate A-H1 and A-H2 exactly as preregistered.
4. Preserve verifier-first semantics: no policy may replace a verified-correct
   original with a failing tool or repair result.

### M35 completion requirements

Commit separately:

1. detector implementation and fitting code;
2. frozen detector/router configuration hashes;
3. B-test result;
4. A-test result and aggregate-only M35 study report;
5. updated `STATE.md`, `reports/FINDINGS.md`, and post-M35 steer.

Run the full suite and `check_commit_safe`. No sealed row, operand, prompt,
output, label, prediction, score, or private path may enter public artifacts.

## Next milestone — M36 Agents-A1 raw versus jLens

Begin M36 after the M35 result commit, regardless of whether every M35
confirmatory claim passes. If M35 is negative, M36 is exploratory product
measurement; if M35 is positive, M36 is an external-model validation of the
frozen architecture. Never present proxy-model calibration as Agents-A1
calibration.

### M36A — practical GGUF benchmark

Use the existing production-serving model identity `agents-a1` through
llama-swap. This arm does not require internal MoE telemetry.

Before decision capture:

1. Create and commit a dedicated M36 protocol.
2. Run a private calibration sweep to locate Agents-A1's own competence
   frontier for deterministic, tool-checkable families. Calibration rows are
   never decision data.
3. Preregister fresh, disjoint sealed tasks with a useful mix of:
   - high-competence cells;
   - mixed-competence cells;
   - near-total-failure anchors.
4. Freeze category features, competence priors, jLens policy, tool budget,
   decoding settings, seeds, metrics, and claim rules before sealed capture.

Primary comparison uses one deterministic Agents-A1 original per task:

- **Arm A — raw Agents-A1:** score the original answer as served.
- **Arm B — Agents-A1 + black-box jLens:** apply the frozen hierarchical
  category/regime policy, verifier-first checks, and deterministic tools to the
  same original answer.

Do not generate independent model answers for the two arms. This is a paired
system comparison, not a sampling contest.

Required M36A metrics:

- verified success rate and paired confidence interval;
- errors corrected, errors missed, and regressions introduced;
- tool invocation fraction and calls saved versus tool-on-every-task;
- end-to-end latency, model tokens, tool latency, and compute per corrected
  answer;
- per-family competence regime and policy choice;
- abstentions and unsupported categories;
- raw Agents-A1 versus jLens-managed final outcome.

A black-box result establishes practical supervisor value only. It does not
establish that Agents-A1 internal telemetry transfers from the Qwen proxy.

## Parallel bounded preflight — M36T Agents-A1 internal telemetry with CPU spill

The previous 44 GiB all-GPU feasibility gate is no longer the only permitted
path. Test the official `InternScience/Agents-A1` safetensors checkpoint with
bounded CPU offload:

- aggregate GPU allocation/reservation target: <= 44 GiB;
- CPU model-memory target: <= 96 GiB, leaving headroom for the OS and runtime;
- router/logit capture only; hidden-state capture disabled;
- short contexts and short greedy continuations;
- no weight, cache, model path, prompt, output, token, tensor, or route record
  committed.

Preflight sequence:

1. Load the official checkpoint with an explicit device map spanning both
   RTX 3090s and CPU RAM.
2. Verify `qwen3_5_moe`, 40 routed layers, 256 experts, and top-8 routing.
3. Verify real router logits and the telemetry feature extraction path.
4. Run eight fixed private smoke prompts and record aggregate peak GPU memory,
   peak process RAM, prompt latency, generation latency, and tokens/second.
5. Restore and verify the normal GGUF `agents-a1` serving path afterward.

Preflight outcomes:

- **Feasible:** stable completion, no OOM, correct telemetry, and median prompt
  runtime <= 6 minutes. Preregister a small 32-64 prompt Agents-A1 telemetry
  pilot. It is a pilot, not the main product benchmark.
- **Slow but runnable:** correct telemetry but median runtime > 6 minutes.
  Keep M36A as the main benchmark and limit telemetry work to a tiny diagnostic
  sample.
- **Blocked:** loader, hook, RAM, or correctness failure. Record the exact
  blocker and continue M36A through GGUF; do not substitute another model.

## Interpretation boundary

The jLens architecture is intended to scale, but model-specific calibration is
mandatory. These do not transfer automatically between the Qwen proxy and
Agents-A1:

- telemetry normalization and fail thresholds;
- competence priors;
- task-family frontiers;
- layer/expert identities;
- routing penalties;
- expected accuracy uplift.

M36A answers whether the complete supervisor improves Agents-A1 in practice.
M36T asks whether Agents-A1's own internal telemetry can eventually improve
that supervisor further.

## Stop conditions

Stop and report immediately on:

- sealed-split leakage or read-order violation;
- any policy replacing a verified-correct answer with an incorrect result;
- privacy or commit-safety failure;
- test failure;
- model identity mismatch;
- unbounded CPU/GPU memory growth;
- inability to restore the production GGUF service.

## Repository hygiene

Do not commit model weights, caches, local paths, prompts, outputs, operands,
per-task labels/predictions/scores, token ids/text, raw logits, router tensors,
expert identities tied to private tasks, or detailed tool results. Public
artifacts remain aggregate-only. Candidate outputs remain candidates, no tool
output becomes training data without a future audited protocol, and production
remains gated.