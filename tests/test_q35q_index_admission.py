"""Q35Q strict weight-index admission tests (CPU-only, no network).

Proves identity verification (Git blob sha1) and the frozen grammar fail closed on
a bytes mismatch, duplicate JSON keys, unknown top-level fields, missing/empty
weight_map, non-string/empty/boolean shard paths, path traversal, and non-
.safetensors shards.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_index_admission import (
    admit_weight_index,
    content_sha256,
    git_blob_sha1,
    parse_weight_index_strict,
    verify_index_identity,
)


def _idx(weight_map, metadata=None, extra=None):
    obj = {"weight_map": weight_map}
    if metadata is not None:
        obj["metadata"] = metadata
    if extra:
        obj.update(extra)
    return json.dumps(obj).encode("utf-8")


GOOD = _idx({"model.embed_tokens.weight": "model-00001.safetensors",
             "lm_head.weight": "model-00002.safetensors"}, metadata={"total_size": 100})


# ---------- git blob identity ----------

def test_git_blob_sha1_known_value():
    # `printf '' | git hash-object --stdin` -> e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
    assert git_blob_sha1(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"


def test_content_sha256_known_value():
    # sha256("") -> e3b0c442...
    assert content_sha256(b"") == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"


def test_verify_identity_ok():
    assert verify_index_identity(GOOD, content_sha256(GOOD)) == content_sha256(GOOD)


def test_verify_identity_mismatch_fails():
    with pytest.raises(Q35QStageBlock, match="do not match the frozen remote identity"):
        verify_index_identity(GOOD, "0" * 64)


def test_verify_identity_bad_shape_fails():
    with pytest.raises(Q35QStageBlock, match="not a 64-hex sha256"):
        verify_index_identity(GOOD, "deadbeef")


# ---------- strict grammar ----------

def test_parse_ok():
    out = parse_weight_index_strict(GOOD)
    assert out["tensor_count"] == 2 and out["shard_set"] == {"model-00001.safetensors", "model-00002.safetensors"}


def test_duplicate_key_fails():
    body = b'{"weight_map": {"a": "m1.safetensors", "a": "m2.safetensors"}}'
    with pytest.raises(Q35QStageBlock, match="duplicate JSON key"):
        parse_weight_index_strict(body)


def test_unknown_top_field_fails():
    with pytest.raises(Q35QStageBlock, match="unknown top-level fields"):
        parse_weight_index_strict(_idx({"a": "m.safetensors"}, extra={"rogue": 1}))


def test_missing_weight_map_fails():
    with pytest.raises(Q35QStageBlock, match="missing weight_map"):
        parse_weight_index_strict(json.dumps({"metadata": {}}).encode())


def test_empty_weight_map_fails():
    with pytest.raises(Q35QStageBlock, match="nonempty object"):
        parse_weight_index_strict(_idx({}))


def test_boolean_shard_path_fails():
    body = b'{"weight_map": {"a": true}}'
    with pytest.raises(Q35QStageBlock, match="shard path invalid"):
        parse_weight_index_strict(body)


def test_empty_tensor_name_fails():
    body = b'{"weight_map": {"": "m.safetensors"}}'
    with pytest.raises(Q35QStageBlock, match="empty/non-string tensor name"):
        parse_weight_index_strict(body)


def test_path_traversal_shard_fails():
    with pytest.raises(Q35QStageBlock, match="escapes"):
        parse_weight_index_strict(_idx({"a": "../secret.safetensors"}))


def test_absolute_shard_path_fails():
    with pytest.raises(Q35QStageBlock, match="escapes"):
        parse_weight_index_strict(_idx({"a": "/etc/x.safetensors"}))


def test_non_safetensors_shard_fails():
    with pytest.raises(Q35QStageBlock, match="not a .safetensors"):
        parse_weight_index_strict(_idx({"a": "m.bin"}))


def test_metadata_non_object_fails():
    body = b'{"weight_map": {"a": "m.safetensors"}, "metadata": 5}'
    with pytest.raises(Q35QStageBlock, match="metadata is not an object"):
        parse_weight_index_strict(body)


def test_bad_utf8_fails():
    with pytest.raises(Q35QStageBlock, match="not valid UTF-8 JSON"):
        parse_weight_index_strict(b"\xff\xfe{}")


# ---------- end to end ----------

def test_admit_ok():
    out = admit_weight_index(GOOD, content_sha256(GOOD))
    assert out["tensor_count"] == 2 and out["index_sha256"] == content_sha256(GOOD)


def test_admit_identity_first_then_parse():
    # identity mismatch must fail before grammar is even considered
    with pytest.raises(Q35QStageBlock, match="frozen remote identity"):
        admit_weight_index(b'{"weight_map": {"a": "m.safetensors"}}', "0" * 64)
