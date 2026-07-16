#!/usr/bin/env python3
"""Q35Q Phase-0 corrected admission staging (CPU/storage/network only).

Repaired per docs/STEER_ADDENDUM_2026-07-16_Q35Q_PHASE0_ADMISSION_CORRECTION_AND_TP_RUNTIME.md
and steer.md. Pins BOTH immutable repositories, stages only small admission files
(no weights, no GPU, no model instantiation), builds a deterministic public-file
manifest (cache/metadata excluded), runs per-field text-only architecture + GPTQ
admission, binds a genuine deterministic tokenizer roundtrip (+ normalization,
special tokens, chat-template digest), and records honest storage projections.

Overall admission is the conjunction of every required check. Raw fixture text,
rendered chat text, and token IDs stay private (digests only).

usage: q35q_stage_admission.py <staging_root> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from q35q_stage import (  # noqa: E402
    Q35QStageBlock,
    admitted_public_manifest,
    tokenizer_roundtrip_verdict,
    validate_gptq_quant,
    validate_text_architecture,
)

REPOS = {
    "gptq": ("Qwen/Qwen3.5-35B-A3B-GPTQ-Int4", "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"),
    "base": ("Qwen/Qwen3.5-35B-A3B-Base", "0f0813072d2358973511097385626f21fcb6d422"),
}
_WEIGHT_EXT = (".safetensors", ".bin", ".pt", ".pth", ".gguf")
_SMALL_OK = ("config.json", "configuration.json", "generation_config.json",
             "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt",
             "chat_template.jinja", "chat_template.json", "LICENSE", "README.md",
             "model.safetensors.index.json", "preprocessor_config.json", "special_tokens_map.json")
_FREE_GIB = 46.0  # per-3090 aggregate ceiling reference; storage headroom check is separate


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def stage_repo(key, staging_root):
    from huggingface_hub import HfApi, snapshot_download
    import re
    repo, sha = REPOS[key]
    assert re.match(r"^[0-9a-f]{40}$", sha), "revision must be immutable 40-hex"
    api = HfApi()
    mi = api.model_info(repo, revision=sha, files_metadata=True)
    siblings = {s.rfilename: (s.size or 0) for s in mi.siblings}
    small_names = [n for n in siblings if n.endswith(tuple(_SMALL_OK))
                   or os.path.basename(n) in _SMALL_OK]
    weight_bytes = sum(sz for n, sz in siblings.items() if n.endswith(_WEIGHT_EXT))
    local = snapshot_download(repo, revision=sha, local_dir=os.path.join(staging_root, key),
                              allow_patterns=list(small_names))
    # present = everything walked; admitted = the small sibling names hashed from staging
    present = {}
    for root, _, files in os.walk(local):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), local)
            present[rel] = _sha(os.path.join(root, fn))
    admitted = {n: present[n] for n in small_names if n in present}
    manifest = admitted_public_manifest(admitted, present)
    return {"repo_id": repo, "immutable_revision": sha,
            "manifest": manifest,
            "weight_file_count": sum(1 for n in siblings if n.endswith(_WEIGHT_EXT)),
            "projected_weight_bytes": int(weight_bytes),
            "local": local}


def architecture_record(gptq_local):
    cfg = json.load(open(os.path.join(gptq_local, "config.json")))
    arch = validate_text_architecture(cfg)
    gptq = validate_gptq_quant(cfg.get("quantization_config") or {})
    return arch, gptq


def tokenizer_record(gptq_local):
    from transformers import AutoTokenizer
    tk = AutoTokenizer.from_pretrained(gptq_local, trust_remote_code=False)
    fixture = ("The quick brown fox jumps over the lazy dog. "
               "Modular arithmetic: (7 * 13) mod 5 = 1. Sort: [3,1,2] -> [1,2,3].")
    ids_a = tk.encode(fixture, add_special_tokens=False)
    ids_b = tk.encode(fixture, add_special_tokens=False)
    decoded = tk.decode(ids_a, skip_special_tokens=True, clean_up_tokenization_spaces=False)
    reenc = tk.encode(decoded, add_special_tokens=False)
    verdict = tokenizer_roundtrip_verdict(ids_a, ids_b, reenc, add_special_tokens=False)
    # chat-template rendering digest (neutral message); raw rendered text private
    chat_digest = None
    try:
        rendered = tk.apply_chat_template(
            [{"role": "user", "content": "2+2?"}], tokenize=False, add_generation_prompt=True)
        chat_digest = hashlib.sha256(rendered.encode()).hexdigest()
    except Exception:
        chat_digest = None
    return {
        **verdict,
        "tokenizer_class": type(tk).__name__,
        "trust_remote_code": False,
        "encoded_length": len(ids_a),
        "id_sequence_sha256": hashlib.sha256(",".join(map(str, ids_a)).encode()).hexdigest(),
        "reencoded_id_sequence_sha256": hashlib.sha256(",".join(map(str, reenc)).encode()).hexdigest(),
        "bos_token_id": tk.bos_token_id, "eos_token_id": tk.eos_token_id,
        "pad_token_id": tk.pad_token_id,
        "reported_vocab_size": getattr(tk, "vocab_size", None),
        "chat_template_render_sha256": chat_digest,
    }


def main():
    staging_root, out = sys.argv[1:3]
    staged = {k: stage_repo(k, staging_root) for k in REPOS}
    arch, gptq = architecture_record(staged["gptq"]["local"])
    tok = tokenizer_record(staged["gptq"]["local"])

    overall = bool(arch["all_required_pass"] and gptq["all_required_pass"]
                   and tok["roundtrip_pass"]
                   and all(staged[k]["manifest"]["file_count"] > 0 for k in staged))
    record = {
        "outcome": "q35q_phase0_admission_corrected",
        "phase0_admission_prerequisites_pass": overall,
        "both_repos_pinned": {k: {"repo_id": v["repo_id"],
                                  "immutable_revision": v["immutable_revision"],
                                  "small_manifest_sha256": v["manifest"]["manifest_sha256"],
                                  "small_file_count": v["manifest"]["file_count"],
                                  "weight_file_count": v["weight_file_count"],
                                  "projected_weight_bytes": v["projected_weight_bytes"]}
                              for k, v in staged.items()},
        "architecture_admission": arch,
        "gptq_admission": gptq,
        "tokenizer_admission": tok,
        "storage_projection": {
            "gptq_weight_gib": round(staged["gptq"]["projected_weight_bytes"] / 2**30, 2),
            "base_weight_gib": round(staged["base"]["projected_weight_bytes"] / 2**30, 2),
            "per_gpu_load_ceiling_gib": 23.0, "aggregate_ceiling_gib": 46.0,
            "isolated_cache": True,
        },
        "gpu_used": False, "weights_loaded": False, "model_instantiated": False,
        "artifact_admission_status": "q35q_artifact_admission_blocked",
    }
    with open(out, "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
    print(json.dumps({"overall_prereq_pass": overall,
                      "arch_all": arch["all_required_pass"],
                      "gptq_all": gptq["all_required_pass"],
                      "tokenizer_roundtrip": tok["roundtrip_pass"],
                      "gptq_weight_gib": record["storage_projection"]["gptq_weight_gib"],
                      "base_weight_gib": record["storage_projection"]["base_weight_gib"]}, indent=2))


if __name__ == "__main__":
    main()
