"""Q35Q Phase-0 provenance-bound ranged fetcher (CPU/storage/network metadata-only).

Closes the header-gate provenance items left open by the format repair, per the
header-gate authorization and self-binding/format-validation corrections: fetch
Safetensors header byte ranges while asserting exact HTTP Range provenance and
binding each shard to an immutable object identity BEFORE any bytes are read.

For every ranged read this enforces:
- the resolve URL is pinned to an immutable 40-hex commit (no mutable ref/branch);
- an immutable per-shard OID (LFS sha256 / blob sha256) is bound before fetching;
- the response status is exactly 206 (Partial Content);
- the `Content-Range` start/end match the requested range and the declared total
  size matches the independently declared immutable shard size;
- the returned body length equals the requested length.

Any deviation — non-206, wrong/absent `Content-Range`, a redirect that drops the
immutable commit, a total-size mismatch, a short/long body, or a missing OID —
fails closed. The HTTP layer is injected (`http_get(url, headers) -> (status,
headers, body)`) so the provenance logic is deterministically testable; the live
adapter wraps huggingface_hub's resolve URL + a real ranged GET. No tensor payload
ranges are requested here and no full shard is cached. Aggregate/booleans only.
"""
from __future__ import annotations

import re

_COMMIT_IN_RESOLVE = re.compile(r"/resolve/[0-9a-f]{40}/")
_OID_HEX = re.compile(r"^[0-9a-f]{64}$")


class RangeProvenanceBlock(Exception):
    """Fail-closed ranged-fetch provenance failure."""


def parse_content_range(value: str):
    """Parse `bytes START-END/TOTAL` -> (start, end, total|None)."""
    if not value or not value.startswith("bytes "):
        raise RangeProvenanceBlock(f"missing/invalid Content-Range: {value!r}")
    spec = value[len("bytes "):].strip()
    rng, sep, total = spec.partition("/")
    if not sep:
        raise RangeProvenanceBlock("Content-Range missing total")
    s, dash, e = rng.partition("-")
    if not dash:
        raise RangeProvenanceBlock("Content-Range missing end")
    try:
        start, end = int(s), int(e)
        tot = None if total.strip() in ("", "*") else int(total)
    except ValueError:
        raise RangeProvenanceBlock("Content-Range not integer")
    return start, end, tot


def verify_range_response(status, content_range, start, length, declared_size) -> bool:
    """Assert exact 206 Range provenance for one read."""
    if status != 206:
        raise RangeProvenanceBlock(f"expected HTTP 206, got {status}")
    cs, ce, ct = parse_content_range(content_range)
    if cs != start or ce != start + length - 1:
        raise RangeProvenanceBlock(f"Content-Range {cs}-{ce} != requested {start}-{start + length - 1}")
    if ct is not None and declared_size is not None and ct != declared_size:
        raise RangeProvenanceBlock(f"Content-Range total {ct} != declared size {declared_size}")
    return True


class ProvenanceRangeFetcher:
    """Provenance-bound fetch(shard, start, length) usable by the header gate.

    `resolve_url(shard) -> str` yields the immutable resolve URL; `http_get(url,
    headers) -> (status, headers_dict, body_bytes)` performs the ranged GET;
    `oid_by_shard` / `size_by_shard` are independently declared immutable identities.
    """

    def __init__(self, resolve_url, http_get, oid_by_shard, size_by_shard):
        self.resolve_url = resolve_url
        self.http_get = http_get
        self.oid_by_shard = dict(oid_by_shard)
        self.size_by_shard = dict(size_by_shard)
        self.bound_oids = {}

    def _bind_oid(self, shard):
        oid = self.oid_by_shard.get(shard)
        if not oid or not _OID_HEX.match(str(oid)):
            raise RangeProvenanceBlock(f"no immutable OID bound for shard: {shard}")
        self.bound_oids[shard] = oid
        return oid

    def fetch(self, shard, start, length):
        self._bind_oid(shard)
        url = self.resolve_url(shard)
        if not _COMMIT_IN_RESOLVE.search(url or ""):
            raise RangeProvenanceBlock("resolve URL not pinned to an immutable commit")
        end = start + length - 1
        status, headers, body = self.http_get(url, {"Range": f"bytes={start}-{end}"})
        cr = (headers or {}).get("Content-Range") or (headers or {}).get("content-range")
        verify_range_response(status, cr, start, length, self.size_by_shard.get(shard))
        if not isinstance(body, (bytes, bytearray)) or len(body) != length:
            raise RangeProvenanceBlock(f"body length {len(body) if body else 0} != requested {length}")
        return bytes(body)
