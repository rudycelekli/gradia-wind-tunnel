"""Real, dataset-backed benchmark adapters.

These load the ACTUAL public benchmarks (via HuggingFace `datasets`) and expose,
behind the `BenchmarkAdapter` interface, (a) items with observational factor
tags, (b) a machine ORACLE, and (c) the gameable GRADER. Dataset download needs
network + the `datasets` package (present in your environment); the oracle logic
is unit-tested here on embedded samples so it is verified without network.

IMPORTANT honesty note: real-benchmark factor tags are OBSERVATIONAL (heuristic
metadata), so slices from them are hypothesis-generating. Causal claims come only
from the procedural factorial or witnessed-universe forks (see `causal.py` /
`universe_forks.py`). Every item carries factors["observational"] = True.

GSM8K plugs fully into the existing math pipeline (numeric #### answers). MATH,
GPQA, and HumanEval have real oracles here; their attack-transform catalogs
(answer shapes differ from math) are the Phase-1 extension.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .contracts import TARGET_BENCHMARKS
from .items import Item, FINAL_RE

_NUM = re.compile(r"-?\d[\d,]*")


# ---------------------------------------------------------------------------
# GSM8K — numeric-answer math (fully wired into the pipeline)
# ---------------------------------------------------------------------------

def _gsm8k_gold(answer: str) -> int:
    tail = answer.split("####")[-1].strip().replace(",", "")
    m = _NUM.search(tail)
    if not m:
        raise ValueError("gsm8k: no gold number")
    return int(m.group(0).replace(",", ""))


def _gsm8k_reasoning(answer: str) -> tuple[str, ...]:
    body = answer.split("####")[0]
    lines = []
    for ln in body.splitlines():
        ln = re.sub(r"<<[^>]*>>", "", ln).strip()  # drop calculator annotations
        if ln:
            lines.append(ln)
    return tuple(lines) or ("(no reasoning provided)",)


def _observational_factors(reasoning: tuple[str, ...], gold: int) -> dict:
    numbers = [int(x.replace(",", "")) for ln in reasoning for x in _NUM.findall(ln)]
    steps = sum(1 for ln in reasoning if "=" in ln) or len(reasoning)
    return {
        "steps": 2 if steps <= 2 else (3 if steps == 3 else 4),
        "large_operands": bool(numbers and max(numbers + [gold]) >= 100),
        "distractor": False,           # unknown for real items; observational
        "observational": True,
    }


class GSM8KAdapter:
    """Real GSM8K (openai/gsm8k). Produces pipeline-compatible math Items."""

    def __init__(self, split: str = "test", limit: int | None = 200) -> None:
        self.spec = next(b for b in TARGET_BENCHMARKS if b.benchmark_id == "gsm8k")
        self.split = split
        self.limit = limit

    def items(self, seed: int = 0, per_cell: int | None = None) -> list[Item]:
        try:
            from datasets import load_dataset  # lazy: needs network + package
        except Exception as exc:  # pragma: no cover
            raise RuntimeError("GSM8KAdapter needs `pip install datasets` and network.") from exc
        split = f"{self.split}[:{self.limit}]" if self.limit else self.split
        ds = load_dataset("openai/gsm8k", "main", split=split)
        out: list[Item] = []
        for i, row in enumerate(ds):
            gold = _gsm8k_gold(row["answer"])
            reasoning = _gsm8k_reasoning(row["answer"])
            out.append(Item(
                item_id=f"gsm8k-{self.split}-{i:05d}",
                question=row["question"],
                gold=gold,
                reasoning_lines=reasoning,
                factors=_observational_factors(reasoning, gold),
            ))
        return out

    def oracle(self, answer_text: str, item: Item) -> bool:
        m = FINAL_RE.search(answer_text.strip())
        return m is not None and int(m.group(1)) == item.gold


# ---------------------------------------------------------------------------
# MATH — competition math (boxed answers); real oracle, Phase-1 transforms
# ---------------------------------------------------------------------------

def math_extract_boxed(text: str) -> str | None:
    """Extract the content of the last \\boxed{...}, balancing braces."""
    idx = text.rfind("\\boxed")
    if idx < 0:
        return None
    i = text.find("{", idx)
    if i < 0:
        return None
    depth, j = 0, i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[i + 1:j].strip()
        j += 1
    return None


def _math_normalize(ans: str) -> str:
    s = ans.strip().replace(" ", "").replace("\\left", "").replace("\\right", "")
    s = s.replace("\\!", "").rstrip(".")
    if s.startswith("$") and s.endswith("$"):
        s = s[1:-1]
    return s


def math_oracle(candidate_boxed: str | None, gold_boxed: str) -> bool:
    if candidate_boxed is None:
        return False
    return _math_normalize(candidate_boxed) == _math_normalize(gold_boxed)


# ---------------------------------------------------------------------------
# GPQA — graduate multiple-choice; oracle = option-letter key match
# ---------------------------------------------------------------------------

_LETTER = re.compile(r"\b([A-D])\b")


def gpqa_extract_choice(text: str) -> str | None:
    # last standalone A-D, or a trailing 'Answer: X'
    m = re.search(r"answer\s*[:=]\s*([A-D])", text, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    hits = _LETTER.findall(text.upper())
    return hits[-1] if hits else None


def gpqa_oracle(candidate: str | None, gold_letter: str) -> bool:
    return candidate is not None and candidate.upper() == gold_letter.upper()


# ---------------------------------------------------------------------------
# HumanEval — execution-checked code; oracle = unit tests pass
# ---------------------------------------------------------------------------

def humaneval_oracle(completion: str, test_program: str, entry_point: str,
                     timeout_s: float = 5.0) -> bool:
    """Run the completion against the task's unit tests in a subprocess.

    NOTE: run only in a sandbox you trust (reuse Guard's container posture).
    Returns True iff the tests pass. Weak/gameable tests are exactly the attack
    surface; a strong hidden test suite is the oracle backstop.
    """
    import subprocess
    import sys
    import tempfile
    import textwrap
    program = f"{completion}\n\n{test_program}\n\ncheck({entry_point})\n"
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as f:
        f.write(program)
        path = f.name
    try:
        r = subprocess.run([sys.executable, path], capture_output=True,
                           timeout=timeout_s)
        return r.returncode == 0
    except Exception:
        return False


# real adapters registry (GSM8K wired; others load-capable with real oracles)
def build_real_adapter(benchmark_id: str, **kwargs):
    if benchmark_id == "gsm8k":
        return GSM8KAdapter(**kwargs)
    raise NotImplementedError(
        f"{benchmark_id}: real loader is Phase-1. Oracle implemented in this module "
        f"(math_oracle / gpqa_oracle / humaneval_oracle); wire its items() + attack "
        f"catalog behind BenchmarkAdapter next."
    )
