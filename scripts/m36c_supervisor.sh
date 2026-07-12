#!/usr/bin/env bash
# M36C supervised pipeline: profile -> adaptive, one retry per stage,
# silent-stall watchdog (kills a stage whose log goes quiet too long).
# Survives operator-session loss: run under nohup/setsid from repo root.
set -u
cd "$(dirname "$0")/.."

PY="$HOME/venvs/jlens-m36v/bin/python"
# Model path is never committed: read from env or untracked .m36c_model_ref.
MODEL="${M36C_MODEL_REF:-$(cat .m36c_model_ref 2>/dev/null)}"
if [ -z "$MODEL" ]; then
    echo "[supervisor] FATAL: set M36C_MODEL_REF or create .m36c_model_ref" >&2
    exit 2
fi
SUPLOG="logs/m36c_supervisor.log"
STALL_SECONDS=1200  # profile can be legitimately quiet ~13 min during the 8 generations
export VLLM_USE_FLASHINFER_SAMPLER=0

note() { echo "[supervisor] $* $(date -u +%H:%M:%S)" >> "$SUPLOG"; }

run_stage() {
    local stage=$1 log=$2 attempt rc age pid
    for attempt in 1 2; do
        note "stage=$stage attempt=$attempt START"
        setsid "$PY" src/m36c_adaptive.py --stage "$stage" --model-ref "$MODEL" \
            >> "$log" 2>&1 &
        pid=$!
        while kill -0 "$pid" 2>/dev/null; do
            sleep 60
            age=$(( $(date +%s) - $(stat -c %Y "$log") ))
            if [ "$age" -gt "$STALL_SECONDS" ]; then
                note "stage=$stage attempt=$attempt STALL log idle ${age}s — killing group $pid"
                kill -TERM -- "-$pid" 2>/dev/null
                sleep 30
                kill -KILL -- "-$pid" 2>/dev/null
                sleep 15
                break
            fi
        done
        wait "$pid"; rc=$?
        note "stage=$stage attempt=$attempt EXIT rc=$rc"
        [ "$rc" -eq 0 ] && return 0
        sleep 20  # let GPUs drain before retry
    done
    return 1
}

note "pipeline START pid=$$"
if ! run_stage profile logs/m36c_profile.log; then
    note "PROFILE FAILED after retry — pipeline ABORTED"
    exit 1
fi
note "profile gates PASSED — launching adaptive"
if ! run_stage adaptive logs/m36c_adaptive.log; then
    note "ADAPTIVE FAILED after retry — pipeline ABORTED"
    exit 1
fi
note "PIPELINE COMPLETE"
