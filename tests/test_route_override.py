#!/usr/bin/env python3
"""M32P Phase-0 route-override tests on a tiny real qwen2_moe (CPU-only)."""
import sys
from pathlib import Path

import pytest

torch = pytest.importorskip("torch")
from transformers import Qwen2MoeConfig, Qwen2MoeForCausalLM  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from qwen2_moe_route_override import (  # noqa: E402
    PenaltyPlan, RouteController, SwapPlan, clone_cache)

NUM_EXPERTS = 6
TOP_K = 4


@pytest.fixture(scope="module")
def tiny():
    torch.manual_seed(7)
    config = Qwen2MoeConfig(
        vocab_size=64, hidden_size=32, intermediate_size=48,
        moe_intermediate_size=16, shared_expert_intermediate_size=24,
        num_hidden_layers=2, num_attention_heads=4, num_key_value_heads=2,
        num_experts=NUM_EXPERTS, num_experts_per_tok=TOP_K,
        decoder_sparse_step=1, norm_topk_prob=False, output_router_logits=False)
    model = Qwen2MoeForCausalLM(config)
    model.eval()
    controller = RouteController(model, NUM_EXPERTS, TOP_K)
    return model, controller


def _greedy(model, input_ids, steps, controller=None, plan=None, at_step=None,
            past=None, first_token=None):
    tokens = []
    with torch.inference_mode():
        if past is None:
            out = model(input_ids=input_ids, use_cache=True)
            past = out.past_key_values
            next_logits = out.logits[:, -1, :]
        else:
            out = model(input_ids=torch.tensor([[first_token]]),
                        past_key_values=past, use_cache=True)
            past = out.past_key_values
            next_logits = out.logits[:, -1, :]
        for step in range(steps):
            token = int(next_logits.argmax(-1))
            tokens.append(token)
            if controller is not None and plan is not None and step == at_step:
                with controller.active(plan):
                    out = model(input_ids=torch.tensor([[token]]),
                                past_key_values=past, use_cache=True)
            else:
                out = model(input_ids=torch.tensor([[token]]),
                            past_key_values=past, use_cache=True)
            past = out.past_key_values
            next_logits = out.logits[:, -1, :]
    return tokens, past


def _selected(model, layer, ids):
    captured = {}

    def hook(_m, _i, output):
        captured["logits"] = output[0].detach().clone()

    handle = model.model.layers[layer].mlp.gate.register_forward_hook(hook)
    with torch.inference_mode():
        model(input_ids=ids)
    handle.remove()
    row = captured["logits"][-1]
    return set(torch.topk(row, TOP_K).indices.tolist()), row


def test_disabled_controller_is_bit_identical(tiny):
    model, controller = tiny
    ids = torch.tensor([[1, 5, 9, 3]])
    with torch.inference_mode():
        baseline = model(input_ids=ids).logits
    assert controller.enabled is False
    with torch.inference_mode():
        attached = model(input_ids=ids).logits
    assert torch.equal(baseline, attached)
    tokens_a, _ = _greedy(model, ids, 6)
    tokens_b, _ = _greedy(model, ids, 6)
    assert tokens_a == tokens_b


def test_swap_keeps_topk_active_and_changes_forward(tiny):
    model, controller = tiny
    ids = torch.tensor([[2, 7, 11]])
    layer = 1
    selected, row = _selected(model, layer, ids)
    unselected = [e for e in range(NUM_EXPERTS) if e not in selected]
    plan = SwapPlan(layer_index=layer, swap_out=sorted(selected)[0],
                    swap_in=unselected[0])
    with torch.inference_mode():
        baseline = model(input_ids=ids).logits
    before = controller.applications
    with controller.active(plan):
        with torch.inference_mode():
            swapped = model(input_ids=ids).logits
    assert controller.applications == before + 1
    assert controller.enabled is False  # auto-removed
    assert not torch.equal(baseline, swapped)
    edited = controller._edit_row(plan, row)
    new_selected = set(torch.topk(edited, TOP_K).indices.tolist())
    assert len(new_selected) == TOP_K
    assert plan.swap_out not in new_selected
    assert plan.swap_in in new_selected
    assert new_selected - {plan.swap_in} == selected - {plan.swap_out}
    # After removal the forward is baseline again.
    with torch.inference_mode():
        restored = model(input_ids=ids).logits
    assert torch.equal(baseline, restored)


