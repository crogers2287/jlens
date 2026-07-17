"""Q35Q Phase-0 strict weight-index admission (CPU-only, pure).

Defect 4 of
docs/STEER_ADDENDUM_2026-07-17_Q35Q_HEADER_REDIRECT_AND_MODULE_RECONCILIATION_CORRECTION.md:
`model.safetensors.index.json` is the authoritative tensor->shard map, so it may
not be admitted through a fail-open `json.load` over unverified local bytes. This
module:

- verifies the downloaded index bytes against an independently frozen immutable
  identity (the LFS sha256 the Hub reports for the content) BEFORE parsing; the
  index is LFS-backed (~15 MB / 124k tensors), so its content identity is the LFS
  object sha256, NOT the git blob sha1 (which hashes only the small LFS pointer);
- parses with duplicate-key rejection at every object level;
- validates a frozen grammar: a top-level object whose keys are a subset of
  {metadata, weight_map}; a nonempty `weight_map` of nonempty string tensor names
  to nonempty string `.safetensors` shard paths with no absolute paths or `..`
  traversal; booleans and non-string names/paths rejected; `metadata`, if present,
  an object.

Pure over bytes; the live CLI supplies the downloaded bytes and the frozen
expected identity. Returns the validated weight_map + shard set + counts.
"""
from __future__ import annotations

import hashlib
import json

from q35q_stage import Q35QStageBlock

_ALLOWED_TOP = {"metadata", "weight_map"}


def git_blob_sha1(data: bytes) -> str:
    """Git blob object id: sha1(b"blob <len>\\0" + data). This is the immutable
    identity the Hub reports for a small (non-LFS) file."""
    h = hashlib.sha1()
    h.update(b"blob " + str(len(data)).encode() + b"\0")
    h.update(data)
    return h.hexdigest()


def content_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verify_index_identity(local_bytes: bytes, expected_sha256: str) -> str:
    """Fail closed unless the local index bytes' sha256 equals the frozen immutable
    LFS object sha256 the Hub reports for the index content."""
    if not isinstance(expected_sha256, str) or len(expected_sha256) != 64 \
            or any(c not in "0123456789abcdef" for c in expected_sha256):
        raise Q35QStageBlock("expected index identity is not a 64-hex sha256")
    observed = content_sha256(local_bytes)
    if observed != expected_sha256:
        raise Q35QStageBlock("weight-index local bytes do not match the frozen remote identity")
    return observed


def _no_dupes(pairs):
    d = {}
    for k, v in pairs:
        if k in d:
            raise Q35QStageBlock(f"duplicate JSON key in weight index: {k!r}")
        d[k] = v
    return d


def parse_weight_index_strict(local_bytes: bytes) -> dict:
    """Parse + grammar-validate the weight index. Duplicate keys, unknown top-level
    fields, non-string/empty tensor names or shard paths, booleans, absolute paths,
    `..` traversal, and non-`.safetensors` shards all fail closed."""
    try:
        obj = json.loads(local_bytes.decode("utf-8"), object_pairs_hook=_no_dupes)
    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        raise Q35QStageBlock(f"weight index not valid UTF-8 JSON: {type(e).__name__}")
    if not isinstance(obj, dict):
        raise Q35QStageBlock("weight index top level is not an object")
    extra = set(obj) - _ALLOWED_TOP
    if extra:
        raise Q35QStageBlock(f"weight index has unknown top-level fields: {sorted(extra)}")
    if "weight_map" not in obj:
        raise Q35QStageBlock("weight index missing weight_map")
    wm = obj["weight_map"]
    if not isinstance(wm, dict) or not wm:
        raise Q35QStageBlock("weight_map is not a nonempty object")
    md = obj.get("metadata")
    if md is not None and not isinstance(md, dict):
        raise Q35QStageBlock("weight index metadata is not an object")

    shards = set()
    for name, shard in wm.items():
        if type(name) is not str or name == "":
            raise Q35QStageBlock("weight_map has an empty/non-string tensor name")
        if type(shard) is not str or shard == "":  # rejects booleans and non-strings
            raise Q35QStageBlock(f"weight_map shard path invalid for {name!r}")
        if shard.startswith("/") or ".." in shard.split("/"):
            raise Q35QStageBlock(f"weight_map shard path escapes: {shard!r}")
        if not shard.endswith(".safetensors"):
            raise Q35QStageBlock(f"weight_map shard is not a .safetensors file: {shard!r}")
        shards.add(shard)
    return {"weight_map": wm, "shard_set": shards, "tensor_count": len(wm)}


def admit_weight_index(local_bytes: bytes, expected_sha256: str) -> dict:
    """Identity-verify (LFS sha256) then strictly parse. Returns map + counts + id."""
    identity = verify_index_identity(local_bytes, expected_sha256)
    parsed = parse_weight_index_strict(local_bytes)
    parsed["index_sha256"] = identity
    return parsed
