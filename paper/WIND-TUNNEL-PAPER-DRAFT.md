---
title: "The Reward-Hacking Wind Tunnel: An Evaluation Immune System that Attacks, Localizes, and Repairs Benchmark Scorers"
author: "Rudy M. Celekli, Gradia Research"
date: "Pre-registered design — no empirical results yet — draft of 29 August 2026"
---

> **Pre-results boundary.** This manuscript states a design, a preregistered
> protocol, and a runnable pilot. It reports **no empirical result about any real
> model or benchmark yet.** All quantities below are defined estimands; every
> reported number in the final paper will be recomputable from a committed
> evidence index, and the hidden regression suite's chain head is published before
> any Phase-1 run. Claims are scoped by the preregistration's `interpretation`
> field: we study whether a benchmark's **scoring pipeline** can be gamed and
> whether repairing it converges — not whether any model is broadly weak or any
> benchmark worthless.

## Abstract

Modern AI evaluation trusts a scorekeeper: an answer extractor, an LLM judge, a
rubric grader, or a unit-test verifier that turns a model's output into a number.
We show this scorekeeper is an attack surface, and we build the first system that
**closes and measures the loop** of attacking it and repairing it. The Reward-
Hacking Wind Tunnel searches for answers a famous public benchmark's scorer grades
*correct* but that a machine **oracle** proves *wrong* — every exploit confirmed
with no human label — then identifies the **exact causal slice** being exploited by
intervening on one variable at a time in a branchable, witnessed universe, and
measures whether iterated patching of the scorer **converges, plateaus, or merely
relocates the flaw**. We contribute: (C1) witnessed universes as a *causal
instrument* for evaluation failure — turning "which slice is exploited?" from a
confounded correlation into an identified interaction effect; (C2) the first
convergence measurement of evaluator repair, with a patch-generalization statistic;
(C3) oracle-witnessed, wrong-by-construction attacks that need zero human labels;
(C4) an *autoimmunity* metric quantifying how many correct answers each patch
starts wrongly rejecting; (C5) a verifiable, contamination-proof protocol whose
hidden regression suite is hash-committed before any result exists; and (C6) a
**platform validation** — the entire study (generation, adversarial search, causal
forks, judging, evidence, preregistration, verification) executes on the Gradia
stack, demonstrating that the program's tooling can run a complete research study
end to end. Every attack, judge call, and patch is a tamper-evident receipt. This
is the third pillar of a program on verifiable evaluation, after Interruptible
Universes (proving *what happened*) and Gradia Guard (proving *the record was not
tampered with*).

## 1. Introduction

Prior work in this program established that agent benchmarks under-verify
world-state [Interruptible Universes] and that runtime evidence must be
tamper-evident and coverage-honest [Gradia Guard]. This paper closes the loop on
the last trusted component — the scorekeeper — and asks a question the field has
not: when you attack a benchmark's scorer and then patch it, does the evaluation
system converge, or is it whack-a-mole forever?

*Public benchmarks can tell you a model is being gamed. Only a branchable,
witnessed universe can tell you which counterfactual causes it — because only there
can you change one fact and prove you changed nothing else.* That single capability
reframes what a universe is: not a benchmark format, but a causal-inference
instrument for model-evaluation failure. It also closes an entire loop — the tunnel
finds the exploit (evaluation), the fork names the exact slice (environment
manipulation), and the named slice becomes a data-generation order (training data).

**Contributions.** C1–C5 above. Section 3 formalizes the estimands; Sections 4–7
give the method; Section 8 the (to-be-run) experiments; Section 10 responsible
disclosure. A runnable pilot (this repository) already realizes the core loop
offline with 16/16 property tests green.

## 2. The benchmark scorer as an attack surface

A benchmark's score is produced by a *scoring pipeline*, not by truth directly.
The pipeline's gameable components are: the **answer extractor** (a regex or model
that decides what the output "answered"), the **LLM judge** or **rubric grader**
(when grading is a judgment), and the **unit-test verifier** (when tests are weak —
e.g., the documented test-gaming on frontier agentic-coding benchmarks). We attack
the pipeline; a machine **oracle** (strong gold answer / strong hidden tests) is the
ground-truth backstop that confirms wrongness with no human. We report four threat
rungs separately (never pooled): **L0** natural incidence (no adversary), **L1**
metamorphic mutation, **L2** budgeted adaptive search under a naturalness
constraint, **L3** patch-aware re-attack.

## 3. Formal statement (estimands)

