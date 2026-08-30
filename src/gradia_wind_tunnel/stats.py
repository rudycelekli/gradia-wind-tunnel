"""Bootstrap confidence intervals for exploit-density estimands.

Every headline density in the paper is a point estimate on one item sample. This
module attaches a 95% CI by resampling the ITEM as the independent unit -- episodes
within an item are correlated (same question, several attacks), so the item, not
the episode, is the draw. Item-clustered nonparametric bootstrap, percentile CI,
plus a Wilson score interval on the raw attempt proportion as an analytic check.

Pure and deterministic given the seed, so the CI is itself recomputable from the
frames a run already writes. Accepts either capture.read_frames dicts or Episode
objects (via _get).
"""
from __future__ import annotations

import math
import random
from collections import defaultdict


def _get(ep, key):
    if isinstance(ep, dict):
        return ep.get(key)
    return getattr(ep, key, None)


def _group_by_item(episodes):
    g = defaultdict(list)
    for e in episodes:
        g[_get(e, "item_id")].append(e)
    return list(g.values())


def _density(groups):
    ex = sum(1 for grp in groups for e in grp if _get(e, "is_exploit"))
    denom = sum(len(grp) for grp in groups)
    return 1000.0 * ex / denom if denom else 0.0


def bootstrap_density_ci(episodes, *, n_boot: int = 5000, seed: int = 20260830):
    """95% percentile CI for exploits-per-1000, resampling item-clusters with
    replacement. Works for L1 (many attempts/item) and L2 (one episode/item)."""
    items = _group_by_item(list(episodes))
    n = len(items)
    point = _density(items)
    n_ex = sum(1 for grp in items for e in grp if _get(e, "is_exploit"))
    n_att = sum(len(grp) for grp in items)
    rng = random.Random(seed)
    boots = []
    for _ in range(n_boot):
        sample = [items[rng.randrange(n)] for _ in range(n)] if n else []
        boots.append(_density(sample))
    boots.sort()

    def pct(p):
        if not boots:
            return 0.0
        k = min(len(boots) - 1, max(0, int(round(p * (len(boots) - 1)))))
        return boots[k]

    mean = sum(boots) / len(boots) if boots else 0.0
    var = sum((b - mean) ** 2 for b in boots) / (len(boots) - 1) if len(boots) > 1 else 0.0
    return {
        "point": round(point, 1),
        "ci95_low": round(pct(0.025), 1),
        "ci95_high": round(pct(0.975), 1),
        "boot_mean": round(mean, 1),
        "boot_se": round(math.sqrt(var), 1),
        "n_items": n, "n_attempts": n_att, "n_exploits": n_ex,
        "n_boot": n_boot, "seed": seed,
        "method": "item-clustered nonparametric bootstrap, percentile 95% CI",
    }


def wilson_ci(k: int, n: int, z: float = 1.96):
    """Wilson score interval for a proportion, reported per-1000 (analytic check;
    ignores item clustering, so it is typically narrower than the bootstrap)."""
    if n == 0:
        return {"point": 0.0, "ci95_low": 0.0, "ci95_high": 0.0, "method": "wilson"}
    p = k / n
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = (z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / denom
    return {"point": round(1000 * p, 1),
            "ci95_low": round(1000 * max(0.0, center - half), 1),
            "ci95_high": round(1000 * min(1.0, center + half), 1),
            "method": "wilson"}


def compare_disjoint(ci_a: dict, ci_b: dict) -> bool:
    """True if two bootstrap CIs do not overlap (a coarse significance read)."""
    return ci_a["ci95_high"] < ci_b["ci95_low"] or ci_b["ci95_high"] < ci_a["ci95_low"]
