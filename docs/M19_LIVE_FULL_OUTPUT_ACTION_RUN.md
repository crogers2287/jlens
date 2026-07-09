# M19 — live full-output action run

M19 integrates M18's bounded action executor into the live Agents-A1 runner and
closes the legacy-preview correctness gap. Approved checkers now receive the
full model output **transiently**, before the runtime record is truncated. The
full output is never written to either the private runtime log or action-result
log, and no public artifact contains raw task/output/retrieved-context text.

## Workload and configuration

`src/gen_m19_batch.py` deterministically builds 500 tasks by preserving the
cleaned 261-task M15 baseline and adding 239 unique cases. The resulting
`data/prompts/agents_a1_m19_batch.jsonl` contains:

| task category | count |
|---|---:|
| math | 360 |
| exact answer | 50 |
| explain / rubric | 43 |
| current information | 20 |
| JSON | 10 |
| numeric | 9 |
| regex | 8 |

`config/agents_a1_m19_run.json` caps the run at exactly 500 tasks and explicitly
enables actions. The default behavior of the shared M18 executor remains off.
Retrieval remains fixture/public-fixture only; checkers remain restricted to
`math_checker`, `json_object_check`, and `numeric_tolerant_check`.

## Transient full-output path

`autonomous_shadow_supervisor.run_task(..., return_full_output=True)` returns a
pair to the private runner: the normal bounded runtime record and the full output
held in memory. The M19 runner immediately:

1. derives the M16 action record;
2. passes the transient output to the M18 allowlisted executor;
3. validates and writes only `action_result_v1`;
4. writes the existing runtime record containing only `output_preview`;
5. discards the transient reference as the loop advances.

Resume requires both the runtime id and action-result id before skipping a task.
When actions are disabled, the runner keeps its pre-M19 behavior.

## Live run

The already-running `agents-a1` endpoint on fred was called; the runner did not
serve, unload, or reconfigure any model.

```bash
python src/gen_m19_batch.py
python src/validate_task_metadata.py \
  --in data/prompts/agents_a1_m19_batch.jsonl
python src/run_agents_a1_shadow_batch.py \
  --config config/agents_a1_m19_run.json --mode live
```

Run `c20512612a978d60` completed 500/500 tasks with zero endpoint failures:

- escalation: 27/500 = **0.054**, down from M15's 0.0728;
- telemetry missing: 500/500, honestly unscored (`policy=null`);
- auto outcomes: 452 okay / 44 undecided / 4 wrong candidates;
- action execution: 383 completed / 117 deliberately skipped;
- approved full-output math checker: **356 pass / 4 fail**;
- fixture retrieval: 23 completed, all still requiring grounded regeneration.

The four checker failures are real full-output candidates, not preview artifacts:
the compact outputs were 2062 vs 1972, 863 vs 862, 3365 vs 3345, and 3052 vs
3032. They remain candidate findings pending human calibration; production is
still gated.

## Current-information separation

Of the 23 retrieval actions, 20 were actual `current_info` tasks and completed
20/20 through the fixture adapter. Three were heuristic false-positive routes:

- two explain rows containing “weather”;
- one static discount problem containing “price.”

The public action summary reports these separately (`current_info_retrieval` vs
`retrieval_non_current_info`) rather than treating all retrieval signals as
current-information success. Fixture completion proves an executable follow-up
path only; no grounded answer regeneration was attempted in M19.

## Aggregate artifacts

- `agents_a1_m19_summary_sample.json`: live completion/escalation/verifier counts;
- `agents_a1_m19_action_execution_summary.json`: full-output action execution,
  checker verdicts, and current-info separation;
- `agents_a1_m19_vs_baseline.json`: M19 vs M15 and the invalid M18 preview replay.

All detailed runtime/action records and the retrieval fixture remain under
`reports/shadow/private/` and are gitignored.

## Gating

- `auto_outcome` and `action_result` remain candidates, not gold.
- No full output is persisted in committed or public artifacts.
- Retrieval is fixture-only and is not answer correctness.
- GGUF telemetry remains unavailable and is never fabricated.
- The 4 checker failures and 3 retrieval false-positive routes need review.
- Production remains gated on broader human calibration and grounded retrieval
  behavior.
