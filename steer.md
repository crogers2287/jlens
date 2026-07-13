# steer.md — fix tensor-parallel Agents-A1 semantic projection before live smoke

`CODEX_AUTOSTEER.md` remains the operating contract. This directive supersedes
steer commit `cccf40aa0b3cea6eda76bb7f7324bd772ab91256` only where explicitly
amended below. Every sealed-data, verifier, privacy, claim-boundary, resource,
production, and repository-hygiene gate from steers `8eb2e9e` and `cccf40a`
remains binding by incorporation. No scientific threshold, feature family, task
set, model, checkpoint, or resource gate is relaxed.

## Current established state

- M36T development completed 96/96 with 65 positive and 31 negative labels. The
  frozen comparators and power gate remain pinned at
  `945830ceca2e02f4940e63f2c3cbe1261b74b359`.
- The 192-task M36T sealed manifest was committed before outcomes at
  `12e3af03ef6c01724b38d60a731948987d31f022`. At pushed heartbeat
  `243942aa49b4b37cce7961b60a5c4e2b01dbe3c5`, sealed capture was 37/192,
  healthy, supervised, and producing about 26 rows/hour. Do not interrupt it.
- The M36T evaluator conformance defect was corrected before sealed outcomes at
  `0285ec3531d40faac286424661f610ade677d3ec`: tool answers are constructed from
  the exact private task, checked through the frozen verifier, and blocked on
  any preflight or verifier failure. The corrected evaluator remains staged and
  must be the only evaluator used.
- M37J-A completed its exact-token 192-task evaluation at
  `df10b69196a35b51cd557dc7c92ec5d3ed8d7197`. H1 was not established: all four
  completed-error comparators had balanced accuracy 0.500 on a holdout with 41
  errors and 2 correct answers. H2 had only five short-cap truncation rows and
  was underpowered. The fitted-Jacobian pilot track is closed; do not run M37J-B
  or tune on this holdout.
- The official InternScience collection still has no verified Agents-A1 4B
  checkpoint. The full-Jacobian Agents-A1 path remains blocked without
  substitution or a raised memory gate.
- M37J-C Phase 0B was implemented CPU-only at
  `8692f69e559682580e719863097e6e6fa1900104` with an inert collector, the frozen
  five layers `[4,12,20,28,36]`, 32-token cadence plus final position, top-k 10,
  fixed semantic groups, bounded fp16 buffers, and seven fake-stack tests.
- M38E remains queued behind the active M36T sealed window. The V100 is idle.

## Binding M37J-C tensor-parallel correction before any live prompt

The Phase 0B CPU implementation is not yet valid on the real vLLM tensor-
parallel runtime. `SemanticBridgeCollector.readout` currently calls
`lm_head(norm(residuals))` directly. On the pinned vLLM architecture this is a
hard implementation error, not a scientific result:

- Qwen3-MoE uses `ParallelLMHead` and exposes the supported projection path as
  `Qwen3MoeForCausalLM.compute_logits`, which calls the model's
  `LogitsProcessor`.
- At vLLM revision `75fe92a3162a68d74581ec324f04684a752e3ad2`,
  `ParallelLMHead.forward` deliberately raises `RuntimeError("LMHead's weights
  should be used in the sampler.")`.
- The vLLM `LogitsProcessor` applies the quantized LM-head method and gathers
  tensor-parallel vocabulary shards before trimming padding. A direct local
  head call would either fail or produce shard-local, non-global token ids.

Do not run the 16-prompt live smoke against commit `8692f69` unchanged. Complete
this CPU-safe correction first without touching M36T:

1. Route residual projection through the live causal model's supported
   `compute_logits`/`logits_processor` path, never through direct
   `ParallelLMHead.forward`.
2. Every tensor-parallel rank must execute the same projection calls in the same
   order so the gather collective cannot deadlock.
3. Treat the gathered result as authoritative only on the rank where vLLM
   returns the full global-vocabulary logits. Non-root ranks may return bounded
   status/counter metadata but must not emit shard-local top-k ids or semantic
   scores.
4. Compute top-k from global, padding-trimmed vocabulary logits. Verify ids are
   in `[0, config.vocab_size)` and identical to a synthetic gathered-reference
   calculation. Never add a shard-local index without the exact shard offset.
