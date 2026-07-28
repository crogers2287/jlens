# STEER ADDENDUM — Spectral hidden-state rank, length, centering, and retrospective-boundary gates

Date: 2026-07-28
Status: **binding protocol correction; design-only; no capture authorization**

This addendum incorporates the minimum controls implied by `D-Score: A Spectral
Hidden-State Signal for Hallucination Detection in Large Language Models`
(arXiv:2607.24586v1). It strengthens the forward-only comparator stack without
weakening any privacy, sealed-data, verifier, provenance, derivative, GPU,
intervention, or production gate.

The external result is evidence that a cheap scalar derived from the singular
spectrum of a completed sequence's hidden-state matrix can carry error-related
information under some model and dataset conditions. It is not evidence of a
model-intrinsic truth circuit, prospective error awareness, semantic workspace
content, causal conflict computation, safe stopping, or transfer to Agents-A1.

## Binding correction

A spectral hidden-state comparator is now mandatory before assigning
incremental value to router, sparse-feature, transcoder, directional-derivative,
Jacobian, or semantic-workspace features in a compatible completed-error study.

The comparator must remain a separately identified block. It may not be hidden
inside a generic learned classifier, pooled with route features, or described as
Jacobian evidence.

For M39 and compatible successors, the forward-only ordering is:

1. frozen nuisance, output, and confidence baselines;
2. ordinary residual-state summaries;
3. frozen spectral hidden-state summaries;
4. router and expert-path summaries;
5. frozen combinations of the preceding blocks;
6. sparse-feature or transcoder comparators;
7. Jacobian or derivative features only after separate derivative admission.

No block may receive credit for information already available to a cheaper
preceding block.

## Object identity

Every spectral score is an artifact of the complete tuple below, not a portable
property of the checkpoint:

- exact checkpoint and revision;
- tokenizer and special-token policy;
- runtime, precision, quantization, kernels, topology, batching, and cache state;
- exact hidden-state boundary, including pre/post normalization and residual
  convention;
- exact layer or prospectively frozen layer set;
- exact token population: prompt, response, prompt-plus-response, prefill,
  decode, or another explicitly named boundary;
- inclusion or exclusion of BOS, EOS, tool delimiters, padding, masked tokens,
  images, retrieved context, system instructions, and verifier text;
- sequence-length and truncation policy;
- centering, scaling, whitening, and token-normalization policy;
- matrix orientation and accumulation dtype;
- spectral estimator, tolerance, iteration count, stopping rule, random seed,
  maximum recovered rank, and invalid-value behavior;
- calibration population, threshold, and missingness rule.

Changing any material member creates a new spectral instrument requiring
separate calibration and transfer evidence.

## Retrospective-versus-prospective boundary

A score computed from the completed generated response is a retrospective
completed-error feature. It may not be represented as prefix-level detection,
early available knowledge, pre-action monitoring, or an early-exit signal.

Compatible work must separately identify:

- feature-availability time;
- final generated token included in the matrix;
- answer exposure time;
- verifier-label time;
- decision time;
- intervention time.

A prospective prefix study must recompute the instrument using only tokens and
states available at each frozen prefix. It must not select the prefix, layer,
tolerance, or threshold using the final answer, future tokens, verifier result,
or full-sequence spectrum.

Full-response performance cannot authorize early exit, truncation, retry,
repair, abstention, routing intervention, activation steering, or production
control.

## Length and position confound gate

A rank-like score whose maximum and spectrum depend on token count must not
receive scientific credit until length and position are controlled.

The minimum compatible analysis must include:

1. exact prompt, response, and total token counts in the nuisance baseline;
2. length-stratified calibration and held-out reporting;
3. matched-length correct/incorrect comparisons where information permits;
4. fixed-window or prospectively frozen subsampling controls;
5. prefix-position controls at matched token counts;
6. padding and masking adversarial tests;
7. truncation and missing-final-answer strata kept separate from completed
   correctness;
8. a length-only classifier and frozen length-interaction terms;
9. transfer tests across materially different output budgets.

If the spectral increment disappears after these controls, the supported result
is a length- or position-conditioned signal, not hidden correctness awareness.

## Centering and normalization gate

Uncentered hidden matrices can be dominated by mean-state, residual-norm,
position, lexical, formatting, or special-token structure. Compatible studies
must prospectively compare at least:

- uncentered hidden states;
- token-centered hidden states;
- feature-centered hidden states when technically meaningful;
- per-token norm-normalized states;
- the admitted model's actual normalized boundary;
- raw-state energy and residual norm controls.

Centering or normalization variants are separate confirmatory comparisons and
must enter the multiplicity plan. The best variant may not be selected after
held-out outcomes are visible.

A result stable only under one post-hoc normalization is exploratory.

## Required spectral comparator family

The launch amendment must freeze a compact nonredundant family containing the
proposed relative numerical rank and cheaper neighboring summaries. At minimum:

