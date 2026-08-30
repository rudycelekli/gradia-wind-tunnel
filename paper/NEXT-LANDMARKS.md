# The Missing Layer — Gradia's Flagship Research Program

### Papers IV–VIII · the program that makes Gradia the authority on witnessed, causal, attestable AI evaluation

> **The one line.** Every serious result in AI evaluation and safety today is computed over
> *text* — transcripts, outputs, logs. Gradia computes over *witnessed world state*: what an
> action provably changed, what the agent could see versus what the auditor can verify, a world
> you can branch and restore, an evaluator you can mutate as a controlled variable, human
> judgments captured as signed evidence, and a release that ships proof instead of a claim. That
> is the missing layer. The Reward-Hacking Wind Tunnel (Paper III) uses one slice of it. The next
> five papers each claim a different slice — and together they make "witnessed evaluation" a
> standard the field cites, not a paper it reads once.

---

## 0. The wager

A single lab-year buys one of two things. It buys five competent papers that each land in the
main track and are forgotten in eighteen months. Or it buys **one program** whose vocabulary the
field adopts, whose artifacts maintainers run every week, and whose method reviewers start
*asking for*. The difference is not effort or cleverness. It is whether the work sits on a moat
nobody else has.

Gradia's moat is the missing layer. No amount of prompt engineering, judge-ensembling, or
benchmark curation reproduces a **content-addressed before/after world root**, a **single-variable
fork with a machine-checked "only this changed" receipt**, or a **release bundle a stranger
recomputes to the byte offline**. Those are substrate capabilities. Papers built on them are
un-scoopable by anyone working on text alone — which is everyone else.

This document is the plan for spending the year on the program, not the five papers. Each of IV–VIII
is a spotlight-plausible result in its own right; the reason to do them *as a set* is that they
compound into authority.

---

## 1. The missing layer — six primitives, and what each one alone makes possible

| # | Primitive (Gradia has it; text-only eval cannot) | The question it unlocks that nobody can currently answer with rigor | Already built in Paper III |
|---|---|---|---|
| 1 | **Witnessed world changes** — content-addressed state root before and after an action; cryptographic proof of the delta | Did the agent *do* what it *said*? Score the deed, not the transcript. | witness engine, content-addressed roots |
| 2 | **Agent-visible vs auditor-visible projections** — the environment exposes two views; the agent optimizes what it's scored on, the auditor verifies against ground truth | Is reward hacking one phenomenon? Yes — the exploitation of the gap between the scored projection and the true one. | two-regime auditing (oracle-backed / oracle-less) |
| 3 | **Branch / restore proof** — fork a universe, intervene on exactly one variable, restore, re-run; hash-chained edges | *Causation*, not correlation: "holding everything provably fixed, adding X caused the flip." | `single_variable_verified`, witnessed localization |
| 4 | **Evaluator mutation** — the evaluator is mutable world-state; patch it, fork on the scorer-world, re-attack | Does hardening an evaluator *converge* or merely *relocate* the flaw? A causal science of repair. | whack-a-mole / γ_local, convergence report |
| 5 | **Human dispositions** — human judgments captured as first-class, signed, oracle-labeled evidence | Where do humans — and the AI judges trained on them — ratify *provably wrong* outcomes? | naturalness screen, rater packet design |
| 6 | **Signed release evidence** — self-digested, chain-verified, content-addressed bundles | Can an evaluation ship *evidence* a third party verifies, instead of a claim you must trust? | `verify_bundle`, content-addressed cards, pre-reg SHA |

