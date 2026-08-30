"""Adversary x judge TRANSFER: is gameability a property of the reference-free
paradigm, or of one judge checkpoint?

We score the full L1 attack catalog against a bank of structurally different
scorers and an independent-verifier scorer, on the real benchmarks:

  deliberation  : reference-free, rewards deliberation phrasing (the FAVORED_PHRASES)
  verification  : reference-free, rewards verification / rigor / citation rhetoric
  permissive    : reference-free, rewards EITHER signal family (a union judge)
  verifier      : passes only if the answer is independently oracle-correct
                  (the structural defense; by construction it passes none of the
                  wrong-by-construction attacks)

Per benchmark we report each judge's exploit density, the attack x judge matrix
(which attack fools which judge), and the judge x judge TRANSFER matrix: of the
exploits that fool judge i, what fraction also fool judge j. Disjoint signal
families => near-zero cross-transfer (an exploit is signal-specific); the verifier
=> zero transfer from everything (independent verification is the paradigm-level
defense). Gameability is thus a property of the PARADIGM (every reference-free
judge has some attack) even though no single exploit is universal.
"""
from __future__ import annotations

import random
from typing import Any

from .benchmark_suite import build_benchmark
from .canonical import digest
from .llm_judge import LLMJudge, SimulatedGraderProvider
from .transforms import Attack, FAVORED_PHRASES, JUDGE_GAMING_WRAPPERS

DELIBERATION_SIGNALS = tuple(FAVORED_PHRASES)
VERIFICATION_SIGNALS = (
    "verification", "re-derived", "confirmed", "rigorous", "well-calibrated",
    "standard interpretation", "aligns exactly", "standard result", "canonical treatment",
)


def _judge_bank() -> dict:
    def J(name, favored):
        j = LLMJudge(SimulatedGraderProvider(favored=tuple(favored)))
        j.name = name
        return j
    return {
        "deliberation": J("deliberation", DELIBERATION_SIGNALS),
        "verification": J("verification", VERIFICATION_SIGNALS),
        "permissive": J("permissive", DELIBERATION_SIGNALS + VERIFICATION_SIGNALS),
    }


def _attacks_for(bench, item, rng) -> list[Attack]:
    as_comment = getattr(bench, "benchmark_id", "") in {"humaneval", "swebench_verified"}
    base = list(bench.attacks(item, rng))
    base_wrong = base[0].answer_text if base else item.correct_answer_text
    jg = [Attack(nm, wrap(base_wrong, rng, as_comment=as_comment), witness="", favored_phrase=None)
          for nm, wrap in JUDGE_GAMING_WRAPPERS.items()]
    return base + jg


def run_transfer(benchmark_ids, *, seed: int = 20260830, limit: int = 100) -> dict[str, Any]:
    bank = _judge_bank()
    jnames = list(bank.keys()) + ["verifier"]
    per_bench: dict[str, Any] = {}
    for bid in benchmark_ids:
        try:
            bench = build_benchmark(bid)
            items = bench.items(seed=seed, limit=limit)
        except Exception as e:
            per_bench[bid] = {"error": f"{type(e).__name__}: {str(e)[:120]}"}
            continue
        rng = random.Random(seed)
        recs = []
        for item in items:
            for atk in _attacks_for(bench, item, rng):
                ow = not bench.oracle(atk.answer_text, item)
                v = {jn: bank[jn].score(atk.answer_text, item.question).passed for jn in bank}
                v["verifier"] = bench.oracle(atk.answer_text, item)   # passes iff correct
                recs.append({"attack": atk.transform_id, "oracle_wrong": ow, "v": v})
        N = len(recs) or 1
        # per-judge exploit density
        dens = {jn: round(1000.0 * sum(1 for r in recs if r["oracle_wrong"] and r["v"][jn]) / N, 1)
                for jn in jnames}
        # attack x judge (which attack fools which judge, per-1000 over all records)
        attacks = sorted({r["attack"] for r in recs})
        axj = {}
        for a in attacks:
            ra = [r for r in recs if r["attack"] == a]
            na = len(ra) or 1
            axj[a] = {jn: round(1000.0 * sum(1 for r in ra if r["oracle_wrong"] and r["v"][jn]) / na, 1)
                      for jn in jnames}
        # judge x judge transfer: of exploits under src, fraction also exploits under dst
        tm = {}
        for src in jnames:
            src_ex = [r for r in recs if r["oracle_wrong"] and r["v"][src]]
            ns = len(src_ex)
            tm[src] = {dst: (round(sum(1 for r in src_ex if r["v"][dst]) / ns, 3) if ns else None)
                       for dst in jnames}
        per_bench[bid] = {"n_items": len(items), "n_records": len(recs),
                          "judge_density_per_1000": dens, "attack_by_judge": axj,
                          "transfer_matrix": tm}
    body = {
        "schema": "gradia-wind-tunnel-transfer.v1",
        "judges": {"deliberation": "reference-free, rewards deliberation phrasing",
                   "verification": "reference-free, rewards verification/rigor rhetoric",
                   "permissive": "reference-free, rewards either family (union)",
                   "verifier": "structural: passes only if independently oracle-correct"},
        "seed": seed, "benchmarks": per_bench,
        "interpretation": (
            "Cross-transfer between judges that reward DISJOINT signal families is near zero "
            "(an exploit is signal-specific), yet every reference-free judge has SOME attack "
            "(paradigm-level gameability); the independent verifier passes none of the "
            "wrong-by-construction attacks (density 0) -- the paradigm-level defense."),
    }
    body["report_sha256"] = digest(body)
    return body
