# The Reward-Hacking Wind Tunnel — Landmark Plan
### Gradia Program, Paper III · plan of record

> **The one line.** Reference-free scorers are gameable *diffusely*, so evaluator repair
> **relocates** rather than converges — and we prove it with a **witnessed, recomputable causal
> tree** of single-variable interventions that no static benchmark can produce.

The goal is not a paper that passes review. It is a paper researchers **keep sending each other**:
because it hands them a number they can run on their own benchmark today, a result that changes how
they think about hardening evaluators, and a causal claim they can recompute offline and verify to
the byte. This document is the plan to get there, and — the heart of it — how we push the **Gradia
Universes branching** machinery to its maximum to make the causal spine unassailable.

---

## 1. Why this paper gets shared (the design constraints, not afterthoughts)

A paper spreads when it gives the reader something they can *use* and something they can't *unsee*.
We engineer for both:

1. **A one-command number on *their* benchmark.** `uvx gradia-windtunnel index --benchmark X`
   returns a scorer-gameability score + 95% CI, content-addressed. Infrastructure, not a claim —
   the living index is the thing a maintainer runs and a reviewer cites.
2. **A result they can't unsee.** *Patching a gamed scorer moves the flaw, it does not fix it*
   (whack-a-mole convergence, γ_local = 0). Once you've read it you re-evaluate every eval-hardening
   story you meet. It is the proxy-reward-hacking / alignment question in miniature.
3. **Credibility they can feel.** The instrument caught its **own** defects twice and refused to
   report (§8.4 SWE fail-open; §8.5 the HumanEval syntax artifact). Reviewers trust a tool that
   argues with itself.
4. **Reproducibility as a feature.** Every number recomputes from `frames.ndjson`; every causal
   claim recomputes from a **hash-chained tree of witnessed forks**. "Trust me" appears nowhere.
5. **An ethical spine that licenses breaking famous benchmarks.** Responsible disclosure + the
   living index reframe an adversarial tool as a community immune system.

Every item below is scored against these five.

---

## 2. Current state (real, recomputable — as of this plan)

| Component | Status | Real result |
|---|---|---|
| L1 metamorphic, 5 benchmarks × ~200 | ✅ | MATH 107.5 · HLE 64.5 · GPQA 6.6 · GSM8K 0 · HumanEval superseded |
| L2 adaptive search, 5 benchmarks | ✅ | ~doubles leaking scorers (HLE 125, MATH 185, GPQA 6.6→15.2); GSM8K 0 at every budget |
| Repair→convergence (C2) | ✅ | relocation_plateau, γ_local = 0; structural self-commitment cures |
| Adversary×judge transfer | ✅ | signal-specific (5–30% cross-transfer), paradigm-universal, verifier passes 0 |
| Bootstrap CIs + living gameability index | ✅ | content-addressed, self-verifying cards; one-command refresh |
| Witnessed single-variable localization | ⚠️ | **mechanism-positive, attribution-inconclusive** — diffuse defect (the leg to power) |
| SWE-bench live (containerized oracle) | 🔄 | valid oracle-witnessed exploits, stratified 50 across 12 repos, checkpointing |
| Naturalness | ⚠️ | automated screen passes 100%; human ratings pending |
| Real-LLM-judge convergence/transfer | ⚙️ | built + offline-verified; not yet run on the Guard judge |
| Regime 2 (oracle-less) | ⚠️ | GSM8K done; HLE/MATH pending |
| Property tests | ✅ | 147 green; guards on every module incl. both caught-defects |
| Prior-work anchor | ✅ | Zhou 2026 (2607.05904) — corroborates on every axis; we extend it |

Legend: ✅ done · 🔄 running · ⚙️ built, unrun · ⚠️ needs a run/strengthening.

---

## 3. The remaining runs (concrete, costed, sequenced)

All are one command; none is research-risky; each closes a specific reviewer angle.

| # | Run | Command | ~Cost | Closes | Needs |
|---|---|---|---|---|---|
| R1 | HumanEval re-run (corrected attacks) | `caffeinate -i bash run_humaneval_fix.sh` | ~$6 | the superseded artifact | Mac |
| R2 | Real-judge convergence + transfer | `REAL=1 bash run_realjudge.sh` (per benchmark) | ~$30–60 | "your judge is a toy" | Mac + Guard |
| R3 | **Powered localization** (see §4.2) | `localize … --limit 200` on MATH, HLE | ~$60–90 | the underpowered causal leg | Mac |
| R4 | Regime 2 on HLE + MATH | `regime2 … --real --live` | ~$70 | the oracle-less half (two-regime) | Mac |
| R5 | Naturalness human study | rater packet (see §6) | $0 | "it's just prompt injection" | 2–3 people |
| R6 | Finish SWE live (in progress) | already running | — | live containerized result | Mac |
| — | Fold everything | `bash run_research.sh` | $0 | tables + index + CIs refresh | — |

