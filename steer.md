# steer.md — M36V router telemetry validation, then Agents-A1 raw-vs-jLens

M1 through M35 are complete. Do not reopen their sealed decision sets.

M35's strongest supported proxy result is a single cross-family global detector
thresholded to a tool budget: about .94 verified success at about .35 tool use
on its sealed benchmark. The family hierarchy did not beat that global score at
matched budget. Treat this as architecture evidence only; no proxy threshold,
centroid, prior, or calibration transfers automatically to Agents-A1.

`CODEX_AUTOSTEER.md` remains the operating contract.

## Current status

M36P's Transformers path remains a recorded loader failure, not a checkpoint
failure. Preserve finding 218 and its aggregate artifact unchanged.

M36V Phase 0 has now PASSED on the exact pinned checkpoint:

- checkpoint: `cyankiwi/Agents-A1-AWQ-INT4`;
- pinned revision: `3e522d4e46438c782789b73c8ff4503e0edd037c`;
- runtime: isolated vLLM 0.24.0, compressed-tensors, tensor parallel 2;
- architecture verified: `qwen3_5_moe`, 40 routed text layers, 256 experts,
  top-8 routing;
- 512-token greedy headroom required for the thinking model to reach final
  answers;
- all eight runtime gates passed;
- combined peak GPU memory: 43.18 GiB;
- decode throughput: 30.24 tokens/second;
- checkable smoke prompts: 4 pass, 0 fail, 0 undecided;
- peak process RSS: 1.89 GiB;
- no broad CPU weight offload;
- normal serving stack restored after the run.

The memory/runtime question is closed positively for this exact AWQ checkpoint.
Do not repeat Phase 0 unless required to verify a source-patch hash or parity.

## Operator decision

Proceed immediately to **M36V Phase 1: dispatch-validated, observation-only
router telemetry**. The purpose is not more runtime experimentation. The purpose
is to determine whether jLens can read the real routing decisions used by the
compressed vLLM MoE kernel without altering generation.

A small, isolated, auditable vLLM source patch or registered layer override is
authorized. Do not modify the working M22-M35 research venv, production
llama-swap/Ollama environment, checkpoint identity, or quantization.

After the M36V result commit:

- if router telemetry validates, proceed directly to the full three-arm M36
  benchmark;
- if the AWQ model remains valid but telemetry cannot be exposed safely, proceed
  directly to the paired raw-AWQ versus black-box-jLens benchmark;
- do not stop merely because the full-telemetry arm is unavailable;
- stop only if the exact AWQ checkpoint cannot continue generating correctly,
  the patch changes dispatch/generation, privacy fails, or the serving stack
  cannot be restored.

Authorize one bounded continuation covering:

1. M36V Phase 1 telemetry instrumentation and validation;
2. M36V Phase 2 parity/overhead smoke and result commit;
3. M36 AWQ-specific calibration, preregistration, paired benchmark, result, and
   final stop report.

Stop after the M36 result and request a fresh operator decision.

# M36V Phase 1 — real router telemetry

## Patch boundary

Patch only the real Qwen3.5 MoE routing path between router score production and
the fused expert dispatch call. The patch must be observation-only.

Capture or compute, for every generated decode token and routed layer:

- pre-dispatch router scores or logits over the 256 experts, at least for a tiny
  validation sample;
- exact top-8 expert ids consumed by dispatch;
- exact normalized top-8 dispatch weights consumed by dispatch;
- decode-step and layer indices needed to align telemetry with output logits;
- approved aggregate summaries required by the existing jLens feature schema.

For benchmark scale, prefer device-side or in-process summary computation rather
than copying all 40 x 256 router values per generated token to CPU. A tiny raw
full-logit validation sample is permitted. Any summary-only path must match the
features recomputed from raw validation tensors within a frozen tolerance.

## Required gates

All gates must pass before any Agents-A1 calibration or decision capture:

1. **Stock parity** — unpatched stock vLLM and patched-with-telemetry-disabled
   produce identical greedy token ids on the fixed smoke set.
2. **Observation parity** — telemetry enabled and disabled produce identical
   greedy token ids on the same fixed smoke set.
3. **Dispatch identity** — captured top-8 expert ids exactly equal the ids passed
   to the real fused expert dispatch for sampled tokens across early, middle,
   and late layers.
4. **Weight identity** — captured weights equal the actual dispatch weights
   within the declared numeric tolerance; finite, nonnegative, and normalized.
5. **Architecture identity** — loaded runtime remains 40 layers, 256 experts,
   top-8, exact pinned revision.
6. **Feature availability** — the existing approved jLens scalar telemetry
   schema can be derived without hidden-state capture.
7. **Bounded overhead** — record telemetry throughput and memory overhead. The
   patch must not push combined peak GPU use above the 44 GiB gate during the
   short validation run.
8. **Privacy** — no prompt/output text, token ids, raw router tensors, expert
   traces, local paths, or weights in public artifacts.

Required tests before the real patched smoke:

