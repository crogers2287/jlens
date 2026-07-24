"""Q35Q independent upstream provenance tests (CPU-only, no network)."""
import importlib.util
import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_upstream_provenance import (
    ADMITTED_SOURCE_MEMBERS,
    compare_installed_to_upstream,
    sha256,
    verify_wheel_and_extract,
)


def make_wheel(members):
    """Build a synthetic wheel from a mapping or an ordered pair sequence."""
    items = members.items() if isinstance(members, dict) else members
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in items:
            archive.writestr(name, data)
    return buffer.getvalue()


MEMBERS = {
    "transformers/conversion_mapping.py": b"CONV",
    "transformers/core_model_loading.py": b"CORE",
    "transformers/models/qwen3_5_moe/configuration_qwen3_5_moe.py": b"CONFIG",
    "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py": b"MODEL",
}
WHEEL = make_wheel(MEMBERS)
WHEEL_SHA = sha256(WHEEL)
UPSTREAM = {name: sha256(data) for name, data in MEMBERS.items()}


def test_configuration_source_is_in_admitted_closure():
    assert "transformers/models/qwen3_5_moe/configuration_qwen3_5_moe.py" in ADMITTED_SOURCE_MEMBERS
    assert len(ADMITTED_SOURCE_MEMBERS) == 4


