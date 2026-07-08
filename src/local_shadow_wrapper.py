#!/usr/bin/env python3
"""jlens M7 local shadow wrapper — real-use shadow logs, ADVISORY only.

Connects PolicyEngine v0 to a local inference flow. For each {prompt_id, prompt}
it obtains an output (fixture in dry-run; a live OpenAI-compatible /chat/
completions call in --mode live), attaches a telemetry feature row IF one exists
for that prompt_id, scores it with PolicyEngine, and writes ONE real-use runtime
record to the shadow log.

ADVISORY / SHADOW ONLY: it recommends + logs. It NEVER performs a tool/file/
GitHub action. `require_confirmation` is recorded as a recommendation string,
never executed.

Key limitation: a GGUF chat endpoint returns output text but NO router logits,
so a live prompt has no telemetry feature row -> policy=null (with a note).

Usage:
  # dry-run (default, no network):
  python src/local_shadow_wrapper.py --prompts data/prompts/benchmark_m5_sample.jsonl
  # live (optional):
  python src/local_shadow_wrapper.py --mode live \
      --endpoint-config config/local_endpoint_example.json \
      --prompts my_prompts.jsonl
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "src"))
from policy_engine import PolicyEngine

NO_TELEMETRY_NOTE = ("no telemetry feature row for this prompt_id "
                     "(GGUF endpoint exposes no router logits)")


def _truncate(s: str, n: int = 160) -> str:
    s = (s or "").replace("\n", " ").strip()
    return s if len(s) <= n else s[:n] + "…"


def load_feature_rows(path):
    rows = {}
    p = Path(path)
    if p.exists():
        for line in open(p, encoding="utf-8"):
            r = json.loads(line)
            rows[r["prompt_id"]] = r
    return rows


def dry_run_output(prompt: str) -> str:
    """Deterministic fixture 'model output' — no network, no wall-clock."""
    return f"[dry-run fixture output for: {_truncate(prompt, 60)}]"


def live_output(prompt: str, cfg: dict) -> str:
    """Call an OpenAI-compatible /chat/completions endpoint for output text only."""
    payload = {"model": cfg.get("model"),
               "messages": [{"role": "user", "content": prompt}]}
    url = cfg["base_url"].rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if cfg.get("api_key") and cfg["api_key"] != "not-needed":
        headers["Authorization"] = f"Bearer {cfg['api_key']}"
    try:
        import requests
        r = requests.post(url, json=payload, headers=headers,
                          timeout=cfg.get("timeout_s", 60))
        data = r.json()
    except ImportError:  # stdlib fallback, no install
        import urllib.request
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(), headers=headers)
        with urllib.request.urlopen(req, timeout=cfg.get("timeout_s", 60)) as resp:
            data = json.loads(resp.read().decode())
    return data["choices"][0]["message"]["content"]


def build_record(prompt_id, prompt, output, model, feature_rows, engine):
    """One advisory real-use runtime record. Never executes anything."""
    row = feature_rows.get(prompt_id)
    if row is not None:
        s = engine.score(row)
        policy = {"level": s["level"], "recommended_action": s["recommended_action"],
                  "scores": s["scores"], "explanation": s["explanation"]}
        note = None
    else:
        policy = None
        note = NO_TELEMETRY_NOTE
    return {
        "prompt_id": prompt_id,
        "model": model,
        "feature_source": engine.features_path.name if row is not None else None,
        "prompt_preview": _truncate(prompt),
        "output_preview": _truncate(output),
        "policy": policy,
        "policy_note": note,
        "mode": "shadow",
        "outcome": {"user_agreed": None, "was_wrong": None,
                    "needed_retrieval": None, "needed_checker": None,
                    "notes": None},
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    ap.add_argument("--prompts", default="data/prompts/benchmark_m5_sample.jsonl")
    ap.add_argument("--features",
                    default="reports/features/benchmark_m5_features.jsonl")
    ap.add_argument("--endpoint-config", default="config/local_endpoint_example.json")
    ap.add_argument("--log", default="reports/shadow/realuse_log.jsonl")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args(argv)

    engine = PolicyEngine(features_path=args.features)
    feature_rows = load_feature_rows(args.features)
    cfg = {}
    model = "dry-run-fixture"
    if args.mode == "live":
        cfg = json.loads(Path(args.endpoint_config).read_text())
        model = cfg.get("model", "local")

    prompts = [json.loads(l) for l in open(args.prompts, encoding="utf-8")]
    if args.limit:
        prompts = prompts[:args.limit]

    out = Path(args.log); out.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with out.open("a", encoding="utf-8") as fh:
        for p in prompts:
            pid, text = p.get("id") or p.get("prompt_id"), p.get("text", "")
            output = (dry_run_output(text) if args.mode == "dry-run"
                      else live_output(text, cfg))
            rec = build_record(pid, text, output, model, feature_rows, engine)
            fh.write(json.dumps(rec) + "\n")
            act = rec["policy"]["recommended_action"] if rec["policy"] else "none(policy=null)"
            print(f"[jlens][SHADOW] {pid}: advise={act} "
                  f"(mode={args.mode}; advisory only, no action taken)")
            n += 1
    print(f"[jlens] wrote {n} real-use shadow records -> {out}")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main())
