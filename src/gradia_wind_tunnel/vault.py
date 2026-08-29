"""The hidden regression vault (C5/IP-5).

Every confirmed exploit enters a permanent, append-only, hash-chained log. The
EMPTY head is committed at preregistration freeze (published with a timestamp)
before any result exists. Each append extends an authenticated chain, so the set
cannot be reordered or curated after the fact. At publication the entries are
revealed and anyone recomputes the chain from the committed empty head forward.
Every scorer version is retested against the full vault — model AND evaluator
after every change.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .canonical import digest
from .windtunnel import Episode

VAULT_SCHEMA = "gradia-wind-tunnel-vault-manifest.v1"
EMPTY_HEAD = digest({"schema": VAULT_SCHEMA, "entries": []})


@dataclass(frozen=True)
class VaultEntry:
    item_id: str
    transform_id: str
    favored_phrase: str | None
    answer_sha256: str
    discovered_cycle: int
    prev_head: str
    entry_head: str


def _entry_body(ep: Episode, cycle: int) -> dict:
    return {
        "item_id": ep.item_id,
        "transform_id": ep.transform_id,
        "favored_phrase": ep.favored_phrase,
        "answer_sha256": ep.answer_sha256,
        "discovered_cycle": cycle,
    }


class RegressionVault:
    def __init__(self) -> None:
        self._head = EMPTY_HEAD
        self.entries: list[VaultEntry] = []

    @property
    def head(self) -> str:
        return self._head

    def committed_empty_head(self) -> str:
        return EMPTY_HEAD

    def append_exploit(self, ep: Episode, cycle: int) -> VaultEntry:
        body = _entry_body(ep, cycle)
        entry_head = digest({"prev": self._head, "entry": body})
        entry = VaultEntry(
            item_id=ep.item_id, transform_id=ep.transform_id,
            favored_phrase=ep.favored_phrase, answer_sha256=ep.answer_sha256,
            discovered_cycle=cycle, prev_head=self._head, entry_head=entry_head,
        )
        self.entries.append(entry)
        self._head = entry_head
        return entry

    def reveal(self) -> dict:
        return {
            "schema": VAULT_SCHEMA,
            "committed_empty_head": EMPTY_HEAD,
            "final_head": self._head,
            "n_entries": len(self.entries),
            "entries": [
                {
                    "item_id": e.item_id, "transform_id": e.transform_id,
                    "favored_phrase": e.favored_phrase, "answer_sha256": e.answer_sha256,
                    "discovered_cycle": e.discovered_cycle,
                    "prev_head": e.prev_head, "entry_head": e.entry_head,
                }
                for e in self.entries
            ],
        }


def verify_reveal(revealed: dict) -> bool:
    """Recompute the chain from the committed empty head; True iff intact."""
    if revealed.get("committed_empty_head") != EMPTY_HEAD:
        return False
    head = EMPTY_HEAD
    for e in revealed.get("entries", []):
        if e.get("prev_head") != head:
            return False
        body = {
            "item_id": e["item_id"], "transform_id": e["transform_id"],
            "favored_phrase": e["favored_phrase"], "answer_sha256": e["answer_sha256"],
            "discovered_cycle": e["discovered_cycle"],
        }
        head = digest({"prev": head, "entry": body})
        if e.get("entry_head") != head:
            return False
    return head == revealed.get("final_head")
