"""Q35Q Phase-0 runtime source-digest pin (CPU-only, pure).

Per docs/STEER_ADDENDUM_2026-07-17_Q35Q_DIFFERENTIABLE_GPTQ_TORCH_BACKEND_PRIORITY.md
items 1-4: the structural conversion verification is only admission-grade when the
inspected source is bound to an independently pinned immutable digest. This module
binds the exact installed Transformers source files my verifiers depend on
(`conversion_mapping.py`, `modeling_qwen3_5_moe.py`) to expected sha256 identities
by equality, so a source swap, monkeypatch, or version drift is caught.

Digests here are of PUBLIC library files (reproducible for a given package version),
i.e. permitted immutable public identities; they are not host/private digests.
Pure over (path -> bytes); the caller supplies file bytes + the frozen expected map.
"""
from __future__ import annotations

import hashlib

from q35q_stage import Q35QStageBlock

# The verifiers that require a pinned source:
PINNED_SOURCE_FILES = ("transformers/conversion_mapping.py",
                       "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py")


def source_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bind_source_digests(observed: dict, expected: dict) -> dict:
    """Equality-bind observed source digests to a frozen expected map. Every
    expected file must be present with a matching 64-hex sha256; fails closed on a
    missing file, an extra unexpected file, a malformed digest, or a mismatch."""
    if not expected:
        raise Q35QStageBlock("empty expected source-digest map")
    for name, exp in expected.items():
        if not isinstance(exp, str) or len(exp) != 64 or any(c not in "0123456789abcdef" for c in exp):
            raise Q35QStageBlock(f"expected digest for {name!r} is not a 64-hex sha256")
    missing = sorted(set(expected) - set(observed))
    extra = sorted(set(observed) - set(expected))
    if missing:
        raise Q35QStageBlock(f"missing pinned source files: {missing}")
    if extra:
        raise Q35QStageBlock(f"unexpected extra source files: {extra}")
    mismatched = sorted(n for n in expected if observed[n] != expected[n])
    checks = {
        "files_bound": len(expected),
        "all_present": not missing,
        "no_extra": not extra,
        "all_match": not mismatched,
        "mismatch_count": len(mismatched),
    }
    checks["source_pin_pass"] = checks["all_present"] and checks["no_extra"] and checks["all_match"]
    if not checks["source_pin_pass"]:
        raise Q35QStageBlock(f"source-digest mismatch on {mismatched}")
    return checks
