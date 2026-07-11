# steer.md — finish M35, then benchmark Agents-A1 AWQ INT4 with and without jLens

**M35 STATUS (2026-07-11): COMPLETE.** All sealed reads done exactly once, in
order. Track B: LOFO transfer holds for mul_carry/mul_add/mod_mul, fails for
div_exact; track A: A-H1 and A-H2 not established — the hierarchy is
redundant over a global-detector threshold at matched budget (findings
215-217, `docs/M35_PARALLEL_TRACKS_RESULTS.md`, result commit fb6e5cb).
Track C shadow mode is live. **M36P below is now the active directive.**

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

Complete M35 exactly as preregistered, then move directly to an Agents-A1
raw-versus-jLens benchmark using the full Hugging Face AWQ INT4 checkpoint:

`cyankiwi/Agents-A1-AWQ-INT4`

This is now the preferred M36 research and benchmark model. It is a community
AWQ INT4 quantization in Hugging Face safetensors/compressed-tensors format,
not the official BF16 checkpoint and not the current Q8 GGUF serving artifact.
Every result must name the exact checkpoint and pinned revision. Do not report
AWQ results as official-BF16 or GGUF results.

The previous official-BF16 CPU-offload plan is superseded as the primary M36
telemetry path. Preserve its Phase-0 feasibility record as history. CPU spill
may be used only as a bounded preflight fallback; the intended AWQ path is an
all-GPU load across the two RTX 3090s.

The operator authorizes downloading this exact checkpoint and installing the
minimum `compressed-tensors`/AWQ runtime dependency in the isolated research
venv if it is absent. Do not modify the production llama-swap environment.

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

# M36 — Agents-A1 AWQ INT4 raw versus jLens

Begin M36 after the M35 result commit. M36 has a preflight gate followed by a
paired benchmark. The benchmark is checkpoint-specific external-model
validation; proxy-model thresholds and competence priors do not transfer.

## M36P — AWQ load, quality, and telemetry preflight

Use only the pinned revision of:

`cyankiwi/Agents-A1-AWQ-INT4`

### Load path

1. Prefer Hugging Face Transformers in the research venv because M36 requires
   direct access to router logits and model internals. Do not begin with vLLM
   or SGLang unless the Transformers path is proven incompatible and the
   alternative exposes equivalent real telemetry and hooks.
2. Use both RTX 3090s with an explicit memory map. Target combined allocated
   plus reserved GPU memory <= 44 GiB, leaving runtime headroom.
3. Hidden-state capture stays disabled. Capture only output logits and router
   telemetry needed by the existing jLens feature schema.
4. CPU RAM may absorb loader metadata and a bounded fallback spill, but record
   peak process RAM and every CPU-mapped module. Silent broad CPU offload is
   forbidden for the decision benchmark.
5. No weights, caches, local model paths, prompts, outputs, token ids, logits,
   tensors, or expert routes may be committed.

### Required architecture and hook gates

Verify from the loaded model, not from assumptions:

- model type `qwen3_5_moe`;
- 40 routed text layers;
- 256 experts per routed layer;
- top-8 active experts per token;
- finite next-token logits;
- finite router logits or equivalent pre-dispatch gate scores;
- selected expert ids and normalized routing weights;
- telemetry extraction through a real greedy decode;
- opt-in instrumentation whose disabled path preserves the normal forward
  result and greedy tokens on the smoke set.

AWQ expert kernels may replace ordinary linear modules. Router visibility and
hook placement must therefore be demonstrated on the real compressed model.
Memory fit alone is not enough.

### Smoke and parity checks

Run a small fixed private smoke set before any M36 calibration or decision
capture:

1. 16 short text prompts spanning exact arithmetic, JSON, instruction
   following, and short reasoning.
2. Record aggregate load time, peak GPU memory per device, peak process RAM,
   prompt latency, generation latency, and tokens/second.
3. Compare deterministic verifier outcomes and gross response validity with the
   currently served Agents-A1 Q8 GGUF. This is a checkpoint-quality diagnostic,
   not the M36 efficacy claim.
4. Confirm telemetry records validate against the schema and contain no raw
   private text in public output.
5. Unload the AWQ model and restore/verify normal GGUF `agents-a1` service after
   the preflight.

### M36P outcomes

- **Full telemetry feasible:** AWQ loads stably within the GPU gate, generates
  valid outputs, and exposes correct router/logit telemetry. Proceed to the
  full three-arm M36 benchmark below.
- **Black-box only:** AWQ generates correctly but compressed kernels prevent
  trustworthy router telemetry. Proceed with raw AWQ versus black-box jLens,
  and report the exact hook blocker.
- **CPU-spill diagnostic only:** correct telemetry requires substantial CPU
  mapping or median smoke runtime above six minutes. Limit internal telemetry
  to a tiny diagnostic sample; do not use that path for the primary benchmark.
