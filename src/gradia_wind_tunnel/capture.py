"""Research-grade evidence capture — every paper number is recomputable.

A run writes two artifacts:

  frames.ndjson  — one canonical line per attack episode (the granular record:
                   rung, benchmark, item, transform, factors, oracle verdict,
                   judge verdict + score + cost, exploit flag, answer digest).
  manifest.json  — a self-digested summary carrying exactly the estimands the
                   paper reports (density by rung/benchmark/transform/slice,
                   exploit-magnitude bins, cost), plus a chain head over the
                   frames.

`verify_bundle` recomputes the chain head AND every aggregate from the frames and
checks them against the manifest — so a reviewer confirms every figure and table
offline, and any edit to a frame is detected. This is the CA `cost-capped-verify`
pattern, and it is what makes the captured observations usable in a world-class
paper: nothing in the writeup is asserted, everything is derived and verifiable.

The frames are also the analytics feed: each line is a row a Gradia analytics
sink (or any warehouse) ingests directly.
"""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable

from .canonical import canonical_bytes, digest
from .windtunnel import Episode, exploit_density

FRAMES_SCHEMA = "gradia-wind-tunnel-frames.v1"
MANIFEST_SCHEMA = "gradia-wind-tunnel-evidence-manifest.v1"

# exploit magnitude bins (judge margin/score on oracle-wrong answers)
_MAG_BINS = [(0.0, 0.25), (0.25, 0.5), (0.5, 0.75), (0.75, 1.01)]


def write_frames(path: Path, episodes: Iterable[Episode]) -> str:
    """Write one canonical NDJSON line per episode; return the chain head."""
    path.parent.mkdir(parents=True, exist_ok=True)
    head = digest({"schema": FRAMES_SCHEMA})
    lines: list[bytes] = []
    for ep in episodes:
        frame = {"prev": head, "episode": asdict(ep)}
        head = digest(frame)
        lines.append(canonical_bytes({**asdict(ep), "frame_sha256": head}))
    path.write_bytes(b"\n".join(lines) + (b"\n" if lines else b""))
    return head


def _by(episodes: list[Episode], key) -> dict[str, dict[str, float]]:
    buckets: dict[Any, list[Episode]] = {}
    for e in episodes:
        buckets.setdefault(key(e), []).append(e)
    return {str(k): {"attempts": len(v), "exploits": sum(x.is_exploit for x in v),
                     "density_per_1000": round(exploit_density(v), 1)}
            for k, v in sorted(buckets.items(), key=lambda kv: str(kv[0]))}


def _magnitude_hist(episodes: list[Episode]) -> dict[str, int]:
    wrong_pass = [e for e in episodes if e.is_exploit]
    hist = {f"{lo:.2f}-{hi:.2f}": 0 for lo, hi in _MAG_BINS}
    for e in wrong_pass:
        for lo, hi in _MAG_BINS:
            if lo <= e.judge_score < hi:
                hist[f"{lo:.2f}-{hi:.2f}"] += 1
                break
    return hist


def build_manifest(run_meta: dict[str, Any], episodes: list[Episode],
                   frames_chain_head: str) -> dict[str, Any]:
    """Assemble the self-digested evidence manifest (the paper's results appendix)."""
    eps = list(episodes)
    body: dict[str, Any] = {
        "schema": MANIFEST_SCHEMA,
        **run_meta,
        "totals": {
            "attempts": len(eps),
            "exploits": sum(e.is_exploit for e in eps),
            "overall_density_per_1000": round(exploit_density(eps), 1),
            "total_cost_usd": round(sum(e.cost_usd for e in eps), 4),
        },
        "density_by_rung": _by(eps, lambda e: e.rung),
        "density_by_transform": _by(eps, lambda e: e.transform_id),
        "density_by_benchmark": _by(eps, lambda e: e.factors.get("benchmark_id", run_meta.get("benchmark_id", "?"))),
        "exploit_magnitude_hist": _magnitude_hist(eps),
        "frames_chain_head": frames_chain_head,
        "frames_schema": FRAMES_SCHEMA,
    }
    body["manifest_sha256"] = digest(body)
    return body


