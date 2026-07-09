# M15 — larger Agents-A1 live run after verifier fixes (261 tasks)

Scale-up to a 261-task live run now that both known verifier-strictness
false-positives are fixed (JSON in M12, numeric in M14). The run confirms the
fixes hold at scale and that escalation quality keeps improving. Same privacy
invariants: raw task/output text stays local and gitignored; only aggregate-only
artifacts are committed.

## Build the batch

`src/gen_m15_batch.py` deterministically generates a PUBLIC 261-task mixed batch
(reuses the M13 pools + adds numeric and explain-rubric pools):

```bash
python src/gen_m15_batch.py --out data/prompts/agents_a1_m15_batch.jsonl
```

| category | count | verifier |
|---|---|---|
| math | 160 | math_checker |
| exact_answer (string) | 20 | exact_answer_match |
| numeric | 20 | numeric_tolerant_check (M14) |
| json | 10 | json_object_check |
| regex | 8 | regex_or_schema_check |
| current_info | 10 | retrieval_required_heuristic |
| explain | 18 | (open-ended — none) |
| explain-rubric | 15 | explain_rubric_check (M14) |

## Run it live against Agents-A1 on fred

The `agents-a1` model is **already served** by llama-swap on fred (:9069) — the
runner **calls** it, never serves/stops models. Point a capped live `model_fn`
(max_tokens 384, temperature 0) at it and use the resumable runner:

```bash
python src/run_agents_a1_shadow_batch.py --config config/agents_a1_m15_run.json --mode live
# -> reports/shadow/private/agents_a1_m15_run_local.jsonl  (gitignored)
```

Bounded (batch size 300, cap 500), **resume-safe** (a re-run skips completed
prompt_ids), and failure-tolerant (`n_failed` counted, run continues). GGUF ⇒
`telemetry_missing=true`, `policy=null` — features never fabricated.

## Aggregate, escalate, review, compare

```bash
python src/agents_a1_run_report.py --in <private run log> --meta <private meta> \
    --out reports/outcomes/agents_a1_m15_summary_sample.json          # public, no text
python src/make_escalation_review_queue.py --in <private run log> \
    --out reports/shadow/private/agents_a1_m15_review_local.jsonl      # gitignored
```

Then review a **representative** escalated subset against public benchmark ground
truth (honest `operator_review`; undeterminable fields left `null`), producing a
public reviewed-subset summary; and build the counts-only comparison
`agents_a1_m15_vs_baseline.json`. Always run `check_commit_safe.py` before staging
under `reports/`.

## Results (run_id 25ca35429474c407)

- 261/261 completed, 0 failed, telemetry_missing 261.
- Escalation 19 (rate **0.073**) — the third point in a monotonic decline across
  live runs: **0.28 → 0.164 → 0.073** as verifier coverage improved.
- **Both fixes held at scale**: JSON tasks and numeric-tagged tasks each had
  `auto_was_wrong = 0`.
- Per category, math / numeric / json / regex escalated **zero** times;
  current_info was flagged needs-retrieval; explain (open-ended, no verifier) and
  a few rubric rows carried the escalations, as designed.
- The single `auto_was_wrong` is a **task-metadata gap**, not a regression: a
  reused string-`exact_answer` speed-of-light row lacks numeric metadata, so it
  routes to the strict `exact_answer_match` instead of `numeric_tolerant_check`
  (the numeric-tagged version passed). Fix: tag numeric-answer exact benchmark
  rows with numeric metadata.
- A rubric row escalated on a synonym ("interaction" vs the rubric keyword
  "force") — `explain_rubric_check` correctly escalated for review rather than
  marking it wrong.

## Gating (unchanged)

- The `agents-a1` endpoint is **only called**, never served/stopped by the agent.
- No private task/output text is ever committed; only aggregate-only artifacts,
  gated by `check_commit_safe.py`; private records stay gitignored.
- `auto_outcome` is a **candidate, not gold**; the run never writes human fields;
  explain answers are never claimed gold without a rubric.
- **Production/final thresholds stay gold/audit gated** until enough
  human-reviewed real-workload records exist.