Sequencing: R1 (cheap, removes an error) → R6 finishes on its own → R2 and R3 in parallel with the
human study (R5) → R4 → fold. Nothing here is a dependency for a strong paper; each is a
strengthener that removes a soft leg.

---

## 4. The Gradia Universes branching program — pushing witnessed forks to the max

This is the differentiator and the part that makes the causal spine **unassailable**. Today the
witnessed fork (`witness_engine.py` → content-addressed before/after world roots,
`single_variable_verified`, hash-chained occurrence log; `universe_forks.py`,
`witnessed_localization.py`) is used for one thing: single-variable localization. We are leaving
90% of its power on the table. The plan is to make the **entire instrument** a witnessed causal
tree — so every causal claim in the paper is a recomputable branch, not a correlation.

### 4.0 What a witnessed fork buys us (the property no static benchmark has)
A fork holds oracle-wrongness fixed and changes **exactly one** construction variable, and *proves
it*: the before-world root and after-world root are content-addressed, the "only this field
changed" invariant is machine-checked (`single_variable_verified`), and the event is appended to a
hash chain any third party recomputes offline. A correlational analysis can say "answers with
phrase X pass more often." Only a witnessed fork can say **"holding everything else provably fixed,
adding X *caused* this judge to flip"** — with a receipt. That is the causal-inference gold standard
(a controlled single-variable intervention) made reproducible and tamper-evident.

### 4.1 Branch A — Powered single-variable localization *(strengthen the existing leg)*
n=20/arm is why MATH lands at lift 0.005. Push to **≥200 items/arm**, replace the "exceeds
baseline" rule with a **bootstrap CI on the flip-rate difference**, and report the **full ranked
candidate table with intervals** rather than a single named winner. Either a variable emerges
(a named, witnessed cause) or diffuseness is confirmed *at power* — both are publishable, and both
sharpen the thesis. Pre-committed in §13.4's design correction.

### 4.2 Branch B — Interaction forks *(the diffuse defect has structure)*
The single-variable result says no *one* cue dominates. The obvious next question — and a genuinely
novel use of the machinery — is whether a **small set of interacting cues** does. Extend the
witness to a **two-variable fork**: change exactly cues {X, Y} together, `single_variable_verified`
generalized to "exactly these two fields changed," and measure **superadditivity** —
`flip(X,Y) − flip(X) − flip(Y)`. If deliberation-phrasing + verification-rhetoric flips a judge that
neither flips alone, the defect is a *witnessed interaction*, not diffuse noise. This directly
converts the paper's honest weak spot into a positive, mechanistic finding, and no prior judge-
hacking work has a witnessed interaction map.

### 4.3 Branch C — Dose-response ladders *(a causal curve, not a binary flip)*
Fork a single cue at increasing **intensity** (0, 1, 2, 3 favored phrases; hedging at escalating
strength) and witness the judge's pass-rate as a **monotone dose-response curve**. A monotone causal
curve under single-variable witnesses is a far stronger claim than a binary flip — it is the
epidemiologist's dose-response evidence for causation, applied to a grader. It also quantifies *how
much* rhetoric a scorer will tolerate before it capitulates, a number maintainers care about.

### 4.4 Branch D — The convergence loop **as** a witnessed universe tree *(the landmark move)*
Right now the whack-a-mole result is a *measurement*. We make it a **causally witnessed** one. Model
each patch as a fork on the **scorer-world**: parent scorer-root → child scorer-root, with the
witness certifying that the **only** thing that changed is the one rubric edit. Then the finding
"held-out exploit density is unchanged after the patch" is no longer a before/after comparison that
a reviewer can attribute to a confound — it is a single-variable causal intervention with a receipt:
*holding the entire scorer fixed except the one patched cue, exploitability on held-out cues did not
move.* The relocation is **caused** by the incompleteness of local patching, and the tree proves it.
The full attack→patch→re-attack history becomes a **content-addressed causal tree of evaluator
repair** — the object nobody in this literature has, and the one that most directly earns the phrase
"the first convergence measurement of evaluator repair."

### 4.5 Branch E — Transfer as sibling worlds *(the transfer matrix, witnessed)*
Fork **one** oracle-wrong answer into sibling worlds that differ only by the **judge**; witness that
the answer and everything else is byte-identical across siblings, only the scorer changed. The
adversary×judge transfer matrix (§13.6) becomes a witnessed causal object: each transfer cell is a
provable single-variable (judge-only) intervention, so "this exploit transfers / does not transfer"
is causal, not observational.

