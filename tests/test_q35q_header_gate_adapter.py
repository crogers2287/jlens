"""Q35Q metadata-header gate adapter tests (CPU-only, no network).

Exercises the committed reproducible composition through synthetic descriptors + a
fake 4-tuple transport, proving fail-closed on every range-provenance defect:
wildcard total, missing/bad declared size, wrong-but-valid-shaped repo/revision/
path/OID, non-HTTPS final URL, descriptor<->index set mismatch, and a descriptor
whose declared size disagrees with the response (self-binding is impossible because
descriptors are frozen before transport).
"""
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_range_fetch import RangeProvenanceBlock
from q35q_safetensors_header import _DTYPE_SIZE
from q35q_header_gate_adapter import (
    ShardDescriptor,
    freeze_descriptors,
    run_header_gate,
)

REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"
REPO = "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4"
OID = "a" * 64


def _elem(shape):
    c = 1
    for d in shape:
        c *= d
    return c


def build_shard(tensors):
    header, cursor = {}, 0
    for name, dtype, shape in tensors:
        nb = _elem(shape) * _DTYPE_SIZE[dtype]
        header[name] = {"dtype": dtype, "shape": shape, "data_offsets": [cursor, cursor + nb]}
        cursor += nb
    body = json.dumps(header).encode()
    return struct.pack("<Q", len(body)) + body, 8 + len(body) + cursor


def _url(repo, path, rev):
    return f"https://huggingface.co/{repo}/resolve/{rev}/{path}"


def setup(*, size_override=None):
    p0, s0 = build_shard([("model.embed_tokens.weight", "F16", [10, 4])])
    p1, s1 = build_shard([("lm_head.weight", "F16", [10, 4])])
    shard_bytes = {"shard0.safetensors": p0, "shard1.safetensors": p1}
    real_sizes = {"shard0.safetensors": s0, "shard1.safetensors": s1}

    def http_get(url, headers):
        path = url.rsplit("/", 1)[-1]
        rng = headers["Range"][len("bytes="):]
        a, b = (int(x) for x in rng.split("-"))
        body = shard_bytes[path][a:b + 1]
        cr = f"bytes {a}-{b}/{real_sizes[path]}"
        final = f"https://cdn-lfs.huggingface.co/repos/x/{path}"
        return 206, {"Content-Range": cr}, body, final, [url]

    wmap = {"model.embed_tokens.weight": "shard0.safetensors", "lm_head.weight": "shard1.safetensors"}
    records = [
        {"repo_id": REPO, "revision": REV, "path": "shard0.safetensors", "lfs_oid": OID,
         "declared_size": size_override or s0},
        {"repo_id": REPO, "revision": REV, "path": "shard1.safetensors", "lfs_oid": "b" * 64,
         "declared_size": s1},
    ]
    return records, wmap, http_get


# ---------- happy path ----------

def test_gate_passes():
    records, wmap, http_get = setup()
    out = run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url, http_get=http_get)
    assert out["outcome"] == "q35q_phase0_metadata_header_gate_passed"
    assert out["reconciled"] and out["shard_count"] == 2 and out["tensor_count"] == 2


# ---------- freeze_descriptors validation ----------

@pytest.mark.parametrize("mut", [
    {"revision": "main"}, {"revision": "3af5ca29"}, {"lfs_oid": "xyz"},
    {"lfs_oid": "a" * 63}, {"declared_size": 0}, {"declared_size": -1},
    {"declared_size": True}, {"declared_size": 1.5}, {"path": "../escape"},
    {"path": "/abs/path"}, {"repo_id": ""},
])
def test_freeze_rejects_bad_field(mut):
    rec = {"repo_id": REPO, "revision": REV, "path": "s.safetensors", "lfs_oid": OID, "declared_size": 100}
    rec.update(mut)
    with pytest.raises(RangeProvenanceBlock):
        freeze_descriptors([rec])


def test_freeze_duplicate_path_fails():
    rec = {"repo_id": REPO, "revision": REV, "path": "s.safetensors", "lfs_oid": OID, "declared_size": 100}
    with pytest.raises(RangeProvenanceBlock, match="duplicate descriptor path"):
        freeze_descriptors([rec, dict(rec)])


def test_freeze_empty_fails():
    with pytest.raises(RangeProvenanceBlock, match="no shard descriptors"):
        freeze_descriptors([])


# ---------- descriptor<->index set binding ----------

