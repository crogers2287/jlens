# STEER ADDENDUM — model-marginal readout, component heterogeneity, orthographic confounds, and fit-budget gates

Date: 2026-07-26
Parent remote head: `d7a0c5447ec9b31a3e42759df4747f291d0bde97`

This is a binding addendum to `CODEX_AUTOSTEER.md`, `steer.md`, and all later
cumulative protocol corrections. It preserves every privacy, sealed-data,
provenance, verifier, exact-set, derivative, resource, retry, intervention, and
production-gating rule. It does not constitute Q35Q admission, authorize weight
staging or GPU use, reopen M38E, permit Agents-A1 capture, or establish an
internal scientific result.

## Primary external evidence

The public campaign `praxagent/jacobian-lens-research-202607a` preregistered a
readout-subspace decomposition at immutable commit
`f563e28a9962505a4166fec7d9b3c0b13639ea24`, reported the frozen analysis at
`eddee8d145288d5345c1f9cbd2d15ed38328848e`, and added a descriptive token-pole
analysis at `db2f88a4daa279afe9f195157c6531b1cac7efde`.

For one WikiText-fitted Gemma-2-9B Jacobian-lens artifact, the reported top four
eigendirections carried approximately 48.4%, 14.8%, 6.7%, and 4.2% of readout
energy. A seven-feature preregistered regression explained approximately 57.2%
of the top direction's per-token effect. The model's own context-averaged output
marginal explained more variance by itself than the external WikiText unigram
count in that analysis. The first three inspected directions appeared broadly
prior-like under token-pole inspection, while the fourth was described after the
frozen analysis as contrasting ordinary punctuation with private-use glyphs,
typographic ligatures, and likely PDF/OCR extraction residue.

The campaign also preregistered, but has not yet reported, a fit-budget study at
`1d9bd6d872a37fda98b9fe3eba411cb44541e031`. It will compare 25, 50, 100, 200,
and 400-prompt fits against the same-corpus seed null. No conclusion about
budget convergence is established by that preregistration.

These are external author-supplied results and interpretations. They have not
been independently reproduced in jLens. The reported decomposition is limited
to one model, one lens artifact, one short-context fitting corpus, one tokenizer,
one runtime, and one feature family. The orthographic interpretation was
post-hoc and descriptive. A high regression fit establishes describability by
chosen features, not a mechanism, causal role, semantic workspace, correctness
monitor, or production control signal.

## Binding interpretation

The new evidence changes the minimum comparator and claim boundary for fitted
Jacobian readout subspaces:

> A fitted readout direction may primarily reflect a model-by-population output
> marginal, token inventory structure, or orthographic corpus artifacts. A
> low-dimensional subspace may contain qualitatively different components. The
> leading component does not identify the entire subspace, and an external
> unigram baseline alone is not a sufficient lexical or output-prior control.

The phrase `model prior` is not admissible without qualification when the
quantity is computed by averaging model outputs over a named context
population. Use terms such as:

- `WikiText-conditioned model output marginal`;
- `prefill-population output marginal`;
- `decode-position-conditioned marginal`;
- `model-by-corpus next-token distribution`.

Such a quantity depends on model, checkpoint, corpus, tokenizer, prompt and
position policy, stage, decoding/runtime semantics, precision, and serving
state. It is not demonstrated to be a model-only constant.

## Component-wise readout-subspace gate

Any future claim about an invariant, shared, semantic, workspace, confidence,
error, or safety readout subspace must report its material components rather
than characterizing the subspace from only the top direction.

Freeze and report at least:

- eigenspectrum or singular spectrum and normalization convention;
- energy share, participation ratio, rank rule, and conditioning;
- sign and basis indeterminacy handling;
- per-component token, logit, hidden-state, and objective-outcome effects;
- stability across independent fits, corpora, positions, stages, precisions,
  runtimes, and checkpoints;
- component alignment or matching rules chosen without sealed outcomes;
- residual unexplained energy and omitted components.

A top direction explaining 48% of readout energy does not authorize assigning
its interpretation to the remaining 52%. Several directions with similar token
poles do not establish one mechanism without subspace, perturbation, and
outcome evidence. A smaller component with a different lexical or orthographic
signature must be reported separately rather than averaged away.

Basis-vector interpretations are not unique under eigenvalue degeneracy or
near-degeneracy. Where applicable, compare invariant subspaces and principal
angles in addition to individual directions. Post-hoc rotations chosen to make
components interpretable are exploratory unless the rotation rule was frozen
before evaluation.

## Model-output-marginal comparator gate

Compatible Jacobian, hidden-state, direct-lens, sparse-feature, and router
monitor studies must include a model-output-marginal comparator when the
claimed signal has token or logit coordinates.

The comparator must freeze and report:

