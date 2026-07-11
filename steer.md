# steer.md — M36V vLLM AWQ telemetry recovery, then Agents-A1 benchmark

M1 through M35 are complete. Do not reopen their sealed decision sets.

M35's strongest supported policy is a single cross-family global detector
thresholded to a tool budget: about .94 verified success at about .35 tool
invocation on its sealed proxy benchmark. The hierarchical family router was
redundant at matched budget, and structurally novel families still require
representation in detector fitting data.

M36P attempted the pinned full Agents-A1 AWQ checkpoint through Transformers
and stopped correctly before calibration or decision capture:

- checkpoint: `cyankiwi/Agents-A1-AWQ-INT4`;
- pinned revision: `3e522d4e46438c782789b73c8ff4503e0edd037c`;
- architecture from config: `qwen3_5_moe`, 40 routed text layers, 256 experts,
  top-8;
- blocker: Transformers 5.13 converts the checkpoint's per-expert asymmetric
  INT4 modules through fused `DecompressExperts`, fails its zero-point path,
  and would expand the experts toward BF16 beyond the 44 GiB GPU gate;
- no M36 calibration or benchmark decision data were generated;
- GPUs were freed and the normal serving stack was restored.

Preserve finding 218 and `reports/telemetry/m36p_preflight_gates.json` as the
failed Transformers-path record. Do not rewrite it as an AWQ/checkpoint
failure: it is a loader-path failure.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Operator decision

Select blocker option **B**: use an isolated **vLLM >= 0.22** runtime for the
same pinned AWQ checkpoint. Do not spend another cycle on speculative
Transformers/compressed-tensors version roulette, and do not change checkpoint
identity.

The intended vLLM path is compressed AWQ Marlin MoE across both RTX 3090s. A
small, bounded, auditable MoE-block instrumentation patch is authorized to
expose real router telemetry. Router telemetry is not assumed merely because
the model generates successfully; it must be causally tied to the actual
expert dispatch and validated below.

Authorize a bounded two-stage continuation:

1. **M36V** — vLLM AWQ load/quality/router-telemetry preflight.
2. **M36** — paired raw Agents-A1 AWQ versus jLens benchmark, using full
   telemetry if M36V validates it, otherwise black-box jLens if the AWQ model
   itself runs correctly.

Stop after the M36 result and request a fresh operator decision.

# M36V — isolated vLLM AWQ preflight

## Environment isolation

1. Create a separate venv or container for M36V. Do not alter the working
   M22-M35 research venv, system Torch, Ollama, llama-swap, or the production
   GGUF environment.
2. Pin and record the exact vLLM version, CUDA/Torch versions, quantization
   backend, checkpoint revision, command line, and source-patch hash.
3. Use the exact full checkpoint above. Do not substitute the text-only AWQ,
   official BF16, FP8/NVFP4, MLX, GGUF, or another community quant.
4. Use text prompts only, but do not prune the checkpoint or silently remove
   multimodal/MTP components.
5. Keep all weights and caches local and gitignored.

## Phase 0 — unmodified compressed-runtime gate

First prove the unpatched runtime works:

- tensor parallel size 2 across the two RTX 3090s;
- short maximum context and short greedy continuations for preflight;
- hidden-state capture disabled;
- no broad CPU weight offload;
- combined GPU allocated/reserved target <= 44 GiB;
- finite logits and stable text generation;
- no architecture or checkpoint revision mismatch.

Run eight fixed private smoke prompts before adding telemetry instrumentation.
Record aggregate-only:

- load time;
- peak GPU memory per device and combined;
- peak process RAM;
- prompt and generation latency;
- output tokens and tokens/second;
- crashes, retries, CPU-mapped modules, and quantization kernel actually used.

If the exact AWQ checkpoint cannot generate through the compressed vLLM path
on this hardware, stop M36V as `runtime_blocked`, restore the normal service,
and request a new operator decision. Do not fall back silently.

## Phase 1 — bounded router-telemetry instrumentation

After the unmodified runtime passes, implement the smallest practical source
patch or registered layer override around the real Qwen3.5 MoE routing path.
Commit the patch and CPU/fake-MoE tests separately before any M36 calibration or
benchmark capture.

The patch must expose, for each generated token and routed layer:

- finite pre-dispatch router scores or logits over 256 experts;
- the exact eight selected expert ids;
- the exact dispatch weights after the runtime's top-k normalization;
- enough timing/index metadata to align routing with the generated decode step.

Validation requirements:

1. Telemetry disabled follows the stock vLLM path and produces identical greedy
   tokens on the smoke set.
2. Telemetry enabled is observation-only and produces the same greedy tokens as
   telemetry disabled.
3. Captured selected expert ids exactly match the ids handed to the actual
   fused expert dispatch for sampled tokens and layers.
4. Captured dispatch weights are finite, nonnegative, normalized within a
   declared tolerance, and match the values consumed by dispatch.
5. Architecture is verified from the loaded runtime: 40 routed text layers,
   256 experts per layer, top-8.
6. The existing jLens telemetry adapter can derive its approved scalar feature
   schema from the captured values.
