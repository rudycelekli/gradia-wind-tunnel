# Process — how the code and the paper advance together

One rule: **nothing is run until the preregistration is frozen and its digest is
published with a timestamp.** After that, code milestones and paper sections
advance in lockstep, each milestone unlocking the section it feeds.

## The lockstep crosswalk

| Milestone (code) | Delivers | Unlocks (paper) | Hypothesis | Status |
|---|---|---|---|---|
| **M0** | procedural generator + exact oracle + factor tags | §5 causal setup | — | ✅ |
| **M1** | transform catalog + oracle-witness self-tests | §4 attacks | — | ✅ |
| **M2** | judge bank (mock) + attack loop + analyst core + verifier + slice screen | §4–§6 method | H5 (offline) | ✅ |
| **M3** | RealModelJudge via Guard; L0+L1 on one frontier benchmark under the frozen prereg | §8 first result; §9 first number | H-natural-incidence | **the one pending swap** |
| **M4** | L2 adaptive search + naturalness screen; causal-fork engine + prospective validation | §5 causal result (Fig 2) | H5 | ✅ offline |
| **M5** | patcher (3 modalities) + L3 + convergence loop + autoimmunity | §6 convergence (Fig 3, Fig 4) | H1, H2, H3, H4 | ✅ offline |
| **M6** | regression vault (hash-chain) + spectrum + exploit-DNA + disagreement detector + universe seam | §7 protocol; §5 universe-tier causal | H2 (cross-benchmark) | ✅ offline |
| **M7** | coverage theorem (scoped) | theory appendix | — | Stretch |

The whole loop runs offline and self-verifies today (`make run`). M3 is the single
runtime swap that turns the demonstration into empirical results: wire
`GuardRoutedProvider` (providers.py) to a frontier model and point `benchmarks`
at a real snapshot (`build_adapter('gsm8k', real=True)`). Everything downstream —
causal localizer, patcher, convergence, vault, analyst, verifier — is unchanged.

## The freeze checklist (before any Phase-1 number)

- [ ] Schemas and versions in `contracts.py` frozen; hashed into the prereg.
- [ ] Transform catalog frozen; `catalog_sha256` recorded.
- [ ] Oracle specs per benchmark frozen; benchmark snapshots pinned (replace the
      `{{...}}` placeholders in `contracts.TARGET_BENCHMARKS`).
- [ ] Judge model ids + versions pinned in the prereg.
- [ ] Spend cap set (currently $300) and provider account limit attested.
- [ ] Hypotheses H1–H5 directions committed (already in `contracts.HYPOTHESES`).
- [ ] Empty-vault chain head published (Zenodo DOI / git tag) with a timestamp.
- [ ] `gradia-wind-tunnel prereg-verify` returns `ok: true` on the frozen file.

## Running on Gradia

`gradia_wind_tunnel.gradia_integration.gradia_stack_status()` reports which Gradia
tools are wired in the current environment; the paper's platform-validation table
is generated from it. Model calls route through Gradia Guard's credentialless
gateway, so no provider key enters the adversary or judge process.

## Two-command daily loop

```bash
make test    # keep the contract green
make demo    # sanity-check the loop offline before spending a dollar
```

Then, once frozen, wire `RealModelJudge` (judges.py) to your provider via Guard and
point `benchmarks.py` at the first pinned snapshot. The loop, metrics, slice screen,
and verifier are unchanged from the offline pilot to the real run — that is the
point of the design.
