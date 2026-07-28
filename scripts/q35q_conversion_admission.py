#!/usr/bin/env python3
"""Q35Q Phase-0 Transformers provenance/dispatch admission adapter (CPU-only).

This adapter composes, in one isolated subprocess:

* exact PyPI metadata resolution for the frozen Transformers wheel;
* verified download and independent source-digest extraction from that wheel;
* installed wheel-distribution ownership through METADATA/WHEEL/RECORD;
* equality between upstream-derived and installed source bytes;
* live dispatch/converter/operation/model/configuration source closure.

The actual frozen GPTQModel/Defuser loader and immutable runtime tuple remain a
separate blocker. Aggregate-only output: public package identities, booleans,
counts, and public digest prefixes. No host paths are emitted.

usage: q35q_conversion_admission.py <out_json>
"""
from __future__ import annotations

import hashlib
import importlib
import json
import os
from pathlib import PurePosixPath
import site
import subprocess
import sys
from urllib.parse import urlparse
from urllib.request import Request, urlopen

_REPO_ROOT = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
_SRC_ROOT = os.path.join(_REPO_ROOT, "src")
if _SRC_ROOT not in sys.path:
    sys.path.insert(0, _SRC_ROOT)

from q35q_dispatch_conversion import extract_mapping, verify_dispatch_conversion  # noqa: E402
from q35q_distribution_ownership import verify_distribution_ownership  # noqa: E402
from q35q_live_object_closure import (  # noqa: E402
    ADMITTED_MODULE_MEMBERS,
    EXPECTED_CONFIG_CLASSES,
    EXPECTED_MODEL_CLASSES,
    verify_live_object_closure,
)
from q35q_stage import Q35QStageBlock  # noqa: E402
from q35q_upstream_provenance import (  # noqa: E402
    PINNED_UPSTREAM,
    compare_installed_to_upstream,
    verify_wheel_and_extract,
)

EXPECTED_VERSION = "5.13.1"
EXPECTED_DISTRIBUTION = "transformers"
EXPECTED_PACKAGE_INIT_MEMBER = "transformers/__init__.py"
EXPECTED_CONVERSION_MODULE = "transformers.core_model_loading"
PINNED = tuple(ADMITTED_MODULE_MEMBERS.values())
PYPI_JSON_URL = "https://pypi.org/pypi/transformers/5.13.1/json"
PYPI_METADATA_MAX_BYTES = 2 * 1024 * 1024
WHEEL_MAX_BYTES = 32 * 1024 * 1024
_ALLOWED_WHEEL_HOST = "files.pythonhosted.org"
_CHILD_ARG = "--isolated-child"


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as handle:
        return handle.read()


def _sha(path: str) -> str:
    return hashlib.sha256(_read_bytes(path)).hexdigest()


def _find_dist_info_member(declared_files: tuple[str, ...], basename: str) -> str:
    matches = [
        value
        for value in declared_files
        if value.endswith(f".dist-info/{basename}") and not value.startswith("../")
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


def _distribution_ownership(
    distribution,
    transformers,
    source_paths: dict[str, str],
    upstream_source_digests: dict[str, str],
) -> dict:
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
        upstream_source_digests=upstream_source_digests,
        direct_url_text=direct_url_text,
    )


def _module_path(module) -> str:
    spec = getattr(module, "__spec__", None)
    origin = getattr(spec, "origin", None) if spec is not None else None
    if not isinstance(origin, str) or not origin:
        raise RuntimeError(f"module {module.__name__} has no import-spec origin")
    return os.path.realpath(origin)


