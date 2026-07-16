"""Q35Q Phase-0 complete tokenizer-admission tests (CPU-only, no model/network).

Proves the tokenizer conjunction fails closed when any bound field is missing or
wrong — the gap flagged as second-repair defect 5 (the prior overall boolean
required only roundtrip_pass).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_tokenizer_admission import complete_tokenizer_admission

REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"
H = "a" * 64


def good_roundtrip(**over):
    v = {"roundtrip_pass": True, "no_special_tokens_requested": True,
         "deterministic_encode": True, "exact_decode_reencode": True, "nonempty": True}
    v.update(over)
    return v


def good(**over):
    kw = dict(
        tokenizer_class="Qwen2TokenizerFast", expected_tokenizer_class="Qwen2TokenizerFast",
        trust_remote_code=False, normalization="nfc", expected_normalization="nfc",
        cleanup_setting=False, roundtrip_verdict=good_roundtrip(),
        special_token_behavior_ok=True, bos_token_id=1, eos_token_id=2, pad_token_id=0,
        encoded_length=44, id_sequence_sha256=H, chat_template_present=True,
        chat_template_render_sha256="b" * 64, tokenizer_manifest_sha256="c" * 64,
        model_repo="Qwen/Qwen3.5-35B-A3B-GPTQ-Int4", model_revision=REV,
        tokenizer_repo="Qwen/Qwen3.5-35B-A3B-GPTQ-Int4", tokenizer_revision=REV)
    kw.update(over)
    return kw


def test_full_pass():
    out = complete_tokenizer_admission(**good())
    assert out["all_required_pass"] is True
    assert all(v for k, v in out.items() if k != "all_required_pass")


@pytest.mark.parametrize("field,bad", [
    ("tokenizer_class", "WrongTokenizer"),
    ("trust_remote_code", True),
    ("normalization", "nfkc"),
    ("cleanup_setting", None),
    ("special_token_behavior_ok", False),
    ("bos_token_id", None),
    ("eos_token_id", None),
    ("pad_token_id", None),
    ("encoded_length", 0),
    ("id_sequence_sha256", None),
    ("chat_template_present", False),
    ("chat_template_render_sha256", None),
    ("tokenizer_manifest_sha256", None),
])
def test_each_field_can_fail(field, bad):
    out = complete_tokenizer_admission(**good(**{field: bad}))
    assert out["all_required_pass"] is False


def test_roundtrip_failure_blocks():
    out = complete_tokenizer_admission(**good(roundtrip_verdict=good_roundtrip(roundtrip_pass=False)))
    assert out["roundtrip_pass"] is False and out["all_required_pass"] is False


def test_special_tokens_requested_blocks():
    out = complete_tokenizer_admission(
        **good(roundtrip_verdict=good_roundtrip(no_special_tokens_requested=False)))
    assert out["no_special_tokens_encoding"] is False and out["all_required_pass"] is False


def test_model_tokenizer_repo_mismatch_blocks():
    out = complete_tokenizer_admission(**good(tokenizer_repo="Qwen/other-repo"))
    assert out["model_tokenizer_repo_paired"] is False and out["all_required_pass"] is False


def test_model_tokenizer_revision_mismatch_blocks():
    out = complete_tokenizer_admission(**good(tokenizer_revision="f" * 40))
    assert out["model_tokenizer_revision_paired"] is False and out["all_required_pass"] is False


def test_mutable_revision_not_paired():
    out = complete_tokenizer_admission(**good(model_revision="main", tokenizer_revision="main"))
    assert out["model_tokenizer_revision_paired"] is False and out["all_required_pass"] is False


def test_non_hex_digests_block():
    out = complete_tokenizer_admission(**good(chat_template_render_sha256="not-hex"))
    assert out["chat_template_render_digest_bound"] is False and out["all_required_pass"] is False


def test_missing_repo_identity_raises():
    with pytest.raises(Q35QStageBlock):
        complete_tokenizer_admission(**good(model_repo=""))


def test_bad_roundtrip_verdict_type_raises():
    with pytest.raises(Q35QStageBlock):
        complete_tokenizer_admission(**good(roundtrip_verdict=None))
