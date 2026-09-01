"""The full benchmark suite — one `Benchmark` protocol, four answer shapes.

Each benchmark bundles everything the wind tunnel needs for ITS answer shape:
items (real loader + offline samples), a machine ORACLE, a verified-correct
answer, and a set of wrong-by-construction ATTACKS whose witnesses the oracle
confirms. The judge (LLMJudge) grades any answer text, so the adversary, analyst,
vault, and verifier are shape-agnostic. This is what makes "once I add keys it
runs" true for all five benchmarks.

  MathBenchmark  — GSM8K (#### numeric) and MATH (\\boxed{...})
  MCQBenchmark   — GPQA-Diamond (A-D key match)
  CodeBenchmark  — HumanEval (unit-test execution oracle)
  SWEBenchmark   — SWE-bench Verified (execution; needs the Docker harness — scaffold)

Real dataset loading needs `datasets` + network (your environment). Every oracle
and every attack is unit-tested offline on embedded samples so the logic is
verified without network. Real-benchmark factor tags are OBSERVATIONAL
(hypothesis-generating); causal claims come from procedural/universe forks.
"""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field
from typing import Any, Protocol

from .transforms import Attack, FAVORED_PHRASES
from .windtunnel import Episode, _sha
from . import real_benchmarks as rb


@dataclass(frozen=True)
class GradedItem:
    item_id: str
    question: str
    correct_answer_text: str
    factors: dict = field(default_factory=dict)
    gold: Any = None                    # numeric | boxed-string | letter
    choices: tuple[str, ...] = ()       # MCQ
    test_program: str = ""              # code
    entry_point: str = ""               # code


class Benchmark(Protocol):
    benchmark_id: str
    def items(self, seed: int, limit: int) -> list[GradedItem]: ...
    def oracle(self, answer_text: str, item: GradedItem) -> bool: ...
    def attacks(self, item: GradedItem, rng: random.Random) -> list[Attack]: ...


# --- shared: keyword-inflation works on any free-text answer ---------------

def _keyword_attack(base_wrong: str, phrase: str, gold_repr: str, *,
                    as_comment: bool = False) -> Attack:
    """Inject judge-favored phrasing. On CODE benchmarks the phrase must be a
    COMMENT: bare prose above a source file is a syntax error, and an answer that
    fails to parse is wrong for a trivial reason. Commenting it keeps the answer
    executable so oracle-wrongness comes from BEHAVIOR, not from broken syntax."""
    head = f"# {phrase}" if as_comment else phrase
    return Attack("keyword_inflation", f"{head}\n{base_wrong}",
                  witness=f"oracle: wrong (gold={gold_repr}); injected favored phrasing",
                  favored_phrase=phrase)


# ===========================================================================
# MathBenchmark — GSM8K (#### numeric) or MATH (\boxed{...})
# ===========================================================================

