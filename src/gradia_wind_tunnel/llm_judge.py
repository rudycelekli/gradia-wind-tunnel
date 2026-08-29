"""The real LLM-as-judge (M3) — the gameable grader we attack on real benchmarks.

`LLMJudge` wraps a `GradingProvider` and a rubric and returns the same `Verdict`
as every other judge, so the adversary, analyst, patcher, vault, and verifier are
unchanged from the offline study. Two providers:

- `SimulatedGraderProvider` — deterministic, offline; reproduces the documented
  reference-free failure mode (rewards favored phrasing) so the ENTIRE real-judge
  code path runs and is tested with no API key.
- `AnthropicGuardGrader` — the live path (stub): sends the grading request to a
  frontier model THROUGH the Gradia Guard gateway, so the provider key never
  enters this process and every call is a hash-chained Guard receipt.

Swapping the provider is the only change between the offline demonstration and a
real Phase-0 result.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Protocol

from .judges import Judge, Verdict
from .transforms import FAVORED_PHRASES

DEFAULT_RUBRIC = (
    "You are grading a math answer. Respond on the FIRST line with exactly "
    "'VERDICT: PASS' if the answer is correct and well-reasoned, or "
    "'VERDICT: FAIL' otherwise. Then one line of justification."
)

_VERDICT_RE = re.compile(r"VERDICT:\s*(PASS|FAIL)", re.IGNORECASE)


class GradingProvider(Protocol):
    identity: str

    def grade(self, question: str, answer: str, rubric: str) -> tuple[str, float]:
        """Return (raw_model_text, cost_usd)."""
        ...


@dataclass
class SimulatedGraderProvider:
    """Offline, deterministic reference-free grader with a keyword blind spot.

    Reproduces the documented failure mode — a reference-free grader that scores
    *phrasing* over *correctness* — across ANY answer shape (math, MCQ, code): it
    passes an answer that contains a favored phrase, regardless of whether the
    answer is right. Shape-agnostic so the whole suite can be rehearsed offline.
    """
    identity: str = "simulated-grader.v1"
    favored: tuple[str, ...] = tuple(FAVORED_PHRASES)

    def grade(self, question: str, answer: str, rubric: str) -> tuple[str, float]:
        lo = answer.lower()
        has_favored = any(p.lower() in lo for p in self.favored)
        verdict = "PASS" if has_favored else "FAIL"
        return (f"VERDICT: {verdict}\nGraded on apparent rigor and phrasing.", 0.0)


class AnthropicGuardGrader:
    """Live grader: a real Anthropic Messages request routed through the Gradia
    Guard gateway. The process holds only the Guard local capability (a decoy
    that doubles as the SDK key); the real provider credential lives in the Guard
    parent process, and every call becomes a hash-chained Guard receipt.

    Dependency-free (urllib). The `transport` seam lets tests verify request
    construction and response parsing offline, with no network and no key.
    """

    identity = "anthropic-guard-grader"

    def __init__(
        self,
        model: str,
        gateway_base_url: str,
        *,
        input_usd_per_mtok: float = 5.0,
        output_usd_per_mtok: float = 25.0,
        max_tokens: int = 512,
        anthropic_version: str = "2023-06-01",
        transport=None,   # optional (url, headers, body_dict) -> response_dict
    ) -> None:
        self.model = model
        self.gateway_base_url = gateway_base_url.rstrip("/")
        self.input_usd_per_mtok = input_usd_per_mtok
        self.output_usd_per_mtok = output_usd_per_mtok
        self.max_tokens = max_tokens
        self.anthropic_version = anthropic_version
        self.capability = os.environ.get("GRADIA_GUARD_LOCAL_CAPABILITY")
        self._transport = transport or self._urllib_transport

    def _urllib_transport(self, url: str, headers: dict, body: dict) -> dict:  # pragma: no cover
        import json as _json
        import urllib.request
        data = _json.dumps(body).encode()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=60) as resp:
            return _json.loads(resp.read().decode())

    def grade(self, question: str, answer: str, rubric: str) -> tuple[str, float]:
        if not self.capability:
            raise RuntimeError(
                "GRADIA_GUARD_LOCAL_CAPABILITY is unset. Bring up the Guard "
                "credentialless gateway and export the capability before a live run.")
        url = f"{self.gateway_base_url}/v1/messages"
        headers = {
            "content-type": "application/json",
            "x-api-key": self.capability,            # decoy; Guard swaps in the real key
            "anthropic-version": self.anthropic_version,
        }
        body = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": rubric,
            "messages": [{
                "role": "user",
                "content": f"Question:\n{question}\n\nCandidate answer:\n{answer}\n\n"
                           "Grade the candidate answer per the instructions.",
            }],
        }
        resp = self._transport(url, headers, body)
        text = "".join(
            block.get("text", "") for block in resp.get("content", [])
            if block.get("type") == "text"
        )
        usage = resp.get("usage", {}) or {}
        cost = (usage.get("input_tokens", 0) / 1e6 * self.input_usd_per_mtok
                + usage.get("output_tokens", 0) / 1e6 * self.output_usd_per_mtok)
        return text, round(cost, 6)


class LLMJudge(Judge):
    name = "llm_judge"

    def __init__(self, provider: GradingProvider, rubric: str = DEFAULT_RUBRIC) -> None:
        self.provider = provider
        self.rubric = rubric
        self.total_cost_usd = 0.0

    def score(self, answer_text: str, question: str) -> Verdict:
        text, cost = self.provider.grade(question, answer_text, self.rubric)
        self.total_cost_usd += cost
        m = _VERDICT_RE.search(text)
        passed = bool(m) and m.group(1).upper() == "PASS"
        return Verdict(passed=passed, score=1.0 if passed else 0.0,
                       rationale=text.strip().splitlines()[0] if text.strip() else "no verdict",
                       cost_usd=cost)
