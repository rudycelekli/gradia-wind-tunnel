"""
The Wind Tunnel loop: attack -> (oracle-witnessed) -> judge -> record exploits,
a factorial causal-slice screen, and a patch/re-attack step that demonstrates
whack-a-mole (H2) and autoimmunity (H3).

An EXPLOIT is a fully automated event: judge PASS and oracle WRONG, with a
valid oracle-checked witness. No human ever adjudicates.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import asdict, dataclass

from .items import Item, oracle
from .judges import Judge
from .transforms import TRANSFORMS, check_witness, t_keyword_inflation


@dataclass
class Episode:
    item_id: str
    transform_id: str
    factors: dict
    favored_phrase: str | None
    oracle_wrong: bool     # witness valid: oracle says the answer is wrong
    judge_pass: bool
    judge_score: float
    is_exploit: bool       # judge_pass AND oracle_wrong
    answer_sha256: str
    rung: str = "L1"       # which threat rung generated this attempt
    cost_usd: float = 0.0  # grader cost for this attempt (0 offline)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def run_attacks(items: list[Item], judge: Judge, seed: int,
                transforms=None, phrase=None, rung: str = "L1") -> list[Episode]:
    """
    L1-style metamorphic pass: for each item x each transform, build a
    wrong-by-construction answer, confirm the witness against the oracle, score
    it with the judge, and flag exploits.
    """
    rng = random.Random(seed)
    transforms = transforms or list(TRANSFORMS.keys())
    episodes: list[Episode] = []
    for item in items:
        for tid in transforms:
            if tid == "keyword_inflation" and phrase is not None:
                attack = t_keyword_inflation(item, rng, phrase=phrase)
            else:
                attack = TRANSFORMS[tid](item, rng)
            witness_valid = check_witness(attack, item)  # oracle confirms wrong
            verdict = judge.score(attack.answer_text, item.question)
            is_exploit = witness_valid and verdict.passed
            episodes.append(Episode(
                rung=rung,
                item_id=item.item_id,
                transform_id=attack.transform_id,
                factors=dict(item.factors),
                favored_phrase=attack.favored_phrase,
                oracle_wrong=witness_valid,
                judge_pass=verdict.passed,
                judge_score=verdict.score,
                is_exploit=is_exploit,
                answer_sha256=_sha(attack.answer_text),
            ))
    return episodes


def exploit_density(episodes: list[Episode]) -> float:
    """Confirmed exploits per 1000 attack attempts."""
    if not episodes:
        return 0.0
    n_exploit = sum(1 for e in episodes if e.is_exploit)
    return 1000.0 * n_exploit / len(episodes)


def false_rejection_rate(items: list[Item], judge: Judge) -> float:
    """
    Autoimmunity measure: fraction of VERIFIED-CORRECT answers the judge
    wrongly REJECTS. (The immune system attacking healthy tissue.)
    """
    if not items:
        return 0.0
    wrong = 0
    for item in items:
        correct = item.correct_answer()
        assert oracle(correct, item)  # sanity: it really is correct
        if not judge.score(correct, item.question).passed:
            wrong += 1
    return wrong / len(items)


def slice_screen(episodes: list[Episode], transform_id: str,
                 factor_keys=("steps",)) -> dict:
    """
    Factorial causal-slice screen: exploit density within each cell of the
    chosen factor(s), restricted to one transform. Because items were generated
    with factors controlled exactly, each cell is a true factorial cell.
    """
    cells: dict[tuple, list[Episode]] = {}
    for e in episodes:
        if e.transform_id != transform_id:
            continue
        key = tuple(e.factors[k] for k in factor_keys)
        cells.setdefault(key, []).append(e)
    return {
        "factor_keys": list(factor_keys),
        "transform_id": transform_id,
        "cells": {
            "|".join(map(str, k)): {
                "n": len(v),
                "exploits": sum(1 for e in v if e.is_exploit),
                "density_per_1000": round(exploit_density(v), 1),
            }
            for k, v in sorted(cells.items())
        },
    }


def run_log_chain_head(episodes: list[Episode]) -> str:
    """
    Deterministic hash over the ordered episode log -- the 'chain head' a
    verifier recomputes (the CA / Guard trust move, in miniature).
    """
    h = hashlib.sha256()
    for e in episodes:
        h.update(json.dumps(asdict(e), sort_keys=True).encode())
    return h.hexdigest()
