# Gradia Wind Tunnel — an evaluation immune system

> **One idea:** an evaluation should prove its own validity before any score counts.
> This is the tool that stress-tests the last untrusted component — **the scorekeeper**.

The Wind Tunnel finds answers a famous benchmark's **scorer** grades *"correct"* but
that a machine **oracle** proves *wrong*, identifies the **exact causal slice** being
exploited via single-variable factorial forks, and measures whether **patching the
scorer converges** — or is whack-a-mole forever. Every attack, judge call, and patch
is a tamper-evident, offline-replayable receipt, and the hidden regression suite is
committed by hash **before any result exists**, so the study cannot be rigged after
the fact.

It runs **end-to-end with no human labels**, because it only targets benchmarks whose
ground truth is a machine oracle (exact-answer math, execution-checked code, verified
multiple-choice). The scorer is the attack surface; the oracle is the ground-truth
backstop.

## The program this belongs to

| Pillar | Proves | Repo |
|---|---|---|
| Interruptible Universes | *what happened* (evolution witnesses) | [gradia-universes-work-sample](https://github.com/rudycelekli/gradia-universes-work-sample) |
| Gradia Guard | *nobody tampered with the record* | [gradia-guard](https://github.com/rudycelekli/gradia-guard) |
| **Wind Tunnel** (this) | **the scorekeeper can't be bought** | this repo |

> Public benchmarks can tell you a model is being gamed. Only a branchable, witnessed
> universe can tell you *which counterfactual causes it* — because only there can you
> change one fact and prove you changed nothing else.

## Try it now (offline, no API key)

```bash
make test    # 45 property tests, all green
make demo    # narrated walkthrough of the whole loop
make run     # run the FULL study; writes a self-verifying report to results/
```

`make run` executes the entire pipeline end-to-end — the four threat rungs
(L0 natural incidence → L3 patch-aware), causal-slice localization with
prospective validation, the K-cycle convergence loop, the hash-committed
regression vault, and the analyst extras — and emits one canonical, self-digested
report whose evidence chain head anyone recomputes with `verify-report`. On the
offline scorer it recovers the interaction *keyword-inflation ∧ steps≥3*, shows a
patch relocating instead of generalizing (whack-a-mole, γ<1), the autoimmunity
cost of repair, convergence once the family is exhausted, and a vault reveal that
verifies to its committed empty head.

### Run it on a real benchmark

```bash
pip install datasets          # your environment (network required)
python -c "from gradia_wind_tunnel.benchmarks import build_adapter; \
           a=build_adapter('gsm8k', real=True); print(len(a.items()), 'real GSM8K items')"
```

The GSM8K adapter is fully wired; MATH, GPQA, and HumanEval ship real, unit-tested
oracles (`real_benchmarks.py`) and Phase-1 items. Swap the deterministic judge for
`GuardRoutedProvider` (a Guard-gated model, key never in the process) to collect
real exploit-density numbers. Causal-strength slices come from
`universe_forks.py` when `gradia_universes` is installed.

## Freeze the science first (the foundation)

Nothing is run until the preregistration is frozen and its digest published with a
timestamp. That is what makes the convergence / causal / autoimmunity findings
credible and establishes precedence.

```bash
make prereg                 # writes preregistrations/<run_id>.json (self-digested, git-pinned, $300 cap)
make prereg-verify FILE=preregistrations/<run_id>.json
```

The preregistration mirrors the program's fail-closed format: canonical JSON,
git-pinned, spend-capped, self-digested, and carrying an explicit `interpretation`
that scopes exactly what the study may and may not claim.

## Target benchmarks (frontier, famous, machine-checkable)

| Benchmark | Kind | Oracle | Why it's here |
|---|---|---|---|
| GSM8K | math | numeric equality | classic anchor; directly comparable to the self-play reward-hacking result |
| MATH | math | numeric equality | competition math; more frontier than GSM8K |
| GPQA-Diamond | mcq | key match | graduate-level, "Google-proof"; current frontier reasoning |
| HumanEval | code | unit tests | classic code anchor |
| SWE-bench Verified | code | unit tests | frontier agentic coding — with a *documented test-gaming precedent* |

Phase 0 wires the procedural-math adapter concretely; the frontier adapters are
declared behind one interface (`benchmarks.py`) and pinned at freeze.

## How it works (seven services, every arrow a Guard receipt)

```
Generator → Adversary → Oracle → Judge Bank → Analyst → Patcher → Regression Vault → (L3 back to Adversary)
```

- **Generator** — items with exactly-controlled causal factors + a machine oracle.
- **Adversary** — a typed catalog of *wrong-by-construction* transforms across four
  threat rungs (L0 natural incidence → L3 patch-aware re-attack), budget-metered.
- **Oracle** — deterministic ground truth; confirms every exploit with no human.
- **Judge Bank** — single / ensemble / self-commitment / rubric-decomposed, hot-swappable.
- **Analyst** — exploit density, magnitude, half-life, causal-slice screen,
  autoimmunity, exploitability spectrum, exploit-DNA, disagreement detector.
- **Patcher** — rubric-edit / judge-architecture / curriculum-retrain, guarded by autoimmunity.
- **Regression Vault** — hash-committed hidden suite; revealed at publication.

Design and full method: [`docs/`](docs/) and the paper draft in [`paper/`](paper/).

## Status

Public research beta. The **entire methodology is implemented and green (45 tests)**:
all four services plus the causal localizer, the three-modality patcher, the
convergence loop, the hash-committed vault, and the analyst extras, driven by a
one-command orchestrator that emits a self-verifying report. Real oracles for
GSM8K/MATH/GPQA/HumanEval are unit-tested; GSM8K loads real data end-to-end. The
remaining Phase-0 step is the one runtime swap: point the judge at a Guard-routed
frontier model and run under the frozen preregistration. **No empirical claim about
any real model or benchmark is made** until that run happens; the offline numbers
demonstrate the machinery, not a finding.

## License

Apache-2.0. The Gradia name and marks are not licensed for derivative branding.
