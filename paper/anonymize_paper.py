#!/usr/bin/env python3
"""Produce the TMLR double-blind (anonymized) variant of the Wind Tunnel paper.
Deterministic + auditable: block rewrites for the program-relation prose, then an ordered
literal map, then a self-check that asserts no identifying token survives. Figures are
repointed to figures/anon/. Run: python paper/anonymize_paper.py
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "paper" / "WIND-TUNNEL-PAPER-FULL.md"
DST = ROOT / "paper" / "WIND-TUNNEL-PAPER-TMLR-anon.md"

t = SRC.read_text()

# ---- 1. author frontmatter → anonymous, with a double-blind banner ----
t = t.replace(
    'author: "Rudy M. Celekli, Gradia Research · gradiahq.com"',
    'author: "Anonymous Author(s) — under double-blind review"')

# insert a submission banner right after the frontmatter block (after the second '---')
banner = ("\n> **Submission note (TMLR, double-blind).** This is the anonymized variant of the\n"
          "> manuscript, prepared for double-blind review at *Transactions on Machine Learning\n"
          "> Research*. Author identity, the names of the authors' prior systems, and repository\n"
          "> URLs are withheld; citations to the authors' own prior work are marked *(withheld to\n"
          "> preserve anonymity)* and will be restored in the camera-ready. The accompanying code,\n"
          "> which reproduces every number and figure, is available to reviewers as an anonymized\n"
          "> supplement. No result or claim depends on the withheld names.\n")
# put banner after the first frontmatter close (the '---' that ends the YAML)
parts = t.split('\n---\n', 1)
t = parts[0] + '\n---\n' + banner + parts[1]

# ---- 2. block rewrites for the program-relation prose ----
BLOCKS = [
 # abstract closing pillars
 ("""This is the third
pillar of a program on verifiable evaluation, after Interruptible Universes (proving
*what happened*) and Gradia Guard (proving *the record was not tampered with*).""",
  """This is the third
pillar of a program on verifiable evaluation, after a prior interruptible-evaluation
benchmark (proving *what happened*) and a tamper-evident evidence runtime (proving *the
record was not tampered with*); citations to both are withheld to preserve anonymity."""),
 # 1.1
 ("""two of the three trusted components honest: *Interruptible Universes* proved that a
benchmark can verify **what happened** in a changing world, and *Gradia Guard* made the
runtime **record** tamper-evident and coverage-honest.""",
  """two of the three trusted components honest: a prior *interruptible-evaluation* work
(citation withheld) proved that a benchmark can verify **what happened** in a changing
world, and a prior *evidence-runtime* work (citation withheld) made the runtime **record**
tamper-evident and coverage-honest."""),
 # 1.4 whole block
 ("""### 1.4 Relation to prior work in this program

