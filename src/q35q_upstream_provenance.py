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
wheel sha256, rejects ambiguous archive/request identities, and extracts exactly
the admitted source closure. `compare_installed_to_upstream` binds installed
source digests to those independent expected values by equality. Pure over bytes
so it is unit-testable with a synthetic zip; the live adapter must compose it
with distribution ownership and live-object source closure in one clean process.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import PurePosixPath
import re
import zipfile

from q35q_stage import Q35QStageBlock


PINNED_UPSTREAM = {
    "wheel_name": "transformers-5.13.1-py3-none-any.whl",
    "wheel_sha256": "53f0ea8aa397e29244c2377ba981bcaf0c87adcf44fbdd447ef6306522afcacd",
    "sdist_name": "transformers-5.13.1.tar.gz",
    "sdist_sha256": "1e2452d6778a7482158df5d5dacf6bf775d5b2fdcfce33caaf7f6b0e5f3e3397",
    "source_commit": "4626421dc6b741a329300682a6408246ee465490",
}

ADMITTED_SOURCE_MEMBERS = (
    "transformers/conversion_mapping.py",
    "transformers/core_model_loading.py",
    "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py",
)

_LOWER_HEX_64 = re.compile(r"^[0-9a-f]{64}$")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _require_lower_hex_digest(value: object, label: str) -> str:
    if not isinstance(value, str) or _LOWER_HEX_64.fullmatch(value) is None:
        raise Q35QStageBlock(f"{label} is not exact lowercase 64-hex")
    return value


def _require_canonical_member_path(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise Q35QStageBlock(f"{label} is not a nonempty string")
    if "\x00" in value or "\\" in value:
        raise Q35QStageBlock(f"{label} is not a canonical relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value or any(part in {"", ".", ".."} for part in path.parts):
        raise Q35QStageBlock(f"{label} is not a canonical relative POSIX path")
    return value


def _require_exact_requested_members(member_paths) -> tuple[str, ...]:
    if isinstance(member_paths, (str, bytes)):
        raise Q35QStageBlock("member paths must be an iterable of paths, not a string")
    try:
        requested = tuple(member_paths)
    except TypeError as exc:
        raise Q35QStageBlock("member paths are not iterable") from exc
    if not requested:
        raise Q35QStageBlock("no member paths requested")
    canonical = tuple(
        _require_canonical_member_path(value, f"requested member path {index}")
        for index, value in enumerate(requested)
    )
    if len(canonical) != len(set(canonical)):
        raise Q35QStageBlock("duplicate requested member path")
    if len(canonical) != len(ADMITTED_SOURCE_MEMBERS) or set(canonical) != set(ADMITTED_SOURCE_MEMBERS):
        raise Q35QStageBlock("requested member paths do not equal the exact admitted source closure")
    return canonical


def _validate_upstream_digest_map(upstream_digests: object) -> dict[str, str]:
    if not isinstance(upstream_digests, dict):
        raise Q35QStageBlock("upstream digest map is not a dict")
    canonical = {
        _require_canonical_member_path(key, "upstream digest path"):
        _require_lower_hex_digest(value, f"upstream digest for {key!r}")
        for key, value in upstream_digests.items()
    }
    if len(canonical) != len(ADMITTED_SOURCE_MEMBERS) or set(canonical) != set(ADMITTED_SOURCE_MEMBERS):
        raise Q35QStageBlock("upstream digest map does not equal the exact admitted source closure")
    return canonical


def _validate_installed_digest_map(installed_digests: object) -> dict[str, str]:
    if not isinstance(installed_digests, dict):
        raise Q35QStageBlock("installed digest map is not a dict")
    return {
        _require_canonical_member_path(key, "installed digest path"):
        _require_lower_hex_digest(value, f"installed digest for {key!r}")
        for key, value in installed_digests.items()
    }


def verify_wheel_and_extract(
    wheel_bytes: bytes,
    expected_wheel_sha256: str,
    member_paths=ADMITTED_SOURCE_MEMBERS,
) -> dict[str, str]:
    """Verify the frozen wheel and hash exactly the admitted source closure.

    Fails closed on malformed digest identities, duplicate ZIP names, duplicate or
    noncanonical requested paths, incomplete/expanded closure, malformed archives,
    missing members, or a wheel-hash mismatch.
    """
    expected_wheel_sha256 = _require_lower_hex_digest(
        expected_wheel_sha256, "expected wheel sha256"
    )
    requested = _require_exact_requested_members(member_paths)
    if sha256(wheel_bytes) != expected_wheel_sha256:
        raise Q35QStageBlock(
            "downloaded wheel sha256 does not match the pinned upstream identity"
        )
    try:
        with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise Q35QStageBlock("wheel contains duplicate ZIP member names")
            available = set(names)
            missing = [member for member in requested if member not in available]
            if missing:
                raise Q35QStageBlock(
                    f"member missing from upstream wheel: {missing[0]!r}"
                )
            return {member: sha256(archive.read(member)) for member in requested}
    except zipfile.BadZipFile as exc:
        raise Q35QStageBlock("wheel is not a valid zip archive") from exc


def compare_installed_to_upstream(
    upstream_digests: dict,
    installed_digests: dict,
) -> dict:
    """Bind installed source digests to the exact independent upstream closure."""
    upstream = _validate_upstream_digest_map(upstream_digests)
    installed = _validate_installed_digest_map(installed_digests)
    missing = sorted(set(upstream) - set(installed))
    extra = sorted(set(installed) - set(upstream))
    mismatch = sorted(
        key for key in upstream if key in installed and installed[key] != upstream[key]
    )
    verdict = {
        "member_count": len(upstream),
        "all_present": not missing,
        "no_extra": not extra,
        "all_match_upstream": not mismatch,
        "missing_count": len(missing),
        "extra_count": len(extra),
        "mismatch_count": len(mismatch),
    }
    verdict["installed_bound_to_upstream"] = (
        verdict["all_present"]
        and verdict["no_extra"]
        and verdict["all_match_upstream"]
    )
    return verdict
