#!/usr/bin/env python3
"""Q35Q Phase-0 live conversion/source/dispatch admission adapter (CPU-only).

Committed production path per
docs/STEER_ADDENDUM_2026-07-17_Q35Q_RUNTIME_COMPOSITION_PROVENANCE_CORRECTION.md.
Unlike the pure verifiers, this adapter obtains identities FROM the installed
runtime (no caller-supplied observed fields):

- resolve the installed Transformers distribution + version via importlib.metadata;
- resolve conversion_mapping.py + modeling_qwen3_5_moe.py via the import system,
  canonicalize realpath, and require containment under the distribution package root
  (rejects shadow / alternate-origin imports);
- hash the actual imported source bytes;
- obtain get_checkpoint_conversion_mapping("qwen3_5_moe_text") LIVE, extract it
  immediately, bind every converter/operation CLASS module qualname to
  transformers.conversion_mapping (rejects shadow classes), and verify the exact
  conversion (count / prefix multiplicity / patterns / dims).

Expected-digest INDEPENDENCE is not asserted by a boolean here: it requires deriving
the expected digests from the immutable PyPI upstream artifact for transformers
5.13.1 (which exists), not the installed bytes. Until that independent derivation is
committed, this adapter emits `q35q_provenance_blocked` for the independence gate.
Aggregate-only output: version, booleans, and public source-digest prefixes only.

usage: q35q_conversion_admission.py <out_json>
"""
from __future__ import annotations

import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from q35q_dispatch_conversion import extract_mapping, verify_dispatch_conversion  # noqa: E402

EXPECTED_VERSION = "5.13.1"
# the converter/operation CLASSES are defined here (the mapping DATA lives in
# conversion_mapping.py); both are pinned, plus the model definition.
EXPECTED_CONVERSION_MODULE = "transformers.core_model_loading"
PINNED = ("transformers/conversion_mapping.py",
          "transformers/core_model_loading.py",
          "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py")


def _sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    out = sys.argv[1]
    import importlib.metadata as md
    import transformers
    import transformers.conversion_mapping as cm

    version = md.version("transformers")
    pkg_root = os.path.realpath(os.path.dirname(transformers.__file__))
    files = {
        "transformers/conversion_mapping.py": os.path.realpath(cm.__file__),
        "transformers/core_model_loading.py": os.path.realpath(os.path.join(pkg_root, "core_model_loading.py")),
        "transformers/models/qwen3_5_moe/modeling_qwen3_5_moe.py":
            os.path.realpath(os.path.join(pkg_root, "models", "qwen3_5_moe", "modeling_qwen3_5_moe.py")),
    }
    contained = all(p.startswith(pkg_root + os.sep) for p in files.values())
    exact_file_set = set(files) == set(PINNED)
    digests = {k: _sha(v) for k, v in files.items() if os.path.exists(v)}

    # LIVE dispatch object, extracted immediately (no injectable intermediate)
    live = cm.get_checkpoint_conversion_mapping("qwen3_5_moe_text")
    extracted = extract_mapping(live)
    disp = verify_dispatch_conversion(extracted)
    class_modules_bound = all(
        type(o).__module__ == EXPECTED_CONVERSION_MODULE for o in live)

    installed_admission = (version == EXPECTED_VERSION and contained and exact_file_set
                           and disp["dispatch_conversion_pass"] and class_modules_bound
                           and len(digests) == len(PINNED))

    record = {
        "outcome": "q35q_provenance_blocked",
        "artifact_admission_status": "q35q_artifact_admission_blocked",
        "installed_runtime_admission": {
            "transformers_version_bound": version == EXPECTED_VERSION,
            "import_origin_contained_under_distribution_root": contained,
            "exact_pinned_file_set": exact_file_set,
            "source_bytes_hashed": len(digests) == len(PINNED),
            "live_dispatch_conversion_pass": disp["dispatch_conversion_pass"],
            "converter_class_modules_bound": class_modules_bound,
            "installed_admission_pass": installed_admission,
            "conversion_source_sha256_prefixes": {k: v[:16] for k, v in digests.items()},
        },
        "independence_gate": {
            "expected_digests_independent": False,
            "blocker": "expected source digests are not yet derived from the immutable PyPI upstream artifact for transformers 5.13.1; deriving them from the installed bytes would be self-binding",
            "upstream_resolvable": "transformers 5.13.1 exists on PyPI (normal install, no direct_url) -> an independent upstream derivation is feasible next",
        },
        "remaining": ["independent upstream digest derivation (PyPI 5.13.1 sdist/wheel)",
                      "GPTQ runtime tuple (Optimum/GPTQModel+Defuser) for the differentiable fixture",
                      "then Phase-0 conjunction, weights, authorized GPU transition, exact parity"],
        "boundary": {"gpu_used": False, "weights_loaded": False, "tensor_payload_fetched": False,
                     "unrelated_gpu_tenant": "present_preserved"},
        "privacy": "aggregate-only; version + booleans + public source-digest prefixes, no host paths",
    }
    with open(out, "w") as f:
        json.dump(record, f, indent=2, sort_keys=True)
    print(json.dumps({"outcome": record["outcome"],
                      "installed_admission_pass": installed_admission,
                      **record["installed_runtime_admission"]}, indent=2))


if __name__ == "__main__":
    main()