- exact model and runtime artifact;
- context corpus and immutable example manifest;
- message boundaries and prompt construction;
- prefill versus decode stage;
- token-position and attention-mask policy;
- whether teacher forcing, greedy generation, sampling, or tool trajectories
  produced the contexts;
- temperature, logit processing, vocabulary masking, and normalization;
- number of examples, positions, effective tokens, and weighting rule;
- accumulation precision, distributed merge rule, and determinism;
- tokenizer, vocabulary, special-token, and unused-token identities.

At minimum, compare the candidate readout against:

1. external corpus unigram frequency;
2. the model-by-population output marginal;
3. same-boundary final logits, token probability, rank, margin, entropy, and
   surprisal;
4. embedding and unembedding norms;
5. token length, word-boundary form, byte-fallback state, language, script,
   Unicode category, and special or unused-token status;
6. raw hidden-state and direct/logit-lens baselines;
7. corpus-, answer-, prompt-family-, and tokenizer-matched controls.

The model output marginal must be estimated on training/development populations
only for feature selection or calibration. Sealed outcomes, generated answers
unavailable at the monitoring boundary, future tool results, and post-decision
feedback may not enter its construction.

A model-output marginal computed on the same fitting corpus is a
model-by-corpus comparator. Superior marginal correlation over an external
unigram count does not establish a model-intrinsic prior, causal computation, or
semantic representation. Cross-corpus and same-corpus refit tests remain
mandatory.

## Orthographic, tokenizer, and extraction-artifact gate

Lexical-confound controls must extend beyond ASCII punctuation and ordinary
word frequency when vocabulary-wide token effects are interpreted.

Where compatible, freeze and evaluate:

- Unicode general category and script;
- private-use-area codepoints;
- compatibility characters and ligatures;
- Unicode normalization forms and normalization instability;
- control, combining, replacement, and zero-width characters;
- byte-fallback and invalid-byte encodings;
- OCR or PDF-extraction residue;
- typographic versus ASCII punctuation;
- whitespace, newline, indentation, and formatting tokens;
- unused, reserved, sentinel, special, and never-observed tokens;
- multilingual, transliterated, mixed-script, and homoglyph tokens;
- tokenizer merges, word-initial markers, token length, and character count.

Extreme-token lists are descriptive diagnostics, not confirmatory evidence by
themselves. The token-decoding rule, number of poles inspected, sign
orientation, normalization, and artifact taxonomy must be frozen for
confirmatory claims. Features invented after inspecting token poles are
exploratory and must not be included in the preregistered verdict.

A direction aligned with OCR residue, private-use glyphs, punctuation, token
length, or unused vocabulary slots is classified as lexical, orthographic,
tokenizer, or corpus-artifact structure unless it demonstrates sealed
incremental objective-outcome value beyond those controls.

## Feature-decomposition and residual-evidence gate

A feature regression or probe must separate explanation of the readout from
prediction of objective outcomes.

Report separately:

- univariate and multivariate fit;
- adjusted and held-out variance explained;
- coefficient stability and multicollinearity diagnostics;
- partial or residual effects after model-marginal, unigram, token-form,
  embedding, and logit controls;
- train/development/test separation;
- cross-corpus, cross-position, cross-stage, and cross-runtime transfer;
- residual monitor discrimination, calibration, coherence, and policy utility.

A high adjusted R-squared against token descriptors means the direction is
describable by those descriptors on that population. It does not establish that
the model internally computes the named feature, that the feature causes model
behavior, or that the direction predicts correctness or safety.

A low fit from an incomplete feature set means `unexplained by the frozen
features`, not intrinsically semantic. A later post-hoc feature that explains
the residue must be labeled exploratory until independently preregistered and
replicated.

## Fit-budget identity and convergence gate

The number of fitting prompts is a scientific artifact identity, not merely a
resource log. Freeze and report:

- prompt count and effective non-padding token count;
- sequence-length and position distributions;
- number of independent examples, documents, episodes, and trajectories;
- sampling and replacement policy;
- fit seed, sharding, accumulation precision, and merge rule;
- stopping rule, convergence diagnostic, and retry budget.

Cross-lens map, boundary, direction, or atlas comparisons using materially
different fit budgets are inadmissible unless either:

1. the fit budgets and effective-token distributions are matched; or
2. a prospectively frozen budget sweep demonstrates convergence relative to a
   same-corpus seed null for every claimed object.

A fit is not `converged` because a larger budget was used or because one scalar
statistic stabilized. Convergence must cover the relevant map, boundary,
subspace, readout, and objective-monitor metrics. If the largest tested budget
still changes the claimed object beyond the seed null, report `not converged`.
If the measurement cannot resolve the seed null, report `underresolved`.

The external fit-budget campaign is currently preregistered only. It supplies no
result and no evidence that 24, 100, 200, or 400 prompts are sufficient for any
jLens or public lens artifact.

## Monitor and intervention claim boundary

