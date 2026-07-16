# jlens

Public research repository for observation-only interpretability and
completed-error monitoring in large Qwen-family mixture-of-experts models.

The repository contains several generations of work. Historical router-logit
and hidden-state experiments on Qwen3.6-35B-A3B remain descriptive technical
artifacts. They do not establish a correctness predictor, causal router
mechanism, safe intervention, early exit, or production utility.

## Binding program state

`steer.md` is the operating directive. `docs/LIVE_STATUS.md` is the newest
aggregate-only heartbeat. When an older roadmap, status file, report, or README
statement conflicts with either, the binding steer and newest live status take
precedence.

The current gated program is:

1. **M38E** — the frozen official sweep is complete at 288/288 tasks. Formal
   completion still requires operator-confirmed driver exit and every frozen
   exact-set, escalation, verifier, provenance, privacy, cleanup,
   commit-safety, dependency, execution-root, and serving-restoration audit.
   The two-family completed-error frontier is unavailable under the frozen
   design; the expected terminal result remains
   `m38e_completed_error_frontier_not_found` only after those audits pass.
2. **Q35Q** — test an architecture-matched quantized Qwen3.5-35B-A3B Jacobian
   path. GPU work remains blocked until M38E finalization releases and verifies
   the dual-RTX-3090 window. Before any backward call, artifact admission must
   bind a real tokenizer roundtrip, text-only model load, immutable model and
   toolchain identities, exact quantization, explicit placement, privacy,
   provenance, and commit-safety evidence.
3. **M39** — independently test forward-only incremental completed-error
   prediction against nuisance, pre-solve and post-solve behavioral
   self-assessment, position-aware autoregressive confidence, router,
   expert-contribution, and hidden-state comparators. Outcome-bearing capture
   remains prohibited until M38E is formally finalized and the complete launch
   amendment is committed.
4. **Agents-A1 scaling** — proceed only through exact executed-route VJPs,
   measured cost and memory gates, a passing frozen micro-fit, and deterministic
   prompt-level horizontal sharding with complete per-layer fp32 weighted merge.

## Established

- Historical router telemetry carries descriptive domain and routing-structure
  information on the previously studied model and prompt set.
- M38E's frozen official sweep contains 288/288 tasks, and its two-family
  completed-error frontier is unavailable. The formal terminal outcome remains
  gated on finalization audits.
- Q35Q has fail-closed CPU-side admission, placement, cost, merge, route-regime,
  and privacy-validation infrastructure.
- Monitoring and control are separate research questions.

## Not established

- Clean M38E finalization, the formal terminal outcome, or restored and verified
  Agents-A1 serving.
- Exact GPTQ or NF4 residual-input VJPs on Qwen3.5-35B-A3B.
- A validated quantized or BF16 Jacobian Lens on Qwen3.5 or Agents-A1.
- Transfer from a Qwen3.5 base lens to Agents-A1.
- Incremental correctness prediction beyond nuisance, behavioral
  self-assessment, position-aware confidence, router, expert-contribution, and
  hidden-state baselines.
- Safe truncation, early exit, retries, tool routing, route intervention,
  activation steering, or production use.

## Privacy and claim boundary

Treat every repository file as publicly visible. Do not commit raw tasks,
corpus text, prompts, outputs, token IDs, hidden states, activations, expert
outputs, routes, Jacobians, VJPs, lens matrices, per-example scores, model
weights, caches, local paths, environment values, process evidence, or
secret-linked provenance.

Only aggregate, privacy-reviewed, provenance-bound evidence may be committed.
A successful load, generation, descriptive telemetry capture, or synthetic test
is not evidence that an exact Jacobian, Agents-A1 predictor, control policy, or
production system exists.
