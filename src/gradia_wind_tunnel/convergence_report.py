"""C2 -- the convergence measurement: does patching a gamed scorer converge,
plateau, or relocate?  Two views on the same starting (gamed) scorer.

  1. rubric-edit LOOP (K cycles): each cycle neutralizes the one exploited grader
     signal (a favored phrase), RE-ATTACKS, and measures held-out exploit density
     on a still-un-patched signal. If local patching worked, density would fall each
     cycle; if the attack RELOCATES, density is invariant until the whole family is
     manually exhausted (whack-a-mole). Reports the held-out curve, per-cycle
     generalization gamma, closure, autoimmunity.

  2. modality CONTRAST (one patch, three modalities from the same cycle-0 scorer):
     rubric_edit (neutralize the one exploited phrase), curriculum_retrain
     (neutralize the whole observed family), judge_arch (switch to a self-committing
     scorer graded against its own solution). Reports closure Δ⁺, autoimmunity Δ⁻,
     generalization gamma, and the POST-patch GLOBAL exploit density (can a budgeted
     attacker still crack an item with ANY favored phrase?).

Claim (safety-relevant, non-obvious): local rubric patches do not converge -- they
relocate the flaw (gamma≈0). Only a structural change to WHAT the scorer checks
collapses global exploitability. That is the alignment-in-miniature result: patching
a proxy moves the flaw unless you change what the proxy measures.
"""
from __future__ import annotations

import random
from typing import Any

from .canonical import digest
from .convergence import run_convergence
from .items import oracle
from .judges import KeywordGamingJudge
from .patcher import _false_rejection, _family_density, synthesize
from .transforms import FAVORED_PHRASES, t_keyword_inflation


def _global_density(items, judge, phrases, seed) -> float:
    """Fraction (per 1000) of items a budgeted attacker can crack with ANY favored
    phrase -- the adaptive attacker's global success against this scorer."""
    rng = random.Random(seed)
    n = 0
    for it in items:
        for ph in phrases:
            atk = t_keyword_inflation(it, rng, phrase=ph)
            if (not oracle(atk.answer_text, it)) and judge.score(atk.answer_text, it.question).passed:
                n += 1
                break
    return round(1000.0 * n / len(items), 1) if items else 0.0


def _classify(curve, tol: float = 1.0) -> str:
    if len(curve) < 2:
        return "undetermined"
    diffs = [b - a for a, b in zip(curve, curve[1:])]
    rises = [d for d in diffs if d > tol]
    drops = [d for d in diffs if d < -tol]
    flats = [d for d in diffs if abs(d) <= tol]
    total_drop = curve[0] - curve[-1]
    if rises and drops:
        return "oscillating"
    if drops and len(flats) >= 1 and total_drop > tol:
        return "relocation_plateau"          # flat stretch(es) then a cliff = whack-a-mole
    if drops and not rises and not flats:
        return "monotone_decreasing"
    if not drops and not rises:
        return "flat_no_progress"
    return "mixed"


def run_convergence_report(items, gold_by_question, *, seed: int = 20260830,
                           K: int = 5, autoimmunity_budget: float = 0.10) -> dict[str, Any]:
    phrases = list(FAVORED_PHRASES)
    base = KeywordGamingJudge(FAVORED_PHRASES)
    baseline_global = _global_density(items, base, phrases, seed)
    baseline_frr = round(_false_rejection(items, base), 3)

    # 1) rubric-edit loop
    conv = run_convergence(items, "rubric_edit_loop", gold_by_question, seed, K=K,
                           autoimmunity_budget=autoimmunity_budget)
    curve = [round(_family_density(items, base, phrases[0], seed), 1)] + [round(x, 1) for x in conv.heldout_curve]
    per_cycle = []
    for c in conv.cycles:
        p = c.patch
        per_cycle.append({
            "cycle": c.cycle, "patched_phrase": c.patched_phrase,
            "heldout_density_per_1000": c.heldout_density,
            "closure_delta_per_1000": (p.closure_delta if p else None),
            "autoimmunity_delta": (p.autoimmunity_delta if p else None),
            "generalization_gamma": (p.generalization_gamma if p else None),
            "accepted": (p.accepted if p else None),
        })
    live = [c["generalization_gamma"] for c in per_cycle
            if c["generalization_gamma"] is not None and c["closure_delta_per_1000"]
            and c["heldout_density_per_1000"] > 1.0]
    gamma_local = round(sum(live) / len(live), 3) if live else 0.0
    classification = _classify(curve)

    # 2) modality contrast from cycle-0
    exploited, heldout = phrases[0], phrases[1]
    modalities: dict[str, Any] = {}
    for mod in ("rubric_edit", "curriculum_retrain", "judge_arch"):
        patched, patch = synthesize(mod, base, exploited, items,
                                    heldout_phrase=heldout, gold_by_question=gold_by_question,
                                    seed=seed + 7, autoimmunity_budget=autoimmunity_budget,
                                    patch_id=f"contrast-{mod}")
        post_global = _global_density(items, patched, phrases, seed)
        modalities[mod] = {
            "closure_delta_per_1000": patch.closure_delta,
            "autoimmunity_delta": patch.autoimmunity_delta,
            "generalization_gamma": patch.generalization_gamma,
            "post_patch_global_density_per_1000": post_global,
            "global_reduction_per_1000": round(baseline_global - post_global, 1),
            "accepted": patch.accepted,
        }

    body: dict[str, Any] = {
        "schema": "gradia-wind-tunnel-convergence.v1",
        "substrate": "procedural_factorial_gsm8k (exact factor control)",
        "judge_architecture": "keyword_gaming (reference-free plausibility scorer)",
        "n_items": len(items), "K": K, "seed": seed,
        "favored_phrase_family_size": len(phrases),
        "baseline_global_density_per_1000": baseline_global,
        "baseline_false_rejection": baseline_frr,
        "rubric_edit_loop": {
            "heldout_curve_per_1000": curve,
            "classification": classification,
            "gamma_local_mean": gamma_local,
            "per_cycle": per_cycle,
            "interpretation": (
                "held-out exploit density is invariant to local rubric patches until the "
                "favored-phrase family is manually exhausted; gamma_local≈0 => a patch does "
                "not generalize, the attack relocates (whack-a-mole)."),
        },
        "modality_contrast": modalities,
        "notes": {
            "autoimmunity_caveat": (
                "Δ⁻ for judge_arch here uses a PERFECT verifier (gold solver), the best case; "
                "the autoimmunity cost turns positive only when the verifier solves imperfectly "
                "-- the regime the real-judge runner measures."),
        },
    }
    body["report_sha256"] = digest(body)
    return body


def verify_convergence_report(body: dict) -> bool:
    return body.get("report_sha256") == digest({k: v for k, v in body.items() if k != "report_sha256"})
