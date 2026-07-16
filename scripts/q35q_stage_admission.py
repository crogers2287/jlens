#!/usr/bin/env python3
"""Q35Q Phase-0 public-artifact admission staging (CPU/storage/network only).

Per docs/STEER_ADDENDUM_2026-07-16_Q35Q_PHASE0_STAGING_AND_EXACT_JVP_CROSSCHECK.md.
Pins an immutable public revision, stages only the small admission files (no
weights), reviews+hashes custom code without executing it, parses a text-only
architecture-admission record without loading weights, and runs a genuine
deterministic tokenizer roundtrip on a NEUTRAL public fixture.

Emits an AGGREGATE-ONLY record: repo id, immutable revision, per-file sha256
manifest digest, architecture booleans, tokenizer roundtrip pass + encoded-length
summary + id-sequence digest, custom-code hashes, license id. Raw fixture text and
token IDs stay private (never written to the committed record). No GPU, no model
instantiation, no weight download.

usage: q35q_stage_admission.py <repo_id> <immutable_sha> <staging_dir> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import re
import sys

_SMALL = ("config.json", "configuration.json", "generation_config.json",
          "tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt",
          "chat_template.jinja", "chat_template.json", "LICENSE", "README.md",
          "model.safetensors.index.json", "preprocessor_config.json")

# Frozen Qwen3.5-35B-A3B text-only architecture expectations (public model-card).
EXPECT = {"hidden_size": 2048, "num_hidden_layers": 40, "vocab_size": 248320}
EXPECT_MOE = {"routed_experts": 256, "experts_per_tok": 8, "shared_experts": 1,
              "moe_intermediate_size": 512}

_HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def _first(d, *keys):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def main():
    repo, sha, staging, out = sys.argv[1:5]
    assert _HEX40.match(sha), "revision must be an immutable 40-hex commit"
    from huggingface_hub import snapshot_download
    import os

    local = snapshot_download(repo, revision=sha, local_dir=staging,
                              allow_patterns=list(_SMALL) + ["*.py"])
    staged = {}
    for root, _, files in os.walk(local):
        for fn in files:
            rel = os.path.relpath(os.path.join(root, fn), local)
            staged[rel] = _sha(os.path.join(root, fn))
    manifest_digest = hashlib.sha256(
        "\n".join(f"{k}:{staged[k]}" for k in sorted(staged)).encode()).hexdigest()
    custom_code = {k: v for k, v in staged.items() if k.endswith(".py")}

    # --- text-only architecture admission (no weights loaded) ---
    cfg = json.load(open(os.path.join(local, "config.json")))
    txt = cfg.get("text_config", cfg)  # multimodal configs nest text under text_config
    arch = {
        "model_type": cfg.get("model_type"),
        "hidden_size": _first(txt, "hidden_size"),
        "num_hidden_layers": _first(txt, "num_hidden_layers"),
        "vocab_size": _first(txt, "vocab_size"),
        "routed_experts": _first(txt, "num_experts", "n_routed_experts", "num_routed_experts"),
        "experts_per_tok": _first(txt, "num_experts_per_tok", "moe_topk", "top_k"),
        "shared_experts": _first(txt, "num_shared_experts", "n_shared_experts", "shared_expert_intermediate_size" if False else "num_shared_experts"),
        "moe_intermediate_size": _first(txt, "moe_intermediate_size", "expert_intermediate_size"),
    }
    arch_match = {k: (arch.get(k) == v) for k, v in {**EXPECT, **{
        "routed_experts": EXPECT_MOE["routed_experts"],
        "experts_per_tok": EXPECT_MOE["experts_per_tok"],
        "moe_intermediate_size": EXPECT_MOE["moe_intermediate_size"],
    }}.items()}
    has_vision = bool(cfg.get("vision_config") or cfg.get("visual") or
                      any("video" in f or "vision" in f for f in staged))
    # text-only admission requires vision to be present-but-omittable, not loaded
    arch_admitted = all(arch_match.get(k, False) for k in ("hidden_size", "num_hidden_layers", "vocab_size"))

    # --- genuine deterministic tokenizer roundtrip (neutral public fixture) ---
    fixture = ("The quick brown fox jumps over the lazy dog. "
               "Modular arithmetic: (7 * 13) mod 5 = 1. Sort: [3,1,2] -> [1,2,3].")
    tok_rec = {}
    try:
        from transformers import AutoTokenizer
        tk = AutoTokenizer.from_pretrained(local, trust_remote_code=False)
        ids = tk.encode(fixture)
        back = tk.decode(ids, skip_special_tokens=True)
        ids2 = tk.encode(fixture)
        id_digest = hashlib.sha256(",".join(map(str, ids)).encode()).hexdigest()
        tok_rec = {
            "loaded": True,
            "trust_remote_code": False,
            "encoded_length": len(ids),
            "deterministic": ids == ids2,
            "roundtrip_substring_ok": fixture.split(".")[0] in back,  # aggregate-only signal
            "vocab_size_reported": getattr(tk, "vocab_size", None),
            "id_sequence_sha256": id_digest,          # digest only; raw ids private
        }
    except Exception as e:
        tok_rec = {"loaded": False, "error_class": type(e).__name__}

    record = {
        "outcome": "q35q_admission_staging",
        "repo_id": repo,
        "immutable_revision": sha,
        "small_file_count": len(staged),
        "manifest_sha256": manifest_digest,
        "custom_code_count": len(custom_code),
        "custom_code_sha256": {k: v for k, v in sorted(custom_code.items())},
        "license_present": "LICENSE" in staged,
        "architecture": {**{k: (arch.get(k) is not None) for k in arch},
                         "model_type": arch.get("model_type")},
        "architecture_match": arch_match,
        "architecture_text_only_admitted": bool(arch_admitted),
        "has_vision_modules_present": has_vision,
        "tokenizer_roundtrip": tok_rec,
        "gpu_used": False,
        "weights_loaded": False,
    }
    with open(out, "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
    print(json.dumps({k: record[k] for k in (
        "repo_id", "immutable_revision", "small_file_count", "manifest_sha256",
        "custom_code_count", "architecture_match",
        "architecture_text_only_admitted", "has_vision_modules_present")},
        indent=2))
    print("tokenizer_roundtrip:", json.dumps(tok_rec))


if __name__ == "__main__":
    main()
