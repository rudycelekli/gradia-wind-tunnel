"""Model providers — the one runtime swap between offline and real.

`Provider` is the seam. `SimulatedProvider` is a deterministic, offline
stand-in that reproduces the documented reference-free failure mode, so the
ENTIRE study runs end-to-end with no API key and byte-reproducible results.
`GuardRoutedProvider` is the Phase-0 real path: it routes every call through
Gradia Guard's credentialless gateway (provider key never enters this process)
and reads the key from the environment. Swapping one for the other does not
change the adversary, analyst, patcher, vault, or verifier.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ModelReply:
    text: str
    model_id: str
    cost_usd: float


class Provider(Protocol):
    identity: str

    def complete(self, prompt: str, *, purpose: str) -> ModelReply:
        ...


class SimulatedProvider:
    """Deterministic offline provider. No network, no key, reproducible.

    Its 'grader' behavior lives in the judges; this provider only supplies
    deterministic model *text* for the adversary's on-policy generations and
    for judge self-commitment solving, so the pipeline exercises the same code
    path a real provider would.
    """

    identity = "simulated-provider.v1"

    def __init__(self, model_id: str = "simulated-model") -> None:
        self.model_id = model_id

    def complete(self, prompt: str, *, purpose: str) -> ModelReply:
        # deterministic pseudo-text keyed by prompt+purpose (never random)
        h = hashlib.sha256(f"{purpose}\x00{prompt}".encode()).hexdigest()
        return ModelReply(text=f"[sim:{purpose}:{h[:8]}]", model_id=self.model_id, cost_usd=0.0)


class GuardRoutedProvider:
    """Phase-0 real path (stub). Route through Gradia Guard's gateway.

    Left explicit so no accidental network/key use in the offline study. Fill
    `complete` with your provider SDK pointed at the Guard gateway base URL; the
    real provider key stays in the Guard parent process, this side holds only a
    capability. Every call becomes a hash-chained Guard receipt.
    """

    def __init__(self, model_id: str, gateway_base_url: str, provider: str = "anthropic") -> None:
        self.identity = f"guard-routed:{provider}:{model_id}"
        self.model_id = model_id
        self.gateway_base_url = gateway_base_url
        self.provider = provider
        # capability (a decoy that doubles as the SDK 'api key'); real key is in Guard
        self.capability = os.environ.get("GRADIA_GUARD_LOCAL_CAPABILITY")

    def complete(self, prompt: str, *, purpose: str) -> ModelReply:  # pragma: no cover
        raise NotImplementedError(
            "GuardRoutedProvider is the Phase-0 real path. Point your provider SDK at "
            f"{self.gateway_base_url} with the local capability as the auth value; the real "
            "credential lives in the Guard parent process. Return ModelReply so the loop is "
            "unchanged from the offline run."
        )
