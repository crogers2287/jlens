"""Aggregate-only guard for public M36V/M36 artifacts.

``assert_aggregate_only(payload)`` walks a JSON-serializable payload and
raises ``PrivacyViolation`` if anything that must stay private could leak:
raw arrays, per-token sequences, prompt/output text, token ids, expert
traces, or filesystem paths. Public artifacts carry scalars, booleans,
short labels, and small dicts — nothing shaped like data.
"""

from __future__ import annotations

import numbers

MAX_LIST_LEN = 16
MAX_STR_LEN = 200

FORBIDDEN_KEYS = {
    "prompt", "prompts", "prompt_text", "text", "output_text", "outputs",
    "completion", "token_ids", "tokens", "token_text", "input_ids",
    "router_logits", "raw_logits", "raw_logits_sample", "logits",
    "routed_experts", "expert_ids", "topk_experts", "topk_ids",
    "expert_trace", "hidden_states", "weights", "topk_probs", "logprobs",
    "ids", "records", "per_token", "per_task",
}


class PrivacyViolation(ValueError):
    pass


def _fail(path: str, why: str):
    raise PrivacyViolation(f"public artifact rejected at {path or '$'}: {why}")


def assert_aggregate_only(payload, _path: str = "") -> None:
    if payload is None or isinstance(payload, (bool, numbers.Number)):
        return
    if isinstance(payload, str):
        if len(payload) > MAX_STR_LEN:
            _fail(_path, f"string longer than {MAX_STR_LEN} chars")
        if payload.count("/") >= 2 and " " not in payload:
            _fail(_path, "string looks like a filesystem path")
        return
    if isinstance(payload, dict):
        for key, value in payload.items():
            if not isinstance(key, str):
                _fail(_path, "non-string key")
            if key.lower() in FORBIDDEN_KEYS:
                _fail(f"{_path}.{key}", "forbidden key")
            assert_aggregate_only(value, f"{_path}.{key}")
        return
    if isinstance(payload, (list, tuple)):
        if len(payload) > MAX_LIST_LEN:
            _fail(_path, f"sequence longer than {MAX_LIST_LEN} entries")
        for i, value in enumerate(payload):
            assert_aggregate_only(value, f"{_path}[{i}]")
        return
    # numpy arrays, tensors, bytes, custom objects: never public.
    _fail(_path, f"disallowed type {type(payload).__name__}")
