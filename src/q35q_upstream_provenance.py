"""Q35Q Phase-0 independent upstream provenance (CPU-only, pure).

Per docs/STEER_ADDENDUM_2026-07-17_Q35Q_LIVE_ADAPTER_DISTRIBUTION_AND_OPERATION_ORIGIN_CORRECTION.md:
expected source digests must be derived from the immutable PyPI upstream artifact,
not the installed bytes. The addendum fixes the upstream identities:

  wheel  transformers-5.13.1-py3-none-any.whl
         sha256 53f0ea8aa397e29244c2377ba981bcaf0c87adcf44fbdd447ef6306522afcacd
  sdist  transformers-5.13.1.tar.gz
         sha256 1e2452d6778a7482158df5d5dacf6bf775d5b2fdcfce33caaf7f6b0e5f3e3397
  source commit 4626421dc6b741a329300682a6408246ee465490

`verify_wheel_and_extract` verifies the downloaded wheel bytes against the frozen
wheel sha256, then extracts + hashes the requested member files -> these are the
INDEPENDENT expected digests. `compare_installed_to_upstream` binds the installed
source digests to those independent expected values by equality. Pure over bytes so
it is unit-testable with a synthetic zip; the thin live CLI downloads the real wheel.
"""
from __future__ import annotations

import hashlib
import io
import zipfile

from q35q_stage import Q35QStageBlock

PINNED_UPSTREAM = {
    "wheel_name": "transformers-5.13.1-py3-none-any.whl",
    "wheel_sha256": "53f0ea8aa397e29244c2377ba981bcaf0c87adcf44fbdd447ef6306522afcacd",
    "sdist_name": "transformers-5.13.1.tar.gz",
    "sdist_sha256": "1e2452d6778a7482158df5d5dacf6bf775d5b2fdcfce33caaf7f6b0e5f3e3397",
    "source_commit": "4626421dc6b741a329300682a6408246ee465490",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_wheel_and_extract(wheel_bytes: bytes, expected_wheel_sha256: str,
                             member_paths) -> dict:
    """Verify the wheel's full sha256, then extract + hash the requested members.
    Returns {member_path: sha256}. Fails closed on a wheel-hash mismatch or a
    missing member."""
    if not isinstance(expected_wheel_sha256, str) or len(expected_wheel_sha256) != 64:
        raise Q35QStageBlock("expected wheel sha256 is not 64-hex")
    if sha256(wheel_bytes) != expected_wheel_sha256:
        raise Q35QStageBlock("downloaded wheel sha256 does not match the pinned upstream identity")
    try:
        z = zipfile.ZipFile(io.BytesIO(wheel_bytes))
    except zipfile.BadZipFile:
        raise Q35QStageBlock("wheel is not a valid zip archive")
    names = set(z.namelist())
    out = {}
    for m in member_paths:
        if m not in names:
            raise Q35QStageBlock(f"member missing from upstream wheel: {m!r}")
        out[m] = sha256(z.read(m))
    if not out:
        raise Q35QStageBlock("no member paths requested")
    return out


def compare_installed_to_upstream(upstream_digests: dict, installed_digests: dict) -> dict:
    """Bind installed source digests to the INDEPENDENT upstream digests by equality."""
    if not upstream_digests:
        raise Q35QStageBlock("empty upstream digest map")
    missing = sorted(set(upstream_digests) - set(installed_digests))
    extra = sorted(set(installed_digests) - set(upstream_digests))
    mismatch = sorted(k for k in upstream_digests
                      if k in installed_digests and installed_digests[k] != upstream_digests[k])
    verdict = {
        "member_count": len(upstream_digests),
        "all_present": not missing,
        "no_extra": not extra,
        "all_match_upstream": not mismatch,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "mismatch_count": len(mismatch),
    }
    verdict["installed_bound_to_upstream"] = (
        verdict["all_present"] and verdict["no_extra"] and verdict["all_match_upstream"])
    return verdict
