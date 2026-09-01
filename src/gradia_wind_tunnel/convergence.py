"""The convergence experiment (C2) — the central scientific question.

For a judge architecture, iterate: attack the CURRENT scorer, identify the top
exploited grader signal, patch it, then RE-ATTACK the patch and measure exploit
density on a held-out budget. Over K cycles we classify the held-out density
sequence as monotone-decreasing (converges), plateau, or oscillating, and report
patch-generalization γ per cycle. This is the measurement no prior work reports.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .items import Item
from .judges import KeywordGamingJudge
from .patcher import Patch, synthesize, _family_density
from .transforms import FAVORED_PHRASES


@dataclass
class CycleRecord:
    cycle: int
    patched_phrase: str | None
    heldout_density: float       # ρ on an un-patched family (per 1000)
    patch: Patch | None


@dataclass
class ConvergenceResult:
    architecture: str
    cycles: list[CycleRecord] = field(default_factory=list)
    classification: str = "undetermined"
    mean_gamma: float = 0.0

    @property
    def heldout_curve(self) -> list[float]:
        return [c.heldout_density for c in self.cycles]


def _classify(curve: list[float], tol: float = 1.0) -> str:
    if len(curve) < 2:
        return "undetermined"
    diffs = [b - a for a, b in zip(curve, curve[1:])]
    if all(d <= tol for d in diffs) and (curve[0] - curve[-1]) > tol:
        return "monotone_decreasing"
    signs = [1 if d > tol else (-1 if d < -tol else 0) for d in diffs]
    ups, downs = signs.count(1), signs.count(-1)
    if ups and downs:
        return "oscillating"
    if max(abs(d) for d in diffs) <= tol:
        return "plateau"
    return "monotone_decreasing" if downs and not ups else "plateau"


def run_convergence(
    items: list[Item],
    architecture: str,
    gold_by_question: dict,
    seed: int,
    K: int = 5,
    autoimmunity_budget: float = 0.10,
) -> ConvergenceResult:
    """Rubric-edit convergence: each cycle patches one exploited phrase; the
    adversary relocates to an un-patched phrase (whack-a-mole) until the family
    is exhausted and density falls to zero."""
    result = ConvergenceResult(architecture=architecture)
    blacklist: set[str] = set()
    gammas: list[float] = []
    phrases = list(FAVORED_PHRASES)

    for cycle in range(1, K + 1):
        judge = KeywordGamingJudge(FAVORED_PHRASES, blacklist=frozenset(blacklist))
        # the adversary attacks with the first still-un-patched phrase
        active = [p for p in phrases if p.lower() not in blacklist]
        if not active:
            result.cycles.append(CycleRecord(cycle, None, 0.0, None))
            continue
        exploited = active[0]
        heldout = active[1] if len(active) > 1 else active[0]

        patched, patch = synthesize(
            "rubric_edit", judge, exploited, items,
            heldout_phrase=heldout, gold_by_question=gold_by_question,
            seed=seed + cycle, autoimmunity_budget=autoimmunity_budget,
            patch_id=f"{architecture}-c{cycle}",
        )
        if patch.accepted:
            blacklist.add(exploited.lower())
        gammas.append(patch.generalization_gamma)
        # held-out density measured AFTER the patch, on a still-un-patched family
        post = KeywordGamingJudge(FAVORED_PHRASES, blacklist=frozenset(blacklist))
        remaining = [p for p in phrases if p.lower() not in blacklist]
        hd = _family_density(items, post, remaining[0], seed + 100 + cycle) if remaining else 0.0
        result.cycles.append(CycleRecord(cycle, exploited, round(hd, 1), patch))

    result.classification = _classify(result.heldout_curve)
    result.mean_gamma = round(sum(gammas) / len(gammas), 3) if gammas else 0.0
    return result
