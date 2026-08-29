"""Analyst extras (IP-6/7/8): the exploitability spectrum, exploit DNA, and the
disagreement-geometry detector.

- Exploitability spectrum: a benchmark's immune fingerprint — density over
  (transform x slice). Two benchmarks with equal accuracy can differ sharply.
- Exploit DNA: typed records clustered to ask whether a small basis of judge
  blind spots explains most exploits (the universality question).
- Disagreement detector: turn multi-judge disagreement into an oracle-free
  early-warning signal — do exploits concentrate where independent judges split?
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .items import Item, oracle
from .judges import Judge
from .transforms import t_keyword_inflation
from .windtunnel import Episode, exploit_density


def exploitability_spectrum(episodes: list[Episode],
                            factor_keys=("steps",)) -> dict:
    """density over (transform x slice-cell)."""
    spectrum: dict[str, dict[str, float]] = {}
    for e in episodes:
        cell = "|".join(str(e.factors[k]) for k in factor_keys)
        spectrum.setdefault(e.transform_id, {}).setdefault(cell, [])  # type: ignore[arg-type]
    # collect then reduce
    buckets: dict[tuple[str, str], list[Episode]] = {}
    for e in episodes:
        cell = "|".join(str(e.factors[k]) for k in factor_keys)
        buckets.setdefault((e.transform_id, cell), []).append(e)
    out: dict[str, dict[str, float]] = {}
    for (tid, cell), eps in sorted(buckets.items()):
        out.setdefault(tid, {})[cell] = round(exploit_density(eps), 1)
    return out


def exploit_dna(episodes: list[Episode]) -> dict:
    """Cluster confirmed exploits by (transform, slice_signature, favored_phrase)."""
    clusters: dict[tuple, int] = {}
    for e in episodes:
        if not e.is_exploit:
            continue
        sig = (e.transform_id, e.factors.get("steps"), e.favored_phrase)
        clusters[sig] = clusters.get(sig, 0) + 1
    total = sum(clusters.values())
    top = sorted(clusters.values(), reverse=True)
    coverage = round(sum(top[:3]) / total, 3) if total else 0.0
    return {
        "n_exploits": total,
        "n_clusters": len(clusters),
        "top3_coverage": coverage,  # do a few archetypes explain most exploits?
        "archetypes": [
            {"transform": k[0], "steps": k[1], "favored_phrase": k[2], "count": v}
            for k, v in sorted(clusters.items(), key=lambda kv: -kv[1])[:8]
        ],
    }


def disagreement_detector(items: list[Item], judges: list[Judge], seed: int) -> dict:
    """Do exploits concentrate where independent judges disagree? Oracle-free
    signal: for each keyword-inflation attack, disagreement = judges split on
    PASS; compare exploit rate in the high- vs low-disagreement sets."""
    rng = random.Random(seed)
    hi_total = hi_exploit = lo_total = lo_exploit = 0
    for it in items:
        atk = t_keyword_inflation(it, rng)
        wrong = not oracle(atk.answer_text, it)
        passes = [j.score(atk.answer_text, it.question).passed for j in judges]
        disagree = 0 < sum(passes) < len(passes)
        exploit = wrong and any(passes)
        if disagree:
            hi_total += 1
            hi_exploit += int(exploit)
        else:
            lo_total += 1
            lo_exploit += int(exploit)
    hi_rate = round(hi_exploit / hi_total, 3) if hi_total else 0.0
    lo_rate = round(lo_exploit / lo_total, 3) if lo_total else 0.0
    return {
        "high_disagreement_exploit_rate": hi_rate,
        "low_disagreement_exploit_rate": lo_rate,
        "signal": round(hi_rate - lo_rate, 3),  # >0 ⇒ disagreement predicts exploits
        "n_high": hi_total, "n_low": lo_total,
    }
