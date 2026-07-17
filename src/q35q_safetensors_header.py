"""Q35Q Phase-0 metadata-only Safetensors header admission (CPU/storage/network).

Authorized by
docs/STEER_ADDENDUM_2026-07-17_Q35Q_LIVE_COMPOSITION_SELF_BINDING_AND_HEADER_GATE.md
and format-hardened per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_SAFETENSORS_FORMAT_VALIDATION_CORRECTION.md.

Reads ONLY the JSON header of each shard via a small ranged fetch (no tensor
payload bytes) and validates it against the Safetensors format so tensor shapes,
dtypes, and offsets are admissible independent evidence:

- header length: 8-byte little-endian, `0 < n <= 64 MiB`, `8 + n <= declared_size`;
- header grammar: first byte is `{`; duplicate JSON keys rejected at every level;
  only trailing ASCII-space padding after the JSON object; `__metadata__`, if
  present, is a string->string map;
- each tensor record has exactly `dtype`, `shape`, `data_offsets`; a nonempty name
  that is not the reserved metadata key;
- strict integer checks that reject booleans for every dimension/offset/length;
- shape<->span binding: `end - start == element_count(shape) * dtype_size(dtype)`
  under a frozen byte-aligned dtype table (sub-byte dtypes fail closed);
- complete hole-free coverage: nonempty spans tile `[0, data_region)` exactly.

Then reconciles the pinned weight index against the shard headers. Not weight
staging: no payload bytes fetched or cached. Aggregate/booleans/public shapes only.
"""
from __future__ import annotations

import json

MAX_HEADER_BYTES = 64 * 1024 * 1024  # frozen per-shard header ceiling
# frozen byte-aligned dtype sizes; sub-byte / packed dtypes are NOT admitted here
_DTYPE_SIZE = {
    "BOOL": 1, "U8": 1, "I8": 1, "F8_E4M3": 1, "F8_E5M2": 1,
    "U16": 2, "I16": 2, "F16": 2, "BF16": 2,
    "U32": 4, "I32": 4, "F32": 4,
    "U64": 8, "I64": 8, "F64": 8,
}


class HeaderGateBlock(Exception):
    """Fail-closed header-admission failure."""


def _sint(x) -> bool:
    """Strict nonnegative integer: rejects booleans (bool is an int subclass)."""
    return type(x) is int and x >= 0


def _no_dupes(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise HeaderGateBlock(f"duplicate JSON key: {k!r}")
        d[k] = v
    return d


def _element_count(shape) -> int:
    c = 1
    for d in shape:
        c *= d
    return c  # empty shape -> scalar (1 element); any zero dim -> 0


def parse_shard_header(fetch, shard: str, declared_size) -> dict:
    """Read + fully validate one shard's Safetensors header via ranged fetch.
    Returns {tensor_name: {'dtype','shape','start','end'}}."""
    if not _sint(declared_size) or declared_size <= 8:
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
    raw = bytes(raw)
    if raw[:1] != b"{":
        raise HeaderGateBlock(f"header does not start with '{{': {shard}")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HeaderGateBlock(f"header not valid UTF-8: {shard}")
    try:
        obj, end = json.JSONDecoder(object_pairs_hook=_no_dupes).raw_decode(text)
    except json.JSONDecodeError as e:
        raise HeaderGateBlock(f"header not valid JSON: {shard}: {e.msg}")
    if text[end:] and any(ch != " " for ch in text[end:]):
        raise HeaderGateBlock(f"non-space padding after header JSON: {shard}")
    if not isinstance(obj, dict):
        raise HeaderGateBlock(f"header is not a JSON object: {shard}")

    if "__metadata__" in obj:
        md = obj["__metadata__"]
        if not isinstance(md, dict) or not all(
                isinstance(k, str) and isinstance(v, str) for k, v in md.items()):
            raise HeaderGateBlock(f"__metadata__ is not a string->string map: {shard}")

    data_region = declared_size - 8 - n
    tensors, spans = {}, []
    for name, spec in obj.items():
        if name == "__metadata__":
            continue
        if not isinstance(name, str) or name == "":
            raise HeaderGateBlock(f"invalid tensor name: {shard}")
        if not isinstance(spec, dict) or set(spec) != {"dtype", "shape", "data_offsets"}:
            raise HeaderGateBlock(f"tensor record fields invalid: {shard}:{name}")
        dtype, shape, offs = spec["dtype"], spec["shape"], spec["data_offsets"]
        if dtype not in _DTYPE_SIZE:
            raise HeaderGateBlock(f"unsupported/sub-byte dtype {dtype!r}: {shard}")
        if not isinstance(shape, list) or not all(_sint(d) for d in shape):
            raise HeaderGateBlock(f"invalid shape: {shard}:{name}")
        if not isinstance(offs, list) or len(offs) != 2 or not all(_sint(o) for o in offs):
            raise HeaderGateBlock(f"invalid data_offsets: {shard}:{name}")
        start, endo = offs
        if start > endo or endo > data_region:
            raise HeaderGateBlock(f"data_offsets out of range: {shard}:{name}")
        expected = _element_count(shape) * _DTYPE_SIZE[dtype]
        if endo - start != expected:
            raise HeaderGateBlock(f"shape/dtype does not match byte span: {shard}:{name}")
        tensors[name] = {"dtype": dtype, "shape": shape, "start": start, "end": endo}
        spans.append((start, endo))

    # complete hole-free coverage: nonempty spans must tile [0, data_region)
    nonempty = sorted(s for s in spans if s[1] > s[0])
    cursor = 0
    for start, endo in nonempty:
        if start != cursor:
            raise HeaderGateBlock(f"hole or overlap in data region: {shard}")
        cursor = endo
    if cursor != data_region:
        raise HeaderGateBlock(f"data region not fully indexed ({cursor}/{data_region}): {shard}")
    for start, endo in spans:
        if start == endo and not (0 <= start <= data_region):
            raise HeaderGateBlock(f"zero-length tensor offset out of range: {shard}")
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
    unindexed = sorted(header_names - index_names)
    missing_tensors = sorted(index_names - header_names)
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
