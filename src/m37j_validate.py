"""M37J Phase 1: lens readout validation + forward invariance (V100).

Runs only after a refit that passes the 30.0 GiB gate. Checks, per the
frozen protocol:

  1. finite lens matrices and finite lens/model logits on all 20
     held-out validation sequences;
  2. stable application: two applications of the lens to the same
     sequence produce identical readouts;
  3. coherent intermediate readouts: mean reciprocal rank of the
     model's actual next token in the lens readout, by early/middle/
     late layer band, against the vanilla logit-lens baseline
     (use_jacobian=False) on a small synthetic concept set;
  4. forward invariance: model logits from the recorded (observation-
     only) forward match a bare forward exactly;
  5. lens application cost and memory overhead.

Public output is aggregate-only: booleans, band-level MRR, timings,
memory. No prompts, tokens, logits, or lens matrices leave the host.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

# Synthetic public concept set (fixed; not committed to any artifact).
CONCEPT_PROMPTS = [
    "The capital of France is the city of",
    "Two plus two equals the number",
    "The chemical symbol for water is",
    "The opposite of hot is",
    "The third planet from the sun is called",
    "A baby dog is called a",
    "The color of a clear daytime sky is",
    "Seven times eight equals",
]


def band(layer: int, n_layers: int) -> str:
    third = n_layers / 3
    return ("early" if layer < third
            else "middle" if layer < 2 * third else "late")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model-ref", required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--lens", required=True)
    ap.add_argument("--result-out", required=True)
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from jlens.hf import from_hf
    from jlens.lens import JacobianLens

    device = "cuda:0"
    torch.zeros(1, device=device)
    torch.cuda.reset_peak_memory_stats(device)

    hf_model = AutoModelForCausalLM.from_pretrained(
        args.model_ref, dtype=torch.float16, device_map={"": device})
    hf_model.eval()
    tokenizer = AutoTokenizer.from_pretrained(args.model_ref)
    model = from_hf(hf_model, tokenizer)
    lens = JacobianLens.load(args.lens)

    val_seqs = [json.loads(l)["text"]
                for l in Path(args.corpus).read_text().splitlines()
                if json.loads(l)["split"] == "val"]
    assert len(val_seqs) == 20, len(val_seqs)

    checks: dict[str, bool] = {}
    checks["jacobians_finite"] = all(
        torch.isfinite(J).all().item() for J in lens.jacobians.values())

    # 1+4: finite logits and forward invariance on all 20 val sequences.
    # Forward invariance per protocol: the observation-only recorder must
    # not change the model's normal output — same computation, hooks on
    # vs hooks off. The unembed-path difference (apply()'s model_logits
    # vs the fused HF head) is a separate numerical diagnostic, reported
    # but not a gate: it compares two computation paths, not the hooks.
    from jlens.hooks import ActivationRecorder

    probe_layers = sorted({lens.source_layers[0],
                           lens.source_layers[len(lens.source_layers) // 2],
                           lens.source_layers[-1]})
    finite_ok, invariance_maxdiff, unembed_maxdiff = True, 0.0, 0.0
    apply_times = []
    for text in val_seqs:
        t0 = time.time()
        lens_logits, model_logits, input_ids = lens.apply(
            model, text, layers=probe_layers, positions=[-1],
            max_seq_len=128)
        apply_times.append(time.time() - t0)
        for L, ll in lens_logits.items():
            finite_ok &= bool(torch.isfinite(ll).all().item())
        finite_ok &= bool(torch.isfinite(model_logits).all().item())
        with torch.no_grad():
            bare = hf_model(input_ids).logits[0, -1]
            with ActivationRecorder(model.layers,
                                    at=probe_layers) as _rec:
                hooked = hf_model(input_ids).logits[0, -1]
        invariance_maxdiff = max(
            invariance_maxdiff,
            float((bare.float() - hooked.float()).abs().max()))
        unembed_maxdiff = max(
            unembed_maxdiff,
            float((bare.float().cpu()
                   - model_logits[-1].float().cpu()).abs().max()))
    checks["val_logits_finite"] = finite_ok
    checks["forward_invariance"] = invariance_maxdiff == 0.0

    # 2: stability — identical readout on repeat application.
    a1, _, _ = lens.apply(model, val_seqs[0], layers=probe_layers,
                          positions=[-1], max_seq_len=128)
    a2, _, _ = lens.apply(model, val_seqs[0], layers=probe_layers,
                          positions=[-1], max_seq_len=128)
    checks["stable_application"] = all(
        torch.equal(a1[L], a2[L]) for L in probe_layers)

    # 3: coherence — MRR of the model's next token in lens readout per
    # band, lens vs vanilla logit-lens baseline, on the concept set.
    def mrr_by_band(use_jacobian: bool) -> dict:
        acc: dict[str, list[float]] = {"early": [], "middle": [], "late": []}
        for prompt in CONCEPT_PROMPTS:
            lens_logits, model_logits, _ = lens.apply(
                model, prompt,
                layers=lens.source_layers if use_jacobian else None,
                positions=[-1], max_seq_len=64, use_jacobian=use_jacobian)
            target = int(model_logits[-1].argmax())
            for L, ll in lens_logits.items():
                rank = int((ll[-1] > ll[-1][target]).sum()) + 1
                acc[band(L, model.n_layers)].append(1.0 / rank)
        return {b: round(sum(v) / len(v), 4) for b, v in acc.items() if v}

    mrr_lens = mrr_by_band(True)
    mrr_baseline = mrr_by_band(False)

    peak_reserved = torch.cuda.max_memory_reserved(device) / 2**30
    payload = {
        "schema_version": 1,
        "run_kind": "m37j_phase1_validation",
        "pilot_model": "Qwen1.5-MoE-A2.7B-Chat",
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "forward_invariance_max_abs_diff": invariance_maxdiff,
        "unembed_path_max_abs_diff_diagnostic": unembed_maxdiff,
        "held_out_sequences": len(val_seqs),
        "probe_layers": probe_layers,
        "concept_mrr_jacobian_lens": mrr_lens,
        "concept_mrr_logit_lens_baseline": mrr_baseline,
        "apply_seconds_mean": round(sum(apply_times) / len(apply_times), 3),
        "validation_peak_reserved_gib": round(peak_reserved, 2),
        "privacy_check_status": "aggregate validation metrics only",
    }
    Path(args.result_out).write_text(json.dumps(payload, indent=1) + "\n")
    print(f"[m37j] validation: passed={payload['all_checks_passed']} "
          f"checks={checks} mrr_lens={mrr_lens} "
          f"mrr_base={mrr_baseline}", flush=True)
    return 0 if payload["all_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
