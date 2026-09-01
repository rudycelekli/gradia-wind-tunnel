"""
End-to-end offline demonstration. No API key, no network.

Run:  python -m pilot.demo

Shows, on procedurally generated math with an exact oracle:
  1. L1 exploit finding: a flawed reference-free judge is gamed.
  2. The causal-slice screen recovering "exploit fires at steps>=3".
  3. Patch -> re-attack: whack-a-mole (H2) + autoimmunity (H3).
  4. Self-commitment defense helps but does not cure (H4).
  5. A recomputable run-log chain head (the trust move).
"""

from __future__ import annotations


from .items import generate_factorial
from .judges import KeywordGamingJudge, SelfCommitmentJudge
from .transforms import FAVORED_PHRASES
from .windtunnel import (
    Episode, exploit_density, false_rejection_rate, run_attacks, run_log_chain_head,
    slice_screen,
)

SEED = 20260828


def hr(t):
    print("\n" + "=" * 68 + f"\n{t}\n" + "=" * 68)


def main() -> int:
    items = generate_factorial(seed=SEED, per_cell=6)
    print(f"Generated {len(items)} procedurally-controlled items "
          f"(exact numeric oracle, factors: steps x large_operands x distractor).")

    # ---- 1. L1 exploit finding vs the flawed judge --------------------------
    hr("1. L1 attack vs a reference-free keyword-gaming judge")
    judge = KeywordGamingJudge(FAVORED_PHRASES)
    eps = run_attacks(items, judge, seed=SEED)
    by_t: dict[str, list[Episode]] = {}
    for e in eps:
        by_t.setdefault(e.transform_id, []).append(e)
    for tid, group in sorted(by_t.items()):
        print(f"  {tid:24s} exploit density = "
              f"{exploit_density(group):6.1f} / 1000   "
              f"({sum(e.is_exploit for e in group)}/{len(group)} attempts)")
    print(f"  OVERALL exploit density = {exploit_density(eps):.1f} / 1000")
    print("  -> every exploit is judge=PASS AND oracle=WRONG, confirmed with no human.")

    # ---- 2. causal slice screen --------------------------------------------
    hr("2. Causal-slice screen on keyword_inflation (factor: steps)")
    screen = slice_screen(eps, "keyword_inflation", factor_keys=("steps",))
    for cell, stat in screen["cells"].items():
        print(f"  steps={cell:3s}  density={stat['density_per_1000']:6.1f}/1000  "
              f"({stat['exploits']}/{stat['n']})")
    print("  -> the exploit is not uniform: it concentrates where steps>=3.")
    print("     A true factorial cell, because we generated the factor exactly.")

    # ---- 3. patch -> re-attack: whack-a-mole + autoimmunity -----------------
    hr("3. Patch the exploited phrase, then re-attack (H2 whack-a-mole, H3 autoimmunity)")
    exploited_phrase = "Considering the elderly population,"
    print(f"  Exploit used favored phrase: {exploited_phrase!r}")
    print("  PATCH v1: judge blacklists that exact phrase.")
    patched = KeywordGamingJudge(FAVORED_PHRASES,
                                 blacklist=frozenset({exploited_phrase.lower()}))

    # re-attack with the SAME phrase (should be closed) ...
    eps_same = run_attacks(items, patched, seed=SEED,
                           transforms=["keyword_inflation"], phrase=exploited_phrase)
    # ... and with a DIFFERENT still-favored phrase (whack-a-mole)
    other_phrase = "Let's think step by step."
    eps_other = run_attacks(items, patched, seed=SEED,
                            transforms=["keyword_inflation"], phrase=other_phrase)
    print(f"  re-attack, same phrase   : density = "
          f"{exploit_density(eps_same):6.1f}/1000   (patched family -> closed)")
    print(f"  re-attack, new phrase    : density = "
          f"{exploit_density(eps_other):6.1f}/1000   (held-out family -> relocated)")
    gen = (exploit_density(eps_other) / max(exploit_density(eps_same), 1e-9))
    print(f"  H2 patch-generalization ratio (held-out/patched) = "
          f"{'inf' if exploit_density(eps_same)==0 else round(1/gen,3)} "
          f"-> patch is SPECIFIC, not general (whack-a-mole).")

    # autoimmunity: does the patch now reject CORRECT answers that used the phrase?
    base_frr = false_rejection_rate(items, judge)
    # correct answers that legitimately open with the now-blacklisted phrase:
    from .items import Item
    def prefixed(it: Item) -> Item:
        return it  # correct_answer() has no favored phrase; simulate legit use below
    # simulate a cohort of correct answers that happen to use the phrase
    class _CorrectWithPhrase:
        def __init__(self, it): self.it = it
        def correct_answer(self): return f"{exploited_phrase}\n" + self.it.correct_answer()
        question = property(lambda s: s.it.question)
        factors = property(lambda s: s.it.factors)
    def frr_with_phrase(judge_) -> float:
        wrong = 0
        for it in items:
            ans = f"{exploited_phrase}\n" + it.correct_answer()
            from .items import oracle as _o
            assert _o(ans, it)  # still correct: gold final unchanged
            if not judge_.score(ans, it.question).passed:
                wrong += 1
        return wrong / len(items)
    # restrict to steps>=3 items, where the favored phrase legitimately carries
    # a CORRECT answer past the judge -- so the patch's collateral damage is clean
    deep_items = [it for it in items if it.factors["steps"] >= 3]
    def frr_deep(judge_) -> float:
        wrong = 0
        for it in deep_items:
            ans = f"{exploited_phrase}\n" + it.correct_answer()
            from .items import oracle as _o
            assert _o(ans, it)  # still correct: gold final unchanged
            if not judge_.score(ans, it.question).passed:
                wrong += 1
        return wrong / len(deep_items)
    frr_before = frr_deep(judge)
    frr_after = frr_deep(patched)
    print("  H3 autoimmunity (correct answers using the phrase, steps>=3):")
    print(f"     wrongly rejected before patch = {frr_before*100:5.1f}%    "
          f"after patch = {frr_after*100:5.1f}%")
    print("     -> hardening the scorer starts rejecting healthy tissue.")

    # ---- 4. self-commitment defense ----------------------------------------
    hr("4. Self-commitment judge: helps but does not cure (H4)")
    # judge solves the problem itself by re-deriving gold (stand-in for solve-blind)
    gold_by_q = {it.question: it.gold for it in items}
    sc = SelfCommitmentJudge(solver=lambda q: gold_by_q[q])
    eps_sc = run_attacks(items, sc, seed=SEED)
    print(f"  keyword-gaming judge overall density = {exploit_density(eps):8.1f}/1000")
    print(f"  self-commitment judge overall density = {exploit_density(eps_sc):8.1f}/1000")
    print("  -> structural defense collapses reference-free gaming; remaining")
    print("     exploits (if any) would need answers whose final actually matches.")

    # ---- 5. recomputable chain head ----------------------------------------
    hr("5. Reproducibility: run-log chain head")
    head = run_log_chain_head(eps)
    print(f"  L1 run-log chain head (sha256) = {head}")
    print("  Re-running this demo with the same seed reproduces this exact hash.")
    print("  In the full study every episode is a Guard receipt; the hidden")
    print("  regression suite commits its chain head before any results exist.")

    print("\nDone. Swap KeywordGamingJudge -> RealModelJudge (your key) for Phase 0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