*(defines: item factor vector φ(x); oracle t; scorer/judge J_θ with margin; a
wrong-by-construction transform m with oracle-checkable witness w; an exploit as
J_θ(a,x)=PASS ∧ t(a,x)=WRONG; exploit density ρ; the causal slice S_{G=v} and its
prospective-validation lift; a patch P with closure Δ⁺ and autoimmunity cost Δ⁻;
patch-generalization γ; and the convergence classification of k ↦ ρ_heldout(θ_k).
See design document §22 for the full notation — ported here at write-up.)*

## 4. Oracle-witnessed wrong-by-construction attacks (C3)

We start from a verified-correct answer and apply a typed truth-breaking transform
carrying a witness the oracle confirms — so every exploit is free and certain, with
no per-candidate human label. The transform catalog (final-answer corruption,
off-by-one step, keyword inflation, authoritative-wrong, irrelevant citation) is
released as reusable infrastructure. *This inverts the program's evaluator-mutation
discipline: in [Conditionally Approved] we mutated rubric criteria to prove each
gate bites; here we mutate the answer to prove the gates leak.*

## 5. Causal-slice identification (C1)

On procedurally generated items, factors are controlled exactly, so slice cells are
a true factorial and ρ-differences are interaction effects, not correlations. On
richer domains the factorial lives in witnessed universe forks: a single-variable
intervention whose evolution witness certifies nothing else changed. This runs on
the real Gradia universe engine — a fork snapshots the shared parent world, applies
an intervention changing exactly one declared variable, and the engine returns the
before/after world roots and the hash-chained occurrence. (Demonstrated: a fork on
`age_band` changes the world root, `changed_fields = (age_band,)`,
`single_variable_verified = true`.) A named slice is a prediction, validated by
generating fresh held-out items in the predicted slice and showing the predicted
rate materializes above broad-slice and random-slice baselines.

## 6. The repair loop and convergence (C2, C4)

The Patcher synthesizes a minimal repair in one of three modalities (rubric edit,
judge-architecture change, curriculum retrain), guarded by the autoimmunity budget:
a patch is rejected if it rejects too many verified-correct answers. The patched
scorer re-enters the adversary at L3. Over K cycles we classify ρ_heldout as
monotone-decreasing, plateau, or oscillating, and report the patch-generalization
statistic γ (Δρ on held-out families ÷ Δρ on the patched family).

### 6.1 Metrics (the estimands we report)

- **Exploit density** ρ — confirmed exploits per 1000 attempts, per rung, per
  adversary×judge cell (never pooled).
- **Exploit magnitude** — distribution of the judge-pass margin on wrong answers.
- **Exploit half-life** — under L3, patch cycles until a family's density halves.
- **Patch generalization** γ = Δρ_heldout ÷ Δρ_patched ∈ [0,1] (the whack-a-mole
  statistic; the single most important number).
- **Autoimmunity** — per patch, the fraction of verified-correct answers the
  patched scorer now wrongly rejects; the closure-vs-preservation Pareto frontier.
- **Convergence class** — a preregistered decision rule over k ↦ ρ_heldout(θ_k).
- **Transfer rate** — fraction of adversary-A exploits that also fire on judge B.
- **Exploitability spectrum** — density×magnitude over (transform × slice ×
  architecture): a benchmark's immune fingerprint, released as an artifact.

All are recomputable offline by `wind-tunnel-verify` from the committed evidence
index — the program's trust move.

## 7. Verifiable, contamination-proof protocol (C5)

Every episode is a hash-chained receipt (Gradia Guard); budgets are enforced, not
just declared; the run replays offline. The hidden regression suite is a Merkle-
committed append-only log whose chain head is published before any scorer is graded
against it and revealed at publication — so the study could not have been curated
after the fact. Procedurally generated items plus a never-public-until-reveal suite
make the study structurally contamination-resistant.

## 8. Experiments (preregistered; to be run)

Two tiers: **A** — famous public oracle benchmarks (GSM8K, MATH, GPQA-Diamond,
HumanEval, SWE-bench Verified); **B** — Gradia universes for the richest causal
claims. Adversary × judge transfer matrix; convergence curves per judge
architecture (including the self-commitment defense); the autoimmunity Pareto
frontier; the exploitability spectrum per benchmark. Phase 0 reports a first real
exploit-density number and one causal-slice proof under a $300 cap.

## 9. Findings

