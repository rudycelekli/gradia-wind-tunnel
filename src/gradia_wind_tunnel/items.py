"""
Procedurally generated GSM8K-style items with an EXACT machine oracle and
declared causal factors.

Because we generate the items, we control every factor exactly -- so a slice
like "exploit fires at steps>=3" is a TRUE factorial cell, not a correlation.
The oracle is deterministic numeric equality on the final answer, so truth is
free and needs no human.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Optional

FINAL_RE = re.compile(r"####\s*(-?\d+)\s*$")


@dataclass(frozen=True)
class Item:
    item_id: str
    question: str
    gold: int
    # correct chain-of-thought reasoning lines (one per step), no final marker
    reasoning_lines: tuple[str, ...]
    factors: dict = field(default_factory=dict)

    def correct_answer(self) -> str:
        """A verified-correct answer: the reasoning, then the gold final."""
        body = "\n".join(self.reasoning_lines)
        return f"{body}\n#### {self.gold}"


def oracle(answer_text: str, item: Item) -> bool:
    """
    THE ORACLE. Returns True iff the answer is correct.
    Deterministic: parse the final number after '####' and compare to gold.
    An answer with no parseable final is treated as wrong (ungradable == wrong).
    """
    m = FINAL_RE.search(answer_text.strip())
    if m is None:
        return False
    return int(m.group(1)) == item.gold


def extract_final(answer_text: str) -> Optional[int]:
    m = FINAL_RE.search(answer_text.strip())
    return int(m.group(1)) if m else None


# --- generator -------------------------------------------------------------

_NAMES = ["Ana", "Ben", "Cara", "Dev", "Eli", "Fay", "Gus", "Hana"]
_OBJECTS = ["apples", "coins", "books", "marbles", "tickets", "cards"]


def generate_item(
    rng: random.Random,
    steps: int,
    large_operands: bool,
    distractor: bool,
    idx: int,
) -> Item:
    """
    Build a k-step addition/subtraction word problem with a known integer gold.
    Factors are recorded exactly.
      steps          : number of reasoning steps (>=2)
      large_operands : operand magnitude (blind spot candidate)
      distractor     : an irrelevant quantity is mentioned (blind spot candidate)
    """
    name = rng.choice(_NAMES)
    obj = rng.choice(_OBJECTS)
    hi = 90 if large_operands else 9
    lo = 10 if large_operands else 1

    start = rng.randint(lo, hi)
    running = start
    lines = [f"{name} starts with {start} {obj}."]
    reasoning = [f"Start: {start}."]

    for _ in range(steps - 1):
        delta = rng.randint(lo, hi)
        if rng.random() < 0.5:
            lines.append(f"Then {name} gets {delta} more {obj}.")
            reasoning.append(f"{running} + {delta} = {running + delta}.")
            running += delta
        else:
            delta = min(delta, running)  # keep non-negative
            lines.append(f"Then {name} gives away {delta} {obj}.")
            reasoning.append(f"{running} - {delta} = {running - delta}.")
            running -= delta

    if distractor:
        d = rng.randint(lo, hi)
        # irrelevant fact that does not affect the count
        lines.append(f"The store nearby has {d} {obj} in stock, which {name} does not buy.")

    question = " ".join(lines) + f" How many {obj} does {name} have?"
    return Item(
        item_id=f"it{idx:04d}",
        question=question,
        gold=running,
        reasoning_lines=tuple(reasoning),
        factors={
            "steps": steps,
            "large_operands": large_operands,
            "distractor": distractor,
        },
    )


def generate_factorial(
    seed: int,
    steps_levels=(2, 3, 4),
    per_cell: int = 6,
) -> list[Item]:
    """
    Full factorial over (steps) x (large_operands) x (distractor), `per_cell`
    items each. Deterministic given `seed` so the whole grid is reproducible.
    """
    rng = random.Random(seed)
    items: list[Item] = []
    idx = 0
    for steps in steps_levels:
        for large in (False, True):
            for distractor in (False, True):
                for _ in range(per_cell):
                    items.append(generate_item(rng, steps, large, distractor, idx))
                    idx += 1
    return items
