#!/usr/bin/env python3
"""Q35Q Phase-0 source<->artifact reconciliation — committed reproducible CLI (CPU-only).

Order item 2 / defect 6. Wires the real independent providers through the same
`run_reconciliation` composition the tests use:

- source: meta-device construction of the admitted text-only Qwen3_5MoeForCausalLM
  class (no weights, no GPU, no memory), parameter names enumerated;
- artifact: strict weight-index admission (immutable LFS sha256 identity + frozen
  grammar) -> canonical module set;
- equality under the frozen packed<->numbered / prefix / vision-MTP-omission map.

Emits aggregate-only evidence. No weights, no GPU, no tensor payloads. This proves
module-SET correspondence only; load-manifest tensor equality (item 3) and
source/package identity (item 4) remain open, so the overall status stays
q35q_artifact_admission_blocked.

usage: q35q_reconcile.py <staging_root> <out_json>
"""
from __future__ import annotations

import json
import os
import sys
import warnings

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
warnings.filterwarnings("ignore")

from q35q_reconcile_compose import run_reconciliation  # noqa: E402
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
    from huggingface_hub import HfApi, hf_hub_download
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM

    api = HfApi()
    mi = api.model_info(REPO, revision=REV, files_metadata=True)
    if getattr(mi, "sha", None) != REV:
        raise Q35QStageBlock("model-info commit != frozen revision")
    index_sha = next((_lfs_sha256(s) for s in mi.siblings
                      if s.rfilename == "model.safetensors.index.json"), None)
    if not index_sha:
        raise Q35QStageBlock("weight-index immutable LFS identity unavailable")

    hf_hub_download(REPO, filename="config.json", revision=REV, local_dir=staging_root)
    cfg = AutoConfig.from_pretrained(staging_root, trust_remote_code=False)
    txt = getattr(cfg, "text_config", cfg)
    num_experts = getattr(txt, "num_experts", 256)
    num_layers = getattr(txt, "num_hidden_layers", 40)
    interval = getattr(txt, "full_attention_interval", 4)
    # reduced meta construction (structurally faithful: packed experts are one module)
    for attr, val in (("num_hidden_layers", 4), ("num_experts", 2)):
        if hasattr(txt, attr):
            setattr(txt, attr, val)
    with torch.device("meta"):
        model = AutoModelForCausalLM.from_config(cfg, trust_remote_code=False)
    source_param_names = [n for n, _ in model.named_parameters()]

    idx_path = hf_hub_download(REPO, filename="model.safetensors.index.json",
                               revision=REV, local_dir=staging_root)
    with open(idx_path, "rb") as f:
        index_bytes = f.read()

    try:
        result = run_reconciliation(
            source_param_names=source_param_names, index_bytes=index_bytes,
            index_expected_sha256=index_sha, num_experts=num_experts,
            num_layers=num_layers, interval=interval)
        result["source_class"] = type(model).__name__
    except Q35QStageBlock as e:
        result = {"outcome": "q35q_artifact_admission_blocked",
                  "blocked": type(e).__name__, "reason": str(e)[:160]}
    result["boundary"] = {"gpu_used": False, "weights_loaded": False,
                          "model_instantiated_on_meta_only": True, "unrelated_gpu_tenant": "preserved"}
    with open(out, "w") as f:
        json.dump(result, f, indent=2, sort_keys=True, default=str)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
