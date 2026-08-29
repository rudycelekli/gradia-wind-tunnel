"""Phase 0 (M3): the first REAL exploit-density number under the frozen prereg.

Runs the cheap, high-signal subset — L0 natural incidence and L1 metamorphic —
on a chosen benchmark with a chosen judge, plus causal localization, and emits a
self-digested report with cost tracking and a spend cap. Point `judge` at an
`LLMJudge(AnthropicGuardGrader(...))` and `adapter` at a real dataset to collect
real numbers; the same call runs offline with the simulated grader for rehearsal.

This is the one runtime swap that turns the demonstration into evidence.
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from typing import Any

from .adversary import run_L0, run_L1
from .benchmarks import build_adapter
from .canonical import digest
from .causal import localize, prospective_validate
from .judges import Judge, KeywordGamingJudge
from .llm_judge import LLMJudge, SimulatedGraderProvider
from .transforms import FAVORED_PHRASES
from .windtunnel import Episode, exploit_density


class SpendCapExceeded(RuntimeError):
    pass


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "{{GIT_SHA}}"
    except Exception:
        return "{{GIT_SHA}}"


def _summary(eps: list[Episode]) -> dict:
    return {"attempts": len(eps), "exploits": sum(e.is_exploit for e in eps),
            "density_per_1000": round(exploit_density(eps), 1)}


def run_phase0(
    run_id: str,
    *,
    benchmark_id: str = "gsm8k",
    real_benchmark: bool = False,
    judge: Judge | None = None,
    seed: int = 20260829,
    per_cell: int = 6,
    max_cost_usd: float = 300.0,
    preregistration_sha256: str | None = None,
) -> dict[str, Any]:
    """L0 + L1 + causal localization with a spend cap; returns a self-digested report."""
    adapter = build_adapter(benchmark_id, real=real_benchmark)
    items = adapter.items(seed=seed, per_cell=per_cell)
    judge = judge or LLMJudge(SimulatedGraderProvider())  # offline rehearsal default

    l0 = run_L0(items, judge, seed)
    _check_cost(judge, max_cost_usd)
    l1 = run_L1(items, judge, seed)
    _check_cost(judge, max_cost_usd)

    kw = [e for e in l1 if e.transform_id == "keyword_inflation"]
    sl = localize(kw or l1)
    if sl is not None:
        sl = prospective_validate(sl, judge, seed)

    body: dict[str, Any] = {
        "schema": "gradia-wind-tunnel-phase0.v1",
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_sha": _git_sha(),
        "preregistration_sha256": preregistration_sha256 or "{{FROZEN_PREREG_SHA256}}",
        "benchmark_id": benchmark_id,
        "benchmark_real": real_benchmark,
        "judge": getattr(judge, "name", judge.__class__.__name__),
        "n_items": len(items),
        "spend": {"max_cost_usd": max_cost_usd,
                  "spent_usd": round(getattr(judge, "total_cost_usd", 0.0), 4)},
        "rungs": {"L0_natural_incidence": _summary(l0), "L1_metamorphic": _summary(l1)},
        "causal_slice": (None if sl is None else {
            "conjunction": sl.conjunction, "prospective_density": sl.prospective_density,
            "random_baseline_density": sl.random_baseline_density,
            "lift_over_random": sl.lift_over_random, "validated": sl.validated,
        }),
        "interpretation": (
            "Observations under this exact frozen cell. Reports oracle-witnessed "
            "exploit incidence of the named benchmark's grader; not a claim about "
            "the model's general capability or the benchmark's overall worth."),
    }
    body["report_sha256"] = digest(body)
    return body


def _check_cost(judge: Judge, cap: float) -> None:
    spent = getattr(judge, "total_cost_usd", 0.0)
    if spent > cap:
        raise SpendCapExceeded(f"spend {spent:.2f} exceeded cap {cap:.2f}")


def run_suite(
    run_id: str,
    benchmark_id: str,
    *,
    judge: Judge | None = None,
    seed: int = 20260829,
    real: bool = False,
    limit: int = 100,
    out_dir: str | None = None,
    max_cost_usd: float = 300.0,
    preregistration_sha256: str | None = None,
) -> dict[str, Any]:
    """Run L1 on any of the five benchmarks via the shape-agnostic suite, and
    write a research-grade evidence bundle (frames.ndjson + self-digested
    manifest) so every reported number is recomputable. This is the path that
    scales the study across GSM8K / MATH / GPQA / HumanEval / SWE-bench."""
    from pathlib import Path
    from .benchmark_suite import build_benchmark, run_benchmark_l1
    from .capture import build_manifest, write_frames
    from .canonical import write_canonical
    from .llm_judge import LLMJudge, SimulatedGraderProvider

    bench = build_benchmark(benchmark_id)
    if real:
        items = bench.items(seed=seed, limit=limit)
    elif hasattr(bench, "offline_samples"):
        items = bench.offline_samples(seed=seed)
    else:
        raise RuntimeError(f"{benchmark_id}: no offline samples; run with real data (--real).")
    judge = judge or LLMJudge(SimulatedGraderProvider())

    episodes = run_benchmark_l1(bench, items, judge, seed)
    _check_cost(judge, max_cost_usd)

    out = Path(out_dir) if out_dir else Path("results") / run_id
    out.mkdir(parents=True, exist_ok=True)
    head = write_frames(out / "frames.ndjson", episodes)
    manifest = build_manifest({
        "run_id": run_id, "benchmark_id": benchmark_id, "benchmark_real": real,
        "judge": getattr(judge, "name", judge.__class__.__name__),
        "git_sha": _git_sha(),
        "preregistration_sha256": preregistration_sha256 or "{{FROZEN_PREREG_SHA256}}",
        "spend": {"max_cost_usd": max_cost_usd,
                  "spent_usd": round(getattr(judge, "total_cost_usd", 0.0), 4)},
        "interpretation": (
            "Oracle-witnessed exploit incidence of this benchmark's grader under the "
            "frozen cell; not a claim about model capability or benchmark worth."),
    }, episodes, head)
    write_canonical(out / "manifest.json", manifest)
    return manifest


def verify_phase0(body: dict[str, Any]) -> bool:
    stored = body.get("report_sha256")
    return stored == digest({k: v for k, v in body.items() if k != "report_sha256"})
