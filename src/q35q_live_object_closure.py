"""Fail-closed live-object source closure for Q35Q Transformers provenance.

The closure is derived from the objects actually used by the live conversion path,
not from caller-constructed source filenames. Every function/class must resolve back
to the same object through its declaring module and must agree with the module's
``__file__`` and ``__spec__.origin``. The exact admitted four-file Transformers
closure is enforced; the future GPTQModel/Defuser loader closure remains separate.
"""
from __future__ import annotations

import inspect
import os
import sys
from collections.abc import Mapping, Sequence

from q35q_stage import Q35QStageBlock

ADMITTED_MODULE_MEMBERS = {
    "transformers.conversion_mapping": "transformers/conversion_mapping.py",
    "transformers.core_model_loading": "transformers/core_model_loading.py",
    "transformers.models.qwen3_5_moe.configuration_qwen3_5_moe": (
        "transformers/models/qwen3_5_moe/configuration_qwen3_5_moe.py"
    ),
    "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe": (
        "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py"
    ),
}
EXPECTED_DISPATCH = (
    "transformers.conversion_mapping",
    "get_checkpoint_conversion_mapping",
)
EXPECTED_MODEL_CLASSES = (
    "Qwen3_5MoeForConditionalGeneration",
    "Qwen3_5MoeForCausalLM",
    "Qwen3_5MoeTextModel",
)
EXPECTED_CONFIG_CLASSES = (
    "Qwen3_5MoeConfig",
    "Qwen3_5MoeTextConfig",
    "Qwen3_5MoeVisionConfig",
)


def _canonical(path: str) -> str:
    if not isinstance(path, str) or not path:
        raise Q35QStageBlock("source path missing")
    return os.path.normcase(os.path.realpath(path))


def _resolve_qualname(module, qualname: str):
    if not isinstance(qualname, str) or not qualname or "<locals>" in qualname:
        raise Q35QStageBlock("object qualname is not import-resolvable")
    current = module
    for part in qualname.split("."):
        if part == "<locals>" or not hasattr(current, part):
            raise Q35QStageBlock("object qualname is not present in declaring module")
        current = getattr(current, part)
    return current


def _target_for_object(obj):
    if inspect.isfunction(obj) or inspect.isclass(obj):
        return obj
    return type(obj)


def _inspect_object(label: str, obj, expected_module_paths: Mapping[str, str]) -> dict:
    target = _target_for_object(obj)
    module_name = getattr(target, "__module__", None)
    qualname = getattr(target, "__qualname__", None)
    if module_name not in ADMITTED_MODULE_MEMBERS:
        raise Q35QStageBlock(f"{label} originates from an unadmitted module")
    module = sys.modules.get(module_name)
    if module is None:
        raise Q35QStageBlock(f"{label} declaring module is not loaded")
    if _resolve_qualname(module, qualname) is not target:
        raise Q35QStageBlock(f"{label} identity differs from declaring module export")

    expected_path = _canonical(expected_module_paths[module_name])
    module_file = _canonical(getattr(module, "__file__", None))
    spec = getattr(module, "__spec__", None)
    spec_origin = _canonical(getattr(spec, "origin", None)) if spec is not None else None
    if spec_origin is None:
        raise Q35QStageBlock(f"{label} module has no canonical import spec origin")
    try:
        inspected_file = inspect.getsourcefile(target) or inspect.getfile(target)
    except (OSError, TypeError) as exc:
        raise Q35QStageBlock(f"{label} source file is not inspectable") from exc
    inspected_path = _canonical(inspected_file)
    if not (module_file == spec_origin == inspected_path == expected_path):
        raise Q35QStageBlock(f"{label} source origins disagree")

    return {
        "label": label,
        "module": module_name,
        "qualname": qualname,
        "member": ADMITTED_MODULE_MEMBERS[module_name],
    }


def _require_named_classes(
    classes: Mapping[str, object],
    expected_names: Sequence[str],
    expected_module: str,
    kind: str,
) -> None:
    if not isinstance(classes, Mapping):
        raise Q35QStageBlock(f"{kind} classes must be a mapping")
    if set(classes) != set(expected_names):
        raise Q35QStageBlock(f"{kind} class set does not match the frozen closure")
    for name, cls in classes.items():
        if not inspect.isclass(cls):
            raise Q35QStageBlock(f"{kind} object {name} is not a class")
        if cls.__name__ != name or cls.__module__ != expected_module:
            raise Q35QStageBlock(f"{kind} class {name} identity mismatch")


def verify_live_object_closure(
    *,
    dispatch_callable,
    converters: Sequence[object],
    model_classes: Mapping[str, object],
    config_classes: Mapping[str, object],
    expected_module_paths: Mapping[str, str],
) -> dict:
    """Verify the exact live Transformers-side source closure.

    This function deliberately does not accept observed module names, qualnames, or
    source paths independently from the objects. It derives those identities from the
    live objects and requires object-export identity plus source-origin agreement.
    """
    if set(expected_module_paths) != set(ADMITTED_MODULE_MEMBERS):
        raise Q35QStageBlock("expected module-path map is not the exact admitted closure")
    if not isinstance(converters, Sequence) or isinstance(converters, (str, bytes)) or not converters:
        raise Q35QStageBlock("live converter sequence is missing")

    dispatch_module, dispatch_name = EXPECTED_DISPATCH
    if (
        not inspect.isfunction(dispatch_callable)
        or dispatch_callable.__module__ != dispatch_module
        or dispatch_callable.__name__ != dispatch_name
        or dispatch_callable.__qualname__ != dispatch_name
    ):
        raise Q35QStageBlock("dispatch callable identity mismatch")

    _require_named_classes(
        model_classes,
        EXPECTED_MODEL_CLASSES,
        "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe",
        "model",
    )
    _require_named_classes(
        config_classes,
        EXPECTED_CONFIG_CLASSES,
        "transformers.models.qwen3_5_moe.configuration_qwen3_5_moe",
        "configuration",
    )

    observed = [_inspect_object("dispatch", dispatch_callable, expected_module_paths)]
    operation_count = 0
    for index, converter in enumerate(converters):
        observed.append(
            _inspect_object(f"converter[{index}]", converter, expected_module_paths)
        )
        operations = getattr(converter, "operations", None) or []
        if isinstance(operations, (str, bytes)) or not isinstance(operations, Sequence):
            raise Q35QStageBlock("converter operations are not a sequence")
        for op_index, operation in enumerate(operations):
            observed.append(
                _inspect_object(
                    f"converter[{index}].operations[{op_index}]",
                    operation,
                    expected_module_paths,
                )
            )
            operation_count += 1

    for name, cls in model_classes.items():
        observed.append(_inspect_object(f"model.{name}", cls, expected_module_paths))
    for name, cls in config_classes.items():
        observed.append(_inspect_object(f"config.{name}", cls, expected_module_paths))

    modules = {item["module"] for item in observed}
    members = {item["member"] for item in observed}
    if modules != set(ADMITTED_MODULE_MEMBERS):
        raise Q35QStageBlock("live objects do not span the exact admitted module closure")
    if members != set(ADMITTED_MODULE_MEMBERS.values()):
        raise Q35QStageBlock("live objects do not span the exact admitted source closure")

    return {
        "live_object_closure_pass": True,
        "source_member_count": len(members),
        "unique_module_count": len(modules),
        "converter_count": len(converters),
        "nested_operation_count": operation_count,
        "model_class_count": len(model_classes),
        "config_class_count": len(config_classes),
        "object_observation_count": len(observed),
        "source_members": sorted(members),
    }
