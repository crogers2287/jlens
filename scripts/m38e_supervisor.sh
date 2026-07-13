#!/usr/bin/env bash
# SUPERSEDED (steer 3f422ad): this launcher's retry path used host-global
# process-name matching and reset the attempt budget. It is not
# authorized to run. Use the corrected one-retry controller instead:
#   scripts/m38e_retry_controller.py <pinned_exec_dir> <expected_full_sha>
# which enforces owned-PGID launching (scripts/m38e_launch.py), an
# exclusive run lock, persisted attempt accounting (original attempt
# counted), liveness proof, immutable-source preflight, and full runtime
# identity verification — and launches at most one retry, only after the
# original attempt has actually failed.
echo "[m38e-supervisor] REFUSED: superseded by scripts/m38e_retry_controller.py (steer 3f422ad)" >&2
exit 2