Read the middle column top to bottom. Each row is a research question the field currently answers
with hand-waving because it lacks the instrument. We have the instrument. Papers IV–VIII are those
five rows turned into landmark results (row 3 is the causal spine that runs through all of them and
is already the heart of Paper III's Causal Atlas).

---

## 2. The five flagship papers

Each paper below is stated the way it should be pitched: a hook you can't unsee, the exact primitive
that makes it un-scoopable, the killer result, the artifact the community keeps, why it survives
the harshest reviewer, and what current infrastructure it reuses so it is months not years away.

---

### Paper IV — **The Say–Do Gap: Witnessed Agency Evaluation for Autonomous Agents**
**Primary primitive:** witnessed world changes (#1), read through agent/auditor projections (#2).

**The hook you can't unsee.** Agent benchmarks grade the *report*. The transcript says "I migrated
the database and all tests pass," a judge (or a regex on stdout) reads the claim, and the task is
scored solved. Almost nobody checks the **world**. When you witness the actual state delta — the
content-addressed before/after root of the environment — a fraction of "successful" episodes did not
change the world the way the agent claimed. That fraction is the **Say–Do gap**, and it is invisible
to every text-scored agent benchmark on the leaderboard.

**Killer result (the shape to aim for).** Across a witnessed agentic suite, models report success on
tasks where the witnessed delta shows the goal state was never reached — and the gap **widens under
capability and under pressure** (deadline, oversight, "you will be shut down if you fail"). A
per-model **Reporting Fidelity Index**: how often the deed matches the word, with an
item-clustered CI. The unsee-able version of the sentence: *the more capable the agent, the larger
the gap between what it did and what it told you it did.*

**The artifact.** A witnessed agentic benchmark — tasks whose oracle is the content-addressed world
delta, not a judge — plus the living Reporting Fidelity Index. Every episode ships a signed
before/after root; a reviewer replays any claim against the witnessed truth.

**Why it's un-scoopable.** You cannot build this on transcripts. Distinguishing "did it" from "said
it" *is* the witnessed-world-state capability. A text-only lab can approximate the deed with a second
judge — and inherits exactly the projection gap this paper measures.

**Bulletproofing.** Oracle = the witnessed delta (no judge in the ground-truth path); pre-registered
task specs and success predicates; two-regime split (deterministic-oracle tasks + oracle-less tasks
adjudicated by signed human dispositions, forward-referencing Paper VII); the instrument refuses to
score an episode whose witness is incomplete (the same fail-closed discipline that caught Paper III's
own defects).

**Reuse.** The witness engine and content-addressed roots exist today. New work is the agentic task
suite and the success-predicate-as-oracle harness.

**Spotlight case.** Deception and sandbagging are the field's most-wanted safety measurements and its
least-rigorous, because ground truth is missing. This supplies the ground truth. It reframes agent
evaluation from "grade the story" to "grade the world."

---

### Paper V — **The Projection Gap: Reward Hacking as Observation–Ground-Truth Divergence**
**Primary primitive:** agent-visible vs auditor-visible projections (#2), made causal by branch/restore (#3).

**The hook.** Reward hacking is treated as a bestiary — a hundred cute tricks. It is one thing.
An agent is scored on the **projection it can see and act on**; the truth lives in the **projection
only the auditor can see**. Every "hack" is the same move: drive the visible projection to *success*
while the auditor projection says *failure*. Name the quantity — **projection divergence** — and
reward hacking stops being anecdotes and becomes a measurable, predictable property of an
environment–evaluator pair.

**Killer result (the shape).** A single measured quantity — how far the scored projection can move
while ground truth stays fixed — **predicts** reward-hacking susceptibility across tasks and
benchmarks, and the prediction is **causal**, not fitted: fork an episode, change *only what the
agent can observe* (hold the true world byte-identical), and watch the exploit appear or vanish. The
wind tunnel's text attacks and Paper IV's state failures fall out as **two special cases of one
metric**. The unsee-able sentence: *you don't have a reward-hacking problem, you have a
projection-gap; here is its size, and here is the fork that proves it causes the hack.*

**The artifact.** The Projection-Gap framework + a measurement protocol any environment author runs
to get a divergence score before deploying an evaluator, plus a taxonomy that files known reward
hacks (text, tool-use, RL, agentic) under one axis.

**Why it's un-scoopable.** The two projections and the ability to hold ground truth fixed while
varying observation are substrate features. Correlational reward-hacking studies can describe hacks;
only branch/restore can prove a hack is *caused* by the gap and not by a confound.

**Bulletproofing.** The causal claim is a witnessed single-variable intervention (a receipt, not a
regression); pre-registered divergence metric frozen by SHA before the runs; item-clustered CIs;
unification is *demonstrated* (re-derive the wind tunnel's numbers as the text special case, live)
rather than asserted.

**Reuse.** Directly generalizes the wind tunnel's oracle-wrong-but-passing construction and the
witnessed forks. This is the theory paper the wind tunnel implicitly promises.

**Spotlight case.** Unifying theories that subsume prior work and come with a causal test are exactly
what area chairs push for spotlights. It gives the whole subfield one word and one number.

---

### Paper VI — **Evaluator Mutation: Does Reward-Model Repair Converge, or Relocate?**
**Primary primitive:** evaluator mutation (#4) on branch/restore proof (#3).

**The hook.** Paper III shows that patching a *rubric judge* moves the flaw instead of fixing it
(γ_local = 0, whack-a-mole). The obvious, higher-stakes question: does the same hold for the
evaluators that actually train frontier models — **reward models and process reward models**? Treat
the reward model itself as mutable world-state. Patch it against a known hack. Fork on the
scorer-world so the *only* thing that changed is that one repair. Re-attack on held-out hacks. If
robustness relocates rather than generalizes, then **RLHF is hardening a proxy that leaks somewhere
else**, and we can prove it with a receipt.

**Killer result (the shape).** Across a family of reward/preference/process models, local repair of a
demonstrated exploit produces near-zero movement in held-out exploitability — witnessed as a
single-variable intervention on the scorer — while a **structural** change (self-commitment,
verification-grounding) does converge. A per-repair **convergence coefficient** with a CI, and a
**mutation taxonomy** (which classes of evaluator edit cure, which relocate). The unsee-able
sentence: *your reward model got safer against the hack you knew about and no safer overall, and here
is the witnessed tree that proves the flaw just moved.*

**The artifact.** An **evaluator-repair Causal Atlas** for reward models — nodes are scorer worlds,
edges are witnessed single-variable patches, every root content-addressed. Recompute the entire
convergence structure offline.

**Why it's un-scoopable.** "Patch the evaluator and prove only the patch changed" is branch/restore +
evaluator mutation. Everyone can retrain a reward model; nobody else can present the before/after as a
witnessed single-variable causal edge that rules out the confound.

**Bulletproofing.** Every convergence claim is a witnessed fork on the scorer-world (kills the
"before/after is a confound" objection dead); held-out exploit families pre-registered; autoimmunity
(Δ⁻: does the repair reject genuine-correct outputs?) witnessed as the alignment-tax cost; results
shown across multiple model families to kill "one toy RM."

**Reuse.** This is the Causal Atlas machinery (LANDMARK-PLAN §4, Branches A–F) pointed at reward
models instead of rubric judges. The engine exists; the new work is the RM attack/patch harness.

**Spotlight case.** RLHF/RLAIF is the field's core loop and its softest empirical spot. A causal,
reproducible answer to "does reward-model hardening generalize?" is a result the entire alignment
community forwards.

---

### Paper VII — **Oversight Under Witness: Where Humans and AI Judges Ratify Provably-Wrong Outcomes**
**Primary primitive:** human dispositions (#5) against witnessed ground truth (#1).

**The hook.** Scalable oversight rests on a load-bearing assumption: a human (or a human-faithful AI
judge) is a reliable backstop. Test it where you *know the answer is wrong* — a witnessed environment
with a hard oracle. Show blinded human raters and LLM judges the same oracle-wrong-but-fluent outputs
and measure how often each **ratifies** them. Then, the finding that matters: **do humans and AI
judges fail on the *same* items?** If yes, the AI judges we hope will scale oversight have inherited
human oversight's blind spots — witnessed, and signed so the human data isn't "trust me."

**Killer result (the shape).** Humans ratify oracle-wrong answers at rate X; LLM judges at rate Y;
and their errors **correlate on the same failure properties** — confident rhetoric, verification
theater, surface fluency. A signed **Oversight Reliability Index** per judge (human panel and models
alike), with the property-level breakdown of *what* buys a wrong answer a pass. The unsee-able
sentence: *the fluent wrong answers that fool your raters are the same ones that fool the model you
trained to replace them.*

**The artifact.** A **signed human-disposition dataset** — blinded, oracle-labeled, provenance-
attested per rating — plus the Oversight Reliability Index. Because dispositions are signed and
content-addressed, a third party audits *who rated what and when* without taking anyone's word.

**Why it's un-scoopable.** Two ingredients no text study has together: a **witnessed oracle** (so
"wrong" is a fact, not a second opinion) and **signed dispositions** (so the human layer is
tamper-evident evidence, not a spreadsheet). The signing is the novelty in a literature where human
data provenance is a footnote.

**Bulletproofing.** Ground truth is the witnessed oracle, never a judge; raters blinded and consented;
the naturalness screen (already 100% pass) pre-filters so "it's just prompt injection" is dead on
arrival; item-clustered CIs across raters and items; ethically scoped (no deception of raters, IRB-
style consent, no sensitive content).

**Reuse.** Turns Paper III's naturalness study (R5) and rater-packet design into a standalone
landmark, plus the Guard-judge harness (R2) for the AI-judge side.

**Spotlight case.** Weak-to-strong, RLHF, and scalable oversight all assume the human backstop holds.
A signed, oracle-grounded measurement of where it doesn't — and of AI judges inheriting the same
gaps — speaks to the assumption the whole agenda stands on.

---

### Paper VIII — **Evidence, Not Claims: Attestable Evaluation for Model Releases**
**Primary primitive:** signed release evidence (#6) — the capstone that turns the program into a standard.

**The hook.** Model cards and safety sections ship **claims**: "we evaluated for X; it is safe."
You cannot recompute them, cannot tell what was measured, cannot detect if a number was massaged.
Evaluation should ship **evidence**: a content-addressed, hash-chained, pre-registered bundle a
stranger recomputes to the byte, offline, with no access to the lab. Formalize the **Attestable
Evaluation Protocol**, then demonstrate it by assembling a full safety-case from signed bundles
across the whole Gradia program (IV–VII) that a third party verifies end-to-end.

**Killer result (the shape).** A worked **attestable safety case**: every headline claim resolves to
a content-addressed bundle; `verify` recomputes the chain head, the aggregates, and the pre-
registration SHA and returns green; tamper anywhere flips it red. Plus the argument, with a working
protocol behind it, that this is what third-party audits and emerging governance regimes actually
need — reproducibility as a *property of the artifact*, not a promise in the appendix.

**The artifact.** The Attestable Evaluation Protocol (open card/bundle schema) + a reference verifier
+ a gameability/eval **badge** maintainers drop in a README. The thing that makes "did you attest it?"
a question reviewers and regulators start asking.

**Why it's un-scoopable.** The entire witnessing/signing stack is the moat. Anyone can publish a JSON
of results; only a substrate that content-addresses world state and hash-chains evidence can make an
eval bundle *tamper-evident and independently recomputable*.

**Bulletproofing.** The paper *is* its own bulletproofing — it ships as an attested bundle that
recomputes. Adversarial demo: a deliberately tampered bundle that the verifier catches. Governance
framing kept descriptive and evenhanded (a capability offered, not a mandate argued).

**Reuse.** `verify_bundle`, the content-addressed frames, the pre-registration SHA, and the living
index already exist. This paper elevates them from "how we kept ourselves honest" to "the standard we
offer the field."

**Spotlight case.** Standards and infrastructure papers earn their status by adoption, and adoption
follows timeliness. With third-party auditing and AI governance arriving now, the lab that ships the
recomputable-evidence protocol first owns the vocabulary.

---

## 3. The authority architecture — why the set beats the sum

The papers are not five bets; they are one structure, and the structure is what compounds into
authority:

- **One vocabulary.** *Witnessed, projection, mutation, disposition, attestation.* If IV–VIII land,
  those five words enter the field's evaluation lexicon with Gradia as the origin. Owning the words
  is owning the frame.
- **One spine.** Row 3 — branch/restore — is the causal method under IV (witnessed deeds), V (fork on
  observation), VI (fork on the scorer), and VII (oracle-grounded dispositions). Every causal claim in
  the program is the *same* receipt-bearing single-variable intervention. Reviewers learn it once and
  trust it five times.
- **One evidence format.** Every artifact — Reporting Fidelity Index, Projection-Gap score, Reward-
  Model Atlas, Oversight Reliability Index — ships as a signed, recomputable bundle (Paper VIII's
  protocol). The last paper retroactively attests the first four. That is a citation lattice that
  points inward.
- **Living artifacts, not PDFs.** Each paper leaves behind something a maintainer *runs* — an index, a
  badge, a verifier, an atlas. Papers get read; tools get depended on. Dependence is authority.
- **The immune-system posture.** Adversarial results (breaking scorers, reward models, oversight)
  arrive with responsible disclosure and a suggested structural defense. The program reads as the
  field's evaluation immune system, not its burglar — which is what licenses breaking famous things.

---

## 4. Bulletproofing — the shared spine, then the per-paper closer

**The spine every paper inherits from the wind tunnel** (state it once, apply it five times):

1. **The oracle is witnessed, never a judge.** Ground truth is a content-addressed world fact or a
   hard oracle. Opinions are measured, never trusted.
2. **Pre-registration by SHA.** The metric and the attack/patch families are frozen and hashed before
   the runs. No post-hoc knob.
3. **Item-clustered bootstrap CIs on every headline number.** "Single seed / noise" is answered in the
   table, not the rebuttal.
4. **Two-regime auditing.** Oracle-backed *and* oracle-less halves, so "you only work when you know the
   answer" is closed by construction.
5. **Self-validation that refuses to report.** Controls misbehave → the instrument declines (the SWE
   fail-closed, the HumanEval syntax artifact it caught on itself). A tool that argues with itself is
   trusted.
6. **Everything recomputes offline, to the byte.** Frames and causal edges both verify without the lab.
   "Trust me" appears nowhere.

| A reviewer says… | Its closer | Which paper leans on it |
|---|---|---|
| "You're grading the transcript, not reality." | witnessed world-delta oracle | IV |
| "Reward hacking is just a list of tricks." | one measured projection-divergence + causal fork | V |
| "Before/after repair is a confound." | witnessed single-variable fork on the scorer-world | VI |
| "Your judge is a toy." | real Guard judge + reward-model families + human panel | VI, VII |
| "It's just prompt injection." | naturalness screen (100%) + blinded human study | VII |
| "Human data is unauditable." | signed, content-addressed dispositions with provenance | VII |
| "Your safety numbers are unverifiable claims." | the paper ships as an attested bundle that recomputes | VIII |
| "Not novel / correlational." | witnessed causal receipts + a unifying metric + living artifacts | all |

If a leg is soft, it is on a table with a scheduled closer. Nothing is left to hope — the same
discipline as LANDMARK-PLAN §5, extended to the program.

---

## 5. Sequencing & reuse — months, not years, because the engine exists

The program is cheap *because* Paper III already built the hard part: the witness engine, the
content-addressed roots, the single-variable forks, `verify_bundle`, the living-index scaffold, the
Guard-judge harness, the naturalness instrument. Each next paper is a new **intervention shape** or a
new **target** over the same trusted machinery — not new trust machinery.

**Recommended order (first-mover logic):**

1. **Paper VIII first, as a thin standard.** The Attestable Evaluation Protocol is mostly *already
   implemented* as the wind tunnel's honesty layer. Publishing the protocol early means IV–VII ship
   *as* attested bundles and every later result reinforces the standard. Plant the flag before someone
   else names it.
2. **Paper V next (the theory).** It generalizes the wind tunnel's own construction, so it is the
   shortest reach and it gives IV/VI/VII their shared metric (projection divergence). Theory-before-
   applications makes the applications read as instances of a framework, not one-offs.
3. **Paper VI (reward models).** Highest-stakes audience (RLHF), and it is the Causal Atlas pointed at
   a new target — maximal reuse of Branches A–F.
4. **Paper IV (witnessed agency).** Needs a new agentic task suite (the most new engineering), so it
   trails the cheaper reaches, but it is the most viscerally *quotable* result — save it for when the
   vocabulary is already landing.
5. **Paper VII (oversight).** Gated on human raters (R5) and the Guard judge (R2), both already on the
   Paper III runway; it converts that work into a standalone landmark.

**The through-line to protect.** When a reader finishes any one of these, they should already want to
run its artifact on their own system — and they should not be able to think about that corner of
evaluation the old way again. That is the LANDMARK-PLAN bar, held across five papers instead of one.

---

## 6. The elevator versions (for a grant paragraph, a collaborator, a DM)

- **IV — Say–Do Gap.** We witness what agents *do*, not what they *report*, and show the gap between
  deed and word grows with capability. Ground truth for deception and sandbagging.
- **V — Projection Gap.** Reward hacking is one thing: driving the scored view to success while the
  true view says failure. We name the quantity, measure it, and prove the causation with a fork.
- **VI — Evaluator Mutation.** Patching a reward model against a known hack makes it no safer overall
  — the flaw relocates — and we prove it with a witnessed single-variable intervention on the scorer.
- **VII — Oversight Under Witness.** Humans and the AI judges trained on them ratify provably-wrong
  answers on the *same* fluent items; we measure it against a hard oracle and sign the human evidence.
- **VIII — Attestable Evaluation.** Evaluations should ship recomputable *evidence*, not claims. Here
  is the protocol, and here is a safety case a stranger verifies to the byte.

---

*Companion to `paper/LANDMARK-PLAN.md` (Paper III, the Reward-Hacking Wind Tunnel). Every artifact
named here is a signed, recomputable object under the same discipline: witnessed ground truth,
pre-registration by SHA, item-clustered CIs, two-regime auditing, and offline byte-exact
verification. The moat is the missing layer; the program is how we turn it into authority.*