def read_frames(path: Path) -> list[dict]:
    import json
    out = []
    for line in path.read_text().splitlines():
        if line.strip():
            out.append(json.loads(line))
    return out


def verify_bundle(frames_path: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    """Recompute the chain head and every derived aggregate from the frames.

    A valid manifest self-digest proves only that the manifest is internally
    consistent.  It does not prove that its claimed counts, costs, or slices
    came from the frames.  This verifier therefore rebuilds each published
    aggregate independently and compares every field exactly.
    """
    frames = read_frames(frames_path)
    # recompute the chain head
    head = digest({"schema": FRAMES_SCHEMA})
    chain_ok = True
    recomputed_eps: list[Episode] = []
    for row in frames:
        stored_frame = row.get("frame_sha256")
        ep_fields = {k: v for k, v in row.items() if k != "frame_sha256"}
        head = digest({"prev": head, "episode": ep_fields})
        if stored_frame != head:
            chain_ok = False
        recomputed_eps.append(Episode(**ep_fields))
    chain_ok = chain_ok and (head == manifest.get("frames_chain_head"))

    expected_aggregates = {
        "totals": {
            "attempts": len(recomputed_eps),
            "exploits": sum(e.is_exploit for e in recomputed_eps),
            "overall_density_per_1000": round(exploit_density(recomputed_eps), 1),
            "total_cost_usd": round(sum(e.cost_usd for e in recomputed_eps), 4),
        },
        "density_by_rung": _by(recomputed_eps, lambda e: e.rung),
        "density_by_transform": _by(recomputed_eps, lambda e: e.transform_id),
        "density_by_benchmark": _by(
            recomputed_eps,
            lambda e: e.factors.get("benchmark_id", manifest.get("benchmark_id", "?")),
        ),
        "exploit_magnitude_hist": _magnitude_hist(recomputed_eps),
    }
    aggregate_checks = {
        key: manifest.get(key) == expected
        for key, expected in expected_aggregates.items()
    }
    aggregates_ok = all(aggregate_checks.values())

    # recompute the manifest self-digest
    self_ok = manifest.get("manifest_sha256") == digest(
        {k: v for k, v in manifest.items() if k != "manifest_sha256"})

    return {
        "frames": len(frames),
        "schema_ok": (
            manifest.get("schema") == MANIFEST_SCHEMA
            and manifest.get("frames_schema") == FRAMES_SCHEMA
        ),
        "chain_head_ok": chain_ok,
        "aggregate_checks": aggregate_checks,
        "aggregates_ok": aggregates_ok,
        "manifest_self_digest_ok": self_ok,
        "ok": (
            manifest.get("schema") == MANIFEST_SCHEMA
            and manifest.get("frames_schema") == FRAMES_SCHEMA
            and chain_ok
            and aggregates_ok
            and self_ok
        ),
    }


def verify_bundle_tree(results_dir: Path) -> dict[str, Any]:
    """Verify every committed Proof Pack under ``results_dir``.

    This is the release gate behind ``verify-release``. A repository is not
    reproducible when only a hand-picked example verifies; every directory that
    publishes both ``frames.ndjson`` and ``manifest.json`` must replay cleanly.
    """
    bundles: list[dict[str, Any]] = []
    for manifest_path in sorted(results_dir.rglob("manifest.json")):
        frames_path = manifest_path.parent / "frames.ndjson"
        if not frames_path.exists():
            continue
        try:
            import json

            manifest = json.loads(manifest_path.read_text())
            if not isinstance(manifest, dict):
                raise ValueError("manifest.json must contain a JSON object")
            report = verify_bundle(frames_path, manifest)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            report = {
                "ok": False,
                "error_kind": type(exc).__name__,
                "detail": str(exc),
            }
        bundles.append({
            "bundle": str(manifest_path.parent),
            **report,
        })
    failures = [row["bundle"] for row in bundles if not row.get("ok")]
    return {
        "ok": bool(bundles) and not failures,
        "results_dir": str(results_dir),
        "bundles_discovered": len(bundles),
        "bundles_verified": len(bundles) - len(failures),
        "failures": failures,
        "bundles": bundles,
    }
