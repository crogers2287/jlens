#!/usr/bin/env bash
# M36T prefix-capture supervisor: one stage, one retry, stall watchdog.
# Health signal is min(log age, rows-file age): the log covers model
# load; each task writes a row within ~7 min once capture starts.
set -u
cd "$(dirname "$0")/.."

PY="$HOME/venvs/jlens-m36v/bin/python"
MODEL="${M36C_MODEL_REF:-$(cat .m36c_model_ref 2>/dev/null)}"
LOG=logs/m36t_capture.log
ROWS=reports/shadow/private/m36t_dev_rows.jsonl
SUPLOG=logs/m36t_supervisor.log
STALL_SECONDS=900
export VLLM_USE_FLASHINFER_SAMPLER=0

[ -n "$MODEL" ] || { echo "[supervisor] FATAL: no model ref" >&2; exit 2; }
note() { echo "[m36t-supervisor] $* $(date -u +%H:%M:%S)" >> "$SUPLOG"; }

age_of() { [ -f "$1" ] && echo $(( $(date +%s) - $(stat -c %Y "$1") )) || echo 999999; }

note "capture START"
for attempt in 1 2; do
    note "attempt=$attempt START"
    setsid "$PY" src/m36t_prefix_capture.py --model-ref "$MODEL" \
        >> "$LOG" 2>&1 &
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
    if [ "$rc" -eq 0 ]; then
        note "capture COMPLETE"
        exit 0
    fi
    sleep 20
done
note "capture FAILED after retry"
exit 1
