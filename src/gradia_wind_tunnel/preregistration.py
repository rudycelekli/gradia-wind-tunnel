"""Fail-closed preregistration for the Reward-Hacking Wind Tunnel.

Mirrors the program's proven prereg discipline (see gradia_universes): a
canonical-JSON document that is git-pinned, spend-capped, self-digested
(``preregistration_sha256``), and carries an explicit ``interpretation`` that
scopes exactly what claims the study may and may not emit. Freezing before any
Phase-1 result is what makes the convergence/causal/autoimmunity findings
credible and establishes precedence — open science as the priority claim.

Build:   python -m gradia_wind_tunnel.cli prereg-freeze --out preregistrations/<run_id>.json
Verify:  python -m gradia_wind_tunnel.cli prereg-verify preregistrations/<run_id>.json
"""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .canonical import digest, load_json, write_canonical
from .contracts import (
    ANALYST_VERSION,
    HYPOTHESES,
    ORACLE_SUITE_VERSION,
    SCHEMA_PREREGISTRATION,
    TARGET_BENCHMARKS,
    TRANSFORM_CATALOG_VERSION,
)
from .transforms import TRANSFORMS, FAVORED_PHRASES

# The empty Merkle root the hidden regression vault commits to on Day 1.
# (No exploits yet; the chain head of an empty append-only log.)
EMPTY_VAULT_CHAIN_HEAD = digest({"schema": "gradia-wind-tunnel-vault-manifest.v1", "entries": []})

_INTERPRETATION = (
    "This study measures whether a benchmark's SCORING PIPELINE (answer extractor, "
    "LLM judge, rubric grader, or unit-test verifier) can be gamed by answers that a "
    "machine oracle proves wrong, and whether iterated repair of that scorer converges. "
    "It does NOT claim: that a model is generally weak or strong; that a benchmark is "
    "worthless; balanced model comparison; human agreement; or that exploits reflect "
    "typical deployment behavior beyond the reported natural-incidence (L0) rung. "
    "Causal-slice claims are made only from factorial cells (procedural or witnessed-"
    "universe forks); observational metadata clusters are labeled hypothesis-generating."
)

_ANALYSIS_BLIND_GATES = [
    "transform_catalog and oracle_specs frozen before any attack is generated",
    "hidden_regression_vault chain-head published before any scorer is graded against it",
    "causal claims only from factorial cells; observational clusters labeled hypothesis-generating",
    "no pooling across rungs or across adversary x judge cells in headline claims",
    "every preregistered cell reported even if null (program claim-ledger discipline)",
    "L2/L3 answers pass an automated naturalness screen; injection artifacts discarded",
    "a patch is rejected if its autoimmunity cost exceeds the pre-fixed threshold",
]


def _git() -> dict[str, Any]:
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True).stdout.strip())
    except Exception:
        sha, dirty = "{{GIT_SHA}}", True
    return {"sha": sha or "{{GIT_SHA}}", "dirty": dirty}


