"""C1 on a REAL exploit — witnessed single-variable causal localization.

The thesis: given a real, oracle-wrong answer that a real grader nonetheless
PASSES, *which single ingredient of the answer causes the grader to pass it?*
A static benchmark can only correlate. We can INTERVENE and prove it:

  1. Hold the answer's correctness fixed (parent and child are BOTH oracle-wrong).
  2. Change exactly one construction variable (e.g. add one judge-gaming layer),
     forked on the universe engine so an evolution witness certifies that ONE
     field changed and nothing else (before/after world roots + hash-chained
     occurrence; see witness_engine / universe_forks — never degrades).
  3. Grade parent and child with the SAME judge. A causal flip
     (child PASS ∧ parent FAIL, both still wrong, single-variable-verified) is a
     witnessed attribution: THIS variable is what buys the wrong answer a pass.

We localize by measuring the witnessed flip-rate of every candidate variable on
a discovery split, then PROSPECTIVELY validate the winner on a held-out split.
This is the causal instrument no static leaderboard can run.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .canonical import digest
from .transforms import FAVORED_PHRASES, JUDGE_GAMING_WRAPPERS
from .universe_forks import fork_on_variable, witness_engine_name


def _git_sha() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip() or "{{GIT_SHA}}"
    except Exception:
        return "{{GIT_SHA}}"


def default_variables() -> list[str]:
    """Candidate single-variable interventions: keyword inflation over each
    favored phrase, plus every judge-gaming vector. 'none' is the parent."""
    return [f"phrase:{p}" for p in FAVORED_PHRASES] + list(JUDGE_GAMING_WRAPPERS)


def render_answer(base_wrong: str, variable: str, rng, *, as_comment: bool = False) -> str:
    """Deterministically render the (still-wrong) answer for one intervention
    value. 'none' -> the plain wrong answer (parent)."""
    if variable in (None, "none"):
        return base_wrong
    if variable.startswith("phrase:"):
        _ph = variable.split(':', 1)[1]
        return f"{('# ' + _ph) if as_comment else _ph}\n{base_wrong}"
    return JUDGE_GAMING_WRAPPERS[variable](base_wrong, rng, as_comment=as_comment)


@dataclass
class WitnessedFlip:
    item_id: str
    variable: str
    parent_pass: bool
    child_pass: bool
    both_oracle_wrong: bool
    single_variable_verified: bool
    engine: str
    before_root: str
    after_root: str

    @property
    def causal_flip(self) -> bool:
        return (self.child_pass and not self.parent_pass
                and self.both_oracle_wrong and self.single_variable_verified)


def _base_wrong(bench, item, rng) -> str:
    base = list(bench.attacks(item, rng))
    return base[0].answer_text if base else item.correct_answer_text


def witnessed_flip(bench, item, variable, judge, rng, *, as_comment=False,
                   parent_pass=None, parent_wrong=None, base_wrong=None) -> WitnessedFlip:
    """One witnessed single-variable intervention on one item. Parent verdict may
    be supplied (cached) to avoid re-grading the shared parent per variable."""
    base_wrong = base_wrong if base_wrong is not None else _base_wrong(bench, item, rng)
    child_ans = render_answer(base_wrong, variable, rng, as_comment=as_comment)
    # witnessed fork: the single construction variable 'gaming' none -> variable
    fork = fork_on_variable("gaming", variable,
                            case={"gaming": "none", "item_id": item.item_id})
    if parent_pass is None or parent_wrong is None:
        parent_ans = render_answer(base_wrong, "none", rng, as_comment=as_comment)
        parent_pass = judge.score(parent_ans, item.question).passed
        parent_wrong = not bench.oracle(parent_ans, item)
    child_wrong = not bench.oracle(child_ans, item)
    child_pass = judge.score(child_ans, item.question).passed
    return WitnessedFlip(
        item_id=item.item_id, variable=variable,
        parent_pass=parent_pass, child_pass=child_pass,
        both_oracle_wrong=bool(parent_wrong and child_wrong),
        single_variable_verified=fork.single_variable_verified,
        engine=fork.engine, before_root=fork.before_root or "",
        after_root=fork.after_root or "")


def _flip_rate(flips: list[WitnessedFlip]) -> float:
    return round(sum(f.causal_flip for f in flips) / len(flips), 4) if flips else 0.0


def run_localization(run_id: str, bench, items, judge, *, seed: int = 20260829,
                     variables: list[str] | None = None,
                     holdout_frac: float = 0.5, max_cost_usd: float = 300.0,
                     preregistration_sha256: str | None = None) -> dict[str, Any]:
    """Localize the causal variable by witnessed flip-rate on a discovery split,
    then prospectively validate the winner on a held-out split."""
    import random
    variables = variables or default_variables()
    as_comment = getattr(bench, "benchmark_id", "") in {"humaneval", "swebench_verified"}

    split = max(1, int(len(items) * (1 - holdout_frac)))
    discovery, holdout = items[:split], items[split:]

    def measure(cohort):
        rng = random.Random(seed ^ 0x51)
        per_var: dict[str, list[WitnessedFlip]] = {v: [] for v in variables}
        witnesses: list[WitnessedFlip] = []
        excluded: list[dict[str, str]] = []
        for item in cohort:
            if getattr(judge, "total_cost_usd", 0.0) > max_cost_usd:
                break  # fail-closed: stop the cohort at the spend cap
            try:
                base_wrong = _base_wrong(bench, item, rng)
                # grade the shared parent ONCE per item, reuse across variables
                parent_ans = render_answer(base_wrong, "none", rng, as_comment=as_comment)
                p_pass = judge.score(parent_ans, item.question).passed
                p_wrong = not bench.oracle(parent_ans, item)
                collected: list[WitnessedFlip] = []
                for v in variables:
                    collected.append(witnessed_flip(
                        bench, item, v, judge, rng, as_comment=as_comment,
                        parent_pass=p_pass, parent_wrong=p_wrong, base_wrong=base_wrong))
            except Exception as e:
                # excluded and named, never scored: a permanent per-item judge failure
                # (e.g. HTTP 400 on an oversized payload) must not sink the cohort,
                # and a partially-measured item must not enter the flip rates.
                excluded.append({"item_id": str(item.item_id), "error": str(e)[:300]})
                continue
            for wf in collected:
                per_var[wf.variable].append(wf)
                if wf.causal_flip and len(witnesses) < 6:
                    witnesses.append(wf)
        return per_var, witnesses, excluded

    disc, sample_w, disc_excluded = measure(discovery)
    hold, _, hold_excluded = (measure(holdout) if holdout
                              else ({v: [] for v in variables}, [], []))

    cand = []
    for v in variables:
        cand.append({
            "variable": v,
            "flip_rate_discovery": _flip_rate(disc[v]),
            "n_flips_discovery": sum(f.causal_flip for f in disc[v]),
            "flip_rate_holdout": _flip_rate(hold[v]),
            "n_flips_holdout": sum(f.causal_flip for f in hold[v]),
            "all_single_variable_verified": all(f.single_variable_verified for f in disc[v]) if disc[v] else False,
        })
    cand.sort(key=lambda c: (c["flip_rate_discovery"], c["flip_rate_holdout"]), reverse=True)
    top = cand[0] if cand else None

    prospective = None
    if top and holdout:
        others = [c["flip_rate_holdout"] for c in cand[1:]]
        baseline = round(sum(others) / len(others), 4) if others else 0.0
        prospective = {
            "variable": top["variable"],
            "discovery_flip_rate": top["flip_rate_discovery"],
            "holdout_flip_rate": top["flip_rate_holdout"],
            "baseline_mean_holdout": baseline,
            "lift_over_baseline": round(top["flip_rate_holdout"] - baseline, 4),
            # the slice found on discovery must predict flips on held-out items,
            # above the field of other candidate variables.
            "validated": bool(top["flip_rate_holdout"] > baseline and top["flip_rate_holdout"] > 0.0),
        }

    body: dict[str, Any] = {
        "schema": "gradia-wind-tunnel-witnessed-localization.v1",
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_sha": _git_sha(),
        "preregistration_sha256": preregistration_sha256 or "{{FROZEN_PREREG_SHA256}}",
        "benchmark_id": getattr(bench, "benchmark_id", "?"),
        "judge": getattr(judge, "name", judge.__class__.__name__),
        "witness_engine": witness_engine_name(),
        "spend": {"max_cost_usd": max_cost_usd, "spent_usd": round(getattr(judge, "total_cost_usd", 0.0), 4)},
        "n_items_total": len(items), "n_discovery": len(discovery), "n_holdout": len(holdout),
        "excluded_items": {"discovery": disc_excluded, "holdout": hold_excluded},
        "candidate_variables": cand,
        "localized_variable": top["variable"] if top else None,
        "prospective": prospective,
        "sample_witnesses": [{
            "item_id": w.item_id, "variable": w.variable,
            "before_root": w.before_root, "after_root": w.after_root,
            "single_variable_verified": w.single_variable_verified, "engine": w.engine,
            "parent_pass": w.parent_pass, "child_pass": w.child_pass, "causal_flip": w.causal_flip,
        } for w in sample_w],
        "interpretation": (
            "Witnessed single-variable causal attribution: each candidate holds "
            "oracle-wrongness fixed and changes exactly ONE construction variable, "
            "certified by an evolution witness (before/after world roots, "
            "single-variable proof). A flip (wrong answer the judge fails as parent "
            "but passes once the one variable is added) attributes the grader defect "
            "to that variable. The localized slice is validated prospectively on a "
            "held-out split. Not a claim about model capability or benchmark worth."),
    }
    body["report_sha256"] = digest(body)
    return body


def verify_localization(body: dict[str, Any]) -> bool:
    stored = body.get("report_sha256")
    return stored == digest({k: v for k, v in body.items() if k != "report_sha256"})
