"""M37J-C Phase 0B bridge unit tests (fake decoder stack, CPU only)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

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


def test_readout_matches_direct_projection():
    layers = make_stack()
    collector = SemanticBridgeCollector(HIDDEN, n_slots=8, cadence=4)
    collector.allocate("cpu")
    handles = install_bridge(layers, collector)
    collector.enabled = True
    run_decode(layers, 8)
    uninstall_bridge(handles)

    norm = torch.nn.LayerNorm(HIDDEN)
    head = torch.nn.Linear(HIDDEN, VOCAB, bias=False)
    result = collector.readout(norm, head)
    layer0 = collector.layers[0]
    data = result["readout"][str(layer0)]
    assert data["finite"]
    # Direct recomputation for the first captured slot.
    residual = collector._buf[0, 0].to(norm.weight.dtype)
    direct = head(norm(residual)).float()
    expect = torch.topk(direct, result["top_k"]).indices.tolist()
    assert data["token_ids"][0] == expect
    # Final position appended after cadence slots.
    assert data["steps"][-1] == 7


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
