# The Reward-Hacking Wind Tunnel — IP Register & Attack Plan
### Companion to `WIND-TUNNEL-DESIGN.md` · Draft v0.1 · Rudy M. Celekli, Gradia Research

This is the **build-it** document. The design doc says *what and why*; this says *what is ours to claim* (Part I) and *exactly how to construct it* (Part II). Written so you can implement straight from it and write the paper as the artifacts land.

> Reading order: skim Part I to know what you're protecting and publishing; implement from Part II milestone by milestone. The runnable `pilot/` already realizes M0–M2.

---

# PART I — THE IP REGISTER

Research IP is not patents; it's **defensible, citable, first-to-publish claims** plus **reusable released infrastructure** that others must cite. Treat each item as a claim with a prior-art delta and a publish-vs-protect decision. The stronger and clearer this register, the more obviously the whole program is *yours*.

## I.0 The umbrella claim (the program thesis)

> **A three-layer discipline for trustworthy AI evaluation:** *what happened* is verified by evolution witnesses (Interruptible Universes), *the record* is made tamper-evident by hash-chained coverage-honest receipts (Gradia Guard), and *the scorekeeper* is stress-tested to its repair limit by an automated adversarial immune system (this work). The novelty of the third layer is that it is the first to **close and measure** the attack→repair loop over a deployed evaluator, and the first to make the exploited failure **causally identified** and the whole study **cryptographically un-rigged**.

Everything below is a sub-claim of that umbrella. State the umbrella in every abstract, talk, and the resume.

## I.1 Claim ledger (numbered, with prior-art delta + disposition)

| # | Claim (what is novel and ours) | Closest prior art | The delta (why ours is new) | Disposition |
|---|---|---|---|---|
| **IP-1** | **Oracle-witnessed wrong-by-construction attack generation** — truth-breaking mutations carrying machine-checkable witnesses that a ground-truth oracle confirms, giving zero-human-label exploit confirmation. | LGMT metamorphic testing (2605.23965); self-play RH (2607.05904) | Prior metamorphic work perturbs *inputs* to test reasoning; self-play searches answers but needs a truth signal. We mutate *verified-correct answers* with a witness the *oracle* validates → every exploit is free and certain. | **Publish + release** the typed transform catalog (Apache-2.0). Flagship enabling method. |
| **IP-2** | **Witnessed-universe causal slice identification** — naming the exact factor interaction behind an exploit via single-variable forks in a world whose evolution witness certifies nothing else changed. | CAFFE counterfactual fairness (2512.16816); slice-discovery literature | Prior counterfactuals perturb text (confounded) or find broad slices. We make *true factorial* interventions with a cryptographic clean-counterfactual guarantee, validated prospectively. **Requires the Universes substrate — only we can do it.** | **Publish.** The moat. Co-headline. |
| **IP-3** | **Evaluator repair-convergence measurement** — the first measurement of whether iterative attack→patch of a deployed scorer converges / plateaus / oscillates, with patch-generalization γ. | Adversarial Reward Auditing (2602.01750); adversarial-robustness literature | ARA trains one defense; robustness work studies model classifiers. Nobody has measured *convergence of the evaluation stack under repair*. | **Publish.** The surprising-either-way result. Co-headline. |
| **IP-4** | **The autoimmunity metric** — quantifying the correct-answers-rejected cost of each patch; the exploit-closure vs. correct-preservation Pareto frontier. | rubric-robustness papers (2601.08843) | The immune-system metaphor is common; the *measurement* of collateral damage per patch is not reported anywhere. | **Publish.** Cheap, novel, memorable. |
| **IP-5** | **Hash-committed hidden regression vault** — a Merkle-committed exploit suite published-by-digest before any result exists and revealed at publication, making post-hoc curation cryptographically detectable. | pre-registration norms; benchmark-contamination literature | Preregistration commits *hypotheses*; we commit the *evolving test set itself* by hash, so the integrity guarantee is mechanical, not trust-based. Generalizes your reserved-DOI trick. | **Publish + release** the vault protocol + verifier. |
| **IP-6** | **The Exploitability Spectrum** — a benchmark's immune fingerprint: density×magnitude over (transform × slice × judge-architecture), tracked across benchmark versions. | JudgeBench (judge benchmarks) | Judge benchmarks score judges on accuracy; nobody publishes a *vulnerability profile object* for a named benchmark. | **Publish + release** the spectrum format. Adoptable standard. |
| **IP-7** | **Exploit DNA & the universality question** — typed exploit records clustered across benchmarks to test whether a small basis of judge blind spots ("periodic table of reward hacks") explains most exploits. | none direct | Genuinely open scientific question; no prior cross-benchmark exploit taxonomy with a universality test. | **Publish.** High-risk/high-reward. |
| **IP-8** | **Disagreement-geometry exploit detector** — turning multi-judge disagreement (your κ=0.151 instrument) into an online, oracle-free early-warning signal for likely exploits. | CA four-judge result (yours); ensemble-judge work | Extends *your own* observational finding into a deployable detector; no prior work predicts exploitability from disagreement manifold position. | **Publish.** Builds on and credits CA. |
| **IP-9** | **Adversarial curriculum repair** — converting a named causal slice into a targeted data-generation order that retrains the judge/rubric and provably (via autoimmunity guard) closes the slice without collapsing correctness. | data-augmentation / active-learning | Closes environments→evaluation→**training-data** in one automated loop with a correctness guardrail; the charter-closing contribution. | **Publish.** The Universes-team magnet. |
| **IP-10** | **Coverage theorem for evaluators** (stretch) — a provable characterization, under the oracle model, of the class of wrong answers that cannot pass without triggering ≥1 committed detector. | Guard coverage-honesty (yours); PAC/robustness theory | Lifts Guard's coverage-honesty from runtime evidence to evaluation theory; gives the paper a proof spine. | **Publish if it closes**; scope to one family otherwise. Flag as stretch. |
| **IP-11** | **The `wind-tunnel` platform** — the integrated, Guard-instrumented, reproducible harness (Generator→…→Vault) as released open infrastructure. | eval frameworks (lm-eval-harness, Inspect) | Existing harnesses *run* benchmarks; none *attacks and repairs* them with verifiable receipts. | **Release** (Apache-2.0). The thing people install and cite. |

