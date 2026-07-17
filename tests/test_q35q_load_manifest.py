"""Q35Q load-manifest / loader-transformation tests (CPU-only, no model/network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import pytest

from q35q_stage import Q35QStageBlock
from q35q_load_manifest import classify_expert_representation, load_manifest_verdict


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


def test_verdict_blocked_when_reprs_differ_no_hook():
    v = load_manifest_verdict(source_repr="packed", artifact_repr="numbered", conversion_hook_present=False)
    assert v["strictly_loadable"] is False and v["outcome"] == "q35q_load_manifest_blocked"
    assert v["representations_match"] is False and v["blocker"]


def test_verdict_ok_when_reprs_match():
    v = load_manifest_verdict(source_repr="numbered", artifact_repr="numbered", conversion_hook_present=False)
    assert v["strictly_loadable"] is True and v["outcome"] == "q35q_phase0_load_manifest_candidate_ok"


def test_verdict_ok_when_conversion_hook_present():
    v = load_manifest_verdict(source_repr="packed", artifact_repr="numbered", conversion_hook_present=True)
    assert v["strictly_loadable"] is True


def test_verdict_unknown_repr_fails():
    with pytest.raises(Q35QStageBlock, match="could not classify"):
        load_manifest_verdict(source_repr="unknown", artifact_repr="numbered", conversion_hook_present=False)
