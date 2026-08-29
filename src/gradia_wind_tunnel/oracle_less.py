"""Regime 2 — oracle-less auditing (H6/H7).

When a benchmark's scorer is an LLM judge or rubric grader with NO deterministic
oracle, PASS-and-WRONG cannot be computed. This module replaces the missing
oracle with RELATIONS whose violation is a scorer defect *regardless of the
unknown ground truth*, each machine-checkable:

  1. Metamorphic INVARIANCE   — a semantics-preserving edit must not change the verdict.
  2. Metamorphic MONOTONICITY — a semantics-degrading edit must not raise the score.
  3. BIAS probes              — verbosity / position edits must not move the verdict.
  4. DISAGREEMENT geometry    — Fleiss' kappa across a judge bank (oracle-free reliability).

Honesty: the text-level preserving/degrading edits below are strong HEURISTICS,
not proofs, so a single violation is evidence, not certainty; the rate across many
items is the measurement. The PROVABLE version of the invariance relation is a
witnessed single-variable universe fork (see `universe_forks.fork_on_variable`):
there, "only one thing changed" is certified by before/after world roots, so a
verdict change is a *causally localized* scorer sensitivity. This module is the
Regime-2 instrument; its hypotheses (H6/H7) are preregistered like Regime 1.
"""

from __future__ import annotations

import math
import random
import re
from dataclasses import dataclass, field
from typing import Any, Callable

_EPS = 1e-9


# --- semantics-PRESERVING edits (verdict MUST be invariant) -----------------
_SYNONYMS = [("Therefore", "Thus"), ("because", "since"), ("the answer is", "the result is"),
             ("we get", "we obtain"), ("compute", "calculate"), ("So ", "Hence ")]


def preserve_paraphrase(text: str, rng: random.Random) -> str:
    out = text
    for a, b in _SYNONYMS:
        if rng.random() < 0.7:
            out = re.sub(re.escape(a), b, out)
    return out


def preserve_reformat(text: str, rng: random.Random) -> str:
    # whitespace / bullet reformat only; content identical
    lines = [ln for ln in text.splitlines()]
    return "\n".join(("  " + ln.strip()) if ln.strip() else ln for ln in lines)


def preserve_reorder(text: str, rng: random.Random) -> str:
    # reverse only the interior lines (keep first line and the final-answer line)
    lines = text.splitlines()
    if len(lines) <= 3:
        return text
    mid = lines[1:-1][::-1]
    return "\n".join([lines[0], *mid, lines[-1]])


PRESERVING = {"paraphrase": preserve_paraphrase, "reformat": preserve_reformat,
              "reorder": preserve_reorder}


# --- semantics-DEGRADING edits (score MUST NOT rise) ------------------------
def degrade_drop_step(text: str, rng: random.Random) -> str:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if len(lines) <= 2:
        return text + "\n(omitting the justification)"
    i = 1 + rng.randrange(max(1, len(lines) - 2))
    return "\n".join(lines[:i] + lines[i + 1:])


def degrade_weaken(text: str, rng: random.Random) -> str:
    return "I'm not fully sure, but possibly: " + text.replace("is exactly", "might be roughly")


DEGRADING = {"drop_step": degrade_drop_step, "weaken": degrade_weaken}


def bias_verbosity_pad(text: str, rng: random.Random) -> str:
    filler = ("It is worth noting that this problem sits within a broad and important "
              "class of questions that many careful practitioners have studied at length. ")
    return filler * 2 + text


# --- probe records ----------------------------------------------------------
@dataclass(frozen=True)
class RelationProbe:
    kind: str            # invariance | monotonic | bias_verbosity
    relation: str        # the property asserted
    edit: str
    violated: bool
    base_pass: bool
    after_pass: bool
    d_score: float
    detail: dict = field(default_factory=dict)


def _score(judge, answer: str, question: str):
    v = judge.score(answer, question)
    return bool(getattr(v, "passed")), float(getattr(v, "score", 0.0))


def invariance_probes(judge, answer: str, question: str, rng: random.Random) -> list[RelationProbe]:
    b_pass, b_score = _score(judge, answer, question)
    out = []
    for name, fn in PRESERVING.items():
        p, s = _score(judge, fn(answer, rng), question)
        out.append(RelationProbe("invariance", f"verdict invariant under {name}", name,
                                 violated=(p != b_pass), base_pass=b_pass, after_pass=p,
                                 d_score=round(s - b_score, 4)))
    return out


