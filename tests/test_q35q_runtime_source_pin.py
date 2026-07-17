"""Q35Q runtime source-digest pin tests (CPU-only, no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_runtime_source_pin import bind_source_digests, source_sha256

A = "a" * 64
B = "b" * 64


def test_source_sha256_known():
    assert source_sha256(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_bind_pass():
    out = bind_source_digests({"f1": A, "f2": B}, {"f1": A, "f2": B})
    assert out["source_pin_pass"] is True and out["files_bound"] == 2


def test_mismatch_fails():
    with pytest.raises(Q35QStageBlock, match="source-digest mismatch"):
        bind_source_digests({"f1": A}, {"f1": B})


def test_missing_file_fails():
    with pytest.raises(Q35QStageBlock, match="missing pinned source files"):
        bind_source_digests({}, {"f1": A})


def test_extra_file_fails():
    with pytest.raises(Q35QStageBlock, match="unexpected extra source files"):
        bind_source_digests({"f1": A, "f2": B}, {"f1": A})


def test_bad_expected_digest_fails():
    with pytest.raises(Q35QStageBlock, match="not a 64-hex sha256"):
        bind_source_digests({"f1": A}, {"f1": "deadbeef"})


def test_empty_expected_fails():
    with pytest.raises(Q35QStageBlock, match="empty expected"):
        bind_source_digests({"f1": A}, {})
