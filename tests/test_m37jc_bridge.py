"""M37J-C Phase 0B bridge unit tests (fake decoder stack, CPU only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest
import torch

from jlens_vllm_telemetry.bridge import (
    BRIDGE_LAYERS, SemanticBridgeCollector, install_bridge,
    semantic_group_scores, uninstall_bridge)

HIDDEN, VOCAB, N_LAYERS = 32, 64, 40


class FakeLayer(torch.nn.Module):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx

    def forward(self, x):
        return x + self.idx  # distinguishable per-layer output


def make_stack():
    return torch.nn.ModuleList([FakeLayer(i) for i in range(N_LAYERS)])


def run_decode(layers, n_steps, hidden=HIDDEN):
    """Simulate prefill (multi-token row) then n_steps single-token rows."""
    prefill = torch.randn(7, hidden)
    for layer in layers:
        layer(prefill)
    for step in range(n_steps):
        x = torch.full((1, hidden), float(step))
        for layer in layers:
            layer(x)


def test_inert_by_default():
    layers = make_stack()
    collector = SemanticBridgeCollector(HIDDEN, n_slots=8)
    collector.allocate("cpu")
    handles = install_bridge(layers, collector)
    run_decode(layers, 40)               # enabled is False
    assert int(collector._cursor.sum()) == 0
    assert int(collector._decode_step.sum()) == 0
    uninstall_bridge(handles)


def test_disabled_path_output_parity():
    layers = make_stack()
    x = torch.randn(3, HIDDEN)
    before = [layer(x.clone()).clone() for layer in layers]
    collector = SemanticBridgeCollector(HIDDEN, n_slots=8)
    collector.allocate("cpu")
    handles = install_bridge(layers, collector)
    collector.enabled = True
    after = [layer(x.clone()).clone() for layer in layers]
    uninstall_bridge(handles)
    for b, a in zip(before, after):
        assert torch.equal(b, a), "hooks must never modify outputs"


def test_cadence_and_final_capture():
    layers = make_stack()
    collector = SemanticBridgeCollector(HIDDEN, n_slots=8, cadence=32)
    collector.allocate("cpu")
    handles = install_bridge(layers, collector)
    collector.enabled = True
    run_decode(layers, 70)               # steps 0..69
    uninstall_bridge(handles)
    # Cadence slots at steps 31 and 63 for every bridged layer.
    assert collector._cursor.tolist() == [2] * len(BRIDGE_LAYERS)
    assert collector._slot_step[0, :2].tolist() == [31, 63]
    assert int(collector._decode_step[0]) == 70


def test_bounded_memory_drops_and_counts():
    layers = make_stack()
    collector = SemanticBridgeCollector(HIDDEN, n_slots=2, cadence=4)
    collector.allocate("cpu")
    handles = install_bridge(layers, collector)
    collector.enabled = True
    run_decode(layers, 40)               # 10 cadence hits, 2 slots
    uninstall_bridge(handles)
    assert collector._cursor.tolist() == [2] * len(BRIDGE_LAYERS)
    assert collector._dropped.tolist() == [8] * len(BRIDGE_LAYERS)


def make_captured_collector(n_steps=8, n_slots=8, cadence=4):
    layers = make_stack()
    collector = SemanticBridgeCollector(HIDDEN, n_slots=n_slots,
                                        cadence=cadence)
    collector.allocate("cpu")
    handles = install_bridge(layers, collector)
    collector.enabled = True
    run_decode(layers, n_steps)
    uninstall_bridge(handles)
    return collector


def gathered_project(norm, shard_heads, pad_cols=0):
    """Reference TP projection: per-shard head matmuls gathered along
    the vocab axis (what vLLM's LogitsProcessor produces on the root)."""
    def project(residuals):
        h = norm(residuals.to(norm.weight.dtype))
        full = torch.cat([head(h) for head in shard_heads], dim=-1)
        if pad_cols:
            full = torch.cat(
                [full, torch.full((*full.shape[:-1], pad_cols),
                                  1e9)], dim=-1)  # poisoned padding
        return full
    return project


def test_readout_matches_gathered_reference():
    collector = make_captured_collector()
    norm = torch.nn.LayerNorm(HIDDEN)
    shard_heads = [torch.nn.Linear(HIDDEN, VOCAB // 2, bias=False)
                   for _ in range(2)]
    result = collector.readout(gathered_project(norm, shard_heads), VOCAB)
    data = result["readout"][str(collector.layers[0])]
    assert data["finite"] and result["authoritative"]
    residual = collector._buf[0, 0].to(norm.weight.dtype)
    direct = torch.cat([h(norm(residual)) for h in shard_heads]).float()
    expect = torch.topk(direct, result["top_k"]).indices.tolist()
    assert data["token_ids"][0] == expect
    assert data["steps"][-1] == 7        # final position appended


def test_direct_parallel_head_forward_is_never_called():
    class ForbiddenHead(torch.nn.Module):
        def forward(self, x):  # mirrors vLLM ParallelLMHead.forward
            raise RuntimeError(
                "LMHead's weights should be used in the sampler.")

    collector = make_captured_collector()
    norm = torch.nn.LayerNorm(HIDDEN)
    forbidden = ForbiddenHead()
    safe_head = torch.nn.Linear(HIDDEN, VOCAB, bias=False)

    def compute_logits_path(residuals):
        # Supported path uses the head's weights via a processor, not
        # head.forward; forbidden.forward must never fire.
        return safe_head(norm(residuals.to(norm.weight.dtype)))

    result = collector.readout(compute_logits_path, VOCAB)
    assert result["authoritative"]
    # And the forbidden module really does raise if touched directly:
    with pytest.raises(RuntimeError, match="sampler"):
        forbidden(torch.randn(1, HIDDEN))


def test_nonroot_rank_returns_status_only():
    collector = make_captured_collector()
    calls = {"n": 0}

    def nonroot_project(residuals):
        calls["n"] += 1
        return None                       # gather returns None off-root

    result = collector.readout(nonroot_project, VOCAB)
    assert result["authoritative"] is False
    assert result["readout"] == {}        # no shard-local ids leak
    assert result["projection_calls"] == calls["n"] > 0


def test_winning_token_on_second_shard_gets_global_id():
    collector = make_captured_collector()
    norm = torch.nn.LayerNorm(HIDDEN)
    shard0 = torch.nn.Linear(HIDDEN, VOCAB // 2, bias=False)
    shard1 = torch.nn.Linear(HIDDEN, VOCAB // 2, bias=False)
    with torch.no_grad():
        shard0.weight.mul_(0.0)           # shard 0 can never win
        shard1.weight.add_(1.0)
    result = collector.readout(gathered_project(norm, [shard0, shard1]),
                               VOCAB)
    for data in result["readout"].values():
        for ids in data["token_ids"]:
            assert all(VOCAB // 2 <= t < VOCAB for t in ids), (
                "winner must carry the global (shard-offset) id")


def test_padded_vocab_is_trimmed():
    collector = make_captured_collector()
    norm = torch.nn.LayerNorm(HIDDEN)
    heads = [torch.nn.Linear(HIDDEN, VOCAB // 2, bias=False)
             for _ in range(2)]
    # 16 poisoned padding columns with huge logits: if trimming fails,
    # top-k picks them and the id-range guard trips.
    result = collector.readout(
        gathered_project(norm, heads, pad_cols=16), VOCAB)
    for data in result["readout"].values():
        for ids in data["token_ids"]:
            assert all(0 <= t < VOCAB for t in ids)


def test_identical_projection_call_counts_across_ranks():
    root = make_captured_collector(n_steps=20, n_slots=8, cadence=4)
    other = make_captured_collector(n_steps=20, n_slots=8, cadence=4)
    norm = torch.nn.LayerNorm(HIDDEN)
    head = torch.nn.Linear(HIDDEN, VOCAB, bias=False)
    r_root = root.readout(
        lambda r: head(norm(r.to(norm.weight.dtype))), VOCAB)
    r_other = other.readout(lambda r: None, VOCAB)
    assert r_root["projection_calls"] == r_other["projection_calls"] > 0, (
        "ranks must issue identical collective call counts")


def test_projection_chunking_is_bounded():
    collector = make_captured_collector(n_steps=64, n_slots=32, cadence=2)
    norm = torch.nn.LayerNorm(HIDDEN)
    head = torch.nn.Linear(HIDDEN, VOCAB, bias=False)
    sizes = []

    def project(residuals):
        sizes.append(residuals.shape[0])
        return head(norm(residuals.to(norm.weight.dtype)))

    collector.readout(project, VOCAB)
    cap = SemanticBridgeCollector.PROJECTION_CHUNK_SLOTS
    assert sizes and max(sizes) <= cap
    assert len(sizes) >= len(BRIDGE_LAYERS) * 2  # chunk walk per layer


def test_reset_clears_state():
    layers = make_stack()
    collector = SemanticBridgeCollector(HIDDEN, n_slots=8, cadence=4)
    collector.allocate("cpu")
    handles = install_bridge(layers, collector)
    collector.enabled = True
    run_decode(layers, 12)
    collector.reset()
    assert int(collector._cursor.sum()) == 0
    assert int(collector._decode_step.sum()) == 0
    assert int((collector._slot_step != -1).sum()) == 0
    uninstall_bridge(handles)


def test_semantic_group_scores_fixed_groups():
    vocab_words = {0: "final", 1: "check", 2: "xyz", 3: "maybe"}
    readout = {"readout": {"4": {"steps": [31],
                                 "token_ids": [[0, 2], [1, 3]],
                                 "finite": True}}}
    scores = semantic_group_scores(readout,
                                   lambda t: vocab_words.get(t, "?"))
    assert scores["group_completion"] == 1.0
    assert scores["group_verification"] == 1.0
    assert scores["group_uncertainty"] == 1.0
    assert scores["group_error_conflict"] == 0.0
