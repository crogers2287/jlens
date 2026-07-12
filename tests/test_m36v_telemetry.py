"""M36V Phase 1 pre-flight tests (steer-required, run before the real smoke).

Covers: fake-MoE router/dispatch alignment, top-k id/weight capture,
normalization and finite-value checks, disabled-path no-op behavior,
summary-versus-raw feature equivalence, bounded-buffer behavior, and the
aggregate-only public-report guard. Uses fakes that reproduce the exact
call convention of vLLM's MoERunner modular path (kwargs into
``select_experts`` and ``forward_modular``).
"""

import sys
from pathlib import Path

import numpy as np
import pytest
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from jlens_vllm_telemetry.capture import (            # noqa: E402
    RouterTelemetryCollector,
    install_router_telemetry,
    uninstall_router_telemetry,
)
from jlens_vllm_telemetry.features import (           # noqa: E402
    derive_decode_records,
    summary_vs_raw_check,
)
from jlens_vllm_telemetry.report_guard import (       # noqa: E402
    PrivacyViolation,
    assert_aggregate_only,
)

NUM_EXPERTS = 32
TOP_K = 4
NUM_LAYERS = 3
HIDDEN = 8


class FakeRouter:
    """Softmax -> top-k -> renormalize, the Qwen3.5 routing semantics."""

    def select_experts(self, hidden_states, router_logits,
                       topk_indices_dtype=None, *, input_ids=None):
        probs = torch.softmax(router_logits.float(), dim=-1)
        topk = torch.topk(probs, k=TOP_K, dim=-1)
        weights = topk.values / topk.values.sum(dim=-1, keepdim=True)
        ids = topk.indices
        if topk_indices_dtype is not None:
            ids = ids.to(topk_indices_dtype)
        return weights, ids


class FakeRoutedExperts:
    """Records exactly what the fused dispatch call receives."""

    def __init__(self):
        self.received = []

    def forward_modular(self, x, topk_weights, topk_ids,
                        shared_experts=None, shared_experts_input=None):
        self.received.append(
            (topk_ids.detach().clone(), topk_weights.detach().clone())
        )
        return x


class FakeMoERunner:
    def __init__(self, layer_id):
        self._layer_id = layer_id
        self.router = FakeRouter()
        self.routed_experts = FakeRoutedExperts()

    @property
    def layer_id(self):
        return self._layer_id

    def step(self, x, router_logits):
        # Mirrors MoERunner._apply_quant_method's modular branch.
        topk_weights, topk_ids = self.router.select_experts(
            hidden_states=x,
            router_logits=router_logits,
            topk_indices_dtype=torch.int32,
        )
        return self.routed_experts.forward_modular(
            x=x, topk_weights=topk_weights, topk_ids=topk_ids
        )


def run_tokens(runners, collector, num_tokens, seed=0, tokens_per_call=1):
    """Drive all layers for num_tokens rows; returns the logits used."""
    gen = torch.Generator().manual_seed(seed)
    all_logits = []
    done = 0
    while done < num_tokens:
        n = min(tokens_per_call, num_tokens - done)
        x = torch.randn((n, HIDDEN), generator=gen)
        step_logits = []
        for runner in runners:
            logits = torch.randn((n, NUM_EXPERTS), generator=gen)
            runner.step(x, logits)
            step_logits.append(logits)
        all_logits.append(torch.stack(step_logits, dim=1))  # [n, L, E]
        done += n
    return torch.cat(all_logits, dim=0)


@pytest.fixture
def installed():
    runners = [FakeMoERunner(layer_id=i) for i in range(NUM_LAYERS)]
    collector = RouterTelemetryCollector(
        num_experts=NUM_EXPERTS, top_k=TOP_K,
        capacity_tokens=64, raw_sample_tokens=16,
    )
    handles = install_router_telemetry(runners, collector)
    collector.enabled = True
    yield runners, collector, handles
    uninstall_router_telemetry(handles)


