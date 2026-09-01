# Gradia Wind Tunnel — an evaluation immune system

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22233638.svg)](https://doi.org/10.5281/zenodo.22233638)
[![Verify](https://github.com/rudycelekli/gradia-wind-tunnel/actions/workflows/verify.yml/badge.svg)](https://github.com/rudycelekli/gradia-wind-tunnel/actions/workflows/verify.yml)

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
make test    # 165 property/control tests, all green
make demo    # narrated walkthrough of the whole loop
make run     # run the FULL study; writes a self-verifying report to results/
make verify-release  # replay every committed Proof Pack; one failure fails the release
gradia-wind-tunnel verify-bundle results/offline-math  # no account or API key
gradia-wind-tunnel verify-bundle results/swe-merged    # recompute the LIVE SWE-bench study
gradia-wind-tunnel index                               # recompute the Scorer Gameability Index (+ CIs)
```

`make run` executes the entire pipeline end-to-end — the four threat rungs
(L0 natural incidence → L3 patch-aware), causal-slice localization with
prospective validation, the K-cycle convergence loop, the hash-committed
regression vault, and the analyst extras — and emits one canonical, self-digested
report whose evidence chain head anyone recomputes with `verify-report`. The repository ships the committed evidence bundles for every headline table, so an
outsider recomputes the published numbers from raw receipts — no account, no API key. Each
frames/manifest Proof Pack can also be checked offline with `verify-bundle`,
which independently recomputes its chain, attempt/exploit/cost totals, every
reported slice, magnitude histogram and manifest digest. On the
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

GSM8K, MATH, GPQA-Diamond, HumanEval and the machine-checkable HLE subset ship
real adapters/oracles. The live SWE harness runs verified repository containers,
records full-test and weak/public-test outcomes, and excludes dirty controls. Real
provider judging is implemented in `llm_judge.py` and `realjudge.py`; the older
`GuardRoutedProvider` class remains an integration seam, not the live-results path.
Causal-strength slices come from `universe_forks.py` when `gradia_universes` is
installed.

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
| HLE (checkable subset) | knowledge | key / string match | Humanity's Last Exam — the frontier knowledge exam; the highest-leaking scorer in the slate |
| SWE-bench Verified | code | unit tests | frontier agentic coding — with a *documented test-gaming precedent* |

All five machine-checkable adapters are wired and run under the frozen
preregistration, each declared behind one interface (`benchmarks.py`) and pinned at freeze.

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

## Paper and citable record

- **Canonical paper:** [Zenodo record and PDF](https://doi.org/10.5281/zenodo.22233638)
- **Branded source:** [`paper/WIND-TUNNEL-PAPER-FULL.md`](paper/WIND-TUNNEL-PAPER-FULL.md)
- **Double-blind source:** [`paper/WIND-TUNNEL-PAPER-TMLR-anon.md`](paper/WIND-TUNNEL-PAPER-TMLR-anon.md)
- **Citation metadata:** [`CITATION.cff`](CITATION.cff)
- **Exact release gates:** [`docs/RELEASE-EVIDENCE.md`](docs/RELEASE-EVIDENCE.md)
- **Method and release boundary:** [`docs/`](docs/)

The DOI record is the canonical rendered publication. Generated PDFs are not tracked
twice in Git; `python paper/build_pdfs.py` rebuilds both editions from the public sources.

## Status

Published study — Zenodo DOI [10.5281/zenodo.22233638](https://doi.org/10.5281/zenodo.22233638); manuscript under submission at TMLR. The **scientific core is green (165 property/control tests)**, and the release verifier replays every committed Proof Pack rather than a selected example:
all four services plus the causal localizer, the three-modality patcher, the
convergence loop, the hash-committed vault, and the analyst extras, driven by a
one-command orchestrator that emits a self-verifying report. Real model-judge
attacks have run across public benchmark families. The live SWE-bench Verified edition covers 100 control-clean instances and 1,800
grader-level attempts, with 89 witnessed exploits (49.4/1,000); one control-dirty
instance is excluded rather than counted.
These are evaluation-metrology findings, not evidence that a training intervention
improves a frontier model. `program-readiness` emits the exact live/offline/wired/
designed boundary and refuses training-dispatch claims.

## License

Apache-2.0. The Gradia name and marks are not licensed for derivative branding.
