# Overnight status — 2026-07-12 (M36C + M37J parallel tracks)

## M36 (primary, dual-3090 host)

**Complete and sealed earlier this cycle:**
- M36V Phase 1 (`d6842f4`): router telemetry classified **full_telemetry** —
  all 8 gates; 0 expert-id mismatches over 2,609 rows x 40 layers; exact
  dispatch-weight identity; baseline runtime nondeterminism measured and
  the parity envelope frozen.
- M36V Phase 2 (`5041b3a`): 16/16 verifier pass stock AND instrumented;
  1.32x overhead; serving stack restored.
- M36C amendment (`729e18c`): 384-row sweep stopped at 88 preserved rows
  after the decode-budget-cliff finding (hard multiplication cells are
  budget-bound, 94-100% truncation at 1,024 tokens, not proven
  capability failures).
- M36C machinery (`8066fe2`+): device-side summary telemetry (4 router
  features, <=1e-5 equivalence vs raw, unit-tested), harness profiler,
  adaptive probe/rescue/expansion state machine (dry-run meets all
  quotas), detector freeze with 5 comparators, benchmark driver with
  power rule + verifier-first arms + H1/H2/H3 — all offline-validated.

**Overnight incident (honest record):** the Phase 0 profile run hung
silently ~15 min in (log frozen after Triton GDN-kernel JIT; process
alive, no progress) and the pilot-model rsync to the V100 host stalled
at 11/27 GB around the same time. Both sat undetected ~6.5 h because
the completion watchers watched the wrong signals. Recovery: both
killed; the M36C pipeline now runs under a supervisor with a 15-minute
silent-stall watchdog and one automatic retry per stage
(profile -> adaptive chained); rsync rewrapped in a timeout+retry loop
(now COMPLETE); a scheduled heartbeat re-checks all pipelines every
~25 min independent of watchers.

**Now running:** M36C Phase 0 profile (supervised). On gate pass the
supervisor launches adaptive calibration automatically (~3-5 h), then:
detector/policy freeze -> benchmark manifest commit -> decision capture
-> single sealed evaluate -> M36 result + stop report.

## M37J (parallel pilot, V100 host)

- Steer `d65caaa` + protocol doc adopted; M36 keeps 3090 priority.
- V100 host located and verified (32 GiB), GPU cleared per operator
  authorization ("the gpu is yours").
- Isolated env provisioned: torch 2.5.1+cu121, transformers 5.13.1,
  `anthropics/jacobian-lens` pinned at `581d3986` (initial release).
- Pilot model `Qwen1.5-MoE-A2.7B-Chat` (27 GB) fully transferred.
- **Phase 0 feasibility gate running now on the V100**: fp16 load,
  128-token forward + activation-gradient backward smoke, <=30 GiB
  peak-memory gate, hidden-state/unembedding access, `jlens.from_hf`
  adapter, forward-unchanged check (`src/m37j_phase0.py`).
- Why a pilot model and not Agents-A1: the lens fit requires
  differentiable backward passes; the Agents-A1 AWQ/vLLM path is
  inference-only (steer's explicit claim boundary). Nothing from M37J
  is an Agents-A1 result.

## Next checkpoints

1. Profile gates -> adaptive calibration rows accumulate (supervised).
2. Feasibility artifact from the V100 -> pre-fit commit -> fit manifest
   -> lens fitting (resumable, checkpointed).
3. Morning target: M36C calibration result + detector freeze +
   benchmark manifest committed; M37J-A lens fitted with readout
   validation, diagnostic task capture queued.
