"""Q35Q Phase-0 metadata-only Safetensors header admission (CPU/storage/network).

Authorized by
docs/STEER_ADDENDUM_2026-07-17_Q35Q_LIVE_COMPOSITION_SELF_BINDING_AND_HEADER_GATE.md.

Safetensors stores tensor name/dtype/shape/data-offsets in a JSON header at the
start of each shard; the payload is not needed for shape evidence. This module
reads only the header via a small ranged fetch and:

- parses the 8-byte little-endian header length, rejecting a length above a frozen
  64 MiB per-shard ceiling or beyond the independently declared shard size;
- parses only tensor name/dtype/shape/data-offsets, requiring valid UTF-8 JSON,
  supported dtypes, nonnegative integer shapes, and ordered non-overlapping
  offsets whose end stays within the declared data region;
- reconciles the pinned weight index against the shard headers: every indexed
  tensor appears exactly once in its declared shard, no unindexed tensor is
  admitted, every expected shard is covered, and no extra shard is consulted.

This is NOT weight staging: no tensor payload bytes are requested or cached. The
`fetch(shard, start, length) -> bytes` seam is injected so tests exercise the
same logic deterministically. Raw tensor names, URLs, paths, and response headers
stay private; only counts, booleans, and shapes for admitted tensors leave.
"""
from __future__ import annotations

import json

MAX_HEADER_BYTES = 64 * 1024 * 1024  # frozen per-shard header ceiling
# dtypes admissible for a GPTQ text-only artifact (packed int weights + scales)
_SUPPORTED_DTYPES = {
    "F16", "BF16", "F32", "F64", "I8", "I16", "I32", "I64",
    "U8", "U16", "U32", "U64", "BOOL", "F8_E4M3", "F8_E5M2",
}


class HeaderGateBlock(Exception):
    """Fail-closed header-admission failure."""


def parse_shard_header(fetch, shard: str, declared_size: int) -> dict:
    """Read + validate one shard's Safetensors header via ranged fetch. Returns
    {tensor_name: {'dtype','shape','start','end'}} for real (non-metadata) tensors."""
    if declared_size is None or declared_size <= 8:
        raise HeaderGateBlock(f"declared shard size missing/too small: {shard}")
    first8 = fetch(shard, 0, 8)
    if not isinstance(first8, (bytes, bytearray)) or len(first8) != 8:
        raise HeaderGateBlock(f"header-length range read did not return 8 bytes: {shard}")
    n = int.from_bytes(bytes(first8), "little")
    if n <= 0 or n > MAX_HEADER_BYTES:
        raise HeaderGateBlock(f"header length out of range ({n}): {shard}")
    if 8 + n > declared_size:
        raise HeaderGateBlock(f"header extends past declared shard size: {shard}")
    raw = fetch(shard, 8, n)
    if not isinstance(raw, (bytes, bytearray)) or len(raw) != n:
        raise HeaderGateBlock(f"header range read wrong length: {shard}")
    try:
        header = json.loads(bytes(raw).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise HeaderGateBlock(f"header not valid UTF-8 JSON: {shard}: {type(e).__name__}")
    if not isinstance(header, dict):
        raise HeaderGateBlock(f"header is not a JSON object: {shard}")

    data_region = declared_size - 8 - n
    tensors, spans = {}, []
    for name, spec in header.items():
        if name == "__metadata__":
            continue
        if not isinstance(spec, dict):
            raise HeaderGateBlock(f"tensor spec not an object: {shard}:{name}")
        dtype = spec.get("dtype")
        shape = spec.get("shape")
        offs = spec.get("data_offsets")
        if dtype not in _SUPPORTED_DTYPES:
            raise HeaderGateBlock(f"unsupported dtype {dtype!r}: {shard}")
        if not isinstance(shape, list) or not all(isinstance(d, int) and d >= 0 for d in shape):
            raise HeaderGateBlock(f"invalid shape: {shard}")
        if (not isinstance(offs, list) or len(offs) != 2
                or not all(isinstance(o, int) and o >= 0 for o in offs) or offs[0] > offs[1]):
            raise HeaderGateBlock(f"invalid data_offsets: {shard}")
        if offs[1] > data_region:
            raise HeaderGateBlock(f"tensor end past data region: {shard}")
        tensors[name] = {"dtype": dtype, "shape": shape, "start": offs[0], "end": offs[1]}
        spans.append((offs[0], offs[1], name))
    spans.sort()
    prev_end = 0
    for start, end, name in spans:
        if start < prev_end:
            raise HeaderGateBlock(f"overlapping tensor offsets: {shard}:{name}")
        prev_end = end
    return tensors


def reconcile_index_with_headers(weight_map: dict, shard_declared_sizes: dict, fetch) -> dict:
    """Reconcile the pinned weight index against the shard headers. `weight_map`
    maps tensor_name -> shard_name; `shard_declared_sizes` maps shard_name ->
    independently declared immutable size."""
    if not weight_map:
        raise HeaderGateBlock("empty weight index")
    indexed_shards = set(weight_map.values())
    declared_shards = set(shard_declared_sizes)
    missing_shards = sorted(indexed_shards - declared_shards)
    extra_shards = sorted(declared_shards - indexed_shards)
    if missing_shards:
        raise HeaderGateBlock(f"indexed shards without declared size: {len(missing_shards)}")
    if extra_shards:
        raise HeaderGateBlock(f"declared shards not referenced by index: {len(extra_shards)}")

    header_tensors, shapes = {}, {}
    for shard in sorted(indexed_shards):
        parsed = parse_shard_header(fetch, shard, shard_declared_sizes[shard])
        for name, spec in parsed.items():
            if name in header_tensors:
                raise HeaderGateBlock(f"tensor appears in multiple shards: {name}")
            header_tensors[name] = shard
            shapes[name] = spec["shape"]

    index_names = set(weight_map)
    header_names = set(header_tensors)
    unindexed = sorted(header_names - index_names)     # tensor in a shard, not in index
    missing_tensors = sorted(index_names - header_names)  # indexed tensor not in any header
    misplaced = sorted(t for t in index_names & header_names if header_tensors[t] != weight_map[t])
    if unindexed:
        raise HeaderGateBlock(f"unindexed tensors present in shards: {len(unindexed)}")
    if missing_tensors:
        raise HeaderGateBlock(f"indexed tensors absent from headers: {len(missing_tensors)}")
    if misplaced:
        raise HeaderGateBlock(f"tensors in wrong shard vs index: {len(misplaced)}")

    return {
        "reconciled": True,
        "shard_count": len(indexed_shards),
        "tensor_count": len(header_names),
        "each_indexed_tensor_once": True,
        "no_unindexed_tensor": True,
        "every_shard_covered": True,
        "no_extra_shard": True,
        "shapes": shapes,
    }
