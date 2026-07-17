"""Q35Q independent upstream provenance tests (CPU-only, no network; synthetic zip)."""
import io
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_upstream_provenance import (
    compare_installed_to_upstream,
    sha256,
    verify_wheel_and_extract,
)


def make_wheel(members):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, data in members.items():
            z.writestr(name, data)
    return buf.getvalue()


MEMBERS = {"transformers/conversion_mapping.py": b"CONV", "transformers/core_model_loading.py": b"CORE"}
WHEEL = make_wheel(MEMBERS)
WHEEL_SHA = sha256(WHEEL)


def test_verify_and_extract():
    out = verify_wheel_and_extract(WHEEL, WHEEL_SHA, list(MEMBERS))
    assert out["transformers/conversion_mapping.py"] == sha256(b"CONV")


def test_wheel_sha_mismatch_fails():
    with pytest.raises(Q35QStageBlock, match="does not match the pinned upstream"):
        verify_wheel_and_extract(WHEEL, "0" * 64, list(MEMBERS))


def test_bad_wheel_sha_shape_fails():
    with pytest.raises(Q35QStageBlock, match="not 64-hex"):
        verify_wheel_and_extract(WHEEL, "deadbeef", list(MEMBERS))


def test_missing_member_fails():
    with pytest.raises(Q35QStageBlock, match="member missing"):
        verify_wheel_and_extract(WHEEL, WHEEL_SHA, ["transformers/nope.py"])


def test_bad_zip_fails():
    with pytest.raises(Q35QStageBlock, match="not a valid zip"):
        verify_wheel_and_extract(b"not a zip", sha256(b"not a zip"), ["x"])


# ---------- compare installed to upstream ----------

def test_compare_bound():
    up = {"a": sha256(b"x"), "b": sha256(b"y")}
    inst = dict(up)
    out = compare_installed_to_upstream(up, inst)
    assert out["installed_bound_to_upstream"] is True


def test_compare_mismatch_fails():
    up = {"a": sha256(b"x")}
    out = compare_installed_to_upstream(up, {"a": sha256(b"TAMPERED")})
    assert out["installed_bound_to_upstream"] is False and out["mismatch_count"] == 1


def test_compare_missing_fails():
    out = compare_installed_to_upstream({"a": sha256(b"x")}, {})
    assert out["installed_bound_to_upstream"] is False and out["missing_count"] == 1


def test_compare_extra_fails():
    up = {"a": sha256(b"x")}
    out = compare_installed_to_upstream(up, {"a": sha256(b"x"), "b": sha256(b"z")})
    assert out["installed_bound_to_upstream"] is False and out["extra_count"] == 1


def test_compare_empty_upstream_fails():
    with pytest.raises(Q35QStageBlock, match="empty upstream"):
        compare_installed_to_upstream({}, {"a": "x"})
