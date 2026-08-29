"""Witnessed-universe forks — the causal instrument (C1), on the real substrate.

This is the wiring that runs a single-variable intervention on the Gradia
universe engine and captures an evolution witness. When `gradia_universes` is
installed it builds a real `World`, snapshots it (the shared parent closure),
applies an `Event` that changes exactly one declared variable, and records the
before/after world roots and the agent-visible projection — the tamper-evident
occurrence that proves the counterfactual changed one thing and nothing else.
Without the substrate it falls back to a procedural descriptor so the study
still runs.

Important: this is a WIRING layer over primitives Gradia already ships (root-
owned world state with before/after roots, snapshot/restore, the hash-chained
occurrence chain — the machinery of Interruptible Universes). It is not a new
platform capability; it calls the existing engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Fork:
    variable: str
    value: Any
    intervention: str                    # "single_variable"
    parent_closure_root: str
    witness_available: bool
    before_root: str | None = None
    after_root: str | None = None
    changed_fields: tuple[str, ...] = ()
    single_variable_verified: bool = False
    projection_sha256: str | None = None
    engine: str = "unknown"


def substrate_available() -> bool:
    try:
        import gradia_universes.world  # noqa: F401
        import gradia_universes.contracts  # noqa: F401
        return True
    except Exception:
        return False


def fork_on_variable(
    variable: str,
    value: Any,
    *,
    case: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
    parent_closure_id: str = "wind-tunnel-parent",
) -> Fork:
    """Fork a parent world on one declared variable and capture the witness.

    `case`/`policy` are the parent world state (the causal factors live in `case`).
    Returns a Fork; on the real substrate it carries before/after world roots and
    a single-variable-changed proof.
    """
    parent_case = dict(case or {variable: None})
    parent_policy = dict(policy or {})

    if not substrate_available():
        # No production engine here -> use the repo's built-in witness engine.
        # Same guarantees (before/after roots, single-variable proof, chained log),
        # fully recomputable. This is why the causal instrument never degrades.
        from .witness_engine import WitnessWorld, digest as _wdigest
        w = WitnessWorld(case=dict(parent_case), policy=dict(parent_policy))
        before_root = w.root
        b_root, a_root, changed, projection = w.apply(
            f"intervene-{variable}", {variable: value},
            observation={"source": "wind-tunnel", "authority": "authoritative",
                         "message": f"single-variable intervention: {variable}={value!r}"})
        return Fork(
            variable=variable, value=value, intervention="single_variable",
            parent_closure_root=before_root, witness_available=True,
            before_root=b_root, after_root=a_root, changed_fields=changed,
            single_variable_verified=(changed == (variable,)),
            projection_sha256=_wdigest(projection), engine="builtin-witness")

    from gradia_universes.canonical import digest
    from gradia_universes.contracts import Event, Observation, Scenario
    from gradia_universes.world import World

    scenario = Scenario(
        scenario_id=f"wt-fork-{parent_closure_id}",
        title="wind-tunnel causal fork",
        case=parent_case,
        policy=parent_policy,
        events=(),
        restore_after_event=False,
        synthetic=True,
    )
    world = World(scenario)
    parent_root = world.root
    parent_case_before = dict(world.case)

    event = Event(
        event_id=f"intervene-{variable}",
        after_act=1,
        target="case",
        updates={variable: value},
        observation=Observation(
            source="wind-tunnel",
            authority="authoritative",
            message=f"single-variable intervention: {variable}={value!r}",
        ),
    )
    before_root, after_root, projection = world.apply(event)
    changed = tuple(sorted(
        k for k in set(parent_case_before) | set(world.case)
        if parent_case_before.get(k) != world.case.get(k)
    ))
    return Fork(
        variable=variable, value=value, intervention="single_variable",
        parent_closure_root=parent_root, witness_available=True,
        before_root=before_root, after_root=after_root,
        changed_fields=changed,
        single_variable_verified=(changed == (variable,)),
        projection_sha256=digest(projection), engine="gradia_universes",
    )


def witness_engine_name() -> str:
    """Which engine backs the witness: the production universe engine when
    installed, else the repo's built-in witness engine. Both are real."""
    return "gradia_universes" if substrate_available() else "builtin-witness"


def causal_validity_note() -> str:
    if substrate_available():
        return ("universe forks available: single-variable interventions carry an "
                "evolution witness (before/after world roots, occurrence chain) — "
                "causal-strength slices on the real Gradia engine")
    return ("production universe engine absent: using the repo's built-in witness "
            "engine — content-addressed before/after world roots, a single-variable "
            "occurrence proof, and a hash-chained log; fully recomputable, same "
            "witness guarantees, so the causal instrument does not degrade")
