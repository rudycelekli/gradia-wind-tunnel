"""Machine-readable boundary between Wind Tunnel evidence and roadmap claims.

This is deliberately an audit, not marketing copy. A capability is marked
``demonstrated_live`` only when a real provider/runtime evidence bundle exists;
offline controls, wiring and designs have distinct states. The same artifact
maps the apparatus to five public benchmark-program archetypes without claiming
that a generic adapter replaces domain experts or their source rights.
"""

from __future__ import annotations

from typing import Any

from .canonical import digest

_CAPABILITY_IDS = {
    "ambitious_rl_environments",
    "automatic_behavior_exploration",
    "measurement_scalability_reliability_variance",
    "steer_large_training_runs",
    "continuous_evaluation",
    "self_improvement_loops",
}
_ARCHETYPE_IDS = {
    "gdpval",
    "swe_bench_verified",
    "mle_bench",
    "paperbench",
    "swe_lancer",
}


def _capability_rows() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": "ambitious_rl_environments",
            "state": "demonstrated_offline",
            "evidence_refs": [
                "src/gradia_wind_tunnel/agent_env.py",
                "src/gradia_wind_tunnel/witness_engine.py",
                "src/gradia_wind_tunnel/swebench_live.py",
            ],
            "demonstrated": "Oracle-witnessed environment-state attacks, causal forks, and live SWE execution.",
            "open_gate": "No completed training loop has consumed Wind Tunnel curricula and measured downstream frontier-model lift.",
            "claim_boundary": "environment metrology demonstrated; frontier RL training impact unmeasured",
        },
        {
            "requirement_id": "automatic_behavior_exploration",
            "state": "demonstrated_live",
            "evidence_refs": [
                "src/gradia_wind_tunnel/adversary.py",
                "src/gradia_wind_tunnel/phase0.py",
                "results/research-v1/research_report.json",
            ],
            "demonstrated": "Bounded L0-L2 search has produced real model-judge exploit evidence across public benchmarks.",
            "open_gate": "L2 explores a typed candidate catalog; it is not an unconstrained model-authored research agent.",
            "claim_boundary": "bounded adaptive exploration demonstrated; autonomous hypothesis generation pending",
        },
        {
            "requirement_id": "measurement_scalability_reliability_variance",
            "state": "demonstrated_live",
            "evidence_refs": [
                "src/gradia_wind_tunnel/stats.py",
                "src/gradia_wind_tunnel/capture.py",
                "src/gradia_wind_tunnel/witnessed_localization.py",
                "paper/WIND-TUNNEL-PAPER-FULL.md",
            ],
            "demonstrated": "Hash-chained attempts, control audits, bootstrap intervals, transfer tests, and explicit inconclusive dispositions.",
            "open_gate": "Several causal slices remain underpowered and require preregistered larger prospective arms.",
            "claim_boundary": "instrument reliability measured; mechanism claims remain power- and control-gated",
        },
        {
            "requirement_id": "steer_large_training_runs",
            "state": "wired_unproven",
            "evidence_refs": [
                "src/gradia_wind_tunnel/patcher.py",
                "src/gradia_wind_tunnel/convergence.py",
                "../gradia/gradia/training/steering.py",
            ],
            "demonstrated": "Exploit families can produce fail-closed, pre-results training-study orders with rights, split, variance and safety gates.",
            "open_gate": "No external trainer, open reward model, or frontier training run has executed an authorized order.",
            "claim_boundary": "training proposal compiled; training execution and realized lift not demonstrated",
        },
        {
            "requirement_id": "continuous_evaluation",
            "state": "demonstrated_live",
            "evidence_refs": [
                "src/gradia_wind_tunnel/vault.py",
                "src/gradia_wind_tunnel/research.py",
                "run_research.sh",
            ],
            "demonstrated": "Append-only regression vaults, resumable suites, living indexes, and one-command aggregate regeneration.",
            "open_gate": "Managed scheduling, alerting and retention still require a deployed cross-repo integration proof.",
            "claim_boundary": "continuous local evaluation demonstrated; managed production SLO unproven",
        },
        {
            "requirement_id": "self_improvement_loops",
            "state": "demonstrated_offline",
            "evidence_refs": [
                "src/gradia_wind_tunnel/patcher.py",
                "src/gradia_wind_tunnel/convergence.py",
                "src/gradia_wind_tunnel/vault.py",
            ],
            "demonstrated": "Attack, deterministic patch, held-out re-attack, autoimmunity measurement, and regression retention run end to end.",
            "open_gate": "Current curriculum and rubric repair arms are controlled simulators, not learned optimizer updates.",
            "claim_boundary": "evaluation self-hardening demonstrated offline; model self-improvement not claimed",
        },
    ]


