# End-to-end readiness — is the foundation ready to run benchmarks?

Short answer: **the evaluation-metrology instrument is implemented and
self-verifying, and real evidence exists.** It is not yet a completed model-training
or frontier-RL steering system. `program-readiness` is the canonical machine-readable
boundary.

## What is DONE and green (165 property/control tests)

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
| Public benchmark families (GSM8K/MATH/GPQA/HumanEval/HLE plus live SWE harness) | ✅ mixed live/offline | tests; `suite`; `swebench-live`; `swebench-merge` |
| **Research-grade evidence capture** (frames + manifest, every derived aggregate recomputable) | ✅ | tests; `gradia-wind-tunnel verify-bundle BUNDLE_DIR` |
| **Public timestamp anchoring** (preregistration + evidence heads; honest offline refusal) | ✅ | tests; `gradia-wind-tunnel anchor` |
| **Analytics sink** (frames stream to Gradia analytics / warehouse) | ✅ | tests |
| **Real universe forks on the Gradia engine** (single-variable + witness) | ✅ demonstrated | `examples/gradia_capability_demo.py`, tests |
| Fail-closed preregistration, git-pinned + self-digested | ✅ frozen | `preregistrations/…gsm8k-01.json` |

## What remains for a training-impact result

1. Freeze disjoint train, validation and untouched held-out memberships.
2. Obtain explicit evaluation/training/raw-trajectory rights for the intended
   recipient and compile a Gradia training-steering order.
3. Authorize one real trainer separately; the order itself is intentionally
   non-dispatchable.
4. Compare baseline and candidate at matched runtime/scaffold/evaluator/seeds,
   with item-clustered uncertainty and autoimmunity/regression metrics.
5. Re-attack the hidden vault and report cured, relocated, regressed or
   inconclusive. Do not translate a scorer improvement into model lift.

## Does this prove Gradia runs complex custom environments?

Yes — `examples/gradia_capability_demo.py` runs a bespoke custom environment on the
real Gradia engine with tool actions, a single-variable branch, and a tamper-evident
proof chain. The universe-fork causal method rides on that same substrate. Pointing
the forks at your v4r1 mortgage scenarios is content wiring, not new capability.

## Open research/product gates

- L2 is bounded typed-catalog search, not autonomous model-authored hypothesis
  generation.
- Existing repair/curriculum arms harden the evaluator offline; they are not
  optimizer-backed model training.
- The live SWE harness and older `SWEBenchmark` protocol surface still need one
  unified adapter.
- Managed scheduling, retention and Analytics+ ingestion need deployed cross-repo
  proof.
- The open v1 verifier and reference witness are usable today; a cross-program
  Proof Pack schema package, badge, GitHub Action and hosted managed index remain
  separate distribution milestones.

**Bottom line:** the apparatus already produces real, replayable metrology. The next
scientific threshold is a rights-clean, prospectively frozen, multi-seed training
study whose result survives held-out re-attack.