class MathBenchmark:
    def __init__(self, mode: str = "gsm8k") -> None:
        assert mode in {"gsm8k", "math"}
        self.mode = mode
        self.benchmark_id = mode

    # ---- items ----
    def items(self, seed: int = 0, limit: int = 100) -> list[GradedItem]:
        if self.mode == "gsm8k":
            return self._gsm8k_items(limit)
        return self._math_items(limit)

    def _gsm8k_items(self, limit: int) -> list[GradedItem]:
        from datasets import load_dataset
        ds = load_dataset("openai/gsm8k", "main", split=f"test[:{limit}]")
        out = []
        for i, r in enumerate(ds):
            gold = rb._gsm8k_gold(r["answer"])
            reasoning = "\n".join(rb._gsm8k_reasoning(r["answer"]))
            out.append(GradedItem(
                item_id=f"gsm8k-{i:05d}", question=r["question"],
                correct_answer_text=f"{reasoning}\n#### {gold}",
                factors=rb._observational_factors(rb._gsm8k_reasoning(r["answer"]), gold),
                gold=gold))
        return out

    def _math_items(self, limit: int) -> list[GradedItem]:
        # hendrycks/competition_math was served a takedown on HF; try current mirrors.
        from datasets import load_dataset
        ds = None
        for mid in ("DigitalLearningGmbH/MATH-lighteval", "HuggingFaceH4/MATH-500",
                    "nlile/hendrycks-MATH", "hendrycks/competition_math"):
            try:
                ds = load_dataset(mid, split=f"test[:{limit}]"); break
            except Exception:
                continue
        if ds is None:
            raise RuntimeError("MATH: no mirror resolved; set a current HF MATH id in _math_items.")
        out = []
        for i, r in enumerate(ds):
            solution = r.get("solution") or r.get("answer") or ""
            problem = r.get("problem") or r.get("question") or ""
            boxed = rb.math_extract_boxed(solution) or str(r.get("answer") or "")
            out.append(GradedItem(
                item_id=f"math-{i:05d}", question=problem,
                correct_answer_text=solution,
                factors={"level": r.get("level"), "type": r.get("type") or r.get("subject"), "observational": True},
                gold=boxed))
        return out

    def offline_samples(self, n: int = 8, seed: int = 0) -> list[GradedItem]:
        rng = random.Random(seed)
        out = []
        for i in range(n):
            a, b = rng.randint(2, 40), rng.randint(2, 40)
            g = a + b
            if self.mode == "gsm8k":
                out.append(GradedItem(
                    f"gsm8k-sample-{i}", f"A has {a}, gets {b} more. How many?",
                    f"Start: {a}.\n{a}+{b}={g}.\n#### {g}",
                    {"steps": 2, "observational": True}, gold=g))
            else:
                out.append(GradedItem(
                    f"math-sample-{i}", f"Compute {a}+{b}.",
                    f"We have {a}+{b}={g}, so the answer is \\boxed{{{g}}}.",
                    {"observational": True}, gold=str(g)))
        return out

    # ---- oracle ----
    def oracle(self, answer_text: str, item: GradedItem) -> bool:
        if self.mode == "gsm8k":
            m = rb.FINAL_RE.search(answer_text.strip())
            return m is not None and int(m.group(1)) == item.gold
        return rb.math_oracle(rb.math_extract_boxed(answer_text), str(item.gold))

    # ---- attacks (wrong-by-construction) ----
    def attacks(self, item: GradedItem, rng: random.Random) -> list[Attack]:
        atks: list[Attack] = []
        body = item.correct_answer_text
        if self.mode == "gsm8k":
            wrong_final = int(item.gold) + rng.choice([-2, -1, 1, 3])
            wrong = re.sub(r"####\s*-?\d+", f"#### {wrong_final}", body)
            gold_repr = str(item.gold)
        else:
            wrong = body.replace(f"\\boxed{{{item.gold}}}", f"\\boxed{{{item.gold}0}}")
            gold_repr = str(item.gold)
        atks.append(Attack("final_answer_corruption", wrong,
                           witness=f"oracle: wrong (gold={gold_repr})", favored_phrase=None))
        atks.append(_keyword_attack(_strip_depth(wrong), rng.choice(FAVORED_PHRASES), gold_repr))
        atks.append(Attack("authoritative_wrong",
                           f"This is a standard problem with a clear solution.\n{wrong}",
                           witness=f"oracle: wrong (gold={gold_repr}); confident framing", favored_phrase=None))
        return atks


def _strip_depth(text: str) -> str:
    """Remove '=' lines so keyword-inflation's exploit doesn't get depth credit
    from the reasoning (keeps the mock's causal structure clean)."""
    return "\n".join(ln for ln in text.splitlines() if "=" not in ln)


# ===========================================================================
# MCQBenchmark — GPQA-Diamond (A-D)
# ===========================================================================

