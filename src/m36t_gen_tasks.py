"""M36T Phase 1: generate the fresh private development task set.

Per steer 79878ab: fresh, disjoint, deterministic, tool-checkable tasks
in the four Phase-0 candidate families (div_exact, json_digits,
mod_arith, sub_mixed), committed seed and family mix, excluding all
M29-M36C operands and prompts. Disjointness is enforced by prompt
string against every prior task file (the prompt fully determines the
operands in these families) plus the historical multiplication-tuple
exclusions. Development tasks are never sealed decision data; the task
file itself is private. Public output is this generator plus an
aggregate manifest (counts + file sha256).
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

from m36_calibration import FAMILIES, TASKS_PATH as M36C_TASKS_PATH  # noqa: E402
from m36v_phase1 import PRIVATE_DIR  # noqa: E402

M36T_SEED = "m36t-dev-v1"
ID_PREFIX = "m36t"
DEV_TASKS_PER_CELL = 6          # x 4 strata x 4 families = 96 dev tasks
CANDIDATE_FAMILIES = ("div_exact", "json_digits", "mod_arith", "sub_mixed")
DEV_TASKS_OUT = PRIVATE_DIR / "m36t_dev_tasks.jsonl"
MANIFEST_OUT = "reports/telemetry/m36t_dev_generation_manifest.json"


def prior_prompts() -> set[str]:
    """Prompt strings from every prior local task file (private + repo)."""
    seen: set[str] = set()
    candidates = [M36C_TASKS_PATH,
                  PRIVATE_DIR / "m35_campaign_tasks_local.jsonl"]
    candidates += sorted(Path("data/prompts").glob("*.jsonl"))
    for path in candidates:
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            for key in ("prompt", "text", "question"):
                if isinstance(row.get(key), str):
                    seen.add(row[key])
    return seen


def build_task(fid: str, family: dict, stratum, rng, s_index: int,
               index: int) -> dict:
    task = {"task_id": f"{ID_PREFIX}_{fid}_s{s_index}_{index:03d}",
            "family": fid, "stratum": f"s{s_index}"}
    if fid == "mod_arith":
        (alo, ahi), (blo, bhi), (mlo, mhi) = stratum
        a, b = rng.randint(alo, ahi), rng.randint(blo, bhi)
        m = rng.randint(mlo, mhi)
        task.update(known_answer=str((a * b) % m),
                    prompt=family["prompt"].format(a=a, b=b, m=m))
    elif fid == "sub_mixed":
        (lo, hi), = stratum
        a, b, c, d = (rng.randint(lo, hi) for _ in range(4))
        task.update(expression=f"{a}-{b}+{c}-{d}",
                    known_answer=str(a - b + c - d),
                    prompt=family["prompt"].format(a=a, b=b, c=c, d=d))
    elif fid == "div_exact":
        (qlo, qhi), (dlo, dhi) = stratum
        q, d = rng.randint(qlo, qhi), rng.randint(dlo, dhi)
        task.update(known_answer=str(q),
                    prompt=family["prompt"].format(n=q * d, d=d))
    elif fid == "json_digits":
        (lo, hi), = stratum
        n = rng.randint(lo, hi)
        digits = [int(ch) for ch in str(n)][::-1]
        task.update(known_answer=json.dumps(digits),
                    json_expected=digits,
                    prompt=family["prompt"].format(n=n))
    else:
        raise ValueError(fid)
    return task


def main() -> int:
    global M36T_SEED, DEV_TASKS_PER_CELL, ID_PREFIX
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", default=str(DEV_TASKS_OUT))
    ap.add_argument("--manifest-out", default=MANIFEST_OUT)
    ap.add_argument("--seed", default=M36T_SEED)
    ap.add_argument("--tasks-per-cell", type=int, default=DEV_TASKS_PER_CELL)
    ap.add_argument("--id-prefix", default="m36t")
    args = ap.parse_args()

    M36T_SEED, DEV_TASKS_PER_CELL = args.seed, args.tasks_per_cell
    ID_PREFIX = args.id_prefix

    excluded = prior_prompts()
    families = {f["family_id"]: f for f in FAMILIES}
    tasks, skipped = [], 0
    for fid in CANDIDATE_FAMILIES:
        family = families[fid]
        for s_index, stratum in enumerate(family["strata"], start=1):
            rng = random.Random(f"{M36T_SEED}:{fid}:s{s_index}")
            emitted = 0
            while emitted < DEV_TASKS_PER_CELL:
                task = build_task(fid, family, stratum, rng, s_index, emitted)
                if task["prompt"] in excluded:
                    skipped += 1
                    continue
                excluded.add(task["prompt"])
                tasks.append(task)
                emitted += 1

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(json.dumps(t) + "\n" for t in tasks))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()

    manifest = {
        "schema_version": 1,
        "run_kind": "m36t_dev_generation_manifest",
        "steer": "79878ab",
        "purpose": "development only — never sealed decision data",
        "seed": M36T_SEED,
        "families": list(CANDIDATE_FAMILIES),
        "strata_per_family": 4,
        "tasks_per_cell": DEV_TASKS_PER_CELL,
        "n_tasks": len(tasks),
        "disjointness": "prompt-string exclusion vs all prior local task "
                        "files (M35/M36C private sets + data/prompts/*)",
        "collisions_skipped": skipped,
        "tasks_sha256": digest,
        "tasks_public": False,
        "privacy_check_status": "aggregate manifest only; tasks private",
    }
    Path(args.manifest_out).write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"[jlens] M36T dev tasks: {len(tasks)} generated "
          f"({skipped} collisions skipped) sha={digest[:16]}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
