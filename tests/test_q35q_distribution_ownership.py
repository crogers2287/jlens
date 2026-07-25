"""Q35Q installed-distribution ownership tests (CPU-only, no network)."""
from __future__ import annotations

import base64
import csv
import hashlib
import io
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from q35q_distribution_ownership import parse_record, verify_distribution_ownership
from q35q_stage import Q35QStageBlock

ROOT = "/venv/site-packages"
DIST_PREFIX = "transformers-5.13.1.dist-info"
SOURCES = (
    "transformers/conversion_mapping.py",
    "transformers/core_model_loading.py",
    "transformers/models/qwen3_5_moe/configuration_qwen3_5_moe.py",
    "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py",
)
METADATA = "Metadata-Version: 2.4\nName: transformers\nVersion: 5.13.1\n\n"
WHEEL = "Wheel-Version: 1.0\nRoot-Is-Purelib: true\nTag: py3-none-any\n\n"
MEMBERS = {
    "transformers/__init__.py": b"INIT",
    SOURCES[0]: b"CONV",
    SOURCES[1]: b"CORE",
    SOURCES[2]: b"CONFIG",
    SOURCES[3]: b"MODEL",
    f"{DIST_PREFIX}/METADATA": METADATA.encode(),
    f"{DIST_PREFIX}/WHEEL": WHEEL.encode(),
}


def _record_hash(data: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(data).digest())
    return "sha256=" + digest.decode().rstrip("=")


def _record(members=MEMBERS, *, duplicate=None):
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    for path, data in members.items():
        writer.writerow([path, _record_hash(data), str(len(data))])
    writer.writerow([f"{DIST_PREFIX}/RECORD", "", ""])
    if duplicate is not None:
        writer.writerow(
            [duplicate, _record_hash(members[duplicate]), str(len(members[duplicate]))]
        )
    return output.getvalue()


def _baseline(**overrides):
    kwargs = {
        "observed_name": "transformers",
        "observed_version": "5.13.1",
        "expected_name": "transformers",
        "expected_version": "5.13.1",
        "distribution_root": ROOT,
        "dist_info_dir": f"{ROOT}/{DIST_PREFIX}",
        "imported_package_init": f"{ROOT}/transformers/__init__.py",
        "expected_package_init_member": "transformers/__init__.py",
        "required_source_members": SOURCES,
        "declared_files": tuple(MEMBERS)
        + (f"{DIST_PREFIX}/RECORD", "../../../bin/transformers-cli"),
        "record_text": _record(),
        "metadata_text": METADATA,
        "wheel_text": WHEEL,
        "member_bytes": dict(MEMBERS),
        "upstream_source_digests": {
            source: hashlib.sha256(MEMBERS[source]).hexdigest()
            for source in SOURCES
        },
        "direct_url_text": None,
    }
    kwargs.update(overrides)
    return verify_distribution_ownership(**kwargs)


def test_baseline_passes():
    result = _baseline()
    assert result["distribution_ownership_pass"] is True
    assert result["required_source_count"] == 4


@pytest.mark.parametrize(
    "overrides,failed_check",
    [
        (
            {"imported_package_init": "/alternate/transformers/__init__.py"},
            "import_owned_by_distribution",
        ),
        (
            {"dist_info_dir": "/alternate/transformers-5.13.1.dist-info"},
            "dist_info_parent_bound",
        ),
        ({"observed_version": "5.13.0"}, "distribution_version_bound"),
        (
            {"metadata_text": METADATA.replace("5.13.1", "5.13.0")},
            "metadata_identity_bound",
        ),
        ({"wheel_text": WHEEL.replace("true", "false")}, "wheel_identity_bound"),
    ],
)
def test_identity_mismatch_fails(overrides, failed_check):
    result = _baseline(**overrides)
    assert result[failed_check] is False
    assert result["distribution_ownership_pass"] is False


def test_record_hash_mismatch_fails():
    changed = dict(MEMBERS)
    changed[SOURCES[0]] = b"CHANGED"
    result = _baseline(member_bytes=changed)
    assert result["record_hashes_match"] is False
    assert result["distribution_ownership_pass"] is False


def test_record_size_mismatch_fails():
    text = _record().replace(f",{len(MEMBERS[SOURCES[0]])}\n", ",999\n", 1)
    result = _baseline(record_text=text)
    assert result["record_sizes_match"] is False
    assert result["distribution_ownership_pass"] is False


def test_missing_declared_or_record_member_fails():
    declared = tuple(path for path in MEMBERS if path != SOURCES[0]) + (
        f"{DIST_PREFIX}/RECORD",
    )
    result = _baseline(declared_files=declared)
    assert result["declared_members_present"] is False
    reduced = dict(MEMBERS)
    reduced.pop(SOURCES[0])
    result = _baseline(record_text=_record(reduced))
    assert result["record_members_present"] is False


def test_upstream_source_mismatch_fails():
    digests = {
        source: hashlib.sha256(MEMBERS[source]).hexdigest() for source in SOURCES
    }
    digests[SOURCES[0]] = "0" * 64
    result = _baseline(upstream_source_digests=digests)
    assert result["upstream_source_match"] is False
    assert result["distribution_ownership_pass"] is False


def test_direct_install_metadata_fails_closed():
    payload = json.dumps(
        {"url": "https://example.invalid/archive.whl", "archive_info": {}}
    )
    result = _baseline(direct_url_text=payload)
    assert result["direct_url_admissible"] is False
    assert result["distribution_ownership_pass"] is False


def test_duplicate_record_path_raises():
    with pytest.raises(Q35QStageBlock, match="duplicate RECORD"):
        parse_record(_record(duplicate=SOURCES[0]))


@pytest.mark.parametrize(
    "path",
    [
        "transformers/../other.py",
        "../../../bin/../other",
        "../../..",
        ".././bin/tool",
    ],
)
def test_noncanonical_record_paths_raise(path):
    with pytest.raises(Q35QStageBlock, match="canonical distribution path"):
        parse_record(f"{path},,\n")


def test_generated_script_record_path_is_valid():
    parsed = parse_record(
        _record({**MEMBERS, "../../../bin/transformers-cli": b"SCRIPT"})
    )
    assert "../../../bin/transformers-cli" in parsed


def test_member_byte_map_must_be_exact():
    with pytest.raises(Q35QStageBlock, match="exact ownership evidence set"):
        _baseline(member_bytes={**MEMBERS, "transformers/extra.py": b"EXTRA"})