- **Blocked:** loader, dependency, OOM, architecture, output-validity, or
  correctness failure. Do not silently switch to the text-only AWQ checkpoint,
  NVFP4, MLX, GGUF, or another model. Record the blocker; the operator decides
  the next model identity.

## M36 calibration and preregistration

Before decision capture:

1. Run a private AWQ-specific capability sweep over deterministic,
   tool-checkable families. Calibration rows are never decision data.
2. Locate this checkpoint's high-, mixed-, and near-total-failure regimes.
3. Fit or recalibrate telemetry normalization and the failure detector using
   only AWQ calibration/development data. Never reuse the proxy threshold as
   though it were frozen for Agents-A1.
4. Preregister fresh disjoint decision tasks, sealed splits, decoding settings,
   seeds, task-family weights, competence priors, tool budget, bootstrap seeds,
   non-inferiority margin, and all claim rules.
5. Freeze the AWQ detector and hierarchical policy before opening the sealed
   benchmark.

Use enough fresh tasks to power the paired raw-versus-jLens comparison, with a
useful mixture of competence regimes. Determine the exact count from a
predeclared power rule rather than copying M35 mechanically.

## M36 paired benchmark arms

Generate exactly one deterministic AWQ original per task. Every arm begins
from that same original answer and capture.

1. **Raw Agents-A1 AWQ** — score the original answer unchanged.
2. **Black-box jLens** — category/regime competence prior, verifier-first
   checks, and deterministic tools, without internal telemetry selection.
3. **Full jLens** — AWQ-specific competence prior plus AWQ router/logit
   telemetry risk gate, verifier-first checks, and deterministic tools.
4. **Tool on every eligible task** — upper-bound and resource reference, not a
   jLens selectivity claim.
5. **Count-matched random tool routing** — selection control.

If M36P is black-box-only, arm 3 is omitted and the result must say so plainly.
Do not fabricate telemetry from GGUF metadata or proxy-model features.

## Primary questions and claim boundaries

### H1 — practical jLens value

Full jLens must improve verified success over raw Agents-A1 AWQ on the sealed
paired benchmark with a paired 95% confidence interval strictly above zero.
When full telemetry is unavailable, black-box jLens is tested against raw
instead.

### H2 — incremental internal-telemetry value

When arm 3 exists, full jLens must beat black-box jLens and count-matched random
routing under the preregistered fixed tool budget, with both paired lower
confidence bounds strictly above zero. Otherwise internal telemetry is not
established as adding value beyond the hierarchical black-box controller.

### H3 — efficiency versus tool-on-every-task

The selected jLens policy must meet the preregistered verified-success
non-inferiority margin versus tool-on-every-task while using significantly
fewer tool calls. Tool-on-every-task cannot satisfy this claim by construction.

All claims are scoped to this exact AWQ checkpoint, task generators, prompt
format, decode protocol, tools, and verifier bundle. No claim of universal
model-independent telemetry is permitted.

## Required M36 metrics

- raw, black-box, full-jLens, random, and tool-all verified success rates;
- paired confidence intervals for every confirmatory comparison;
- errors corrected, errors missed, false alarms, and regressions introduced;
- tool invocation fraction and calls saved versus tool-on-every-task;
- model latency, tool latency, total latency, output tokens, and compute per
  corrected answer;
- detector precision/recall/calibration by family and competence regime;
- category-level route choice and abstention counts;
- AWQ peak GPU memory, peak process RAM, and throughput;
- exact checkpoint repository and pinned revision;
- Q8 GGUF smoke-parity diagnostics, reported separately from M36 claims.

## Result-driven continuation

- If H1 and H3 pass, freeze an Agents-A1-AWQ jLens candidate policy for extended
  shadow evaluation. Production remains gated.
- If H1 passes but H2 fails, retain the black-box hierarchical controller and
  stop claiming internal telemetry adds value.
- If telemetry is useful but efficiency fails, return to router calibration on
  fresh development data; do not tune on the sealed benchmark.
- If H1 fails, stop the Agents-A1 jLens efficacy track and report the negative
  result without changing checkpoints post hoc.
- Stop after the M36 result and request a fresh operator decision.

## Stop conditions

Stop and report immediately on:

- M35 or M36 sealed-split leakage or read-order violation;
- any policy replacing a verified-correct answer with an incorrect result;
- privacy or commit-safety failure;
- test failure;
- checkpoint identity or pinned-revision mismatch;
- unbounded CPU/GPU memory growth;
- invalid or fabricated router telemetry;
- inability to restore the production GGUF service.

## Repository hygiene

Do not commit model weights, caches, local paths, prompts, outputs, operands,
per-task labels/predictions/scores, token ids/text, raw logits, router tensors,
expert identities tied to private tasks, or detailed tool results. Public
artifacts remain aggregate-only. Candidate outputs remain candidates, no tool
output becomes training data without a future audited protocol, and production
remains gated.