#!/usr/bin/env python3
"""Positive control for the witnessed causal localizer (C1).

The powered R3 runs return validated=false on real judges (MATH, HLE): the defect is
genuinely diffuse, no single construction variable survives held-out validation. A fair
reviewer asks the obvious question — is the localizer simply incapable of confirming
*anything*? This control answers it.

We grade REAL benchmark items with a single-cue control scorer that passes any answer
containing exactly ONE known cue phrase, regardless of correctness. By construction the
scorer has a single exploitable variable, so the localizer must recover exactly that cue
with a positive held-out lift (validated=true). It does. The same instrument therefore
CONFIRMS when a single cause exists and REFUSES when the defect is diffuse — which is the
property a causal instrument must have and a static leaderboard cannot.

Run:  PYTHONPATH=src python3 run_localize_positive_control.py
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "src")
from gradia_wind_tunnel.benchmark_suite import build_benchmark
from gradia_wind_tunnel.witnessed_localization import run_localization, verify_localization
from gradia_wind_tunnel.transforms import FAVORED_PHRASES
from gradia_wind_tunnel.judges import Verdict

CUE = FAVORED_PHRASES[0]  # a single, known, exploitable cue


class SingleCueJudge:
    """A scorer with exactly one exploitable cue: it passes any answer containing CUE,
    regardless of correctness. The single localizable defect by construction."""
    name = "single_cue_control"
    total_cost_usd = 0.0

    def __init__(self, cue: str) -> None:
        self.cue = cue.lower()

    def score(self, answer_text, question):
        p = self.cue in (answer_text or "").lower()
        return Verdict(passed=p, score=1.0 if p else 0.0,
                       rationale="single-cue control", cost_usd=0.0)


def main() -> int:
    bench = build_benchmark("math")
    items = bench.offline_samples(n=40, seed=1)
    rep = run_localization("positive-control-singlecue-math", bench, items,
                           SingleCueJudge(CUE), holdout_frac=0.5)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    out = Path("results") / f"localize-positive-control-{stamp}" / "singlecue-math.localization.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(rep, indent=2, sort_keys=True))
    pr = rep["prospective"]
    print(json.dumps({
        "cue": CUE,
        "localized_variable": rep["localized_variable"],
        "validated": pr["validated"],
        "lift_over_baseline": pr["lift_over_baseline"],
        "holdout_flip_rate": pr["holdout_flip_rate"],
        "baseline_mean_holdout": pr["baseline_mean_holdout"],
        "self_digest_ok": verify_localization(rep),
        "path": str(out),
    }, indent=2))
    assert pr["validated"] is True and rep["localized_variable"] == f"phrase:{CUE}", \
        "positive control FAILED — the localizer did not confirm the single cue"
    print("POSITIVE CONTROL PASSED: the localizer confirmed the single cue (validated=true, lift=1.0).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
