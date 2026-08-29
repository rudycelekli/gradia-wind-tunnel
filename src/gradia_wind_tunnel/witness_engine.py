"""A self-contained, faithful realization of the Interruptible-Universes WITNESS
primitives, shipped in the OPEN Wind Tunnel repo so the causal instrument is
reproducible by anyone — no private engine required.

When the production `gradia_universes` engine is installed, `universe_forks`
uses THAT. When it is not, this module supplies the same witness so the causal
localizer NEVER degrades:

  * root(world)      = sha256 over the canonical serialization of (case, policy)
                       — content-addressed world state (before/after roots).
  * single-variable  = exactly one declared case field differs before -> after
                       (the intervention proof a static benchmark cannot give).
  * occurrence chain = head_i = sha256(head_{i-1} || digest(record_i)) — a
                       tamper-evident log; recompute the head to verify.

Everything here is dependency-free and offline-recomputable.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

GENESIS = "0" * 64


def canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, default=str).encode("utf-8")


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical_bytes(obj)).hexdigest()


def _chain(prev_head: str, record: dict) -> str:
    return hashlib.sha256((prev_head + digest(record)).encode()).hexdigest()


_RECORD_KEYS = ("event_id", "before_root", "after_root", "updates",
                "changed_fields", "projection_sha256")


@dataclass
class WitnessWorld:
    """Root-owned world state with a hash-chained occurrence log. Minimal but
    faithful: content-addressed roots, single-variable interventions, and a
    tamper-evident chain — the exact machinery the causal witness needs."""
    case: dict
    policy: dict = field(default_factory=dict)
    head: str = GENESIS
    occurrences: list = field(default_factory=list)

    @property
    def root(self) -> str:
        return digest({"case": self.case, "policy": self.policy})

    def apply(self, event_id: str, updates: dict, *, observation: dict | None = None):
        """Apply a case update, returning (before_root, after_root, changed, projection)
        and appending a tamper-evident occurrence to the chain."""
        before_root = self.root
        before_case = dict(self.case)
        self.case.update(updates)
        after_root = self.root
        changed = tuple(sorted(
            k for k in set(before_case) | set(self.case)
            if before_case.get(k) != self.case.get(k)))
        projection = {"visible_case": dict(self.case), "observation": observation or {}}
        record = {"event_id": event_id, "before_root": before_root,
                  "after_root": after_root, "updates": dict(updates),
                  "changed_fields": list(changed),
                  "projection_sha256": digest(projection)}
        self.head = _chain(self.head, record)
        self.occurrences.append({**record, "head": self.head})
        return before_root, after_root, changed, projection


def verify_chain(occurrences: list, genesis: str = GENESIS) -> bool:
    """Recompute the occurrence chain head and confirm each stored head matches."""
    head = genesis
    for rec in occurrences:
        body = {k: rec.get(k) for k in _RECORD_KEYS}
        head = _chain(head, body)
        if head != rec.get("head"):
            return False
    return True
