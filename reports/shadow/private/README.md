# reports/shadow/private/ — LOCAL-ONLY

This directory holds **private real-use shadow logs** (real prompts + model
outputs). Its `*.jsonl` files are **gitignored and must NEVER be committed** —
they can contain sensitive prompt/output text.

Only this README is tracked. To share results:
1. Redact with `src/redact_shadow_log.py` (scrubs prompt/output/notes text), OR
2. Produce an aggregate-only summary with `src/private_outcome_summary.py`
   (counts/rates only, no text).
3. Run `src/check_commit_safe.py` before committing anything derived from here.

See `docs/PRIVATE_SHADOW_WORKFLOW.md`. Production thresholds stay gold/audit gated.