def test_fake_moe_router_dispatch_alignment(installed):
    runners, collector, _ = installed
    run_tokens(runners, collector, num_tokens=10)
    cap = collector.fetch()
    assert cap["rows"] == 10
    for li, runner in enumerate(runners):
        received = runner.routed_experts.received
        assert len(received) == 10
        for row, (ids, weights) in enumerate(received):
            np.testing.assert_array_equal(
                cap["ids"][row, li], ids.numpy().reshape(-1).astype(np.int32)
            )
            np.testing.assert_allclose(
                cap["weights"][row, li], weights.numpy().reshape(-1),
                rtol=0, atol=1e-6,
            )
    assert cap["id_mismatch"] == [0] * NUM_LAYERS
    assert max(cap["weight_maxdiff"]) == 0.0
    assert cap["dispatch_missed"] == [0] * NUM_LAYERS


def test_topk_id_weight_capture_matches_reference(installed):
    runners, collector, _ = installed
    logits = run_tokens(runners, collector, num_tokens=6, seed=7)
    cap = collector.fetch()
    probs = torch.softmax(logits.double(), dim=-1)
    ref = torch.topk(probs, k=TOP_K, dim=-1)
    ref_w = (ref.values / ref.values.sum(-1, keepdim=True)).numpy()
    np.testing.assert_array_equal(
        np.sort(cap["ids"], -1), np.sort(ref.indices.numpy(), -1)
    )
    np.testing.assert_allclose(
        np.sort(cap["weights"], -1), np.sort(ref_w, -1), rtol=0, atol=1e-5
    )


def test_normalization_and_finite_values(installed):
    runners, collector, _ = installed
    run_tokens(runners, collector, num_tokens=8)
    cap = collector.fetch()
    assert cap["weight_nonfinite"] == [0] * NUM_LAYERS
    assert min(cap["weight_min"]) >= 0.0
    assert max(cap["weight_normdev"]) < 1e-5
    assert np.isfinite(cap["entropy"]).all()
    assert np.isfinite(cap["mass"]).all()
    assert (cap["mass"] > 0).all() and (cap["mass"] <= 1.0 + 1e-6).all()


def test_disabled_path_is_noop_and_uninstall_restores():
    runners = [FakeMoERunner(layer_id=i) for i in range(NUM_LAYERS)]
    originals = [
        (r.router.select_experts, r.routed_experts.forward_modular)
        for r in runners
    ]
    collector = RouterTelemetryCollector(num_experts=NUM_EXPERTS, top_k=TOP_K)
    handles = install_router_telemetry(runners, collector)
    # Telemetry disabled: forward runs, nothing is captured or allocated.
    run_tokens(runners, collector, num_tokens=4)
    cap = collector.fetch()
    assert cap["rows"] == 0
    assert collector._ids is None
    # Outputs are byte-identical to an uninstrumented run.
    x = torch.ones((1, HIDDEN))
    logits = torch.linspace(-1, 1, NUM_EXPERTS).unsqueeze(0)
    w_hooked, i_hooked = runners[0].router.select_experts(
        hidden_states=x, router_logits=logits
    )
    uninstall_router_telemetry(handles)
    for runner, (orig_sel, orig_fwd) in zip(runners, originals):
        assert runner.router.select_experts.__func__ is orig_sel.__func__
        assert runner.routed_experts.forward_modular.__func__ is orig_fwd.__func__
    w_plain, i_plain = runners[0].router.select_experts(
        hidden_states=x, router_logits=logits
    )
    torch.testing.assert_close(w_hooked, w_plain, rtol=0, atol=0)
    torch.testing.assert_close(i_hooked, i_plain, rtol=0, atol=0)


