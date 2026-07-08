#!/usr/bin/env python3
"""CPU stub test for capture_one greedy-decode wiring (no GPU, no download).

Mimics the HF MoE forward interface with a random stub so we can assert the
decode loop produces N per-token records with correct fields/shapes, and that
max_new_tokens==0 stays prefill-only (no regression).
"""
import sys
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from capture_router_logits import capture_one  # noqa: E402

N_LAYERS, N_EXP, VOCAB, HID = 3, 8, 16, 4


class StubTok:
    eos_token_id = -999  # never hit in tests

    def __call__(self, text, return_tensors, truncation, max_length):
        return {"input_ids": torch.tensor([[1, 2, 3, 4]]),
                "attention_mask": torch.ones(1, 4, dtype=torch.long)}

    def decode(self, ids):
        return f"<{ids[0]}>"


class _Out:
    pass


class StubModel:
    device = "cpu"

    def __call__(self, input_ids=None, attention_mask=None, past_key_values=None,
                 output_router_logits=False, output_hidden_states=False,
                 use_cache=False, **kw):
        seq = input_ids.shape[1]
        o = _Out()
        o.router_logits = [torch.randn(1, seq, N_EXP) for _ in range(N_LAYERS)]
        o.hidden_states = ([torch.randn(1, seq, HID) for _ in range(N_LAYERS + 1)]
                           if output_hidden_states else None)
        o.logits = torch.randn(1, seq, VOCAB)
        o.past_key_values = object() if use_cache else None
        return o


def test_prefill_only_no_decode():
    ids, router, hidden, steps = capture_one(
        StubTok(), StubModel(), "hello", 128, max_new_tokens=0)
    assert steps is None
    assert ids.shape[0] == 4
    assert len(router) == N_LAYERS and len(hidden) == N_LAYERS + 1
    assert router[0].shape == (4, N_EXP)


def test_decode_captures_per_token():
    k = 5
    ids, router, hidden, steps = capture_one(
        StubTok(), StubModel(), "hello", 128, max_new_tokens=k)
    assert len(steps) == k, f"expected {k} steps, got {len(steps)}"
    req = {"generated_token_index", "generated_token_id", "generated_token_text",
           "selected_token_prob", "entropy_final_logits", "router_logits"}
    for i, s in enumerate(steps):
        assert req <= set(s), set(s) ^ req
        assert s["generated_token_index"] == i
        assert isinstance(s["generated_token_id"], int)
        assert 0.0 <= s["selected_token_prob"] <= 1.0
        assert s["entropy_final_logits"] >= 0.0
        assert len(s["router_logits"]) == N_LAYERS
        # single decoded token -> per-layer router shape (1, N_EXP)
        assert s["router_logits"][0].shape == (1, N_EXP)
    # prefill unchanged alongside decode
    assert len(router) == N_LAYERS and router[0].shape == (4, N_EXP)


if __name__ == "__main__":
    test_prefill_only_no_decode()
    test_decode_captures_per_token()
    print("[jlens] decode-capture stub tests PASSED")
