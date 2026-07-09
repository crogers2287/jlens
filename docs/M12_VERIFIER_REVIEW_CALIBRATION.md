# M12 — verifier hardening + reviewed escalation calibration

The first live Agents-A1 run (M11) surfaced one auto-wrong candidate that turned
out to be a **verifier** problem, not a model problem. M12 fixes the verifier,
reviews the escalated live records, computes the first auto-vs-human agreement,
and shows the before/after impact — all without leaking any prompt/output text.

## The M11 finding

The JSON task escalated with `auto_was_wrong=True`, but Agents-A1 had returned a
valid JSON object. The old `regex_or_schema_check` used `^\{.*\}$` — full-string
anchors, no DOTALL — so any trailing prose or newline after the JSON failed the
match. A **false-positive from the checker**, exactly why `auto_outcome` is only a
candidate and why escalated records get reviewed.

## The fix: a JSON-aware verifier

`src/verifiers.py` gained `json_object_check(output, required_keys, expected_type)`:

- strip whitespace and `json.loads`; on failure, extract the first balanced
  `{...}`/`[...]` substring (brace matching that respects strings/escapes) and
  parse that — so leading/trailing prose and markdown fences are tolerated;
- optionally check the expected type (object/array) and that all required keys
  are present;
- PASS on valid JSON meeting requirements, FAIL otherwise; evidence is hashed,
  never raw text.

`regex_or_schema_check` is **unchanged** — kept for true regex tasks only.

### Routing (JSON vs regex)

In `autonomous_shadow_supervisor._run_verifiers`, a task with `json_check: true`
(or a `json_required` key list) now runs `json_object_check`; the regex verifier
is guarded to skip JSON tasks. `json_object_check` was also added to the
`CORRECTNESS` set so its verdict actually feeds `auto_was_wrong` (a correctness
verdict must count as correctness). The confidence/escalation **thresholds are
unchanged** — only the verifier wiring was completed. The public smoke fixture's
JSON row (`sm_regex_01`) now uses `json_check` + `json_required: ["result"]`
instead of a full-anchor regex.

## Reviewing the 7 escalated live records

The escalated subset was reviewed against **public benchmark ground truth**
(these are objective tasks — 6×7=42, capital of France = Paris, a syntactically
valid JSON object ⇒ not wrong). Rules kept honest:

- set `outcome.was_wrong` only where objectively determinable; `review_source =
  "operator_review"`; leave anything undeterminable `null` (never false);
- the reviewed queue stays in the **gitignored** private dir — its text is never
  committed;
- `auto_outcome` remains a candidate, never promoted to gold by this review.

All 7 outputs were objectively correct (the JSON row included). The reviewed
records are validated against `schema/auto_outcome_v1.json`.

## First auto-vs-human agreement

`src/agents_a1_run_report.py` over the reviewed queue →
`reports/outcomes/agents_a1_reviewed_summary_sample.json` (aggregate-only, no
text). Agreement compares only rows where **both** `auto_was_wrong` and human
`was_wrong` are set:

- `auto_vs_human_agreement = { n_compared: 1, agreement_rate: 0.0 }`
- `human_reviewed_count: 7`

Agreement is 0% on the single comparable row precisely because that row was the
verifier false-positive (auto = wrong, human = right). The 6 explain rows were
reviewed correct but had `auto_was_wrong = null` (escalated on low confidence, no
applicable verifier), so they don't enter the agreement denominator.

## Before / after

`reports/outcomes/agents_a1_verifier_beforeafter_sample.json` (counts only):

| | verifier | escalation_count | auto_was_wrong_count |
|---|---|---|---|
| before | regex_full_anchor | 7 | 1 |
| after | json_object_check | 6 | 0 |

On a representative valid-JSON+trailing-prose output the old regex **fails** and
`json_object_check` **passes**, so the JSON row flips wrong→ok and no longer
escalates (delta −1 / −1). The stored 160-char preview can't hold the full live
output, so the JSON verdict is re-scored on a representative output; the batch
delta follows from that single verified flip.

## Gating (unchanged)

- `auto_outcome` is a **candidate, not gold** — promoted only by a later audit.
- The autonomous run never writes human `outcome`/`review_meta` fields.
- Only aggregate-only artifacts are committable; `check_commit_safe.py` gates it;
  private raw/reviewed records stay gitignored.
- **Production/final thresholds stay gold/audit gated** until enough
  human-reviewed real-workload records exist. This review + the corrected checker
  are how those reviewed records start to accumulate honestly.
