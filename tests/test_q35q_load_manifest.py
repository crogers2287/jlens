"""Q35Q load-manifest / loader-transformation tests (CPU-only, no model/network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_load_manifest import (
    classify_expert_representation,
    load_manifest_verdict,
    runtime_load_path_verdict,
)


def test_classify_numbered():
    assert classify_expert_representation(
        ["model.layers.0.mlp.experts.0.gate_proj.qweight",
         "model.layers.0.mlp.experts.255.down_proj.scales"]) == "numbered"


def test_classify_packed():
    assert classify_expert_representation(
        ["model.layers.0.mlp.experts.gate_up_proj", "model.layers.0.mlp.experts.down_proj"]) == "packed"


def test_classify_unknown():
    assert classify_expert_representation(["model.embed_tokens.weight"]) == "unknown"


def test_classify_ambiguous_fails():
    with pytest.raises(Q35QStageBlock, match="ambiguous expert representation"):
        classify_expert_representation(
            ["model.layers.0.mlp.experts.0.gate_proj", "model.layers.0.mlp.experts.gate_up_proj"])


def test_low_level_check_reports_reprs():
    v = load_manifest_verdict(source_repr="packed", artifact_repr="numbered", conversion_hook_present=False)
    assert v["representations_match"] is False and v["model_local_conversion_hook_present"] is False


# ---------- runtime path verdict (corrected model) ----------

def test_runtime_unresolved_when_conversion_present_no_gptq_stack():
    # the live case: loader-level conversion exists, GPTQ stack (optimum/gptqmodel) absent
    v = runtime_load_path_verdict(source_repr="packed", artifact_repr="numbered",
                                  model_local_hook_present=False, loader_conversion_present=True,
                                  gptq_loader_stack_present=False)
    assert v["outcome"] == "q35q_load_manifest_runtime_path_unresolved"


def test_runtime_candidate_when_conversion_and_gptq_stack():
    v = runtime_load_path_verdict(source_repr="packed", artifact_repr="numbered",
                                  model_local_hook_present=False, loader_conversion_present=True,
                                  gptq_loader_stack_present=True)
    assert v["outcome"] == "q35q_phase0_load_manifest_runtime_candidate"


def test_runtime_candidate_when_reprs_match():
    v = runtime_load_path_verdict(source_repr="numbered", artifact_repr="numbered",
                                  model_local_hook_present=False, loader_conversion_present=False,
                                  gptq_loader_stack_present=False)
    assert v["outcome"] == "q35q_phase0_load_manifest_runtime_candidate"


def test_runtime_blocked_when_no_conversion_and_reprs_differ():
    v = runtime_load_path_verdict(source_repr="packed", artifact_repr="numbered",
                                  model_local_hook_present=False, loader_conversion_present=False,
                                  gptq_loader_stack_present=False)
    assert v["outcome"] == "q35q_load_manifest_blocked"


def test_runtime_unknown_repr_fails():
    with pytest.raises(Q35QStageBlock, match="could not classify"):
        runtime_load_path_verdict(source_repr="unknown", artifact_repr="numbered",
                                  model_local_hook_present=False, loader_conversion_present=True,
                                  gptq_loader_stack_present=False)
