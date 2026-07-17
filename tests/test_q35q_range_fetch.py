"""Q35Q provenance-bound ranged-fetch tests (CPU-only, no network).

Drives the Range-provenance logic through a fake http_get, proving fail-closed on
non-206 status, wrong/absent Content-Range, total-size mismatch, an unpinned
(mutable) resolve URL, a missing immutable OID, and a short body.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_range_fetch import (
    ProvenanceRangeFetcher,
    RangeProvenanceBlock,
    parse_content_range,
    verify_range_response,
)

REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"
OID = "a" * 64
PINNED_URL = f"https://huggingface.co/Qwen/Repo/resolve/{REV}/model-00001.safetensors"


# ---------- pure verify ----------

def test_parse_content_range():
    assert parse_content_range("bytes 0-7/12345") == (0, 7, 12345)
    assert parse_content_range("bytes 8-107/*") == (8, 107, None)


@pytest.mark.parametrize("bad", ["", "0-7/12345", "bytes 0-7", "bytes x-7/9", "bytes 0/9"])
def test_parse_content_range_bad(bad):
    with pytest.raises(RangeProvenanceBlock):
        parse_content_range(bad)


def test_verify_ok():
    assert verify_range_response(206, "bytes 0-7/100", 0, 8, 100) is True


def test_verify_non_206():
    with pytest.raises(RangeProvenanceBlock, match="expected HTTP 206"):
        verify_range_response(200, "bytes 0-7/100", 0, 8, 100)


def test_verify_range_mismatch():
    with pytest.raises(RangeProvenanceBlock, match="!= requested"):
        verify_range_response(206, "bytes 0-15/100", 0, 8, 100)


def test_verify_total_size_mismatch():
    with pytest.raises(RangeProvenanceBlock, match="!= declared size"):
        verify_range_response(206, "bytes 0-7/999", 0, 8, 100)


def test_verify_wildcard_total_fails():
    with pytest.raises(RangeProvenanceBlock, match="wildcard/absent"):
        verify_range_response(206, "bytes 0-7/*", 0, 8, 100)


@pytest.mark.parametrize("size", [None, True, 0, -5, 1.5])
def test_verify_bad_declared_size_fails(size):
    with pytest.raises(RangeProvenanceBlock, match="positive integer"):
        verify_range_response(206, "bytes 0-7/100", 0, 8, size)


# ---------- fetcher composition ----------

def make_fetcher(*, status=206, content_range="bytes 0-7/100", body=b"01234567",
                 url=PINNED_URL, oid=OID, size=100):
    def http_get(u, headers):
        return status, {"Content-Range": content_range}, body
    return ProvenanceRangeFetcher(lambda s: url, http_get, {"shard": oid}, {"shard": size})


def test_fetch_ok():
    f = make_fetcher()
    assert f.fetch("shard", 0, 8) == b"01234567"
    assert f.bound_oids["shard"] == OID


def test_fetch_non_206_blocks():
    with pytest.raises(RangeProvenanceBlock, match="expected HTTP 206"):
        make_fetcher(status=200).fetch("shard", 0, 8)


def test_fetch_absent_content_range_blocks():
    def http_get(u, h):
        return 206, {}, b"01234567"
    f = ProvenanceRangeFetcher(lambda s: PINNED_URL, http_get, {"shard": OID}, {"shard": 100})
    with pytest.raises(RangeProvenanceBlock, match="missing/invalid Content-Range"):
        f.fetch("shard", 0, 8)


def test_fetch_unpinned_url_blocks():
    with pytest.raises(RangeProvenanceBlock, match="not pinned to an immutable commit"):
        make_fetcher(url="https://huggingface.co/Qwen/Repo/resolve/main/model-00001.safetensors").fetch("shard", 0, 8)


def test_fetch_missing_oid_blocks():
    with pytest.raises(RangeProvenanceBlock, match="no immutable OID bound"):
        make_fetcher(oid=None).fetch("shard", 0, 8)


def test_fetch_bad_oid_shape_blocks():
    with pytest.raises(RangeProvenanceBlock, match="no immutable OID bound"):
        make_fetcher(oid="not-a-sha").fetch("shard", 0, 8)


def test_fetch_short_body_blocks():
    with pytest.raises(RangeProvenanceBlock, match="body length"):
        make_fetcher(body=b"0123", content_range="bytes 0-7/100").fetch("shard", 0, 8)


def test_fetch_total_size_mismatch_blocks():
    with pytest.raises(RangeProvenanceBlock, match="!= declared size"):
        make_fetcher(content_range="bytes 0-7/999", size=100).fetch("shard", 0, 8)