### 4.6 Branch F — Autoimmunity forks *(the cost of hardening, witnessed)*
When a patch lands, fork the **correct-answer** world across it and witness whether the patch flips a
genuine-correct verdict (the Δ⁻ autoimmunity cost). This makes the "hardening has a cost" claim a
witnessed causal quantity rather than a rate — and it is exactly the alignment-tax question
(does fixing the proxy break the real signal?) rendered reproducible.

### 4.7 The payoff artifact — the **Causal Atlas**
Publish the union of A–F as one navigable, recomputable object: **nodes are scorer/answer worlds,
edges are witnessed single-variable interventions, every root is content-addressed and every edge is
hash-chained.** A reviewer clones it and recomputes the entire causal structure offline, verifying
every edge's root — the way `verify_bundle` already verifies the frames, now for *causality*. This
is "Gradia Universes" realized inside a benchmark paper: the branched reality **is** the atlas of how
each scorer fails, why local patches relocate, and where the interacting cues live. It is also the
single most shareable object in the paper — a causal map you can walk.

> **Build status, honest.** The witness engine, single-variable forks, and localization (Branch A's
> substrate) are **built and running today**. Branches B–F are pre-committed Phase-2 extensions of
> the *same* engine — each is a new intervention shape over existing witnessed-fork primitives, not
> new trust machinery. We ship A powered for this paper; B–D as the headline Phase-2 program with at
> least one worked, witnessed exhibit each; E–F as they land. We will not claim a branch we have not
> witnessed end-to-end.

---

## 5. Bulletproofing checklist — every reviewer angle, and its closer

| A reviewer says… | Our closer | Where |
|---|---|---|
| "Your judge is a toy." | real claude-opus-5 headline numbers **+** real-judge rubric-edit convergence/transfer (R2) | §7.3, §13, R2 |
| "It's just prompt injection." | automated naturalness screen (100%) **+** blind human study | §13.7, R5 |
| "Single seed / noise." | item-clustered bootstrap CIs on every headline number | §13.5 |
| "Cherry-picked / small N." | 5 frontier benchmarks × ~200 + stratified SWE across 12 repos | §13.1, §4.7 |
| "Not novel vs Zhou 2026." | oracle witness + repair-convergence + witnessed causal tree + living index | §2, §7.3, §4.4 |
| "Your causal claim is underpowered." | **powered localization (R3) + witnessed interaction/dose-response forks** | §4.1–4.3 |
| "Before/after could be a confound." | **the convergence loop as a witnessed single-variable scorer intervention** | §4.4 |
| "Live SWE numbers are unreliable." | self-validation refuses to report unless controls behave | §8.4 |
| "Trust-me numbers." | frames + causal tree both recompute + verify offline | §8, §4.7 |

If a leg is soft, it is on this table with a scheduled closer. Nothing is left to hope.

---

## 6. The "keep sharing" layer (make it infrastructure, not a PDF)

- **Living Scorer Gameability Index** — published leaderboard on gradiahq.com; `uvx` one-liner;
  GitHub Action + gameability **badge** maintainers drop in their README; open card schema so it is a
  **protocol**, not a tool.
- **Responsible disclosure** — a content-addressed index card + oracle-witnessed examples + the
  repair-convergence result + a suggested structural defense, sent to HLE / SWE-bench maintainers
  before public release. Immune response, not exploit.
- **The Causal Atlas** (§4.7) — the walkable, recomputable causal map.
- **The naturalness rater packet** — 50–100 blinded exploit answers + a 1–5 plausibility instrument +
  the automated screen's verdict per item, so the "reward hacking, not injection" claim is human-
  backed. (Buildable now, no compute.)

---

## 7. Sequence

**Now (in flight / this session):** SWE live to completion; §13.4 folded (done); naturalness rater
packet built; Branch-A powering wired.

**This week:** R1 HumanEval re-run → R2 real-judge convergence/transfer → R3 powered localization →
R4 Regime-2 → `run_research.sh` fold → one worked witnessed exhibit each for Branches B, C, D.

**Pre-submission:** human ratings in; Causal Atlas published; disclosure packets sent; final
consistency pass; the "what's new vs Zhou" table tightened; abstract rewritten to lead with the
witnessed convergence result and the living index.

**The bar:** when a reader finishes the abstract they should already want to run the index on their
own benchmark, and when they finish §7 + §4.4 they should not be able to think about eval hardening
the old way again.
