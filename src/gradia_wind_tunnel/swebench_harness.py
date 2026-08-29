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


def evaluate_patch(instance_id: str, model_patch: str, *, run_id: str = "wt-swe",
                   dataset_name: str = "princeton-nlp/SWE-bench_Verified",
                   max_workers: int = 1, timeout: int = 2400) -> dict[str, Any]:
    """Run the OFFICIAL SWE-bench harness on ONE prediction via its documented CLI
    (`python -m swebench.harness.run_evaluation`). Requires an executor (Docker or
    the Gradia substrate) + the swebench package. Returns {"resolved": bool|None,...}
    where resolved == the ORACLE (full hidden FAIL_TO_PASS + PASS_TO_PASS suite).

    Executes real containers, so it runs on a Docker host — not in this sandbox.
    Parsing is defensive across swebench report-schema versions; verify the
    resolved flag against the written report on first use."""
    import glob
    import json as _json
    import os
    import subprocess
    import tempfile

    if not (docker_available() or gradia_executor_available()):
        raise RuntimeError(f"no executor available: {executor_status()}")
    if not swebench_available():
        raise RuntimeError("swebench package not installed: `pip install swebench` on the Docker host")

    with tempfile.TemporaryDirectory() as td:
        preds = os.path.join(td, "preds.jsonl")
        with open(preds, "w") as f:
            f.write(_json.dumps({"instance_id": instance_id,
                                 "model_name_or_path": "wind-tunnel",
                                 "model_patch": model_patch}) + "\n")
        cmd = ["python", "-m", "swebench.harness.run_evaluation",
               "--dataset_name", dataset_name, "--predictions_path", preds,
               "--run_id", run_id, "--max_workers", str(max_workers),
               "--instance_ids", instance_id]
        proc = subprocess.run(cmd, cwd=td, capture_output=True, text=True, timeout=timeout)
        # the harness writes <model>.<run_id>.json (cwd or td); find it and read RESOLVED
        resolved = None
        report: dict[str, Any] = {}
        for rp in sorted(glob.glob(os.path.join(td, "*.json")) + glob.glob(f"*{run_id}*.json")):
            try:
                data = _json.load(open(rp))
            except Exception:
                continue
            blob = _json.dumps(data)
            if instance_id in blob:
                report = data
                for key in ("resolved_ids", "resolved_instances", "resolved"):
                    v = data.get(key) if isinstance(data, dict) else None
                    if isinstance(v, list):
                        resolved = instance_id in v
                    elif isinstance(v, dict) and instance_id in v:
                        resolved = bool(v[instance_id])
                if resolved is None and isinstance(data, dict) and instance_id in data:
                    inst = data[instance_id]
                    if isinstance(inst, dict):
                        resolved = bool(inst.get("resolved", inst.get("RESOLVED_FULL")))
                break
        return {"instance_id": instance_id, "resolved": resolved,
                "returncode": proc.returncode, "report": report,
                "stdout_tail": proc.stdout[-800:], "stderr_tail": proc.stderr[-400:],
                "note": "resolved==oracle (full hidden suite). None => parse the written report by hand once."}


def gold_patch_smoke(instance_id: str | None = None, *, run_id: str = "wt-swe-smoke") -> dict[str, Any]:
    """Readiness proof to run ON the Docker host: evaluate a task's GOLD patch — it
    must resolve (True). If the gold patch resolves, the execution oracle is wired
    correctly and the only remaining research step is generating test-gaming patches."""
    from datasets import load_dataset
    ds = load_dataset("princeton-nlp/SWE-bench_Verified", split="test[:20]")
    row = None
    for r in ds:
        if instance_id is None or r["instance_id"] == instance_id:
            row = r
            break
    if row is None:
        raise RuntimeError(f"instance {instance_id!r} not in the first slice")
    res = evaluate_patch(row["instance_id"], row["patch"], run_id=run_id)
    res["expected_resolved"] = True
    res["smoke_ok"] = (res["resolved"] is True)
    return res


def readiness_report(try_dataset: bool = True, limit_probe: int = 1) -> dict[str, Any]:
    """The SWE-bench readiness ladder: executor -> package -> dataset access ->
    ready. Says exactly what to bring up next. Safe to run anywhere."""
    rep: dict[str, Any] = {
        "executor": executor_status(),
        "swebench_package": swebench_available(),
        "dataset_access": None,
        "sample_instance": None,
        "ready_to_execute": False,
        "next_step": "",
    }
    if try_dataset:
        try:
            items = load_items(limit=limit_probe)
            rep["dataset_access"] = True
            if items:
                it = items[0]
                rep["sample_instance"] = {
                    "instance_id": it.instance_id, "repo": it.repo,
                    "n_fail_to_pass": len(it.fail_to_pass),
                    "n_pass_to_pass": len(it.pass_to_pass),
                    "n_public_subset": len(it.public_tests)}
        except Exception as e:
            rep["dataset_access"] = False
            rep["dataset_error"] = f"{type(e).__name__}: {e}"[:200]
    ex = rep["executor"]
    rep["ready_to_execute"] = bool(ex["any_executor"] and rep["swebench_package"]
                                   and rep["dataset_access"] in (True, None))
    if not ex["any_executor"]:
        rep["next_step"] = "bring up an executor: start Docker locally OR bind Gradia's Firecracker/AgentENV substrate"
    elif not rep["swebench_package"]:
        rep["next_step"] = "pip install swebench (on the executor host)"
    elif rep["dataset_access"] is False:
        rep["next_step"] = "grant HF access / set HF_TOKEN for princeton-nlp/SWE-bench_Verified"
    else:
        rep["next_step"] = "READY: run gold_patch_smoke() to prove the oracle, then the test-gaming exploit sweep"
    return rep


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
