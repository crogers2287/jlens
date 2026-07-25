"""Q35Q installed-distribution ownership verification (CPU-only, pure).

This module binds an imported package to one installed wheel-style distribution
using the distribution's own METADATA, WHEEL, RECORD, declared-file list, and
source bytes. It is deliberately pure over supplied identities/bytes so the
adversarial cases are testable without importing Transformers or touching the
network.

This verifier establishes installed-distribution ownership only. It does not by
itself establish independent upstream-wheel equality, live-object source closure,
clean-subprocess integrity, or GPTQModel/Defuser loader admission.
"""
from __future__ import annotations

import base64
import csv
from email.parser import Parser
import io
import json
import os
from pathlib import PurePosixPath
import re
from typing import Iterable, Mapping

from q35q_stage import Q35QStageBlock


_CANONICAL_NAME_SEP = re.compile(r"[-_.]+")
_DIST_INFO_SUFFIX = ".dist-info"


def _normalize_distribution_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise Q35QStageBlock("distribution name is not a nonempty string")
    return _CANONICAL_NAME_SEP.sub("-", value.strip()).lower()


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise Q35QStageBlock(f"{label} is not a nonempty string")
    if "\x00" in value:
        raise Q35QStageBlock(f"{label} contains NUL")
    return value


def _require_canonical_record_path(value: object, label: str) -> str:
    """Require an in-root, canonical relative POSIX member path."""
    value = _require_text(value, label)
    if "\\" in value:
        raise Q35QStageBlock(f"{label} is not a canonical relative POSIX path")
    path = PurePosixPath(value)
    if path.is_absolute() or str(path) != value or any(
        part in {"", ".", ".."} for part in path.parts
    ):
        raise Q35QStageBlock(f"{label} is not a canonical relative POSIX path")
    return value


def _require_canonical_distribution_path(value: object, label: str) -> str:
    """Require a canonical RECORD/distribution path.

    Installed wheel RECORD files may contain generated console scripts expressed
    as leading ``../`` components relative to purelib. Those paths cannot own the
    admitted package or dist-info members, but rejecting them would reject a valid
    wheel installation. Leading parent components are therefore accepted while
    embedded traversal, absolute paths, backslashes, dot components, and aliases
    remain forbidden.
    """
    value = _require_text(value, label)
    if "\\" in value:
        raise Q35QStageBlock(f"{label} is not a canonical distribution path")
    path = PurePosixPath(value)
    parts = path.parts
    if path.is_absolute() or str(path) != value or any(
        part in {"", "."} for part in parts
    ):
        raise Q35QStageBlock(f"{label} is not a canonical distribution path")
    first_non_parent = next(
        (index for index, part in enumerate(parts) if part != ".."), len(parts)
    )
    if first_non_parent == len(parts) or any(
        part == ".." for part in parts[first_non_parent:]
    ):
        raise Q35QStageBlock(f"{label} is not a canonical distribution path")
    return value


def _decode_record_sha256(value: str, label: str) -> bytes:
    if not value.startswith("sha256="):
        raise Q35QStageBlock(f"{label} does not use sha256")
    encoded = value[len("sha256=") :]
    if not encoded or "=" in encoded:
        raise Q35QStageBlock(
            f"{label} is not canonical unpadded urlsafe base64"
        )
    try:
        decoded = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
    except Exception as exc:
        raise Q35QStageBlock(f"{label} is not valid urlsafe base64") from exc
    if len(decoded) != 32:
        raise Q35QStageBlock(f"{label} is not a sha256 digest")
    canonical = base64.urlsafe_b64encode(decoded).decode("ascii").rstrip("=")
    if canonical != encoded:
        raise Q35QStageBlock(
            f"{label} is not canonical unpadded urlsafe base64"
        )
    return decoded


def parse_record(record_text: str) -> dict[str, dict[str, object]]:
    """Parse a wheel RECORD file and reject ambiguous or malformed identities."""
    record_text = _require_text(record_text, "RECORD text")
    entries: dict[str, dict[str, object]] = {}
    try:
        rows = csv.reader(io.StringIO(record_text, newline=""))
        for index, row in enumerate(rows, start=1):
            if len(row) != 3:
                raise Q35QStageBlock(
                    f"RECORD row {index} does not contain exactly three fields"
                )
            path = _require_canonical_distribution_path(
                row[0], f"RECORD row {index} path"
            )
            if path in entries:
                raise Q35QStageBlock(f"duplicate RECORD path: {path!r}")
            hash_field, size_field = row[1], row[2]
            if bool(hash_field) != bool(size_field):
                raise Q35QStageBlock(
                    f"RECORD row {index} has only one of hash and size"
                )
            if hash_field:
                digest = _decode_record_sha256(
                    hash_field, f"RECORD row {index} hash"
                )
                if not size_field.isdecimal():
                    raise Q35QStageBlock(
                        f"RECORD row {index} size is not a nonnegative decimal"
                    )
                size = int(size_field)
            else:
                digest = None
                size = None
            entries[path] = {"digest": digest, "size": size}
    except csv.Error as exc:
        raise Q35QStageBlock("RECORD is not valid CSV") from exc
    if not entries:
        raise Q35QStageBlock("RECORD is empty")
    return entries


