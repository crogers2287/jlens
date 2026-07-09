# M13 — larger Agents-A1 live run (110 tasks)

Scale-up from the 25-task run (M11/M12) to a bounded 110-task live run against
Agents-A1, now that the JSON verifier is fixed. Same privacy invariants: raw
task/output text stays local and gitignored; only aggregate-only artifacts are
committed.

## Build the batch

`src/gen_m13_batch.py` deterministically generates a PUBLIC 110-task mixed batch
(no RNG — reproducible) across the six scorable categories:

```bash
python src/gen_m13_batch.py --out data/prompts/agents_a1_m13_batch.jsonl
```

| category | count | verifier |
|---|---|---|
| math | 44 | math_checker (known_answer + expression) |
| exact_answer | 20 | exact_answer_match (known_answer) |
| json | 10 | json_object_check (json_check + json_required) |
| regex | 8 | regex_or_schema_check (pattern) |
| current_info | 10 | retrieval_required_heuristic |
| explain | 18 | (open-ended — no correctness verifier) |

## Run it live against Agents-A1 on fred

The `agents-a1` model is **already served** by llama-swap on fred (:9069). The
runner **calls** that endpoint — it never serves or stops models. Point a capped
live `model_fn` (max_tokens 384, temperature 0) at it and use the resumable
runner:

```bash
# config/agents_a1_m13_run.json targets http://localhost:9069/v1 model "agents-a1",
# batch size 120 (cap 250), self_consistency_samples 1 (one call per task).
python src/run_agents_a1_shadow_batch.py --config config/agents_a1_m13_run.json --mode live
# -> reports/shadow/private/agents_a1_m13_run_local.jsonl  (gitignored)
#    reports/shadow/private/agents_a1_m13_run_meta_local.json (gitignored)
```

The run is bounded and **resume-safe** (a re-run skips completed prompt_ids and
appends only missing ones); endpoint failures are counted in `n_failed` and the
run continues. A GGUF endpoint exposes no router logits, so every record has
`telemetry_missing=true` and `policy=null` — features are never fabricated.

## Aggregate, escalate, review

```bash
python src/agents_a1_run_report.py \
    --in reports/shadow/private/agents_a1_m13_run_local.jsonl \
    --meta reports/shadow/private/agents_a1_m13_run_meta_local.json \
    --out reports/outcomes/agents_a1_m13_summary_sample.json         # public, no text

python src/make_escalation_review_queue.py \
    --in reports/shadow/private/agents_a1_m13_run_local.jsonl \
    --out reports/shadow/private/agents_a1_m13_review_local.jsonl     # gitignored
```

Then review a **representative** escalated subset (sample if large — not
necessarily every row) against public benchmark ground truth, honestly:
`outcome.was_wrong` only where objectively determinable, `review_source =
"operator_review"`, undeterminable fields left `null`. The reviewed subset stays
gitignored; a public reviewed-subset summary
(`agents_a1_m13_reviewed_subset_sample.json`) carries only counts + the
auto-vs-human agreement where review exists. Always run `check_commit_safe.py`
before staging anything under `reports/`.

## Results (this run: run_id cd3d744045af170e)

- 110/110 completed, 0 failed, telemetry_missing 110.
- Escalation 18 (rate **0.164**, down from the baseline's 0.28 at 4.4× scale).
- Per category: math 44, json 10, regex 8 escalated **zero** times; current_info
  correctly flagged needs-retrieval (not escalated); explain 17/18 escalated
  (unverifiable open-ended, low-confidence — as designed).
- One auto-wrong (`exact_answer_match` on "speed of light in km/s"): the model
  answered ≈ 299,792 km/s ≈ 300,000 (correct); the checker wanted the literal
  "300000" — a **verifier-strictness** false-positive on approximate/unit-converted
  numbers, distinct from the fixed JSON case. Candidate for a future milestone
  (numeric-tolerant exact match).

`agents_a1_m13_vs_baseline.json` holds the counts-only M13-vs-M11/M12 comparison.

## Gating (unchanged)

- The `agents-a1` endpoint is **only called**, never served/stopped by the agent.
- No private task/output text is ever committed; only aggregate-only artifacts,
  gated by `check_commit_safe.py`; private records stay gitignored.
- `auto_outcome` is a **candidate, not gold**; the run never writes human
  `outcome`/`review_meta` fields.
- **Production/final thresholds stay gold/audit gated** until enough
  human-reviewed real-workload records exist.
