# steer.md — finish M36T, execute frozen M37J-A/M38E, and build the Agents-A1 semantic bridge

`CODEX_AUTOSTEER.md` remains the operating contract. This is the current binding
directive. It supersedes the stale M37J state in steer commit `0497526`; all
sealed-data, verifier, privacy, claim-boundary, resource, and production gates
remain binding.

Read and follow:

- `docs/M38E_HARD_COMPLETED_ERROR_PROTOCOL.md`
- `docs/M37J_JACOBIAN_LENS_SEMANTIC_WORKSPACE_AUTOLOOP.md`
- `docs/M36V_ROUTER_TELEMETRY.md`

## Established state

- M36V is complete and sealed on `cyankiwi/Agents-A1-AWQ-INT4`: 40 routed
  layers, 256 experts, top-8 dispatch, exact observed dispatch-id/weight
  identity, bounded observation overhead, and aggregate-only public artifacts.
- M36C is closed: 115 completed correct, 0 completed incorrect, and 81
  token-budget truncations. The completed-error study was not testable on that
  population.
- M36T is healthy. At pushed head
  `279a61fdd966df1447d11e25ee0f20fff9332f63`, capture is 89/96 with 58
  positive and 31 negative labels; the frozen >=24/>=24 power floor is already
  cleared. Seven rows remain. No blocker is established.
- M37J's authorized `dim_batch=4` refit passed the unchanged 30.0-GiB gate at
  29.58 GiB. Lens validation passed 4/4 checks on 20 held-out sequences,
  including finite Jacobians/logits, stable repeat application, and exactly
  zero observation-hook forward difference. Early/middle semantic readout is
  encouraging but is not failure-prediction evidence.
- M37J-A's 192-task diagnostic set was preregistered before labels at commit
  `81432ffb80d575356ed39f8cb41d1c95d33537de`: 96 discovery, 48 validation,
  48 sealed holdout; paired 256/1024 caps; four deterministic families; fixed
  lens layers/cadence/top-k; fixed semantic groups; private tasks.
- M38E's deterministic families, frozen development manifest, and bounded
  288-task sweep driver are staged. Live sweeps remain gated on the M36T safe
  stop.
- Full backward-pass Jacobian fitting on the 35B Agents-A1 checkpoint is not
  feasible on the current 32-GiB V100 or 44-GiB dual-3090 gates. The existing
  AWQ vLLM runtime is an inference runtime and does not provide the
  differentiable backward path required by the fitted Jacobian lens.
- The official Agents-A1 project announced a 4B model on 2026-07-08, but no
  official 4B checkpoint is present in the official model collection at this
  steer. Do not substitute an unofficial checkpoint.

## Immediate execution order

Do not interrupt the healthy M36T capture. Finish the current atomic task,
flush private progress, record this steer SHA, and continue the committed task
order and resume rules.

At M36T completion, execute the already-staged sequence without adding an
exploratory branch:

1. restore and verify normal Agents-A1 serving;
2. run the frozen power check;
3. freeze the four step-256 comparators and all hashes/configuration;
4. create the fresh sealed manifest only if the power gate passes;
5. complete the frozen M36T evaluation and commit the scoped result.

After the M36T safe stop:

- dual RTX 3090 priority: M38E development sweep, followed by its sealed
  benchmark only if every eligibility gate passes;
- V100 priority: M37J-A diagnostic capture and frozen H1/H2 evaluation;
- CPU-only work may build and test the Agents-A1 semantic-bridge adapter in
  parallel, but no live GPU smoke may delay M36T, M38E, service restoration, or
  the active M37J-A run.

# M36T — frozen completion rules

Complete the 96-task development capture and freeze these step-256
comparators:

1. metadata only;
2. metadata plus token confidence;
3. metadata plus router summaries;
4. full approved prefix telemetry.

No feature created after token 256 may enter the primary prediction. Token 128
and 384 remain secondary lead-time analyses.

If development contains fewer than 24 positive or 24 negative labels, commit
the power failure and close M36T. Otherwise freeze the classifier,
calibration, feature schema, tool-call budget, seeds, metrics, hashes, and
claim rules before creating the fresh sealed manifest.

Test exactly the preregistered questions:

- full prefix telemetry versus metadata plus confidence;
- full jLens routing versus metadata routing and count-matched random at the
  same tool-call count;
- full jLens versus long 2,048-token decoding for verified success and token
  use.

Do not tune on the sealed result. Commit the scoped conclusion before starting
an unregistered successor study.

# M38E — completed-error baseline

M38E remains a separate reliability track. Do not hand-pick known failures or
alter its frozen manifest, generators, family/band gates, verifier identities,
selection rule, or frontier-not-found stop condition.

Eligible development bands still require:

- completion rate >= .90;
- truncation rate <= .10;
- raw verified pass rate from .20 through .80;
- at least 6 completed correct and 6 completed incorrect examples;
- an objective verifier;
- sufficient unseen task space for a sealed holdout.

Require at least two eligible families and at least 48 completed incorrect
examples across development. If the bounded sweep cannot find that population,
commit `m38e_completed_error_frontier_not_found` and stop. Do not expand the
search adaptively.

The correct answer and verifier result remain labels only. They may never enter
a prediction feature. Public output remains aggregate-only.

# M37J-A — run the preregistered pilot diagnostic unchanged

Run the exact manifest and lens pinned at commit `81432ffb`. Do not add
features, semantic words, layers, positions, task families, budgets, or
comparators after seeing any discovery, validation, or holdout outcome.

The current external research scan is informative for future work but must not
contaminate this frozen primary evaluation:

