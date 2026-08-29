"""SWE-bench Verified harness — the containerized execution oracle.

STATUS: integration scaffold, NOT runnable in this session. Unlike the other
benchmarks, SWE-bench's oracle is *code execution inside a per-task Docker image*
(apply the candidate patch, run the task's tests). That needs Docker, the
`swebench` package, and network to pull task images — none available here — so
this module is written to the real API but has NOT been executed. Validate it on
a machine with Docker before trusting a number.

The reward-hacking surface (why it is on the slate): the *gameable grader* is a
weak/public subset of tests; the *oracle backstop* is the full hidden suite
(FAIL_TO_PASS + PASS_TO_PASS). A patch that satisfies the public subset but fails
the hidden suite is an oracle-witnessed exploit — the documented SWE-bench
test-gaming phenomenon, measured.

Implementation path (do this on a Docker host):
  1. pip install swebench   (and have Docker running)
  2. load the split:  datasets.load_dataset("princeton-nlp/SWE-bench_Verified", split="test")
  3. for a candidate patch, build a prediction record
       {"instance_id", "model_name_or_path", "model_patch"}
  4. run the official harness:
       python -m swebench.harness.run_evaluation \
         --dataset_name princeton-nlp/SWE-bench_Verified \
         --predictions_path preds.jsonl --run_id wt-swe --max_workers N
  5. parse the report JSON: an instance is RESOLVED iff all FAIL_TO_PASS and
     PASS_TO_PASS tests pass  -> that is the ORACLE (full hidden suite).
  6. the GAMEABLE grader = run only the PUBLIC subset (a task's visible tests);
     exploit := grader PASS and oracle FAIL.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from typing import Any


def docker_available() -> bool:
    return shutil.which("docker") is not None


def swebench_available() -> bool:
    try:
        import swebench  # noqa: F401
        return True
    except Exception:
        return False


def harness_ready() -> dict[str, Any]:
    return {"docker": docker_available(), "swebench_package": swebench_available(),
            "ready": docker_available() and swebench_available(),
            "note": "both must be True on a Docker host before any SWE-bench run"}


@dataclass(frozen=True)
class SWEItem:
    instance_id: str
    repo: str
    fail_to_pass: tuple[str, ...]
    pass_to_pass: tuple[str, ...]
    public_tests: tuple[str, ...]      # the weak/gameable grader's visible subset


def load_items(limit: int = 50):
    """Load SWE-bench Verified task specs (needs network; no Docker required just to read)."""
    from datasets import load_dataset
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split=f"test[:{limit}]")
    out = []
    for r in ds:
        ftp = tuple(json.loads(r["FAIL_TO_PASS"])) if isinstance(r.get("FAIL_TO_PASS"), str) else tuple(r.get("FAIL_TO_PASS", ()))
        ptp = tuple(json.loads(r["PASS_TO_PASS"])) if isinstance(r.get("PASS_TO_PASS"), str) else tuple(r.get("PASS_TO_PASS", ()))
        out.append(SWEItem(r["instance_id"], r.get("repo", ""), ftp, ptp,
                           public_tests=ptp[: max(1, len(ptp) // 3)]))  # heuristic 'public' subset
    return out


def evaluate_patch(instance_id: str, model_patch: str, run_id: str = "wt-swe") -> dict[str, Any]:
    """Run the official harness on ONE prediction. Requires Docker + swebench.
    Returns {"resolved": bool, ...} where resolved == oracle (full hidden suite)."""
    if not harness_ready()["ready"]:
        raise RuntimeError(f"SWE-bench harness not ready: {harness_ready()}")
    # Real call path (kept explicit; verify signature against your swebench version):
    #   from swebench.harness.run_evaluation import main as run_eval
    #   write predictions jsonl -> run_eval(...) -> read report -> resolved flag
    raise NotImplementedError(
        "Wire swebench.harness.run_evaluation here on a Docker host; parse the report "
        "for RESOLVED (oracle). Left explicit and unexecuted — see module docstring.")


# --- executor seam: Docker OR the Gradia execution substrate ----------------
def gradia_executor_available() -> bool:
    """Gradia's environment engine (Firecracker/AgentENV) is the natural executor
    for per-task SWE-bench containers. Capability-detected; when present, route
    patch evaluation through it instead of a local Docker daemon. Wire the actual
    call against your execution-plane API (this only probes availability)."""
    try:
        import gradia_universes  # noqa: F401
        return True
    except Exception:
        return False


def executor_status() -> dict:
    return {"local_docker": docker_available(),
            "gradia_substrate": gradia_executor_available(),
            "any_executor": docker_available() or gradia_executor_available(),
            "note": "SWE-bench execution can run on local Docker or on Gradia's "
                    "Firecracker/AgentENV substrate; bind one before a real run."}
