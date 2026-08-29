# The Reward-Hacking Wind Tunnel
### An evaluation immune system that attacks famous public benchmarks, identifies the exact causal slice being exploited, and proves — verifiably, with no human in the loop — whether the scorekeeper can be repaired

**Design document · Draft v0.3 · Rudy M. Celekli, Gradia Research**
*Status: pre-execution design + freezable preregistration. Decisions locked (§18). Pilot harness built (`pilot/`, 16/16 green). Companion: `WIND-TUNNEL-IP-AND-ATTACK-PLAN.md` (IP register + implementation roadmap). Start when compute is ready.*

**v0.3 adds:** formal problem statement (§22), figures/tables plan (§23), reviewer-objection matrix (§24), and a full companion document with the IP register and the build-it attack plan.

**What changed from v0.1 (read this):** three of your calls reshaped the paper for the better.
1. **No extra human reviewer.** We only use benchmarks whose ground truth is *machine-checkable*. The truth score comes from an **oracle**, not an expert. That makes the entire loop automated, reproducible, and cheap — and *more* rigorous, because there's no human-label noise. (§5 is the whole trick.)
2. **Universes lead.** The one thing no other lab can do — causal identification of the exploited slice via clean factorial intervention — is now the co-headline, not a supporting act. (§3.)
3. **Name and break famous benchmarks.** You'd rather establish expertise by naming real, well-known benchmarks and showing exactly how their scoring can be gamed — with a responsible-disclosure protocol that is itself part of the expert signal. (§13.)

---

## 0. The one sentence

> We turn a branchable, witnessed universe into a **causal instrument for model-evaluation failure**: an automated adversary finds answers that famous public benchmarks score as correct but that are wrong *by construction* (a machine oracle proves it), we fork the world to identify the exact variable interaction being exploited, and we measure — with every step in a tamper-evident evidence chain and zero human labeling — whether patching the benchmark's scorer converges or is whack-a-mole forever.

---

## 1. Why this is the right third paper (the program spine)

One thesis, three moves — this is what makes a research committee sit up:

- **Papers 1–2 (Interruptible Universes / Conditionally Approved):** benchmarks lie about *what happened* — world-state change is unverified. Fix: evolution witnesses + proof-bound receipts.
- **Gradia Guard:** runtime evidence is worthless unless tamper-evident and coverage-honest. Fix: hash-chained receipts that can't overclaim.
- **This paper (Wind Tunnel):** even with honest world-state and honest receipts, **the scorekeeper itself can be gamed** — and no one has measured whether that can be fixed.

> **Universes prove what happened. Guard proves nobody tampered with the record. The Wind Tunnel proves the scorekeeper can't be bought.**

That's a platform, not a paper pile — exactly the "environments + evaluation + training data" charter you're targeting.

---

## 2. The novelty map (build only in the open space)

The field moved in 2026. The naive idea — "an adversary finds answers that fool a judge" — is **published**. Writing that = desk reject. Here is what's taken and what's open.

### 2.1 Occupied (this is your Related Work + motivation, not your contribution)

