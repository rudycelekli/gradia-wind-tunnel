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
| **M3** | RealModelJudge via governed provider path; L0+L1 on public benchmarks | §8 first result; §9 first number | H-natural-incidence | ✅ live |
| **M4** | L2 bounded search + naturalness screen; causal-fork engine + prospective validation | §5 causal result (Fig 2) | H5 | ✅ live/offline; several slices inconclusive |
| **M5** | patcher (3 modalities) + L3 + convergence loop + autoimmunity | §6 convergence (Fig 3, Fig 4) | H1, H2, H3, H4 | ✅ offline |
| **M6** | regression vault (hash-chain) + spectrum + exploit-DNA + disagreement detector + universe seam | §7 protocol; §5 universe-tier causal | H2 (cross-benchmark) | ✅ mixed live/offline |
| **M7** | coverage theorem (scoped) | theory appendix | — | Stretch |

The whole loop runs offline and self-verifies today (`make run`), and public-
benchmark/provider evidence now exists. The remaining research jump is not another
provider swap: it is an admitted model-authored adversary and an actual authorized
optimizer-backed repair/training arm. Existing deterministic patches establish
evaluator self-hardening and relocation behavior; they do not establish learned
model improvement.

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

For a new edition, freeze the exact adapter, scorer, oracle, transform catalog,
provider/runtime, held-out vault and claim boundary first. Real model calls go
through the live judge path; the loop, metrics, slice screen and verifier remain
the same from rehearsal to paid execution.
