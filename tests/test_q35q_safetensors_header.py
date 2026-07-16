"""Q35Q metadata-only Safetensors header-gate tests (CPU-only, no network).

Drives the header parse + index reconciliation through a deterministic fake
ranged fetcher, forcing every failure the header-gate addendum requires to fail
closed: bad header length, over-ceiling, past declared size, short read, bad
UTF-8/JSON, unsupported dtype, invalid shape/offsets, out-of-region and
overlapping offsets, and index/header reconciliation mismatches.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_safetensors_header import (
    HeaderGateBlock,
    MAX_HEADER_BYTES,
    parse_shard_header,
    reconcile_index_with_headers,
)


def build_shard(tensors, *, data_region=None):
    """tensors: {name: (dtype, shape, start, end)} -> (prefix_bytes, declared_size)."""
    header = {n: {"dtype": dt, "shape": sh, "data_offsets": [s, e]}
              for n, (dt, sh, s, e) in tensors.items()}
    hb = json.dumps(header).encode("utf-8")
    n = len(hb)
    region = data_region if data_region is not None else max([e for *_, e in tensors.values()] + [0])
    prefix = n.to_bytes(8, "little") + hb
    return prefix, 8 + n + region


def make_fetch(shard_bytes):
    def fetch(shard, start, length):
        return shard_bytes[shard][start:start + length]
    return fetch


# ---------- single-shard parse ----------

def test_parse_valid_header():
    prefix, size = build_shard({"model.embed_tokens.weight": ("F16", [248320, 2048], 0, 1016463360)})
    out = parse_shard_header(make_fetch({"s": prefix}), "s", size)
    assert out["model.embed_tokens.weight"]["shape"] == [248320, 2048]


def test_zero_header_length_blocks():
    fetch = make_fetch({"s": (0).to_bytes(8, "little")})
    with pytest.raises(HeaderGateBlock, match="header length out of range"):
        parse_shard_header(fetch, "s", 1 << 20)


def test_header_over_ceiling_blocks():
    fetch = make_fetch({"s": (MAX_HEADER_BYTES + 1).to_bytes(8, "little")})
    with pytest.raises(HeaderGateBlock, match="header length out of range"):
        parse_shard_header(fetch, "s", MAX_HEADER_BYTES + 1 << 4)


def test_header_past_declared_size_blocks():
    prefix, size = build_shard({"t": ("F16", [4], 0, 8)})
    with pytest.raises(HeaderGateBlock, match="past declared shard size"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 10)  # too small


def test_short_range_read_blocks():
    def fetch(shard, start, length):
        return b"\x00\x00\x00\x00"  # only 4 bytes for the 8-byte read
    with pytest.raises(HeaderGateBlock, match="did not return 8 bytes"):
        parse_shard_header(fetch, "s", 1 << 20)


def test_bad_utf8_json_blocks():
    body = b"\xff\xfe not json"
    prefix = len(body).to_bytes(8, "little") + body
    with pytest.raises(HeaderGateBlock, match="valid UTF-8 JSON"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + len(body) + 100)


def test_unsupported_dtype_blocks():
    prefix, size = build_shard({"t": ("COMPLEX128", [2], 0, 32)})
    with pytest.raises(HeaderGateBlock, match="unsupported dtype"):
        parse_shard_header(make_fetch({"s": prefix}), "s", size)


def test_negative_shape_blocks():
    prefix, size = build_shard({"t": ("F16", [-1, 8], 0, 16)})
    with pytest.raises(HeaderGateBlock, match="invalid shape"):
        parse_shard_header(make_fetch({"s": prefix}), "s", size)


def test_bad_offsets_blocks():
    prefix, size = build_shard({"t": ("F16", [4], 8, 4)})  # start > end
    with pytest.raises(HeaderGateBlock, match="invalid data_offsets"):
        parse_shard_header(make_fetch({"s": prefix}), "s", size)


def test_offset_past_data_region_blocks():
    prefix, _ = build_shard({"t": ("F16", [4], 0, 8)})
    # declare a shard size that leaves a data region smaller than the tensor end
    with pytest.raises(HeaderGateBlock, match="past data region"):
        parse_shard_header(make_fetch({"s": prefix}), "s", 8 + (len(prefix) - 8) + 4)


def test_overlapping_offsets_blocks():
    prefix, size = build_shard({"a": ("F16", [8], 0, 16), "b": ("F16", [8], 8, 24)})
    with pytest.raises(HeaderGateBlock, match="overlapping"):
        parse_shard_header(make_fetch({"s": prefix}), "s", size)


# ---------- index <-> header reconciliation ----------

def _two_shard_setup():
    p0, s0 = build_shard({"model.embed_tokens.weight": ("F16", [248320, 2048], 0, 100)})
    p1, s1 = build_shard({"lm_head.weight": ("F16", [248320, 2048], 0, 100)})
    fetch = make_fetch({"shard0.safetensors": p0, "shard1.safetensors": p1})
    wmap = {"model.embed_tokens.weight": "shard0.safetensors", "lm_head.weight": "shard1.safetensors"}
    sizes = {"shard0.safetensors": s0, "shard1.safetensors": s1}
    return fetch, wmap, sizes


def test_reconcile_pass():
    fetch, wmap, sizes = _two_shard_setup()
    out = reconcile_index_with_headers(wmap, sizes, fetch)
    assert out["reconciled"] and out["tensor_count"] == 2 and out["shard_count"] == 2
    assert out["shapes"]["lm_head.weight"] == [248320, 2048]


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
    p0, s0 = build_shard({"model.embed_tokens.weight": ("F16", [4], 0, 8),
                          "sneaky.extra": ("F16", [4], 8, 16)})
    fetch = make_fetch({"shard0.safetensors": p0})
    wmap = {"model.embed_tokens.weight": "shard0.safetensors"}
    with pytest.raises(HeaderGateBlock, match="unindexed tensors"):
        reconcile_index_with_headers(wmap, {"shard0.safetensors": s0}, fetch)


def test_reconcile_missing_tensor_blocks():
    p0, s0 = build_shard({"model.embed_tokens.weight": ("F16", [4], 0, 8)})
    fetch = make_fetch({"shard0.safetensors": p0})
    wmap = {"model.embed_tokens.weight": "shard0.safetensors", "lm_head.weight": "shard0.safetensors"}
    with pytest.raises(HeaderGateBlock, match="absent from headers"):
        reconcile_index_with_headers(wmap, {"shard0.safetensors": s0}, fetch)


def test_reconcile_misplaced_tensor_blocks():
    p0, s0 = build_shard({"a.weight": ("F16", [4], 0, 8)})
    p1, s1 = build_shard({"b.weight": ("F16", [4], 0, 8)})
    fetch = make_fetch({"shard0.safetensors": p0, "shard1.safetensors": p1})
    # index claims a.weight lives in shard1 but the header puts it in shard0
    wmap = {"a.weight": "shard1.safetensors", "b.weight": "shard1.safetensors"}
    sizes = {"shard0.safetensors": s0, "shard1.safetensors": s1}
    with pytest.raises(HeaderGateBlock):
        reconcile_index_with_headers(wmap, sizes, fetch)


def test_reconcile_empty_index_blocks():
    with pytest.raises(HeaderGateBlock, match="empty weight index"):
        reconcile_index_with_headers({}, {}, lambda *a: b"")