| Prior work | Established | Why it isn't your contribution |
|---|---|---|
| **Self-Play Reward Hacking of Reference-Free LLM Judges** (arXiv 2607.05904, Jul '26) | Judges "score plausibility, not correctness." GSM8K: judge pass 0.72→0.94 while **true accuracy stayed 0.20**; exploits transfer across judge families; 3-judge ensemble still accepts **55%** of wrong answers. Best defense: **judge self-commitment** (solve before scoring) → FP 0.719→0.012. | This *is* the judge-high/truth-low gap. Your opening citation and opening number, not your finding. Their defense becomes one arm in your architecture table. |
| **Adversarial Reward Auditing** (arXiv 2602.01750, Feb '26) | Hacker-vs-Auditor game against RLHF reward models; latent detector; fixes sycophancy/verbosity/code-gaming. | They attack *reward models in training* with a representation probe. You attack the *deployed public-benchmark scorer* and measure *repair convergence*. Different target, different question. |
| **LLM-as-a-Judge Security SoK** (arXiv 2603.29403) | Taxonomy of judge attacks. | The map of the attack zoo. You don't add an attack; you close the loop and measure repair. |
| **Prompt-injection on judges** (arXiv 2504.18333) | Injection strings flip verdicts. | The failure mode you must *exclude* with a naturalness constraint (§6.3), or a reviewer says you rediscovered injection. |
| **LGMT — Logic-Grounded Metamorphic Testing** (arXiv 2605.23965) | Metamorphic testing for LLM reasoning. | Metamorphic testing for LLMs exists. Your twist (truth-breaking mutation with a machine-checkable *oracle witness*, aimed at the scorer, in a causal factorial) is the specific new use — never claim "we introduce metamorphic testing." |
| **PReMISE / Autorubric / JudgeBench / rubric-conditioned grading** (2605.30803, 2603.00077, JudgeBench, 2601.08843) | Rubrics-as-spec, unified rubric eval, judge benchmarks, rubric robustness. | Crowded 2026 subfield. You are **not** proposing a better rubric format — you're breaking rubrics and measuring repair. |
| **CAFFE** (arXiv 2512.16816) | Counterfactual fairness eval of LLMs. | Counterfactual perturbation for *fairness* exists. You differ by targeting *reward-hacking exploits* and using *true factorial forks in a witnessed universe*, validated prospectively. |

> ⚠️ PReMISE / Autorubric / LGMT / CAFFE positioning is from title+abstract. **Read each in full before submission and confirm the delta.** I don't believe any does a closed adversarial→repair loop with convergence measurement — but verify, don't assume. (Same discipline that saved us on the textbook frameworks.)

### 2.2 Open (this is the paper)

1. **A closed adversarial→repair loop with a convergence measurement.** Everyone finds exploits OR trains a defense. Nobody re-attacks the patch and asks whether the system converges. Adversarial-robustness history says patching rarely generalizes — *nobody has run that experiment on evaluation scorers.* Either answer publishes.
2. **Oracle-witnessed, wrong-by-construction attacks needing zero human labels.**
3. **Causal identification of the exploited slice via true factorial intervention**, validated by prospective held-out generation.
4. **An autoimmunity metric** — when a patch starts rejecting *correct* answers (immune system attacking healthy tissue). The metaphor everyone uses; the measurement no one reports.
5. **A cryptographically verifiable protocol** — every attack, judge call, and patch replayable; the hidden regression suite committed by hash before any results exist.

---

## 3. THE HEADLINE: witnessed universes are a causal instrument (lead with this)

This is the half-page that excites the Universes team, and it belongs in the abstract and the intro, not buried in methods.

**The claim other labs can make.** "The model fails on the elderly." On a static benchmark you find exploits, cluster their metadata, and report a correlation: *exploits concentrate at age 75+.* But editing a vignette to change age also perturbs coherence, length, ten other facts. **Confounded.** Every good reviewer knows it.

**The claim only you can make.** In a branchable, witnessed universe, an exploit's context is a *world you can fork and intervene on one declared variable at a time*, with the evolution witness certifying **nothing else changed**. That converts correlation into a controlled factorial experiment:

> *"The exploit fires **iff** age = 75+ **∧** dementia type = Alzheimer's **∧** the cited study excludes a specific cardiac condition"* — a causal claim, with a witness chain proving the counterfactuals were clean, validated by generating fresh held-out items in the predicted slice and showing the predicted failure rate materializes.

**Why this is the hire, not just a paper.** It reframes what universes *are*. Not a benchmark format — a **causal-inference instrument for model failures**. And it closes the team's entire charter in one motion: the tunnel finds the exploit (**evaluation**), the fork names the exact slice (**environment manipulation**), and the named slice becomes a data-generation order — *"make 400 more items at 75+ ∧ Alzheimer's ∧ cardiac-exclusion"* (**training data**). Find → explain → generate the fix, automated.

The sentence to open the paper:
> *"Public benchmarks can tell you a model is being gamed. Only a branchable, witnessed universe can tell you which counterfactual causes it — because only there can you change one fact and prove you changed nothing else."*

Register matters with this audience: pitch **measurement**, not "AI-safety immune system" grandiosity. Humble, quantitative, and it happens to require their substrate.

---

## 4. Contributions (abstract order: causal + convergence co-lead)

> **C1 — Universes as a causal instrument for evaluation failure.** We show a witnessed, branchable universe turns "which slice is being exploited?" from a confounded correlation into an identified interaction effect via single-variable forks, validated by prospective held-out generation.
>
> **C2 — The convergence question.** The first measurement of whether iterative attack-and-patch of a benchmark scorer converges, plateaus, or oscillates — and whether a patch generalizes to held-out exploit families or merely relocates the vulnerability.
>
> **C3 — Oracle-witnessed, wrong-by-construction attacks (zero human labels).** On machine-checkable public benchmarks, every exploit is confirmed by a ground-truth oracle, not an expert: a truth-breaking mutation carries a witness that the oracle verifies automatically, so the whole loop runs end-to-end with no human reviewer.
>
> **C4 — Autoimmunity.** The first measurement of the repair trade-off: how many *correct* answers each patch starts wrongly rejecting — the Pareto frontier of exploit-closure vs. correct-preservation.
>
> **C5 — A verifiable, contamination-proof protocol.** Every attack, judge call, and patch is a tamper-evident, offline-replayable receipt; the hidden regression suite is hash-committed before any results exist, making post-hoc curation cryptographically detectable.

Abstract shape: lead C1 (only-we-can-do-this) + C2 (surprising measurement), support with C3 (enabling trick) + C4 (new metric) + C5 (integrity). Spotlight-shaped.

---

## 5. The oracle trick — why there's no human in the loop (C3, the enabling move)

The fatal cost of the naive design is that "truth score is low" needs an expert per candidate; the search dies of labeling. We remove the expert entirely by **scoping to benchmarks whose ground truth is a machine oracle.**

**Definition.** An *oracle benchmark* is one where correctness of an answer is decided by a deterministic checker, not a judgment:
- **exact-answer math** (GSM8K-style): oracle = numeric equality.
- **execution-checked code** (HumanEval/MBPP-style): oracle = unit tests pass.
- **verified multiple-choice** (MMLU-style, ARC): oracle = key match.

**What the oracle buys us — the dependency collapse:**
- **Truth is free and exact.** `t(a,x)` = oracle verdict. No human, no noise.
- **Wrong-by-construction becomes double-locked.** Start from a verified-correct answer `a*`; apply a truth-breaking transform `m`; the transform's *witness* says "this is now wrong because …"; the oracle **independently confirms** the mutated answer fails. Witness-validity — the one thing that needed a human audit in v0.1 — is now checked by the oracle automatically. If a transform's witness ever disagrees with the oracle, that's a *bug in the transform*, caught mechanically.
- **An exploit is a fully automated event:** `judge(a) = PASS` **∧** `oracle(a) = WRONG`. No expert ever adjudicates.
- **The naturalness audit** (the other human step) is replaced by construction: answers are on-policy (sampled from the policy model, then minimally mutated) and passed through an automated artifact filter that bans injection-style meta-text (§6.3).

**The scoping cost, stated as a design choice, not a weakness.** We can only study tasks with machine-checkable truth. That excludes open-ended generation where "correct" is itself a judgment. We say so plainly and turn it into the two-tier design (§12): oracle benchmarks give airtight automation + external validity; universes extend the causal claims to richer, generated domains. This is *more* reproducible than any human-judged study, and we lead with that.

**Small-n is fine and preregistered.** You don't need thousands. Exploit density is a rate; a few hundred attack attempts per cell gives tight enough intervals to classify convergence, and the hidden-suite commitment (not sample size) is what makes it bulletproof. Budgets are prospectively fixed (§17); you control spend.

---

## 6. The threat-model ladder (pre-empts the #1 reviewer objection)

Report four rungs **separately** — never pooled (your own claim-ledger sin).

- **L0 — Natural incidence (no adversary).** Sample the policy model's ordinary outputs; measure how often it *already* emits oracle-wrong answers the benchmark's judge scores as correct. The "does reward hacking happen in the wild" number — the most credible one to a skeptic. L0 > 0 means the phenomenon is real before you attack anything.
- **L1 — Metamorphic mutation.** Oracle-witnessed truth-breaking edits of verified-correct answers. No judge queries; pure generate-and-test. Measures the base rate of scorer blind spots.
- **L2 — Adaptive search with judge query access, under a fixed budget.** Adversary may query the judge N times per exploit; report exploits per 1000 queries and per dollar. Naturalness constraint **on** (§6.3).
- **L3 — Patch-aware re-attack.** After a patch, the adversary is told the patch and re-searches. **This rung measures convergence (C2).** Without it there's no immune-system claim, only a one-shot audit.

**Adversary = an identity-pinned frontier model** (reuse your CA panel: Opus 5, Gemini 3.1 Pro Preview, Grok 4.6, GPT-5.6-sol). Cross adversary × judge — do exploits from adversary A transfer to judge B? The transfer matrix is a screenshot-grade table and directly extends the self-play paper's cross-family finding.

**Attack objective, formal.** For item `x`, benchmark scorer/judge `J`, oracle `t`: find on-policy answer `a` with `J(a,x) = PASS` and `t(a,x) = WRONG`. The margin by which `J` passes is the exploit magnitude.

**6.3 Naturalness constraint (do not skip).** At L2/L3 the answer must be one a deployed model could plausibly emit: constrain to on-policy generations, minimally edited; ban injection artifacts ("ignore previous instructions", judge-directed meta-text) with an automated screen. This paragraph is the line between "novel reward-hacking study" and "reviewer #2 says you rediscovered prompt injection."

---

## 7. Wrong-by-construction, worked (the transform catalog is itself a contribution)

Don't search answer space blindly. Start from verified-correct `a*`; apply a typed truth-breaking transform `m` with an **oracle-checkable witness** `w(m)`.

Worked, on a GSM8K-style item (the pilot implements exactly this):

| Transform | Edit | Oracle-checkable witness |
|---|---|---|
| `final-answer-corruption` | keep all reasoning, change the final number | oracle: mutated final ≠ gold |
| `off-by-one-step` | corrupt one intermediate arithmetic step, propagate | oracle: recomputed final ≠ gold |
| `keyword-inflation` | keep the *wrong* number, prepend rubric-favored phrasing ("carefully, step by step, the elderly population…") | oracle: final ≠ gold **and** answer now contains judge-favored tokens → tests keyword-gaming directly |
| `authoritative-wrong` | wrap the wrong answer in confident, well-structured justification | oracle: final ≠ gold; measures whether the judge rewards form over correctness |
| `irrelevant-citation` | attach a plausible but unrelated citation to the wrong answer | oracle: final ≠ gold; registry: citation not admissible |

Every witness is checked by the oracle or a rule — **no LLM, no expert.** Pipeline: mutate → oracle confirms wrong → judge scores → judge PASS = confirmed exploit, free.

**This is your evaluator-mutation philosophy, inverted.** In CA you mutated the *rubric criteria* (44 probes) to prove each gate *bites*. Here you mutate the *answer* to prove the judge's gates *leak*. Same instrument, opposite muzzle. Say that sentence — it signals method maturity and ties the program together.

Release the typed transform catalog (Apache-2.0). It becomes reusable infrastructure other labs cite and extend.

---

## 8. The causal slice detector, zero-human version (C1)

On oracle benchmarks you get causal control *without* needing universes for the pilot, because **procedurally generated items give you a factorial for free**:

- **Math:** generate matched problems varying declared factors — number of reasoning steps, operand magnitude, presence of a distractor quantity, unit conversion yes/no. You control every factor exactly, so "exploit fires at ≥4 steps ∧ distractor present" is a *true* factorial, not a correlation.
- **Code:** vary problem structure — recursion vs iteration, edge-case density, input size — programmatically.
- **MC:** vary distractor similarity, topic, answer position.

Procedure: (1) take a confirmed exploit; (2) enumerate candidate causal factors `V`; (3) generate the factorial grid (or a fractional-factorial screen) varying one factor per cell; (4) re-run attack+judge per cell; (5) the exploit's presence across cells is an **interaction effect**. Output: the exact conjunction, with the generation seeds recorded so anyone reproduces the grid.

**Validation (makes it real, not a story):** a named slice is a *prediction*. Generate fresh held-out items in the predicted slice; show the predicted exploit rate materializes vs. (a) a broad-slice baseline (one factor alone) and (b) a random-slice control. Predicted ≫ baselines ⇒ signal, not noise.

**Then the universe tier (C1's strongest form).** For the richest domains where factors interact with *world state* (your v4r1 underwriting family), the factorial lives in witnessed forks — same procedure, but the witness certifies clean single-variable intervention on a full agentic world, not just a text template. Public-benchmark procedural control gives external validity + reproducibility; universes give causal identification in settings too rich to template. Say exactly that in Limitations and reviewers trust both.

---

## 9. Metrics (half the novelty is measuring what nobody measures)

Define each with a formula and a preregistered estimator; ship a `wind-tunnel-verify` CLI that recomputes all of them from the public evidence index (the CA `cost-capped-verify` pattern).

- **Exploit density** — confirmed exploits / 1000 attempts, per rung, per adversary×judge cell. Base currency.
- **Exploit magnitude** — distribution of judge-pass margin on wrong answers.
- **Exploit half-life** — under L3, patch cycles until a family's density halves. Convergence rate.
- **Patch generalization (the single most important number)** — Δdensity on held-out families ÷ Δdensity on the patched family. <1 ⇒ specific/whack-a-mole; ≈1 ⇒ general immunity.
- **Autoimmunity / correct-answer preservation** — per patch, fraction of *verified-correct* answers the patched scorer now wrongly rejects. Plot closure vs. preservation → Pareto frontier.
- **Rubric bloat** — growth in scorer complexity over cycles vs. judge cost and correct-preservation.
- **Convergence classification** — fit density-vs-cycle to {monotone↓, plateau, oscillating} with a preregistered decision rule, per architecture.
- **Transfer rate** — fraction of exploits vs. judge A that also fire vs. judge B.

---

## 10. The verifiable protocol (C5 — where Guard plugs in)

**10.1 Every episode is a receipt.** Each attack, judge call, oracle check, causal fork, and patch runs through Guard: hash-chained frames, preregistered per-rung query/dollar budgets *enforced* (not just declared), whole run replays offline from the checked-in chain. The claim isn't "trust our numbers" — it's "here's the chain head; recompute." Literally your 20-day demo pointed at a research artifact.

**10.2 The hidden regression suite as a hash-committed prereg (your reserved-DOI trick, generalized).**
1. **Day 1:** every exploit found enters a permanent suite. Publish its **chain-head SHA-256** immediately; contents stay hidden.
2. **Throughout:** every new scorer version (every patch, every judge architecture) is scored against the *full* hidden suite — model AND evaluator retested after every change.
3. **Publication:** reveal the suite; anyone verifies contents hash to the day-1 commitment ⇒ **you could not have curated it post-hoc.**

No adversarial-eval paper has this. "A benchmark we mathematically could not have rigged" belongs in the abstract.

**10.3 Contamination resistance.** Procedurally generated items + a never-public-until-reveal suite = structurally contamination-proof. A live objection against every static benchmark, and it complements Paper 1's "benchmarks are flawed" thesis directly.

---

## 11. How it complements the program (put this paragraph in the intro)

- **Universes** supply the clean causal forks (§8) — this is universes' first application beyond world-state auditing, evidence the platform generalizes.
- **Guard** supplies the tamper-evident spine (§10) — Guard's first *research* consumer.
- **CA / four-judge result** — CA *observed* judge instability (κ=0.151, 55–70% pairwise). The Wind Tunnel *weaponizes* it: the cells where your four judges disagreed are the soft tissue. **Your 889 red assignments with four-judge disagreement are free L1 seed data.** Observational predecessor → interventional successor.
- **VEB** — a clean public benchmark you control end-to-end: the ideal first testbed where you know ground truth exactly before pointing the tunnel at external benchmarks.

Draft: *"Prior work in this program established that agent benchmarks under-verify world-state and that runtime evidence must be tamper-evident and coverage-honest. This paper closes the loop on the last trusted component — the scorekeeper — by treating a famous benchmark's scoring as an attack surface and measuring, for the first time, whether it can be repaired."*

---

## 12. Testbeds (two tiers; both fully automated)

- **Tier A — famous public oracle benchmarks (named).** Pick 2–3 with machine-checkable truth: one **math** (GSM8K-style — the self-play paper's turf, so directly comparable), one **code** (HumanEval/MBPP-style — execution truth, airtight witnesses), one **MC** (MMLU/ARC-style — key-match truth). Named, because you're establishing expertise (§13).
- **Tier B — Gradia universes.** v4r1 underwriting family + one second domain, for the richest causal claims (§8).

Report every headline metric on both tiers. The contrast *is* a finding: "public benchmarks let us find exploits; only universes let us fully explain them."

---

## 13. Naming-and-breaking famous benchmarks — done the expert way (responsible disclosure)

You chose to name real benchmarks and show exactly how their scoring gets gamed. That's higher-impact and more authoritative — *if* you pair it with a disclosure protocol that is itself the expert signal. This is how respected security researchers publish, and adopting that posture is what marks you as an expert rather than a provocateur.

**The protocol (make it a numbered section in the paper):**
1. **Coordinated disclosure first.** Before public release, privately notify each benchmark's maintainers with: the exploit families, the oracle-witnessed examples, the causal-slice finding, and **a suggested patch**. Offer a reasonable embargo window (e.g., 30–45 days).
2. **Fix, don't just dunk.** For each broken benchmark, ship a concrete scorer/rubric patch and the hidden-suite regression test that keeps it fixed. You're the one who *repairs* the benchmark, not just the one who broke it — that's the reputation you want.
3. **Report their response.** Include maintainer acknowledgments/reactions in the paper. A maintainer thanking you in the acknowledgments is worth more than any self-claim of expertise.
4. **Frame as defense.** The artifact you release prominently is the *repair loop + hidden-suite protocol*, not a turnkey "fool any benchmark" script. The naturalness constraint (§6.3) already limits weaponization to plausible failures, not injection payloads.
5. **No PHI / synthetic clinical.** Universe clinical examples are synthetic, never real records — state it.

Say in the paper, plainly: *"We name these benchmarks because vague criticism does not help the field; each finding was disclosed to maintainers with a patch before publication, and we report their responses."* That sentence *is* the expert posture.

**One honest caution:** naming benchmarks raises the correctness bar. A wrong exploit against a famous benchmark is embarrassing in a way a vague claim never is. Which is exactly why the oracle-witnessed design matters — every named exploit ships with a machine-checkable proof of wrongness that a maintainer can run themselves. Your usual discipline isn't optional here; it's the whole shield. And it's *good* that the bar is high — clearing it publicly is what sets you apart.

---

## 14. Paper skeleton (spotlight-shaped)

1. **Intro** — the scorekeeper is the last untrusted component; universes as causal instrument (§3); the three-move program; C1–C5.
2. **The benchmark scorer as attack surface** — threat ladder L0–L3.
3. **Related work** — the §2.1 table, honestly; lead with self-play + ARA; differentiate on closed-loop + convergence + causal + verifiable.
4. **Oracle-witnessed wrong-by-construction attacks** — transform catalog, the dependency collapse (C3).
5. **Causal slice identification** — procedural factorial + universe forks, prospective validation (C1).
6. **The repair loop & convergence** — patch synthesis, hidden suite, the convergence classification (C2, C4).
7. **Verifiable, contamination-proof protocol** — Guard spine, hash-committed suite (C5).
8. **Experiments** — 2–3 named oracle benchmarks + 2 universe domains; adversary×judge matrix; convergence curves; autoimmunity Pareto; architecture-per-dollar table (incl. self-commitment arm).
9. **Findings** — convergence classification; whack-a-mole verdict; self-commitment helps ≠ cures; named slices predict.
10. **Responsible disclosure** — §13, with maintainer responses.
11. **Limitations** — oracle-only scope; adversary ≠ all models; compute bounds rung depth; public slices quasi-experimental (universe slices causal).
12. **Program & future work.**

Appendices: transform catalog spec; per-benchmark oracle rules; full prereg; evidence-index schema; `wind-tunnel-verify` docs.

---

## 15. Execution plan (start now, small-n, automated)

Your queue: adjudication (Papers 1–2) and Study C are the critical path. But this paper is *cheap to start* because it's automated and small-n.

- **Now (zero compute, done today):** this design; the **pilot harness** (`pilot/`, already built and demonstrated offline); the **freezable prereg** (§17). Locking the prereg lets you cite a preregistered successor in the ICLR rebuttal.
- **Phase 0 — pilot (days, tiny budget):** one named math benchmark, L0+L1, single judge, real models via your keys. Goal: a first real exploit-density number + one causal-slice proof-of-concept on procedurally generated math. This alone is a workshop paper / strong rebuttal exhibit.
- **Phase 1 — full study:** all four rungs, 2–3 named oracle benchmarks + 2 universe domains, adversary×judge matrix, K patch cycles, hidden suite committed, disclosure protocol running in parallel (notify maintainers as soon as Phase-1 exploits are confirmed, well before write-up).
- **Phase 2 — release:** transform catalog + `wind-tunnel-verify` + revealed suite, Apache-2.0.

**Sequencing rule:** don't let Phase 1 compute displace adjudication for Papers 1–2 — that's still the highest-value bottleneck. But Phase 0 is small enough to run in the seams, and the prereg locks now.

---

## 16. Venue

- **TMLR** — claims-supported-by-evidence bar, rolling, tolerates "interesting-either-way" convergence results; already your VEB plan. Natural home.
- **Top-tier conference (NeurIPS D&B / ICLR 2028)** — if convergence is crisp and the named-benchmark breaks land, spotlight potential is real; the verifiable + hidden-suite integrity story is what benchmark tracks say they want.

Decide after Phase 0: crisp → conference; nuanced → TMLR. Don't pre-commit.

---

## 17. Preregistration skeleton (freeze before any Phase-1 result)

```
IDENTITY: gradia.wind-tunnel.eval-immune-system.v1
FREEZE BLOCK:
  design_commit: {{PHASE1_COMMIT}}
  frozen_at_utc: {{TIMESTAMP}}
  adversary_models:  {{pinned ids+versions}}
  judge_architectures: {single, naive-ensemble, self-commitment, rubric-decomposed}
  tierA_named_oracle_benchmarks: {{math, code, MC — named + snapshot/commit}}
  tierB_universe_domains: {{v4r1 + one more}}
  transform_catalog_sha256: {{frozen truth-breaking transform set}}
  oracle_specs_sha256: {{per-benchmark deterministic checker definitions}}
  hidden_regression_suite_chain_head_sha256: {{committed BEFORE results}}
  budgets: per-rung {queries, dollars} caps, prospectively fixed
  pass_threshold, exploit-magnitude bins: {{fixed}}

HYPOTHESES (direction pre-committed):
  H1 convergence-shape (≥1 architecture monotone↓ on held-out budget)
  H2 patch-generalization < 1 (whack-a-mole)
  H3 autoimmunity trade-off exists (closure ⟂ preservation, negative)
  H4 self-commitment dominates per-dollar but ≠ 0 exploitability
  H5 causal-slice prospective lift > broad-slice and random-slice baselines

PRIMARY OUTCOMES: exploit density/rung; patch-generalization ratio; autoimmunity Pareto;
  convergence classification/architecture; slice prospective-validation lift; transfer matrix.

STOP RULES (prospective): max K patch cycles OR density plateau over {{j}} cycles;
  max total dollars {{$}}; per-cell attempt budget {{n}} fixed in advance.

ANALYSIS-BLIND GATES:
  - transform catalog + oracle specs frozen before attacks
  - hidden-suite hash published before any scorer is graded against it
  - causal claims only from factorial cells (procedural or universe); observational
    metadata clusters labeled hypothesis-generating
  - no pooling across rungs or across adversary×judge cells in headline claims
  - report every preregistered cell even if null (CA claim-ledger discipline)

DISCLOSURE: maintainers of each named benchmark notified with patch + embargo
  before public release; responses reported.
REVEAL: hidden suite released at publication; verify hash == day-1 commitment.
```

---

## 18. Decisions — LOCKED (per your calls)

1. **No extra human reviewer** → oracle benchmarks only; truth is machine-checkable; loop fully automated (§5). ✅
2. **Domains** → famous public **oracle** benchmarks (math + code + MC), plus universes for causal depth (§12). ✅
3. **Budget** → you handle; **small-n** by design (rates, not volume; a few hundred attempts/cell), budgets prereg-fixed (§5, §17). ✅
4. **Patch autonomy** → **automatic** patch synthesis (no human), which the oracle makes possible; a human-approval arm is optional future work, not required. ✅
5. **Disclosure** → **name and break** famous benchmarks, paired with the responsible-disclosure-with-patch protocol that establishes expertise (§13). ✅

**Still yours to pick (small, not blocking):**
- Which specific named benchmarks for Tier A (my rec: GSM8K for math — direct comparability to self-play; MBPP or HumanEval for code — cleanest oracle; ARC-Challenge or MMLU-subset for MC). Tell me and I fill the prereg.
- K (patch cycles) and per-cell attempt budget — set by your spend; I'll suggest defaults once you name a dollar ceiling.

---

## 19. What's already built (the ball is rolling)

`pilot/` in this folder is a **runnable, offline, zero-key** proof that the core loop works:
- procedurally generated GSM8K-style items with an exact numeric **oracle**;
- the typed **transform catalog** with oracle-checked witnesses (§7);
- a **pluggable judge**: a deterministic `KeywordGamingJudge` that reproduces the documented failure mode (rewards rubric-favored phrasing) so the pipeline runs with no API key **right now**, plus a real-model adapter stub that reads your key from the environment for Phase 0;
- the **exploit-finding loop** (judge PASS ∧ oracle WRONG);
- a **factorial slice screen** on procedural factors (§8);
- a **verify CLI** that recomputes exploit density from the run log (the CA trust move);
- **tests**, all green.

Run `python -m pilot.demo` and it finds keyword-gaming exploits end-to-end. That's your Phase-0 skeleton; swap the mock judge for your real-model adapter and it's collecting real numbers.

---

---

## 20. Deeper novelty — five mechanisms that make this stronger than a "find exploits" paper

You asked for maximum novelty and granular architecture. Here are five inventions that go *beyond* the closed loop, each a citable contribution on its own, each buildable on your stack. Add the ones that survive your own scrutiny; even two of them lift this above the other papers.

### 20.1 The Exploitability Spectrum — a benchmark's "immune profile," not a scalar
Don't report one exploit-density number per benchmark. Report a **profile**: a vector over (transform family × causal-slice × judge-architecture) of exploit density + magnitude. Two benchmarks with identical accuracy can have wildly different immune profiles — one gamed only by keyword-inflation at high depth, another gamed everywhere. **The profile is the artifact**: it's what a benchmark maintainer actually needs, it's never been published, and it's a fingerprint you can track over benchmark versions. Novel object: *the first "exploitability spectrum" for named benchmarks.*

### 20.2 Transferable exploit DNA — do exploits share structure across benchmarks?
Every confirmed exploit carries its transform + slice + judge-response as a typed record ("exploit DNA"). Cluster DNA across benchmarks and adversary×judge cells. The research question no one has asked: **is there a small universal basis of judge blind spots** (say, 6–8 recurring exploit archetypes) that explains most exploits across *all* benchmarks? If yes — a *periodic table of reward hacks* — that's a landmark result and a reusable defense target. If no, that's also a finding (blind spots are benchmark-idiosyncratic). Either way, novel.

### 20.3 The judge that watches itself — meta-evaluation via disagreement geometry
Reuse your four-judge instrument (κ=0.151) as an **online exploit *detector***, not just an offline auditor. Hypothesis: exploits live disproportionately in the region where independent judges *disagree*. If disagreement geometry predicts exploitability, you get a **cheap, deployable early-warning signal** — flag any answer landing in the high-disagreement manifold for human/oracle review — without needing the oracle at inference time. This directly extends CA's contribution 5 (single-judge instability) from *observation* to *operational detector*, and it's the kind of "measurement that becomes a tool" that reviewers love.

### 20.4 Adversarial curriculum → the exploit becomes training data (closes the charter loop)
The named causal slice isn't just a diagnosis — it's a **generation order**. Feed identified slices back as a curriculum: generate a fresh cohort in the exploited slice, and measure whether *retraining the judge* (or the rubric) on that cohort closes the slice **without** collapsing correct-answer preservation. This is the environments→evaluation→**training-data** loop executed end to end, automatically, with the autoimmunity metric as the guardrail. For the Universes team specifically, this is the money contribution: *the wind tunnel doesn't just audit an evaluator, it manufactures the data that repairs it.*

### 20.5 Formal guarantee layer — a provable floor on undetectable exploits
The ambitious swing. Under the oracle model, define an exploit as detectable iff some committed detector in your library flags it. Then state and prove a **coverage theorem**: given detector set D and transform catalog T, characterize the class of wrong answers that *provably cannot* pass without triggering ≥1 detector — and, dually, the residual class that can. This gives the paper a *theory* spine (rare in eval papers), turns "we found exploits" into "here is the boundary of what this evaluator can and cannot catch," and it's exactly your Guard philosophy — coverage honesty — lifted to evaluation. Even a scoped version (one benchmark, one transform family) is a differentiator. Flag clearly as the stretch goal; don't let it block the empirical paper.

**Architecture granularity (for the methods section).** The system is five services with typed contracts, each independently testable and Guard-instrumented:
`Generator` (procedural items + factor tags + oracle spec) → `Adversary` (transform catalog × rung policy, budget-metered) → `Oracle` (deterministic witness check) → `Judge Bank` (single / ensemble / self-commitment / rubric-decomposed, hot-swappable) → `Analyst` (exploit DNA, slice screen, spectrum, autoimmunity) → `Patcher` (rubric/judge/curriculum synthesis) → `Regression Vault` (hash-committed hidden suite) → back to `Adversary` (L3). Every arrow is a Guard receipt; every service has a frozen schema hash in the prereg. The pilot already implements Generator→Adversary→Oracle→Judge→Analyst; Patcher + Vault + L3 are Phase 1.

---

## 21. Credit where it's due — this paper stands on the program (and says so loudly)

Reviewers reward a coherent research program; funders and hiring committees reward it more. This paper must **explicitly cite and credit** the prior work, not as boilerplate but as load-bearing foundation:

- **Cite Interruptible Universes / Proof-Bound Branchable Universes (Conditionally Approved), Zenodo DOI 10.5281/zenodo.22087020 (concept) / 22104672 (v1.1.0), OpenReview IrPdpUo7Rz** as: (a) the source of the witnessed-universe substrate that makes §8's causal forks possible — *"the branchable, witnessed universe of [CA] is what lets us intervene on one variable and prove nothing else changed"*; (b) the origin of the four-judge instability instrument (κ=0.151) that §20.3 turns into a detector — *"we build directly on the multi-judge disagreement finding of [CA]"*; (c) the claim-ledger / preregistration methodology this paper inherits wholesale.
- **Cite Gradia Guard** as the evidence substrate (§10): *"all attack, judge, and patch episodes are recorded using the tamper-evident evidence runtime of [Guard]."* Guard's coverage-honesty principle is the intellectual parent of §20.5's coverage theorem — say so.
- **Cite The Value Engine Benchmark** as the controlled public testbed used before external benchmarks (§12).
- **A "Relation to prior work in this program" paragraph** in the intro, stating the three-move thesis explicitly. This is the paragraph that makes three papers read as one body of work — which is worth more than the sum.

Draft credit line for the intro:
> *"This work is the third in a program on verifiable evaluation. [Interruptible Universes] established that agent benchmarks under-verify world-state and contributed the witnessed, branchable universe we use here as a causal instrument; [Gradia Guard] contributed the tamper-evident evidence runtime that records every experiment; and [Conditionally Approved] contributed both the proof-bound benchmark methodology and the multi-judge instability finding that motivates attacking the scorer directly. We are grateful to build on that foundation."*

(Blinded for ICLR-style submission: cite as "prior work by the authors [Anonymous]" per venue norms, then de-anonymize at camera-ready. Never leak identity in the anonymous version — same discipline as CA.)

---

---

## 22. Formal problem statement (the notation the paper uses)

Give reviewers a crisp formalization; it signals rigor and pins down exactly what is claimed.

**Objects.**
- Task item `x ∈ X` with a **factor vector** `φ(x) ∈ F = F₁ × … × F_d` (the declared, controlled causal factors: steps, operand-magnitude, distractor, … — exactly known because items are generated).
- **Oracle** `t : A × X → {CORRECT, WRONG}`, deterministic and cheap (numeric equality / unit tests / key match). Ground truth, no human.
- **Answer space** `A`; a **verified-correct** answer `a*(x)` with `t(a*(x), x) = CORRECT`.
- **Scorer / judge** `J_θ : A × X → {PASS, FAIL}` with real-valued margin `m_θ(a,x) ∈ ℝ`; `θ` indexes the judge *architecture* (single, ensemble, self-commitment, rubric-decomposed) and its patched versions `θ₀, θ₁, …, θ_K`.
- **Transform** `m ∈ T`, a truth-breaking map `A × X → A` with a machine-checkable **witness** `w_m(a,x)` such that a valid transform guarantees `t(m(a,x), x) = WRONG`.

**Exploit.** An answer `a` is an *exploit* of `J_θ` on `x` iff
> `J_θ(a, x) = PASS  ∧  t(a, x) = WRONG`.
An exploit is *witnessed* iff produced by a transform whose witness the oracle confirms (`w` valid). All L1 exploits are witnessed by construction — the labeling cost is zero.

**Exploit density** on item set `S`, judge `θ`, transform family `m`, rung `ℓ`:
> `ρ(S, θ, m, ℓ) = (1/|Att|) · Σ_{(a,x)∈Att} 𝟙[exploit(a,x,θ)]`, `Att` = attempts generated under rung `ℓ`'s policy.

**Causal slice.** For a factor subset `G ⊆ {1..d}` and a value assignment `v`, the *slice* `S_{G=v} = {x : φ_G(x) = v}`. Because items are generated, `S_{G=v}` cells are a **true factorial**, so `ρ` differences across cells are **interaction effects**, not correlations. A *named slice* is the minimal conjunction `G=v` maximizing `ρ(S_{G=v}, …)`; its **validity** is the prospective lift `ρ(S^{held-out}_{G=v}) − max(ρ_broad, ρ_random) > 0`.

**Patch.** A map `P : θ_k → θ_{k+1}` synthesized from a discovered exploit family, of one of three modalities (rubric edit, judge-architecture change, curriculum retrain — §Attack-Plan). Two quantities per patch:
> **closure** `Δ⁺ = ρ(patched family; θ_k) − ρ(patched family; θ_{k+1})` (want > 0);
> **autoimmunity cost** `Δ⁻ = FRR(θ_{k+1}) − FRR(θ_k)`, `FRR(θ) = Pr_{a*}[J_θ(a*,x)=FAIL]` over verified-correct answers (want ≈ 0).

**Patch generalization** `γ = Δρ_heldout / Δρ_patched ∈ [0,1]` (γ<1 ⇒ whack-a-mole). **Convergence**: classify `k ↦ ρ_heldout(θ_k)` into {monotone↓, plateau, oscillating} by a prereg rule. **The paper's central empirical object is the pair (γ, convergence-class) per architecture, with the autoimmunity frontier (Δ⁺, Δ⁻).**

This half-page turns the whole design into estimable quantities; every hypothesis in §5/§17 is a statement about one of them.

---

## 23. Figures & tables plan (spotlight papers win on the visuals)

Design the figures before running — they dictate what you log.

- **Fig 1 — the loop schematic.** Generator→Adversary→Oracle→Judge Bank→Analyst→Patcher→Vault→(L3 back), every arrow a Guard receipt. One clean diagram that *is* the paper. (Reuse your CA pipeline-figure style.)
- **Fig 2 — the causal-slice reveal.** A factorial heatmap: exploit density across `steps × distractor` (or the domain's factors), with the named conjunction boxed, and a second panel showing the *prospective* held-out cohort hitting the predicted rate. This is the Universes-team money figure.
- **Fig 3 — convergence curves.** ρ_heldout vs. patch cycle `k`, one line per judge architecture, annotated with the convergence class. The "does it converge?" answer at a glance.
- **Fig 4 — the autoimmunity Pareto frontier.** Δ⁺ (closure) vs. Δ⁻ (correct-answers-lost) scatter, one point per patch, per architecture; the frontier drawn. The metaphor, quantified.
- **Fig 5 — the exploitability spectrum.** Per named benchmark, a small-multiples grid of density over (transform × slice), so two benchmarks with equal accuracy visibly differ. The artifact maintainers will want.
- **Table 1 — adversary × judge transfer matrix.** Fraction of exploits from adversary A that fire on judge B. Extends the self-play cross-family result.
- **Table 2 — architecture per-dollar.** Exploit density, γ, and cost for each judge architecture (incl. self-commitment). The practitioner screenshot.
- **Table 3 — named-benchmark breakage summary** with disclosure status + maintainer response per benchmark.

Log schema must capture everything these need on the first run; retrofitting a figure means re-spending compute.

---

## 24. Reviewer-objection matrix (pre-empt every rejection path)

Write the rebuttals into the paper before a reviewer writes the objection.

| Likely objection | Where it bites | Pre-emption already in the design |
|---|---|---|
| "You rediscovered prompt injection / self-play reward hacking." | Novelty | §2 table + §2.2: your contribution is the *closed loop + convergence + causal fork + verifiable*, not the attack. Lead C1/C2, cite 2607.05904 as motivation. |
| "Exploits are adversarial curiosities, not real model behavior." | Significance | §6 L0 natural-incidence rung; §6.3 naturalness constraint + on-policy generation; report L0 first. |
| "Your causal slices are just correlations." | Validity | §3/§8: true factorial via generated items + universe forks; prospective held-out validation (H5), random-slice control. |
| "You can't judge truth without a human." | Method | §5 oracle trick: truth is a deterministic checker; zero human labels; *more* reproducible than human-judged work. |
| "Small-n." | Rigor | §5: density is a rate; prereg CIs; the integrity guarantee is the hash-committed suite, not sample size. |
| "You cherry-picked which exploits to report." | Integrity | §10.2 hash-committed hidden suite revealed at publication; §17 report-every-cell rule. |
| "Breaking famous benchmarks is irresponsible." | Ethics | §13 coordinated disclosure + a *patch* per break + maintainer responses; defense framing. |
| "Results won't generalize beyond your benchmarks." | External validity | §12 two-tier (2–3 named public + 2 universe); §20.2 exploit-DNA cross-benchmark analysis explicitly tests generality. |
| "Judge architectures are strawmen." | Fairness | §6/Table 2 includes the *strongest known* defense (self-commitment, per 2607.05904) as an arm; you show it helps, honestly. |
| "Where's the theory?" | Depth | §20.5 coverage theorem (scoped) gives a provable detectability boundary. |

If a reviewer's objection isn't in this table after you draft, add it and its rebuttal. This table is your rebuttal period, pre-written.

---

## 25. Companion document

The **what/why** lives here. The **how** and the **IP** live in `WIND-TUNNEL-IP-AND-ATTACK-PLAN.md`:
- **Part I — IP Register:** every novel invention as a numbered, defensible claim with prior-art delta and publish-vs-protect note; a freedom-to-operate map; the research-program claim ladder.
- **Part II — Attack Plan:** typed service contracts, data schemas, per-component build specs, the causal-fork engine, the patch synthesizer (three modalities), the regression-vault Merkle protocol, the convergence experiment, milestones M0–M6 with acceptance criteria, a small-n compute/cost model, the risk register, and the responsible-disclosure operational checklist. Written so you can implement straight from it.

---

*Positioned against literature surfaced Aug 28 2026; PReMISE/Autorubric/LGMT/CAFFE deltas inferred from title+abstract — confirm by full reads before submission. The causal-fork, convergence, autoimmunity, exploitability-spectrum, exploit-DNA, disagreement-detector, adversarial-curriculum, coverage-theorem, and hash-committed-suite contributions are, to the best of this search, unoccupied. That is the paper. A runnable pilot (`pilot/`) already demonstrates the core loop end-to-end offline: 16/16 tests green, keyword-gaming exploits found, the steps≥3 causal slice recovered, whack-a-mole and autoimmunity shown, self-commitment defense verified, chain head recomputable.*