Model-marginal alignment, token-frequency alignment, orthographic structure,
subspace compactness, or fit convergence does not by itself establish:

- objective correctness or error awareness;
- semantic or global workspace identity;
- planning, intent, evaluator awareness, or deception;
- recoverability, tool safety, or permission compliance;
- safe early exit, retry, repair, truncation, routing, steering, or production
  control.

Passive sealed monitor value, causal intervention effects, and policy utility
remain separate claims. No model-marginal, lexical, orthographic, or component
score may be converted into a reward, route target, abort rule, or production
veto without its separately admitted intervention protocol.

## Agents-A1 scaling consequence

The technically credible Agents-A1 sequence is now:

1. Complete Q35Q production-path provenance, strict loading, forward parity,
   activation-VJP parity, activation-JVP parity, finite-difference parity, and
   deterministic replay.
2. Separately admit Agents-A1-4B and establish deterministic checks, external
   verifiers, logits, confidence, visible trajectory, memory, program-state,
   and simple hidden-state baselines.
3. Freeze fit corpus, prompt budget, effective-token budget, stage, position,
   and same-corpus refit nulls before fitting an Agents-A1-4B Jacobian lens.
4. Establish budget convergence or scope every lens artifact to its exact fit
   budget.
5. Decompose material readout components and compare each against external
   unigram, model-by-population output marginal, logits, embedding norms,
   tokenizer structure, Unicode/orthographic artifacts, raw states, and direct
   lenses.
6. Require residual sealed objective-error value after all lexical,
   output-prior, corpus, stage, and answer-identity controls.
7. Separately admit Agents-A1-35B hidden-state, cache, router, expert-path,
   quantized, topology, and serving capture.
8. Refit and re-estimate every corpus-, budget-, stage-, checkpoint-, and
   runtime-sensitive artifact on 35B rather than importing 4B or public-atlas
   coordinates.
9. Establish nominal and functional routing, occupancy, ancestry, transition,
   token-frequency, trajectory-phase, route-regret, and model-marginal
   comparators.
10. Require router and Jacobian features to add sealed objective-outcome value
    beyond the complete external, 4B, raw-state, direct-lens, lexical,
    model-marginal, corpus-aware, budget-aware, and route-aware stack.
11. Keep projection, ablation, activation steering, early exit, retry, repair,
    truncation, forced routing, router adaptation, and production enforcement
    separately gated.

This adds model-output-marginal, component, orthographic, and fit-budget controls
to future fit and transfer studies. It does not change the active Q35Q
engineering milestone and authorizes no new execution.

## Current engineering blocker remains unchanged

The active milestone remains complete production-path Q35Q provenance and
runtime admission:

1. verify frozen upstream-wheel and installed-distribution bytes in the same
   controlled subprocess;
2. reject shadow packages, editable installs, pre-imported modules, and
   in-memory monkeypatching;
3. execute the complete adversarial provenance conjunction in the target
   runtime;
4. freeze GPTQModel, Defuser, Optimum, Accelerate, PyTorch, CUDA, and
   `GPTQ_TORCH` as one immutable tuple;
5. bind the actual GPTQModel/Defuser loader and its complete live-object source
   closure;
6. run the strict synthetic Qwen3.5-MoE loading fixture;
7. prove one-time packed-tensor consumption and exact expert/fusion ordering;
8. prove deterministic forward, activation-VJP, activation-JVP, and
   finite-difference parity; and
9. complete Phase-0 admission before weight staging or GPU authorization.

## Established by this correction

- A model-by-population output marginal is now a mandatory token/logit readout
  comparator where compatible.
- External unigram frequency is not the sole required lexical or prior control.
- Material readout-subspace components must be interpreted separately.
- Unicode, private-use, ligature, OCR/PDF, tokenizer, and unused-token artifacts
  are mandatory compatible controls.
- Fit prompt and effective-token budget are binding lens-artifact identities.
- Cross-budget atlas comparisons require matched budgets or prospective
  convergence evidence against a same-corpus seed null.
- No privacy, sealed-data, verifier, provenance, derivative, intervention,
  resource, or production gate is weakened.

## Still unproven

- Independent reproduction of the external readout decomposition.
- A model-intrinsic default-output or unigram-prior direction.
- Causal computation of the reported token descriptors.
- Replication of prior-like or orthographic components across models, corpora,
  stages, tokenizers, quantizations, or runtimes.
- Any result from the pending external fit-budget experiment.
- Fit-budget convergence for public Jacobian lenses, Q35Q, Agents-A1-4B, or
  Agents-A1-35B.
- Objective correctness, safety, planning, or recoverability prediction from
  the reported directions.
- Q35Q runtime admission, strict tensor consumption, expert ordering, forward
  parity, or derivative parity.
- Safe early exit, retry, repair, truncation, forced routing, activation
  steering, or production deployment.
