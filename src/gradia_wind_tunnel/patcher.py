"""The Patcher (C4/IP-9): synthesize a minimal repair for an exploit family and
measure what it costs.

Three modalities, all guarded by an autoimmunity budget — a patch is REJECTED if
it wrongly rejects more than `autoimmunity_budget` of verified-correct answers:
  rubric_edit        — neutralize the exact exploited grader signal.
  judge_arch         — switch to a structurally stronger scorer (self-commitment).
  curriculum_retrain — neutralize the whole family observed in the slice cohort.

Every patch reports closure Δ⁺ (family density removed), autoimmunity cost Δ⁻
(correct answers newly rejected), and generalization γ (Δρ on a held-out family
÷ Δρ on the patched family) — γ<1 is whack-a-mole.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .items import Item, oracle
from .judges import Judge, KeywordGamingJudge, SelfCommitmentJudge
from .transforms import FAVORED_PHRASES, t_keyword_inflation


@dataclass
class Patch:
    patch_id: str
    modality: str
    targets_phrase: str | None
    closure_delta: float          # Δ⁺  (per 1000)
    autoimmunity_delta: float     # Δ⁻  (fraction of correct answers newly rejected)
    generalization_gamma: float   # γ   (held-out Δρ / patched Δρ)
    accepted: bool
    reason: str = ""


def _family_density(items: list[Item], judge: Judge, phrase: str, seed: int) -> float:
    rng = random.Random(seed)
    n = 0
    for it in items:
        atk = t_keyword_inflation(it, rng, phrase=phrase)
        if (not oracle(atk.answer_text, it)) and judge.score(atk.answer_text, it.question).passed:
            n += 1
    return 1000.0 * n / len(items) if items else 0.0


def _false_rejection(items: list[Item], judge: Judge) -> float:
    """Fraction of verified-correct answers the judge wrongly rejects."""
    wrong = 0
    for it in items:
        ans = it.correct_answer()
        assert oracle(ans, it)
        if not judge.score(ans, it.question).passed:
            wrong += 1
    return wrong / len(items) if items else 0.0


def synthesize(
    modality: str,
    current: KeywordGamingJudge,
    exploited_phrase: str,
    items: list[Item],
    *,
    heldout_phrase: str,
    gold_by_question: dict,
    seed: int,
    autoimmunity_budget: float = 0.10,
    patch_id: str = "patch",
) -> tuple[Judge, Patch]:
    """Produce (patched_judge, Patch) for one modality."""
    before_patched = _family_density(items, current, exploited_phrase, seed)
    before_heldout = _family_density(items, current, heldout_phrase, seed + 1)
    frr_before = _false_rejection(items, current)

    if modality == "rubric_edit":
        patched: Judge = KeywordGamingJudge(
            FAVORED_PHRASES, blacklist=frozenset({exploited_phrase.lower()}))
    elif modality == "curriculum_retrain":
        # neutralize the whole family observed in the slice cohort
        patched = KeywordGamingJudge(
            FAVORED_PHRASES, blacklist=frozenset(p.lower() for p in FAVORED_PHRASES))
    elif modality == "judge_arch":
        patched = SelfCommitmentJudge(solver=lambda q: gold_by_question[q])
    else:
        raise ValueError(f"unknown modality {modality!r}")

    after_patched = _family_density(items, patched, exploited_phrase, seed + 2)
    after_heldout = _family_density(items, patched, heldout_phrase, seed + 3)
    frr_after = _false_rejection(items, patched)

    closure = round(before_patched - after_patched, 1)
    d_patched = max(before_patched - after_patched, 1e-9)
    d_heldout = before_heldout - after_heldout
    gamma = round(max(d_heldout, 0.0) / d_patched, 3)
    autoimmunity = round(frr_after - frr_before, 3)

    accepted = autoimmunity <= autoimmunity_budget
    reason = "within autoimmunity budget" if accepted else (
        f"rejected: autoimmunity {autoimmunity:.3f} > budget {autoimmunity_budget:.3f}")

    return patched, Patch(
        patch_id=patch_id, modality=modality, targets_phrase=exploited_phrase,
        closure_delta=closure, autoimmunity_delta=autoimmunity,
        generalization_gamma=gamma, accepted=accepted, reason=reason,
    )
