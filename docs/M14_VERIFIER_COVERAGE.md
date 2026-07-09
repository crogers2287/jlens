# M14 — numeric-tolerant verifier + explain coverage

The M13 live run surfaced a second verifier-strictness false-positive: the model
answered the speed of light as 299,792,458 m/s ≈ 299,792 km/s (correct), but
`exact_answer_match` wanted the literal string "300000" and failed. M14 fixes that
with a numeric-tolerant verifier and adds a rubric-only verifier for open-ended
explain tasks — without ever pretending subjective answers are gold.

## Numeric-tolerant verifier

`numeric_tolerant_check(output, expected_value, tolerance, rel_tolerance,
expected_units, accepted_values)` in `src/verifiers.py`:

- extracts **all** numbers from the output (thousands separators stripped);
- optionally normalizes simple units (m/km family) when `expected_units` is set;
- **PASS** if any extracted/normalized value is within absolute `tolerance` OR
  `rel_tolerance` (relative) of any accepted target (`expected_value` or
  `accepted_values`);
- **FAIL** when numbers are present but all outside tolerance;
- **UNDECIDED (escalate)** when no reliable number can be extracted or no target
  was given.

Evidence is hashed — never raw text. `exact_answer_match` is **unchanged** and
kept for pure-string exact answers.

## Explain rubric verifier

`explain_rubric_check(output, required_facts)` scores an open-ended explanation
**only** against an explicit public fact checklist:

- counts how many required facts appear (case-insensitive);
- **PASS** only at full coverage;
- **UNDECIDED (escalate)** when the rubric is missing/empty **or** coverage is
  weak.

It **never** returns PASS without a rubric — a subjective explanation is never
called gold. With no checklist it escalates for a human rather than guessing.

## Routing (autonomous_shadow_supervisor._run_verifiers)

- A task with **numeric metadata** (`numeric: true`, or any of `expected_value`,
  `tolerance`, `rel_tolerance`, `expected_units`, `accepted_values`) →
  `numeric_tolerant_check` (instead of `exact_answer_match`).
- A task with **`required_facts`** → `explain_rubric_check`.
- Pure-string exact tasks (`known_answer`, non-numeric, non-math) still →
  `exact_answer_match`.

Both new verifiers were added to the `CORRECTNESS` set so their verdicts feed
`auto_was_wrong`. The confidence/escalation **thresholds are unchanged** — only
the verifier wiring was extended.

## New optional task-metadata fields

| field | meaning |
|---|---|
| `numeric` | mark the task as numeric-scored (route to numeric verifier) |
| `expected_value` | the objective numeric answer |
| `tolerance` | absolute tolerance |
| `rel_tolerance` | relative tolerance (fraction, e.g. 0.01 = 1%) |
| `expected_units` | expected unit for simple normalization (e.g. "km") |
| `accepted_values` | list of additional acceptable numeric targets |
| `required_facts` | explain-task fact checklist (all must appear to PASS) |

Public examples: `data/prompts/agents_a1_numeric_batch.jsonl` (4 numeric + 2
explain-rubric rows).

## Before / after (the M13 flip)

`reports/outcomes/agents_a1_numeric_beforeafter_sample.json` (verdicts/counts
only, no task text):

| | verifier | verdict | auto_was_wrong | escalated |
|---|---|---|---|---|
| before | exact_answer_match | fail | true | true |
| after | numeric_tolerant_check | pass | false | false |

On a representative approximate/unit-converted output, the old exact-match rejects
a correct answer while `numeric_tolerant_check` accepts it — the numeric row flips
wrong→ok and no longer escalates.

## Gating (unchanged)

- `auto_outcome` is a **candidate, not gold**; the run never writes human fields.
- Explain answers are **never** claimed gold without a rubric; weak/absent
  coverage escalates.
- Only aggregate-only artifacts are committable (`check_commit_safe.py` gates it);
  private detailed records stay gitignored.
- **Production/final thresholds stay gold/audit gated** until enough
  human-reviewed real-workload records exist.