This is the third work in a program on verifiable evaluation. **Interruptible Universes**
contributed the witnessed, branchable universe we use here as a causal instrument;
**Gradia Guard** (gradiahq.com) contributed the tamper-evident evidence runtime that records
every experiment; and **Conditionally Approved** contributed both the proof-bound benchmark
methodology and the multi-judge instability finding (Fleiss' κ = 0.151) that motivates
attacking the scorer directly. Interruptible Universes and Conditionally Approved are
archived together (Zenodo DOI [10.5281/zenodo.22087020](https://doi.org/10.5281/zenodo.22087020));
Conditionally Approved is under review at ICLR 2027 (OpenReview `IrPdpUo7Rz`). We are grateful
to build on that foundation.""",
  """### 1.4 Relation to prior work in this program

This is the third work in a program on verifiable evaluation (all citations withheld to
preserve anonymity). A prior **interruptible-evaluation** work contributed the witnessed,
branchable world we use here as a causal instrument; a prior **evidence-runtime** work
contributed the tamper-evident receipts that record every experiment; and a prior
**proof-bound benchmark** work contributed both the proof-bound benchmark methodology and
the multi-judge instability finding (Fleiss' κ = 0.151) that motivates attacking the scorer
directly. The three prior works are the authors' own and will be cited in the
camera-ready."""),
 # the adversary panel line — keep it clean
 ("the Conditionally Approved panel:", "the frontier adversary panel:"),
]
for a, b in BLOCKS:
    if a not in t:
        print("WARN block not found:", a[:60].replace("\n"," "))
    t = t.replace(a, b)

# ---- 3. ordered literal map (longest / most specific first) ----
REPL = [
 ("Archived at Zenodo — DOI",      "Public record — citation"),
 ("gradia_universes World engine", "witnessed world-engine"),
 ("gradia_universes.World",        "WorldEngine.World"),
 ("`gradia_universes`",            "`world_engine`"),
 ("gradia_universes",              "the world engine"),
 ("gradia_stack_status",           "stack_status"),
 ("gradia_capability_demo",        "capability_demo"),
 ("gradia-wind-tunnel",            "windtunnel"),
 ("gradia-windtunnel",             "windtunnel"),
 ("gradiahq.com",                  "the project site (URL withheld for review)"),
 ("Gradia Guard",                  "the evidence runtime"),
 ("Gradia Research",               "(affiliation withheld)"),
 ("the Gradia stack",              "the world-engine stack"),
 ("the real Gradia engine",        "the real world engine"),
 ("on the Gradia engine",          "on the world engine"),
 ("the Gradia engine",             "the world engine"),
 ("Gradia engine",                 "world engine"),
 ("Gradia-*consistent*",           "engine-*consistent*"),
 ("Gradia-consistent",             "engine-consistent"),
 ("Gradia analytics",              "analytics"),
 ("Gradia canonical JSON",         "canonical JSON"),
 ("gradia canonical JSON",         "canonical JSON"),
 ("gradia fail-closed preregistration", "fail-closed preregistration"),
 ("gradia reserved-DOI",           "reserved-DOI"),
 ("Gradia is a general environment engine", "the engine is a general environment engine"),
 ("Gradia universes",              "world-engine universes"),
 ("Gradia tool",                   "engine component"),
 ("Interruptible Universes",       "the prior interruptible-evaluation work"),
 ("Conditionally Approved",        "the prior proof-bound benchmark work"),
 ("Guard-routed",                  "gateway-routed"),
 ("Guard-instrumented",            "gateway-instrumented"),
 ("Guard's credentialless gateway","the credentialless gateway"),
 ("Guard's central guarantee",     "the gateway's central guarantee"),
 ("Guard gateway",                 "credentialless gateway"),
 ("Guard/CA",                      "the prior works"),
 ("through Guard's",               "through the"),
 ("exercise of Guard's",           "exercise of the gateway's"),
 ("Guard's",                       "the gateway's"),
 # figures → anon set
 ("](figures/fig",                 "](figures/anon/fig"),
]
for a, b in REPL:
    t = t.replace(a, b)

# ---- 4. regex catch-alls for any straggler whole-word names ----
t = re.sub(r"\bGuard\b", "the evidence runtime", t)
t = re.sub(r"\bgradia\b", "the engine", t, flags=re.I)
# safety net: strip any self-identifying DOI / OpenReview id that survived a block edit
t = re.sub(r"\[?10\.5281/zenodo\.\d+\]?(\(https?://doi\.org/10\.5281/zenodo\.\d+\))?",
           "[citation withheld for review]", t)
t = t.replace("IrPdpUo7Rz", "[withheld]")
# strip the identity-bearing code-repository URL (markdown-link or bare form)
t = re.sub(r"\[?github\.com/rudycelekli/[^\]\s)]*\]?(\(https?://github\.com/rudycelekli/[^)]*\))?",
           "[repository withheld for review]", t)
t = re.sub(r"https?://github\.com/rudycelekli/\S*", "[repository withheld for review]", t)

DST.write_text(t)

# ---- 5. self-check: no identifying token may survive ----
BAD = ["Gradia", "gradia", "Celekli", "Rudy", "Interruptible Universes",
       "Conditionally Approved", "gradiahq", "rudycelekli", "Gradia Guard", " Guard",
       "Zenodo", "zenodo", "IrPdpUo7Rz", "doi.org"]
leftovers = []
for tok in BAD:
    for i, line in enumerate(t.splitlines(), 1):
        if tok in line:
            leftovers.append((tok, i, line.strip()[:90]))
if leftovers:
    print("LEFTOVERS FOUND:")
    for tok, i, s in leftovers[:40]:
        print(f"  [{tok!r}] L{i}: {s}")
    sys.exit(1)
print(f"OK — anonymized paper written to {DST.name} ({len(t)} bytes); no identifying token remains.")