def _canonical_declared_files(values: Iterable[object]) -> tuple[str, ...]:
    if isinstance(values, (str, bytes)):
        raise Q35QStageBlock("declared files must be an iterable, not a string")
    try:
        raw = tuple(values)
    except TypeError as exc:
        raise Q35QStageBlock("declared files are not iterable") from exc
    if not raw:
        raise Q35QStageBlock("distribution declared-file list is empty")
    normalized: list[str] = []
    for index, value in enumerate(raw):
        if not isinstance(value, (str, os.PathLike)):
            raise Q35QStageBlock(f"declared file {index} is not path-like")
        text = _require_canonical_distribution_path(
            os.fspath(value), f"declared file {index}"
        )
        normalized.append(text)
    if len(normalized) != len(set(normalized)):
        raise Q35QStageBlock("duplicate distribution declared-file path")
    return tuple(normalized)


def _headers(text: str, label: str):
    text = _require_text(text, label)
    message = Parser().parsestr(text)
    if message.defects:
        raise Q35QStageBlock(f"{label} is malformed")
    return message


def _direct_url_is_admissible(direct_url_text: str | None) -> bool:
    if direct_url_text is None:
        return True
    direct_url_text = _require_text(direct_url_text, "direct_url.json")
    try:
        payload = json.loads(direct_url_text)
    except json.JSONDecodeError as exc:
        raise Q35QStageBlock("direct_url.json is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise Q35QStageBlock("direct_url.json is not an object")
    # Local directories, VCS checkouts, and editable installs are outside the
    # admitted wheel-install identity. A future separately frozen exact-wheel
    # direct_url may be admitted by a stronger upstream-composition verifier.
    if payload.get("vcs_info") is not None:
        return False
    dir_info = payload.get("dir_info")
    if isinstance(dir_info, dict) and dir_info.get("editable") is True:
        return False
    url = payload.get("url")
    if isinstance(url, str) and url.startswith("file:"):
        return False
    return False


def verify_distribution_ownership(
    *,
    observed_name: str,
    observed_version: str,
    expected_name: str,
    expected_version: str,
    distribution_root: str,
    dist_info_dir: str,
    imported_package_init: str,
    expected_package_init_member: str,
    required_source_members: Iterable[str],
    declared_files: Iterable[object],
    record_text: str,
    metadata_text: str,
    wheel_text: str,
    member_bytes: Mapping[str, bytes],
    upstream_source_digests: Mapping[str, str] | None = None,
    direct_url_text: str | None = None,
) -> dict[str, object]:
    """Verify that live package files are owned by one wheel-style distribution.

    ``member_bytes`` must contain the package ``__init__``, every required source
    member, and the installed dist-info METADATA and WHEEL members. RECORD itself
    is validated structurally but may carry the standard empty self-hash.
    """
    observed_name_norm = _normalize_distribution_name(observed_name)
    expected_name_norm = _normalize_distribution_name(expected_name)
    observed_version = _require_text(observed_version, "observed version")
    expected_version = _require_text(expected_version, "expected version")
    expected_package_init_member = _require_canonical_record_path(
        expected_package_init_member, "expected package init member"
    )
    required_sources = tuple(
        _require_canonical_record_path(
            value, f"required source member {index}"
        )
        for index, value in enumerate(required_source_members)
    )
    if len(required_sources) != len(set(required_sources)):
        raise Q35QStageBlock("duplicate required source member")

    root = os.path.realpath(_require_text(distribution_root, "distribution root"))
    dist_info = os.path.realpath(
        _require_text(dist_info_dir, "dist-info directory")
    )
    imported_init = os.path.realpath(
        _require_text(imported_package_init, "imported package init")
    )
    dist_info_name = os.path.basename(dist_info)
    dist_info_parent_bound = os.path.dirname(dist_info) == root
    dist_info_suffix_bound = dist_info_name.endswith(_DIST_INFO_SUFFIX)
    expected_dist_info_name = (
        f"{expected_name_norm.replace('-', '_')}-{expected_version}"
        f"{_DIST_INFO_SUFFIX}"
    )
    dist_info_identity_bound = dist_info_name == expected_dist_info_name

    metadata = _headers(metadata_text, "METADATA")
    wheel = _headers(wheel_text, "WHEEL")
    metadata_names = metadata.get_all("Name") or []
    metadata_versions = metadata.get_all("Version") or []
    metadata_identity_bound = (
        len(metadata_names) == 1
        and len(metadata_versions) == 1
        and _normalize_distribution_name(metadata_names[0]) == expected_name_norm
        and metadata_versions[0] == expected_version
    )
    wheel_versions = wheel.get_all("Wheel-Version") or []
    purelib_values = wheel.get_all("Root-Is-Purelib") or []
    wheel_tags = wheel.get_all("Tag") or []
    wheel_identity_bound = (
        wheel_versions == ["1.0"]
        and [value.lower() for value in purelib_values] == ["true"]
        and wheel_tags == ["py3-none-any"]
    )

    declared = _canonical_declared_files(declared_files)
    record = parse_record(record_text)
    metadata_member = f"{dist_info_name}/METADATA"
    wheel_member = f"{dist_info_name}/WHEEL"
    record_member = f"{dist_info_name}/RECORD"
    required_bytes_members = (
        expected_package_init_member,
        *required_sources,
        metadata_member,
        wheel_member,
    )
    expected_member_set = set(required_bytes_members)
    if set(member_bytes) != expected_member_set:
        raise Q35QStageBlock(
            "member byte map does not equal the exact ownership evidence set"
        )
    if not all(
        isinstance(value, (bytes, bytearray))
        for value in member_bytes.values()
    ):
        raise Q35QStageBlock("member byte map contains non-bytes values")

    required_declared = expected_member_set | {record_member}
    declared_members_present = required_declared.issubset(set(declared))
    record_members_present = required_declared.issubset(set(record))

    import hashlib

    record_hashes_match = True
    record_sizes_match = True
    for member in required_bytes_members:
        entry = record.get(member)
        if entry is None or entry["digest"] is None or entry["size"] is None:
            record_hashes_match = False
            record_sizes_match = False
            continue
        data = bytes(member_bytes[member])
        record_hashes_match = (
            record_hashes_match
            and hashlib.sha256(data).digest() == entry["digest"]
        )
        record_sizes_match = record_sizes_match and len(data) == entry["size"]
    record_self_entry_valid = (
        record_member in record
        and record[record_member] == {"digest": None, "size": None}
    )

    expected_imported_init = os.path.realpath(
        os.path.join(root, *PurePosixPath(expected_package_init_member).parts)
    )
    import_owned_by_distribution = imported_init == expected_imported_init

    upstream_source_match = True
    if upstream_source_digests is not None:
        if set(upstream_source_digests) != set(required_sources):
            raise Q35QStageBlock(
                "upstream source digest map does not equal required source members"
            )
        for member in required_sources:
            expected_digest = upstream_source_digests[member]
            if not isinstance(expected_digest, str) or re.fullmatch(
                r"[0-9a-f]{64}", expected_digest
            ) is None:
                raise Q35QStageBlock(
                    "upstream source digest is not exact lowercase 64-hex"
                )
            upstream_source_match = (
                upstream_source_match
                and hashlib.sha256(bytes(member_bytes[member])).hexdigest()
                == expected_digest
            )

    direct_url_admissible = _direct_url_is_admissible(direct_url_text)
    checks = {
        "distribution_name_bound": observed_name_norm == expected_name_norm,
        "distribution_version_bound": observed_version == expected_version,
        "dist_info_parent_bound": dist_info_parent_bound,
        "dist_info_suffix_bound": dist_info_suffix_bound,
        "dist_info_identity_bound": dist_info_identity_bound,
        "metadata_identity_bound": metadata_identity_bound,
        "wheel_identity_bound": wheel_identity_bound,
        "declared_members_present": declared_members_present,
        "record_members_present": record_members_present,
        "record_hashes_match": record_hashes_match,
        "record_sizes_match": record_sizes_match,
        "record_self_entry_valid": record_self_entry_valid,
        "import_owned_by_distribution": import_owned_by_distribution,
        "upstream_source_match": upstream_source_match,
        "direct_url_admissible": direct_url_admissible,
        "required_source_count": len(required_sources),
    }
    checks["distribution_ownership_pass"] = all(
        value
        for key, value in checks.items()
        if key not in {"distribution_ownership_pass", "required_source_count"}
    )
    return checks