def test_live_adapter_manifest_matches_upstream_closure():
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "q35q_conversion_admission.py"
    spec = importlib.util.spec_from_file_location("q35q_conversion_admission_script", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    assert tuple(module.PINNED) == ADMITTED_SOURCE_MEMBERS


def test_verify_and_extract_exact_closure():
    output = verify_wheel_and_extract(WHEEL, WHEEL_SHA, ADMITTED_SOURCE_MEMBERS)
    assert output == UPSTREAM


def test_default_member_set_is_exact_admitted_closure():
    assert verify_wheel_and_extract(WHEEL, WHEEL_SHA) == UPSTREAM


def test_wheel_sha_mismatch_fails():
    with pytest.raises(Q35QStageBlock, match="does not match the pinned upstream"):
        verify_wheel_and_extract(WHEEL, "0" * 64)


@pytest.mark.parametrize("digest", ["deadbeef", "g" * 64, "A" * 64, 7, None])
def test_bad_wheel_sha_identity_fails(digest):
    with pytest.raises(Q35QStageBlock, match="exact lowercase 64-hex"):
        verify_wheel_and_extract(WHEEL, digest)


def test_missing_member_fails():
    incomplete = dict(MEMBERS)
    incomplete.pop(ADMITTED_SOURCE_MEMBERS[-1])
    wheel = make_wheel(incomplete)
    with pytest.raises(Q35QStageBlock, match="member missing"):
        verify_wheel_and_extract(wheel, sha256(wheel))


def test_missing_configuration_member_fails():
    incomplete = dict(MEMBERS)
    incomplete.pop("transformers/models/qwen3_5_moe/configuration_qwen3_5_moe.py")
    wheel = make_wheel(incomplete)
    with pytest.raises(Q35QStageBlock, match="configuration_qwen3_5_moe"):
        verify_wheel_and_extract(wheel, sha256(wheel))


def test_bad_zip_fails():
    with pytest.raises(Q35QStageBlock, match="not a valid zip"):
        verify_wheel_and_extract(b"not a zip", sha256(b"not a zip"))


def test_duplicate_zip_member_name_fails():
    duplicate = list(MEMBERS.items()) + [(ADMITTED_SOURCE_MEMBERS[0], b"SHADOW")]
    wheel = make_wheel(duplicate)
    with pytest.raises(Q35QStageBlock, match="duplicate ZIP member"):
        verify_wheel_and_extract(wheel, sha256(wheel))


def test_duplicate_requested_member_path_fails():
    requested = list(ADMITTED_SOURCE_MEMBERS) + [ADMITTED_SOURCE_MEMBERS[0]]
    with pytest.raises(Q35QStageBlock, match="duplicate requested"):
        verify_wheel_and_extract(WHEEL, WHEEL_SHA, requested)


@pytest.mark.parametrize(
    "requested",
    [
        ADMITTED_SOURCE_MEMBERS[:-1],
        ADMITTED_SOURCE_MEMBERS + ("transformers/extra.py",),
    ],
)
def test_requested_members_must_equal_exact_closure(requested):
    with pytest.raises(Q35QStageBlock, match="exact admitted source closure"):
        verify_wheel_and_extract(WHEEL, WHEEL_SHA, requested)


@pytest.mark.parametrize(
    "bad_path",
    [
        "/transformers/conversion_mapping.py",
        "transformers/../conversion_mapping.py",
        "transformers//conversion_mapping.py",
        "transformers\\conversion_mapping.py",
        "transformers/./conversion_mapping.py",
        "transformers/conversion_mapping.py\x00",
    ],
)
def test_requested_members_must_be_canonical_relative_posix(bad_path):
    requested = list(ADMITTED_SOURCE_MEMBERS)
    requested[0] = bad_path
    with pytest.raises(Q35QStageBlock, match="canonical relative POSIX"):
        verify_wheel_and_extract(WHEEL, WHEEL_SHA, requested)


def test_member_paths_string_is_rejected():
    with pytest.raises(Q35QStageBlock, match="not a string"):
        verify_wheel_and_extract(WHEEL, WHEEL_SHA, ADMITTED_SOURCE_MEMBERS[0])


# ---------- compare installed to upstream ----------

def test_compare_bound():
    output = compare_installed_to_upstream(UPSTREAM, dict(UPSTREAM))
    assert output["installed_bound_to_upstream"] is True
    assert output["member_count"] == 4


def test_compare_mismatch_reports_fail_closed():
    installed = dict(UPSTREAM)
    installed[ADMITTED_SOURCE_MEMBERS[0]] = sha256(b"TAMPERED")
    output = compare_installed_to_upstream(UPSTREAM, installed)
    assert output["installed_bound_to_upstream"] is False
    assert output["mismatch_count"] == 1


def test_compare_missing_reports_fail_closed():
    installed = dict(UPSTREAM)
    installed.pop(ADMITTED_SOURCE_MEMBERS[0])
    output = compare_installed_to_upstream(UPSTREAM, installed)
    assert output["installed_bound_to_upstream"] is False
    assert output["missing_count"] == 1


def test_compare_extra_reports_fail_closed():
    installed = dict(UPSTREAM)
    installed["transformers/extra.py"] = sha256(b"EXTRA")
    output = compare_installed_to_upstream(UPSTREAM, installed)
    assert output["installed_bound_to_upstream"] is False
    assert output["extra_count"] == 1


@pytest.mark.parametrize(
    "upstream",
    [
        {},
        {ADMITTED_SOURCE_MEMBERS[0]: UPSTREAM[ADMITTED_SOURCE_MEMBERS[0]]},
        {**UPSTREAM, "transformers/extra.py": sha256(b"EXTRA")},
    ],
)
def test_upstream_digest_map_must_equal_exact_closure(upstream):
    with pytest.raises(Q35QStageBlock, match="exact admitted source closure"):
        compare_installed_to_upstream(upstream, dict(UPSTREAM))


@pytest.mark.parametrize("bad_digest", ["g" * 64, "A" * 64, "short", None])
def test_upstream_digest_values_must_be_lower_hex(bad_digest):
    upstream = dict(UPSTREAM)
    upstream[ADMITTED_SOURCE_MEMBERS[0]] = bad_digest
    with pytest.raises(Q35QStageBlock, match="exact lowercase 64-hex"):
        compare_installed_to_upstream(upstream, dict(UPSTREAM))


def test_installed_digest_values_must_be_lower_hex():
    installed = dict(UPSTREAM)
    installed[ADMITTED_SOURCE_MEMBERS[0]] = "g" * 64
    with pytest.raises(Q35QStageBlock, match="exact lowercase 64-hex"):
        compare_installed_to_upstream(UPSTREAM, installed)


def test_installed_digest_paths_must_be_canonical():
    installed = dict(UPSTREAM)
    value = installed.pop(ADMITTED_SOURCE_MEMBERS[0])
    installed["transformers/../conversion_mapping.py"] = value
    with pytest.raises(Q35QStageBlock, match="canonical relative POSIX"):
        compare_installed_to_upstream(UPSTREAM, installed)