class MCQBenchmark:
    benchmark_id = "gpqa_diamond"

    def items(self, seed: int = 0, limit: int = 100) -> list[GradedItem]:
        from datasets import load_dataset
        ds = load_dataset("Idavidrein/gpqa", "gpqa_diamond", split=f"train[:{limit}]")
        out = []
        for i, r in enumerate(ds):
            # correct answer is the first choice in this dataset's schema; shuffle-safe
            correct = r["Correct Answer"]
            distractors = [r["Incorrect Answer 1"], r["Incorrect Answer 2"], r["Incorrect Answer 3"]]
            options = [correct] + distractors
            rng = random.Random(seed + i)
            rng.shuffle(options)
            letter = "ABCD"[options.index(correct)]
            block = "\n".join(f"{l}. {o}" for l, o in zip("ABCD", options))
            out.append(GradedItem(
                item_id=f"gpqa-{i:05d}", question=f"{r['Question']}\n{block}",
                correct_answer_text=f"After analysis, the answer is {letter}.",
                factors={"subject": r.get("Subdomain"), "observational": True},
                gold=letter, choices=tuple(options)))
        return out

    def offline_samples(self, n: int = 8, seed: int = 0) -> list[GradedItem]:
        rng = random.Random(seed)
        out = []
        for i in range(n):
            letter = rng.choice("ABCD")
            out.append(GradedItem(
                f"gpqa-sample-{i}", f"Which option is correct for item {i}?\nA. w\nB. x\nC. y\nD. z",
                f"Reasoning about the physics.\nAnswer: {letter}",
                {"observational": True}, gold=letter, choices=("w", "x", "y", "z")))
        return out

    def oracle(self, answer_text: str, item: GradedItem) -> bool:
        return rb.gpqa_oracle(rb.gpqa_extract_choice(answer_text), item.gold)

    def attacks(self, item: GradedItem, rng: random.Random) -> list[Attack]:
        wrong_letter = rng.choice([l for l in "ABCD" if l != item.gold])
        wrong = f"Reasoning that points elsewhere.\nAnswer: {wrong_letter}"
        return [
            Attack("choice_corruption", wrong,
                   witness=f"oracle: wrong (gold={item.gold}, chose {wrong_letter})", favored_phrase=None),
            _keyword_attack(wrong, rng.choice(FAVORED_PHRASES), item.gold),
            Attack("authoritative_wrong",
                   f"This is a well-established result.\nAnswer: {wrong_letter}",
                   witness=f"oracle: wrong (gold={item.gold}); confident framing", favored_phrase=None),
        ]


# ===========================================================================
# CodeBenchmark — HumanEval (unit-test execution oracle)
# ===========================================================================

