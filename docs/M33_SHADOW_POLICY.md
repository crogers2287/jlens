# M33 shadow policy — track C (advisory-only)

`src/m33_shadow_policy.py` wires the frozen M33 tool-routing recommendation
into the practical supervisor's shadow stream as **advisory-only** product
telemetry (M35 protocol track C, operator decision `c3c67fa`). It never
blocks, executes, or performs any action; `actual_tool_invocations` is
structurally 0. Advisories live in their own stream, separate from
supervisor actions, so the shadow stays causally interpretable.

## What it records (per the external-consult audit schema)

- The **eligible denominator**: every record is counted — eligible, or
  abstained with a reason (`category_not_checkable`, `no_telemetry`,
  `incomplete_features`).
- Versioning: `policy_version`, detector, threshold, feature schema, and a
  `config_hash` on every advisory and rollup.
- Aggregate-only rollup keyed by workload class x score band x
  recommendation, with `auto_was_wrong` contingency counts for BOTH
  recommended and not-recommended records — so a later audit can decide
  promote-or-kill without selection bias.

## Scoring basis and honest limitations

Real workloads carry no band metadata, so the frozen M30 classifier is scored
with `band: unknown` (all band one-hots zero), recorded as
`score_basis: bandless_unknown`. Per M34, the detector is distribution-bound;
shadow advisories on shifted categories are expected to under-recall, and the
rollup exists to measure exactly that. No production action or threshold
unlock without reviewed audit criteria.

## Live smokes

- `agents_a1_reviewed_live.jsonl`: 7 records, 0 eligible (all
  category_not_checkable) — the honest GGUF/real-use state per M7.
- `m24_qwen_auto_outcomes_local.jsonl` + M24 telemetry: 40 records, 13
  eligible, advise rate .154 — low, consistent with M34's recall collapse on
  the a*b+c category under bandless scoring.

Committed rollup: `reports/telemetry/m33_shadow_policy_rollup.json`
(aggregate-only, commit-safe). Private advisories stay gitignored.