def _archetype_rows() -> list[dict[str, Any]]:
    return [
        {
            "archetype_id": "gdpval",
            "state": "wired_unproven",
            "covered": ["expert task seeds", "multi-format assets", "rubrics", "blind review", "model panels"],
            "missing": ["domain-specific expert corpus", "multi-round source validation", "human baseline per occupation"],
            "expert_required": True,
        },
        {
            "archetype_id": "swe_bench_verified",
            "state": "demonstrated_live",
            "covered": ["repository runtime", "test oracle", "test-gaming attacks", "clean-control exclusion", "resumable execution"],
            "missing": ["one unified adapter surface; the legacy scaffold remains separate from the live harness"],
            "expert_required": True,
        },
        {
            "archetype_id": "mle_bench",
            "state": "designed",
            "covered": ["research_gpu archetype", "sandbox and sidecar contracts", "spend and runtime evidence"],
            "missing": ["competition dataset adapter", "GPU experiment ledger", "leaderboard-normalized human baseline", "resource-scaling study"],
            "expert_required": True,
        },
        {
            "archetype_id": "paperbench",
            "state": "designed",
            "covered": ["hierarchical rubrics", "long-horizon execution", "judge admission", "human review"],
            "missing": ["paper asset resolver", "author-rubric kit", "research-compute adapter", "PhD baseline workflow proof"],
            "expert_required": True,
        },
        {
            "archetype_id": "swe_lancer",
            "state": "designed",
            "covered": ["real-work provenance", "rights envelopes", "offline runtimes", "deterministic and human decisions"],
            "missing": ["labor-market intake", "economic-value labels", "managerial choice adapter", "triple-verification operations"],
            "expert_required": True,
        },
    ]


def build_program_readiness() -> dict[str, Any]:
    body: dict[str, Any] = {
        "schema_version": "gradia-wind-tunnel-program-readiness.v1",
        "status": "evidence_bounded",
        "capabilities": _capability_rows(),
        "benchmark_archetypes": _archetype_rows(),
        "training_dispatch_authorized": False,
        "general_claim": (
            "Gradia provides a common environment/evidence grammar for these programs; "
            "each program still requires its own rights-clean corpus, domain experts, "
            "runtime adapter, oracle validation, and human baseline."
        ),
    }
    body["readiness_sha256"] = digest(body)
    return body


def verify_program_readiness(value: dict[str, Any]) -> dict[str, Any]:
    stored = value.get("readiness_sha256")
    recomputed = digest({key: item for key, item in value.items() if key != "readiness_sha256"})
    states = {
        "demonstrated_live",
        "demonstrated_offline",
        "wired_unproven",
        "designed",
        "blocked",
    }
    capabilities = value.get("capabilities") or []
    archetypes = value.get("benchmark_archetypes") or []
    rows = [*capabilities, *archetypes]
    state_ok = bool(rows) and all(isinstance(row, dict) and row.get("state") in states for row in rows)
    capability_ids = [row.get("requirement_id") for row in capabilities if isinstance(row, dict)]
    archetype_ids = [row.get("archetype_id") for row in archetypes if isinstance(row, dict)]
    coverage_ok = (
        len(capability_ids) == len(set(capability_ids)) == len(_CAPABILITY_IDS)
        and set(capability_ids) == _CAPABILITY_IDS
        and len(archetype_ids) == len(set(archetype_ids)) == len(_ARCHETYPE_IDS)
        and set(archetype_ids) == _ARCHETYPE_IDS
    )
    boundaries_ok = all(
        row.get("claim_boundary") and row.get("open_gate")
        for row in capabilities
    )
    schema_ok = value.get("schema_version") == "gradia-wind-tunnel-program-readiness.v1"
    dispatch_ok = value.get("training_dispatch_authorized") is False
    return {
        "ok": (
            stored == recomputed
            and state_ok
            and coverage_ok
            and boundaries_ok
            and schema_ok
            and dispatch_ok
        ),
        "self_digest_ok": stored == recomputed,
        "states_ok": state_ok,
        "coverage_ok": coverage_ok,
        "claim_boundaries_ok": boundaries_ok,
        "schema_ok": schema_ok,
        "training_dispatch_refused": dispatch_ok,
        "stored_sha256": stored,
        "recomputed_sha256": recomputed,
    }
