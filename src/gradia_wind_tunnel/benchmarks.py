"""Benchmark adapters: the seam between a named public benchmark and the tunnel.

Every adapter exposes (a) items with declared causal factors, (b) a machine
ORACLE for ground truth, and (c) the gameable GRADER(s) we attack. The oracle is
the backstop that confirms wrongness; the grader is the attack surface. This is
the whole design in one interface: we do not attack difficulty, we attack the
scoring pipeline, and the oracle catches it with no human.

Phase 0 wires the procedural math adapter concretely (extends the pilot). The
frontier adapters (MATH, GPQA, HumanEval, SWE-bench Verified) are declared with
their oracle/grader kinds and left as explicit NotImplemented stubs so the
freeze can pin them and Phase 1 can fill each in behind the same interface.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .contracts import BenchmarkSpec, TARGET_BENCHMARKS
from .items import Item, generate_factorial, oracle as numeric_oracle


@runtime_checkable
class BenchmarkAdapter(Protocol):
    spec: BenchmarkSpec

    def items(self, seed: int, per_cell: int) -> list[Item]:
        """Return items with declared, controlled causal factors."""
        ...

    def oracle(self, answer_text: str, item: Item) -> bool:
        """Ground-truth machine check: True iff the answer is CORRECT."""
        ...


class ProceduralMathAdapter:
    """Concrete Phase-0 adapter: procedurally generated GSM8K-shaped math.

    Generated items give an exact numeric oracle AND exact factor control, so
    causal-slice cells are a true factorial (no confounding). Stands in for
    GSM8K/MATH-style exact-answer math until the real snapshots are pinned.
    """

    def __init__(self) -> None:
        self.spec = next(b for b in TARGET_BENCHMARKS if b.benchmark_id == "gsm8k")

    def items(self, seed: int, per_cell: int = 6) -> list[Item]:
        return generate_factorial(seed=seed, per_cell=per_cell)

    def oracle(self, answer_text: str, item: Item) -> bool:
        return numeric_oracle(answer_text, item)


class _StubAdapter:
    """Declared-but-unimplemented frontier adapter (pinned at freeze, filled in Phase 1)."""

    def __init__(self, benchmark_id: str) -> None:
        self.spec = next(b for b in TARGET_BENCHMARKS if b.benchmark_id == benchmark_id)

    def items(self, seed: int, per_cell: int = 6) -> list[Item]:
        raise NotImplementedError(
            f"{self.spec.benchmark_id} adapter is a Phase-1 stub. Wire the pinned "
            f"snapshot {self.spec.snapshot!r}, its {self.spec.oracle_kind} oracle, and "
            f"the grader(s) {self.spec.grader_kinds} behind this same interface."
        )

    def oracle(self, answer_text: str, item: Item) -> bool:
        raise NotImplementedError(f"{self.spec.benchmark_id} oracle is a Phase-1 stub.")


def build_adapter(benchmark_id: str, real: bool = False) -> BenchmarkAdapter:
    """Return an adapter. `real=True` loads the actual dataset (needs network +
    `datasets`); the default is the offline procedural adapter used by the demo
    and the self-verifying study. GSM8K has a fully-wired real loader; the other
    frontier benchmarks have real oracles (real_benchmarks.py) and Phase-1 items.
    """
    if real:
        from .real_benchmarks import build_real_adapter
        return build_real_adapter(benchmark_id)
    if benchmark_id == "gsm8k":
        return ProceduralMathAdapter()
    return _StubAdapter(benchmark_id)


def target_benchmark_ids() -> list[str]:
    return [b.benchmark_id for b in TARGET_BENCHMARKS]