def test_summary_vs_raw_feature_equivalence(installed):
    runners, collector, _ = installed
    run_tokens(runners, collector, num_tokens=12, seed=3)
    cap = collector.fetch()
    check = summary_vs_raw_check(cap)
    assert check["checked"] and check["raw_rows"] == 12
    assert check["passed"], check
    # And the schema features derive without any raw tensors.
    records = derive_decode_records(
        cap["ids"], cap["weights"], cap["entropy"], cap["mass"],
        prompt_rows=4, num_experts=NUM_EXPERTS,
    )
    assert len(records) == 8
    first = records[0]
    assert first["drift_from_previous_token_weighted"] is None
    assert 0.0 <= first["drift_from_prefill_weighted"] <= 2.0
    assert len(first["full_entropy"]) == NUM_LAYERS


def test_bounded_buffer_drops_and_counts(installed):
    runners, collector, _ = installed
    run_tokens(runners, collector, num_tokens=100)  # capacity is 64
    cap = collector.fetch()
    assert cap["rows"] == 64
    assert cap["dropped_rows"] == [36] * NUM_LAYERS
    assert cap["ids"].shape == (64, NUM_LAYERS, TOP_K)
    assert cap["raw_logits_sample"].shape == (16, NUM_LAYERS, NUM_EXPERTS)
    # Identity checks still cover the dropped rows.
    assert cap["dispatch_calls"] == [100] * NUM_LAYERS
    assert cap["id_mismatch"] == [0] * NUM_LAYERS


def test_dispatch_mismatch_is_detected():
    runners = [FakeMoERunner(layer_id=0)]
    collector = RouterTelemetryCollector(num_experts=NUM_EXPERTS, top_k=TOP_K)
    install_router_telemetry(runners, collector)
    collector.enabled = True
    router = runners[0].router
    routed = runners[0].routed_experts
    x = torch.randn((1, HIDDEN))
    logits = torch.randn((1, NUM_EXPERTS))
    weights, ids = router.select_experts(hidden_states=x, router_logits=logits)
    tampered = ids.clone()
    tampered[0, 0] = (int(tampered[0, 0]) + 1) % NUM_EXPERTS
    routed.forward_modular(x=x, topk_weights=weights * 0.5, topk_ids=tampered)
    cap = collector.fetch()
    assert cap["id_mismatch"][0] >= 1
    assert cap["weight_maxdiff"][0] > 0.0


def test_summary_vs_raw_tie_equivalence():
    """A k-boundary tie (8th and 9th expert with equal probability) may be
    broken differently by the kernel and the recompute; the mass-equivalence
    criterion must accept it, while a genuinely wrong id must fail."""
    rows, L = 1, 1
    logits = np.zeros((rows, L, NUM_EXPERTS), dtype=np.float64)
    logits[0, 0, :TOP_K + 1] = 5.0          # experts 0..4 tied at the boundary
    probs = np.exp(logits[0, 0] - logits[0, 0].max())
    probs /= probs.sum()
    tied = list(range(TOP_K + 1))
    ent = float(-(probs * np.log(np.clip(probs, 1e-12, None))).sum())
    mass = float(probs[tied[:TOP_K]].sum())

    def capture_with(ids_row):
        w = probs[ids_row]
        return {
            "top_k": TOP_K,
            "raw_logits_sample": logits.copy(),
            "ids": np.array([[ids_row]]),
            "weights": (w / w.sum()).reshape(1, 1, TOP_K),
            "entropy": np.array([[ent]]),
            "mass": np.array([[mass]]),
        }

    # Kernel picked experts 1..K (skipping 0), recompute picks 0..K-1: tie.
    tie_check = summary_vs_raw_check(capture_with(tied[1:TOP_K + 1]))
    assert tie_check["passed"], tie_check
    assert tie_check["id_exact_mismatch_rowlayers"] == 1

    # A non-tied expert (prob ~uniform tail) in the set must fail.
    wrong = tied[:TOP_K - 1] + [NUM_EXPERTS - 1]
    wrong_check = summary_vs_raw_check(capture_with(wrong))
    assert not wrong_check["passed"]