*(to be written from Phase-1 results; each cell reported even if null, per the
preregistration's claim-ledger discipline.)*

The instrument is complete and self-verifying (`make run`), and Phase 0 — the
first real number — is a single runtime swap: an `LLMJudge` routed through Gradia
Guard grades wrong-by-construction answers on a real benchmark while the oracle
backstops (see the runbook). Figures 1–3 (rung densities, causal-slice
validation, convergence) are generated by `figures.py`; until Phase 0 runs
against real models they illustrate the machinery and are labeled as such.

## 9a. Impact and vision (future work)

If honest-coverage scorer audits become expected — as agent-liability and
audit requirements mature — a benchmark that has been Wind-Tunnel-audited and
patched carries a credential a bare leaderboard cannot: a published
exploitability spectrum, a disclosed-and-fixed exploit set, and a hidden
regression suite that keeps it fixed. The natural end state is a standard that
benchmarks *opt into*, and the wrong-by-construction + oracle-backstop method
generalizes to a family of novel scorer audits beyond this first one. We state
this as a direction, not a claim; the paper's contribution is the measured
instrument and its first results.

## 10. Responsible disclosure

We name the benchmarks we break because vague criticism does not help the field.
Each finding is disclosed to maintainers with a suggested patch and a 45-day
embargo before publication, and we report their responses. We release the repair
loop and hidden-suite protocol, not a turnkey attack script.

## 11. Limitations

Oracle-only scope (open-ended grading is future work); the adversary is not all
real models; compute bounds rung depth; public-benchmark slices are quasi-
experimental (only universe forks license causal claims).

## 12. Running entirely on Gradia (platform validation, C6)

A benchmark-scorer study is a demanding end-to-end workload: it generates
controlled items, forks worlds for causal identification, calls identity-pinned
frontier models under a spend cap, records tamper-evident evidence, and freezes a
preregistration whose digests must verify across runtimes. We run the **entire**
pipeline on the Gradia stack. This is not incidental: it validates that the
program's tooling — built across the prior papers — can execute a complete research
study, which is itself a result. The mapping (generated from the repository's
integration map, not asserted) is:

<!-- generated: gradia_wind_tunnel.gradia_integration.platform_validation_table() -->
| Wind Tunnel component | Gradia tool | Role | Standalone fallback |
|---|---|---|---|
| Generator (causal forks) | gradia_universes world/fork engine (evolution witnesses) | single-variable interventions on a witnessed universe, certifying nothing else changed | procedural factorial items with exactly-controlled factors |
| Evidence spine | Gradia Guard hash-chained receipts + credentialless gateway | every attack, judge call, and patch becomes a tamper-evident, offline-replayable receipt; provider keys never enter the agent process | in-repo run-log chain head with tamper detection |
| Model calls | gradia_universes providers / live_runner (identity-pinned, spend-capped) | identity-pinned frontier model calls with the spend-policy discipline | RealModelJudge stub + deterministic mock judge |
| Canonical evidence | gradia canonical JSON (sorted keys, integer-normalized, NaN-refused) | byte-identical digests across Python and the Guard verifier | vendored identical scheme |
| Preregistration | gradia fail-closed preregistration (self-digested, git-pinned) | the freeze/verify contract the program uses | Wind-Tunnel-schema preregistration, same contract |
| Regression vault | gradia reserved-DOI / hash-commit precedent (Zenodo) | publish the hidden-suite chain head with a timestamp before any result exists | empty-tree chain head in the prereg; Merkle vault in Phase 1 |

Every binding is capability-detected: when a Gradia tool is installed the component
uses it; otherwise a byte-compatible fallback keeps the study runnable. The paper
reports the wired fraction for the exact environment that produced the results, so
the platform claim is measured, not decorative. Concretely, model calls route
through Gradia Guard's credentialless gateway, so **no provider key ever enters the
adversary or judge process** — the study is also a live exercise of Guard's central
guarantee.

## 13. Relation to prior work in this program

This is the third of a program. [Interruptible Universes] contributed the
witnessed, branchable universe we use as a causal instrument; [Gradia Guard]
contributed the tamper-evident evidence runtime that records every experiment; and
[Conditionally Approved] contributed both the proof-bound benchmark methodology and
the multi-judge instability finding (Fleiss' κ = 0.151) that motivates attacking the
scorer directly. We are grateful to build on that foundation.

## Related work

*(full-read and differentiate before submission: self-play reward hacking of
reference-free judges [2607.05904]; Adversarial Reward Auditing [2602.01750];
LLM-as-a-judge security SoK [2603.29403]; prompt-injection on judges [2504.18333];
logic-grounded metamorphic testing [2605.23965]; rubric-eval line [PReMISE
2605.30803, Autorubric 2603.00077, JudgeBench, 2601.08843]; counterfactual fairness
CAFFE [2512.16816]. The open space is the closed attack→repair loop with a
convergence measurement, oracle-witnessed and causally identified.)*
