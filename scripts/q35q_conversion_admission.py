#!/usr/bin/env python3
"""Q35Q Phase-0 live conversion/source/dispatch admission adapter (CPU-only).

Committed production path per
``docs/STEER_ADDENDUM_2026-07-17_Q35Q_RUNTIME_COMPOSITION_PROVENANCE_CORRECTION.md``.
The adapter obtains identities from the installed runtime rather than accepting
caller-supplied observations. It now additionally binds the imported Transformers
package to one installed wheel-style distribution through ``distribution()``, the
canonical package/dist-info roots, METADATA, WHEEL, RECORD, declared files, and
RECORD-verified bytes.

This remains a partial admission. Independent upstream-wheel extraction, complete
live-object source closure, clean-subprocess isolation, and the actual frozen
GPTQModel/Defuser loader still have to be composed in the same conjunction.
Aggregate-only output: versions, booleans, counts, and public source-digest prefixes.

usage: q35q_conversion_admission.py <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import PurePosixPath
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from q35q_dispatch_conversion import extract_mapping, verify_dispatch_conversion  # noqa: E402
from q35q_distribution_ownership import verify_distribution_ownership  # noqa: E402

EXPECTED_VERSION = "5.13.1"
EXPECTED_DISTRIBUTION = "transformers"
EXPECTED_PACKAGE_INIT_MEMBER = "transformers/__init__.py"
EXPECTED_CONVERSION_MODULE = "transformers.core_model_loading"
PINNED = (
    "transformers/conversion_mapping.py",
    "transformers/core_model_loading.py",
    "transformers/models/qwen3_5_moe/configuration_qwen3_5_moe.py",
    "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py",
)


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def _sha(path: str) -> str:
    return hashlib.sha256(_read_bytes(path)).hexdigest()


def _find_dist_info_member(declared_files: tuple[str, ...], basename: str) -> str:
    matches = [
        value
        for value in declared_files
        if value.endswith(f".dist-info/{basename}")
        and not value.startswith("../")
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"installed distribution does not declare exactly one {basename}"
        )
    return matches[0]


def _canonical_declared_files(distribution) -> tuple[str, ...]:
    files = distribution.files
    if files is None:
        raise RuntimeError("installed distribution has no declared-file list")
    return tuple(str(value).replace(os.sep, "/") for value in files)


def _distribution_ownership(distribution, transformers, source_paths: dict[str, str]) -> dict:
    declared_files = _canonical_declared_files(distribution)
    metadata_member = _find_dist_info_member(declared_files, "METADATA")
    dist_info_member = str(PurePosixPath(metadata_member).parent)
    dist_info_dir = os.path.realpath(str(distribution.locate_file(dist_info_member)))
    root = os.path.realpath(str(distribution.locate_file("")))
    wheel_member = f"{dist_info_member}/WHEEL"
    record_member = f"{dist_info_member}/RECORD"
    metadata_path = os.path.realpath(str(distribution.locate_file(metadata_member)))
    wheel_path = os.path.realpath(str(distribution.locate_file(wheel_member)))
    record_path = os.path.realpath(str(distribution.locate_file(record_member)))
    package_init_path = os.path.realpath(transformers.__file__)

    member_bytes = {
        EXPECTED_PACKAGE_INIT_MEMBER: _read_bytes(package_init_path),
        **{member: _read_bytes(path) for member, path in source_paths.items()},
        metadata_member: _read_bytes(metadata_path),
        wheel_member: _read_bytes(wheel_path),
    }
    direct_url_path = os.path.join(dist_info_dir, "direct_url.json")
    direct_url_text = None
    if os.path.exists(direct_url_path):
        direct_url_text = _read_bytes(direct_url_path).decode("utf-8")

    return verify_distribution_ownership(
        observed_name=distribution.metadata.get("Name", ""),
        observed_version=distribution.version,
        expected_name=EXPECTED_DISTRIBUTION,
        expected_version=EXPECTED_VERSION,
        distribution_root=root,
        dist_info_dir=dist_info_dir,
        imported_package_init=package_init_path,
        expected_package_init_member=EXPECTED_PACKAGE_INIT_MEMBER,
        required_source_members=PINNED,
        declared_files=declared_files,
        record_text=_read_bytes(record_path).decode("utf-8"),
        metadata_text=member_bytes[metadata_member].decode("utf-8"),
        wheel_text=member_bytes[wheel_member].decode("utf-8"),
        member_bytes=member_bytes,
        upstream_source_digests=None,
        direct_url_text=direct_url_text,
    )


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: q35q_conversion_admission.py <out_json>")
    out = sys.argv[1]
    import importlib.metadata as md
    import transformers
    import transformers.conversion_mapping as cm

    distribution = md.distribution(EXPECTED_DISTRIBUTION)
    version = distribution.version
    pkg_root = os.path.realpath(os.path.dirname(transformers.__file__))
    source_paths = {
        "transformers/conversion_mapping.py": os.path.realpath(cm.__file__),
        "transformers/core_model_loading.py": os.path.realpath(
            os.path.join(pkg_root, "core_model_loading.py")
        ),
        "transformers/models/qwen3_5_moe/configuration_qwen3_5_moe.py": os.path.realpath(
            os.path.join(
                pkg_root,
                "models",
                "qwen3_5_moe",
                "configuration_qwen3_5_moe.py",
            )
        ),
        "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py": os.path.realpath(
            os.path.join(
                pkg_root,
                "models",
                "qwen3_5_moe",
                "modeling_qwen3_5_moe.py",
            )
        ),
    }
    contained = all(
        path.startswith(pkg_root + os.sep) for path in source_paths.values()
    )
    exact_file_set = set(source_paths) == set(PINNED)
    digests = {
        member: _sha(path)
        for member, path in source_paths.items()
        if os.path.exists(path)
    }

    ownership = _distribution_ownership(distribution, transformers, source_paths)

    live = cm.get_checkpoint_conversion_mapping("qwen3_5_moe_text")
    extracted = extract_mapping(live)
    dispatch = verify_dispatch_conversion(extracted)
    top_level_class_modules_bound = all(
        type(obj).__module__ == EXPECTED_CONVERSION_MODULE for obj in live
    )

    installed_admission = (
        version == EXPECTED_VERSION
        and contained
        and exact_file_set
        and dispatch["dispatch_conversion_pass"]
        and top_level_class_modules_bound
        and len(digests) == len(PINNED)
        and ownership["distribution_ownership_pass"]
    )

    record = {
        "outcome": "q35q_provenance_blocked",
        "artifact_admission_status": "q35q_artifact_admission_blocked",
        "installed_runtime_admission": {
            "transformers_version_bound": version == EXPECTED_VERSION,
            "import_origin_contained_under_package_root": contained,
            "exact_pinned_file_set": exact_file_set,
            "source_bytes_hashed": len(digests) == len(PINNED),
            "live_dispatch_conversion_pass": dispatch[
                "dispatch_conversion_pass"
            ],
            "top_level_converter_class_modules_bound": (
                top_level_class_modules_bound
            ),
            "distribution_ownership": ownership,
            "installed_admission_pass": installed_admission,
            "conversion_source_sha256_prefixes": {
                member: digest[:16] for member, digest in digests.items()
            },
        },
        "independence_gate": {
            "expected_digests_independent": False,
            "blocker": (
                "independent upstream-wheel extraction, complete live-object "
                "source closure, clean-subprocess isolation, and loader binding "
                "are not yet composed in one process"
            ),
            "upstream_resolvable": (
                "transformers 5.13.1 frozen PyPI wheel identity is recorded"
            ),
        },
        "remaining": [
            "compose frozen upstream wheel verification and installed-byte equality in this clean-process adapter",
            "derive source closure from the live dispatch, converter, nested-operation, model, and config objects",
            "bind the actual GPTQModel/Defuser loader after freezing the runtime tuple",
            "then Phase-0 conjunction, weights, authorized GPU transition, exact parity",
        ],
        "boundary": {
            "gpu_used": False,
            "weights_loaded": False,
            "tensor_payload_fetched": False,
            "unrelated_gpu_tenant": "present_preserved",
        },
        "privacy": (
            "aggregate-only; versions + booleans + counts + public source-digest "
            "prefixes, no host paths"
        ),
    }
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
    print(
        json.dumps(
            {
                "outcome": record["outcome"],
                "installed_admission_pass": installed_admission,
                "distribution_ownership_pass": ownership[
                    "distribution_ownership_pass"
                ],
                "live_dispatch_conversion_pass": dispatch[
                    "dispatch_conversion_pass"
                ],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
