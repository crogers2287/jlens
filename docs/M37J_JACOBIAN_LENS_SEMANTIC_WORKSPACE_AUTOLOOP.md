# M37J — Jacobian-lens semantic workspace research track

Status: operator-authorized adjacent-research protocol. This track complements,
but does not replace or delay, the active M36 Agents-A1 raw-versus-jLens study.
`steer.md` remains the execution source of truth and `CODEX_AUTOSTEER.md`
remains the operating contract.

## Research basis and claim boundary

Primary sources:

- `anthropics/jacobian-lens`, the Apache-2.0 reference implementation for
  fitting and applying a Jacobian lens to Hugging Face decoder models;
- Anthropic's *Verbalizable Representations Form a Global Workspace in Language
  Models*.

The reference method transports intermediate residual-stream activations into
an output-readable basis using an average Jacobian. The official repository
states that roughly 100 fitting prompts can produce a usable lens, while the
paper-scale lenses use 1,000 sequences of 128 tokens; fitting cost is dominated
by the base model's backward pass.

Community claims that J-space editing is a cheap general replacement for LoRA
are **unreplicated and out of scope**. M37J tests observation and temporary
activation intervention only. No permanent weight edit, exported altered model,
safety bypass, or production behavior change is authorized.

## Why this matters to jLens

M36 already provides validated router/logit telemetry, but those signals are
mostly statistical. The Jacobian lens may expose semantically interpretable
workspace content such as verification, error recognition, continuation, and
completion. The concrete questions are:

1. Do J-space features add held-out failure information beyond metadata,
   output length, logit confidence, and MoE-router telemetry?
2. Can they distinguish a genuinely wrong completed answer from a model that
   is merely still reasoning when the decode budget expires?
3. Can a frozen, bounded workspace intervention reduce excessive reasoning or
   truncation without lowering verified accuracy?

All claims remain scoped to the exact pilot model, lens fit, prompts, task
families, decode protocol, and intervention implementation. Nothing from the
pilot is an Agents-A1 claim.

## Hardware and environment isolation

M36 remains the primary program on the dual RTX 3090 machine. M37J should use
the separate 32 GiB V100 host when available.

- Do not interrupt an active M36 capture or benchmark to run M37J.
- Use an isolated environment and pin the exact
  `anthropics/jacobian-lens` revision, Transformers, Torch, CUDA, model revision,
  and configuration.
- Do not alter the working M36 vLLM environment, production llama-swap/Ollama
  service, or existing research venv.
- If the V100 host is unavailable, implementation and CPU tests may proceed,
  but real lens fitting waits until M36 releases the 3090s or the operator
  provides another device.

# M37J-A — feasibility, fit, and semantic-monitor study

## Phase 0 — model and backward-pass feasibility

The preferred pilot is the already-local `Qwen1.5-MoE-A2.7B-Chat` because it is
an MoE Qwen proxy already used in jLens research. It may not fit a full
backward-pass Jacobian calculation on a 32 GiB V100.

Before any fitting data are generated:

1. inventory locally available open-weight Qwen decoder checkpoints;
2. test the preferred MoE proxy with a tiny forward/backward smoke;
3. if it fails the resource gate, select one already-local dense Qwen decoder
   no larger than 4B parameters;
4. commit the exact selected model identity, revision/hash, tokenizer, dtype,
   sequence length, layer count, and reason for selection before fitting.

This ordered fallback is authorized, but it is not silent: the selected model
must be recorded in a separate pre-fit commit and all claims must use its name.

Resource gate:

- peak allocated plus reserved GPU memory <= 30 GiB on the V100;
- no unbounded CPU offload;
- one 128-token backward smoke completes correctly;
- residual-stream hooks and final unembedding are accessible;
- the official `jlens.from_hf` adapter or a minimal tested Qwen adapter works;
- normal forward outputs remain unchanged when the lens is not being applied.

Stop with `jlens_fit_resource_blocked` if no approved local Qwen model passes.
Do not download a different model family or redesign the method silently.

## Phase 1 — lens fitting and readout validation

Before fitting, commit a private-data manifest containing only aggregate-safe
metadata and hashes:

- deterministic corpus seed;
- 120 generic pretraining-like sequences of 128 tokens;
- 100 fit sequences and 20 lens-validation sequences;
- no M36 benchmark prompts or answers;
- checkpoint cadence and merge procedure;
- exact layer set and Jacobian estimator configuration.

The sequences themselves remain private and gitignored.

Fit using the official implementation or a minimal compatibility patch.
Checkpoint resumably. Public output may include only aggregate fit time, peak
memory, merge counts, numerical health, and lens hash.

Readout validation must establish:

- finite lens matrices and logits;
- stable application on the 20 held-out validation sequences;
- coherent intermediate readouts on a small synthetic concept set;
- early/middle/late layer behavior reported descriptively;
- no change to the model's normal output from observation-only lens application;
- lens application cost and memory overhead.

This phase validates a readable lens, not semantic truth or self-awareness.

## Phase 2 — fresh diagnostic decision set

Preregister 192 fresh deterministic tasks after the lens is fitted but before
any diagnostic labels are inspected:

- 96 discovery;
- 48 validation;
- 48 sealed holdout.

Use at least four task families and deliberately populate four outcome classes:

1. `completed_correct`;
2. `completed_incorrect`;
3. `short_cap_truncated_long_cap_correct`;
4. `truncated_at_both_caps`.