- fake-MoE router/dispatch alignment;
- top-k id and weight capture;
- normalization and finite-value checks;
- disabled-path no-op behavior;
- summary-versus-raw feature equivalence;
- bounded ring-buffer or aggregation behavior;
- aggregate-only public-report guard.

Commit the patch and tests separately before the real telemetry result commit.
Record vLLM version, patch hash, checkpoint revision, CUDA/Torch versions, and
launch configuration.

## Phase 1 outcomes

### Full telemetry feasible

The patch passes every gate. Proceed to Phase 2 and then the full M36 benchmark
with raw, black-box-jLens, full-telemetry-jLens, count-matched-random, and
 tool-on-every-eligible-task arms.

### Black-box only

The model continues to run correctly, but trustworthy router telemetry cannot be
exposed without changing generation/dispatch semantics, exceeding the bounded
patch, or violating the memory gate. Record the exact blocker, omit the full
telemetry arm, and continue to M36 raw versus black-box jLens.

### Runtime regressed

The patch or environment makes the exact checkpoint unstable, invalid, or
unrestorable. Revert the patch, verify stock Phase 0 still passes, restore normal
serving, stop, and report.

# M36V Phase 2 — parity, quality, and overhead smoke

Run 16 fixed private prompts spanning deterministic arithmetic, JSON, exact
instruction following, and short reasoning under:

1. stock vLLM AWQ;
2. instrumented vLLM AWQ with telemetry enabled, only if Phase 1 passed;
3. current Agents-A1 Q8 GGUF as a separate diagnostic.

Use 512-token output headroom unless a smaller cap is proven sufficient for the
specific prompt family before decision capture. Do not mistake truncation for a
model failure.

Report aggregate-only:

- deterministic verifier outcomes;
- malformed-output counts;
- output-token counts;
- load and generation latency;
- tokens/second;
- peak memory;
- telemetry overhead versus stock;
- disabled/enabled token parity;
- telemetry validation gates.

AWQ-versus-Q8 output equality is not required and is not an efficacy claim.
Always unload the research runtime and restore/verify the normal `agents-a1`
GGUF service afterward.

# M36 — paired Agents-A1 AWQ raw versus jLens

Begin only after an M36V result commit classifies the path as `full_telemetry`
or `black_box_only`.

## Calibration before preregistration

Run a private capability sweep using this exact AWQ checkpoint/runtime over
fresh deterministic, tool-checkable families. Calibration rows are never
benchmark decision data.

The sweep must find Agents-A1's own:

- high-competence cells;
- mixed-competence cells;
- near-total-failure anchors;
- output-length requirements and truncation risk.

For full telemetry:

- derive normalized telemetry features from fresh AWQ data only;
- fit and calibrate an Agents-A1-specific global detector;
- compare against difficulty/category metadata during development;
- do not import the proxy's threshold or score scale.

For black-box jLens:

- derive category/regime competence estimates from AWQ calibration outcomes;
- freeze the category policy and tool budget before decision capture.

Use a predeclared power rule to choose the benchmark count. Then commit a fresh
manifest before any decision-task generation or capture. Freeze task generators,
splits, decode cap, seeds, tool budget, feature schema, detector/policy hashes,
bootstrap seeds, family weights, non-inferiority margin, metrics, and claim
rules.

## Paired benchmark arms

Generate exactly one deterministic AWQ original per decision task. Every arm
starts from that same original answer and capture:

1. `raw_awq` — unchanged Agents-A1 AWQ result;
2. `black_box_jlens` — AWQ-specific competence policy, verifier-first checks,
   and deterministic tools without token/router telemetry selection;
3. `full_jlens` — only if M36V validated real router telemetry; AWQ-specific
   telemetry detector plus verifier-first tools;
4. `count_matched_random` — same tool-call count as the selected jLens arm;
5. `tool_on_every_eligible_task` — accuracy/resource ceiling.

No policy may replace a verified-correct original with a failing tool result.

## Confirmatory questions

- **H1 practical value:** selected jLens policy improves paired verified success
  over raw AWQ with the paired 95% lower confidence bound strictly above zero.
- **H2 telemetry increment:** when `full_jlens` exists, it beats black-box jLens
  and count-matched random at the frozen budget with both lower confidence
  bounds strictly above zero.
- **H3 efficiency:** the selected jLens policy is non-inferior to tool-all within
  the preregistered success margin while using significantly fewer tool calls.

Report raw and final verified success, corrections, misses, false alarms,
regressions, tool fraction, calls saved, model/tool/total latency, output tokens,
throughput, memory, telemetry overhead, and compute per corrected answer.

Claims remain scoped to the exact AWQ checkpoint revision, vLLM version, patch
hash, prompts, decode protocol, task generators, tools, and verifier bundle.

## Result branches

- H1 + H3 pass: freeze an Agents-A1-AWQ jLens candidate for extended shadow
  evaluation; production remains gated.
- H1 passes and H2 fails: retain black-box jLens and stop claiming internal
  telemetry adds incremental value.
- H1 fails: close the Agents-A1 efficacy track without checkpoint shopping or
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