def _require_https_url(value: object, *, expected_host: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise Q35QStageBlock(f"{label} is not a nonempty URL")
    parsed = urlparse(value)
    try:
        port = parsed.port
    except ValueError as exc:
        raise Q35QStageBlock(f"{label} is outside the admitted HTTPS origin") from exc
    if (
        parsed.scheme != "https"
        or parsed.hostname != expected_host
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.query
        or parsed.fragment
    ):
        raise Q35QStageBlock(f"{label} is outside the admitted HTTPS origin")
    return value


def _select_pinned_wheel_url(metadata: object) -> str:
    if not isinstance(metadata, dict):
        raise Q35QStageBlock("PyPI release metadata is not an object")
    info = metadata.get("info")
    if not isinstance(info, dict) or info.get("version") != EXPECTED_VERSION:
        raise Q35QStageBlock("PyPI release metadata version is not the frozen version")
    urls = metadata.get("urls")
    if not isinstance(urls, list):
        raise Q35QStageBlock("PyPI release metadata has no URL list")
    matches = []
    for item in urls:
        if not isinstance(item, dict):
            continue
        if item.get("filename") != PINNED_UPSTREAM["wheel_name"]:
            continue
        digests = item.get("digests")
        if (
            item.get("packagetype") != "bdist_wheel"
            or item.get("python_version") != "py3"
            or item.get("yanked") is True
            or not isinstance(digests, dict)
            or digests.get("sha256") != PINNED_UPSTREAM["wheel_sha256"]
        ):
            raise Q35QStageBlock("PyPI wheel metadata disagrees with the frozen identity")
        url = _require_https_url(
            item.get("url"), expected_host=_ALLOWED_WHEEL_HOST, label="PyPI wheel URL"
        )
        if os.path.basename(urlparse(url).path) != PINNED_UPSTREAM["wheel_name"]:
            raise Q35QStageBlock("PyPI wheel URL filename disagrees with the frozen identity")
        matches.append(url)
    if len(matches) != 1:
        raise Q35QStageBlock("PyPI metadata does not identify exactly one frozen wheel")
    return matches[0]


def _bounded_fetch(
    url: str,
    *,
    expected_host: str,
    max_bytes: int,
    opener=urlopen,
) -> bytes:
    _require_https_url(url, expected_host=expected_host, label="requested URL")
    request = Request(url, headers={"User-Agent": "jlens-q35q-provenance/1"})
    try:
        response = opener(request, timeout=60)
    except Exception as exc:
        raise Q35QStageBlock("failed to retrieve frozen public provenance artifact") from exc
    try:
        final_url = response.geturl()
        _require_https_url(final_url, expected_host=expected_host, label="resolved URL")
        content_length = response.headers.get("Content-Length")
        if content_length is not None:
            if not content_length.isdecimal() or int(content_length) > max_bytes:
                raise Q35QStageBlock("retrieved provenance artifact exceeds the size bound")
        chunks = []
        total = 0
        while True:
            chunk = response.read(min(1024 * 1024, max_bytes - total + 1))
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise Q35QStageBlock("retrieved provenance artifact exceeds the size bound")
            chunks.append(chunk)
        return b"".join(chunks)
    finally:
        response.close()


def _fetch_upstream_wheel(opener=urlopen) -> tuple[bytes, dict[str, object]]:
    metadata_bytes = _bounded_fetch(
        PYPI_JSON_URL,
        expected_host="pypi.org",
        max_bytes=PYPI_METADATA_MAX_BYTES,
        opener=opener,
    )
    try:
        metadata = json.loads(metadata_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise Q35QStageBlock("PyPI release metadata is not valid UTF-8 JSON") from exc
    wheel_url = _select_pinned_wheel_url(metadata)
    wheel_bytes = _bounded_fetch(
        wheel_url,
        expected_host=_ALLOWED_WHEEL_HOST,
        max_bytes=WHEEL_MAX_BYTES,
        opener=opener,
    )
    return wheel_bytes, {
        "registry_metadata_bound": True,
        "wheel_filename_bound": True,
        "wheel_sha256_metadata_bound": True,
    }


def _compose_upstream_binding(
    wheel_bytes: bytes, installed_digests: dict[str, str]
) -> tuple[dict[str, str], dict[str, object]]:
    upstream_digests = verify_wheel_and_extract(
        wheel_bytes,
        PINNED_UPSTREAM["wheel_sha256"],
        PINNED,
    )
    binding = compare_installed_to_upstream(upstream_digests, installed_digests)
    return upstream_digests, binding


def _clean_process_verdict() -> dict[str, bool]:
    preimport_clear = not any(
        name == "transformers" or name.startswith("transformers.")
        for name in sys.modules
    )
    user_sites = site.getusersitepackages()
    if isinstance(user_sites, str):
        user_sites = [user_sites]
    canonical_user_sites = {
        os.path.realpath(value) for value in user_sites if isinstance(value, str) and value
    }
    canonical_sys_path = {
        os.path.realpath(value)
        for value in sys.path
        if isinstance(value, str) and value not in {"", "."}
    }
    checks = {
        "isolated_flag": bool(sys.flags.isolated),
        "ignore_environment_flag": bool(sys.flags.ignore_environment),
        "no_user_site_flag": bool(sys.flags.no_user_site),
        "safe_path_flag": bool(getattr(sys.flags, "safe_path", False)),
        "user_site_disabled": site.ENABLE_USER_SITE is False,
        "user_site_absent_from_sys_path": canonical_user_sites.isdisjoint(
            canonical_sys_path
        ),
        "transformers_not_preimported": preimport_clear,
        "src_root_is_exact": os.path.realpath(sys.path[0]) == _SRC_ROOT,
    }
    checks["clean_subprocess_pass"] = all(checks.values())
    return checks


def _isolated_environment() -> dict[str, str]:
    allowed = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "TEMP", "TMP")
    return {key: os.environ[key] for key in allowed if key in os.environ}


def _run_isolated_child(out: str) -> int:
    command = [
        sys.executable,
        "-I",
        "-s",
        "-E",
        os.path.realpath(__file__),
        _CHILD_ARG,
        out,
    ]
    completed = subprocess.run(command, env=_isolated_environment(), check=False)
    return int(completed.returncode)


def _run_child(out: str) -> None:
    clean_process = _clean_process_verdict()
    if not clean_process["clean_subprocess_pass"]:
        raise Q35QStageBlock(
            "Q35Q provenance adapter is not running in the admitted isolated process"
        )

    import importlib.metadata as md
    import transformers
    import transformers.conversion_mapping as cm

    module_objects = {
        "transformers.conversion_mapping": cm,
        "transformers.core_model_loading": importlib.import_module(
            "transformers.core_model_loading"
        ),
        "transformers.models.qwen3_5_moe.configuration_qwen3_5_moe": importlib.import_module(
            "transformers.models.qwen3_5_moe.configuration_qwen3_5_moe"
        ),
        "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe": importlib.import_module(
            "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe"
        ),
    }
    module_paths = {
        name: _module_path(module) for name, module in module_objects.items()
    }
    source_paths = {
        member: module_paths[module_name]
        for module_name, member in ADMITTED_MODULE_MEMBERS.items()
    }

    distribution = md.distribution(EXPECTED_DISTRIBUTION)
    version = distribution.version
    pkg_root = os.path.realpath(os.path.dirname(transformers.__file__))
    contained = all(path.startswith(pkg_root + os.sep) for path in source_paths.values())
    exact_file_set = set(source_paths) == set(PINNED)
    installed_digests = {
        member: _sha(path)
        for member, path in source_paths.items()
        if os.path.exists(path)
    }

    wheel_bytes, registry_binding = _fetch_upstream_wheel()
    upstream_digests, upstream_binding = _compose_upstream_binding(
        wheel_bytes, installed_digests
    )
    ownership = _distribution_ownership(
        distribution,
        transformers,
        source_paths,
        upstream_digests,
    )

    live = cm.get_checkpoint_conversion_mapping("qwen3_5_moe_text")
    extracted = extract_mapping(live)
    dispatch = verify_dispatch_conversion(extracted)
    top_level_class_modules_bound = all(
        type(obj).__module__ == EXPECTED_CONVERSION_MODULE for obj in live
    )

    modeling = module_objects[
        "transformers.models.qwen3_5_moe.modeling_qwen3_5_moe"
    ]
    configuration = module_objects[
        "transformers.models.qwen3_5_moe.configuration_qwen3_5_moe"
    ]
    live_closure = verify_live_object_closure(
        dispatch_callable=cm.get_checkpoint_conversion_mapping,
        converters=live,
        model_classes={name: getattr(modeling, name) for name in EXPECTED_MODEL_CLASSES},
        config_classes={
            name: getattr(configuration, name) for name in EXPECTED_CONFIG_CLASSES
        },
        expected_module_paths=module_paths,
    )

    transformers_provenance_pass = (
        version == EXPECTED_VERSION
        and contained
        and exact_file_set
        and dispatch["dispatch_conversion_pass"]
        and top_level_class_modules_bound
        and len(installed_digests) == len(PINNED)
        and registry_binding["registry_metadata_bound"]
        and upstream_binding["installed_bound_to_upstream"]
        and ownership["distribution_ownership_pass"]
        and live_closure["live_object_closure_pass"]
        and clean_process["clean_subprocess_pass"]
    )

    record = {
        "outcome": (
            "q35q_transformers_provenance_composed"
            if transformers_provenance_pass
            else "q35q_provenance_blocked"
        ),
        "artifact_admission_status": "q35q_artifact_admission_blocked",
        "transformers_provenance_composition": {
            "clean_process": clean_process,
            "registry_binding": registry_binding,
            "upstream_binding": upstream_binding,
            "distribution_ownership": ownership,
            "live_object_source_closure": live_closure,
            "transformers_version_bound": version == EXPECTED_VERSION,
            "import_origin_contained_under_package_root": contained,
            "exact_pinned_file_set": exact_file_set,
            "source_bytes_hashed": len(installed_digests) == len(PINNED),
            "live_dispatch_conversion_pass": dispatch["dispatch_conversion_pass"],
            "top_level_converter_class_modules_bound": top_level_class_modules_bound,
            "composition_pass": transformers_provenance_pass,
            "wheel_sha256_prefix": PINNED_UPSTREAM["wheel_sha256"][:16],
            "conversion_source_sha256_prefixes": {
                member: digest[:16] for member, digest in installed_digests.items()
            },
        },
        "remaining": [
            "freeze the exact GPTQModel/Defuser/Optimum/Accelerate/PyTorch/CUDA/GPTQ_TORCH tuple",
            "bind the actual GPTQModel/Defuser loader entry and executable live-object closure",
            "run strict synthetic loading, one-time tensor consumption, expert ordering, forward/VJP/JVP/finite-difference parity",
            "complete Phase-0 before weights or an authorized GPU transition",
        ],
        "boundary": {
            "gpu_used": False,
            "weights_loaded": False,
            "tensor_payload_fetched": False,
            "public_library_wheel_fetched_for_provenance": True,
        },
        "privacy": (
            "aggregate-only; public package identities, booleans, counts, and public "
            "digest prefixes; no host paths"
        ),
    }
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
    print(
        json.dumps(
            {
                "outcome": record["outcome"],
                "transformers_provenance_composition_pass": transformers_provenance_pass,
                "installed_bound_to_upstream": upstream_binding[
                    "installed_bound_to_upstream"
                ],
                "distribution_ownership_pass": ownership[
                    "distribution_ownership_pass"
                ],
                "live_dispatch_conversion_pass": dispatch[
                    "dispatch_conversion_pass"
                ],
                "live_object_closure_pass": live_closure[
                    "live_object_closure_pass"
                ],
            },
            indent=2,
        )
    )


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == _CHILD_ARG:
        _run_child(sys.argv[2])
        return 0
    if len(sys.argv) != 2:
        raise SystemExit("usage: q35q_conversion_admission.py <out_json>")
    return _run_isolated_child(sys.argv[1])


if __name__ == "__main__":
    raise SystemExit(main())
