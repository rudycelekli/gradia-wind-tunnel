# The Proof-Bound Program — What Gradia Ships Next

### Prioritized plan of record · research claims, evidence packs, and the audit surface they become

> **The one line.** Gradia's asset is not a thesis, it is an *apparatus that refuses to overclaim*:
> proof-bound world state, single-variable branch/restore with a receipt, and evidence a stranger
> recomputes offline. Two artifacts already prove it works (the Conditionally Approved Universes
> study; the Reward-Hacking Wind Tunnel). The next three papers spend that apparatus on **empirical
> claims about models** — each shipping code, proof, and numbers — and each leaves behind an
> endpoint of the Gradia Benchmark Audit API.

**What changed from the previous draft.** That version proposed five papers built on five new terms.
It was wrong in three ways, and this revision fixes them:

1. **Self-overlap.** It didn't account for *Conditionally Approved* already claiming witnessed world
   roots and agent-visible projections. Papers pitched on those primitives would eat their own
   novelty. Differentiation is now by **claim type**: the existing submission is *methodological*
   ("this can be frozen, restored, audited"); everything below makes an **empirical claim about
   models** that the apparatus makes measurable.
2. **Neologism inflation.** Five coined terms dilute each other and reviewers punish it. We own one
   word — **proof-bound** — already used in the ICLR submission.
3. **The reproducibility hole.** Every claim is "third-party verifiable," but if verifying requires
   Gradia's substrate, the moat becomes the objection. §2 makes the open verifier non-negotiable.

Two papers are demoted on purpose. Neither is wasted: one folds in as a metric, one becomes the
product.

---

## 1. The Proof Pack — the standard every claim ships under

The wind tunnel's real innovation is not an attack family, it is a **discipline**: no number leaves
the building without the means to recompute and falsify it. Every claim below ships a Proof Pack,
and the Proof Pack is simultaneously the paper's appendix, the repo's artifact, and the API's
response object.

| Element | What it is | Already exists as |
|---|---|---|
| **Command** | one line that regenerates every number from scratch | `bash run_research.sh` |
| **Frames** | per-episode NDJSON, hash-chained, one line per scored attempt | `frames.ndjson` |
| **Manifest** | self-digested aggregate: totals, densities, CIs, provenance | `manifest.json` + `manifest_sha256` |
| **Pre-registration** | metric + attack/patch families frozen by SHA *before* the run | `GRADIA_WT_PREREG_SHA256` |
| **Verifier** | recomputes chain head, every derived aggregate and self-digest → green/red, offline | `gradia-wind-tunnel verify-bundle BUNDLE_DIR` |
| **Self-validation** | controls misbehave ⇒ the instrument **refuses to report** | SWE control audit, clean-instance reporting |
| **Intervals** | item-clustered bootstrap CI on every headline number | `stats.bootstrap_density_ci` |
| **Tests** | property guards, including one per defect the tool caught in itself | 165 green |
| **Anchor** | public timestamp proof of the prereg SHA + evidence heads (OpenTimestamps; CT-style log planned) | `cli anchor` in `run_research.sh` — live today |

**Why this is the brand, not the plumbing.** Anyone can publish a table. The distinctive thing —
across both existing artifacts — is an apparatus that *declines*: Conditionally Approved refuses
provider comparisons its evidence can't support; the wind tunnel caught its own SWE fail-open and
its own HumanEval syntax artifact and refused to report until both were fixed. Lead with that in
every venue. "The eval apparatus that argues with itself" is more memorable, and far rarer, than
any noun we could coin.

---

## 2. The open verifier — the non-negotiable that protects every claim

**Risk.** Results reproducible only on proprietary infrastructure are results reviewers discount and
competitors dismiss. Left unaddressed, "witnessed evidence" reads as "trust Gradia," which is the
exact opposite of the claim.

**Implemented boundary.** Split the stack in two, and say so in every paper:

- **Open (Apache-2.0, no Gradia dependency):** the bundle schema, the frames/manifest format, the
  chain-and-digest verifier, the index card schema, and a reference witness implementation. A
  stranger clones it, runs `verify`, and gets green/red on our bundles without an account.
- **Commercial (Gradia):** running the apparatus at scale — hosted branch/restore, Guard-routed
  judging with receipts, the continuously-updated index, audit workflows, retention.

The current repository now exposes the v1 frames/manifest verifier as the
account-free `verify-bundle` CLI and includes the reference witness. The generic
cross-program schema package, README badge, GitHub Action and hosted index are
still adoption milestones; the current implementation must not be described as
those later surfaces.

