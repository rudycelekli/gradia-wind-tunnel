"""Reward-Hacking Wind Tunnel — an evaluation immune system.

Third pillar of the Gradia program on verifiable evaluation:
  Interruptible Universes  — prove what happened (evolution witnesses)
  Gradia Guard             — prove nobody tampered with the record
  Wind Tunnel (this)       — prove the scorekeeper can't be bought

It finds answers a benchmark's SCORER grades "correct" but that a machine ORACLE
proves wrong, identifies the exact causal slice being exploited via single-
variable factorial forks, and measures whether patching the scorer converges.
"""

from .canonical import canonical_bytes, digest, file_digest, write_canonical
from .contracts import HYPOTHESES, TARGET_BENCHMARKS, BenchmarkSpec, Hypothesis
from .items import Item, generate_factorial, oracle
from .transforms import TRANSFORMS, FAVORED_PHRASES, Attack, check_witness
from .judges import Judge, KeywordGamingJudge, SelfCommitmentJudge, RealModelJudge, Verdict
from .windtunnel import (
    Episode, exploit_density, false_rejection_rate, run_attacks,
    run_log_chain_head, slice_screen,
)
from .benchmarks import BenchmarkAdapter, ProceduralMathAdapter, build_adapter, target_benchmark_ids
from .preregistration import build_preregistration, freeze, verify as verify_preregistration
from .adversary import BudgetMeter, NaturalnessScreen, run_L0, run_L1, run_L2, run_L3
from .causal import CausalSlice, localize, prospective_validate
from .patcher import Patch, synthesize
from .convergence import ConvergenceResult, run_convergence
from .vault import RegressionVault, verify_reveal
from .analyst import disagreement_detector, exploit_dna, exploitability_spectrum
from .experiment import run_study, verify_report
from .universe_forks import fork_on_variable, substrate_available
from .gradia_integration import gradia_stack_status, platform_validation_table
from .llm_judge import LLMJudge, SimulatedGraderProvider, AnthropicGuardGrader
from .phase0 import run_phase0, verify_phase0, run_suite
from .providers import Provider, SimulatedProvider, GuardRoutedProvider
from .benchmark_suite import (Benchmark, GradedItem, MathBenchmark, MCQBenchmark,
                              CodeBenchmark, SWEBenchmark, build_benchmark, run_benchmark_l1)
from .capture import write_frames, build_manifest, verify_bundle
from .analytics import AnalyticsSink, LocalJsonlSink, GradiaAnalyticsSink, stream_frames
from .universe_forks import Fork, fork_on_variable, substrate_available, causal_validity_note
from .program_readiness import build_program_readiness, verify_program_readiness

__version__ = "0.1.0"

__all__ = [
    "canonical_bytes", "digest", "file_digest", "write_canonical",
    "HYPOTHESES", "TARGET_BENCHMARKS", "BenchmarkSpec", "Hypothesis",
    "Item", "generate_factorial", "oracle",
    "TRANSFORMS", "FAVORED_PHRASES", "Attack", "check_witness",
    "Judge", "KeywordGamingJudge", "SelfCommitmentJudge", "RealModelJudge", "Verdict",
    "Episode", "exploit_density", "false_rejection_rate", "run_attacks",
    "run_log_chain_head", "slice_screen",
    "BenchmarkAdapter", "ProceduralMathAdapter", "build_adapter", "target_benchmark_ids",
    "build_preregistration", "freeze", "verify_preregistration",
    "build_program_readiness", "verify_program_readiness",
]