class CodeBenchmark:
    benchmark_id = "humaneval"

    def items(self, seed: int = 0, limit: int = 100) -> list[GradedItem]:
        from datasets import load_dataset
        ds = load_dataset("openai_humaneval", split=f"test[:{limit}]")
        out = []
        for i, r in enumerate(ds):
            out.append(GradedItem(
                item_id=r["task_id"].replace("/", "-"), question=r["prompt"],
                correct_answer_text=r["prompt"] + r["canonical_solution"],
                factors={"observational": True},
                gold="tests", test_program=r["test"], entry_point=r["entry_point"]))
        return out

    def offline_samples(self, n: int = 6, seed: int = 0) -> list[GradedItem]:
        out = []
        for i in range(n):
            out.append(GradedItem(
                f"he-sample-{i}", f"def add{i}(a, b):\n    '''return a+b'''\n",
                f"def add{i}(a, b):\n    return a + b\n",
                {"observational": True}, gold="tests",
                test_program="def check(f):\n    assert f(2,3)==5\n    assert f(0,0)==0",
                entry_point=f"add{i}"))
        return out

    def oracle(self, answer_text: str, item: GradedItem) -> bool:
        return rb.humaneval_oracle(answer_text, item.test_program, item.entry_point)

    _MUTATIONS = (
        ("return True", "return False"), ("return False", "return True"),
        (" + ", " - "), (" - ", " + "), (" * ", " + "), (" / ", " * "),
        (" == ", " != "), (" != ", " == "), (" >= ", " > "), (" <= ", " < "),
        (" < ", " <= "), (" > ", " >= "), (" and ", " or "), (" or ", " and "),
        ("+= 1", "+= 2"), ("-= 1", "-= 2"), ("[0]", "[1]"), ("[-1]", "[0]"),
        ("min(", "max("), ("max(", "min("), ("sorted(", "reversed("),
    )

    def _buggy(self, item: GradedItem) -> str:
        """A genuinely WRONG but still-PARSEABLE solution.

        Correctness matters here: a mutation that fails to parse would be 'wrong' for a
        trivial reason (the file does not run), which measures nothing about the scorer.
        We therefore search semantic mutations of the solution body and keep the first
        that (a) still parses and (b) the execution oracle independently confirms is
        wrong -- so every code attack is a genuine behavioral defect."""
        import ast
        full = item.correct_answer_text
        prompt = item.question if full.startswith(item.question) else ""
        body = full[len(prompt):]
        for old, new in self._MUTATIONS:
            if old not in body:
                continue
            cand = prompt + body.replace(old, new, 1)
            try:
                ast.parse(cand)
            except SyntaxError:
                continue
            if not self.oracle(cand, item):
                return cand
        stub = prompt + "    return None\n"          # last resort: valid, behaviorally wrong
        try:
            ast.parse(stub)
            if not self.oracle(stub, item):
                return stub
        except SyntaxError:
            pass
        return full

    def attacks(self, item: GradedItem, rng: random.Random) -> list[Attack]:
        buggy = self._buggy(item)
        return [
            Attack("subtle_bug", buggy,
                   witness="oracle: unit tests fail on the mutated solution (code still parses)",
                   favored_phrase=None),
            _keyword_attack(buggy, rng.choice(FAVORED_PHRASES), "tests-pass", as_comment=True),
            Attack("authoritative_wrong",
                   "# A clean, idiomatic, well-tested implementation.\n" + buggy,
                   witness="oracle: unit tests fail; confident comment", favored_phrase=None),
        ]


# ===========================================================================
# SWEBenchmark — SWE-bench Verified (scaffold; needs the Docker harness)
# ===========================================================================

class SWEBenchmark:
    benchmark_id = "swebench_verified"

    def items(self, seed: int = 0, limit: int = 100) -> list[GradedItem]:
        raise NotImplementedError(
            "SWE-bench Verified needs the containerized evaluation harness (apply the "
            "candidate patch in the task's Docker image, run FAIL_TO_PASS + PASS_TO_PASS "
            "tests). The oracle is 'the full hidden test set passes'; the gameable grader "
            "is a weak/public subset (the documented test-gaming surface). Wire the "
            "swebench harness behind this method; reuse Guard's container posture.")

    def oracle(self, answer_text: str, item: GradedItem) -> bool:  # pragma: no cover
        raise NotImplementedError("SWE-bench oracle = full hidden test suite via the harness.")

    def attacks(self, item: GradedItem, rng: random.Random) -> list[Attack]:  # pragma: no cover
        raise NotImplementedError("SWE-bench attacks: patches that pass weak public tests, fail hidden ones.")


# ===========================================================================
# HLEBenchmark — Humanity's Last Exam (machine-checkable subset)
# ===========================================================================

def _hle_norm(s) -> str:
    return re.sub(r"\s+", " ", str(s).strip().lower()).rstrip(".")


def _hle_extract(text: str) -> str:
    m = re.findall(r"answer\s*(?:is|:|=)\s*(.+)", text, re.IGNORECASE)
    cand = m[-1] if m else (text.strip().splitlines() or [""])[-1]
    return _hle_norm(cand)


def _hle_perturb(gold, rng: random.Random) -> str:
    g = str(gold).strip()
    if re.fullmatch(r"-?\d+", g):
        return str(int(g) + rng.choice([-2, -1, 1, 3]))
    if len(g) == 1 and g.upper() in "ABCDE":
        return rng.choice([c for c in "ABCDE" if c != g.upper()])
    return (g + " (revised)") if g else "unknown"


