# Phase-0 runbook — from scaffold to your first real number

The instrument is built and green. This is the exact path to a real,
publishable exploit-density number under a frozen preregistration. Nothing here
is run until the prereg is frozen and its digest published.

## Step 1 — Freeze the preregistration (locks the science; earns the DOI)

```bash
# pin the benchmark snapshots first (edit contracts.TARGET_BENCHMARKS: replace
# the {{...}}_SNAPSHOT placeholders with exact dataset commit hashes / releases),
# then freeze on a clean commit:
git commit -am "pin Phase-0 benchmarks + config"
make prereg                       # writes preregistrations/<run_id>.json
make prereg-verify FILE=preregistrations/<run_id>.json   # -> ok: true, git_dirty: false
```

Record the printed `preregistration_sha256` and the `hidden_regression_vault.committed_chain_head_sha256`.

## Step 2 — Publish the freeze to Zenodo (precedence + the resume DOI)

Create a Zenodo record (see `docs/ZENODO-PREREG-DESCRIPTION.md` for paste-ready
text). Upload the frozen `preregistrations/<run_id>.json`. Publish. This
timestamps the design and the empty-vault head **before any result exists** —
that is what makes the convergence/causal/autoimmunity findings un-riggable, and
it gives you the citable DOI for the resume line (replaces `{{ZENODO_DOI}}`).

## Step 3 — Rehearse the run offline (no key, no spend)

```bash
make test                                   # 49 green
python -m gradia_wind_tunnel.cli phase0 --benchmark gsm8k   # offline rehearsal
```

You get the exact report shape a live run produces, with the simulated grader.

## Step 4 — Go live on ONE benchmark (the one runtime swap)

Bring up the Guard gateway so the provider key never enters the run process
(`gradia-guard` credentialless runtime), then:

```bash
export GRADIA_GUARD_LOCAL_CAPABILITY=<capability-from-guard>
python -m gradia_wind_tunnel.cli phase0 \
  --benchmark gsm8k --real --live \
  --model claude-opus-5 \
  --gateway http://127.0.0.1:8787 \
  --prereg-sha256 <preregistration_sha256 from step 1> \
  --max-cost-usd 300 \
  --out results/phase0-gsm8k-live.json
```

`AnthropicGuardGrader.grade` is implemented (a dependency-free Anthropic Messages
POST to `{gateway}/v1/messages`, authenticated with the Guard capability, cost
tracked from `usage`). You only need the Guard gateway up and the capability
exported; the loop, oracle, causal localizer, and verifier are unchanged. The
spend cap fail-closes and `spent_usd` is reported. To sanity-check the wiring
without spending, inject a fake transport (see the test
`live grader posts to the gateway /v1/messages`).

## Step 5 — Read the result honestly

The report is self-digested (`report_sha256`) and carries an `interpretation`
that scopes the claim. Two headline numbers:

- **L0 natural incidence** — does the real grader already pass oracle-wrong
  answers with no adversary? (the "reward hacking happens in the wild" number.)
- **L1 metamorphic density** — how often a wrong-by-construction answer passes.

Plus the causal slice and its prospective lift. Report every number, including
nulls. If L0 is ~0 and L1 is high, you have a clean, defensible first result: the
grader is robust to accidents but gameable on purpose — exactly the paper's thesis.

## Step 6 — Then scale across all five benchmarks

Every benchmark is wired behind one shape-agnostic interface (`benchmark_suite.py`):
GSM8K and MATH (numeric / boxed), GPQA-Diamond (A-D), HumanEval (unit-test oracle),
and SWE-bench Verified (scaffold — needs the container harness). Run any of them
and write a research-grade evidence bundle:

```bash
# offline rehearsal (no key) — any benchmark:
python -m gradia_wind_tunnel.cli suite --benchmark gpqa_diamond

# real data, live grader through Guard:
python -m gradia_wind_tunnel.cli suite --benchmark math --real --live \
  --model claude-opus-5 --gateway http://127.0.0.1:8787 \
  --prereg-sha256 <frozen> --out results/math-live
```

Each run writes `frames.ndjson` (one canonical line per attack — the granular,
analytics-ready record, with per-attempt cost) and a self-digested `manifest.json`
carrying the paper's estimands (density by rung/transform/benchmark, exploit
magnitude, total cost). `capture.verify_bundle` recomputes the chain head AND
every aggregate from the frames, so **every number in the paper is recomputable
and any edit to a frame is detected** — the writeup asserts nothing, it derives
everything. Then run the adversary×judge matrix and the K-cycle convergence loop
(`make run` structure), commit exploits to the vault, and generate figures
(`python -m gradia_wind_tunnel.figures`). That is the full paper.

The evidence design is deliberate: the frames are the results appendix and the
analytics feed at once. Every observation the paper reports comes with its own
proof, which is the whole program's discipline applied to this study.

## Cost discipline

Everything is metered and capped ($300 default). Start with GSM8K L0+L1 at small
n — a few hundred grader calls, tens of dollars — get the first number, then
decide where to spend the rest. You never spend a dollar the prereg didn't authorize.
