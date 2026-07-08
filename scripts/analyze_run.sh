#!/usr/bin/env bash
# One-shot routing analysis for a capture run.
# Usage: scripts/analyze_run.sh data/captures/qwen3_6_35b_a3b_r3 r3
set -euo pipefail
cd "$(dirname "$0")/.."
DIR="${1:?capture dir}"
TAG="${2:?report tag}"
PY=.venv/bin/python

echo "=== overlap ($TAG) ==="
$PY src/expert_overlap.py "$DIR" --json "reports/${TAG}_overlap.json"

echo "=== domain probe ($TAG) ==="
$PY src/routing_probe.py "$DIR" --json "reports/${TAG}_probe.json"

echo "=== NN retrieval ($TAG) ==="
$PY - "$DIR" << 'EOF'
import numpy as np, sys
sys.path.insert(0, "src")
from routing_probe import build_features
X, y, names, nl, ne = build_features(sys.argv[1], 8)
Xn = X / np.linalg.norm(X, axis=1, keepdims=True)
S = Xn @ Xn.T
np.fill_diagonal(S, -1)
hits = sum(y[int(S[i].argmax())] == y[i] for i in range(len(y)))
intra = [S[i, j] for i in range(len(y)) for j in range(len(y)) if i < j and y[i] == y[j]]
inter = [S[i, j] for i in range(len(y)) for j in range(len(y)) if i < j and y[i] != y[j]]
print(f"retrieval@1 = {hits}/{len(y)}")
print(f"intra={np.mean(intra):.4f} inter={np.mean(inter):.4f} gap={np.mean(intra)-np.mean(inter):.4f}")
EOF