- Agents-A1 technical report: arXiv `2606.30616`;
- counterfactual MoE routing analysis: arXiv `2605.07260`;
- semantic-convergence early exit/PUMA: arXiv `2605.17672`;
- IG-Lens no-backward layer attribution: arXiv `2606.29693`;
- Jacobian Scopes token attribution: arXiv `2601.16407`;
- latent-state refinement/ReLAR: arXiv `2606.17524`.

These papers do not establish a result on this repository's models or tasks.
Counterfactual routing and latent refinement are intervention/training evidence,
not authorization to edit Agents-A1 routes or weights. PUMA and IG-Lens support
separate observation-only comparators, not retroactive changes to M37J-A.

Evaluate the sealed M37J-A hypotheses exactly as frozen:

- H1: incremental completed-error prediction beyond metadata, output length,
  logit confidence, and router telemetry;
- H2: short-cap budget-state discrimination beyond ordinary telemetry.

Run M37J-B only if H1 or H2 satisfies its preregistered paired confidence-bound
rule. If neither is established, close the fitted-Jacobian pilot without tuning
on holdout.

# M37J-C — Agents-A1 semantic portability bridge

This milestone is authorized now because direct 35B Jacobian fitting is
resource-blocked while a no-backward, observation-only bridge can be tested on
the actual Agents-A1 runtime. It is a portability feasibility study, not a
claim that the pilot lens transfers and not a replacement for a fitted
Jacobian lens.

## Phase 0A — official 4B checkpoint watch and full-Jacobian path

At each safe checkpoint, inspect only the official `InternScience` repository
and model collection for an official Agents-A1 4B release.

If an official 4B checkpoint appears:

1. pin the exact repository, revision, license, config, tokenizer, dtype, and
   architecture before loading weights;
2. use the isolated V100 environment and the official/pinned Jacobian-lens
   revision;
3. run one 128-token backward smoke with peak allocated plus reserved memory
   <=30.0 GiB, no unbounded CPU offload, finite gradients/Jacobians, accessible
   residual hooks/unembedding, and unchanged normal forward output;
4. if the gate passes, commit a pre-fit aggregate manifest before generating
   the 120 private 128-token sequences, then use the existing 100-fit/20-
   validation protocol;
5. if any gate fails, commit the exact aggregate blocker and stop this branch.

Do not infer that a similarly named community quant is the official 4B model.
Do not use GGUF/AWQ for fitting. Do not raise the memory gate.

## Phase 0B — 35B observation-only semantic bridge

Implement a separate vLLM worker-extension path that is inert by default and
captures bounded residual checkpoints from the actual pinned Agents-A1 AWQ
runtime. The bridge may project those checkpoints through the model's own final
normalization/unembedding to produce only bounded top-k readouts and fixed
semantic-group scores. It must not fit or apply the pilot Jacobian lens to
Agents-A1.

Freeze before the first live prompt:

- five evenly spaced decoder layers selected from the 40-layer text stack;
- every-32-decode-token cadence plus final position;
- top-k 10 readout;
- the same five predeclared semantic groups used by M37J-A;
- standard logit-lens readout as the required baseline;
- an IG-Lens-style no-backward probability-attribution comparator only if its
  implementation has an exact completeness unit test and disabled-path parity;
- no discovery-derived vocabulary or task labels in Phase 0.

Phase-0 live smoke is bounded to 16 fresh deterministic public-safe prompts and
may run only at a safe service window after M36T completion. It must pass all of
these gates:

- disabled extension path is unchanged;
- observation-enabled dispatch ids and weights remain identical to dispatch
  entry, using the established M36V identity checks;
- finite readouts and semantic scores;
- normal output divergence no worse or earlier than the frozen stock-vLLM
  nondeterminism envelope;
- combined peak reserved memory <=44 GiB;
- generation-time overhead <=1.50x versus the paired disabled runtime;
- no raw prompt/output text, token ids, hidden states, full logits, or per-token
  semantic traces in git;
- normal Agents-A1 serving restored and verified after the smoke.

Commit only aggregate gate results, implementation hashes, layer identities,
resource measurements, and privacy status. If any gate fails, commit
`agents_a1_semantic_bridge_feasibility_blocked` and stop; do not tune layers or
cadence against task outcomes.

If Phase 0B passes, preregister a fresh bounded decision set before inspecting
labels. A later efficacy phase must compare metadata+confidence, router-only,
standard logit-lens semantic scores, and the approved no-backward attribution
features. It may not reuse M36T or M38E sealed outcomes as training data, and it
may not begin while those primary tracks need the same GPUs.

## Claim boundary

A passing Phase 0B establishes only that semantic layer readouts can be
observed on the full Agents-A1 inference runtime within resource and parity
gates. It does not establish a Jacobian lens, causal attribution, error
prediction, safe early exit, self-awareness, route quality, or production
utility.

A fitted 4B Agents-A1 lens establishes only a model-scoped 4B result. It does
not transfer to the 35B model without a separate fresh evaluation.

# Scheduling, safety, and repository hygiene

Continue pushed 30-minute heartbeats while any track is active. Every heartbeat
must fetch and compare remote `steer.md`, report aggregate progress, and verify
that its pushed SHA is visible remotely.

Stop on checkpoint mismatch, sealed-data leakage, feature leakage, invalid
telemetry alignment, verifier misuse, numerical instability, repeated worker
failure, privacy failure, resource-gate breach, or inability to restore normal
serving.

Never commit private prompts, outputs, operands, token text or ids, per-task
labels or predictions, raw telemetry, hidden states, activations, gradients,
Jacobians, lens matrices, steering vectors, model weights, caches, or local
paths. Public artifacts remain aggregate-only and must pass
`check_commit_safe.py`.

Production remains gated. No observation, classifier, tool policy, route edit,
activation intervention, or early-exit rule may be promoted to production by
this directive.