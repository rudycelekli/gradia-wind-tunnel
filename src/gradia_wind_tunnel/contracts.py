"""Typed contracts and frozen version identifiers for the Wind Tunnel.

Every version string here is hashed into the preregistration. Changing a
contract without bumping its version and re-freezing is a protocol violation:
the verifier recomputes these and refuses a mismatch (fail-closed, like the
rest of the program).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

# --- frozen component versions (hashed into the prereg) --------------------
SCHEMA_PREREGISTRATION = "gradia-wind-tunnel-preregistration.v1"
SCHEMA_EPISODE = "gradia-wind-tunnel-episode.v1"
SCHEMA_VAULT_MANIFEST = "gradia-wind-tunnel-vault-manifest.v1"

TRANSFORM_CATALOG_VERSION = "gradia-wind-tunnel-transform-catalog.v1"
ORACLE_SUITE_VERSION = "gradia-wind-tunnel-oracle-suite.v1"
ANALYST_VERSION = "gradia-wind-tunnel-analyst.v1"

Rung = Literal["L0", "L1", "L2", "L3"]
Verdict = Literal["PASS", "FAIL"]
Truth = Literal["CORRECT", "WRONG"]
JudgeArchitecture = Literal[
    "single", "naive_ensemble", "self_commitment", "rubric_decomposed"
]
PatchModality = Literal["rubric_edit", "judge_arch", "curriculum_retrain"]
GraderKind = Literal[
    # what component of the benchmark's scoring pipeline we attack
    "exact_match_extractor",   # regex/normalizer that decides the "answer"
    "llm_judge",               # an LLM grades free-form output
    "rubric_grader",           # criterion-decomposed grading
    "unit_test_verifier",      # execution-checked; weak tests are gameable
]


@dataclass(frozen=True)
class BenchmarkSpec:
    """A named public benchmark: its machine oracle + the gameable grader."""
    benchmark_id: str
    kind: Literal["math", "code", "mcq"]
    oracle_kind: Literal["numeric_equality", "unit_tests", "key_match"]
    grader_kinds: tuple[GraderKind, ...]
    snapshot: str          # pinned commit / release / hash of the benchmark data
    famous_precedent: str  # why it is famous/frontier (for the paper)


@dataclass(frozen=True)
class Hypothesis:
    hid: str
    statement: str
    precommitted_direction: str
    interesting_if_false: str


# --- the preregistered hypotheses (directions committed before results) ----
HYPOTHESES: tuple[Hypothesis, ...] = (
    Hypothesis("H1", "Iterated attack-and-patch of the scorer converges on held-out budget for >=1 architecture.",
               "monotone decreasing exploit density over cycles", "plateau/oscillation is a stronger, more surprising finding"),
    Hypothesis("H2", "A patch closing family F generalizes to held-out families less than to F itself.",
               "patch-generalization gamma < 1 (whack-a-mole)", "gamma ~= 1 would mean general immunity is achievable"),
    Hypothesis("H3", "Exploit-closure and correct-answer preservation trade off (autoimmunity).",
               "negative correlation; a real Pareto frontier", "no trade-off would mean free repair"),
    Hypothesis("H4", "Judge self-commitment dominates per-dollar but does not reach zero exploitability.",
               "lowest exploit density per dollar, but > 0", "reaching 0 would mean a structural cure exists"),
    Hypothesis("H5", "Named causal slices predict failure on prospectively generated held-out items above baselines.",
               "predicted-slice rate > broad-slice and random-slice controls", "no lift would falsify causal identification"),
    Hypothesis("H6", "For oracle-less scorers (LLM-judge/rubric), adaptive search finds semantics-preserving inputs that move the verdict above the natural rate; exploitability concentrates in high judge-disagreement regions.",
               "L2 invariance-violation rate > L0 natural rate; disagreement-region exploit rate > agreement-region", "invariance-stable judges would mean oracle-less benchmarks are safer than feared (also publishable)"),
    Hypothesis("H7", "In agentic/universe tasks the witnessed record proves a nonzero, human-free rate of accepted answers that assert facts the world contradicts (witnessed confabulation).",
               "witnessed-confabulation rate > 0 with zero human labels", "a zero rate bounds the witnessed substrate reach as a partial oracle"),
)


# --- the target benchmarks (frontier + famous + machine-checkable) ---------
# Snapshots are placeholders to be pinned at freeze.
TARGET_BENCHMARKS: tuple[BenchmarkSpec, ...] = (
    BenchmarkSpec("gsm8k", "math", "numeric_equality",
                  ("exact_match_extractor", "llm_judge"), "{{GSM8K_SNAPSHOT}}",
                  "classic anchor; the self-play reward-hacking paper's turf (direct comparability)"),
    BenchmarkSpec("math", "math", "numeric_equality",
                  ("exact_match_extractor", "llm_judge"), "{{MATH_SNAPSHOT}}",
                  "competition math; more frontier than GSM8K; still exact-answer"),
    BenchmarkSpec("gpqa_diamond", "mcq", "key_match",
                  ("exact_match_extractor",), "{{GPQA_SNAPSHOT}}",
                  "graduate-level, Google-proof; current frontier reasoning benchmark"),
    BenchmarkSpec("humaneval", "code", "unit_tests",
                  ("unit_test_verifier", "llm_judge"), "{{HUMANEVAL_SNAPSHOT}}",
                  "classic code anchor; execution oracle"),
    BenchmarkSpec("swebench_verified", "code", "unit_tests",
                  ("unit_test_verifier",), "{{SWEBENCH_SNAPSHOT}}",
                  "frontier agentic-coding benchmark with a DOCUMENTED test-gaming precedent"),
    BenchmarkSpec("hle", "mcq", "key_match",
                  ("exact_match_extractor",), "{{HLE_SNAPSHOT}}",
                  "current frontier multidisciplinary reasoning benchmark reported in recent frontier model cards; machine-checkable subset only (free-response half is a Regime-2 target)"),
)
