#!/usr/bin/env python3
"""M11 bounded, resumable Agents-A1 shadow workload runner.

A THIN wrapper around autonomous_shadow_supervisor.run_task that:
  - bounds the batch to config batch.size (never exceeds batch.cap),
  - is RESUME-safe: prompt_ids already in the run log are skipped and only
    missing tasks are appended (a re-run adds nothing if the batch is complete),
  - records run metadata (run_id = sha256 of the config, model, endpoint alias,
    task/completed/failed/telemetry-missing/escalation counts, placeholder
    timestamps in deterministic mode),
  - counts endpoint failures per task and CONTINUES when safe.

Raw records + a run-meta sidecar go to the GITIGNORED private dir. Advisory /
shadow only; auto_outcome is a candidate; human outcome fields are never written.

A GGUF chat endpoint has no router logits -> telemetry_missing=true, policy=null.

CLI (default = deterministic smoke/dry-run, no network, no GPU):
  python src/run_agents_a1_shadow_batch.py --config config/agents_a1_shadow_run.json

Live (HUMAN-GATED: the operator serves the Agents-A1 endpoint first):
  python src/run_agents_a1_shadow_batch.py --config my_local.json --mode live
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import autonomous_shadow_supervisor as SUP  # noqa: E402
import local_shadow_wrapper as LSW  # noqa: E402

PLACEHOLDER_TS = "<deterministic-run: no wall-clock>"


def config_run_id(cfg: dict) -> str:
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()[:16]


def _existing_ids(out_path: Path) -> set:
    """prompt_ids already recorded — the basis for resume."""
    ids = set()
    if out_path.exists():
        for line in open(out_path, encoding="utf-8"):
            line = line.strip()
            if line:
                try:
                    ids.add(json.loads(line)["prompt_id"])
                except (json.JSONDecodeError, KeyError):
                    continue
    return ids


def load_batch(cfg, source_path=None):
    """Load tasks from the first available source, bounded by batch.size/cap."""
    batch = cfg.get("batch", {})
    size = int(batch.get("size", 25))
    cap = int(batch.get("cap", 100))
    limit = min(size, cap)
    path = source_path
    if path is None:
        for s in cfg.get("task_sources", []):
            p = Path(s["path"])
            if p.exists():
                path = str(p)
                break
    if path is None:
        raise FileNotFoundError("no available task source in config.task_sources")
    return SUP.load_tasks(path, limit=limit), path


def run_batch(cfg, model_fn, out_path, meta_path=None, validator=None,
              started_at=None, finished_at=None, source_path=None):
    """Run the bounded batch resume-safely; return the run-meta dict."""
    tasks, used_source = load_batch(cfg, source_path)
    out = Path(out_path); out.parent.mkdir(parents=True, exist_ok=True)
    deterministic = cfg.get("run", {}).get("deterministic", True)
    resume = cfg.get("resume", {}).get("enabled", True)

    done = _existing_ids(out) if resume else set()
    todo = [t for t in tasks if t["prompt_id"] not in done]

    n_completed = n_failed = n_tel = n_esc = 0
    with out.open("a", encoding="utf-8") as fh:  # APPEND — never rewrite completed
        for t in todo:
            try:
                rec = SUP.run_task(t, model_fn, cfg)
            except Exception:            # endpoint failure for this task
                n_failed += 1            # count it and CONTINUE when safe
                continue
            if validator is not None and list(validator.iter_errors(rec)):
                n_failed += 1
                continue
            fh.write(json.dumps(rec) + "\n")
            n_completed += 1
            n_tel += 1 if rec.get("telemetry_missing") else 0
            n_esc += 1 if rec.get("auto_outcome", {}).get("escalate_for_review") else 0

    ts = PLACEHOLDER_TS if deterministic else None
    meta = {
        "run_id": config_run_id(cfg),
        "model": cfg.get("endpoint", {}).get("model"),
        "endpoint_alias": cfg.get("endpoint", {}).get("alias"),
        "task_source": used_source,
        "n_tasks": len(tasks),
        "n_completed_this_run": n_completed,
        "n_failed": n_failed,
        "n_telemetry_missing_this_run": n_tel,
        "escalation_count_this_run": n_esc,
        "n_already_done_skipped": len(tasks) - len(todo),
        "started_at": (started_at if started_at is not None else ts),
        "finished_at": (finished_at if finished_at is not None else ts),
        "duration": (PLACEHOLDER_TS if deterministic else None),
        "mode": cfg.get("run", {}).get("mode", "dry-run"),
    }
    if meta_path:
        Path(meta_path).parent.mkdir(parents=True, exist_ok=True)
        Path(meta_path).write_text(json.dumps(meta, indent=1) + "\n")
    return meta


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--config", default="config/agents_a1_shadow_run.json")
    ap.add_argument("--mode", choices=["dry-run", "live"], default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--meta", default=None)
    args = ap.parse_args(argv)

    cfg = SUP.load_config(args.config)
    rcfg = cfg.setdefault("run", {})
    if args.mode:
        rcfg["mode"] = args.mode
    mode = rcfg.get("mode", "dry-run")
    out_path = args.out or rcfg.get("run_log",
                                    "reports/shadow/private/agents_a1_run_local.jsonl")
    meta_path = args.meta or rcfg.get("run_meta",
                                      "reports/shadow/private/agents_a1_run_meta_local.json")

    if mode == "live":
        ecfg = cfg["endpoint"]
        model_fn = lambda p: LSW.live_output(p, ecfg)  # noqa: E731  (HUMAN-GATED endpoint)
    else:
        model_fn = LSW.dry_run_output

    validator = None
    try:
        from jsonschema import Draft7Validator
        S = json.loads(Path("schema/auto_outcome_v1.json").read_text())
        validator = Draft7Validator(S)
    except Exception:
        validator = None

    meta = run_batch(cfg, model_fn, out_path, meta_path, validator=validator)
    print(f"[jlens] agents-a1 run {meta['run_id']}: "
          f"completed={meta['n_completed_this_run']} failed={meta['n_failed']} "
          f"skipped={meta['n_already_done_skipped']} escalated={meta['escalation_count_this_run']} "
          f"telemetry_missing={meta['n_telemetry_missing_this_run']} -> {out_path} "
          f"[advisory/shadow, auto_outcome=candidate]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
