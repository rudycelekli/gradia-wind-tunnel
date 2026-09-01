"""Causal-slice localization (C1) — the moat.

On procedurally generated items every factor is controlled exactly, so a slice
cell is a TRUE factorial cell and a density difference across cells is an
interaction effect, not a correlation. We (1) find the minimal factor
conjunction that maximizes exploit density, then (2) validate it prospectively:
generate a fresh held-out cohort in the predicted slice and show the predicted
exploit rate materializes above a broad-slice baseline and a random-slice
control. A named slice is a prediction; prospective lift is its test.

In the full study the same procedure runs over witnessed-universe forks, where
the evolution witness certifies the single-variable intervention changed nothing
else — the version no static benchmark can do.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import combinations

from .items import Item, generate_item, oracle
from .judges import Judge
from .transforms import t_keyword_inflation
from .windtunnel import Episode, exploit_density


@dataclass
class CausalSlice:
    conjunction: dict            # {factor: value}
    density_in: float            # exploit density inside the slice (per 1000)
    density_out: float           # exploit density outside the slice
    prospective_density: float = 0.0
    broad_baseline_density: float = 0.0
    random_baseline_density: float = 0.0
    lift_over_broad: float = 0.0
    lift_over_random: float = 0.0
    validated: bool = False


def _cell_key(ep: Episode, keys: tuple[str, ...]):
    return tuple(ep.factors[k] for k in keys)


def localize(episodes: list[Episode], factor_keys=("steps", "large_operands", "distractor"),
             max_order: int = 2) -> CausalSlice | None:
    """Greedy minimal conjunction (up to `max_order` factors) maximizing the
    in-slice exploit density while keeping the slice non-trivial."""
    exploit_eps = [e for e in episodes if e.oracle_wrong]  # attempts that could exploit
    if not exploit_eps:
        return None

    best: CausalSlice | None = None
    for order in range(1, max_order + 1):
        for keys in combinations(factor_keys, order):
            values = {tuple(v) for v in ([_cell_key(e, keys) for e in exploit_eps])}
            for val in values:
                inside = [e for e in exploit_eps if _cell_key(e, keys) == val]
                outside = [e for e in exploit_eps if _cell_key(e, keys) != val]
                if not inside or not outside:
                    continue
                d_in, d_out = exploit_density(inside), exploit_density(outside)
                cand = CausalSlice(
                    conjunction=dict(zip(keys, val)),
                    density_in=round(d_in, 1), density_out=round(d_out, 1),
                )
                # prefer the largest in/out gap; break ties toward fewer factors
                if best is None or (d_in - d_out, -order) > (best.density_in - best.density_out, -len(best.conjunction)):
                    best = cand
    return best


def _attack_and_measure(items: list[Item], judge: Judge, seed: int) -> float:
    """Exploit density of keyword_inflation on a held-out item set."""
    rng = random.Random(seed)
    n_exploit = 0
    for it in items:
        atk = t_keyword_inflation(it, rng)
        wrong = not oracle(atk.answer_text, it)
        if wrong and judge.score(atk.answer_text, it.question).passed:
            n_exploit += 1
    return 1000.0 * n_exploit / len(items) if items else 0.0


def _gen_in_slice(conjunction: dict, seed: int, n: int) -> list[Item]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        steps = conjunction.get("steps", rng.choice([2, 3, 4]))
        large = conjunction.get("large_operands", rng.choice([False, True]))
        distr = conjunction.get("distractor", rng.choice([False, True]))
        out.append(generate_item(rng, steps, large, distr, 90000 + i))
    return out


def prospective_validate(slice_: CausalSlice, judge: Judge, seed: int, n: int = 24) -> CausalSlice:
    """Generate fresh held-out cohorts and test the named slice as a prediction."""
    factor_keys = ("steps", "large_operands", "distractor")
    in_slice = _gen_in_slice(slice_.conjunction, seed + 1, n)
    # broad baseline: a COARSER slice (drop the most specific factor); if the
    # named slice is a single factor, the coarser slice is unconstrained.
    broad_conj = dict(list(slice_.conjunction.items())[:-1])
    broad = _gen_in_slice(broad_conj, seed + 2, n)
    # random control: no constraint
    rand = _gen_in_slice({}, seed + 3, n)

    slice_.prospective_density = round(_attack_and_measure(in_slice, judge, seed + 11), 1)
    slice_.broad_baseline_density = round(_attack_and_measure(broad, judge, seed + 12), 1)
    slice_.random_baseline_density = round(_attack_and_measure(rand, judge, seed + 13), 1)
    slice_.lift_over_broad = round(slice_.prospective_density - slice_.broad_baseline_density, 1)
    slice_.lift_over_random = round(slice_.prospective_density - slice_.random_baseline_density, 1)
    # the named slice must predict failure above an unconstrained control, and be
    # at least as predictive as the coarser slice.
    slice_.validated = (slice_.prospective_density > slice_.random_baseline_density
                        and slice_.prospective_density >= slice_.broad_baseline_density)
    return slice_
