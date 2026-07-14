# Binding addendum — M39 cross-milestone outcome firewall

Date: 2026-07-14

This addendum supplements `steer.md`, `CODEX_AUTOSTEER.md`, the M38E protocol,
all prior binding addenda, and `docs/M39_FORWARD_ONLY_COMPARATOR_PREREG.md`.
Every sealed-data, verifier, privacy, provenance, exact-set, cap-escalation,
resource, retry, statistical, production, and stop rule remains in force.
Nothing here authorizes a restart, retry, M38E modification, M39 scientific
capture, threshold change, task-set expansion, or retrospective reinterpretation.

## 1. Defect closed: M39 did not explicitly prevent adaptive reuse of M38E

M39 is scheduled after M38E finalization, so M38E outcomes will exist before the
M39 launch amendment is written. The current M39 draft requires a new frozen
manifest and locked holdout, but it does not explicitly prohibit using M38E rows,
labels, family outcomes, eligibility results, error counts, or telemetry analyses
to select the M39 population, layers, features, endpoints, thresholds, or models.
That leaves a false-confirmation path through adaptive cross-milestone reuse.

Adaptive reuse of outcome-bearing data can overfit the next hypothesis or
validation rule even when the later analysis uses nominal cross-validation. The
general statistical issue is described by Dwork et al., `Generalization in
Adaptive Data Analysis and Holdout Reuse` (arXiv:1506.02629). This addendum closes
the project-specific path prospectively, before M38E finalization and before any
M39 scientific row exists.

## 2. M38E outcome-bearing material is not M39 confirmatory data

For any confirmatory M39 run:

1. No M38E scientific row may enter M39 training, calibration, validation,
   held-out evaluation, feature discovery, layer selection, classifier selection,
   threshold selection, or error analysis.
2. No M38E task instance, repeated generation, paraphrase, difficulty variant,
   source problem, or derived row may be relabeled or recast as an M39 row.
3. M38E verifier labels, truncation outcomes, eligible-band decisions, completed-
   error counts, predictions, telemetry features, hidden summaries, routes,
   expert contributions, and per-family performance remain outside the M39
   confirmatory pipeline.
4. Running an M39-style feature extractor retrospectively on M38E rows is
   exploratory only. Such results must remain sealed and may not influence the
   confirmatory launch amendment or be presented as M39 validation.
5. M38E may determine only the already frozen program-level go/stop sequence.
   It does not become a development set for M39.

## 3. Required independent M39 population

The M39 launch amendment must freeze a fresh outcome-blind population before any
M39 outcome-bearing capture. It must provide:

1. task instances and generation seeds disjoint from M38E;
2. no shared source instance, paraphrase cluster, repeated generation, or derived
   variant crossing the M38E/M39 boundary;
3. an immutable manifest and digest produced without reading the private M38E
   ledger or M38E per-row outcomes;
4. a deterministic source-lineage audit proving cross-milestone disjointness;
5. frozen family, band, difficulty, cap, repetition, ambiguity-stratum, and
   verifier-family allocations that do not depend on M38E family success,
   eligibility, class balance, or feature behavior;
6. fresh train/calibration/validation/held-out split groups entirely internal to
   M39, with the existing grouped-split and locked-holdout rules unchanged.

The same broad generator family may be used only when the launch amendment proves
that instances, seeds, source lineage, and derived variants are disjoint and that
family allocation was not selected because of M38E outcomes. If that proof is
unavailable, the affected family is not confirmatory.

## 4. Permitted and prohibited use of aggregate M38E results

Permitted uses are narrow:

- reporting the final M38E outcome under its frozen protocol;
- applying the already frozen program-level decision about whether M39 may be
  considered next;
- conservative sample-size planning from explicitly named aggregate quantities,
  only when the launch amendment discloses the use before M39 capture and the M39
  evaluation population remains fully independent.

Even for sample-size planning, M38E may not be used to choose favorable families,
layers, phases, features, classifiers, endpoints, effect thresholds, exclusions,
or ambiguity strata. Power assumptions must be conservative and may not encode a
post-hoc favorable effect estimate. External evidence, worst-case planning, or a
separately authorized non-overlapping pilot is preferred.

The following are prohibited:

- dropping or enriching task families because M38E performed poorly or well;
- targeting bands because M38E produced more errors, less truncation, or better
  eligibility there;
- selecting layers or telemetry blocks after inspecting M38E label associations;
- using M38E effect sizes as the M39 minimum meaningful effect;
- treating the observed `mod_chain` escalation facts as justification to exclude,
  replace, or upweight a family in M39;
- pooling M38E and M39 rows to satisfy power or class-balance gates.

## 5. Launch-amendment additions

The M39 launch amendment must now freeze and verify, in addition to every existing
requirement:

1. a cross-milestone disjointness policy and audit implementation;
2. the exact list of any aggregate M38E quantities consulted and their sole
   permitted purpose;
3. a declaration that no M38E per-row outcomes or retrospective M39-style M38E
   analyses influenced the manifest, features, layers, models, endpoints, or
   thresholds;
4. an independent-population provenance digest and source-lineage report;
5. a decision rule that marks M39 `adaptive-contamination-blocked` or
   `exploratory-only` if the firewall cannot be proved.

Missing evidence cannot be reconstructed after M39 outcomes are known. Failure to
prove independence blocks confirmatory capture or interpretation; it does not
permit reusing M38E, weakening a split rule, or relabeling the study exploratory
after inspecting a favorable result.

## 6. Current authorization and claim boundary

- Continue M38E attempt one undisturbed under the exact frozen task set.
- Keep automatic retry fail-closed.
- M38E remains incomplete and has no scientific result.
- M39 remains design-only and capture-prohibited.
- No M39 launch amendment may use M38E as an adaptive development or validation
  set.
- No router, hidden-state, expert-contribution, geometry, path, semantic, or
  Jacobian feature has demonstrated incremental completed-error prediction on
  Agents-A1.
- No safe truncation, early exit, correction, routing intervention, activation
  steering, or production utility is established.
- All raw tasks, outputs, labels, telemetry, states, routes, expert outputs,
  predictions, split assignments, and secret-linked provenance remain private
  and uncommitted.