## I.2 Disposition summary
- **Release open (Apache-2.0), so others must cite you:** transform catalog (IP-1), vault protocol + verifier (IP-5), spectrum format (IP-6), the platform (IP-11).
- **Publish as findings:** IP-2, IP-3, IP-4, IP-7, IP-8, IP-9, and IP-10 if it closes.
- **Protect only in the sense of priority:** freeze the preregistration with a public timestamp (Zenodo DOI) *before* running — that is how you establish precedence on IP-2/IP-3/IP-4 without secrecy. Open science *is* the protection here; the DOI + git history is the priority claim.

## I.3 Freedom-to-operate (what you must not collide with)
Before submission, full-read and explicitly distinguish: 2607.05904 (self-play RH — your motivation, cite prominently), 2602.01750 (ARA — different target), 2603.29403 (SoK — cite as map), 2605.23965 (LGMT — metamorphic delta), 2512.16816 (CAFFE — counterfactual delta), 2605.30803 / 2603.00077 / 2601.08843 / JudgeBench (rubric/judge subfield — you're not proposing a rubric format). If any performs a *closed attack→repair loop with convergence measurement on a deployed scorer*, escalate and re-sharpen — but current evidence says the space is open.

## I.4 The research-program claim ladder (put on the resume + in talks)
1. **Interruptible Universes** — verifiable world-state change (evolution witnesses). *Published, Zenodo, ICLR 2027 under review.*
2. **Gradia Guard** — tamper-evident, coverage-honest runtime evidence. *Open source.*
3. **Conditionally Approved** — proof-bound benchmark + multi-judge instability finding. *Published, Zenodo.*
4. **The Value Engine Benchmark** — reproducible public benchmark. *Published.*
5. **→ The Wind Tunnel** — automated adversarial repair of the scorekeeper. *This work; preregistered.*

Each rung cites the ones below it. The ladder is the asset.

---

# PART II — THE ATTACK PLAN (implement from this)

## II.0 Architecture: seven services, typed contracts, Guard-instrumented

```
        ┌──────────────────────────────────────────────────────────────┐
        │  wind-tunnel platform  (every arrow emits a Guard receipt)    │
        └──────────────────────────────────────────────────────────────┘

  ┌───────────┐   items+φ+oracle   ┌───────────┐  wrong-by-construction ┌────────┐
  │ GENERATOR │ ─────────────────▶ │ ADVERSARY │ ─────────────────────▶ │ ORACLE │
  │ (items,   │                    │ (T × rung │      answers           │ (t:    │
  │  factors, │◀── slice orders ── │  policy,  │◀── witness valid? ──── │ det.   │
  │  oracle)  │   (curriculum)     │  budget)  │                        │ check) │
  └───────────┘                    └─────┬─────┘                        └────────┘
        ▲                                │ answers (witnessed wrong)
        │                                ▼
        │                          ┌───────────┐   verdict+margin   ┌───────────┐
        │                          │ JUDGE BANK │ ─────────────────▶│  ANALYST  │
        │                          │ θ: single/ │                   │ density,  │
        │                          │ ensemble/  │                   │ magnitude,│
        │                          │ self-commit│                   │ slice,    │
        │                          │ /rubric-dec│                   │ spectrum, │
        │                          └───────────┘                   │ DNA,      │
        │                                                          │ disagree, │
        │                                                          │ autoimmun.│
        │                                                          └─────┬─────┘
        │                                                                │ exploit families
        │                     ┌───────────┐   θ_{k+1}   ┌───────────┐    │
        └──── curriculum ─────│  PATCHER  │◀────────────│  ANALYST  │◀───┘
                              │ rubric /  │             └───────────┘
                              │ judge /   │                   │ every confirmed exploit
                              │ curriculum│                   ▼
                              └─────┬─────┘             ┌─────────────┐
                                    │ patched scorer    │ REGRESSION  │
                                    └──────────────────▶│   VAULT     │  (Merkle-committed,
                                       L3 re-attack     │ hidden→reveal│   hidden suite)
                                                        └─────────────┘
```

**Design rules (inherit from Guard/CA):** every service is pure-ish and independently testable; every artifact is content-addressed (sha256); every run replays offline from checked-in evidence; deny/fail-closed on any schema mismatch; nothing pooled across rungs or cells in headline stats.

## II.1 Data model (freeze these schemas; hash them into the prereg)

```jsonc
// Item — a task instance with EXACTLY known causal factors
Item {
  item_id: str, benchmark_id: str, question: str,
  gold: <oracle-typed>,                 // int | test-suite-id | key
  factors: { <factor_name>: <level> },  // the controlled φ(x)
  correct_answer: str,                  // a verified a*(x)
  generation_seed: int                  // reproduce this exact item
}

// Transform application → Attack (wrong-by-construction)
Attack {
  attack_id: str, item_id: str, transform_id: str,
  answer_text: str,
  witness: { kind: str, statement: str, oracle_confirmed: bool },
  favored_signal: str|null,             // what surface feature it injected
  rung: "L0"|"L1"|"L2"|"L3",
  parent_attack_id: str|null            // L3: which patch it re-attacks
}

// Judge verdict
Verdict { judge_theta: str, passed: bool, margin: float, rationale: str,
          committed_answer: <opt>, cost_usd: float, latency_ms: int }

// Episode — one full attempt, the atomic evidence unit (Guard frame)
Episode {
  episode_id, attack: Attack, oracle_wrong: bool, verdict: Verdict,
  is_exploit: bool,                     // verdict.passed AND oracle_wrong
  exploit_dna: ExploitDNA|null,
  observed_at, prev_frame_sha256, frame_sha256
}

// ExploitDNA — typed record for cross-benchmark clustering (IP-7)
ExploitDNA { transform_id, slice_signature: {factor:level}, judge_theta,
             margin_bin, favored_signal, benchmark_id }

// Patch — one repair step (IP-9)
Patch {
  patch_id, from_theta, to_theta,
  modality: "rubric_edit"|"judge_arch"|"curriculum_retrain",
  targets_family: {transform_id, slice_signature},
  spec: <modality-specific>,
  closure_delta: float, autoimmunity_delta: float, generalization_gamma: float
}

// VaultEntry — hidden regression suite item (IP-5)
VaultEntry { entry_id, attack: Attack, discovered_cycle: int, sha256 }
VaultManifest { chain_head_sha256, committed_at, n_entries, reveal_status }
```

## II.2 Component build specs

### II.2.1 GENERATOR
- **Procedural mode (pilot, done):** parametric item families with a factor grid; every factor a first-class column; `generation_seed` reproduces any item. Extend the pilot's math family with: code family (recursion/iteration × edge-density × input-size) and MC family (distractor-similarity × topic × position).
- **Real-benchmark adapter mode (Phase 1):** load a named benchmark snapshot (pinned commit/hash), attach a `factors` tagger (heuristic or model-assisted metadata → *observational*, labeled hypothesis-generating) and the benchmark's native oracle. Keep procedural items for causal claims; real items for external validity.
- **Oracle spec** per benchmark: a deterministic checker with a frozen `oracle_specs_sha256`. Math=numeric normalize+equality; code=sandboxed unit tests (resource-limited, no network — reuse Guard's container-enforcement posture); MC=key match.
- **Acceptance:** every generated `correct_answer` passes its oracle; factor columns exactly recoverable; re-run from seed is byte-identical.

### II.2.2 ADVERSARY
- **Transform catalog** (IP-1): typed registry `{transform_id → (fn, witness_fn, injected_signal)}`. Start with the pilot's five; expand per domain (code: `dead-code-inflation`, `assert-weakening`; MC: `confident-distractor`, `format-mimicry`). Each transform MUST produce an oracle-WRONG answer or it's rejected at registration (a self-test).
- **Rung policies:**
  - L0: no transform — sample policy-model outputs, oracle-check, count naturally-wrong-but-passed.
  - L1: apply every transform to every `a*`; pure generate-and-test.
  - L2: budgeted search — the adversary model proposes edits toward `PASS ∧ WRONG`; cap queries/dollars per exploit; **naturalness screen on**.
  - L3: same as L2 but the adversary is given the patch diff and re-searches; parent-links to the patched family.
- **Naturalness screen (§6.3):** on-policy constraint + an automated classifier/regex bank that rejects injection artifacts and judge-directed meta-text; log the screen verdict on every L2/L3 attempt.
- **Budget meter:** hard per-rung query/dollar caps enforced (fail-closed), recorded as a Guard budget receipt.
- **Acceptance:** 100% of emitted attacks are oracle-witnessed wrong; L2/L3 respect budget exactly; naturalness screen has a measured FP/FN on a labeled dev set.

### II.2.3 ORACLE
- Deterministic, pure, sandboxed for code. No LLM. Returns `{CORRECT,WRONG}` + a normalized-answer trace for auditability.
- **Acceptance:** idempotent; sandbox escape-tested (reuse Guard's probe battery idea — an oracle that shells out is a bug).

### II.2.4 JUDGE BANK
- Four hot-swappable architectures behind one `Judge.score(answer, question) → Verdict`:
  1. **single** — one model, rubric-prompted.
  2. **naive-ensemble** — k models, majority/strict.
  3. **self-commitment** — judge solves blind first, accepts iff its own answer matches (the 2607.05904 defense; pilot has a stand-in).
  4. **rubric-decomposed** — score each rubric criterion separately, aggregate.
- **RealModelJudge adapter:** provider SDK call, parse to `Verdict`, **routed through Gradia Guard** so every judge call is a hash-chained receipt with cost. Pin model ids+versions in the prereg.
- **Acceptance:** identical `Verdict` schema across architectures; deterministic under fixed seed/temperature=0 where possible; every call produces a Guard frame.

### II.2.5 ANALYST
Computes, per the formal statement (§22 of design), and logs everything Fig 1–5 / Table 1–3 need:
- exploit density ρ (per rung/family/cell), magnitude distribution, half-life;
- **slice screen** (IP-2): factorial ρ across factor cells → minimal named conjunction; prospective-validation harness (generate held-out slice cohort, compare to broad+random baselines);
- **exploitability spectrum** (IP-6): the (transform×slice×θ) tensor per benchmark;
- **exploit DNA clustering** (IP-7): embed+cluster DNA records across benchmarks; report cluster count + coverage (the universality test);
- **disagreement detector** (IP-8): fit exploit probability vs. multi-judge disagreement features; report AUC as an oracle-free predictor;
- **autoimmunity** (IP-4): FRR on verified-correct sets before/after each patch.
- **Acceptance:** every headline number recomputable by the `wind-tunnel-verify` CLI from the evidence log (pilot has the seed of this); chain head stable.

### II.2.6 PATCHER (three modalities — IP-9)
Given an exploit family `(transform, slice)`:
- **rubric_edit:** synthesize a minimal rubric criterion that rejects the family (e.g., "penalize unsupported hedging phrasing"); apply; measure closure + autoimmunity.
- **judge_arch:** switch/augment architecture (e.g., add self-commitment); measure.
- **curriculum_retrain:** generate a fresh cohort in the slice (correct + wrong-by-construction), fine-tune/prompt-update the judge on it, measure closure **and** autoimmunity guardrail — reject the patch if Δ⁻ exceeds a prereg threshold.
- Emit a `Patch` record; the patched `to_theta` re-enters the Adversary at L3.
- **Acceptance:** every patch reports (Δ⁺, Δ⁻, γ); no patch is accepted that violates the autoimmunity budget; patched scorer is content-addressed.

### II.2.7 REGRESSION VAULT (IP-5)
- Every confirmed exploit → `VaultEntry`; the suite is a growing Merkle tree.
- **Commit:** publish `chain_head_sha256` + `committed_at` to Zenodo/git tag on Day 1; contents stay private.
- **Retest:** every `θ_k` scored against the *full* current vault after every change (model AND evaluator).
- **Reveal:** at publication, release contents; anyone verifies `merkle(contents) == committed chain_head`.
- **Acceptance:** append-only; reveal verification passes; any reordering/curation breaks the hash (tamper-evident, like Guard).

### II.2.8 VERIFIER CLI (`wind-tunnel-verify`)
- Recompute every headline metric + chain head from the public evidence index; exit 1 on drift. Pilot ships the seed; extend to all metrics + vault reveal check.

## II.3 The causal-fork engine (the moat, in detail — IP-2)
- **Procedural path (public tier):** the factorial IS the generator — enumerate `F_G` cells, generate matched items per cell holding other factors fixed, run attack+judge, diff ρ across cells. Clean because factors are constructed.
- **Universe path (richest tier):** take an exploit's world `c`; for each candidate factor, **fork the universe** with `intervention = single-variable`, `shared parent closure` (the CA continuation-fork machinery); the evolution witness certifies the counterfactual changed exactly one declared variable; run attack+judge per fork; the ρ pattern across forks is the interaction effect.
- **Naming:** minimal conjunction maximizing ρ (greedy + fractional-factorial screen to bound cost).
- **Validation:** prospective — generate a *new* held-out cohort in the named slice; H5 lift test vs. broad/random baselines.
- **Acceptance:** every causal claim traces to factorial cells (never observational clusters); universe forks carry witness receipts; prospective lift reported with CI.

## II.4 The convergence experiment (the science — IP-3)
```
freeze prereg (schemas, budgets, hypotheses, vault chain-head)   # before any result
for benchmark in tierA_named + tierB_universe:
  for theta_arch in {single, ensemble, self_commit, rubric_decomposed}:
    theta = theta_arch_0
    for k in 1..K:                        # patch cycles
      exploits = adversary.run(rung=L3 if k>1 else L1/L2, theta)   # budgeted
      vault.append(exploits)
      family = analyst.top_family(exploits)
      theta_next = patcher.patch(theta, family)                    # 3 modalities tried
      record(closure=Δ⁺, autoimmunity=Δ⁻, gamma, rho_heldout(theta_next))
      theta = theta_next
      if plateau(rho_heldout, window=j) or spent>budget: break     # prereg stop rule
    classify_convergence(rho_heldout[0..k])                        # monotone/plateau/oscillate
report (gamma, convergence_class, autoimmunity_frontier) per (benchmark, arch)
```
- **Acceptance:** stop rules prospectively fixed; every cycle logged; convergence classified by the prereg rule; report every cell incl. nulls.

## II.5 Milestones (with acceptance gates — implement in order)

| M | Deliverable | Acceptance gate | Status |
|---|---|---|---|
| **M0** | Procedural generator + exact oracle + factor tags | correct answers pass oracle; seed-reproducible | ✅ pilot |
| **M1** | Transform catalog + oracle-witness self-tests | every transform oracle-confirmed wrong | ✅ pilot |
| **M2** | Judge Bank (mock) + attack loop + Analyst core + verifier + slice screen | 16/16 tests green; slice recovered; chain head recomputable | ✅ pilot |
| **M3** | RealModelJudge adapters (4 archs) via Guard; L0+L1 on ONE named math benchmark | real exploit-density number; every judge call a Guard receipt; budgets enforced | Phase 0 |
| **M4** | L2 adaptive search + naturalness screen; causal-fork engine (procedural) + prospective validation | H5 lift > baselines on ≥1 slice; naturalness FP/FN measured | Phase 1 |
| **M5** | Patcher (3 modalities) + L3 re-attack + convergence loop + autoimmunity | γ and convergence class per arch; autoimmunity frontier plotted | Phase 1 |
| **M6** | Regression Vault (Merkle commit/reveal) + exploitability spectrum + exploit-DNA + disagreement detector + universe-tier forks | vault reveal verifies to Day-1 hash; spectrum + DNA + detector AUC reported; universe causal claim with witness | Phase 1 |
| **M7 (stretch)** | Coverage theorem (scoped) | proof for ≥1 transform family, or dropped cleanly | Optional |

Ship M3 as a **workshop paper / ICLR-rebuttal exhibit**; M4–M6 are the full paper; M7 is upside.

## II.6 Compute & cost model (small-n by design)
- Attempts = benchmarks × archs × rungs × families × per-cell-budget. With ~3 named benchmarks, 4 archs, small per-cell n (a few hundred), K≈5 cycles, this is **thousands, not millions** of judge calls. You control it via the prereg budget caps; the meter fails closed at the cap. Report exploits-per-dollar so cost is a first-class result, not an afterthought.
- **Cheapest high-signal first:** M3 on one math benchmark, single judge, L0+L1 — a few hundred calls, a first real number, a rebuttal exhibit.

## II.7 Risk register

| Risk | Type | Mitigation |
|---|---|---|
| Exploits look like injection → dismissed | Reviewer | L0 rung + naturalness screen + on-policy; report L0 first |
| Causal slice challenged as correlational | Reviewer | procedural factorial + universe forks + prospective validation |
| Convergence is messy/null | Scientific | prereg says either answer publishes; frame as finding |
| Named-benchmark break is wrong/embarrassing | Reputational | oracle-witnessed proof per exploit maintainers can run; disclose before publish |
| Patcher overfits (closes family, wrecks correctness) | Technical | autoimmunity guardrail rejects such patches by prereg threshold |
| Cost overrun | Ops | hard budget meter, fail-closed; small-n prereg |
| Vault could be seen as curated | Integrity | Merkle commit before results; reveal verification |
| Scope creep across too many benchmarks | Ops | 2–3 named + 2 universe, frozen in prereg |
| Universe forks leak identity in blinded submission | Integrity | reuse CA anonymity scan; env-var forbidden-pattern gate |

## II.8 Responsible-disclosure operational checklist (IP + ethics)
1. Confirm each exploit family with oracle-witnessed examples + causal slice.
2. Draft a **patch** per broken benchmark (rubric/judge/curriculum) + its vault regression test.
3. Privately notify maintainers (security contact / GitHub private advisory) with examples + patch + proposed embargo (30–45 days).
4. Track responses; offer a call; incorporate their fix if they ship one.
5. Publish only after embargo; include maintainer responses + acknowledgments.
6. Release the *defense* prominently (repair loop + vault + patches), not a turnkey attack script.
7. Never include real PHI; clinical items are synthetic.

## II.9 Guard integration points (make the whole study replayable)
Wrap in a Guard evidence chain: (a) each judge call, (b) each budget decision, (c) each oracle check batch, (d) each universe fork, (e) each patch application, (f) the vault commit. The paper then ships a single chain head; `wind-tunnel-verify` + Guard's verifier reproduce every number offline. This is your differentiator no one can copy without your stack.

## II.10 Paper-writing plan (write as artifacts land)
- After **M3**: draft Intro, Related Work, §Oracle-trick, and a first exploit-density table → workshop paper / rebuttal exhibit.
- After **M4**: add §Causal-slice with Fig 2 (the money figure).
- After **M5**: add §Convergence with Fig 3 + Fig 4; the central result.
- After **M6**: add §Spectrum/DNA/detector + Fig 5 + Table 1–3; the disclosure section with responses.
- Freeze, de-anonymize prior-work credits at camera-ready, publish preprint + release platform.

---

## Appendix A — the freeze checklist (do before any Phase-1 number)
- [ ] Schemas (II.1) frozen; each hashed into the prereg.
- [ ] Transform catalog frozen; `transform_catalog_sha256` recorded.
- [ ] Oracle specs frozen; `oracle_specs_sha256` recorded.
- [ ] Named benchmarks + snapshots pinned.
- [ ] Judge model ids+versions pinned.
- [ ] Budgets (queries/dollars per rung) fixed.
- [ ] Hypotheses H1–H5 directions committed.
- [ ] Vault empty-tree chain-head published (Zenodo DOI / git tag) with timestamp.
- [ ] Anonymity scan wired (reuse CA's) if targeting a blinded venue.

## Appendix B — what the pilot already proves (so you're not starting from zero)
`pilot/` realizes M0–M2 end-to-end offline: procedural math + exact oracle, five-transform catalog with oracle-checked witnesses, the attack loop, the factorial slice screen (recovers `keyword_inflation ∧ steps≥3`), autoimmunity + whack-a-mole demonstration, the self-commitment defense collapsing gaming to zero, and a recomputable chain head with tamper detection. 16/16 property tests green. Swap `KeywordGamingJudge → RealModelJudge`, point the generator at a named benchmark, and you're at M3.