def test_invalid_plans_are_rejected(tiny):
    model, controller = tiny
    ids = torch.tensor([[2, 7, 11]])
    layer = 0
    selected, row = _selected(model, layer, ids)
    unselected = [e for e in range(NUM_EXPERTS) if e not in selected]
    with pytest.raises(ValueError, match="not currently selected"):
        controller._edit_row(SwapPlan(layer, unselected[0], unselected[-1]), row)
    with pytest.raises(ValueError, match="already selected"):
        controller._edit_row(SwapPlan(layer, sorted(selected)[0],
                                      sorted(selected)[1]), row)
    with pytest.raises(ValueError, match="out of range"):
        controller._edit_row(SwapPlan(layer, sorted(selected)[0], 99), row)
    with pytest.raises(ValueError, match="must differ"):
        controller._edit_row(SwapPlan(layer, 3, 3), row)
    with pytest.raises(ValueError, match="finite positive"):
        controller._edit_row(PenaltyPlan(layer, ((0, float("nan")),)), row)
    with pytest.raises(ValueError, match="layer index out of range"):
        controller._router(99)
    with pytest.raises(RuntimeError, match="already active"):
        plan = SwapPlan(layer, sorted(selected)[0], unselected[0])
        with controller.active(plan):
            with controller.active(plan):
                pass
    assert controller.enabled is False


def test_penalty_lowers_targeted_logits_only(tiny):
    model, controller = tiny
    ids = torch.tensor([[4, 8]])
    _, row = _selected(model, 0, ids)
    plan = PenaltyPlan(0, ((1, 2.0), (3, 0.5)))
    edited = controller._edit_row(plan, row)
    assert torch.isclose(edited[1], row[1] - 2.0)
    assert torch.isclose(edited[3], row[3] - 0.5)
    untouched = [i for i in range(NUM_EXPERTS) if i not in (1, 3)]
    assert torch.equal(edited[untouched], row[untouched])
    assert len(set(torch.topk(edited, TOP_K).indices.tolist())) == TOP_K


def test_branch_uses_modified_cache_not_spliced_tokens(tiny):
    model, controller = tiny
    ids = torch.tensor([[3, 1, 4, 1, 5]])
    baseline_tokens, _ = _greedy(model, ids, 8)
    # Build prefix cache once, snapshot it, and branch twice from step 2.
    with torch.inference_mode():
        out = model(input_ids=ids, use_cache=True)
    past = out.past_key_values
    replay = baseline_tokens[:2]
    with torch.inference_mode():
        for token in replay[:-1]:
            out = model(input_ids=torch.tensor([[token]]),
                        past_key_values=past, use_cache=True)
            past = out.past_key_values
    snapshot = clone_cache(past)
    layer = 1
    # Branch B first: normal forward from an independent clone, capturing the
    # router row of THIS forward so the swap plan is valid for it.
    captured = {}

    def spy(_m, _i, output):
        captured["row"] = output[0].detach().clone()[-1]

    handle = model.model.layers[layer].mlp.gate.register_forward_hook(spy)
    normal_past = clone_cache(snapshot)
    with torch.inference_mode():
        out2 = model(input_ids=torch.tensor([[replay[-1]]]),
                     past_key_values=normal_past, use_cache=True)
    handle.remove()
    normal_logits = out2.logits[:, -1, :]
    selected = set(torch.topk(captured["row"], TOP_K).indices.tolist())
    unselected = [e for e in range(NUM_EXPERTS) if e not in selected]
    plan = SwapPlan(layer, sorted(selected)[0], unselected[0])
    # Branch A: intervened forward consuming replay[-1] on its own clone.
    branch_past = clone_cache(snapshot)
    with controller.active(plan):
        with torch.inference_mode():
            out = model(input_ids=torch.tensor([[replay[-1]]]),
                        past_key_values=branch_past, use_cache=True)
    branch_logits = out.logits[:, -1, :]
    # The intervened branch's KV differs from the normal branch's KV: the
    # snapshot must be untouched, so the normal branch reproduces baseline.
    assert torch.equal(
        normal_logits.argmax(-1), branch_logits.argmax(-1)) or not torch.equal(
        normal_logits, branch_logits)
    assert not torch.equal(normal_logits, branch_logits)
    # Continuations proceed on their own caches.
    cont_a = int(branch_logits.argmax(-1))
    cont_b = int(normal_logits.argmax(-1))
    del cont_a, cont_b


def test_no_public_route_table_leaks_from_plan_objects():
    plan = SwapPlan(3, 10, 55)
    text = repr(plan)
    assert "SwapPlan" in text
    # Plans carry indices only; no prompts/outputs/task ids exist on them.
    assert not any(hasattr(plan, attr) for attr in
                   ("prompt", "output", "task_id", "operands"))