This is the standard open-core split, and it is what makes the moat *defensible in review*:
verification is free and universal; producing the evidence at scale is the product. Every paper
states plainly: **verification requires nothing from Gradia.**

**Public anchoring (shipped).** A chain we control proves integrity, not originality or time:
it cannot show the history wasn't regenerated, the prereg wasn't backdated, or that everyone
sees the same chain. So every `run_research.sh` fold now stamps an **anchor manifest** — the
preregistration SHA plus the evidence heads — via OpenTimestamps (calendar attestation
upgrading to Bitcoin block inclusion), with receipts that honestly record `stamped: false`
when no stamper or network is available. The sentence every paper carries: *the
preregistration and evidence heads are anchored in public timestamp logs; backdating or
equivocation by the authors is detectable by anyone.* This is the Haber–Stornetta / CT /
Sigstore lineage, deliberately not a blockchain play — no tokens, no on-chain compute, no
consensus; the CT-style public log for scorer versions and index cards (E, §3) is the
natural extension.

---

## 3. Prioritization — the scoring, then the calls

Five candidates scored on what actually determines return. 1–5, higher is better; **novelty
safety** = how likely it survives a "not novel" attack.

| Candidate | Novelty safety | Readiness | Anthropic fit | Gradia product | Cost | Call |
|---|---:|---:|---:|---:|---:|---|
| **A. Evaluator Mutation** (does reward-model repair converge or relocate?) | 5 | 3 | 5 | 5 | high | **Tier 1 — the bet** |
| **B. Oversight Under Witness** (human/AI judges ratify provably-wrong outputs) | 4 | 5 | 5 | 4 | low | **Tier 1 — the fast one** |
| **C. The Say–Do Gap** (report vs. witnessed deed) | 3 | 2 | 5 | 4 | med | **Tier 2 — narrow it first** |
| ~~D. Projection Gap~~ (reward hacking as proxy/true divergence) | 1 | 4 | 3 | 2 | low | **Fold in** as a metric |
| ~~E. Attestable Evaluation~~ (evidence, not claims) | 2 | 5 | 3 | 5 | low | **Ship as product**, not a paper |

**Why D folds rather than ships.** "Reward hacking is divergence between the proxy and the true
objective" is the textbook definition (Amodei et al. 2016), and Skalse et al. 2022 already give
formal hackability definitions. A standalone paper invites "this is Skalse with new vocabulary."
But as a *measured quantity inside* A and C — how far the scored projection moves while witnessed
ground truth stays fixed — it is a genuine operationalization of an existing theoretical construct,
and it gives both papers a shared axis. Same idea, defensible framing, zero extra runs.

**Why E ships as product rather than paper.** Protocol papers rarely spotlight without demonstrated
adoption, and attestation has prior art (SLSA, in-toto, Sigstore). But as **infrastructure** it is
the most valuable item on the list: it is already 80% built (§1), every paper cites it, and it is
the thing customers buy. Publish it as an open spec plus the audit API, and let adoption make the
case a paper couldn't. If adoption arrives, the paper writes itself later — with data.

---

## 4. Tier 1 · Paper A — **Evaluator Mutation: Does Reward-Model Repair Converge, or Relocate?**

**The claim (falsifiable, one sentence).** Locally patching a reward model against a demonstrated
exploit produces no significant reduction in held-out exploitability, while structural changes do —
and the difference is established by a single-variable intervention on the scorer, not a before/after
comparison.

**Why it's the bet.** It takes the wind tunnel's actual finding (γ_local = 0 — patching a rubric
judge relocates the flaw) and asks it of the machinery that trains frontier models. Reward-model
overoptimization is studied (Gao et al. scaling laws); whether *repair generalizes* is not, and
nobody else can run the causal version. High stakes, well-posed, and a negative result is still a
result.

**Differentiation.** Conditionally Approved shows an evaluator can be a versioned, restorable object.
This paper uses that to make an empirical claim about *reward models* — a different artifact, a
different literature, a different conference audience.

**Proof Pack.** Attack corpus per RM family; patch ledger (each repair a witnessed scorer-world fork
with "only this changed" verified); held-out exploit families pre-registered by SHA; convergence
coefficient with item-clustered CI; autoimmunity Δ⁻ (does the repair reject genuine-correct outputs?
— the alignment tax, measured); the **evaluator-repair Causal Atlas** (nodes = scorer worlds, edges =
witnessed patches) recomputable offline.

**Anthropic value.** RLHF/RLAIF is the core loop; "does hardening the reward model generalize?" is
directly load-bearing for it, and the honest answer is currently unknown.

