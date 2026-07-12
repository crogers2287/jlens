# LIVE_STATUS — pushed 30-minute operational heartbeat

Status-only file per the 2026-07-12 steer (`8768df4`). Aggregates only —
no task text, operands, outputs, token ids, telemetry arrays, paths,
weights, or per-task predictions. Newest heartbeat at top.

## Heartbeat 2026-07-12T21:15Z

- **Milestone/phase:** M36C adaptive calibration (branch A — healthy,
  progressing) on the dual-3090 host; M37J pre-fit manifest queued on
  the V100 host.
- **Remote head at collection:** `8768df4`; `steer_sha_seen` (steer.md
  blob): `9aa560e1d8111c67a67dc4fad6b72d68f8f8ed1a` — new steer read in
  full this heartbeat and adopted (this file is its first directive).
- **Process state:** supervisor pid alive; adaptive stage attempt 2
  running since 17:34:11 UTC (attempt 1 was killed at 17:33 by the
  20-min log watchdog during a legitimately quiet heavy cell — false
  positive; a keep-alive sidecar now bridges rows-file freshness to the
  watched log, true-hang detection ≤ ~32 min). Retry count: 1 of 1
  used at stage level; run resumes by task id, no rows regenerated.
- **Rows:** retained 152 / cap 192 (88 original preserved + new);
  completed_correct **89 / 48 quota — met**; completed_incorrect
  **0 / 48 — binding deficit**; truncated_budget 63; mixed cells
  0 / 2; failure families 0 / 3.
- **Coverage:** probe families done or in progress: add_chain,
  div_exact, json_digits, mod_arith, sub_mixed (mul_multi excluded per
  amendment; 22 cells with data).
- **Last completed task id:** `m36c_sub_mixed_s2_003`; last progress
  2026-07-12 21:12 UTC.
- **Throughput:** ~139.5 s/row mean (gen + non-gen) ≈ 26 rows/h.
- **ETA:** not estimable from row rate alone — completed_incorrect is
  the binding quota and no completed failure has been observed yet
  (model either completes correctly or truncates). Stop condition is
  quotas met OR retention cap 192 (≈ 40 rows of headroom → cap could
  bind in ~2–3 h if failure yield stays zero, giving outcome
  `completed_failure_frontier_not_found`).
- **Blockers:** none.
- **Tests:** 12/12 telemetry unit tests pass at `0a5e023`.
- **Privacy:** all task-level data private; this file and committed
  artifacts aggregate-only.
- **Serving restoration:** pending — llama-swap Agents-A1 GGUF serving
  restores after the research run completes (per protocol).
- **M36 gate history this cycle:** Phase 0 profile PASSED at `10767bb`
  (equivalence 8.88e-16; overhead 0.59% vs 25%).
- **M37J:** Phase 0 feasibility PASSED (all 7 gates, 28.27 GiB peak,
  artifact at `27bafe1`). Next per steer: pre-fit manifest commit →
  resumable lens fit → readout/forward-invariance validation → 192-task
  diagnostic dataset → M37J-A observation-only evaluation.
