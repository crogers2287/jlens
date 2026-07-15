# M39 STATUS — ReasoningLab paper/code provenance drift

Audit time: `2026-07-15T17:20:51Z`

Status: **aggregate-only external-provenance record; no M39 capture authorization and no steer change.**

This record applies the binding provenance gate in
`docs/STEER_ADDENDUM_2026-07-15_M39_METACOGNITION_TEMPORAL_AND_EARLY_EXIT_BOUNDARY.md`.
It does not alter M38E, Q35Q, M39 task populations, thresholds, comparators,
verifier rules, sealed-data rules, resource ceilings, production gates, or the
monitoring-versus-control boundary.

## Audited identities

- jLens head before this record:
  `35bed30a1dcf5a69b54172d7ec6af03561aa8ba6`.
- External repository:
  `CarloDiCicco/ReasoningLab`.
- Audited external head:
  `952d34441a42e7765d8bd30df5286f747087299b`.
- Referenced paper:
  `Code Correctness Signals in LLM Hidden States: Pre-Generation Probing and Repair Geometry`,
  arXiv `2606.14530v2`.

## Material unsynchronized changes

The current external repository no longer matches the current arXiv v2 claims.
At the audited repository head, the paper source and README report:

- raw nested-CV pre-generation AUC `0.881 +/- 0.008`;
- prompt-length-residualized AUC `0.842 +/- 0.010`;
- prompt-length-only AUC `0.657 +/- 0.014`;
- layer selection spread across layers 29-36, with layer 30 modal in only
  `16/50` outer splits;
- the repair-direction question as a null result because successful repairs are
  too sparse for reliable geometric analysis.

The current arXiv v2 landing page instead reports raw/residualized/prompt-only
AUCs of `0.955 / 0.940 / 0.720` and a repair-success direction surviving its
reported conditional residualization. The source repository therefore changed
materially after the paper version now cited by M39.

## Follow-up audit 2026-07-15T23:16:10Z

The external repository advanced by two commits after the original audit:

- `1c96602489af1b2332bbfd13d59f3453d095d3b7` refined README terminology;
- `5925dc6a7a3fa6242479ecf30fb7f13eac40bd6f` refined abstract and probe-section
  terminology and formatting.

The new external head remains numerically and scientifically aligned with the
repository state audited above: raw/residualized/prompt-length AUCs remain
`0.881 / 0.842 / 0.657`, and self-repair geometry remains unsupported because
successful repairs are too sparse. The two commits do not reconcile the
repository with arXiv `2606.14530v2`, do not publish a matched immutable paper
revision, and do not supply an independently reproduced implementation.

The provenance block therefore remains fully in force. Continued upstream
wording edits are not evidence for changing an M39 feature, layer, comparator,
threshold, power prior, or launch gate.

## Binding consequence

Until a matched immutable paper/code pair is published and reproduced, this
external work is **provenance-blocked for quantitative or implementation
adoption** inside M39.

Specifically:

1. Do not import a reported AUC, selected layer, repair direction, exact feature
   formula, hyperparameter, or claimed effect from the mutable external head.
2. Do not treat either the arXiv v2 numbers or the current repository numbers as
   an Agents-A1 expectation, power prior, threshold basis, or layer-selection
   basis.
3. The already-binding train-fold-only nuisance-control principle remains valid
   as an independently specified jLens design rule; it does not depend on this
   source's current quantitative claims.
4. Admission of any source-specific implementation requires, before M39
   capture, an exact arXiv version, immutable repository commit, matching
   abstract/README/source tables, license and dependency identities, exact
   formulas, synthetic tests, reproduction hashes, and a repository privacy
   scan.
5. Continued upstream edits do not permit iterative M39 feature, layer,
   comparator, or threshold changes after any outcome-bearing capture.

## Program effect

No steer amendment is warranted. The existing M39 provenance gate correctly
fails closed on this mismatch. M38E remains mandatory to finish unchanged;
Q35Q remains blocked pending real artifact admission and GPU release; M39
remains capture-prohibited until its existing launch conditions are satisfied.

No raw tasks, prompts, outputs, token IDs, hidden states, routes, feature
vectors, predictions, verifier labels, model artifacts, local paths, secrets, or
per-example data are recorded here.

The research program remains incomplete and production remains gated.