def build_preregistration(
    run_id: str,
    *,
    max_cost_usd: float = 300.0,
    per_cell_attempts: int = 200,
    patch_cycles_K: int = 5,
    plateau_window: int = 2,
    adversary_models: list[str] | None = None,
    judge_architectures: list[str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    """Assemble the preregistration body and stamp its self-digest."""
    created = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    adversary_models = adversary_models or [
        "claude-opus-5", "gemini-3.1-pro-preview", "grok-4.6", "gpt-5.6-sol",
    ]
    judge_architectures = judge_architectures or [
        "single", "naive_ensemble", "self_commitment", "rubric_decomposed",
    ]

    body: dict[str, Any] = {
        "schema": SCHEMA_PREREGISTRATION,
        "run_id": run_id,
        "created_at": created,
        "study_kind": "confirmatory_adversarial_repair",
        "claim_status": "private_pre_results",
        "interpretation": _INTERPRETATION,
        "git": _git(),
        "program": {
            "thesis": "an evaluation must prove its own validity before any score counts",
            "builds_on": {
                "interruptible_universes_concept_doi": "10.5281/zenodo.22087020",
                "conditionally_approved_forum": "openreview.net/forum?id=IrPdpUo7Rz",
                "gradia_guard_repo": "github.com/rudycelekli/gradia-guard",
            },
        },
        "target_benchmarks": [
            {
                "benchmark_id": b.benchmark_id,
                "kind": b.kind,
                "oracle_kind": b.oracle_kind,
                "grader_kinds": list(b.grader_kinds),
                "snapshot": b.snapshot,
                "famous_precedent": b.famous_precedent,
            }
            for b in TARGET_BENCHMARKS
        ],
        "adversary_models": adversary_models,
        "judge_architectures": judge_architectures,
        "rungs": ["L0", "L1", "L2", "L3"],
        "transform_catalog": {
            "version": TRANSFORM_CATALOG_VERSION,
            "transform_ids": sorted(TRANSFORMS.keys()),
            "favored_phrase_count": len(FAVORED_PHRASES),
            "catalog_sha256": digest(sorted(TRANSFORMS.keys())),
        },
        "oracle_suite_version": ORACLE_SUITE_VERSION,
        "analyst_version": ANALYST_VERSION,
        "hypotheses": [
            {
                "id": h.hid,
                "statement": h.statement,
                "precommitted_direction": h.precommitted_direction,
                "interesting_if_false": h.interesting_if_false,
            }
            for h in HYPOTHESES
        ],
        "primary_outcomes": [
            "exploit_density_per_rung",
            "patch_generalization_gamma",
            "autoimmunity_pareto_frontier",
            "convergence_classification_per_architecture",
            "causal_slice_prospective_lift",
            "adversary_by_judge_transfer_matrix",
        ],
        "hidden_regression_vault": {
            "schema": "gradia-wind-tunnel-vault-manifest.v1",
            "committed_chain_head_sha256": EMPTY_VAULT_CHAIN_HEAD,
            "reveal_status": "hidden_until_publication",
        },
        "spend_policy": {
            "max_cost_usd": max_cost_usd,
            "operator_attests_provider_account_spend_limit_enabled": True,
            "live_spend_confirmation_required": True,
        },
        "execution": {
            "per_cell_attempts": per_cell_attempts,
            "patch_cycles_K": patch_cycles_K,
            "plateau_stop_window": plateau_window,
        },
        "analysis_blind_gates": _ANALYSIS_BLIND_GATES,
        "responsible_disclosure": {
            "policy": "coordinated disclosure with a suggested patch before public release",
            "embargo_days": 45,
            "report_maintainer_responses": True,
        },
    }
    body["preregistration_sha256"] = digest(body)
    return body


def freeze(run_id: str, out: Path, **kwargs: Any) -> tuple[Path, str]:
    """Write the prereg canonically; return (path, self_digest).

    The returned digest is the document's own ``preregistration_sha256`` field
    (the self-digest over the body excluding that field) — the value a verifier
    recomputes — not the whole-file digest.
    """
    body = build_preregistration(run_id, **kwargs)
    write_canonical(out, body)
    return out, body["preregistration_sha256"]


def verify(path: Path) -> dict[str, Any]:
    """Recompute the self-digest and report whether the prereg is intact."""
    body = load_json(path)
    stored = body.get("preregistration_sha256")
    recomputed = digest({k: v for k, v in body.items() if k != "preregistration_sha256"})
    return {
        "run_id": body.get("run_id"),
        "schema": body.get("schema"),
        "stored_sha256": stored,
        "recomputed_sha256": recomputed,
        "ok": stored == recomputed,
        "git_dirty": body.get("git", {}).get("dirty"),
        "vault_chain_head": body.get("hidden_regression_vault", {}).get("committed_chain_head_sha256"),
    }