5. Project captured slots in a fixed bounded chunk size so a full
   slots-by-vocabulary tensor cannot create an avoidable peak-memory failure.
   Chunk size is an implementation resource control, not a task-derived tuning
   variable; freeze it before the first live prompt.
6. Compute the already-frozen M37J-A-style semantic-group counts only from the
   authoritative global top-k ids. Keep the five groups, substring rule, layers,
   cadence, final-position rule, and top-k unchanged.
7. Add CPU tests that emulate: direct `ParallelLMHead.forward` raising; root
   global-logit return plus non-root `None`; two vocabulary shards whose winning
   token is on the second shard; padded-vocabulary trimming; identical collective
   call counts; bounded chunking; and disabled-path parity.
8. Commit the correction and an aggregate-only technical note before any live
   prompt. Run the full private-safe test suite and `check_commit_safe.py`, then
   verify the pushed remote SHA.

This correction changes only the projection implementation needed to realize the
already-frozen standard logit-lens baseline. It does not authorize new semantic
words, layers, positions, cadence, top-k, prompts, labels, comparators, route
edits, activation intervention, or an IG-Lens comparator without its separately
required exact-completeness tests.

## M36T sealed completion remains binding

Continue sealed capture unchanged. After all 192 rows are durably present, run
only the corrected evaluator from `0285ec3`:

- execute the exact task/row identity, task-file SHA-256, checkpoint, schema,
  feature-timing, uniqueness, and token-ceiling preflight before scoring;
- construct deterministic tool output from the private task and require the
  same frozen verifier to return `pass`;
- preserve `k`, all six arms, rankings, token accounting, decision step 256,
  counterfactual caps, hypotheses, 10,000 paired bootstrap resamples, and the
  dedicated count-matched-random seed;
- on any preflight or verifier failure, commit only the aggregate blocker and
  stop before opening hypotheses;
- do not tune on the sealed result.

## M37J-A closure and claim boundary

M37J-A's negative/underpowered result is final for its frozen pilot population.
Do not reopen the pilot, merge discarded round-trip rows, add features, or use
its holdout to choose M37J-C vocabulary, prompts, layers, or thresholds.

The M37J-C smoke can establish only that bounded semantic readouts are observable
on the full Agents-A1 inference runtime within parity, identity, memory, latency,
and privacy gates. It cannot establish a Jacobian lens on Agents-A1, error
prediction, causal attribution, route quality, safe early exit, self-awareness,
intervention value, or production utility.

## Research and implementation scan

No new official Agents-A1 4B checkpoint and no actionable r/LocalLLaMA
implementation lead were verified in this scan. Existing paper registrations
remain future-work evidence only, including counterfactual MoE routing
`2605.07260`, PUMA `2605.17672`, IG-Lens `2606.29693`, Jacobian Scopes
`2601.16407`, ReLAR `2606.17524`, interpretability-without-actionability
`2603.18353`, Self-Routing `2604.00421`, and MoE equifinality `2604.14419`.
None authorizes route edits, activation steering, early exit, or retroactive
changes to a frozen study.

The steer-worthy new evidence in this run is the primary vLLM implementation
contract: Qwen3-MoE's global logits must pass through `LogitsProcessor`; direct
`ParallelLMHead.forward` is explicitly unsupported and tensor-parallel local ids
are not valid semantic readouts.

## Execution order

1. Continue M36T sealed capture uninterrupted.
2. Correct and test the M37J-C projection CPU-only while capture runs.
3. At M36T completion, run the corrected evaluator exactly once and commit the
   scoped result or aggregate blocker.
4. Restore and verify normal Agents-A1 serving.
5. Run the already-bounded 16-prompt M37J-C live smoke only from the corrected
   projection commit and only if all eight Phase 0B gates remain enforced.
6. Then release the dual-3090 window to M38E under its frozen protocol.

Stop on checkpoint mismatch, task/row mismatch, task-hash mismatch, feature or
label leakage, verifier bypass, tensor-parallel collective mismatch, shard-local
readout, invalid telemetry alignment, numerical instability, repeated worker
failure, privacy failure, resource-gate breach, or inability to restore normal
serving.

Never commit private prompts, outputs, operands, token text or ids, per-task
labels or predictions, raw telemetry, hidden states, activations, gradients,
Jacobians, lens matrices, model weights, caches, or local paths. Public artifacts
remain aggregate-only and must pass `check_commit_safe.py`.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, or early-exit rule may be promoted to production by
this directive.