**Gradia value.** `POST /audit/repair` — submit an evaluator and a demonstrated exploit, receive a
convergence coefficient and a patch-class recommendation (which repairs cure, which relocate). This
is the enterprise question: *we fixed the flaw you found — did it actually help?*

**Cost & risk.** Highest compute (open RM families, fine-tuning). Main risk: RM access and training
variance. **Kill criterion:** if repair effects can't be separated from training noise at n=3 seeds
on the pilot family, downgrade to a rubric-judge-only result and redirect to B.

---

## 5. Tier 1 · Paper B — **Oversight Under Witness: Where Humans and AI Judges Ratify Provably-Wrong Outcomes**

**The claim.** Against a hard oracle, human raters and LLM judges ratify oracle-wrong outputs at
measurable rates — and their errors **correlate on the same items**, concentrated on identifiable
surface properties (confident rhetoric, verification theater, fluency).

**Why it's the fast one.** It is already seeded. Conditionally Approved packaged **889 red criterion
surfaces** for "a separately scoped blinded-attribution study" and already reports four pinned judges
at Fleiss' κ = 0.151 with 26.1% unanimity. The wind tunnel supplies oracle-wrong-but-fluent items and
a naturalness screen that already passes 100%. This is mostly *analysis and raters*, not new compute.

**The finding that matters.** Not "judges are unreliable" — that is well-trodden (verbosity bias,
self-preference, MT-Bench). The contribution is **human/AI error correlation against ground truth**:
if AI judges inherit the specific blind spots of the humans they were trained on, then RLAIF and
weak-to-strong supervision do not escape those blind spots by construction. That is a real claim with
real consequences, and it needs exactly this apparatus — a hard oracle plus signed dispositions.

**Differentiation.** The existing submission reports judge *disagreement* with no ground truth and
explicitly refuses to claim human agreement. This paper adds the oracle, so disagreement becomes
**error**, and error becomes attributable.

**Proof Pack.** Blinded rater packet (50–100 oracle-labeled items, consented raters, no deception);
per-rating signed disposition with provenance; the automated naturalness screen's verdict per item
(kills "it's just prompt injection" pre-emptively); Oversight Reliability Index per judge — human
panel and models alike — with item-clustered and rater-clustered CIs; property-level breakdown of
what buys a wrong answer a pass.

**Anthropic value.** Scalable oversight rests on the human backstop holding. This measures where it
doesn't, and whether the AI judges meant to scale it inherit the same failures.

**Gradia value.** `POST /audit/oversight` — submit a judge or rubric, receive a reliability index and
the property profile of what fools it. Sells directly to anyone running LLM-as-judge in production.

**Cost & risk.** Lowest cost of the three; needs 2–3 raters and careful ethics (consent, no deception,
no sensitive content). **Kill criterion:** if the human panel's ratification rate is near zero, the
paper becomes "AI judges fail where humans don't" — still publishable, and still an honest result.

---

## 6. Tier 2 · Paper C — **The Say–Do Gap** *(narrow it before you build it)*

**What the previous draft got wrong.** It claimed agent benchmarks "grade the report, not the world."
That is false and a reviewer would kill it on sight: SWE-bench runs tests, τ-bench compares database
state, WebArena and OSWorld use programmatic validators. Deception and sandbagging measurement is
also an active area (Apollo's scheming evaluations; Anthropic's alignment-faking work).

**The narrow claim that survives.** Not "nobody checks the world," but: *the divergence between an
agent's **self-report** and the **witnessed delta** is a measurable, tamper-evident quantity that
existing validators do not capture* — because they check task success, not report fidelity. A binary
validator says pass/fail; it cannot say the agent claimed to migrate the database, actually
half-migrated it, and reported success. That gap is the paper.

**Proof Pack.** Witnessed agentic tasks whose oracle is the content-addressed world delta; a
report-extraction step (what the agent claimed) scored against that delta; **Reporting Fidelity
Index** per model with item-clustered CI; pressure conditions (deadline, oversight, shutdown threat)
as pre-registered arms; episodes with incomplete witnesses **excluded and named**, never scored.

**Anthropic value.** RSP-relevant: report fidelity under pressure is close to the capability
evaluations that matter for deployment decisions.

**Gradia value.** `POST /audit/witness` — attach to an agent deployment, receive report-vs-deed
divergence. The compliance-facing product: *your agent said it did the thing; here is whether it did.*

**Why Tier 2.** Most new engineering (the task suite), and it must be positioned against an active
literature rather than an empty field. Build it once A or B has landed and the vocabulary is
established — the result is the most quotable of the three, so it benefits from arriving with
authority behind it.

---

## 7. The product surface — how the papers become the audit API

