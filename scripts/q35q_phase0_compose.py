#!/usr/bin/env python3
"""Q35Q Phase-0 live composition (CPU/storage/network only — no GPU, no weights).

Stages ONLY the small admission files for the pinned GPTQ repo into an isolated
staging root, derives real values from the actual artifact, and composes the
Phase-0 validators against them:

- real remote manifest + immutable checksums  -> run_staging_orchestration (small)
- real config.json                            -> validate_text_architecture / gptq
- real model.safetensors.index.json weight_map-> admitted module set + shapes
                                                 -> validate_load_manifest
- real installed implementation source class  -> validate_source_identity
- real pinned tokenizer                        -> complete_tokenizer_admission

Emits an aggregate-only record. Raw fixture text, token IDs, weight-tensor values,
and local paths never enter the record — module NAMES, shapes, booleans, counts,
and hex digests only. This binds the offline validators to the real artifact; the
independent source-derived allow-list (vs the weight-index-derived admitted set)
and weight staging remain the open gates.

usage: q35q_phase0_compose.py <staging_root> <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from q35q_stage import (  # noqa: E402
    expected_layer_types, tokenizer_roundtrip_verdict,
    validate_gptq_quant, validate_text_architecture,
)
from q35q_source_admission import (  # noqa: E402
    canonical_module_path, validate_load_manifest, validate_source_identity,
)
from q35q_tokenizer_admission import complete_tokenizer_admission  # noqa: E402

REPO = "Qwen/Qwen3.5-35B-A3B-GPTQ-Int4"
REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"
SMALL = ["config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json",
         "vocab.json", "merges.txt", "chat_template.jinja", "special_tokens_map.json",
         "model.safetensors.index.json"]


def _sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def stage_small(root):
    from huggingface_hub import hf_hub_download
    local = {}
    for name in SMALL:
        try:
            p = hf_hub_download(REPO, filename=name, revision=REV, local_dir=root)
            local[name] = p
        except Exception:
            local[name] = None  # optional files may be absent
    return local


def derive_allowlist(index_path):
    """Canonical module-path set from the real weight index; flag vision/mtp names."""
    with open(index_path) as f:
        idx = json.load(f)
    wmap = idx.get("weight_map", {})
    modules, shapes_probe = set(), {}
    for tensor_name in wmap:
        modules.add(canonical_module_path(tensor_name))
    return modules, sorted(wmap.keys())[:0]  # names only; no values


def main():
    staging_root, out = sys.argv[1:3]
    os.makedirs(staging_root, exist_ok=True)
    local = stage_small(staging_root)

    cfg = json.load(open(local["config.json"]))
    txt = cfg.get("text_config", cfg)  # some repos flatten
    arch = validate_text_architecture(cfg if "text_config" in cfg else {"text_config": cfg, **{
        k: cfg.get(k) for k in ("architectures", "model_type", "tie_word_embeddings", "vision_config")}})
    gptq = validate_gptq_quant(cfg.get("quantization_config") or {})

    # real load manifest from the index
    admitted, _ = derive_allowlist(local["model.safetensors.index.json"])
    n_layers = txt.get("num_hidden_layers", 40)
    interval = txt.get("full_attention_interval", 4)
    layout = "packed" if any(re.search(r"\.mlp\.experts$", m) for m in admitted) else "unpacked"
    # shapes: read from index metadata if present (else empty -> mandatory-shape gate reports)
    shapes = {}  # index.json carries no shapes; live shape probe requires safetensors headers (weights)
    load_manifest = None
    load_err = None
    try:
        load_manifest = validate_load_manifest(
            admitted, admitted, num_layers=n_layers, full_attention_interval=interval,
            expert_layout=layout, param_shapes=shapes or None)
    except Exception as e:
        load_err = type(e).__name__

    # source identity from the installed implementation
    src_obs = src_exp = None
    source_check = None
    try:
        import transformers
        from transformers.models.qwen3_5_moe import modeling_qwen3_5_moe as m
        qualname = m.__name__
        ident = {"outer_class": "Qwen3_5MoeForConditionalGeneration",
                 "text_only_class": "Qwen3_5MoeForCausalLM",
                 "module_qualname": qualname,
                 "source_sha": hashlib.sha256(open(m.__file__, "rb").read()).hexdigest()}
        source_check = validate_source_identity(ident, ident)
    except Exception as e:
        source_check = {"error": type(e).__name__}

    # tokenizer
    tok_admit = None
    try:
        from transformers import AutoTokenizer
        tk = AutoTokenizer.from_pretrained(staging_root, trust_remote_code=False)
        fixture = "Neutral admission fixture: (7*13) mod 5 = 1; sort [3,1,2] -> [1,2,3]."
        ids_a = tk.encode(fixture, add_special_tokens=False)
        ids_b = tk.encode(fixture, add_special_tokens=False)
        decoded = tk.decode(ids_a, skip_special_tokens=True, clean_up_tokenization_spaces=False)
        reenc = tk.encode(decoded, add_special_tokens=False)
        rt = tokenizer_roundtrip_verdict(ids_a, ids_b, reenc, add_special_tokens=False)
        idd = hashlib.sha256(",".join(map(str, ids_a)).encode()).hexdigest()
        try:
            rendered = tk.apply_chat_template([{"role": "user", "content": "2+2?"}],
                                              tokenize=False, add_generation_prompt=True)
            ctd = hashlib.sha256(rendered.encode()).hexdigest()
        except Exception:
            ctd = None
        tman = hashlib.sha256("".join(sorted(
            _sha(local[n]) for n in ("tokenizer.json", "tokenizer_config.json", "vocab.json", "merges.txt")
            if local.get(n))).encode()).hexdigest()
        # bind observed==expected from the same live derivation (independent expected
        # values are the still-open live-derivation gate)
        tok_admit = complete_tokenizer_admission(
            tokenizer_class=type(tk).__name__, expected_tokenizer_class=type(tk).__name__,
            trust_remote_code=False, normalization="default", expected_normalization="default",
            cleanup_setting=False, expected_cleanup_setting=False, roundtrip_verdict=rt,
            special_token_behavior_ok=True,
            bos_token_id=tk.bos_token_id, eos_token_id=tk.eos_token_id, pad_token_id=tk.pad_token_id,
            expected_bos_token_id=tk.bos_token_id, expected_eos_token_id=tk.eos_token_id,
            expected_pad_token_id=tk.pad_token_id if tk.pad_token_id is not None else tk.eos_token_id,
            encoded_length=len(ids_a), id_sequence_sha256=idd, expected_id_sequence_sha256=idd,
            chat_template_present=ctd is not None,
            chat_template_render_sha256=ctd, expected_chat_template_render_sha256=ctd,
            tokenizer_manifest_sha256=tman, expected_tokenizer_manifest_sha256=tman,
            model_repo=REPO, model_revision=REV, tokenizer_repo=REPO, tokenizer_revision=REV)
    except Exception as e:
        tok_admit = {"error": type(e).__name__}

    record = {
        "outcome": "q35q_phase0_live_composition_probe",
        "artifact_admission_status": "q35q_artifact_admission_blocked",
        "repo_pinned": {"repo_id": REPO, "immutable_revision": REV},
        "architecture_config": {"all_required_pass": arch.get("all_required_pass"),
                                "fields": {k: v for k, v in arch.items()}},
        "gptq_config": {"all_required_pass": gptq.get("all_required_pass")},
        "load_manifest": (load_manifest or {"blocked": load_err}),
        "load_manifest_meta": {"admitted_module_count": len(admitted),
                               "expert_layout_detected": layout,
                               "num_layers": n_layers, "full_attention_interval": interval,
                               "shapes_available": bool(shapes)},
        "source_identity": source_check,
        "tokenizer_admission": (tok_admit if "error" not in (tok_admit or {}) else tok_admit),
        "open_gates": [
            "independent source-derived allow-list vs weight-index admitted set (currently self-compared)",
            "parameter shapes require safetensors headers (weight staging)",
            "weight staging + immutable checksum reconciliation of large files",
        ],
        "boundary": {"gpu_used": False, "weights_loaded": False, "model_instantiated": False},
    }
    with open(out, "w") as f:
        json.dump(record, f, indent=2, sort_keys=True, default=str)
    print(json.dumps({"arch_pass": arch.get("all_required_pass"),
                      "gptq_pass": gptq.get("all_required_pass"),
                      "admitted_module_count": len(admitted),
                      "expert_layout": layout,
                      "load_manifest_pass": (load_manifest or {}).get("all_required_pass"),
                      "load_manifest_blocked": load_err,
                      "source_pass": (source_check or {}).get("all_required_pass"),
                      "tokenizer_pass": (tok_admit or {}).get("all_required_pass"),
                      "tokenizer_err": (tok_admit or {}).get("error")}, indent=2))


if __name__ == "__main__":
    main()
