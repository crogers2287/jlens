"""M37J Phase 1: build the private deterministic lens-fitting corpus.

120 generic pretraining-like sequences of >=128 tokens (fit truncates to
exactly 128): Wikipedia evidence prose sampled deterministically from the
local FEVER validation file. 100 fit + 20 lens-validation sequences.
Contains no M36 benchmark prompts or answers. The output corpus is
private and gitignored; only its sha256 and aggregate stats are public.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
from pathlib import Path

SEED = 37
N_FIT, N_VAL = 100, 20
MIN_TOKENS = 128


def evidence_sentences(fever_path: Path) -> list[str]:
    """Unique Wikipedia evidence sentences, cleaned of FEVER markup."""
    seen, out = set(), []
    for line in fever_path.read_text().splitlines():
        row = json.loads(line)
        for group in row.get("evidence") or []:
            if len(group) >= 3 and isinstance(group[2], str):
                text = group[2]
                text = re.sub(r"-LRB-\s*", "(", text)
                text = re.sub(r"\s*-RRB-", ")", text)
                text = re.sub(r"-LSB-.*?-RSB-", "", text)
                text = re.sub(r"\s+", " ", text).strip()
                if len(text) > 40 and text not in seen:
                    seen.add(text)
                    out.append(text)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--fever", default="data/raw/valid.jsonl")
    ap.add_argument("--model-ref", required=True,
                    help="pilot model dir (tokenizer only; never committed)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model_ref)

    sentences = evidence_sentences(Path(args.fever))
    rng = random.Random(SEED)
    rng.shuffle(sentences)

    sequences, cursor = [], 0
    while len(sequences) < N_FIT + N_VAL and cursor < len(sentences):
        parts, n_tokens = [], 0
        while n_tokens < MIN_TOKENS and cursor < len(sentences):
            parts.append(sentences[cursor])
            cursor += 1
            n_tokens = len(tok(" ".join(parts))["input_ids"])
        if n_tokens >= MIN_TOKENS:
            sequences.append(" ".join(parts))
    assert len(sequences) == N_FIT + N_VAL, (
        f"only packed {len(sequences)} sequences")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as sink:
        for i, text in enumerate(sequences):
            sink.write(json.dumps(
                {"split": "fit" if i < N_FIT else "val", "text": text}) + "\n")

    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    lengths = [len(tok(t)["input_ids"]) for t in sequences]
    print(json.dumps({
        "seed": SEED, "n_fit": N_FIT, "n_val": N_VAL,
        "min_tokens": MIN_TOKENS,
        "token_len_min": min(lengths), "token_len_max": max(lengths),
        "corpus_sha256": digest,
        "source": "FEVER valid.jsonl Wikipedia evidence prose (local)",
    }, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
