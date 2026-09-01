"""End-to-end orchestrator: run the whole Wind Tunnel study and emit a
self-verifying evidence bundle.

`run_study` composes every service — rungs L0-L2, causal localization with
prospective validation, the convergence loop, the hidden vault, and the analyst
extras — into one canonical, self-digested, git-pinned report whose evidence
chain head any third party recomputes offline. Runs fully offline on the
deterministic scorer; point `adapter` at a real benchmark and `judge` at a
Guard-routed model to collect real numbers with the same code.
"""

from __future__ import annotations

import subprocess
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from .adversary import BudgetMeter, run_L0, run_L1, run_L2
from .analyst import disagreement_detector, exploit_dna, exploitability_spectrum
from .benchmarks import BenchmarkAdapter, build_adapter
from .canonical import digest
from .causal import localize, prospective_validate
from .contracts import ANALYST_VERSION, SCHEMA_EPISODE, TRANSFORM_CATALOG_VERSION
from .convergence import run_convergence
from .judges import Judge, KeywordGamingJudge
from .transforms import FAVORED_PHRASES
from .vault import RegressionVault, verify_reveal
from .windtunnel import Episode, exploit_density


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "{{GIT_SHA}}"
    except Exception:
        return "{{GIT_SHA}}"


def _rung_summary(eps: list[Episode]) -> dict:
    return {
        "attempts": len(eps),
        "exploits": sum(1 for e in eps if e.is_exploit),
        "density_per_1000": round(exploit_density(eps), 1),
    }


def run_study(
    run_id: str,
    *,
    benchmark_id: str = "gsm8k",
    seed: int = 20260829,
    per_cell: int = 6,
    K: int = 6,
    l2_query_budget: int = 2000,
) -> dict[str, Any]:
    adapter: BenchmarkAdapter = build_adapter(benchmark_id)
    items = adapter.items(seed=seed, per_cell=per_cell)
    judge = KeywordGamingJudge(FAVORED_PHRASES)
    gold_by_q = {it.question: it.gold for it in items}

    # --- rungs --------------------------------------------------------------
    l0 = run_L0(items, judge, seed)
    l1 = run_L1(items, judge, seed)
    l2 = run_L2(items, judge, seed, BudgetMeter(max_queries=l2_query_budget))

    # --- causal localization + prospective validation -----------------------
    # localize on the exploiting transform for a clean factorial signal
    kw = [e for e in l1 if e.transform_id == "keyword_inflation"]
    sl = localize(kw or l1)
    if sl is not None:
        sl = prospective_validate(sl, judge, seed)

    # --- convergence (rubric-edit loop) + the structural-defense arm --------
    conv = run_convergence(items, "rubric_edit_loop", gold_by_q, seed, K=K)
    # self-commitment collapses reference-free gaming from cycle 1
    from .judges import SelfCommitmentJudge
    from .patcher import _family_density
    sc = SelfCommitmentJudge(solver=lambda q: gold_by_q[q])
    sc_density = round(_family_density(items, sc, FAVORED_PHRASES[0], seed), 1)

    # --- hidden regression vault -------------------------------------------
    vault = RegressionVault()
    for e in l1:
        if e.is_exploit:
            vault.append_exploit(e, cycle=1)
    revealed = vault.reveal()

    # --- analyst extras -----------------------------------------------------
    spectrum = exploitability_spectrum(l1, ("steps",))
    dna = exploit_dna(l1)
    ensemble: list[Judge] = [
        KeywordGamingJudge(FAVORED_PHRASES[:3]),
        KeywordGamingJudge(FAVORED_PHRASES[1:]),
        KeywordGamingJudge([FAVORED_PHRASES[0], FAVORED_PHRASES[3]]),
    ]
    disagreement = disagreement_detector(items, ensemble, seed)

    # --- assemble the report ------------------------------------------------
    body: dict[str, Any] = {
        "schema": "gradia-wind-tunnel-report.v1",
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_sha": _git_sha(),
        "benchmark_id": benchmark_id,
        "n_items": len(items),
        "versions": {
            "transform_catalog": TRANSFORM_CATALOG_VERSION,
            "analyst": ANALYST_VERSION,
            "episode_schema": SCHEMA_EPISODE,
        },
        "rungs": {
            "L0_natural_incidence": _rung_summary(l0),
            "L1_metamorphic": _rung_summary(l1),
            "L2_adaptive_search": _rung_summary(l2),
        },
        "causal_slice": (None if sl is None else {
            "conjunction": sl.conjunction,
            "density_in": sl.density_in,
            "density_out": sl.density_out,
            "prospective_density": sl.prospective_density,
            "broad_baseline_density": sl.broad_baseline_density,
            "random_baseline_density": sl.random_baseline_density,
            "lift_over_broad": sl.lift_over_broad,
            "lift_over_random": sl.lift_over_random,
            "validated": sl.validated,
        }),
        "convergence": {
            "architecture": conv.architecture,
            "heldout_curve": conv.heldout_curve,
            "classification": conv.classification,
            "mean_gamma": conv.mean_gamma,
            "cycles": [
                {"cycle": c.cycle, "patched_phrase": c.patched_phrase,
                 "heldout_density": c.heldout_density,
                 "patch": (None if c.patch is None else asdict(c.patch))}
                for c in conv.cycles
            ],
        },
        "structural_defense": {
            "architecture": "self_commitment",
            "family_density_per_1000": sc_density,   # expect 0: helps but see interpretation
            "note": "self-commitment collapses reference-free gaming; it does not prove a cure on judged benchmarks",
        },
        "vault": {
            "committed_empty_head": revealed["committed_empty_head"],
            "final_head": revealed["final_head"],
            "n_entries": revealed["n_entries"],
            "reveal_verifies": verify_reveal(revealed),
        },
        "exploitability_spectrum": spectrum,
        "exploit_dna": dna,
        "disagreement_detector": disagreement,
    }
    # evidence chain head over the whole ordered report body (the trust move)
    body["evidence_chain_head"] = digest(body)
    return body


def verify_report(body: dict[str, Any]) -> dict[str, Any]:
    stored = body.get("evidence_chain_head")
    recomputed = digest({k: v for k, v in body.items() if k != "evidence_chain_head"})
    vault_ok = bool(body.get("vault", {}).get("reveal_verifies"))
    return {
        "run_id": body.get("run_id"),
        "evidence_chain_head_ok": stored == recomputed,
        "vault_reveal_ok": vault_ok,
        "ok": stored == recomputed and vault_ok,
    }
