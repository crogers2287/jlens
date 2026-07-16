"""Q35Q Phase-0 staging-orchestration integration tests (CPU-only, no network/model).

Drives each required failure condition through the *same* orchestration the CLI
uses (`run_staging_orchestration`) via a deterministic fake remote manifest and a
fake downloader, proving the missing-file, partial, extra, checksum, storage,
resume, path-escape, and mutable-revision branches are actually reachable — the
gap the second-correction addendum flagged (defect 6).
"""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_orchestration import (
    RemoteFile,
    StorageInputs,
    build_expected_admitted,
    reconcile_checksums,
    reconcile_presence,
    run_staging_orchestration,
    storage_resumability_gate,
)
from q35q_stage import Q35QStageBlock

REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"
SMALL = ("config.json", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 16), b""):
            h.update(c)
    return h.hexdigest()


def _content(name):
    return f"pinned-public-content-of::{name}".encode()


def _digest(name):
    return hashlib.sha256(_content(name)).hexdigest()


def _remote_manifest():
    # small admitted files carry immutable lfs/blob sha256 identities; one weight
    # is present in the remote manifest but is not an admission file.
    files = [RemoteFile(n, len(_content(n)), _digest(n), "lfs_sha256") for n in SMALL]
    files.append(RemoteFile("model-00001-of-00002.safetensors", 22_000_000_000, "e" * 64, "lfs_sha256"))
    return files


def _good_storage(**over):
    base = dict(
        free_bytes=200 * 2**30, expected_weight_bytes=90 * 2**30,
        temp_overhead_bytes=10 * 2**30, safety_margin_bytes=20 * 2**30,
        partial_files_detected=False, partial_cleanup_done=True,
        interrupted_resume_matches=True, final_manifest_reconciled=True,
        cache_isolated_from_unrelated_tenant=True)
    base.update(over)
    return StorageInputs(**base)


def _make_downloader(*, drop=None, partial=None, extra=None, corrupt=None, cache=None):
    """Fake downloader: writes the expected small files, minus/plus forced faults."""
    def dl(revision, expected, staging_root):
        root = Path(staging_root)
        for name in expected:
            if name == drop:
                continue
            data = _content(name)
            if name == corrupt:
                data = b"tampered-" + data
            (root / name).parent.mkdir(parents=True, exist_ok=True)
            (root / name).write_bytes(data)
        if partial:
            (root / partial).write_bytes(b"half")  # .incomplete-style name
        if extra:
            (root / extra).write_bytes(b"rogue")
        if cache:
            (root / cache).parent.mkdir(parents=True, exist_ok=True)
            (root / cache).write_bytes(b"cache")
    return dl


def _run(tmp_path, downloader, storage=None):
    return run_staging_orchestration(
        revision=REV, remote_provider=lambda r: _remote_manifest(),
        downloader=downloader, staging_root=str(tmp_path / "stage"),
        hasher=_sha, small_ok_suffixes=SMALL, storage=storage or _good_storage())


# ---------- happy path ----------

def test_full_orchestration_passes(tmp_path):
    out = _run(tmp_path, _make_downloader())
    assert out["overall_pass"] is True
    assert out["presence"]["all_expected_present"] is True
    assert out["checksums"]["all_match"] is True
    assert out["checksums"]["checksum_verified_count"] == len(SMALL)
    assert out["storage"]["all_required_pass"] is True


# ---------- defect 1: missing / partial / extra reachable through orchestration ----------

def test_missing_expected_file_fails_closed(tmp_path):
    with pytest.raises(Q35QStageBlock, match="missing expected"):
        _run(tmp_path, _make_downloader(drop="tokenizer.json"))


def test_partial_download_detected_fails_closed(tmp_path):
    # an uncleaned .incomplete file signals an interrupted download -> fail closed
    with pytest.raises(Q35QStageBlock, match="partial/interrupted"):
        _run(tmp_path, _make_downloader(partial="config.json.incomplete"))


def test_extra_unapproved_file_fails_closed(tmp_path):
    with pytest.raises(Q35QStageBlock, match="unapproved extra"):
        _run(tmp_path, _make_downloader(extra="rogue.py"))


def test_stale_cache_excluded_not_extra(tmp_path):
    out = _run(tmp_path, _make_downloader(cache=".cache/huggingface/x"))
    assert out["overall_pass"] is True  # cache path excluded, not counted


# ---------- defect 2: checksum bound to remote identity, not self-hash ----------

def test_wrong_checksum_fails_closed(tmp_path):
    with pytest.raises(Q35QStageBlock, match="checksum mismatch"):
        _run(tmp_path, _make_downloader(corrupt="config.json"))


def test_missing_immutable_identity_blocks():
    expected = {"config.json": RemoteFile("config.json", 3, None, None)}
    with pytest.raises(Q35QStageBlock, match="immutable checksum identity"):
        reconcile_checksums(expected, {"config.json": "a" * 64})


def test_checksum_is_not_self_referential():
    # expected from remote metadata; observed from local. Different sources.
    expected = {"config.json": RemoteFile("config.json", 3, "a" * 64, "lfs_sha256")}
    v = reconcile_checksums(expected, {"config.json": "a" * 64})
    assert v["pass"] and v["checksum_verified_count"] == 1


# ---------- defect 3: storage / resume gate in the conjunction ----------

def test_insufficient_free_space_fails(tmp_path):
    with pytest.raises(Q35QStageBlock, match="storage"):
        _run(tmp_path, _make_downloader(), storage=_good_storage(free_bytes=1 * 2**30))


def test_cleanup_failure_fails():
    with pytest.raises(Q35QStageBlock):
        storage_resumability_gate(_good_storage(
            partial_files_detected=True, partial_cleanup_done=False))


def test_resume_mismatch_fails():
    with pytest.raises(Q35QStageBlock):
        storage_resumability_gate(_good_storage(interrupted_resume_matches=False))


def test_missing_safety_margin_fails():
    with pytest.raises(Q35QStageBlock):
        storage_resumability_gate(_good_storage(safety_margin_bytes=0))


def test_cache_not_isolated_fails():
    with pytest.raises(Q35QStageBlock):
        storage_resumability_gate(_good_storage(cache_isolated_from_unrelated_tenant=False))


# ---------- revision / path-escape guards ----------

def test_mutable_revision_blocked(tmp_path):
    with pytest.raises(Q35QStageBlock, match="immutable 40-hex"):
        run_staging_orchestration(
            revision="main", remote_provider=lambda r: _remote_manifest(),
            downloader=_make_downloader(), staging_root=str(tmp_path / "s"),
            hasher=_sha, small_ok_suffixes=SMALL, storage=_good_storage())


def test_path_escape_in_remote_manifest_blocked():
    with pytest.raises(Q35QStageBlock, match="path escape"):
        build_expected_admitted([RemoteFile("../escape.json", 3, "a" * 64, "lfs_sha256")], SMALL)


def test_cache_name_in_admitted_blocked():
    with pytest.raises(Q35QStageBlock, match="cache/metadata"):
        build_expected_admitted([RemoteFile(".cache/config.json", 3, "a" * 64, "lfs_sha256")], SMALL)


def test_empty_expected_set_blocked():
    with pytest.raises(Q35QStageBlock, match="empty expected"):
        build_expected_admitted([RemoteFile("model.safetensors", 3, "a" * 64, "lfs_sha256")], SMALL)


def test_presence_missing_reported_not_dropped():
    v_names = ["config.json", "tokenizer.json"]
    with pytest.raises(Q35QStageBlock, match="missing expected"):
        reconcile_presence(v_names, ["config.json"])