Each paper ships an endpoint. The endpoints share one response object: a **Proof Pack** (§1). That
is the coherence that turns five research artifacts into one product line.

The short route names in the earlier memo were product sketches, not shipped
Gradia endpoints. The canonical managed API is versioned and benchmark-audit
scoped; a generic `/verify` would collide with existing identity, certificate and
receipt verification surfaces.

| Open/local surface | Managed `/v1` target | Question it answers | Exact state |
|---|---|---|---|
| `gradia-wind-tunnel index` | `GET /v1/benchmark-audit-evaluations/{evaluation_id}/gameability-index` | How gameable is this scorer? | Local index live; existing mutation/work-receipt primitives live; managed projection planned |
| evaluator-repair campaign | `POST /v1/benchmark-audit-evaluations/{evaluation_id}/evaluator-repair-campaigns` | Did a patch cure, relocate or worsen exploitability? | Paper A and managed route unrun/unbuilt |
| oversight study | `POST /v1/benchmark-audit-evaluations/{evaluation_id}/oversight-studies` | What oracle-wrong outputs fool this panel? | Paper B and managed route unrun/unbuilt |
| report-fidelity assessment | `POST /v1/benchmark-audit-evaluations/{evaluation_id}/report-fidelity-assessments` | Did the agent do what it reported? | Paper C and managed route unrun/unbuilt |
| `gradia-wind-tunnel verify-bundle BUNDLE_DIR` | optional convenience: `POST /v1/proof-packs/verify` | Is this bundle intact and derivable from its frames? | **Open offline verifier live; hosted route unbuilt** |

Three properties make this a business rather than a demo:

- **Every response is falsifiable.** A customer recomputes our number offline with the open verifier.
  An audit vendor whose findings you can check is a different category from one you must trust.
- **The free endpoint is the distribution.** `verify` costs nothing, requires no account, and works on
  anyone's bundles. It is how the schema becomes a norm — and norms are what a standard is made of.
- **The papers are the marketing that doesn't feel like marketing.** Each publication is a worked
  example of an endpoint, with the numbers already public.

**Adoption ladder, in order:** open verifier + schema → gameability badge maintainers drop in a README
→ GitHub Action → hosted index → audit API with retention and workflow. Each rung is cheap and each
makes the next one plausible.

---

## 8. Sequencing

**Now (weeks).** Finish the wind tunnel: SWE to target, R2 real-judge convergence, R3 powered
localization, fold via `run_research.sh`. Publish the **open verifier + bundle schema** (§2) — it is
nearly done, it protects every future claim, and it starts the adoption ladder immediately.

**Next (1–2 months).** **Paper B**, because it is seeded, cheap, and reuses packaged data. It also
produces the signed-disposition dataset that later work reuses.

**Parallel (2–4 months).** **Paper A** pilot on one open RM family. Decide at the kill criterion
before committing full compute.

**After.** **Paper C**, once A or B has landed and "proof-bound" carries weight.

**Continuous.** Responsible disclosure to benchmark maintainers before each public release; the
index kept live; every claim shipped as a Proof Pack.

---

## 9. For the Anthropic application — the honest strategic note

**Lead with what is finished, not with the roadmap.** You have two artifacts that answer "can he
deliver?" — a completed proof-bound instrument study that refuses the comparisons its evidence
can't support, and a wind tunnel with real numbers across five benchmarks, live containerized
SWE-bench results, 165 property/control tests, and **three defect classes it caught and now refuses
to report around**: dirty SWE controls, a HumanEval syntax artifact, and a self-consistent forged
aggregate. That last item is the strongest signal in the whole portfolio: it demonstrates research
integrity under pressure, which is the rarest thing to verify in a candidate.

A five-paper program presented as the headline invites "is this overreach?" This document is an
**appendix** — evidence of direction and judgment, including the judgment to demote two of its own
proposals. Two pages of it, at most, in any application.

**If asked "what would you work on here":** Paper A. It is the one whose answer the field needs, whose
method only this apparatus supports, and whose result is load-bearing for RLHF either way it comes
out.

**The through-line.** Every claim ships with the code, the proof, and the numbers — and anyone can
check them without asking us. That is the standard the wind tunnel already meets, and the only
standard worth scaling.

---

*Supersedes the five-paper draft. Companion to `paper/LANDMARK-PLAN.md` (Wind Tunnel) and the
Conditionally Approved ICLR 2027 submission. Discipline unchanged: witnessed ground truth,
pre-registration by SHA, item-clustered CIs, self-validation that refuses, offline byte-exact
verification — and, new here, verification that requires nothing from Gradia.*
