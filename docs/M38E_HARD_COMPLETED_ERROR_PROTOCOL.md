# M38E — Hard completed-error benchmark protocol

## Purpose

M38E tests whether jLens can recognize genuine wrong completed answers from
Agents-A1. It is separate from M36T, which predicts excessive reasoning length
and token-budget truncation.

The benchmark must be difficult enough to produce completed errors, but not so
difficult that nearly every answer fails. Individual known failures may not be
hand-picked.

## Candidate families

Prefer fresh, deterministic, objectively scored tasks:

1. multi-step modular arithmetic and congruence problems;
2. symbolic or algebraic transformations with canonical exact answers;
3. logical deduction, constrained ordering, and object tracking;
4. executable code tasks from an already-local public dataset with deterministic
   unit tests;
5. public MATH/AIME-style material only as a secondary transfer check.

Procedural generators are preferred where practical to reduce benchmark
contamination. Every generator and verifier must be deterministic and tested.

## Development difficulty sweep

Commit a development manifest before live capture. Freeze candidate families,
difficulty bands, 24–32 tasks per band, seeds, dataset revisions, verifiers,
decode protocol, selection rule, and stop conditions.

Use enough decode headroom that a wrong label normally means a completed wrong
answer rather than a timeout:

- start at 2,048 output tokens;
- move an entire band to 4,096 only when truncation exceeds .10 and a bounded
  pilot shows the larger cap materially reduces it;
- do not mix caps inside a primary band estimate.

An eligible band must have:

- completion rate at least .90;
- truncation rate at most .10;
- verified raw pass rate between .20 and .80;
- at least 6 completed correct and 6 completed incorrect development examples;
- an objective verifier or executable test suite;
- enough unseen task space for a sealed holdout.

Require at least two eligible families and at least 48 completed incorrect
examples across development. Otherwise commit
`m38e_completed_error_frontier_not_found` and stop.

Band selection is based only on aggregate development performance. Never select
individual sealed questions because the model previously missed them.

## Features and comparators

The correct answer and verifier result are labels only and may not enter a
prediction feature.

Freeze transparent comparators on development data:

1. metadata only;
2. metadata plus output length and finish reason;
3. metadata plus token-confidence summaries;
4. metadata plus router summaries;
5. full approved jLens telemetry.

Use only transparent models already used in the project, such as calibrated
logistic regression or nearest centroid. No hidden-state capture, large learned
head, or sealed-set feature discovery.

The primary population is completed, nontruncated answers. Timeout prediction
belongs to M36T and must not inflate M38E results.

Where a trusted deterministic solver exists, a separate routing policy may be
frozen. Families with only an answer-key verifier contribute to detection claims,
not repair claims.

## Sealed benchmark

Commit the sealed manifest before generating or opening outcomes. Freeze the
checkpoint, runtime and telemetry hashes, eligible bands, disjoint seeds, task
counts, family weights, decode cap, verifier hashes, features, model, calibration,
threshold, selection budget, random seeds, bootstrap settings, confidence
intervals, and claim rules.

Choose N from 192, 240, or 288 using a predeclared power calculation. Require at
least 24 expected completed errors overall and at least 8 in each primary family.
Target:

- raw verified success approximately .30–.70 overall;
- at least two primary families;
- truncation at most .10;
- no more than .60 of tasks from one family.

## Confirmatory questions

- **E-H1:** full jLens improves balanced accuracy and average precision for
  completed-error prediction over metadata plus confidence, with both paired 95%
  lower confidence bounds above zero.
- **E-H2:** full jLens beats router-only and count-matched random error selection
  at the frozen selection budget.
- **E-H3:** on tool-eligible tasks and at the same tool-call count, full jLens
  improves verified success over metadata routing and random routing without
  right-to-wrong regressions.
- **E-H4:** when tool-all exists, full jLens is non-inferior within .02 verified
  success while making significantly fewer calls.

Report raw accuracy, completed-error prevalence, truncation, malformed outputs,
prediction metrics, calibration, corrections, misses, false alarms,
right-to-wrong regressions, tool use, tokens, latency, overhead, and per-family
results.

Stop after the M38E result and request an operator decision.