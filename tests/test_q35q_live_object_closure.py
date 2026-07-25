import importlib.machinery
import sys
import types
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from q35q_live_object_closure import (
    ADMITTED_MODULE_MEMBERS,
    EXPECTED_CONFIG_CLASSES,
    EXPECTED_MODEL_CLASSES,
    verify_live_object_closure,
)
from q35q_stage import Q35QStageBlock


def _install_module(monkeypatch, tmp_path, name, source):
    path = tmp_path / ADMITTED_MODULE_MEMBERS[name]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(source, encoding="utf-8")
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__spec__ = importlib.machinery.ModuleSpec(name, loader=None, origin=str(path))
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(source, str(path), "exec"), module.__dict__)
    return module, str(path)


def live_fixture(monkeypatch, tmp_path):
    cm, cm_path = _install_module(
        monkeypatch,
        tmp_path,
        "transformers.conversion_mapping",
        "def get_checkpoint_conversion_mapping(model_type):\n    return []\n",
    )
    core, core_path = _install_module(
        monkeypatch,
        tmp_path,
        "transformers.core_model_loading",
        "class PrefixChange:\n"
        "    def __init__(self): self.operations = []\n"
        "class WeightConverter:\n"
        "    def __init__(self, operations=None): self.operations = operations or []\n"
        "class MergeModulelist:\n    pass\n"
        "class Concatenate:\n    pass\n",
    )
    model_source = "\n".join(f"class {name}:\n    pass" for name in EXPECTED_MODEL_CLASSES) + "\n"
    modeling, modeling_path = _install_module(
        monkeypatch,
        tmp_path,
        "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe",
        model_source,
    )
    config_source = "\n".join(f"class {name}:\n    pass" for name in EXPECTED_CONFIG_CLASSES) + "\n"
    config, config_path = _install_module(
        monkeypatch,
        tmp_path,
        "transformers.models.qwen3_5_moe.configuration_qwen3_5_moe",
        config_source,
    )
    converters = [
        core.PrefixChange(),
        core.WeightConverter([core.MergeModulelist(), core.Concatenate()]),
        core.WeightConverter([core.MergeModulelist()]),
    ]
    return {
        "dispatch_callable": cm.get_checkpoint_conversion_mapping,
        "converters": converters,
        "model_classes": {name: getattr(modeling, name) for name in EXPECTED_MODEL_CLASSES},
        "config_classes": {name: getattr(config, name) for name in EXPECTED_CONFIG_CLASSES},
        "expected_module_paths": {
            "transformers.conversion_mapping": cm_path,
            "transformers.core_model_loading": core_path,
            "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe": modeling_path,
            "transformers.models.qwen3_5_moe.configuration_qwen3_5_moe": config_path,
        },
    }


def test_live_closure_passes(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    out = verify_live_object_closure(**fixture)
    assert out["live_object_closure_pass"] is True
    assert out["source_member_count"] == 4
    assert out["converter_count"] == 3
    assert out["nested_operation_count"] == 3


def test_incomplete_expected_module_map_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    fixture["expected_module_paths"].pop("transformers.core_model_loading")
    with pytest.raises(Q35QStageBlock, match="exact admitted closure"):
        verify_live_object_closure(**fixture)


def test_extra_expected_module_map_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    fixture["expected_module_paths"]["transformers.decoy"] = "/tmp/decoy.py"
    with pytest.raises(Q35QStageBlock, match="exact admitted closure"):
        verify_live_object_closure(**fixture)


def test_dispatch_module_export_identity_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    original = fixture["dispatch_callable"]
    module = sys.modules[original.__module__]
    module.get_checkpoint_conversion_mapping = lambda model_type: []
    with pytest.raises(Q35QStageBlock, match="identity differs"):
        verify_live_object_closure(**fixture)


def test_forged_dispatch_identity_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)

    def forged(model_type):
        return []

    forged.__module__ = "transformers.conversion_mapping"
    forged.__name__ = "get_checkpoint_conversion_mapping"
    forged.__qualname__ = "get_checkpoint_conversion_mapping"
    fixture["dispatch_callable"] = forged
    with pytest.raises(Q35QStageBlock, match="identity differs"):
        verify_live_object_closure(**fixture)


def test_module_spec_origin_mismatch_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    module = sys.modules["transformers.core_model_loading"]
    module.__spec__ = importlib.machinery.ModuleSpec(
        module.__name__, loader=None, origin=str(tmp_path / "shadow.py")
    )
    with pytest.raises(Q35QStageBlock, match="source origins disagree"):
        verify_live_object_closure(**fixture)


def test_expected_path_mismatch_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    fixture["expected_module_paths"]["transformers.core_model_loading"] = str(tmp_path / "wrong.py")
    with pytest.raises(Q35QStageBlock, match="source origins disagree"):
        verify_live_object_closure(**fixture)


def test_unadmitted_nested_operation_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)

    class ForeignOperation:
        pass

    fixture["converters"][1].operations.append(ForeignOperation())
    with pytest.raises(Q35QStageBlock, match="unadmitted module"):
        verify_live_object_closure(**fixture)


def test_missing_model_class_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    fixture["model_classes"].pop(EXPECTED_MODEL_CLASSES[0])
    with pytest.raises(Q35QStageBlock, match="model class set"):
        verify_live_object_closure(**fixture)


def test_replaced_config_class_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    name = EXPECTED_CONFIG_CLASSES[0]
    original = fixture["config_classes"][name]
    replacement = type(name, (), {})
    replacement.__module__ = original.__module__
    fixture["config_classes"][name] = replacement
    with pytest.raises(Q35QStageBlock, match="identity differs"):
        verify_live_object_closure(**fixture)


def test_converter_without_sequence_operations_fails(monkeypatch, tmp_path):
    fixture = live_fixture(monkeypatch, tmp_path)
    fixture["converters"][1].operations = object()
    with pytest.raises(Q35QStageBlock, match="operations are not a sequence"):
        verify_live_object_closure(**fixture)
