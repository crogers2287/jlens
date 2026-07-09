# M16 — action routing + metadata cleanup

Two M15 loose ends, closed: the task-metadata gap that kept a numeric-answer row
on the strict exact-match verifier, and the fact that verifier signals
(needs-retrieval / needs-checker / escalate) produced no next action. M16 fixes
the metadata in batch generation and adds a **read-only** action-routing layer.
All actions are PLANNED — nothing is executed by default.

## Metadata cleanup

`src/validate_task_metadata.py` detects **numeric-looking exact_answer rows
missing numeric metadata** (a clean numeric `known_answer` but no
`numeric`/`expected_value`), so they'd route to strict `exact_answer_match`
instead of `numeric_tolerant_check`.

```bash
python src/validate_task_metadata.py --in data/prompts/agents_a1_m15_batch.jsonl
# exit 0 = clean;  nonzero = lists offending prompt_ids by issue
```

`gen_m13_batch.normalize_numeric_metadata` (applied by both generators)
deterministically tags such rows: `numeric=true` + `expected_value` (parsed from
`known_answer`) + a default tolerance (`rel_tolerance 0.01` when |value|≥1000,
else absolute `0.5`). Non-numeric answers (Paris, Au) are untouched. After
regeneration the validator reports **zero gaps**, and the speed-of-light row
routes to `numeric_tolerant_check` (before/after in
`agents_a1_m16_metadata_beforeafter_sample.json`: 7 reused exact rows moved
exact→numeric; the speed-of-light row flips old exact-match **fail** → new numeric
**pass** and de-escalates).

## Action records (read-only)

`schema/action_record_v1.json` (separate from the frozen schemas) — no raw task
text, only ids/enums/a hashed evidence tag:

```
task_id, action_type (retrieval_needed|checker_needed|no_action|review_needed),
reason_code, source_verifier, confidence, status (planned|skipped|completed|failed),
evidence_hash
```

`status` defaults to `planned`. `completed`/`failed` are only ever set by an
approved deterministic action — never fabricated.

## Action router

`src/action_router.py` maps an `auto_outcome` candidate to a **planned** action
record. It executes nothing.

| condition | action_type | notes |
|---|---|---|
| `auto_needed_retrieval` | `retrieval_needed` | current-info tasks always get this — the base model answer is **never** treated as sufficient |
| `auto_needed_checker` + an approved checker present | `checker_needed` | approved deterministic checkers only: `math_checker`, `json_object_check`, `numeric_tolerant_check` |
| `auto_needed_checker` + no approved checker | `checker_needed`, status `skipped` | nothing is run |
| `escalate_for_review` (and no retrieval/checker) | `review_needed` | for a human |
| otherwise | `no_action` | clean |

```bash
python src/action_router.py \
    --in reports/shadow/private/agents_a1_m15_run_local.jsonl \
    --out reports/shadow/private/agents_a1_m15_actions_local.jsonl   # gitignored
```

Over the M15 run (read-only replay): checker_needed 160 (all approved),
no_action 70, review_needed 19, retrieval_needed 12 — all `planned`
(`agents_a1_m16_action_summary_sample.json`, aggregate-only).

## Gating (unchanged)

- **Actions are read-only / planned** by default — no real retrieval, no arbitrary
  tools; checker actions route only to approved deterministic checkers.
- **Current-info is never faked** — a retrieval_needed record is emitted rather
  than pretending the base answer suffices.
- `auto_outcome` is a **candidate, not gold**; the run never writes human fields;
  evidence is hashed; no private task/output text is committed (only aggregate-only
  artifacts, gated by `check_commit_safe.py`).
- **Production/final thresholds stay gold/audit gated** until enough
  human-reviewed real-workload records exist.
