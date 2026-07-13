"""M37J-A: preregistered 192-task diagnostic decision set (pilot model).

Generated and committed BEFORE any diagnostic labels are inspected.
Four deterministic tool-checkable families (three M38E procedural
generators under an M37J-specific seed plus json_digits with fresh
operands), 48 tasks per family split 24 discovery / 12 validation /
12 sealed holdout. Difficulty bands are mixed (b1/b1/b2/b2 per
family's four 12-task blocks) to deliberately populate the four
outcome classes on the weaker pilot model. Disjointness from M29-M36
decision sets is enforced by prompt-string exclusion against every
prior local task file plus the fresh seed. Tasks are private; only
the aggregate manifest is public.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import m38e_families as E  # noqa: E402
from m36_calibration import FAMILIES as M36_FAMILIES  # noqa: E402
from m36t_gen_tasks import prior_prompts  # noqa: E402
from m36v_phase1 import PRIVATE_DIR  # noqa: E402

M37J_SEED = "m37j-diag-v1"
PER_FAMILY = 48                      # 24 discovery / 12 val / 12 holdout
BAND_BLOCKS = (1, 1, 2, 2)           # difficulty mix per 12-task block
TASKS_OUT = PRIVATE_DIR / "m37j_diagnostic_tasks.jsonl"
MANIFEST_OUT = "reports/telemetry/m37j_diagnostic_manifest.json"


def gen_json_digits(band: int, index: int) -> dict:
    family = next(f for f in M36_FAMILIES if f["family_id"] == "json_digits")
    (lo, hi), = family["strata"][band - 1]
    rng = random.Random(f"{M37J_SEED}:json_digits:b{band}:{index}")
    n = rng.randint(lo, hi)
    digits = [int(ch) for ch in str(n)][::-1]
    return {"prompt": family["prompt"].format(n=n),
            "known_answer": json.dumps(digits), "json_expected": digits}


def generate(family: str, band: int, index: int) -> dict:
    if family == "json_digits":
        task = gen_json_digits(band, index)
    else:
        # M38E generators under the M37J seed (monkeypatched seed const).
        original = E.M38E_SEED
        E.M38E_SEED = M37J_SEED
        try:
            task = E.GENERATORS[family](band, index)
        finally:
            E.M38E_SEED = original
    task.update(task_id=f"m37j_{family}_b{band}_{index:03d}",
                family=family, band=f"b{band}")
    return task


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(TASKS_OUT))
    ap.add_argument("--manifest-out", default=MANIFEST_OUT)
    args = ap.parse_args()

    excluded = prior_prompts()
    families = ("mod_chain", "alg_coeff", "order_track", "json_digits")
    tasks, skipped = [], 0
    for family in families:
        emitted, index = 0, 0
        while emitted < PER_FAMILY:
            band = BAND_BLOCKS[emitted // 12]
            task = generate(family, band, index)
            index += 1
            if task["prompt"] in excluded:
                skipped += 1
                continue
            excluded.add(task["prompt"])
            # Split assignment: deterministic by emission order.
            split = ("discovery" if emitted < 24
                     else "validation" if emitted < 36 else "holdout")
            task["split"] = split
            tasks.append(task)
            emitted += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(t) + "\n" for t in tasks))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()

    counts = {s: sum(1 for t in tasks if t["split"] == s)
              for s in ("discovery", "validation", "holdout")}
    manifest = {
        "schema_version": 1,
        "run_kind": "m37j_diagnostic_manifest",
        "steer": "0497526",
        "preregistered_before_any_labels": True,
        "pilot_model": "Qwen1.5-MoE-A2.7B-Chat",
        "seed": M37J_SEED,
        "families": list(families),
        "per_family": PER_FAMILY,
        "band_mix_per_family": "12 tasks each at bands b1,b1,b2,b2",
        "splits": counts,
        "decode_budgets": {"short_cap_tokens": 256, "long_cap_tokens": 1024,
                           "single_source_run": "one greedy run to the long "
                           "cap; short-cap outcome derived from the prefix "
                           "(EOS position <= 256); capped outputs are never "
                           "labeled completed-wrong"},
        "outcome_classes": ["completed_correct", "completed_incorrect",
                            "short_cap_truncated_long_cap_correct",
                            "truncated_at_both_caps"],
        "lens_readout": {"layers": [2, 6, 11, 16, 21],
                         "positions": "every 32 decode tokens plus the final "
                                      "position (teacher-forced re-forward "
                                      "of the recorded generation)",
                         "top_k_tokens": 10,
                         "lens_sha256": "49faf4e926395393acf543d578ad3022d3"
                                        "61e373a598921ba4d2ec5afc95378b"},
        "semantic_groups": "the five fixed groups from the protocol "
                           "(completion/continuation/verification/"
                           "error-conflict/uncertainty); no words added "
                           "after observing holdout outcomes",
        "feature_freeze": "discovery-derived sparse features fit on "
                          "discovery only; vocabulary/normalization/"
                          "sparsity/count frozen on validation before "
                          "holdout is opened; labels and verifier results "
                          "never enter features",
        "disjointness": "prompt-string exclusion vs all prior local task "
                        "sets + fresh seed",
        "collisions_skipped": skipped,
        "tasks_sha256": digest,
        "tasks_public": False,
        "privacy_check_status": "aggregate manifest only; tasks private",
    }
    Path(args.manifest_out).write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"[m37j] diagnostic set: {len(tasks)} tasks "
          f"({counts}) {skipped} collisions sha={digest[:16]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