def monotonicity_probes(judge, answer: str, question: str, rng: random.Random) -> list[RelationProbe]:
    b_pass, b_score = _score(judge, answer, question)
    out = []
    for name, fn in DEGRADING.items():
        p, s = _score(judge, fn(answer, rng), question)
        out.append(RelationProbe("monotonic", f"score must not rise under {name}", name,
                                 violated=(s > b_score + 1e-6), base_pass=b_pass, after_pass=p,
                                 d_score=round(s - b_score, 4)))
    return out


def bias_probes(judge, answer: str, question: str, rng: random.Random) -> list[RelationProbe]:
    b_pass, b_score = _score(judge, answer, question)
    p, s = _score(judge, bias_verbosity_pad(answer, rng), question)
    return [RelationProbe("bias_verbosity", "irrelevant padding must not raise score", "verbosity",
                          violated=(s > b_score + 1e-6), base_pass=b_pass, after_pass=p,
                          d_score=round(s - b_score, 4))]


def audit_item(judge, answer: str, question: str, seed: int = 0) -> dict[str, Any]:
    """All Regime-2 probes for one (answer, question) against one judge → fingerprint."""
    rng = random.Random(seed)
    probes = (invariance_probes(judge, answer, question, rng)
              + monotonicity_probes(judge, answer, question, rng)
              + bias_probes(judge, answer, question, rng))
    inv = [p for p in probes if p.kind == "invariance"]
    mon = [p for p in probes if p.kind == "monotonic"]
    return {
        "n_probes": len(probes),
        "invariance_violation_rate": round(sum(p.violated for p in inv) / max(1, len(inv)), 3),
        "monotonicity_violation_rate": round(sum(p.violated for p in mon) / max(1, len(mon)), 3),
        "verbosity_bias": any(p.violated for p in probes if p.kind == "bias_verbosity"),
        "any_violation": any(p.violated for p in probes),
        "probes": [p.__dict__ for p in probes],
    }


# --- disagreement geometry (oracle-free reliability) ------------------------
def fleiss_kappa(counts: list[list[int]]) -> float:
    """Fleiss' kappa. `counts[i] = [n_pass, n_fail]` over the SAME number of raters
    per item. Returns kappa in [-1, 1]; near 0 = chance-level agreement."""
    counts = [c for c in counts if sum(c) > 0]
    if not counts:
        return 0.0
    n = sum(counts[0])
    if n < 2 or any(sum(c) != n for c in counts):
        return 0.0
    N = len(counts)
    p_cat = [sum(c[j] for c in counts) / (N * n) for j in range(len(counts[0]))]
    P_bar = sum((sum(cij * cij for cij in c) - n) / (n * (n - 1)) for c in counts) / N
    P_e = sum(p * p for p in p_cat)
    denom = 1 - P_e
    return 1.0 if abs(denom) < _EPS else round((P_bar - P_e) / denom, 4)


def disagreement_over_bank(judges: list, answer: str, question: str) -> dict[str, Any]:
    """Run one answer through a judge bank; report pass-rate + a single-item split."""
    passes = [1 if _score(j, answer, question)[0] else 0 for j in judges]
    k = len(passes)
    n_pass = sum(passes)
    split = min(n_pass, k - n_pass) / max(1, k // 1)   # 0 = unanimous, higher = split
    return {"n_judges": k, "n_pass": n_pass, "unanimous": n_pass in (0, k),
            "disagreement_index": round(2 * min(n_pass, k - n_pass) / max(1, k), 3)}


def regime2_status() -> dict[str, Any]:
    return {
        "regime": 2,
        "substitutes": ["metamorphic_invariance", "metamorphic_monotonicity",
                        "bias_verbosity", "disagreement_fleiss_kappa"],
        "provable_variant": "universe_forks.fork_on_variable (single-variable witnessed metamorphic pair)",
        "hypotheses": ["H6", "H7"],
        "status": "instrument v1 — offline-tested; preregister before any Regime-2 run",
    }
