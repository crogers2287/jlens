"""Q35Q Phase-0 complete tokenizer-admission tests (CPU-only, no model/network).

Proves the tokenizer conjunction binds every observed value to an independently
derived expected value by equality — the gaps flagged as tokenizer-binding
defects 1-4 (wrong cleanup, substituted special-token IDs, boolean encoded
length, and caller-supplied fake-but-valid-shape digests must all fail closed).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_tokenizer_admission import complete_tokenizer_admission

REV = "3af5ca2972faf6de1fd6f4efc4d8d319ca751e8b"
IDD = "a" * 64   # id-sequence digest
CTD = "b" * 64   # chat-template render digest
TMD = "c" * 64   # tokenizer manifest digest


def good_roundtrip(**over):
    v = {"roundtrip_pass": True, "no_special_tokens_requested": True,
         "deterministic_encode": True, "exact_decode_reencode": True, "nonempty": True}
    v.update(over)
    return v


def good(**over):
    kw = dict(
        tokenizer_class="Qwen2TokenizerFast", expected_tokenizer_class="Qwen2TokenizerFast",
        trust_remote_code=False, normalization="nfc", expected_normalization="nfc",
        cleanup_setting=False, expected_cleanup_setting=False,
        roundtrip_verdict=good_roundtrip(), special_token_behavior_ok=True,
        bos_token_id=1, eos_token_id=2, pad_token_id=0,
        expected_bos_token_id=1, expected_eos_token_id=2, expected_pad_token_id=0,
        encoded_length=44,
        id_sequence_sha256=IDD, expected_id_sequence_sha256=IDD,
        chat_template_present=True,
        chat_template_render_sha256=CTD, expected_chat_template_render_sha256=CTD,
        tokenizer_manifest_sha256=TMD, expected_tokenizer_manifest_sha256=TMD,
        model_repo="Qwen/Qwen3.5-35B-A3B-GPTQ-Int4", model_revision=REV,
        tokenizer_repo="Qwen/Qwen3.5-35B-A3B-GPTQ-Int4", tokenizer_revision=REV)
    kw.update(over)
    return kw


def test_full_pass():
    out = complete_tokenizer_admission(**good())
    assert out["all_required_pass"] is True
    assert all(v for k, v in out.items() if k != "all_required_pass")


# ---------- defect 1: cleanup must be exact equality, not merely non-null ----------

def test_present_but_wrong_cleanup_fails():
    out = complete_tokenizer_admission(**good(cleanup_setting=True, expected_cleanup_setting=False))
    assert out["cleanup_setting_admitted"] is False and out["all_required_pass"] is False


def test_missing_expected_cleanup_raises():
    with pytest.raises(Q35QStageBlock, match="expected_cleanup_setting"):
        complete_tokenizer_admission(**good(expected_cleanup_setting=None))


# ---------- defect 2: BOS/EOS/PAD bound to expected identities ----------

@pytest.mark.parametrize("field,exp_field", [
    ("bos_token_id", "expected_bos_token_id"),
    ("eos_token_id", "expected_eos_token_id"),
    ("pad_token_id", "expected_pad_token_id"),
])
def test_substituted_special_token_id_fails(field, exp_field):
    out = complete_tokenizer_admission(**good(**{field: 999}))
    key = {"bos_token_id": "bos_identity_bound", "eos_token_id": "eos_identity_bound",
           "pad_token_id": "pad_identity_bound"}[field]
    assert out[key] is False and out["all_required_pass"] is False


@pytest.mark.parametrize("null_field", ["bos_token_id", "eos_token_id", "pad_token_id"])
def test_null_observed_vs_nonnull_expected_fails(null_field):
    # a dropped/absent observed id against a non-null expected identity fails
    out = complete_tokenizer_admission(**good(**{null_field: None}))
    assert out["all_required_pass"] is False


def test_legitimately_absent_token_admitted_when_expected_null():
    # real Qwen case: bos_token_id is None; admitted only because expected is None
    out = complete_tokenizer_admission(**good(bos_token_id=None, expected_bos_token_id=None))
    assert out["bos_identity_bound"] is True and out["all_required_pass"] is True


def test_nonnull_observed_vs_null_expected_fails():
    out = complete_tokenizer_admission(**good(bos_token_id=5, expected_bos_token_id=None))
    assert out["bos_identity_bound"] is False and out["all_required_pass"] is False


def test_missing_expected_special_token_identity_raises():
    kw = good()
    del kw["expected_eos_token_id"]  # not supplied at all -> sentinel -> raise
    with pytest.raises(Q35QStageBlock, match="must be independently supplied"):
        complete_tokenizer_admission(**kw)


# ---------- defect 3: boolean encoded length rejected ----------

def test_boolean_encoded_length_fails():
    out = complete_tokenizer_admission(**good(encoded_length=True))
    assert out["encoded_length_strict_positive_int"] is False and out["all_required_pass"] is False


def test_zero_encoded_length_fails():
    out = complete_tokenizer_admission(**good(encoded_length=0))
    assert out["encoded_length_strict_positive_int"] is False and out["all_required_pass"] is False


# ---------- defect 4: digest equality, not just hex shape ----------

def test_caller_fake_but_valid_shape_id_digest_fails():
    out = complete_tokenizer_admission(**good(id_sequence_sha256="d" * 64))  # valid hex, wrong value
    assert out["id_sequence_digest_bound"] is False and out["all_required_pass"] is False


def test_caller_fake_chat_render_digest_fails():
    out = complete_tokenizer_admission(**good(chat_template_render_sha256="e" * 64))
    assert out["chat_template_render_digest_bound"] is False and out["all_required_pass"] is False


def test_caller_fake_manifest_digest_fails():
    out = complete_tokenizer_admission(**good(tokenizer_manifest_sha256="f" * 64))
    assert out["tokenizer_manifest_identity_bound"] is False and out["all_required_pass"] is False


def test_non_hex_digest_fails():
    out = complete_tokenizer_admission(
        **good(id_sequence_sha256="not-hex", expected_id_sequence_sha256="not-hex"))
    assert out["id_sequence_digest_bound"] is False and out["all_required_pass"] is False


# ---------- remaining conjunction fields ----------

@pytest.mark.parametrize("field,bad", [
    ("tokenizer_class", "WrongTokenizer"),
    ("trust_remote_code", True),
    ("normalization", "nfkc"),
    ("special_token_behavior_ok", False),
    ("chat_template_present", False),
])
def test_each_remaining_field_can_fail(field, bad):
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


def test_missing_repo_identity_raises():
    with pytest.raises(Q35QStageBlock):
        complete_tokenizer_admission(**good(model_repo=""))


def test_bad_roundtrip_verdict_type_raises():
    with pytest.raises(Q35QStageBlock):
        complete_tokenizer_admission(**good(roundtrip_verdict=None))
