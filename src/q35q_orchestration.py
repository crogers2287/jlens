"""Q35Q Phase-0 staging orchestration (CPU/storage/network composition, pure-injectable).

Second-repair core per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_PHASE0_SECOND_CORRECTION_AND_M39_PREGEN_PROBE.md.

The prior repair (`q35q_stage.py`) supplied correct *validators* but the staging
*path* could not reach several of them: the admitted-name set was derived from
files already present locally, so an interrupted download silently dropped a
missing file before the missing-file branch ran; checksums were self-referential
(expected and observed both hashed from the same local bytes); and no free-space,
overhead, partial-cleanup, or resume evidence entered the conjunction.

This module composes the real staging path through injectable seams so the CLI
and deterministic integration tests exercise the *same* orchestration:

    remote_provider  -> expected admitted-name set (independent of local presence)
    downloader       -> populates the isolated staging root (real or fake)
    local discovery  -> walk + hash the staging root
    presence gate    -> every expected name must exist locally (defect 1)
    partial/extra    -> partial files cleaned; no unapproved extras
    checksum gate    -> remote immutable identities reconciled vs local (defect 2)
    storage gate     -> free / expected / overhead / margin / resume (defect 3)

No GPU, no weights loaded, no model instantiation. Pure logic + injected IO.
Raw file bytes, token IDs, and local paths never leave via the returned verdict
(aggregate counts and hex digests only).
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence

from q35q_stage import Q35QStageBlock, _MANIFEST_EXCLUDE

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
# Immutable checksum identities we accept as *expected* provenance. A required
# admitted file whose remote metadata carries none of these fails closed.
_SUPPORTED_CHECKSUM_KINDS = ("lfs_sha256", "blob_sha256")


@dataclass(frozen=True)
class RemoteFile:
    """One sibling from the pinned *remote* public manifest (never local)."""
    name: str
    size: int
    checksum_hex: str | None = None
    checksum_kind: str | None = None  # one of _SUPPORTED_CHECKSUM_KINDS or None


@dataclass
class StorageInputs:
    free_bytes: int
    expected_weight_bytes: int
    temp_overhead_bytes: int
    safety_margin_bytes: int
    partial_files_detected: bool
    partial_cleanup_done: bool
    interrupted_resume_matches: bool
    final_manifest_reconciled: bool
    cache_isolated_from_unrelated_tenant: bool


def build_expected_admitted(
    remote_files: Sequence[RemoteFile],
    small_ok_suffixes: Sequence[str],
) -> dict[str, RemoteFile]:
    """Expected admitted small-file set built from the *remote* manifest, before
    any local inspection (fixes defect 1). Fails closed on path escape / absolute
    paths / cache-or-metadata names slipping into the admitted set."""
    expected: dict[str, RemoteFile] = {}
    for rf in remote_files:
        n = rf.name
        if n.startswith("/") or ".." in n.split("/"):
            raise Q35QStageBlock(f"path escape / absolute remote name: {n!r}")
        is_small = n.endswith(tuple(small_ok_suffixes)) or os.path.basename(n) in small_ok_suffixes
        if not is_small:
            continue  # weights/large artifacts are not admission files
        if _MANIFEST_EXCLUDE.search(n):
            raise Q35QStageBlock(f"cache/metadata name in admitted set: {n!r}")
        expected[n] = rf
    if not expected:
        raise Q35QStageBlock("empty expected admitted set from remote manifest")
    return expected


def reconcile_presence(expected_names: Sequence[str], local_names: Sequence[str]) -> dict:
    """Every expected name must exist locally. A name absent locally is reported
    as missing here — it is never silently dropped (fixes defect 1). Extra
    non-excluded local files are contamination."""
    local = set(local_names)
    missing = sorted(n for n in expected_names if n not in local)
    extra = sorted(
        n for n in local
        if n not in set(expected_names) and not _MANIFEST_EXCLUDE.search(n)
    )
    partial = sorted(n for n in local if re.search(r"\.(incomplete|partial|tmp|temp)$", n))
    verdict = {
        "expected_count": len(expected_names),
        "present_count": sum(1 for n in expected_names if n in local),
        "missing_count": len(missing),
        "extra_unapproved_count": len(extra),
        "partial_detected_count": len(partial),
        "all_expected_present": not missing,
        "no_unapproved_extra": not extra,
    }
    verdict["no_partial_files"] = not partial
    if missing:
        raise Q35QStageBlock(f"missing expected staged files: {len(missing)}")
    if extra:
        raise Q35QStageBlock(f"unapproved extra files: {len(extra)}")
    if partial:
        raise Q35QStageBlock(f"uncleaned partial/interrupted downloads: {len(partial)}")
    verdict["pass"] = True
    return verdict


def reconcile_checksums(
    expected: Mapping[str, RemoteFile],
    local_hashes: Mapping[str, str],
) -> dict:
    """Bind expected checksums from *remote* immutable metadata and reconcile
    against locally computed sha256 (fixes defect 2 — the two sources are
    distinct). A required admitted file lacking a supported immutable checksum
    identity, or whose local hash disagrees, fails closed."""
    unverifiable, mismatched, checked = [], [], []
    for name, rf in expected.items():
        if rf.checksum_kind not in _SUPPORTED_CHECKSUM_KINDS or not rf.checksum_hex:
            unverifiable.append(name)
            continue
        if not _HEX64.match(rf.checksum_hex):
            unverifiable.append(name)
            continue
        local = local_hashes.get(name)
        if local is None:
            raise Q35QStageBlock(f"no local hash for expected file: {name!r}")
        checked.append(name)
        if local != rf.checksum_hex:
            mismatched.append(name)
    verdict = {
        "expected_count": len(expected),
        "checksum_verified_count": len(checked),
        "unverifiable_identity_count": len(unverifiable),
        "mismatch_count": len(mismatched),
        "all_have_immutable_identity": not unverifiable,
        "all_match": not mismatched,
    }
    if mismatched:
        raise Q35QStageBlock(f"checksum mismatch vs remote metadata: {len(mismatched)}")
    if unverifiable:
        # Fail closed as provenance-blocked rather than passing on self-hash only.
        raise Q35QStageBlock(
            f"required files without immutable checksum identity: {len(unverifiable)}")
    verdict["pass"] = True
    return verdict


def storage_resumability_gate(s: StorageInputs) -> dict:
    """Actual free-space / overhead / margin / partial-cleanup / resume /
    reconciliation / cache-isolation conjunction (fixes defect 3). GPU memory
    ceilings are deliberately not part of this — they are not storage headroom."""
    required = s.expected_weight_bytes + s.temp_overhead_bytes + s.safety_margin_bytes
    checks = {
        "free_space_sufficient": s.free_bytes >= required,
        "safety_margin_declared": s.safety_margin_bytes > 0,
        "temp_overhead_declared": s.temp_overhead_bytes >= 0,
        "partial_cleanup_ok": (not s.partial_files_detected) or s.partial_cleanup_done,
        "interrupted_resume_deterministic": s.interrupted_resume_matches,
        "final_manifest_reconciled": s.final_manifest_reconciled,
        "cache_isolated": s.cache_isolated_from_unrelated_tenant,
    }
    checks["required_bytes"] = required
    checks["all_required_pass"] = all(
        v for k, v in checks.items() if isinstance(v, bool))
    if not checks["all_required_pass"]:
        raise Q35QStageBlock("storage/resumability gate failed")
    return checks


def run_staging_orchestration(
    *,
    revision: str,
    remote_provider: Callable[[str], Sequence[RemoteFile]],
    downloader: Callable[[str, Mapping[str, RemoteFile], str], None],
    staging_root: str,
    hasher: Callable[[str], str],
    small_ok_suffixes: Sequence[str],
    storage: StorageInputs,
) -> dict:
    """Compose the full CPU/storage staging path the CLI uses, so integration
    tests can force every failure through the same code. Returns an aggregate
    verdict (counts + gate booleans). Never returns raw bytes, IDs, or paths."""
    if not _HEX40.match(revision or ""):
        raise Q35QStageBlock("revision must be an immutable 40-hex commit")
    remote_files = list(remote_provider(revision))
    expected = build_expected_admitted(remote_files, small_ok_suffixes)

    # Populate the isolated staging root through the injected downloader.
    os.makedirs(staging_root, exist_ok=True)
    downloader(revision, expected, staging_root)

    # Discover + hash what actually landed (relative names).
    local_hashes: dict[str, str] = {}
    for root, _, files in os.walk(staging_root):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), staging_root)
            # normalize to forward slashes for cross-checking against remote names
            rel = rel.replace(os.sep, "/")
            local_hashes[rel] = hasher(os.path.join(root, fn))

    presence = reconcile_presence(list(expected), list(local_hashes))
    checksums = reconcile_checksums(expected, local_hashes)
    storage_v = storage_resumability_gate(storage)

    return {
        "outcome": "q35q_phase0_staging_orchestration_ok",
        "immutable_revision": revision,
        "expected_admitted_count": len(expected),
        "presence": presence,
        "checksums": checksums,
        "storage": storage_v,
        "gpu_used": False,
        "weights_loaded": False,
        "overall_pass": bool(
            presence.get("pass") and checksums.get("pass")
            and storage_v.get("all_required_pass")),
    }
