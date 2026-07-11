#!/usr/bin/env python3
"""M21 fixture-first Hugging Face/safetensors telemetry backend.

The backend records aggregate logits/hidden/router features without prompt or
generation text and without raw tensors. The loader never downloads weights:
it accepts an existing local safetensors directory or an explicitly approved
model id resolved with ``local_files_only=True``. Real model execution is gated
for a later milestone; M21 is exercised with deterministic fake sources.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from abc import ABC, abstractmethod
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from verifiers import evidence_hash


class ModelApprovalRequired(RuntimeError):
    """Raised before any download when a model id/path is not locally approved."""


class SafetensorsNotFound(RuntimeError):
    """Raised when a local directory has no safetensors weights/index."""


@dataclass(frozen=True)
class LoaderSpec:
    model_ref: str
    source_kind: str
    local_files_only: bool = True
    trust_remote_code: bool = False


class HFSafetensorsLoader:
    """No-download loader contract for a future real HF telemetry source."""

    def __init__(self, model_ref=None, approved_model_ids=None):
        self.model_ref = model_ref or os.getenv("JLENS_HF_MODEL")
        env_ids = {x.strip() for x in os.getenv(
            "JLENS_HF_APPROVED_MODEL_IDS", "").split(",") if x.strip()}
        self.approved_model_ids = set(approved_model_ids or ()) | env_ids

    def resolve(self) -> LoaderSpec:
        if not self.model_ref:
            raise ModelApprovalRequired(
                "set JLENS_HF_MODEL or provide a local path/approved model id")
        path = Path(self.model_ref).expanduser()
        if path.exists():
            if not path.is_dir():
                raise SafetensorsNotFound("model path must be a directory")
            has_weights = (any(path.glob("*.safetensors"))
                           or (path / "model.safetensors.index.json").exists())
            if not has_weights:
                raise SafetensorsNotFound(
                    "local model directory contains no safetensors weights/index")
            return LoaderSpec(str(path.resolve()), "local_path")
        if self.model_ref not in self.approved_model_ids:
            raise ModelApprovalRequired(
                "model id is not explicitly approved; automatic download refused")
        return LoaderSpec(self.model_ref, "approved_model_id")

    def load(self):
        """Load only from local files/cache; never downloads or trusts remote code."""
        spec = self.resolve()
        from transformers import AutoModelForCausalLM, AutoTokenizer
        kwargs = {"local_files_only": True, "trust_remote_code": False}
        tokenizer = AutoTokenizer.from_pretrained(spec.model_ref, **kwargs)
        model = AutoModelForCausalLM.from_pretrained(spec.model_ref, **kwargs)
        model.eval()
        return tokenizer, model, spec


class BackendDescriptor(ABC):
    backend_name: str
    record_kind: str

    @property
    @abstractmethod
    def telemetry_access(self) -> str: ...


class GGUFBackendDescriptor(BackendDescriptor):
    """Existing runtime stays separate and honestly lacks internal telemetry."""

    backend_name = "gguf_runtime"
    record_kind = "auto_outcome_v1"

    @property
    def telemetry_access(self):
        return "missing"


class HFSafetensorsBackendDescriptor(BackendDescriptor):
    backend_name = "hf_safetensors"
    record_kind = "hf_telemetry_record_v1"

    @property
    def telemetry_access(self):
        return "available_when_source_exposes_it"


def _softmax(values):
    if not values:
        return []
    m = max(values)
    exps = [math.exp(float(v) - m) for v in values]
    total = sum(exps)
    return [v / total for v in exps]


def _mean(values):
    return sum(values) / len(values) if values else None


def _norm(vector):
    return math.sqrt(sum(float(x) ** 2 for x in vector))


def _logit_stats(logits, selected_token_id=None, top_k=2):
    probs = _softmax(logits)
    if not probs:
        return None
    selected = (max(range(len(probs)), key=probs.__getitem__)
                if selected_token_id is None else int(selected_token_id))
    if selected < 0 or selected >= len(probs):
        return None
    ranked = sorted(probs, reverse=True)
    k = min(max(1, int(top_k)), len(ranked))
    entropy = -sum(p * math.log(max(p, 1e-12)) for p in probs)
    margin = ranked[0] - ranked[1] if len(ranked) > 1 else ranked[0]
    return {
        "selected_token_id": selected,
        "entropy": entropy,
        "selected_token_probability": probs[selected],
        "top_k": k,
        "top_k_mass": min(1.0, sum(ranked[:k])),
        "top_k_margin": margin,
    }


def _empty_logits(status="missing"):
    return {
        "status": status, "selected_token_id": None, "entropy": None,
        "selected_token_probability": None, "top_k": None,
        "top_k_mass": None, "top_k_margin": None,
        "window": {"step_count": 0, "mean_entropy": None,
                   "high_entropy_count": 0, "low_confidence_count": 0,
                   "top_k_margin_trend": None},
    }


def _summarize_logits(steps, top_k, high_entropy, low_confidence):
    stats = []
    for step in steps:
        if isinstance(step.get("logits"), (list, tuple)):
            item = _logit_stats(step["logits"], step.get("selected_token_id"), top_k)
            if item:
                stats.append(item)
    if not stats:
        return _empty_logits("missing")
    final = stats[-1]
    margins = [x["top_k_margin"] for x in stats]
    return {
        "status": "available",
        **{k: final[k] for k in ("selected_token_id", "entropy",
                                 "selected_token_probability", "top_k",
                                 "top_k_mass", "top_k_margin")},
        "window": {
            "step_count": len(stats),
            "mean_entropy": _mean([x["entropy"] for x in stats]),
            "high_entropy_count": sum(x["entropy"] >= high_entropy for x in stats),
            "low_confidence_count": sum(
                x["selected_token_probability"] <= low_confidence for x in stats),
            "top_k_margin_trend": margins[-1] - margins[0] if len(margins) > 1 else 0.0,
        },
    }


def _summarize_precomputed_logits(steps, high_entropy, low_confidence):
    """Summarize capture-time scalars without retaining full vocabulary logits."""
    stats = []
    for step in steps:
        required = ("generated_token_id", "entropy_final_logits",
                    "selected_token_prob", "top_k", "top_k_mass",
                    "top_k_margin")
        if not all(step.get(key) is not None for key in required):
            continue
        stats.append({
            "selected_token_id": int(step["generated_token_id"]),
            "entropy": float(step["entropy_final_logits"]),
            "selected_token_probability": float(step["selected_token_prob"]),
            "top_k": int(step["top_k"]),
            "top_k_mass": float(step["top_k_mass"]),
            "top_k_margin": float(step["top_k_margin"]),
        })
    if not stats:
        return _empty_logits("missing")
    final = stats[-1]
    margins = [x["top_k_margin"] for x in stats]
    return {
        "status": "available",
        **final,
        "window": {
            "step_count": len(stats),
            "mean_entropy": _mean([x["entropy"] for x in stats]),
            "high_entropy_count": sum(
                x["entropy"] >= high_entropy for x in stats),
            "low_confidence_count": sum(
                x["selected_token_probability"] <= low_confidence
                for x in stats),
            "top_k_margin_trend": (
                margins[-1] - margins[0] if len(margins) > 1 else 0.0),
        },
    }


def _summarize_hidden(steps, enabled):
    if not enabled:
        return {"status": "disabled", "layer_count": None,
                "vector_norm_mean": None}
    layers = next((s.get("hidden_states") for s in reversed(steps)
                   if s.get("hidden_states") is not None), None)
    if not layers:
        return {"status": "missing", "layer_count": None,
                "vector_norm_mean": None}
    return {"status": "available", "layer_count": len(layers),
            "vector_norm_mean": _mean([_norm(v) for v in layers])}


def _router_vectors(steps):
    return [layer for step in steps for layer in (step.get("router_logits") or [])
            if isinstance(layer, (list, tuple)) and layer]


def _summarize_router(steps, model_kind, router_supported=True):
    empty = {"layer_count": None, "top_expert_ids": [],
             "router_entropy_mean": None, "expert_concentration_mean": None,
             "windowed_expert_shift": None}
    if model_kind == "dense":
        return {"status": "not_moe", **empty}
    if model_kind == "moe" and not router_supported:
        return {"status": "unsupported", **empty}
    vectors = _router_vectors(steps)
    if not vectors:
        return {"status": "missing", **empty}
    probs = [_softmax(v) for v in vectors]
    entropies = [-sum(p * math.log(max(p, 1e-12)) for p in row) for row in probs]
    concentrations = [max(row) for row in probs]
    last_layers = steps[-1].get("router_logits") or []
    last_ids = [max(range(len(v)), key=lambda i: v[i]) for v in last_layers]
    first_layers = steps[0].get("router_logits") or []
    first_ids = [max(range(len(v)), key=lambda i: v[i]) for v in first_layers]
    comparable = min(len(first_ids), len(last_ids))
    shift = (sum(first_ids[i] != last_ids[i] for i in range(comparable)) / comparable
             if comparable else 0.0)
    return {"status": "available", "layer_count": len(last_layers),
            "top_expert_ids": last_ids, "router_entropy_mean": _mean(entropies),
            "expert_concentration_mean": _mean(concentrations),
            "windowed_expert_shift": shift}


class HFTelemetryBackend:
    """Aggregate telemetry builder over a source-provided sequence of steps."""

    def __init__(self, model_ref="fake-fixture", source_kind="fake_fixture",
                 top_k=2, high_entropy=1.0, low_confidence=0.5):
        self.model_ref = model_ref
        self.source_kind = source_kind
        self.top_k = top_k
        self.high_entropy = high_entropy
        self.low_confidence = low_confidence

    def capture(self, task_id, steps, *, model_kind="unknown", input_token_count=0,
                capture_hidden=False, router_supported=True, alignment=None):
        steps = list(steps or [])
        logits = _summarize_logits(
            steps, self.top_k, self.high_entropy, self.low_confidence)
        hidden = _summarize_hidden(steps, capture_hidden)
        router = _summarize_router(steps, model_kind, router_supported)
        return self._record(
            task_id, logits, hidden, router, model_kind=model_kind,
            input_token_count=input_token_count, alignment=alignment)

    def capture_precomputed(self, task_id, steps, *, model_kind="unknown",
                            input_token_count=0, router_supported=True,
                            alignment=None):
        """Build a record from private capture-time scalar/router summaries.

        ``steps`` may contain router vectors, but only aggregate router features
        enter the returned schema record. Full vocabulary logits are never
        required or persisted by this path.
        """
        steps = list(steps or [])
        logits = _summarize_precomputed_logits(
            steps, self.high_entropy, self.low_confidence)
        hidden = {"status": "disabled", "layer_count": None,
                  "vector_norm_mean": None}
        router = _summarize_router(steps, model_kind, router_supported)
        return self._record(
            task_id, logits, hidden, router, model_kind=model_kind,
            input_token_count=input_token_count, alignment=alignment)

    def _record(self, task_id, logits, hidden, router, *, model_kind,
                input_token_count, alignment=None):
        alignment = alignment or {}
        statuses = [logits["status"], hidden["status"], router["status"]]
        capture_status = ("completed" if logits["status"] == "available"
                          else "partial" if any(s == "available" for s in statuses)
                          else "failed")
        record = {
            "schema_version": 1,
            "record_kind": "hf_telemetry",
            "backend": "hf_safetensors",
            "task_id": task_id,
            "model_ref_hash": evidence_hash(self.model_ref),
            "source_kind": self.source_kind,
            "model_kind": model_kind,
            "capture_status": capture_status,
            "input_token_count": int(input_token_count),
            "decode_step_count": logits["window"]["step_count"],
            "logits": logits,
            "hidden": hidden,
            "router": router,
            "outcome_alignment": {
                "auto_outcome": bool(alignment.get("auto_outcome")),
                "action_result": bool(alignment.get("action_result")),
                "grounded_result": bool(alignment.get("grounded_result")),
                "reviewed_outcome": bool(alignment.get("reviewed_outcome")),
            },
            "evidence_hash": evidence_hash(
                task_id, self.model_ref, logits["status"], hidden["status"],
                router["status"], logits.get("selected_token_id")),
            "candidate_only": True,
            "production_gated": True,
        }
        return record


def fixture_records():
    backend = HFTelemetryBackend()
    dense = backend.capture(
        "m19_m_000",
        [{"logits": [0.0, 1.0, 2.0]}, {"logits": [0.5, 1.5, 0.0]}],
        model_kind="dense", input_token_count=7,
        alignment={"auto_outcome": True, "action_result": True})
    moe = backend.capture(
        "m15_c_000",
        [{"logits": [2.0, 0.0, 1.0], "hidden_states": [[3.0, 4.0], [0.0, 2.0]],
          "router_logits": [[3.0, 1.0, 0.0], [0.0, 2.0, 1.0]]},
         {"logits": [0.0, 3.0, 1.0], "hidden_states": [[0.0, 1.0], [2.0, 2.0]],
          "router_logits": [[0.0, 1.0, 3.0], [0.0, 2.0, 1.0]]}],
        model_kind="moe", input_token_count=9, capture_hidden=True,
        alignment={"auto_outcome": True, "action_result": True,
                   "grounded_result": True})
    missing = backend.capture(
        "fixture_missing", [{"logits": None}], model_kind="unknown",
        input_token_count=3, capture_hidden=True)
    return [dense, moe, missing]


def summarize(records):
    available_logits = [r for r in records if r["logits"]["status"] == "available"]
    summary = {
        "schema_version": 1,
        "backend": "hf_safetensors",
        "fixture_only": True,
        "weights_loaded": 0,
        "n_records": len(records),
        "capture_status_distribution": dict(sorted(Counter(
            r["capture_status"] for r in records).items())),
        "logits_status_distribution": dict(sorted(Counter(
            r["logits"]["status"] for r in records).items())),
        "hidden_status_distribution": dict(sorted(Counter(
            r["hidden"]["status"] for r in records).items())),
        "router_status_distribution": dict(sorted(Counter(
            r["router"]["status"] for r in records).items())),
        "mean_final_entropy_available": _mean(
            [r["logits"]["entropy"] for r in available_logits]),
        "mean_selected_probability_available": _mean(
            [r["logits"]["selected_token_probability"] for r in available_logits]),
        "alignment_coverage": {key: sum(
            r["outcome_alignment"][key] for r in records)
            for key in ("auto_outcome", "action_result", "grounded_result",
                        "reviewed_outcome")},
        "raw_prompt_output_or_tensor_persisted": False,
        "model_weights_or_cache_committed": False,
        "candidate_only": True,
        "production_gated": True,
        "privacy_check_status": "aggregate-only fixture telemetry; no raw text/tensors",
    }
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fixture-summary-out",
                    default="reports/telemetry/hf_fixture_summary.json")
    args = ap.parse_args(argv)
    records = fixture_records()
    schema = json.loads(Path("schema/hf_telemetry_record_v1.json").read_text())
    from jsonschema import Draft7Validator
    validator = Draft7Validator(schema)
    errors = [(r["task_id"], e.message) for r in records
              for e in validator.iter_errors(r)]
    if errors:
        raise ValueError(f"invalid fixture telemetry: {errors[0]}")
    summary = summarize(records)
    out = Path(args.fixture_summary_out); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=1) + "\n")
    print(f"[jlens] HF telemetry fixture: {len(records)} records, "
          f"weights_loaded=0 -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
