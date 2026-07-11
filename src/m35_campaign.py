#!/usr/bin/env python3
"""M35 A/B campaign: six-family generation, split assignment, capture."""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import m30_decisive_increment as M30  # noqa: E402
import m33_tool_routing as M33  # noqa: E402
import m34_detector_transfer as M34  # noqa: E402

CAPTURE_DIR = "m35_qwen15_moe"
SPLITS = ("D", "R", "B_test", "A_test")


def load_manifest(path):
    manifest = json.loads(Path(path).read_text())
    if manifest.get("selection_status") != \
            "predeclared_before_m35_task_generation":
        raise ValueError("M35 manifest is not predeclared before generation")
    families = manifest.get("families") or []
    if len(families) != 6:
        raise ValueError("M35 manifest must declare six families")
    if manifest["n_tasks_total"] != sum(f["n_tasks"] for f in families):
        raise ValueError("M35 n_tasks_total mismatch")
    seq = manifest["split_assignment"]["sequence"]
    if len(seq) != 16 or set(seq) != set(SPLITS):
        raise ValueError("M35 split sequence changed")
    counts = {s: seq.count(s) for s in SPLITS}
    if counts != manifest["split_assignment"]["sequence_counts"]:
        raise ValueError("M35 split sequence counts mismatch")
    for family in families:
        if family["n_tasks"] % (4 * 16):
            raise ValueError(
                f"M35 {family['family_id']}: n_tasks not divisible by "
                "strata * sequence length")
    return manifest


def prior_multiplication_tuples(m29_path, m30_path, m31_path, m32_path,
                                m33_path, m34_path):
    """Flat set of every (a, b) tuple the M29-M34 manifests generate."""
    prior = M34.prior_tuples_through_m33(m29_path, m30_path, m31_path,
                                         m32_path, m33_path)
    m34_manifest = M34.load_manifest(m34_path)
    seed = m34_manifest["generation"]["seed"]
    for band in m34_manifest["bands"]:
        rng = random.Random(f"{seed}:{band['band_id']}")
        seen = set(prior[band["band_id"]])
        tuples = M30._draw_tuples(rng, band, band["n_tasks"], seen)
        prior[band["band_id"]] |= set(tuples)
    flat = set()
    for tuples in prior.values():
        flat |= tuples
    return flat


def _draw_pair(rng, stratum, seen, constraint=None):
    """Draw one unseen (a, b) pair for the stratum, honoring a constraint."""
    lo_a, hi_a = stratum["operand_a_range"]
    lo_b, hi_b = stratum["operand_b_range"]
    for _ in range(200000):
        a = rng.randint(lo_a, hi_a)
        b = rng.randint(lo_b, hi_b)
        if constraint == "a > b" and a <= b:
            continue
        if (a, b) not in seen:
            return a, b
    raise ValueError("M35 tuple exhaustion")


def _build_task(family, stratum, rng, a, b):
    fid = family["family_id"]
    if fid == "add_carry":
        expression, answer = f"{a}+{b}", a + b
        prompt = family["prompt_template"].format(a=a, b=b)
        extra = {}
    elif fid == "sub_borrow":
        expression, answer = f"{a}-{b}", a - b
        prompt = family["prompt_template"].format(a=a, b=b)
        extra = {}
    elif fid == "mul_carry":
        expression, answer = f"{a}*{b}", a * b
        prompt = family["prompt_template"].format(a=a, b=b)
        extra = {}
    elif fid == "div_exact":
        # a arrived as (quotient, divisor) product; recompute pieces below
        raise AssertionError("div_exact handled by _build_div_task")
    elif fid == "mul_add":
        lo_c, hi_c = family["additive_term_range"]
        c = rng.randint(lo_c, hi_c)
        expression, answer = f"{a}*{b}+{c}", a * b + c
        prompt = family["prompt_template"].format(a=a, b=b, c=c)
        extra = {"c": c}
    elif fid == "mod_mul":
        lo_m, hi_m = family["modulus_range"]
        m = rng.randint(lo_m, hi_m)
        expression, answer = f"({a}*{b})%{m}", (a * b) % m
        prompt = family["prompt_template"].format(a=a, b=b, m=m)
        extra = {"m": m}
    else:
        raise ValueError(f"unknown family {fid}")
    return {"a": a, "b": b, **extra, "expression": expression,
            "known_answer": str(answer), "prompt": prompt}


