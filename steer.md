# steer.md — post-M32P decision gate (expert-routing track closed)

M1 through M32P are complete. M32 structured repair remains a preregistered,
never-executed historical artifact; M32R stopped at its Agents-A1 resource
gate; M32P ran the full model-calibrated counterfactual routing study on the
Qwen proxy and returned negative causal verdicts. Per the preregistered
Branch 3 in `docs/M32P_QWEN_PROXY_COUNTERFACTUAL_ROUTING_AUTOLOOP.md`, the
expert-routing autoloop stops here.

`CODEX_AUTOSTEER.md` remains the operating contract.

## M32P outcome (proxy-scoped; says nothing about Agents-A1)

- Phase 0A hook verified: bit-identical when disabled; equal-compute swaps
  with the router's own arithmetic; smoke passed at 27.95 GiB peak.
- Phase 0B calibration: the proxy's multiplication frontier is
  carry-structured (2x2 .96 low-carry vs .42 carry-heavy; 3x2 .83 vs .04;
  4x2 .71 vs .00; middle-zero .375; near-pow10 .667). Frozen rules chose the
  192-task benchmark (4 boundary cells x36, easy/hard anchors x12).
- Decision run met every power minimum (realized failures 41/18/21) with
  0 undecided, 34 minutes wall, 28.3 GiB peak.
- Frozen M30 trigger degraded on the frontier distribution: precision .766,
  recall .738 (vs ~.89 on band-based sets) — an honest distribution-shift
  finding about the detector.
- **H1 NOT ESTABLISHED**: heuristic-guided equal-compute swaps rescued
  sealed-holdout triggered failures at exactly the matched-random rate
  (.125 vs .125; paired CI [0,0]); the all-route oracle ceiling is 11.9%.
- **H2 NOT ESTABLISHED**: the validation-frozen non-oracle policy exactly
  matched normal routing (.5625).
- **H3**: no layer-expert soft-penalty candidate survived discovery.
- Route families rescue at random-perturbation rates and regress more than
  they rescue. Conclusion: on this proxy, systematic failures are not caused
  by locally poor top-4 expert choices at telemetry-fragile tokens; the
  small recoverable fraction is decode-path sensitivity to any perturbation.

## Cumulative repair-operator evidence

- M31: temperature resample rescues ~4.5% of triggered failures.
- M32P: equal-compute route perturbation rescues ~12% (oracle,
  untargetable — random matches guided).
- Neither stochastic decoding nor internal rerouting repairs systematic
  arithmetic errors. The unexplored repair directions from the superseded
  M32 protocol remain: structured prompting operators (deliberate re-solve,
  checker-guided, diagnose-then-repair) and telemetry-gated deterministic
  tools, with the tool arm as a known-perfect ceiling for this category.

## Required operator decision before the next milestone

Choose exactly one:

### A. Execute the preserved M32 structured-repair bakeoff (recommended)

The full protocol, manifest, module, and tests already exist (preregistered
at 5f0edfe, never executed, superseded before results). Reactivating it
requires only an operator instruction acknowledging the supersession notice
is lifted; the H1/H2 rules there directly test the last untested model-side
repair direction against the M31 resample baseline, with the tool upper
bound measured alongside.

### B. Telemetry-gated tool routing study

Skip model-side repair; measure the end-to-end value and compute savings of
routing triggered checkable tasks to deterministic computation versus
tool-on-every-task and random gating (runtime/product evidence).

### C. Detector robustness first

M32P showed the frozen detector loses precision/recall under task-structure
shift at matched digit counts. Preregister a detector-robustness milestone
(train/evaluate across carry-structured distributions) before investing in
more repair studies that depend on the trigger.

### D. Stop the telemetry program

Document the program state and return to practical supervisor work.

Do not begin the next milestone until the operator selects A–D. Any new
model run stays under the existing Qwen proxy approval.

## Repository hygiene

Do not commit model weights, caches, local model paths, prompts, outputs,
operands, per-task routes, expert identities tied to private tasks, token
ids/text, raw router tensors, or detailed counterfactual records. Public
artifacts remain aggregate-only. No candidate becomes gold and production
remains gated until explicit audited unlock criteria are defined.
