# Zenodo preregistration record — paste-ready

Use this when publishing the frozen preregistration to Zenodo (matches the
program's CA / Interruptible Universes record style). Upload the frozen
`preregistrations/<run_id>.json`. CC BY 4.0 for the text; Apache-2.0 for any code.

---

**Title**

> Preregistration: The Reward-Hacking Wind Tunnel — an evaluation immune system for benchmark scorers (Phase 0)

**Authors**

> Rudy M. Celekli (Gradia Research)

**Description** (paste)

> This record preregisters the design and analysis plan for the Reward-Hacking
> Wind Tunnel before any results exist. The study measures whether a public
> benchmark's SCORING PIPELINE — its answer extractor, LLM judge, rubric grader,
> or unit-test verifier — can be gamed by answers that a machine oracle proves
> wrong, identifies the exact causal slice being exploited via single-variable
> interventions, and measures whether iterated repair of the scorer converges,
> plateaus, or merely relocates the flaw.
>
> The preregistration is a canonical-JSON document that is git-pinned,
> spend-capped, and self-digested (`preregistration_sha256`), carrying an
> explicit `interpretation` that scopes exactly what the study may and may not
> claim. It commits the transform catalog, the per-benchmark oracle definitions,
> the four threat rungs (L0 natural incidence through L3 patch-aware re-attack),
> the judge architectures (single, ensemble, self-commitment, rubric-decomposed),
> five directional hypotheses (H1 convergence shape, H2 patch generalization,
> H3 autoimmunity trade-off, H4 structural-defense dominance, H5 causal-slice
> validity), the primary outcomes, prospective stop rules and spend caps, and the
> analysis-blind gates.
>
> It also commits the chain head of an EMPTY hidden regression suite. Every
> exploit discovered later enters an append-only, hash-chained vault; because the
> empty head is timestamped here before any result exists, the revealed suite can
> be verified at publication to hash back to this commitment, so the results
> cannot have been curated after the fact.
>
> Target benchmarks are famous, frontier, and machine-checkable: GSM8K, MATH,
> GPQA-Diamond, HumanEval, and SWE-bench Verified. Benchmarks are named because
> vague criticism does not help the field; each finding will be disclosed to the
> benchmark's maintainers with a suggested patch before public release, and their
> responses will be reported.
>
> This is the third preregistration in a program on verifiable evaluation, after
> Interruptible Universes (verifiable world-state change) and Conditionally
> Approved (proof-bound benchmarking), and it runs on the Gradia stack with Gradia
> Guard evidence. No empirical result about any model or benchmark is claimed by
> this record; it fixes the protocol so the eventual results are credible.

**Keywords**

> LLM evaluation; reward hacking; LLM-as-a-judge; benchmark integrity;
> preregistration; causal inference; verifiable evidence; AI agents

**Related identifiers**

> - isDerivedFrom: doi.org/10.5281/zenodo.22087020 (Interruptible Universes / Conditionally Approved, concept DOI)
> - isSupplementedBy: github.com/rudycelekli/gradia-wind-tunnel
> - references: Gradia Guard — github.com/rudycelekli/gradia-guard

---

After publishing: copy the DOI into (a) the resume Wind Tunnel entry (replaces
`{{ZENODO_DOI}}`) and (b) `phase0 --prereg-sha256` / the report's
`preregistration_sha256` field for every run, so each result points back to the
frozen design.
