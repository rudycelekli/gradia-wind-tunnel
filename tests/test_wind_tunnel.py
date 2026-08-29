"""Pytest entry point: runs the package property-test suite and the prereg self-digest.

    pytest            # from the repo root
    make test         # equivalent, stdlib only
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


def test_property_suite_passes():
    from gradia_wind_tunnel import tests as suite
    assert suite.main() == 0


def test_preregistration_self_digest_round_trips(tmp_path):
    from gradia_wind_tunnel import preregistration
    out = tmp_path / "prereg.json"
    _, sha = preregistration.freeze("gradia-wind-tunnel-test-0001", out, max_cost_usd=300.0)
    report = preregistration.verify(out)
    assert report["ok"] is True
    assert report["stored_sha256"] == sha
    assert report["recomputed_sha256"] == sha


def test_target_benchmarks_declare_oracle_and_grader():
    from gradia_wind_tunnel.contracts import TARGET_BENCHMARKS
    assert len(TARGET_BENCHMARKS) >= 3
    for b in TARGET_BENCHMARKS:
        assert b.oracle_kind in {"numeric_equality", "unit_tests", "key_match"}
        assert len(b.grader_kinds) >= 1  # there is a gameable scoring component


def test_procedural_math_adapter_oracle_is_honest():
    from gradia_wind_tunnel.benchmarks import build_adapter
    a = build_adapter("gsm8k")
    items = a.items(seed=1, per_cell=2)
    assert items and all(a.oracle(it.correct_answer(), it) for it in items)