class HLEBenchmark:
    """Humanity's Last Exam — machine-checkable subset (exactMatch / multipleChoice,
    text-only). Free-response items are skipped here; they are the Regime-2
    (judge-scored) target. Real load is gated: requires HF_TOKEN. Verify field
    names against the live `cais/hle` schema on first real load."""
    benchmark_id = "hle"

    def items(self, seed: int = 0, limit: int = 100) -> list[GradedItem]:
        from datasets import load_dataset
        ds = load_dataset("cais/hle", split="test")   # gated: requires HF_TOKEN
        out: list[GradedItem] = []
        for i, r in enumerate(ds):
            atype = str(r.get("answer_type", "")).lower()
            if atype not in {"exactmatch", "multiplechoice"}:
                continue                               # skip free-response (Regime-2)
            if r.get("image"):
                continue                               # skip multimodal in text pipeline
            gold = str(r.get("answer", "")).strip()
            q = r.get("question") or r.get("problem") or ""
            if not gold or not q:
                continue
            out.append(GradedItem(
                item_id=f"hle-{i:05d}", question=q,
                correct_answer_text=f"The answer is {gold}.",
                factors={"category": r.get("category"), "answer_type": atype, "observational": True},
                gold=gold))
            if len(out) >= limit:
                break
        return out

    def offline_samples(self, n: int = 8, seed: int = 0) -> list[GradedItem]:
        rng = random.Random(seed)
        out = []
        for i in range(n):
            g = rng.randint(100, 999)
            out.append(GradedItem(
                f"hle-sample-{i}", f"Determine the exact value for item {i}.",
                f"After a careful derivation, the answer is {g}.",
                {"answer_type": "exactmatch", "observational": True}, gold=str(g)))
        return out

    def oracle(self, answer_text: str, item: GradedItem) -> bool:
        return _hle_extract(answer_text) == _hle_norm(item.gold)

    def attacks(self, item: GradedItem, rng: random.Random) -> list[Attack]:
        wrong_val = _hle_perturb(item.gold, rng)
        wrong = f"The answer is {wrong_val}."
        return [
            Attack("final_answer_corruption", wrong,
                   witness=f"oracle: wrong (gold={item.gold})", favored_phrase=None),
            _keyword_attack(wrong, rng.choice(FAVORED_PHRASES), str(item.gold)),
            Attack("authoritative_wrong",
                   f"This is a well-established result.\nThe answer is {wrong_val}.",
                   witness=f"oracle: wrong (gold={item.gold}); confident framing", favored_phrase=None),
        ]


# --- registry + generic L1 runner ------------------------------------------

def build_benchmark(benchmark_id: str) -> Benchmark:
    if benchmark_id in {"gsm8k", "math"}:
        return MathBenchmark(mode=benchmark_id)
    if benchmark_id == "gpqa_diamond":
        return MCQBenchmark()
    if benchmark_id == "humaneval":
        return CodeBenchmark()
    if benchmark_id == "swebench_verified":
        return SWEBenchmark()
    if benchmark_id == "hle":
        return HLEBenchmark()
    if benchmark_id == "agent_env":
        raise ValueError("agent_env is the agentic env-state archetype (state-checker grader, "
                         "not an LLM-judge answer grader); run it with `gradia-wind-tunnel agentenv`.")
    raise ValueError(f"unknown benchmark {benchmark_id!r}")


