"""Q35Q Phase-0 metadata-header gate — committed reproducible live adapter (CPU-only).

Repairs the range-provenance sub-gate per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_RANGE_PROVENANCE_AND_REPRODUCIBLE_LIVE_ADAPTER_CORRECTION.md.

The prior work proved fail-closed range helpers but had no committed production path,
so the live rerun could not be reproduced or adversarially exercised. This module is
that committed composition, used identically in tests and live work:

- freeze one exact `ShardDescriptor{repo_id, revision, path, lfs_oid, declared_size}`
  per shard from immutable public repository metadata, BEFORE any transport (so an
  expected value can never be derived from an observed HTTP response — self-binding
  is structurally impossible);
- construct each request URL from the frozen descriptor and require exact repo /
  revision / path binding before transport;
- require exact 206 + exact requested range + a present positive-integer total equal
  to the frozen declared size (wildcard `*` fails);
- observe the transport's final URL and reject HTTPS downgrade or a resolver path that
  no longer carries the immutable commit;
- invoke the format-hardened Safetensors header parser and index<->header reconciliation.

Narrow permitted claim: immutable Hub metadata + exact descriptor binding + exact
ranged-response provenance + valid Safetensors header format + index/header
reconciliation. Ranged header bytes do NOT cryptographically verify the shard payload.
No payload ranges, no full-shard cache, no weights, no GPU. Aggregate/booleans only.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlsplit

from q35q_range_fetch import RangeProvenanceBlock, verify_range_response
from q35q_safetensors_header import reconcile_index_with_headers

_HEX40 = re.compile(r"^[0-9a-f]{40}$")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
# frozen permitted host class for Hub resolve + LFS/CDN redirects
_PERMITTED_HOSTS = ("huggingface.co", "cdn-lfs.huggingface.co", "cdn-lfs.hf.co",
                    "cdn-lfs-us-1.hf.co", "cdn-lfs-eu-1.hf.co", "hf.co")


def _host_permitted(host: str) -> bool:
    host = (host or "").lower()
    return any(host == h or host.endswith("." + h) for h in _PERMITTED_HOSTS)


def _require_exact_resolve_url(url: str, repo_id: str, revision: str, path: str):
    """Parse the request URL and require exact scheme/host-class/repo/revision/path
    components — not substring containment (defect 2)."""
    parts = urlsplit(url or "")
    if parts.scheme != "https":
        raise RangeProvenanceBlock(f"request URL is not HTTPS: {parts.scheme!r}")
    if not _host_permitted(parts.hostname or ""):
        raise RangeProvenanceBlock(f"request host not permitted: {parts.hostname!r}")
    if parts.username or parts.password or parts.query or parts.fragment:
        raise RangeProvenanceBlock("request URL carries credentials/query/fragment")
    # exact path: /<repo_id>/resolve/<revision>/<path>
    expected = f"/{repo_id}/resolve/{revision}/{path}"
    if parts.path != expected:
        raise RangeProvenanceBlock("request URL path is not the exact frozen descriptor")


@dataclass(frozen=True)
class ShardDescriptor:
    repo_id: str
    revision: str
    path: str
    lfs_oid: str
    declared_size: int


def freeze_descriptors(records) -> dict:
    """Validate + freeze immutable per-shard descriptors from repository metadata.
    `records`: iterable of dicts with repo_id/revision/path/lfs_oid/declared_size."""
    out = {}
    for r in records:
        repo, rev, path = r.get("repo_id"), r.get("revision"), r.get("path")
        oid, size = r.get("lfs_oid"), r.get("declared_size")
        if not isinstance(repo, str) or not repo:
            raise RangeProvenanceBlock("descriptor repo_id missing")
        if not isinstance(rev, str) or not _HEX40.match(rev):
            raise RangeProvenanceBlock("descriptor revision not an immutable 40-hex commit")
        if not isinstance(path, str) or not path or path.startswith("/") or ".." in path.split("/"):
            raise RangeProvenanceBlock(f"descriptor path invalid: {path!r}")
        if not isinstance(oid, str) or not _HEX64.match(oid):
            raise RangeProvenanceBlock("descriptor lfs_oid not a 64-hex immutable identity")
        if type(size) is not int or size <= 0:
            raise RangeProvenanceBlock(f"descriptor declared_size not a positive integer: {size!r}")
        if path in out:
            raise RangeProvenanceBlock(f"duplicate descriptor path: {path}")
        out[path] = ShardDescriptor(repo, rev, path, oid, size)
    if not out:
        raise RangeProvenanceBlock("no shard descriptors frozen")
    return out


class DescriptorBoundFetcher:
    """fetch(path, start, length) bound to a frozen descriptor. `url_builder(repo,
    path, revision) -> url`; `http_get(url, headers) -> (status, headers, body,
    final_url)`."""

    def __init__(self, descriptors, url_builder, http_get):
        self.descriptors = descriptors
        self.url_builder = url_builder
        self.http_get = http_get

    def fetch(self, path, start, length):
        desc = self.descriptors.get(path)
        if desc is None:
            raise RangeProvenanceBlock(f"no frozen descriptor for shard: {path}")
        url = self.url_builder(desc.repo_id, desc.path, desc.revision)
        _require_exact_resolve_url(url, desc.repo_id, desc.revision, desc.path)
        end = start + length - 1
        result = self.http_get(url, {"Range": f"bytes={start}-{end}"})
        if not isinstance(result, tuple) or len(result) != 5:
            raise RangeProvenanceBlock(
                "transport must expose (status, headers, body, final_url, redirect_chain)")
        status, headers, body, final_url, redirect_chain = result
        # every hop (including the final URL) must be HTTPS on a permitted host
        for hop_url in list(redirect_chain or []) + [final_url]:
            hp = urlsplit(hop_url or "")
            if hp.scheme != "https":
                raise RangeProvenanceBlock(f"redirect/final hop not HTTPS: {hop_url!r}")
            if not _host_permitted(hp.hostname or ""):
                raise RangeProvenanceBlock(f"redirect/final host not permitted: {hp.hostname!r}")
        cr = (headers or {}).get("Content-Range") or (headers or {}).get("content-range")
        verify_range_response(status, cr, start, length, desc.declared_size)
        if not isinstance(body, (bytes, bytearray)) or len(body) != length:
            raise RangeProvenanceBlock(f"body length {len(body) if body else 0} != requested {length}")
        return bytes(body)


def run_header_gate(*, descriptor_records, weight_map, url_builder, http_get) -> dict:
    """Reproducible metadata-header gate: freeze descriptors (pre-transport),
    reconcile the pinned weight index against provenance-bound shard headers."""
    if not weight_map:
        raise RangeProvenanceBlock("empty weight index")
    descriptors = freeze_descriptors(descriptor_records)  # frozen BEFORE any transport
    indexed_shards = set(weight_map.values())
    if indexed_shards != set(descriptors):
        missing = sorted(indexed_shards - set(descriptors))
        extra = sorted(set(descriptors) - indexed_shards)
        raise RangeProvenanceBlock(
            f"descriptor set != indexed shard set (missing {len(missing)}, extra {len(extra)})")
    fetcher = DescriptorBoundFetcher(descriptors, url_builder, http_get)
    sizes = {p: d.declared_size for p, d in descriptors.items()}
    recon = reconcile_index_with_headers(weight_map, sizes, fetcher.fetch)
    return {
        "outcome": "q35q_phase0_metadata_header_gate_passed",
        "descriptor_count": len(descriptors),
        "reconciled": recon["reconciled"],
        "shard_count": recon["shard_count"],
        "tensor_count": recon["tensor_count"],
        "shapes": recon["shapes"],
    }
