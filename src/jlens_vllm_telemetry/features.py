"""Derive the approved jLens scalar telemetry schema from router captures.

Mirrors the schema-v3 fields produced by ``export_decode_schema.py`` for the
HF path (per-layer topk experts/probs, full entropy, usage-vector drift),
but sourced from the vLLM capture arrays instead of raw logit tensors —
no hidden-state capture and no raw router tensors at benchmark scale.

Also implements the frozen summary-versus-raw equivalence check: features
recomputed from the raw validation logits must match the device-side
summaries within tolerance.
"""

from __future__ import annotations

import numpy as np

# Frozen tolerances for the summary-vs-raw equivalence gate. Raw logits are
# stored fp32; summaries are computed fp32 device-side from the same values,
# so agreement is tight. Weights compare against the router's own fp
# renormalization, which may differ from a numpy recompute at fp rounding
# level on fp16-derived logits.
RAW_ENTROPY_TOL = 1e-3
RAW_MASS_TOL = 1e-3
RAW_WEIGHT_TOL = 5e-3


def _softmax(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)


def usage_matrix(ids: np.ndarray, weights: np.ndarray, num_experts: int) -> np.ndarray:
    """Scatter top-k weights into per-layer expert-usage rows.

    ids/weights: [rows, L, K] -> returns [L, E], each layer row summed over
    tokens then L1-normalized (the schema-v3 weighted usage signature).
    """
    rows, L, K = ids.shape
    out = np.zeros((L, num_experts), dtype=np.float64)
    for layer in range(L):
        np.add.at(out[layer], ids[:, layer, :].reshape(-1),
                  weights[:, layer, :].reshape(-1).astype(np.float64))
        s = out[layer].sum()
        if s > 0:
            out[layer] /= s
    return out


def cosine_dist(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(1.0 - np.dot(a, b) / (na * nb))


def derive_decode_records(
    ids: np.ndarray,
    weights: np.ndarray,
    entropy: np.ndarray,
    mass: np.ndarray,
    prompt_rows: int,
    num_experts: int,
) -> list[dict]:
    """Per-decode-token feature records (private-side; never committed).

    Arrays cover prompt+decode rows in forward order; ``prompt_rows`` marks
    the prefill/decode boundary. Returns one record per decode token with
    the schema-v3 feature set derivable without hidden states.
    """
    rows = ids.shape[0]
    prefill_sig = usage_matrix(
        ids[:prompt_rows], weights[:prompt_rows], num_experts
    ).reshape(-1)
    records = []
    prev_sig = None
    for r in range(prompt_rows, rows):
        tok_sig = usage_matrix(ids[r : r + 1], weights[r : r + 1],
                               num_experts).reshape(-1)
        rec = {
            "decode_index": r - prompt_rows,
            "topk_experts": ids[r].tolist(),
            "topk_probs": weights[r].tolist(),
            "full_entropy": entropy[r].tolist(),
            "topk_mass": mass[r].tolist(),
            "mean_full_entropy": float(entropy[r].mean()),
            "mean_topk_mass": float(mass[r].mean()),
            "drift_from_prefill_weighted": cosine_dist(tok_sig, prefill_sig),
            "drift_from_previous_token_weighted": (
                None if prev_sig is None else cosine_dist(tok_sig, prev_sig)
            ),
        }
        records.append(rec)
        prev_sig = tok_sig
    return records


def summary_vs_raw_check(capture: dict) -> dict:
    """Recompute ids/weights/entropy/mass from the raw validation sample and
    compare against the device-side summaries. Returns aggregate deviations
    only (public-safe)."""
    raw = capture["raw_logits_sample"]          # [R, L, E] fp32
    R = raw.shape[0]
    if R == 0:
        return {"raw_rows": 0, "checked": False}
    ids = capture["ids"][:R]                    # [R, L, K]
    weights = capture["weights"][:R]
    entropy = capture["entropy"][:R]
    mass = capture["mass"][:R]
    k = capture["top_k"]

    probs = _softmax(raw.astype(np.float64))
    ent_re = -(probs * np.log(np.clip(probs, 1e-12, None))).sum(-1)
    top_idx = np.argsort(-probs, axis=-1)[..., :k]
    top_p = np.take_along_axis(probs, top_idx, axis=-1)
    mass_re = top_p.sum(-1)
    w_re = top_p / np.clip(top_p.sum(-1, keepdims=True), 1e-12, None)

    # Order-insensitive id comparison (topk kernels may order ties freely).
    ids_sorted = np.sort(ids, axis=-1)
    re_sorted = np.sort(top_idx, axis=-1)
    id_mismatch_rows = int((ids_sorted != re_sorted).any(axis=-1).sum())

    # Weight comparison in sorted order to stay order-insensitive.
    w_sorted = np.sort(weights, axis=-1)
    w_re_sorted = np.sort(w_re, axis=-1)

    result = {
        "raw_rows": int(R),
        "checked": True,
        "id_mismatch_rowlayers": id_mismatch_rows,
        "entropy_maxdev": float(np.abs(ent_re - entropy).max()),
        "mass_maxdev": float(np.abs(mass_re - mass).max()),
        "weight_maxdev": float(np.abs(w_re_sorted - w_sorted).max()),
        "tolerances": {
            "entropy": RAW_ENTROPY_TOL,
            "mass": RAW_MASS_TOL,
            "weight": RAW_WEIGHT_TOL,
        },
    }
    result["passed"] = (
        result["id_mismatch_rowlayers"] == 0
        and result["entropy_maxdev"] <= RAW_ENTROPY_TOL
        and result["mass_maxdev"] <= RAW_MASS_TOL
        and result["weight_maxdev"] <= RAW_WEIGHT_TOL
    )
    return result
