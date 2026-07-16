"""Q35Q Phase-0 admission logic (CPU-only, pure, testable).

Corrected per docs/STEER_ADDENDUM_2026-07-16_Q35Q_PHASE0_ADMISSION_CORRECTION_AND_TP_RUNTIME.md
and steer.md "repair Q35Q artifact admission". Every frozen field gets its own
pass/fail; the overall admission is the conjunction over all required fields (no
small-subset boolean). Deterministic public-file manifests exclude caches and
downloader metadata. Tokenizer roundtrip is a real deterministic decode/re-encode
under a preregistered normalization rule, not a substring check.

Pure functions here take already-parsed metadata so they are unit-testable
without network/model. The thin CLI in scripts/q35q_stage_admission.py performs
download + tokenizer load and feeds these validators. No GPU, no weights.
"""
from __future__ import annotations

import hashlib
import re

# --- Frozen Qwen3.5-35B-A3B text-only expectations (public model card / config) ---
EXPECTED = {
    "outer_architectures": ["Qwen3_5MoeForConditionalGeneration"],
    "outer_model_type": "qwen3_5_moe",
    "text_model_type": "qwen3_5_moe_text",
    "hidden_size": 2048,
    "num_hidden_layers": 40,
    "vocab_size": 248320,
    "num_experts": 256,
    "num_experts_per_tok": 8,
    "moe_intermediate_size": 512,
    "shared_expert_intermediate_size": 512,
    "full_attention_interval": 4,
    "tie_word_embeddings": False,
}
GPTQ_EXPECTED = {"bits": 4, "group_size": 128, "quant_method": "gptq", "sym": True}

# Local paths that must never enter a deterministic public-file manifest.
_MANIFEST_EXCLUDE = re.compile(
    r"(^|/)\.cache(/|$)|(^|/)\.locks(/|$)|\.lock$|\.tmp$|\.temp$|"
    r"\.incomplete$|\.partial$|~$|(^|/)\.gitattributes$")


class Q35QStageBlock(Exception):
    """Fail-closed staging/admission failure."""


def expected_layer_types(num_layers=40, interval=4):
    """Hybrid schedule: `interval-1` linear_attention then one full_attention,
    repeated. For interval=4, num_layers=40 -> [lin,lin,lin,full] x10."""
    return ["full_attention" if (i + 1) % interval == 0 else "linear_attention"
            for i in range(num_layers)]


def validate_text_architecture(config: dict) -> dict:
    """Per-field text-only architecture admission. Returns {field: bool, ...,
    'all_required_pass': bool}. Never collapses into a subset boolean."""
    if not isinstance(config, dict):
        raise Q35QStageBlock("config must be a dict")
    txt = config.get("text_config")
    if not isinstance(txt, dict):
        raise Q35QStageBlock("text_config missing (multimodal text-only load requires it)")
    checks = {
        "outer_architectures": config.get("architectures") == EXPECTED["outer_architectures"],
        "outer_model_type": config.get("model_type") == EXPECTED["outer_model_type"],
        "text_model_type": txt.get("model_type") == EXPECTED["text_model_type"],
        "hidden_size": txt.get("hidden_size") == EXPECTED["hidden_size"],
        "num_hidden_layers": txt.get("num_hidden_layers") == EXPECTED["num_hidden_layers"],
        "vocab_size": txt.get("vocab_size") == EXPECTED["vocab_size"],
        "num_experts": txt.get("num_experts") == EXPECTED["num_experts"],
        "num_experts_per_tok": txt.get("num_experts_per_tok") == EXPECTED["num_experts_per_tok"],
        "moe_intermediate_size": txt.get("moe_intermediate_size") == EXPECTED["moe_intermediate_size"],
        "shared_expert_intermediate_size":
            txt.get("shared_expert_intermediate_size") == EXPECTED["shared_expert_intermediate_size"],
        "full_attention_interval": txt.get("full_attention_interval") == EXPECTED["full_attention_interval"],
        "layer_types_hybrid_schedule":
            list(txt.get("layer_types") or []) == expected_layer_types(
                EXPECTED["num_hidden_layers"], EXPECTED["full_attention_interval"]),
        "untied_output_head": config.get("tie_word_embeddings") is False,
        "vision_present_in_repo": isinstance(config.get("vision_config"), dict),
        "mtp_metadata_present": txt.get("mtp_num_hidden_layers") is not None,
    }
    checks["all_required_pass"] = all(v for k, v in checks.items() if k != "all_required_pass")
    return checks