def test_inference_mode_capture_then_reset_outside():
    """Regression: capture runs inside torch.inference_mode (as in vLLM's
    forward), while reset()/fetch() are called outside it via RPC. With
    eager allocation this must not raise the inference-tensor error."""
    runners = [FakeMoERunner(layer_id=i) for i in range(NUM_LAYERS)]
    collector = RouterTelemetryCollector(
        num_experts=NUM_EXPERTS, top_k=TOP_K,
        capacity_tokens=32, raw_sample_tokens=8,
    )
    install_router_telemetry(runners, collector)
    collector.allocate("cpu")
    collector.enabled = True
    with torch.inference_mode():
        run_tokens(runners, collector, num_tokens=5)
    cap = collector.fetch()
    assert cap["rows"] == 5
    collector.reset()          # raised before the eager-allocation fix
    cap2 = collector.fetch()
    assert cap2["rows"] == 0
    with torch.inference_mode():
        run_tokens(runners, collector, num_tokens=3)
    assert collector.fetch()["rows"] == 3


def test_summary_path_equals_raw_router_features():
    """M36C equivalence gate at unit level: the collector's device-side
    summarize() must match the numpy router_features recompute from the
    same buffers within 1e-5 per feature."""
    import m36_calibration as C

    runners = [FakeMoERunner(layer_id=i) for i in range(NUM_LAYERS)]
    collector = RouterTelemetryCollector(
        num_experts=NUM_EXPERTS, top_k=TOP_K,
        capacity_tokens=64, raw_sample_tokens=4,
    )
    install_router_telemetry(runners, collector)
    collector.allocate("cpu")
    collector.enabled = True
    run_tokens(runners, collector, num_tokens=6, tokens_per_call=6)  # prefill
    run_tokens(runners, collector, num_tokens=17, seed=5)            # decode
    prompt_rows = 6

    summary = collector.summarize(prompt_rows)
    cap = collector.fetch()
    cap = {**cap,
           "ids": cap["ids"].astype(np.int64),
           "weights": cap["weights"].astype(np.float64),
           "entropy": cap["entropy"].astype(np.float64),
           "mass": cap["mass"].astype(np.float64)}
    raw = C.router_features(cap, prompt_rows)
    for name in C.ROUTER_FEATURE_NAMES:
        assert abs(summary[name] - raw[name]) <= 1e-5, (
            name, summary[name], raw[name])
    assert summary["rows"] == 23
    # Bounded return: scalars only, no arrays.
    assert all(isinstance(v, (int, float)) for v in summary.values())


def test_aggregate_only_report_guard():
    good = {
        "schema_version": 1,
        "gates": {"observation_parity": True, "dispatch_identity": True},
        "telemetry": {"weight_maxdiff_max": 0.0, "entropy_maxdev": 1.2e-5},
        "tokens_per_second": 30.2,
        "notes": "aggregate gates/metrics only; outputs private",
    }
    assert_aggregate_only(good)

    with pytest.raises(PrivacyViolation):
        assert_aggregate_only({"prompt": "what is 2+2"})
    with pytest.raises(PrivacyViolation):
        assert_aggregate_only({"token_ids": [1, 2, 3]})
    with pytest.raises(PrivacyViolation):
        assert_aggregate_only({"stats": {"topk_experts": [4, 9, 11, 30]}})
    with pytest.raises(PrivacyViolation):
        assert_aggregate_only({"trace": list(range(64))})
    with pytest.raises(PrivacyViolation):
        assert_aggregate_only({"model_dir": "/mnt/some/local/path"})
    with pytest.raises(PrivacyViolation):
        assert_aggregate_only({"arr": np.zeros(4)})
    with pytest.raises(PrivacyViolation):
        assert_aggregate_only({"raw_logits_sample": 3})
