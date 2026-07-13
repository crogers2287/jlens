#!/usr/bin/env bash
# M38E official-sweep control supervisor (steer a726b35 architecture).
#
# Control/execution separation: this script lives in the CONTROL
# checkout (which receives status/steer/test commits) but launches the
# driver ONLY from an immutable EXECUTION checkout pinned to the exact
# source identity bound into the official rows. There is no fallback to
# the current directory, a branch tip, or the latest commit; a retry is
# a resume of the same run identity or nothing.
#
# Required environment (no defaults — refusal is the failure mode):
#   M38E_EXEC_DIR       absolute path to the pinned execution worktree
#   M38E_EXPECTED_SHA   full 40-hex source commit bound into the rows
set -u
CONTROL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

EXEC_DIR="${M38E_EXEC_DIR:?M38E_EXEC_DIR must be set to the pinned execution worktree}"
EXPECTED="${M38E_EXPECTED_SHA:?M38E_EXPECTED_SHA must be the full 40-hex row-bound commit}"
PY="$HOME/venvs/jlens-m36v/bin/python"
LOG="$CONTROL_DIR/logs/m38e_official.log"
ROWS="$EXEC_DIR/reports/shadow/private/m38e_dev_rows.jsonl"
SUPLOG="$CONTROL_DIR/logs/m38e_supervisor.log"
STALL_SECONDS=1200
export VLLM_USE_FLASHINFER_SAMPLER=0

note() { echo "[m38e-supervisor] $* $(date -u +%H:%M:%S)" >> "$SUPLOG"; }
age_of() { [ -f "$1" ] && echo $(( $(date +%s) - $(stat -c %Y "$1") )) || echo 999999; }

case "$EXPECTED" in
    master|main|HEAD|*[!0-9a-f]*) note "REFUSED symbolic/invalid SHA '$EXPECTED'"; exit 2;;
esac
[ ${#EXPECTED} -eq 40 ] || { note "REFUSED non-full SHA"; exit 2; }

note "control supervisor START exec=$EXEC_DIR sha=${EXPECTED:0:12}"
for attempt in 1 2; do
    # Immutable-source verification immediately before every launch.
    if ! "$PY" "$CONTROL_DIR/scripts/m38e_exec_preflight.py" \
            "$EXEC_DIR" "$EXPECTED" >> "$SUPLOG" 2>&1; then
        note "attempt=$attempt PREFLIGHT BLOCK — no launch"
        exit 3
    fi
    note "attempt=$attempt START (preflight ok)"
    ( cd "$EXEC_DIR" && setsid "$PY" src/m38e_dev_sweep.py \
        --model-ref "$(cat "$EXEC_DIR/.m36c_model_ref")" ) >> "$LOG" 2>&1 &
    pid=$!
    while kill -0 "$pid" 2>/dev/null; do
        sleep 60
        la=$(age_of "$LOG"); ra=$(age_of "$ROWS")
        age=$(( la < ra ? la : ra ))
        if [ "$age" -gt "$STALL_SECONDS" ]; then
            note "attempt=$attempt STALL (log ${la}s rows ${ra}s) — killing group"
            child=$(pgrep -f "m38e_dev_sweep.py" | head -1)
            [ -n "$child" ] && kill -TERM -- "-$child" 2>/dev/null
            sleep 30
            [ -n "$child" ] && kill -KILL -- "-$child" 2>/dev/null
            sleep 15
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