def validate_gptq_quant(qcfg: dict) -> dict:
    """GPTQ quantization identity checks + skip-rule presence."""
    if not isinstance(qcfg, dict):
        raise Q35QStageBlock("quantization_config missing")
    dyn = qcfg.get("dynamic") or {}
    dyn_keys = " ".join(dyn.keys()) if isinstance(dyn, dict) else ""
    checks = {
        "bits_4": qcfg.get("bits") == GPTQ_EXPECTED["bits"],
        "group_size_128": qcfg.get("group_size") == GPTQ_EXPECTED["group_size"],
        "quant_method_gptq": qcfg.get("quant_method") == GPTQ_EXPECTED["quant_method"],
        "symmetric": qcfg.get("sym") == GPTQ_EXPECTED["sym"],
        "skips_attention": "attn" in dyn_keys,
        "skips_mtp": "mtp" in dyn_keys,
        "skips_shared_expert": "shared_expert" in dyn_keys,
        "skips_vision": "visual" in dyn_keys or "vision" in dyn_keys,
        "skips_lm_head": "lm_head" in dyn or any("lm_head" in k for k in (dyn if isinstance(dyn, dict) else [])),
    }
    checks["all_required_pass"] = all(v for k, v in checks.items() if k != "all_required_pass")
    return checks


def admitted_public_manifest(admitted_files, present_files) -> dict:
    """Deterministic public-file manifest from the pinned repo's admitted file
    list. `admitted_files`: {relpath: sha256} for the pinned public files;
    `present_files`: {relpath: sha256} actually staged. Fails closed on cache/
    metadata contamination among *admitted* names, path escape, missing file, or
    hash mismatch. Extra non-excluded files not in the admitted set are
    contamination."""
    if not admitted_files:
        raise Q35QStageBlock("empty admitted file set")
    for rel in list(admitted_files) + list(present_files):
        if rel.startswith("/") or ".." in rel.split("/"):
            raise Q35QStageBlock(f"path escape / absolute path: {rel!r}")
    missing = [r for r in admitted_files if r not in present_files]
    if missing:
        raise Q35QStageBlock(f"missing admitted files: {len(missing)}")
    mismatch = [r for r in admitted_files if present_files[r] != admitted_files[r]]
    if mismatch:
        raise Q35QStageBlock(f"hash mismatch: {len(mismatch)}")
    extra = [r for r in present_files if r not in admitted_files
             and not _MANIFEST_EXCLUDE.search(r)]
    if extra:
        raise Q35QStageBlock(f"unapproved extra files: {len(extra)}")
    contaminated = [r for r in admitted_files if _MANIFEST_EXCLUDE.search(r)]
    if contaminated:
        raise Q35QStageBlock("cache/metadata contaminated the admitted set")
    lines = [f"{r}:{admitted_files[r]}" for r in sorted(admitted_files)]
    return {"file_count": len(admitted_files),
            "manifest_sha256": hashlib.sha256("\n".join(lines).encode()).hexdigest()}


def tokenizer_roundtrip_verdict(ids_a, ids_b, reencoded_ids,
                                add_special_tokens: bool) -> dict:
    """Deterministic roundtrip verdict (NOT substring). Requires two identical
    encode passes and that decode->re-encode reproduces the exact id sequence."""
    ids_a, ids_b, reencoded_ids = list(ids_a), list(ids_b), list(reencoded_ids)
    checks = {
        "deterministic_encode": ids_a == ids_b,
        "exact_decode_reencode": ids_a == reencoded_ids,
        "no_special_tokens_requested": add_special_tokens is False,
        "nonempty": len(ids_a) > 0,
    }
    checks["roundtrip_pass"] = all(v for k, v in checks.items() if k != "roundtrip_pass")
    return checks
