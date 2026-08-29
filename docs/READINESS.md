# End-to-end readiness — is the foundation ready to run benchmarks?

Short answer: **yes, the instrument is complete and self-verifying.** The only
thing between here and real results is your API key + the Guard gateway.

## What is DONE and green (71 tests, on your Mac)

| Capability | Status | Proof |
|---|---|---|
| Procedural generator + exact oracle + factors | ✅ | tests; `make demo` |
| Wrong-by-construction transform catalog (per answer shape) | ✅ | tests |
| Four judge architectures + real `LLMJudge` | ✅ | tests |
| Live grader through Guard (Anthropic Messages, key never in process) | ✅ wired | `AnthropicGuardGrader`, offline-verified |
| Threat rungs L0–L3 + naturalness screen + budget meter | ✅ | tests |
| Causal-slice localizer + prospective validation | ✅ | tests |
| Patcher (3 modalities) + autoimmunity guard | ✅ | tests |
| Convergence loop + classification | ✅ | tests |
| Hash-committed regression vault (reveal + tamper detect) | ✅ | tests |
| Analyst: spectrum, exploit-DNA, disagreement detector | ✅ | tests |
| End-to-end orchestrator + self-verifying report | ✅ | `make run` |
| **All five benchmarks** (GSM8K/MATH/GPQA/HumanEval runnable; SWE-bench scaffold) | ✅ | tests; `suite` |
| **Research-grade evidence capture** (frames + manifest, every number recomputable) | ✅ | tests; `capture.verify_bundle` |
| **Analytics sink** (frames stream to Gradia analytics / warehouse) | ✅ | tests |
| **Real universe forks on the Gradia engine** (single-variable + witness) | ✅ demonstrated | `examples/gradia_capability_demo.py`, tests |
| Fail-closed preregistration, git-pinned + self-digested | ✅ frozen | `preregistrations/…gsm8k-01.json` |

## What is YOURS to do for real results (needs your key/gateway/Zenodo)

1. **Pin the dataset snapshots** in `contracts.TARGET_BENCHMARKS` and re-freeze.
2. **Publish the frozen prereg to Zenodo** (`docs/ZENODO-PREREG-DESCRIPTION.md`) → DOI.
3. **Bring up the Guard gateway**, export `GRADIA_GUARD_LOCAL_CAPABILITY`, and:
   ```bash
   python -m gradia_wind_tunnel.cli suite --benchmark gsm8k --real --live \
     --model claude-opus-5 --gateway http://127.0.0.1:8787 \
     --prereg-sha256 <frozen> --out results/gsm8k-live
   ```
   → first real exploit-density number + a recomputable evidence bundle.
4. Repeat across MATH / GPQA / HumanEval; wire the SWE-bench harness; run the
   convergence loop; generate figures.

## Does this prove Gradia runs complex custom environments?

Yes — `examples/gradia_capability_demo.py` runs a bespoke custom environment on the
real Gradia engine with tool actions, a single-variable branch, and a tamper-evident
proof chain. The universe-fork causal method rides on that same substrate. Pointing
the forks at your v4r1 mortgage scenarios is content wiring, not new capability.

## Known follow-ups (not blockers)

- Guard: fix the scope-sort collation split (one shared code-unit comparator) and
  publish the `0.1.0-beta.1` npm release — both flagged earlier.
- Stream `frames.ndjson` to your live Gradia analytics endpoint (sink is built).

**Bottom line:** the end-to-end foundation is ready. The next action that produces a
real result is one live run.