- leading singular value;
- Frobenius norm or total spectral energy;
- stable rank;
- effective rank or spectral entropy;
- participation ratio;
- the frozen relative-rank count at each admitted tolerance;
- a frozen top-spectrum slope or concentration summary;
- exact failure/lower-bound flags when the estimator stops at its rank cap.

The family must be small enough for prospective multiplicity control. Searching
large grids of layers, tolerances, centering rules, windows, or spectrum
statistics after outcome inspection is prohibited.

Singular vectors, token projections, or full Gram matrices are not required for
this comparator and may not be retained merely because the scalar score is
useful.

## Numerical verification gate

The spectral implementation must pass non-outcome-bearing fixtures that prove:

- agreement with exact CPU SVD or eigendecomposition on small matrices;
- deterministic behavior under the frozen seed and runtime;
- correct masking and padding exclusion;
- correct handling of zero, rank-deficient, constant, repeated-token, and
  near-threshold matrices;
- explicit lower-bound behavior when the maximum recovered rank is reached;
- bounded approximation error around threshold crossings;
- finite-value and dtype behavior under the admitted precision;
- enabled-path versus disabled-path model-output parity;
- resource ceilings for memory, latency, bandwidth, and on-device reduction.

Approximate power iteration or another partial solver may not silently report an
exact rank when convergence or threshold crossing is unresolved.

## Layer-selection and calibration gate

A best-performing layer selected on evaluation outcomes is diagnostic evidence,
not an admitted detector.

Compatible confirmatory work must freeze layer, tolerance, normalization,
window, and decision threshold using training and calibration data only. Every
selection step must occur inside source-lineage-grouped folds. Locked held-out
outcomes may not influence:

- layer selection;
- tolerance selection;
- score family selection;
- centering or normalization;
- length strata;
- threshold selection;
- block combination;
- missingness or exclusion rules.

Cross-family and cross-runtime transfer must be reported without threshold
retuning before any portability claim.

## Claim boundary

A high-dimensional or flatter hidden-state spectrum may reflect many causes,
including lexical diversity, formatting, sequence length, multiple topics,
retrieved evidence, tool transcripts, uncertainty, contradiction, correction,
or ordinary task complexity.

A predictive spectral score does not by itself establish:

- internally recognized falsity;
- encoded counter-evidence;
- conflict computation;
- semantic workspace occupancy;
- a reasoning phase transition;
- causal participation in the answer;
- recoverability or safe intervention.

Those claims require separately frozen nuisance controls, natural-label
variation, causal tests, and objective outcomes.

## MoE and Agents-A1 gate

Agents-A1-35B adds route-, expert-, quantization-, and serving-dependent sources
of spectral variation. A compatible study must therefore:

1. complete Q35Q provenance, strict loading, forward parity, VJP/JVP parity, and
   finite-difference admission first;
2. establish the spectral family on the separately admitted Agents-A1-4B or a
   tractable bridge model before 35B capture;
3. freeze prefill and decode matrices separately;
4. preserve prompt, response, tool, observation, and action-stage identities;
5. compare spectral features against raw-state energy, logits, confidence,
   trajectory, memory, verifier, and program-state baselines;
6. separately admit the 35B checkpoint, router, experts, quantization, topology,
   runtime, and capture path;
7. report route-load, expert-path, and spectral features as distinct blocks;
8. test whether route or Jacobian features add sealed value after the spectral
   block;
9. refit and recalibrate on 35B rather than transferring 4B layers or thresholds;
10. retain full-compute and no-intervention defaults unless a separate control
    protocol passes.

The D-Score paper's dense 7B-8B completed-text results do not authorize transfer
to a large quantized MoE, long-horizon tool trajectory, prefix monitor, or
production decision.

## Privacy and sealed-data boundary

Only the minimum prospectively frozen scalar or low-dimensional summaries may
leave the worker, and they remain private per-task data.

The public repository may contain only aggregate counts, aggregate metrics,
protocol identities, code, tests, and fail-closed status. It may not contain raw
prompts, responses, token IDs, hidden states, singular vectors, Gram matrices,
per-example spectra, routes, expert IDs, predictions, labels, split assignments,
or secret-linked provenance.

Verifier outcomes remain sealed until feature extraction and immutable row
identity are complete.

## Decision rule

A spectral block advances only if it clears the complete existing parity,
provenance, privacy, power, calibration, minimum-effect, multiplicity,
family-disjoint, length-control, locked-held-out, and cost gates.

A positive result establishes only completed-error predictive increment for the
exact frozen model, runtime, population, sequence boundary, and spectral
instrument. A negative result must be recorded and stops that branch without
post-hoc layer, tolerance, normalization, or length-window search.

This addendum does not authorize capture, weight staging, GPU use, Jacobian
execution, intervention, or production deployment. Q35Q remains blocked until
the complete Phase-0 conjunction passes.
