#!/usr/bin/env python3
"""Q35Q Phase-0 metadata-header gate — committed reproducible live CLI (CPU-only).

Wires immutable Hub metadata (repo/revision/path/lfs_oid/declared_size) + the real
ranged HTTPS transport + the format-hardened parser + index reconciliation through
the SAME `run_header_gate` composition the tests use. Reproducible from the repo:

    q35q_header_gate.py <staging_root> <out_json>

Descriptors are resolved from immutable public repository metadata (files_metadata)
independently of the response, frozen before any transport (self-binding impossible),
and equality-bound to each request URL. Only Safetensors header byte ranges are
requested; no tensor payload ranges, no full-shard cache, no weights, no GPU.
Emits aggregate-only evidence (counts, booleans, public architecture shapes).
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from q35q_header_gate_adapter import run_header_gate  # noqa: E402
from q35q_index_admission import admit_weight_index  # noqa: E402
from q35q_range_fetch import RangeProvenanceBlock  # noqa: E402
from q35q_safetensors_header import HeaderGateBlock  # noqa: E402
from q35q_stage import Q35QStageBlock  # noqa: E402

REPO = "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4"
REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"


def _lfs_sha256(sibling):
    lfs = getattr(sibling, "lfs", None)
    if isinstance(lfs, dict):
        return lfs.get("sha256")
    return getattr(lfs, "sha256", None) if lfs else None


def main():
    staging_root, out = sys.argv[1:3]
    os.makedirs(staging_root, exist_ok=True)
    from huggingface_hub import HfApi, hf_hub_download, hf_hub_url
    import requests

    api = HfApi()
    mi = api.model_info(REPO, revision=REV, files_metadata=True)
    # defect 3: bind the metadata response commit to the frozen revision by equality
    if getattr(mi, "sha", None) != REV:
        raise RangeProvenanceBlock(f"model-info commit {getattr(mi, 'sha', None)!r} != frozen revision")
    records = []
    for s in mi.siblings:
        if s.rfilename.endswith(".safetensors"):
            records.append({"repo_id": REPO, "revision": REV, "path": s.rfilename,
                            "lfs_oid": _lfs_sha256(s), "declared_size": s.size})
    # strict weight-index admission: freeze the index's immutable LFS sha256 from
    # metadata, verify the downloaded bytes against it, then parse under the frozen
    # grammar (no fail-open json.load).
    index_lfs_sha = None
    for s in mi.siblings:
        if s.rfilename == "model.safetensors.index.json":
            index_lfs_sha = _lfs_sha256(s)
    if not index_lfs_sha:
        raise Q35QStageBlock("weight-index immutable LFS identity unavailable")
    idx_path = hf_hub_download(REPO, filename="model.safetensors.index.json",
                               revision=REV, local_dir=staging_root)
    with open(idx_path, "rb") as f:
        weight_map = admit_weight_index(f.read(), index_lfs_sha)["weight_map"]

    session = requests.Session()

    def http_get(url, headers):
        r = session.get(url, headers=headers, allow_redirects=True, timeout=60)
        chain = [h.url for h in r.history]  # each redirect hop's URL
        return r.status_code, dict(r.headers), r.content, r.url, chain

    try:
        result = run_header_gate(descriptor_records=records, weight_map=weight_map,
                                 url_builder=lambda repo, path, rev: hf_hub_url(repo, path, revision=rev),
                                 http_get=http_get)
        shapes = result.pop("shapes", {})
        result["independent_shapes"] = {
            "embed_tokens": next((v for k, v in shapes.items() if "embed_tokens" in k), None),
            "lm_head": next((v for k, v in shapes.items() if "lm_head" in k), None),
        }
        result["artifact_admission_status"] = "q35q_artifact_admission_blocked"
        result["boundary"] = {"gpu_used": False, "weights_loaded": False,
                              "tensor_payload_fetched": False, "unrelated_gpu_tenant": "preserved"}
    except (RangeProvenanceBlock, HeaderGateBlock, Q35QStageBlock) as e:
        result = {"outcome": "q35q_artifact_admission_blocked",
                  "blocked": type(e).__name__, "reason": str(e)[:160]}

    with open(out, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)
    print(json.dumps({k: v for k, v in result.items() if k != "independent_shapes"}
                     | {"independent_shapes": result.get("independent_shapes")}, indent=2, default=str))


if __name__ == "__main__":
    main()
