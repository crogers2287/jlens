"""Q35Q metadata-only Safetensors header-gate tests (CPU-only, no network).

Drives the format-hardened parser + index reconciliation through a deterministic
fake ranged fetcher. Valid shards are built with spans that exactly tile the data
region under a frozen dtype table; adversarial cases force every format failure
the safetensors-format-validation correction requires to fail closed.
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_safetensors_header import (
    _DTYPE_SIZE,
    HeaderGateBlock,
    MAX_HEADER_BYTES,
    parse_shard_header,
    reconcile_index_with_headers,
)


def _elem(shape):
    c = 1
    for d in shape:
        c *= d
    return c


def build_shard(tensors, *, trailing_pad=0, raw_header=None, extra_region=0):
    """tensors: list of (name, dtype, shape) laid out contiguously from offset 0.
    Returns (prefix_bytes, declared_size) with a data region that exactly fits
    (plus optional extra_region to force an unindexed-hole failure)."""
    header, cursor = {}, 0
    for name, dtype, shape in tensors:
        nbytes = _elem(shape) * _DTYPE_SIZE[dtype]
        header[name] = {"dtype": dtype, "shape": shape, "data_offsets": [cursor, cursor + nbytes]}
        cursor += nbytes
    body = raw_header if raw_header is not None else json.dumps(header).encode("utf-8")
    body += b" " * trailing_pad
    n = len(body)
    prefix = struct.pack("<Q", n) + body
    return prefix, 8 + n + cursor + extra_region


def make_fetch(shard_bytes):
    def fetch(shard, start, length):
        return shard_bytes[shard][start:start + length]
    return fetch


# ---------- valid parse ----------

def test_parse_valid_tiled_header():
    prefix, size = build_shard([("a.weight", "F16", [4, 8]), ("b.weight", "I32", [2, 2])])
    out = parse_shard_header(make_fetch({"s": prefix}), "s", size)
    assert out["a.weight"]["shape"] == [4, 8] and out["b.weight"]["dtype"] == "I32"


def test_scalar_and_empty_tensor_spans():
    # scalar (1 element) then a zero-element tensor (0 bytes)
    prefix, size = build_shard([("scal", "F32", []), ("empty", "F16", [0, 8])])
    out = parse_shard_header(make_fetch({"s": prefix}), "s", size)
    assert out["scal"]["end"] - out["scal"]["start"] == 4
    assert out["empty"]["end"] == out["empty"]["start"]


# ---------- defect 1: shape/dtype bound to span ----------

def test_right_shape_wrong_span_fails():
    hdr = {"t": {"dtype": "F16", "shape": [4, 8], "data_offsets": [0, 8]}}  # needs 64 bytes
    prefix, _ = build_shard([], raw_header=json.dumps(hdr).encode())
    with pytest.raises(HeaderGateBlock, match="does not match byte span"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(prefix) - 8 + 64)


def test_wrong_shape_right_span_fails():
    # span is 64 bytes but shape claims 128 F16 elements (256 bytes)
    hdr = {"t": {"dtype": "F16", "shape": [128], "data_offsets": [0, 64]}}
    body = json.dumps(hdr).encode()
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="does not match byte span"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 64)


def test_sub_byte_dtype_fails():
    hdr = {"t": {"dtype": "I4", "shape": [8], "data_offsets": [0, 4]}}
    body = json.dumps(hdr).encode()
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="unsupported/sub-byte dtype"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 4)


# ---------- defect 2: complete hole-free coverage ----------

def test_leading_hole_fails():
    hdr = {"t": {"dtype": "F16", "shape": [4], "data_offsets": [8, 16]}}  # starts at 8, not 0
    body = json.dumps(hdr).encode()
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="hole or overlap"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 16)


def test_intermediate_hole_fails():
    hdr = {"a": {"dtype": "F16", "shape": [4], "data_offsets": [0, 8]},
           "b": {"dtype": "F16", "shape": [4], "data_offsets": [16, 24]}}  # gap 8..16
    body = json.dumps(hdr).encode()
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="hole or overlap"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 24)


def test_trailing_unindexed_bytes_fails():
    prefix, size = build_shard([("a.weight", "F16", [4])], extra_region=16)
    with pytest.raises(HeaderGateBlock, match="not fully indexed"):
        parse_shard_header(make_fetch({"s": prefix}), "s", size)


def test_overlap_fails():
    hdr = {"a": {"dtype": "F16", "shape": [8], "data_offsets": [0, 16]},
           "b": {"dtype": "F16", "shape": [8], "data_offsets": [8, 24]}}
    body = json.dumps(hdr).encode()
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="hole or overlap"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 24)


# ---------- defect 3: duplicate JSON keys ----------

def test_duplicate_tensor_name_fails():
    body = b'{"a": {"dtype":"F16","shape":[4],"data_offsets":[0,8]}, "a": {"dtype":"F16","shape":[4],"data_offsets":[8,16]}}'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="duplicate JSON key"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 16)


def test_duplicate_record_field_fails():
    body = b'{"a": {"dtype":"F16","dtype":"I32","shape":[4],"data_offsets":[0,8]}}'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="duplicate JSON key"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 8)


# ---------- defect 4: grammar ----------

def test_leading_whitespace_fails():
    body = b' {"a":{"dtype":"F16","shape":[4],"data_offsets":[0,8]}}'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="does not start with"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 8)


def test_nonspace_trailing_padding_fails():
    body = b'{"a":{"dtype":"F16","shape":[4],"data_offsets":[0,8]}}XX'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="non-space padding"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 8)


def test_space_trailing_padding_ok():
    prefix, size = build_shard([("a.weight", "F16", [4])], trailing_pad=6)
    out = parse_shard_header(make_fetch({"s": prefix}), "s", size)
    assert out["a.weight"]["shape"] == [4]


def test_bad_metadata_value_fails():
    body = b'{"__metadata__": {"k": 123}, "a":{"dtype":"F16","shape":[4],"data_offsets":[0,8]}}'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="__metadata__ is not a string"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 8)


def test_extra_record_field_fails():
    body = b'{"a":{"dtype":"F16","shape":[4],"data_offsets":[0,8],"extra":1}}'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="record fields invalid"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 8)


# ---------- defect 5: booleans rejected ----------

def test_boolean_shape_dim_fails():
    body = b'{"a":{"dtype":"F16","shape":[true],"data_offsets":[0,2]}}'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="invalid shape"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 2)


def test_boolean_offset_fails():
    body = b'{"a":{"dtype":"F16","shape":[4],"data_offsets":[false,8]}}'
    prefix = struct.pack("<Q", len(body)) + body
    with pytest.raises(HeaderGateBlock, match="invalid data_offsets"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 8)


# ---------- header length / range framing ----------

def test_zero_header_length_blocks():
    with pytest.raises(HeaderGateBlock, match="header length out of range"):
        parse_shard_header(make_fetch({"s": struct.pack("<Q", 0)}), "s", 1 << 20)


def test_header_over_ceiling_blocks():
    fetch = make_fetch({"s": struct.pack("<Q", MAX_HEADER_BYTES + 1)})
    with pytest.raises(HeaderGateBlock, match="header length out of range"):
        parse_shard_header(fetch, "s", (MAX_HEADER_BYTES + 1) << 2)


def test_short_range_read_blocks():
    with pytest.raises(HeaderGateBlock, match="did not return 8 bytes"):
        parse_shard_header(lambda *a: b"\x00\x00\x00\x00", "s", 1 << 20)


def test_declared_size_boolean_blocks():
    prefix, _ = build_shard([("a.weight", "F16", [4])])
    with pytest.raises(HeaderGateBlock, match="declared shard size"):
        parse_shard_header(make_fetch({"s": prefix}), "s", True)


# ---------- index <-> header reconciliation (preserved) ----------

def _two_shard_setup():
    p0, s0 = build_shard([("model.embed_tokens.weight", "F16", [10, 4])])
    p1, s1 = build_shard([("lm_head.weight", "F16", [10, 4])])
    fetch = make_fetch({"shard0.safetensors": p0, "shard1.safetensors": p1})
    wmap = {"model.embed_tokens.weight": "shard0.safetensors", "lm_head.weight": "shard1.safetensors"}
    sizes = {"shard0.safetensors": s0, "shard1.safetensors": s1}
    return fetch, wmap, sizes


def test_reconcile_pass():
    fetch, wmap, sizes = _two_shard_setup()
    out = reconcile_index_with_headers(wmap, sizes, fetch)
    assert out["reconciled"] and out["tensor_count"] == 2 and out["shard_count"] == 2


def test_reconcile_missing_declared_shard_blocks():
    fetch, wmap, sizes = _two_shard_setup()
    del sizes["shard1.safetensors"]
    with pytest.raises(HeaderGateBlock, match="without declared size"):
        reconcile_index_with_headers(wmap, sizes, fetch)


def test_reconcile_extra_declared_shard_blocks():
    fetch, wmap, sizes = _two_shard_setup()
    sizes["shard2.safetensors"] = 999
    with pytest.raises(HeaderGateBlock, match="not referenced by index"):
        reconcile_index_with_headers(wmap, sizes, fetch)


def test_reconcile_unindexed_tensor_blocks():
    p0, s0 = build_shard([("model.embed_tokens.weight", "F16", [4]), ("sneaky.extra", "F16", [4])])
    fetch = make_fetch({"shard0.safetensors": p0})
    wmap = {"model.embed_tokens.weight": "shard0.safetensors"}
    with pytest.raises(HeaderGateBlock, match="unindexed tensors"):
        reconcile_index_with_headers(wmap, {"shard0.safetensors": s0}, fetch)


def test_reconcile_missing_tensor_blocks():
    p0, s0 = build_shard([("model.embed_tokens.weight", "F16", [4])])
    fetch = make_fetch({"shard0.safetensors": p0})
    wmap = {"model.embed_tokens.weight": "shard0.safetensors", "lm_head.weight": "shard0.safetensors"}
    with pytest.raises(HeaderGateBlock, match="absent from headers"):
        reconcile_index_with_headers(wmap, {"shard0.safetensors": s0}, fetch)


def test_reconcile_empty_index_blocks():
    with pytest.raises(HeaderGateBlock, match="empty weight index"):
        reconcile_index_with_headers({}, {}, lambda *a: b"")