def generate_tasks(manifest, m29_path, m30_path, m31_path, m32_path,
                   m33_path, m34_path):
    seed = manifest["generation"]["seed"]
    sequence = manifest["split_assignment"]["sequence"]
    seen = prior_multiplication_tuples(m29_path, m30_path, m31_path,
                                       m32_path, m33_path, m34_path)
    tasks = []
    for family in manifest["families"]:
        fid = family["family_id"]
        per_stratum = family["n_tasks"] // len(family["strata"])
        for stratum in family["strata"]:
            sid = stratum["stratum_id"]
            rng = random.Random(f"{seed}:{fid}:{sid}")
            for index in range(per_stratum):
                if fid == "div_exact":
                    lo_q, hi_q = stratum["quotient_range"]
                    lo_b, hi_b = stratum["operand_b_range"]
                    for _ in range(200000):
                        q = rng.randint(lo_q, hi_q)
                        b = rng.randint(lo_b, hi_b)
                        a = q * b
                        if (a, b) not in seen:
                            break
                    else:
                        raise ValueError("M35 tuple exhaustion")
                    body = {"a": a, "b": b, "q": q,
                            "expression": f"{a}/{b}",
                            "known_answer": str(q),
                            "prompt": family["prompt_template"].format(
                                a=a, b=b)}
                else:
                    a, b = _draw_pair(rng, stratum, seen,
                                      family.get("constraint"))
                    body = _build_task(family, stratum, rng, a, b)
                seen.add((body["a"], body["b"]))
                tasks.append({
                    "prompt_id": f"m35_{fid}_{sid}_{index:03d}",
                    "family": fid,
                    "stratum": sid,
                    "split": sequence[index % len(sequence)],
                    "task_category": "math",
                    **body,
                })
    if len(tasks) != manifest["n_tasks_total"]:
        raise ValueError("M35 generation count mismatch")
    if len({t["prompt_id"] for t in tasks}) != len(tasks):
        raise ValueError("M35 duplicate prompt ids")
    pairs = [(t["a"], t["b"]) for t in tasks]
    if len(set(pairs)) != len(pairs):
        raise ValueError("M35 (a, b) tuples not unique campaign-wide")
    return tasks


def prepare_private_tasks(manifest_path, m29_path, m30_path, m31_path,
                          m32_path, m33_path, m34_path, output_path):
    manifest = load_manifest(manifest_path)
    tasks = generate_tasks(manifest, m29_path, m30_path, m31_path, m32_path,
                           m33_path, m34_path)
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(task) + "\n" for task in tasks))
    return manifest, tasks


def run_captures(manifest, tasks, model_ref, captures_root):
    """Single-model-load greedy originals capture for the whole campaign."""
    import capture_router_logits as CAP
    import torch

    args = argparse.Namespace(
        model=model_ref, dtype="bf16", device_map="auto",
        max_gpu_mem_gib=20.0, trust_remote_code=False)
    tok, model, cfg = CAP.load_model(args)
    root = Path(captures_root)
    cap_tokens = manifest["decode_protocols"]["original"]["decode_cap_tokens"]
    print(f"[jlens] M35 campaign capture ({len(tasks)})", flush=True)
    done = 0
    for task in tasks:
        dest = root / CAPTURE_DIR / f"{task['prompt_id']}.pt"
        if CAP._valid_capture(dest):
            done += 1
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        input_ids, router, hidden, steps = CAP.capture_one(
            tok, model, task["prompt"], 4096, max_new_tokens=cap_tokens,
            router_only=True, chat_template=True)
        torch.save({
            "prompt_id": task["prompt_id"], "input_ids": input_ids,
            "router_logits": router, "hidden_states": hidden,
            "model_type": cfg.model_type, "model_path": str(model_ref),
            "decode_steps": steps,
            "generated_output": tok.decode(
                [s["generated_token_id"] for s in steps],
                skip_special_tokens=True)}, dest)
        done += 1
        if done % 128 == 0:
            print(f"[jlens] M35 capture progress {done}/{len(tasks)}",
                  flush=True)
    print("[jlens] M35 captures complete", flush=True)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest",
                    default="data/prompts/m35_campaign_manifest.json")
    ap.add_argument("--m29-manifest",
                    default="data/prompts/m29_power_manifest.json")
    ap.add_argument("--m30-manifest",
                    default="data/prompts/m30_decisive_manifest.json")
    ap.add_argument("--m31-manifest",
                    default="data/prompts/m31_intervention_manifest.json")
    ap.add_argument("--m32-manifest",
                    default="data/prompts/m32_repair_manifest.json")
    ap.add_argument("--m33-manifest",
                    default="data/prompts/m33_tool_routing_manifest.json")
    ap.add_argument("--m34-manifest",
                    default="data/prompts/m34_transfer_manifest.json")
    ap.add_argument("--tasks-out",
                    default="reports/shadow/private/m35_hf_prompts_local.jsonl")
    ap.add_argument("--captures-root", default="data/captures")
    ap.add_argument("--model-ref")
    ap.add_argument("--prepare-only", action="store_true")
    ap.add_argument("--capture", action="store_true")
    args = ap.parse_args(argv)

    manifest, tasks = prepare_private_tasks(
        args.manifest, args.m29_manifest, args.m30_manifest,
        args.m31_manifest, args.m32_manifest, args.m33_manifest,
        args.m34_manifest, args.tasks_out)
    root = Path(args.captures_root)
    if args.prepare_only:
        done = sum((root / CAPTURE_DIR / f"{t['prompt_id']}.pt").exists()
                   for t in tasks)
        by_split = Counter(t["split"] for t in tasks)
        print(f"[jlens] M35 predeclared tasks: {len(tasks)}; splits="
              f"{dict(by_split)}; captures existing={done}")
        return 0
    if not args.model_ref:
        raise ValueError("--model-ref is required")
    if args.capture:
        run_captures(manifest, tasks, args.model_ref, args.captures_root)
        return 0
    raise SystemExit("specify --prepare-only or --capture; analysis stages "
                     "ship in the track A/B evaluation modules")


if __name__ == "__main__":
    raise SystemExit(main())
