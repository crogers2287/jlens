# M17 — reviewed calibration pass

Before scaling to bigger runs, this milestone asks a plain question of the data:
**what do the human-reviewed records actually say?** It consolidates the reviewed
subsets from M11–M16 into a category-level calibration summary — counts, agreement
where comparable, fixed findings, remaining gaps — without committing any private
prompt/output text.

```bash
python src/reviewed_calibration_report.py \
    --out reports/outcomes/agents_a1_reviewed_calibration_summary.json
```

Private reviewed logs are read **locally** for per-category detail; only the
aggregate summary (no task text) is committed, gated by `check_commit_safe.py`.

## What the reviewed data says

Across the reviewed subsets: **44 records scanned, 19 human-reviewed, 3
objectively comparable** (both an auto verdict and a human `was_wrong` set).

| category | reviewed | comparable | agreement | status |
|---|---|---|---|---|
| exact | 2 | 2 | 0.0 | usable_shadow |
| regex | 1 | 1 | 0.0 | usable_shadow |
| explain-rubric | 1 | 0 | — | needs_more_review |
| open-explain | 15 | 0 | — | verifier_gap |

The two 0.0-agreement rows (exact, regex) are not a live problem — they are exactly
the **two verifier false-positives that human review found**, both since **fixed**:

- **JSON false-positive** — a valid JSON object rejected by a full-anchor regex,
  fixed in **M12** (`json_object_check`). (It shows under `regex` because that was
  the verifier at review time.)
- **numeric false-positive** — an approximate / unit-converted answer rejected by
  strict exact-match, fixed in **M14** (`numeric_tolerant_check`) and **M16**
  (metadata normalization so numeric-answer rows route there).

So the only objectively comparable reviewed rows were the false-positives the loop
caught and corrected — the honest calibration story, not a current regression.

## Category maturity

- **usable_shadow** (exact, numeric, json, math, regex): checkable categories with
  deterministic verifiers; the known false-positives are fixed. Ready to carry more
  shadow load.
- **needs_more_review** (explain-rubric): the rubric verifier works but synonym
  matching is basic — a synonym mismatch escalates for review (as designed) rather
  than marking wrong. More reviewed rubric rows would tighten this.
- **verifier_gap** (open-ended explain): no objective verifier exists, so these
  escalate on low confidence and can't be compared. This is the biggest remaining
  gap — a rubric/reference-answer strategy is needed before they count.

## Action routing (planned-only)

The M16 read-only action layer, over the M15 run, produced **planned** counts
(nothing executed): `retrieval_needed 12`, `checker_needed 160`, `review_needed 19`,
`no_action 70`. These are carried into the calibration summary as planned-only —
they are suggestions, not executed successes.

## Gating (unchanged)

- `auto_outcome` is a **candidate, not gold**; agreement is computed only over
  comparable reviewed rows; tiny-n numbers are indicative, not production.
- Action-routing outcomes are **planned-only**, never executed-success.
- Only aggregate-only artifacts are committable; private reviewed logs stay
  gitignored.
- **Production/final thresholds stay gold/audit gated** until enough human-reviewed
  real-workload records accumulate — this summary is the honest scoreboard of how
  far along that is, per category.