Task construction must be disjoint from M29-M36 decision sets. Use paired short
and long decode budgets fixed in the manifest. Capped outputs are never labeled
as completed wrong answers.

Collect, privately:

- existing metadata and output-length features;
- output-logit confidence features;
- MoE router features when the selected pilot exposes them;
- J-lens top-k token readouts at preregistered positions/layers;
- deterministic verifier labels and finish reasons.

## J-space feature families

Freeze two feature families before the sealed holdout:

### A. Predeclared semantic groups

Normalize decoded lens tokens and count/persist signals in these fixed groups:

- completion: `final`, `answer`, `done`, `complete`, `conclude`;
- continuation: `continue`, `next`, `more`, `step`, `then`;
- verification: `check`, `verify`, `recheck`, `confirm`, `calculate`;
- error/conflict: `error`, `wrong`, `mistake`, `conflict`, `but`;
- uncertainty: `uncertain`, `maybe`, `perhaps`, `unsure`, `doubt`.

Report tokenization misses honestly. Do not add words after observing holdout
outcomes.

### B. Discovery-derived sparse readout features

On discovery only, fit a bounded sparse representation from normalized top-k
J-lens tokens, layer bands, persistence, transition timing, and concept churn.
Freeze vocabulary, normalization, sparsity, and feature count on validation
before opening holdout.

No correct answer, verifier result, or long-cap outcome may enter the feature
calculation presented to the detector.

## M37J-A comparators and hypotheses

Evaluate on the sealed holdout:

1. metadata plus output length;
2. metadata plus output length plus current logit/router telemetry;
3. metadata plus output length plus J-space features;
4. all approved features combined.

### H1 — semantic telemetry increment

On completed, nontruncated outputs, the combined model must improve paired
failure-prediction accuracy and balanced accuracy over comparator 2, with both
95% bootstrap lower confidence bounds strictly above zero.

### H2 — budget-state discrimination

Among short-cap truncations, a frozen J-space policy must predict long-cap
completion/correctness better than metadata plus short-cap length and ordinary
telemetry, with the paired 95% lower confidence bound strictly above zero.

H2 is about allocating more reasoning budget intelligently. It is not evidence
that the model knows its answer or possesses consciousness.

If neither H1 nor H2 is established, stop the J-space track after M37J-A.

# M37J-B — bounded workspace intervention

Run only if M37J-A establishes H1 or H2 and observation-only lens validation is
clean.

## Intervention design

Use temporary activation interventions only. No weights are changed or exported.

Preregister discovery-derived layer/position targeting and fixed scale grids for:

1. no intervention;
2. matched-norm random-vector sham;
3. completion steering using frozen J-lens vectors for completion-group tokens;
4. verification-then-completion two-stage steering;
5. ablation of excessive continuation-group components, only if numerical
   stability is proven in fake and smoke tests.

The intervention must be applied after a frozen trigger based only on information
available at decision time. It must never use the correct answer or candidate
verifier outcome to choose a vector or scale.

Required safety gates:

- disabled path is numerically unchanged;
- intervention is bounded in norm and layer count;
- no NaNs, runaway activations, or malformed-output increase on smoke tests;
- matched random controls receive identical compute and branch budgets;
- right-to-wrong regressions are tracked explicitly;
- no global personality, safety, or refusal steering is authorized.

## M37J-B hypotheses

### H3 — reasoning-efficiency intervention

On a sealed set of truncation-prone but long-cap-solvable tasks, a frozen
J-space intervention must reduce median generated tokens or truncation rate
versus both no intervention and matched-random sham, with paired 95% confidence
bounds above zero, while verified accuracy is non-inferior within a predeclared
absolute margin of 0.02.

### H4 — completed-error safety

On completed-answer tasks, the intervention must not significantly increase
right-to-wrong regressions and must preserve malformed-output and verifier-fail
rates within preregistered bounds.

A token reduction obtained by forcing premature answers while reducing accuracy
is a failure, not a rescue.

# Result-driven continuation

- H1/H2 positive, H3 positive: preserve a model-scoped semantic monitor and
  intervention candidate; stop and request an operator decision before any
  Agents-A1 portability work.
- H1/H2 positive, H3 negative: retain J-space as an observation-only diagnostic;
  do not claim it repairs reasoning.
- H1/H2 negative: close the track; do not tune semantic lexicons or interventions
  on the sealed set.
- Resource/adapter/lens-fit failure: record the exact blocker and stop without
  changing model families.

Nothing in M37J authorizes applying a lens trained on the pilot model to
Agents-A1. Agents-A1 portability would require a separate feasibility and
validation milestone because the AWQ vLLM runtime is inference-oriented and the
Jacobian fit requires differentiable backward passes.

# Deliverables and privacy

Expected public deliverables:

- selected-model feasibility artifact;
- pinned environment and lens hash;
- aggregate lens-fit and readout-validation report;
- preregistered diagnostic manifest;
- aggregate M37J-A evaluation;
- conditional aggregate M37J-B evaluation;
- updated `STATE.md`, `reports/FINDINGS.md`, and `steer.md`.

Keep private and gitignored:

- fitting corpus text;
- prompts and outputs;
- token ids and per-position readouts;
- residual activations, gradients, Jacobians, lens matrices, steering vectors,
  per-task labels/predictions, local paths, model weights, and caches.

Public artifacts remain aggregate-only and must pass `check_commit_safe`.
Production remains gated. Candidate outputs remain candidates, and no tool or
lens output becomes training data without a future audited protocol.
