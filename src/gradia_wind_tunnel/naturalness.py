"""Naturalness study harness -- evidence that oracle-witnessed exploits are answers
a deployed model could plausibly emit, not prompt-injection artifacts.

The 'reward hacking, not prompt injection' claim rests on the exploit answers being
NATURAL. This module (1) samples the actual oracle-wrong exploit answer texts, (2)
records the automated NaturalnessScreen verdict on each, and (3) emits a blind Likert
rating instrument for human raters. When ratings return, score_agreement() reports
screen<->human agreement and the human-rated natural rate -- converting the naturalness
assertion into evidence.
"""
from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path
from typing import Any

from .adversary import NaturalnessScreen
from .benchmark_suite import build_benchmark
from .transfer import _attacks_for


def sample_exploit_answers(benchmark_ids, *, n_per_benchmark: int = 15,
                           seed: int = 20260830, limit: int = 100) -> list[dict[str, Any]]:
    screen = NaturalnessScreen()
    rng = random.Random(seed)
    out: list[dict[str, Any]] = []
    for bid in benchmark_ids:
        try:
            bench = build_benchmark(bid)
            items = bench.items(seed=seed, limit=limit)
        except Exception:
            continue
        rr = random.Random(seed)
        pool = []
        for item in items:
            for atk in _attacks_for(bench, item, rr):
                if not bench.oracle(atk.answer_text, item):     # oracle-wrong by construction
                    pool.append((item, atk))
        rng.shuffle(pool)
        for item, atk in pool[:n_per_benchmark]:
            out.append({
                "benchmark": bid, "attack": atk.transform_id,
                "question": item.question[:400], "answer_text": atk.answer_text,
                "oracle_wrong": True, "screen_natural": screen.passes(atk.answer_text),
            })
    for i, r in enumerate(out):
        r["id"] = f"nat-{i:04d}"
    return out


def screen_baseline(samples) -> dict[str, Any]:
    by = defaultdict(lambda: [0, 0])
    tot = [0, 0]
    for s in samples:
        by[s["attack"]][0] += 1
        by[s["attack"]][1] += int(s["screen_natural"])
        tot[0] += 1
        tot[1] += int(s["screen_natural"])
    return {"n": tot[0],
            "overall_natural_rate": round(tot[1] / tot[0], 3) if tot[0] else 0.0,
            "by_attack": {k: {"n": v[0], "natural_rate": round(v[1] / v[0], 3)}
                          for k, v in sorted(by.items())}}


def write_rating_sheet(samples, path) -> str:
    """Blind Likert instrument. Raters see only question + candidate answer and rate
    plausibility 1-5; attack label + screen verdict are trailing hidden columns."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "benchmark", "question", "candidate_answer",
                    "human_plausibility_1to5", "notes", "_attack_hidden", "_screen_natural"])
        for s in samples:
            w.writerow([s["id"], s["benchmark"],
                        s["question"].replace("\n", " ")[:300],
                        s["answer_text"].replace("\n", " "), "", "",
                        s["attack"], s["screen_natural"]])
    return str(p)


def score_agreement(rows) -> dict[str, Any]:
    """Score a returned rating sheet (rows = dicts). plausibility>=4 => 'natural'."""
    rated = [r for r in rows if str(r.get("human_plausibility_1to5", "")).strip()]
    if not rated:
        return {"n_rated": 0, "note": "no human ratings yet"}
    human = [1 if float(r["human_plausibility_1to5"]) >= 4 else 0 for r in rated]
    scr = [1 if str(r.get("_screen_natural", "")).lower() in ("true", "1") else 0 for r in rated]
    agree = sum(1 for h, s in zip(human, scr) if h == s)
    return {"n_rated": len(rated),
            "human_natural_rate": round(sum(human) / len(rated), 3),
            "screen_human_agreement": round(agree / len(rated), 3),
            "mean_plausibility": round(sum(float(r["human_plausibility_1to5"]) for r in rated) / len(rated), 2)}
