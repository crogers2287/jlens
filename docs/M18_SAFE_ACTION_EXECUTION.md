# M18 — safe retrieval/checker action execution

M16 converted verifier signals into **planned** action records. M18 adds the
first bounded executor for those records. It is explicit opt-in, read-only, and
candidate-only: execution does not create gold labels or unlock production.

## Safety contract

- Execution is disabled unless `execute_action(..., enabled=True)` or the CLI
  receives `--execute`.
- Retrieval is accepted only through `FixtureRetrievalAdapter`, whose rows must
  declare `fixture` or `public_fixture` source kind. No network adapter exists.
- Checker names resolve through a fixed allowlist: `math_checker`,
  `json_object_check`, and `numeric_tolerant_check`.
- The executor has no shell/subprocess/dynamic-import surface and ignores task
  fields such as `command` and `fixture_test`. Arithmetic remains confined to
  the existing verifier's numeric-expression grammar.
- Raw task text, model output, and retrieved context may exist only in trusted
  local inputs. `action_result_v1` stores ids, enums, confidence, and hashes.
- Retrieval completion means context became available. It does **not** mean the
  original answer became correct; grounded regeneration is still required.

## Records

`schema/action_result_v1.json` is separate from the frozen outcome and action
schemas. Every result links back to its planned action with `task_id`,
`action_type`, and `action_evidence_hash`, then records:

| field | meaning |
|---|---|
| `action_status` | `completed`, `skipped`, or `failed` |
| `executor_name` | allowlisted checker, fixture retrieval, disabled, or none |
| `result_type` | retrieved context, checker result, or no result |
| `result_confidence` | executor confidence, never calibrated gold |
| `checker_verdict` | pass/fail/undecided for checker results only |
| `evidence_hash` | non-reversible evidence; never raw text |
| `followup_needed` | whether regeneration/review remains necessary |
| `error_code` | bounded machine-readable skip/failure reason |
| `candidate_only` | always `true` |

## Running it

Default behavior is disabled and produces safe `execution_disabled` results:

```bash
python src/action_executor.py \
  --actions reports/shadow/private/agents_a1_m18_actions_local.jsonl \
  --out reports/shadow/private/agents_a1_m18_disabled_results_local.jsonl
```

Explicit fixture/checker execution:

```bash
python src/action_executor.py \
  --actions reports/shadow/private/agents_a1_m18_actions_local.jsonl \
  --tasks data/prompts/agents_a1_m15_batch.jsonl \
  --records reports/shadow/private/agents_a1_m15_run_local.jsonl \
  --retrieval-fixture reports/shadow/private/m18_retrieval_fixture_local.json \
  --execute \
  --out reports/shadow/private/agents_a1_m18_action_results_local.jsonl \
  --summary reports/outcomes/agents_a1_m18_action_execution_summary.json
```

Retrieval fixture files and detailed action results remain under the gitignored
private directory. Only the aggregate summary is public.

## Planned versus executed replay

The M15/M16 action distribution was replayed through the M18 executor:

| action | planned | completed | interpretation |
|---|---:|---:|---|
| retrieval | 12 | 12 | fixture context path worked; all 12 still need grounded regeneration |
| checker | 160 | 160 | allowlisted `math_checker` executed |
| review | 19 | 0 | intentionally not automated |
| no action | 70 | 0 | intentionally not executed |

That yields 172 completed and 89 deliberately skipped actions. Current-info
fixture follow-up coverage is 12/12. This is execution-path coverage, not an
accuracy claim.

The historical M15 runtime log stores only 160-character `output_preview`
values, not full model outputs. Consequently the checker replay reports 70 pass
and 90 fail, but the public summary labels its input mode
`legacy_truncated_preview_replay` and its correctness interpretation
`not_valid_from_legacy_truncated_previews`. Those verdict counts must **not** be
used as model-quality measurements. A future live run must pass the full output
transiently into the executor before truncating/private logging.

## Gating

- `auto_outcome` and `action_result` remain candidates, not gold.
- Production remains gated on full-output live execution plus human-reviewed
  calibration.
- No arbitrary command execution and no live/public-web retrieval adapter were
  introduced.
- Private details and retrieved context remain gitignored; the public summary
  passes the commit-safety gate.
