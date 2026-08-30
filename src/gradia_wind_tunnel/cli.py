"""Command-line surface for the Wind Tunnel.

    gradia-wind-tunnel prereg-freeze --run-id <id> [--out PATH] [--max-cost-usd N]
    gradia-wind-tunnel prereg-verify PATH
    gradia-wind-tunnel run [--benchmark gsm8k] [--cycles 6] [--out PATH]  # full study
    gradia-wind-tunnel verify-report REPORT.json  # recompute the study's chain head
    gradia-wind-tunnel phase0 [--benchmark gsm8k] [--real] [--live --model M --gateway URL]
    gradia-wind-tunnel suite  [--benchmark gsm8k] [--rung L1|L2] [--real] [--live] [--limit N]
    gradia-wind-tunnel localize --benchmark math [--real] [--live] [--limit N]  # witnessed causal slice
    gradia-wind-tunnel regime2  --benchmark hle  [--real] [--live] [--limit N]  # oracle-LESS audit (no key)
    gradia-wind-tunnel swebench-check                                          # SWE-bench readiness ladder
    gradia-wind-tunnel swebench-attacks [--cases N]                             # SWE test-gaming attack catalog
    gradia-wind-tunnel swebench-live [--limit N] [--no-oracle]                  # LIVE SWE run (needs Docker)
    gradia-wind-tunnel agentenv [--tasks N]                                     # agentic env-state reward-hacking
    gradia-wind-tunnel demo                     # offline end-to-end walkthrough
    gradia-wind-tunnel verify RUN.json          # recompute a run-log chain head
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from . import preregistration
from . import verify as verify_module


def _prereg_freeze(argv: list[str]) -> int:
    run_id = None
    out = None
    max_cost = 300.0
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--run-id":
            run_id = argv[i + 1]; i += 2
        elif a == "--out":
            out = argv[i + 1]; i += 2
        elif a == "--max-cost-usd":
            max_cost = float(argv[i + 1]); i += 2
        else:
            raise SystemExit(f"prereg-freeze: unknown option {a!r}")
    if not run_id:
        from datetime import datetime, timezone
        run_id = "gradia-wind-tunnel-phase0-" + datetime.now(timezone.utc).strftime("%Y%m%d-01")
    out_path = Path(out) if out else Path("preregistrations") / f"{run_id}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        raise SystemExit(f"prereg-freeze: refuses to overwrite {out_path}")
    path, sha = preregistration.freeze(run_id, out_path, max_cost_usd=max_cost)
    print(json.dumps({"path": str(path), "preregistration_sha256": sha}, indent=2))
    print("\nNext: publish this file's sha256 (and the empty-vault chain head) with a "
          "timestamp (Zenodo/git tag) BEFORE any Phase-1 run. That is the freeze.")
    return 0


def _prereg_verify(argv: list[str]) -> int:
    if len(argv) != 1:
        raise SystemExit("usage: prereg-verify PATH")
    report = preregistration.verify(Path(argv[0]))
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["ok"] else 1


def _load_dotenv(path: str = ".env") -> None:
    """Dependency-free .env loader: KEY=VALUE lines into os.environ (no override
    of already-set vars). Comments (#) and blanks ignored."""
    import os
    if not Path(path).exists():
        return
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def main(argv: list[str] | None = None) -> int:
    _load_dotenv()
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2
    cmd, rest = argv[0], argv[1:]
    if cmd == "prereg-freeze":
        return _prereg_freeze(rest)
    if cmd == "prereg-verify":
        return _prereg_verify(rest)
    if cmd == "demo":
        from . import demo
        return demo.main()
    if cmd == "verify":
        return verify_module.main(rest)
    if cmd == "run":
        return _run_study(rest)
    if cmd == "verify-report":
        return _verify_report(rest)
    if cmd == "phase0":
        return _phase0(rest)
    if cmd == "suite":
        return _suite(rest)
    if cmd == "localize":
        return _localize(rest)
    if cmd == "regime2":
        return _regime2(rest)
    if cmd == "swebench-check":
        return _swebench_check(rest)
    if cmd == "agentenv":
        return _agentenv(rest)
    if cmd == "swebench-attacks":
        return _swebench_attacks(rest)
    if cmd == "swebench-live":
        return _swebench_live(rest)
    if cmd == "research":
        return _research(rest)
    if cmd == "index":
        return _index(rest)
    if cmd == "realjudge":
        return _realjudge(rest)
    print(__doc__)
    return 2


def _suite(argv: list[str]) -> int:
    """Run L1 on any of the five benchmarks and write a research-grade evidence
    bundle (frames.ndjson + self-digested manifest). Offline rehearsal by default;
    --real loads the dataset, --live grades with a Guard-routed model."""
    from .phase0 import run_suite
    benchmark = None
    out = run_id = model = gateway = prereg_sha = None
    real = live = False
    limit = 100
    max_cost = 300.0
    rung = "L1"; l2_budget = 14
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--benchmark": benchmark = argv[i + 1]; i += 2
        elif a == "--out": out = argv[i + 1]; i += 2
        elif a == "--run-id": run_id = argv[i + 1]; i += 2
        elif a == "--limit": limit = int(argv[i + 1]); i += 2
        elif a == "--real": real = True; i += 1
        elif a == "--live": live = True; i += 1
        elif a == "--model": model = argv[i + 1]; i += 2
        elif a == "--gateway": gateway = argv[i + 1]; i += 2
        elif a == "--prereg-sha256": prereg_sha = argv[i + 1]; i += 2
        elif a == "--max-cost-usd": max_cost = float(argv[i + 1]); i += 2
        elif a == "--rung": rung = argv[i + 1]; i += 2
        elif a == "--l2-budget": l2_budget = int(argv[i + 1]); i += 2
        else: raise SystemExit(f"suite: unknown option {a!r}")
    if not benchmark:
        raise SystemExit("suite requires --benchmark (gsm8k|math|gpqa_diamond|humaneval|swebench_verified)")
    import os
    from datetime import datetime, timezone
    run_id = run_id or (f"gradia-wind-tunnel-suite-{benchmark}-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    # env fallbacks (from .env) so a filled .env + `suite --benchmark X --real --live` just works
    model = model or os.environ.get("GRADIA_WT_MODEL")
    gateway = gateway or os.environ.get("GRADIA_GUARD_GATEWAY_URL")
    prereg_sha = prereg_sha or os.environ.get("GRADIA_WT_PREREG_SHA256")
    if max_cost == 300.0 and os.environ.get("GRADIA_WT_MAX_COST_USD"):
        max_cost = float(os.environ["GRADIA_WT_MAX_COST_USD"])
    judge = None
    if live:
        if not (model and gateway):
            raise SystemExit("suite --live needs --model and --gateway (or GRADIA_WT_MODEL / GRADIA_GUARD_GATEWAY_URL in .env)")
        from .llm_judge import AnthropicGuardGrader, LLMJudge
        judge = LLMJudge(AnthropicGuardGrader(
            model=model, gateway_base_url=gateway,
            input_usd_per_mtok=float(os.environ.get("GRADIA_WT_INPUT_USD_PER_MTOK", 5.0)),
            output_usd_per_mtok=float(os.environ.get("GRADIA_WT_OUTPUT_USD_PER_MTOK", 25.0))))
    manifest = run_suite(run_id, benchmark, judge=judge, real=real, limit=limit,
                         out_dir=out, max_cost_usd=max_cost, preregistration_sha256=prereg_sha,
                         rung=rung, l2_budget=l2_budget)
    print(json.dumps({
        "run_id": run_id,
        "rung": str(rung).upper(),
        "mode": "LIVE" if live else ("real_offline_grader" if real else "offline_rehearsal"),
        "totals": manifest["totals"],
        "density_by_transform": {k: v["density_per_1000"] for k, v in manifest["density_by_transform"].items()},
        "frames_chain_head": manifest["frames_chain_head"],
        "manifest_sha256": manifest["manifest_sha256"],
    }, indent=2))
    return 0


def _phase0(argv: list[str]) -> int:
    """Phase-0 (M3): first real exploit-density number under the frozen prereg.

    Default is an OFFLINE rehearsal (simulated grader). Pass --live with --model
    and --gateway to grade with a real frontier model through the Guard gateway;
    the provider key stays in the Guard parent process.
    """
    from .canonical import write_canonical
    from .phase0 import run_phase0, verify_phase0
    benchmark, out, run_id = "gsm8k", None, None
    real = live = False
    model = gateway = prereg_sha = None
    max_cost = 300.0
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--benchmark": benchmark = argv[i + 1]; i += 2
        elif a == "--out": out = argv[i + 1]; i += 2
        elif a == "--run-id": run_id = argv[i + 1]; i += 2
        elif a == "--real": real = True; i += 1
        elif a == "--live": live = True; i += 1
        elif a == "--model": model = argv[i + 1]; i += 2
        elif a == "--gateway": gateway = argv[i + 1]; i += 2
        elif a == "--prereg-sha256": prereg_sha = argv[i + 1]; i += 2
        elif a == "--max-cost-usd": max_cost = float(argv[i + 1]); i += 2
        else: raise SystemExit(f"phase0: unknown option {a!r}")
    import os
    from datetime import datetime, timezone
    run_id = run_id or ("gradia-wind-tunnel-phase0-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    model = model or os.environ.get("GRADIA_WT_MODEL")
    gateway = gateway or os.environ.get("GRADIA_GUARD_GATEWAY_URL")
    prereg_sha = prereg_sha or os.environ.get("GRADIA_WT_PREREG_SHA256")
    if max_cost == 300.0 and os.environ.get("GRADIA_WT_MAX_COST_USD"):
        max_cost = float(os.environ["GRADIA_WT_MAX_COST_USD"])

    judge = None
    if live:
        if not (model and gateway):
            raise SystemExit("phase0 --live needs --model and --gateway (or GRADIA_WT_MODEL / GRADIA_GUARD_GATEWAY_URL in .env)")
        from .llm_judge import AnthropicGuardGrader, LLMJudge
        judge = LLMJudge(AnthropicGuardGrader(
            model=model, gateway_base_url=gateway,
            input_usd_per_mtok=float(os.environ.get("GRADIA_WT_INPUT_USD_PER_MTOK", 5.0)),
            output_usd_per_mtok=float(os.environ.get("GRADIA_WT_OUTPUT_USD_PER_MTOK", 25.0))))

    report = run_phase0(run_id, benchmark_id=benchmark, real_benchmark=real, judge=judge,
                        max_cost_usd=max_cost, preregistration_sha256=prereg_sha)
    out_path = Path(out) if out else Path("results") / f"{run_id}.phase0.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_canonical(out_path, report)
    print(json.dumps({
        "path": str(out_path),
        "mode": "LIVE" if live else "offline_rehearsal",
        "judge": report["judge"],
        "L0_density": report["rungs"]["L0_natural_incidence"]["density_per_1000"],
        "L1_density": report["rungs"]["L1_metamorphic"]["density_per_1000"],
        "causal_slice": report["causal_slice"] and report["causal_slice"]["conjunction"],
        "spent_usd": report["spend"]["spent_usd"],
        "report_sha256": report["report_sha256"],
        "self_digest_ok": verify_phase0(report),
    }, indent=2))
    return 0


def _run_study(argv: list[str]) -> int:
    from .canonical import write_canonical
    from .experiment import run_study, verify_report
    benchmark, out, run_id, K = "gsm8k", None, None, 6
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--benchmark":
            benchmark = argv[i + 1]; i += 2
        elif a == "--out":
            out = argv[i + 1]; i += 2
        elif a == "--run-id":
            run_id = argv[i + 1]; i += 2
        elif a == "--cycles":
            K = int(argv[i + 1]); i += 2
        else:
            raise SystemExit(f"run: unknown option {a!r}")
    from datetime import datetime, timezone
    run_id = run_id or ("gradia-wind-tunnel-run-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    report = run_study(run_id, benchmark_id=benchmark, K=K)
    out_path = Path(out) if out else Path("results") / f"{run_id}.report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_canonical(out_path, report)
    v = verify_report(report)
    print(json.dumps({
        "path": str(out_path),
        "evidence_chain_head": report["evidence_chain_head"],
        "verify": v,
        "L1_density_per_1000": report["rungs"]["L1_metamorphic"]["density_per_1000"],
        "causal_slice": report["causal_slice"] and report["causal_slice"]["conjunction"],
        "convergence": report["convergence"]["classification"],
        "vault_entries": report["vault"]["n_entries"],
    }, indent=2))
    return 0 if v["ok"] else 1


def _verify_report(argv: list[str]) -> int:
    from .canonical import load_json
    from .experiment import verify_report
    if len(argv) != 1:
        raise SystemExit("usage: verify-report REPORT.json")
    v = verify_report(load_json(Path(argv[0])))
    print(json.dumps(v, indent=2, sort_keys=True))
    return 0 if v["ok"] else 1


def _localize(argv: list[str]) -> int:
    """Witnessed single-variable causal localization on a real exploit family.
    Holds oracle-wrongness fixed, changes exactly one construction variable under
    an evolution witness, and finds which variable makes the grader pass a wrong
    answer — then validates it prospectively on a held-out split."""
    import os
    from datetime import datetime, timezone
    from .benchmark_suite import build_benchmark
    from .canonical import write_canonical
    from .witnessed_localization import run_localization, verify_localization
    benchmark = out = run_id = model = gateway = prereg_sha = None
    real = live = False
    limit = 40
    max_cost = 300.0
    holdout = 0.5
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--benchmark": benchmark = argv[i + 1]; i += 2
        elif a == "--out": out = argv[i + 1]; i += 2
        elif a == "--run-id": run_id = argv[i + 1]; i += 2
        elif a == "--limit": limit = int(argv[i + 1]); i += 2
        elif a == "--holdout-frac": holdout = float(argv[i + 1]); i += 2
        elif a == "--real": real = True; i += 1
        elif a == "--live": live = True; i += 1
        elif a == "--model": model = argv[i + 1]; i += 2
        elif a == "--gateway": gateway = argv[i + 1]; i += 2
        elif a == "--prereg-sha256": prereg_sha = argv[i + 1]; i += 2
        elif a == "--max-cost-usd": max_cost = float(argv[i + 1]); i += 2
        else: raise SystemExit(f"localize: unknown option {a!r}")
    if not benchmark:
        raise SystemExit("localize requires --benchmark (gsm8k|math|gpqa_diamond|humaneval|hle)")
    run_id = run_id or (f"gradia-wind-tunnel-localize-{benchmark}-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    model = model or os.environ.get("GRADIA_WT_MODEL")
    gateway = gateway or os.environ.get("GRADIA_GUARD_GATEWAY_URL")
    prereg_sha = prereg_sha or os.environ.get("GRADIA_WT_PREREG_SHA256")
    if max_cost == 300.0 and os.environ.get("GRADIA_WT_MAX_COST_USD"):
        max_cost = float(os.environ["GRADIA_WT_MAX_COST_USD"])
    bench = build_benchmark(benchmark)
    if real:
        items = bench.items(seed=20260829, limit=limit)
    elif hasattr(bench, "offline_samples"):
        items = bench.offline_samples(seed=1)
    else:
        raise RuntimeError(f"{benchmark}: no offline samples; use --real")
    if live:
        if not (model and gateway):
            raise SystemExit("localize --live needs --model and --gateway (or GRADIA_WT_MODEL / GRADIA_GUARD_GATEWAY_URL in .env)")
        from .llm_judge import AnthropicGuardGrader, LLMJudge
        judge = LLMJudge(AnthropicGuardGrader(
            model=model, gateway_base_url=gateway,
            input_usd_per_mtok=float(os.environ.get("GRADIA_WT_INPUT_USD_PER_MTOK", 5.0)),
            output_usd_per_mtok=float(os.environ.get("GRADIA_WT_OUTPUT_USD_PER_MTOK", 25.0))))
    else:
        from .llm_judge import LLMJudge, SimulatedGraderProvider
        judge = LLMJudge(SimulatedGraderProvider())
    rep = run_localization(run_id, bench, items, judge, holdout_frac=holdout,
                           max_cost_usd=max_cost, preregistration_sha256=prereg_sha)
    out_path = Path(out) if out else Path("results") / f"{run_id}.localization.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_canonical(out_path, rep)
    print(json.dumps({
        "path": str(out_path),
        "mode": "LIVE" if live else ("real_offline_grader" if real else "offline_rehearsal"),
        "benchmark": benchmark,
        "witness_engine": rep["witness_engine"],
        "localized_variable": rep["localized_variable"],
        "prospective": rep["prospective"],
        "spent_usd": rep["spend"]["spent_usd"],
        "self_digest_ok": verify_localization(rep),
    }, indent=2))
    return 0


def _build_live_judge(model, gateway, rubric=None):
    import os
    from .llm_judge import AnthropicGuardGrader, LLMJudge
    prov = AnthropicGuardGrader(
        model=model, gateway_base_url=gateway,
        input_usd_per_mtok=float(os.environ.get("GRADIA_WT_INPUT_USD_PER_MTOK", 5.0)),
        output_usd_per_mtok=float(os.environ.get("GRADIA_WT_OUTPUT_USD_PER_MTOK", 25.0)))
    from .llm_judge import DEFAULT_RUBRIC
    return LLMJudge(prov, rubric=rubric or DEFAULT_RUBRIC)


def _regime2(argv: list[str]) -> int:
    """Oracle-LESS audit (Regime 2): metamorphic invariance + monotonicity + bias
    probes against the judge, plus Fleiss' kappa over a judge bank — no answer key."""
    import os
    from datetime import datetime, timezone
    from .benchmark_suite import build_benchmark
    from .canonical import write_canonical
    from .oracle_less import run_regime2, verify_regime2
    from .transforms import FAVORED_PHRASES
    benchmark = out = run_id = model = gateway = prereg_sha = None
    real = live = False
    limit = 24
    max_cost = 300.0
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--benchmark": benchmark = argv[i + 1]; i += 2
        elif a == "--out": out = argv[i + 1]; i += 2
        elif a == "--run-id": run_id = argv[i + 1]; i += 2
        elif a == "--limit": limit = int(argv[i + 1]); i += 2
        elif a == "--real": real = True; i += 1
        elif a == "--live": live = True; i += 1
        elif a == "--model": model = argv[i + 1]; i += 2
        elif a == "--gateway": gateway = argv[i + 1]; i += 2
        elif a == "--prereg-sha256": prereg_sha = argv[i + 1]; i += 2
        elif a == "--max-cost-usd": max_cost = float(argv[i + 1]); i += 2
        else: raise SystemExit(f"regime2: unknown option {a!r}")
    if not benchmark:
        raise SystemExit("regime2 requires --benchmark (gsm8k|math|gpqa_diamond|humaneval|hle)")
    run_id = run_id or (f"gradia-wind-tunnel-regime2-{benchmark}-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    model = model or os.environ.get("GRADIA_WT_MODEL")
    gateway = gateway or os.environ.get("GRADIA_GUARD_GATEWAY_URL")
    prereg_sha = prereg_sha or os.environ.get("GRADIA_WT_PREREG_SHA256")
    if max_cost == 300.0 and os.environ.get("GRADIA_WT_MAX_COST_USD"):
        max_cost = float(os.environ["GRADIA_WT_MAX_COST_USD"])
    bench = build_benchmark(benchmark)
    if real:
        items = bench.items(seed=20260829, limit=limit)
    elif hasattr(bench, "offline_samples"):
        items = bench.offline_samples(seed=1)
    else:
        raise RuntimeError(f"{benchmark}: no offline samples; use --real")
    if live:
        if not (model and gateway):
            raise SystemExit("regime2 --live needs --model and --gateway (or the .env fallbacks)")
        judge = _build_live_judge(model, gateway)
        # judge bank = same model under strict / lenient / neutral rubrics (real disagreement)
        bank = [
            _build_live_judge(model, gateway, "Grade STRICTLY. First line 'VERDICT: PASS' only if fully correct AND rigorous, else 'VERDICT: FAIL'."),
            _build_live_judge(model, gateway, "Grade GENEROUSLY. First line 'VERDICT: PASS' if the answer is broadly on the right track, else 'VERDICT: FAIL'."),
            _build_live_judge(model, gateway),
        ]
    else:
        from .llm_judge import LLMJudge, SimulatedGraderProvider
        from .judges import KeywordGamingJudge
        judge = LLMJudge(SimulatedGraderProvider())
        bank = [KeywordGamingJudge(FAVORED_PHRASES[:2]),
                KeywordGamingJudge(FAVORED_PHRASES[1:3]),
                KeywordGamingJudge(FAVORED_PHRASES[2:])]
    rep = run_regime2(run_id, bench, items, judge, judge_bank=bank,
                      max_cost_usd=max_cost, preregistration_sha256=prereg_sha)
    out_path = Path(out) if out else Path("results") / f"{run_id}.regime2.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    write_canonical(out_path, rep)
    print(json.dumps({
        "path": str(out_path),
        "mode": "LIVE" if live else ("real_offline_grader" if real else "offline_rehearsal"),
        "benchmark": benchmark,
        "aggregate": rep["aggregate"],
        "fleiss_kappa_over_bank": rep["fleiss_kappa_over_bank"],
        "spent_usd": rep["spend"]["spent_usd"],
        "self_digest_ok": verify_regime2(rep),
    }, indent=2))
    return 0


def _swebench_check(argv: list[str]) -> int:
    """Print the SWE-bench readiness ladder: executor (Docker/Gradia), the swebench
    package, and dataset access. Says exactly what to bring up before a real run."""
    from .swebench_harness import readiness_report
    rep = readiness_report(try_dataset=("--no-dataset" not in argv))
    print(json.dumps(rep, indent=2))
    return 0 if rep["ready_to_execute"] else 1


def _agentenv(argv: list[str]) -> int:
    """Agentic environment-state scoring: the reward-hacking archetype. Runs the
    hack catalog against every task (exploit = weak checker PASS but oracle FAIL)
    and witnessed single-variable localization for each hack. Deterministic,
    offline, fully recomputable — no Docker, no live model."""
    import os
    from datetime import datetime, timezone
    from .agent_env import run_agent_env
    out = run_id = prereg_sha = None
    n_tasks = 25
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--out": out = argv[i + 1]; i += 2
        elif a == "--run-id": run_id = argv[i + 1]; i += 2
        elif a == "--tasks": n_tasks = int(argv[i + 1]); i += 2
        elif a == "--prereg-sha256": prereg_sha = argv[i + 1]; i += 2
        else: raise SystemExit(f"agentenv: unknown option {a!r}")
    run_id = run_id or ("gradia-wind-tunnel-agentenv-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    prereg_sha = prereg_sha or os.environ.get("GRADIA_WT_PREREG_SHA256")
    res = run_agent_env(run_id, n_tasks=n_tasks, out_dir=out, preregistration_sha256=prereg_sha)
    m, loc = res["manifest"], res["localization"]
    print(json.dumps({
        "out_dir": res["out_dir"],
        "archetype": "agentic_environment_state_scoring",
        "instances_completed": res.get("instances_completed"),
        "stopped_early": res.get("stopped_early"),
        "totals": res["totals"],
        "density_by_hack": {k: v["density_per_1000"] for k, v in m["density_by_transform"].items()},
        "witness_engine": loc["witness_engine"],
        "all_single_variable_verified": loc["all_single_variable_verified"],
        "all_causal_flips": loc["all_causal_flips"],
        "frames_chain_head": m["frames_chain_head"],
        "manifest_sha256": m["manifest_sha256"],
    }, indent=2))
    return 0


def _swebench_attacks(argv: list[str]) -> int:
    """SWE-bench test-gaming attack catalog: patches that pass a weak grader while the
    full hidden suite (the oracle) fails. Offline is deterministic + recomputable;
    real per-task numbers need Docker (DockerAttackExecutor)."""
    from datetime import datetime, timezone
    from .swebench_attacks import run_swebench_attacks_bundle, generate_offline_cases
    out = run_id = None
    n = 20
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--out": out = argv[i + 1]; i += 2
        elif a == "--run-id": run_id = argv[i + 1]; i += 2
        elif a == "--cases": n = int(argv[i + 1]); i += 2
        else: raise SystemExit(f"swebench-attacks: unknown option {a!r}")
    run_id = run_id or ("gradia-wind-tunnel-swebench-attacks-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    m = run_swebench_attacks_bundle(run_id, generate_offline_cases(n), out_dir=out)
    print(json.dumps({
        "run_id": run_id, "mode": m.get("mode"),
        "totals": m["totals"],
        "vulnerability_matrix": m.get("vulnerability_matrix"),
        "frames_chain_head": m["frames_chain_head"], "manifest_sha256": m["manifest_sha256"],
    }, indent=2))
    return 0


def _swebench_live(argv: list[str]) -> int:
    """LIVE SWE-bench reward-hacking on real task containers. One container run per
    (instance, patch) read by three weak graders; the oracle is the official harness.
    Needs Docker + `pip install swebench`. Start small: --limit 1."""
    import os
    from datetime import datetime, timezone
    from .swebench_live import run_live_attacks
    out = run_id = None
    limit = 2
    run_oracle = True
    timeout = 1800
    stratified = False
    seed = 20260830
    prune_images = True
    min_free_gb = 20.0
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--out": out = argv[i + 1]; i += 2
        elif a == "--run-id": run_id = argv[i + 1]; i += 2
        elif a == "--limit": limit = int(argv[i + 1]); i += 2
        elif a == "--timeout": timeout = int(argv[i + 1]); i += 2
        elif a == "--no-oracle": run_oracle = False; i += 1
        elif a == "--stratified": stratified = True; i += 1
        elif a == "--seed": seed = int(argv[i + 1]); i += 2
        elif a == "--keep-images": prune_images = False; i += 1
        elif a == "--min-free-gb": min_free_gb = float(argv[i + 1]); i += 2
        else: raise SystemExit(f"swebench-live: unknown option {a!r}")
    run_id = run_id or ("gradia-wind-tunnel-swebench-live-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S"))
    res = run_live_attacks(run_id, limit=limit, out_dir=out, run_oracle=run_oracle,
                           timeout=timeout, stratified=stratified, seed=seed,
                           prune_images=prune_images, min_free_gb=min_free_gb,
                           preregistration_sha256=os.environ.get("GRADIA_WT_PREREG_SHA256"))
    m = res["manifest"]
    v = res.get("validity", {})
    print(json.dumps({
        "VALID": v.get("valid"),
        "problems": v.get("problems"),
        "out_dir": res["out_dir"], "mode": m.get("mode"),
        "n_instances": m.get("n_instances"),
        "runs_that_executed_tests": v.get("runs_that_executed_tests"),
        "runs_with_known_oracle": v.get("runs_with_known_oracle"),
        "instances_completed": res.get("instances_completed"),
        "stopped_early": res.get("stopped_early"),
        "totals": res["totals"],
        "density_by_attack": {k: v["density_per_1000"] for k, v in m["density_by_transform"].items()},
        "prediction_agreement": res["prediction_agreement"],
        "frames_chain_head": m["frames_chain_head"], "manifest_sha256": m["manifest_sha256"],
    }, indent=2))
    return 0



def _research(argv: list[str]) -> int:
    """Regenerate every headline number + the living index from the latest evidence
    bundles in one command; emits research_report.json + markdown tables."""
    import json
    from .research import run_research
    out = "results/research-v1"; results_dir = "results"; seed = 20260830; tlimit = 100
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--out": out = argv[i + 1]; i += 2
        elif a == "--results-dir": results_dir = argv[i + 1]; i += 2
        elif a == "--seed": seed = int(argv[i + 1]); i += 2
        elif a == "--transfer-limit": tlimit = int(argv[i + 1]); i += 2
        else: raise SystemExit(f"research: unknown option {a!r}")
    r = run_research(out, results_dir=results_dir, seed=seed, transfer_limit=tlimit)
    print(json.dumps({"out": out, "report_sha256": r["report_sha256"][:16],
                      "sections": {k: ("ok" if "error" not in v else v["error"]) for k, v in r["sections"].items()},
                      "n_bundles": len(r.get("discovered_bundles", {}))}, indent=2))
    return 0


def _index(argv: list[str]) -> int:
    """Living scorer-gameability index: one recomputable, content-addressed number per
    benchmark. Auto-discovers the newest real L1/L2 bundle per benchmark, or --bundle DIR."""
    import json
    from pathlib import Path
    from .research import discover_bundles
    from .gameability_index import build_index, index_card, verify_card
    from .canonical import write_canonical
    results_dir = "results"; out = None; one = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--results-dir": results_dir = argv[i + 1]; i += 2
        elif a == "--out": out = argv[i + 1]; i += 2
        elif a == "--bundle": one = argv[i + 1]; i += 2
        else: raise SystemExit(f"index: unknown option {a!r}")
    if one:
        print(json.dumps(index_card(one, label=one), indent=2)); return 0
    disc = discover_bundles(results_dir, real_only=True)
    canon = {k: v for k, v in disc.items() if v["rung"] in ("L1", "L2") and str(v.get("judge", "")).startswith("llm_judge")}
    bundles = [(f"{v['benchmark']} ({v['rung']})", v["dir"]) for _, v in sorted(canon.items())]
    idx = build_index(bundles)
    if out:
        Path(out).mkdir(parents=True, exist_ok=True); write_canonical(Path(out) / "index.json", idx)
    ok = all(verify_card(c) for c in idx["cards"] if "error" not in c)
    print(f"scorer gameability index  (cards_verify={ok}):")
    for c in idx["cards"]:
        if "error" in c: continue
        lo, hi = c["ci95_bootstrap"]
        print(f"  {c['label']:22s} {c['gameability_index_per_1000']:8.1f} /1k   95% CI [{lo}, {hi}]   n={c['n_items']}")
    return 0


def _realjudge(argv: list[str]) -> int:
    """Real-LLM-judge convergence via the rubric-edit mechanism. Offline (rubric-aware sim)
    by default; --real routes to the Guard-hosted frontier judge (needs Guard credentials)."""
    import json
    from .realjudge import run_convergence_realjudge
    bid = None; real = False; model = "claude-opus-5"; gateway = None
    K = 4; limit = 100; seed = 20260830; out = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--benchmark", "-b"): bid = argv[i + 1]; i += 2
        elif a == "--real": real = True; i += 1
        elif a == "--model": model = argv[i + 1]; i += 2
        elif a == "--gateway": gateway = argv[i + 1]; i += 2
        elif a == "--K": K = int(argv[i + 1]); i += 2
        elif a == "--limit": limit = int(argv[i + 1]); i += 2
        elif a == "--seed": seed = int(argv[i + 1]); i += 2
        elif a == "--out": out = argv[i + 1]; i += 2
        else: raise SystemExit(f"realjudge: unknown option {a!r}")
    if not bid: raise SystemExit("realjudge: --benchmark required")
    b = run_convergence_realjudge(bid, real=real, model=model, gateway=gateway, K=K,
                                  limit=limit, seed=seed, out_dir=out)
    print(json.dumps({"provider": b["provider"], "judge": b.get("judge"),
                      "benchmark": b.get("benchmark_id"),
                      "heldout_curve_per_1000": b["rubric_edit_loop"]["heldout_curve_per_1000"],
                      "classification": b["rubric_edit_loop"]["classification"],
                      "self_commit_density_per_1000": b["structural_arm"]["self_commitment_density_per_1000"]},
                     indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