def test_descriptor_missing_shard_fails():
    records, wmap, http_get = setup()
    records = records[:1]  # drop shard1 descriptor
    with pytest.raises(RangeProvenanceBlock, match="descriptor set != indexed shard set"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url, http_get=http_get)


# ---------- wrong-but-valid-shaped identities (URL binding) ----------

@pytest.mark.parametrize("builder", [
    lambda repo, path, rev: f"https://huggingface.co/Other/Repo/resolve/{rev}/{path}",       # wrong repo
    lambda repo, path, rev: f"https://huggingface.co/{repo}/resolve/{'f'*40}/{path}",         # wrong revision
    lambda repo, path, rev: f"https://huggingface.co/{repo}/resolve/{rev}/other.safetensors",  # wrong path
])
def test_url_identity_mismatch_fails(builder):
    records, wmap, http_get = setup()
    with pytest.raises(RangeProvenanceBlock, match="exact frozen descriptor"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=builder, http_get=http_get)


# ---------- transport provenance ----------

def test_non_https_final_url_fails():
    records, wmap, _ = setup()

    def http_get(url, headers):
        rng = headers["Range"][len("bytes="):]
        a, b = (int(x) for x in rng.split("-"))
        return 206, {"Content-Range": f"bytes {a}-{b}/999999"}, b"x" * (b - a + 1), "http://downgrade/x", [url]

    with pytest.raises(RangeProvenanceBlock, match="not HTTPS"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url, http_get=http_get)


def test_intermediate_downgrade_hop_fails():
    records, wmap, _ = setup()

    def http_get(url, headers):
        rng = headers["Range"][len("bytes="):]
        a, b = (int(x) for x in rng.split("-"))
        # a mid-chain HTTP hop must fail even if the final URL is HTTPS
        chain = [url, "http://mid-hop.example/x"]
        return (206, {"Content-Range": f"bytes {a}-{b}/999999"}, b"x" * (b - a + 1),
                "https://cdn-lfs.huggingface.co/x", chain)

    with pytest.raises(RangeProvenanceBlock, match="not HTTPS"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url, http_get=http_get)


def test_unpermitted_final_host_fails():
    records, wmap, _ = setup()

    def http_get(url, headers):
        rng = headers["Range"][len("bytes="):]
        a, b = (int(x) for x in rng.split("-"))
        return (206, {"Content-Range": f"bytes {a}-{b}/999999"}, b"x" * (b - a + 1),
                "https://evil.example.com/x", [url])

    with pytest.raises(RangeProvenanceBlock, match="host not permitted"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url, http_get=http_get)


def test_url_with_query_fails():
    records, wmap, http_get = setup()
    builder = lambda repo, path, rev: f"https://huggingface.co/{repo}/resolve/{rev}/{path}?x=1"
    with pytest.raises(RangeProvenanceBlock, match="credentials/query/fragment"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=builder, http_get=http_get)


def test_unpermitted_request_host_fails():
    records, wmap, http_get = setup()
    builder = lambda repo, path, rev: f"https://evil.example.com/{repo}/resolve/{rev}/{path}"
    with pytest.raises(RangeProvenanceBlock, match="request host not permitted"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=builder, http_get=http_get)


def test_five_tuple_required():
    records, wmap, _ = setup()
    with pytest.raises(RangeProvenanceBlock, match="final_url, redirect_chain"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url,
                        http_get=lambda u, h: (206, {}, b""))


def test_wildcard_total_fails():
    records, wmap, _ = setup()

    def http_get(url, headers):
        rng = headers["Range"][len("bytes="):]
        a, b = (int(x) for x in rng.split("-"))
        return 206, {"Content-Range": f"bytes {a}-{b}/*"}, b"x" * (b - a + 1), url, [url]

    with pytest.raises(RangeProvenanceBlock, match="wildcard/absent"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url, http_get=http_get)


# ---------- self-binding is impossible: declared size is the frozen descriptor,
# never the observed response ----------

def test_declared_size_disagreeing_with_response_fails():
    # descriptor size deliberately wrong; the response total is the real size.
    # The gate uses the FROZEN descriptor size, so it must fail -> proves the
    # expected total is not taken from the observed response.
    records, wmap, http_get = setup(size_override=999999)
    with pytest.raises(RangeProvenanceBlock, match="!= declared size"):
        run_header_gate(descriptor_records=records, weight_map=wmap, url_builder=_url, http_get=http_get)
