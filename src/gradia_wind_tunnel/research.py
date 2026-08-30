"""Master research orchestrator -- regenerate every headline number, table, and the
living gameability index from the LATEST evidence bundles, in ONE call.

Auto-discovers the newest real bundle per (benchmark, rung) under results/, then
recomputes: the gameability index (density + bootstrap CI + provenance), the C2
convergence measurement, the adversary x judge transfer matrix, and the naturalness
sample + automated-screen baseline. Emits one self-digested research_report.json plus
auto-generated markdown tables. This is the 'one command to redo all numbers' that
keeps the paper in lockstep with the runs as SWE / HLE / L2 results land.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import digest, load_json, write_canonical


def discover_bundles(results_dir: str = "results", *, real_only: bool = True) -> dict[str, Any]:
    """Newest evidence bundle per (benchmark, rung): dir with frames.ndjson + manifest."""
    best: dict[str, Any] = {}
    root = Path(results_dir)
    if not root.exists():
        return best
    for man_path in root.rglob("manifest.json"):
        d = man_path.parent
        if not (d / "frames.ndjson").exists():
            continue
        try:
            man = load_json(man_path)
        except Exception:
            continue
        bid = man.get("benchmark_id")
        if not bid or "totals" not in man:
            continue
        if real_only and not man.get("benchmark_real", False):
            continue
        key = f"{bid}::{man.get('rung')}"
        mt = man_path.stat().st_mtime
        if key not in best or mt > best[key]["mtime"]:
            best[key] = {"mtime": mt, "dir": str(d), "benchmark": bid,
                         "rung": str(man.get("rung")), "judge": man.get("judge"),
                         "density_per_1000": man.get("totals", {}).get("overall_density_per_1000")}
    return best


def _markdown_tables(report: dict) -> dict[str, str]:
    tabs: dict[str, str] = {}
    idx = report["sections"].get("gameability_index", {})
    if "cards" in idx:
        rows = ["| Benchmark | Rung | Judge | Gameability /1k | 95% CI | n |",
                "|---|---|---|---:|---|---:|"]
        for c in idx["cards"]:
            if "error" in c:
                continue
            lo, hi = c["ci95_bootstrap"]
            rows.append(f"| {c.get('label')} | {c.get('rung')} | {c.get('judge')} | "
                        f"{c['gameability_index_per_1000']} | [{lo}, {hi}] | {c['n_items']} |")
        tabs["table_gameability_index.md"] = "\n".join(rows) + "\n"
    conv = report["sections"].get("convergence", {})
    if "rubric_edit_loop" in conv:
        L, M = conv["rubric_edit_loop"], conv["modality_contrast"]
        md = [f"**Convergence (C2)** — substrate: {conv['substrate']}", "",
              f"- held-out curve (/1k): {L['heldout_curve_per_1000']} → **{L['classification']}**, "
              f"γ_local = {L['gamma_local_mean']}", "",
              "| Patch modality | closure Δ⁺/1k | autoimmunity Δ⁻ | γ | post global /1k | reduction /1k |",
              "|---|---:|---:|---:|---:|---:|"]
        for m, v in M.items():
            md.append(f"| {m} | {v['closure_delta_per_1000']} | {v['autoimmunity_delta']} | "
                      f"{v['generalization_gamma']} | {v['post_patch_global_density_per_1000']} | "
                      f"{v['global_reduction_per_1000']} |")
        tabs["table_convergence.md"] = "\n".join(md) + "\n"
    tr = report["sections"].get("transfer", {})
    if "benchmarks" in tr:
        md = ["**Transfer** — judge exploit density (/1k) by benchmark", "",
              "| Benchmark | deliberation | verification | permissive | verifier |",
              "|---|---:|---:|---:|---:|"]
        for bid, d in tr["benchmarks"].items():
            if "error" in d:
                continue
            jd = d["judge_density_per_1000"]
            md.append(f"| {bid} | {jd['deliberation']} | {jd['verification']} | "
                      f"{jd['permissive']} | {jd['verifier']} |")
        tabs["table_transfer.md"] = "\n".join(md) + "\n"
    return tabs


def run_research(out_dir: str, *, results_dir: str = "results", seed: int = 20260830,
                 transfer_benchmarks=("math", "gsm8k", "gpqa_diamond", "humaneval"),
                 transfer_limit: int = 100, conv_per_cell: int = 24, K: int = 5,
                 n_boot: int = 5000) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": "gradia-wind-tunnel-research.v1",
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "seed": seed, "sections": {},
    }
    disc = discover_bundles(results_dir, real_only=True)
    report["discovered_bundles"] = {k: {kk: v[kk] for kk in ("benchmark", "rung", "judge", "density_per_1000", "dir")}
                                    for k, v in sorted(disc.items())}
    # 1) gameability index + CIs over discovered real bundles
    try:
        from .gameability_index import build_index
        canon = {k: v for k, v in disc.items()
                 if v["rung"] in ("L1", "L2") and str(v.get("judge", "")).startswith("llm_judge")}
        bundles = [(f"{v['benchmark']} ({v['rung']})", v["dir"]) for _, v in sorted(canon.items())]
        report["sections"]["gameability_index"] = build_index(bundles, n_boot=n_boot)
        report["archetype_bundles"] = {k: v["dir"] for k, v in sorted(disc.items())
                                       if not (v["rung"] in ("L1", "L2") and str(v.get("judge", "")).startswith("llm_judge"))}
    except Exception as e:
        report["sections"]["gameability_index"] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}
    # 2) convergence (procedural mechanism)
    try:
        from .items import generate_factorial
        from .convergence_report import run_convergence_report
        items = generate_factorial(seed=seed, per_cell=conv_per_cell)
        gold = {it.question: it.gold for it in items}
        report["sections"]["convergence"] = run_convergence_report(items, gold, seed=seed, K=K)
    except Exception as e:
        report["sections"]["convergence"] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}
    # 3) transfer matrix
    try:
        from .transfer import run_transfer
        report["sections"]["transfer"] = run_transfer(list(transfer_benchmarks), seed=seed, limit=transfer_limit)
    except Exception as e:
        report["sections"]["transfer"] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}
    # 4) naturalness
    try:
        from .naturalness import sample_exploit_answers, screen_baseline
        s = sample_exploit_answers(list(transfer_benchmarks), n_per_benchmark=20, seed=seed, limit=transfer_limit)
        report["sections"]["naturalness"] = {"n_samples": len(s), "screen_baseline": screen_baseline(s)}
    except Exception as e:
        report["sections"]["naturalness"] = {"error": f"{type(e).__name__}: {str(e)[:160]}"}

    report["report_sha256"] = digest(report)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    write_canonical(out / "research_report.json", report)
    for name, md in _markdown_tables(report).items():
        (out / name).write_text(md)
    return report