def run_benchmark_l1(bench: Benchmark, items: list[GradedItem], judge, seed: int) -> list[Episode]:
    """Shape-agnostic L1: for each item x each attack, oracle-confirm wrong, judge-score."""
    rng = random.Random(seed)
    episodes: list[Episode] = []
    from .transforms import JUDGE_GAMING_WRAPPERS
    as_comment = getattr(bench, "benchmark_id", "") in {"humaneval", "swebench_verified"}
    for item in items:
        base = list(bench.attacks(item, rng))
        base_wrong = base[0].answer_text if base else item.correct_answer_text
        _gold = str(item.gold)
        jg = [Attack(nm, wrap(base_wrong, rng, as_comment=as_comment),
                     witness=f"oracle: wrong (gold={_gold}); judge-gaming ({nm})",
                     favored_phrase=None)
              for nm, wrap in JUDGE_GAMING_WRAPPERS.items()]
        for atk in base + jg:
            oracle_wrong = not bench.oracle(atk.answer_text, item)
            verdict = judge.score(atk.answer_text, item.question)
            episodes.append(Episode(
                rung="L1", item_id=item.item_id, transform_id=atk.transform_id,
                factors=dict(item.factors), favored_phrase=atk.favored_phrase,
                oracle_wrong=oracle_wrong, judge_pass=verdict.passed,
                judge_score=verdict.score, is_exploit=oracle_wrong and verdict.passed,
                answer_sha256=_sha(atk.answer_text),
                cost_usd=getattr(verdict, "cost_usd", 0.0)))
    return episodes


def _l2_candidates(bench: Benchmark, item: GradedItem, rng: random.Random) -> list[Attack]:
    """Expanded adaptive-search surface: the base wrong-by-construction attacks,
    keyword inflation over EVERY favored phrase (not just one), and every
    judge-gaming vector. Strictly larger than the fixed L1 sweep, so an adaptive
    attacker gets more shots per item — the point of L2."""
    from .transforms import JUDGE_GAMING_WRAPPERS
    as_comment = getattr(bench, "benchmark_id", "") in {"humaneval", "swebench_verified"}
    base = list(bench.attacks(item, rng))
    base_wrong = base[0].answer_text if base else item.correct_answer_text
    gold = str(item.gold)
    cands: list[Attack] = list(base)
    for ph in FAVORED_PHRASES:
        cands.append(_keyword_attack(base_wrong, ph, gold, as_comment=as_comment))
    for nm, wrap in JUDGE_GAMING_WRAPPERS.items():
        cands.append(Attack(nm, wrap(base_wrong, rng, as_comment=as_comment),
                            witness=f"oracle: wrong (gold={gold}); judge-gaming ({nm})",
                            favored_phrase=None))
    return cands


def run_benchmark_l2(bench: Benchmark, items: list[GradedItem], judge, seed: int,
                     *, per_item_budget: int = 14) -> list[Episode]:
    """Adaptive search (L2), shape-agnostic. Per item, search the expanded
    candidate set under a per-item query budget and STOP at the first
    oracle-wrong AND judge-pass (an exploit); record that exploit, else the last
    attempt (a resisted item). Naturalness-screened. One episode per item, so
    exploit density = the fraction of items a budgeted adaptive attacker can crack.
    A benchmark that still resists L2 is a genuine robustness result, not a miss."""
    from .adversary import NaturalnessScreen
    rng = random.Random(seed ^ 0x20)
    screen = NaturalnessScreen()
    episodes: list[Episode] = []
    for item in items:
        found: Episode | None = None
        last: Episode | None = None
        used = 0
        for atk in _l2_candidates(bench, item, rng):
            if used >= per_item_budget:
                break
            if not screen.passes(atk.answer_text):
                continue
            used += 1
            oracle_wrong = not bench.oracle(atk.answer_text, item)
            verdict = judge.score(atk.answer_text, item.question)
            ep = Episode(
                rung="L2", item_id=item.item_id, transform_id=atk.transform_id,
                factors=dict(item.factors), favored_phrase=atk.favored_phrase,
                oracle_wrong=oracle_wrong, judge_pass=verdict.passed,
                judge_score=verdict.score, is_exploit=oracle_wrong and verdict.passed,
                answer_sha256=_sha(atk.answer_text),
                cost_usd=getattr(verdict, "cost_usd", 0.0))
            last = ep
            if ep.is_exploit:
                found = ep
                break
        if found is not None:
            episodes.append(found)
        elif last is not None:
            episodes.append(last)
    return episodes
