#!/usr/bin/env bash
# M38E official dev-sweep supervisor: one launch, one retry (resume is
# provenance-validated), stall watchdog on min(log, official-rows) age.
set -u
cd "$(dirname "$0")/.."

PY="$HOME/venvs/jlens-m36v/bin/python"
MODEL="${M36C_MODEL_REF:-$(cat .m36c_model_ref 2>/dev/null)}"
LOG=logs/m38e_official.log
ROWS=reports/shadow/private/m38e_dev_rows.jsonl
SUPLOG=logs/m38e_supervisor.log
STALL_SECONDS=1200
export VLLM_USE_FLASHINFER_SAMPLER=0

[ -n "$MODEL" ] || { echo "[m38e-supervisor] FATAL: no model ref" >&2; exit 2; }
note() { echo "[m38e-supervisor] $* $(date -u +%H:%M:%S)" >> "$SUPLOG"; }
age_of() { [ -f "$1" ] && echo $(( $(date +%s) - $(stat -c %Y "$1") )) || echo 999999; }

note "official sweep START"
for attempt in 1 2; do
    note "attempt=$attempt START"
    setsid "$PY" src/m38e_dev_sweep.py --model-ref "$MODEL" >> "$LOG" 2>&1 &
    pid=$!
    while kill -0 "$pid" 2>/dev/null; do
        sleep 60
        la=$(age_of "$LOG"); ra=$(age_of "$ROWS")
        age=$(( la < ra ? la : ra ))
        if [ "$age" -gt "$STALL_SECONDS" ]; then
            note "attempt=$attempt STALL (log ${la}s rows ${ra}s) — killing group $pid"
            kill -TERM -- "-$pid" 2>/dev/null; sleep 30
            kill -KILL -- "-$pid" 2>/dev/null; sleep 15
            break
        fi
    done
    wait "$pid"; rc=$?
    note "attempt=$attempt EXIT rc=$rc"
    if [ "$rc" -eq 0 ]; then note "official sweep COMPLETE"; exit 0; fi
    sleep 20
done
note "official sweep FAILED after retry"
exit 1