7. Full raw router tensors, token ids/text, expert traces, prompts, and outputs
   remain private and gitignored. Public artifacts are aggregate-only.

A tiny full-logit capture is permitted for validation. For benchmark scale,
prefer online computation of approved summaries plus top-8 ids/weights so that
copying 40 x 256 router values per token to CPU does not become the benchmark's
main cost. Any change from validation capture to summary capture must be tested
for numerical equivalence of the derived jLens features.

## Phase 2 — quality and overhead smoke

Run 16 fixed private prompts spanning exact arithmetic, JSON, instruction
following, and short reasoning with:

- stock vLLM AWQ;
- instrumented vLLM AWQ with telemetry enabled;
- the currently served Agents-A1 Q8 GGUF as a separate quality diagnostic.

AWQ and Q8 answers need not be identical. Report deterministic verifier
outcomes, malformed-output counts, gross instruction-following failures,
throughput, and telemetry overhead. This is a checkpoint/runtime diagnostic,
not the M36 efficacy claim.

Always unload M36V and restore/verify the normal `agents-a1` GGUF service after
preflight work.

## M36V outcomes

### Full telemetry feasible

The exact AWQ checkpoint runs compressed within the memory gate, generates
valid outputs, and the patch exposes dispatch-validated router telemetry with
observation-only parity. Proceed to the full M36 benchmark with raw,
black-box-jLens, and full-telemetry-jLens arms.

### Black-box only

The exact AWQ checkpoint runs correctly, but trustworthy router telemetry
cannot be exposed without changing dispatch semantics, violating parity, or
using an unbounded patch. Record the exact blocker and proceed to M36 with raw
AWQ versus black-box jLens plus random/tool-all controls. Do not fabricate a
full-telemetry arm.

### Runtime blocked

The exact checkpoint cannot run correctly through the compressed vLLM path on
this hardware. Stop, restore service, and request an operator decision. No
checkpoint switch is authorized.

# M36 — paired Agents-A1 AWQ raw versus jLens

Begin only after an M36V result commit.

## AWQ-specific calibration and preregistration

Before any decision capture:

1. Run a private capability sweep for this exact AWQ runtime over several
   deterministic, tool-checkable families.
2. Locate high-, mixed-, and near-total-failure cells from AWQ outcomes only.
3. If full telemetry exists, fit normalization and the detector only on fresh
   AWQ development data. Proxy thresholds, centroids, priors, and score scales
   do not transfer.
4. For black-box jLens, fit category/regime competence estimates from AWQ
   calibration data only.
5. Preregister fresh disjoint development/calibration/sealed splits, task count
   from a power rule, prompt/decode settings, seeds, tool budget, family
   weighting, bootstrap seeds, non-inferiority margin, and all claim rules.
6. Freeze every detector and policy hash before the sealed read.

## Paired arms

Generate exactly one deterministic AWQ original per task. Every arm starts from
that same original answer and capture:

1. `raw_awq` — unchanged model answer;
2. `black_box_jlens` — AWQ competence prior, verifier-first checks, and
   deterministic tools without token/router telemetry selection;
3. `full_jlens` — only when M36V validated telemetry: AWQ-specific telemetry
   detector plus verifier-first tools;
4. `count_matched_random` — selection control;
5. `tool_on_every_eligible_task` — accuracy/resource ceiling.

No arm may replace a verified-correct original with a failing result.

## Confirmatory questions

- **H1 practical value:** selected jLens policy improves paired verified success
  over raw AWQ with the 95% lower confidence bound strictly above zero.
- **H2 telemetry increment:** when `full_jlens` exists, it beats black-box jLens
  and count-matched random at the frozen budget with both lower confidence
  bounds strictly above zero.
- **H3 efficiency:** selected jLens policy is non-inferior to tool-all within the
  preregistered success margin while using significantly fewer tool calls.

Report success, corrections, misses, regressions, false alarms, tool fraction,
calls saved, model/tool/total latency, output tokens, throughput, memory,
telemetry overhead, and compute per corrected answer. Claims remain scoped to
the exact AWQ checkpoint, vLLM version, patch hash, task generators, prompt,
decode protocol, tools, and verifier bundle.

## Result-driven continuation

- H1 + H3 pass: freeze an Agents-A1 AWQ jLens candidate for extended shadow
  evaluation; production remains gated.
- H1 passes and H2 fails: retain the black-box policy and stop claiming internal
  telemetry adds incremental value.
- H1 fails: close this Agents-A1 efficacy track without checkpoint shopping or
  post-hoc benchmark changes.
- Stop after the result commit in every branch.

## Stop conditions and hygiene

Stop immediately on checkpoint/revision mismatch, invalid dispatch telemetry,
observation changing tokens, sealed-split leakage, verifier-first violation,
unbounded memory, test failure, privacy/commit-safety failure, or inability to
restore the serving stack.

Do not commit weights, caches, local paths, prompts, outputs, operands, per-task
labels/predictions/scores, token ids/text, raw logits, router tensors, or expert
traces. Public artifacts remain aggregate-only. Candidate outputs stay
candidates; no tool output becomes training data without a future audited
protocol, and production remains gated.
