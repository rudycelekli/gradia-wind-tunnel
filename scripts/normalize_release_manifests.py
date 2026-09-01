#!/usr/bin/env python3
"""Normalize two historical floating-point cost totals without touching frames.

The raw receipt chains are immutable. Two pre-release manifests rounded the same
IEEE-754 cost sum differently from the released verifier (one up, one down by
0.0001). This allowlisted migration records the prior manifest digest, changes
only ``totals.total_cost_usd``, and emits a new self-digest. It refuses any
unexpected source digest or any non-cost aggregate mismatch.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gradia_wind_tunnel.canonical import digest, load_json, write_canonical
from gradia_wind_tunnel.capture import read_frames, verify_bundle


ALLOWLIST = {
    "results/REST-20260829-222256/hle-L2":
        "7488c5c7074bf57e11b0bef154faaa4fa7dfa532d8d0eeb5ee32b21e131753c8",
    "results/overnight-20260829-012112/smoke-gsm8k":
        "750ce71692e7905213feb615119f2cf0a335662ffd3c620c982b02378e5deafc",
}


def normalize(relative_dir: str, expected_source_digest: str) -> None:
    bundle = ROOT / relative_dir
    manifest_path = bundle / "manifest.json"
    frames_path = bundle / "frames.ndjson"
    manifest = load_json(manifest_path)
    report = verify_bundle(frames_path, manifest)
    if report["ok"]:
        print(f"already normalized: {relative_dir}")
        return
    if manifest.get("manifest_sha256") != expected_source_digest:
        raise RuntimeError(f"unexpected source manifest digest: {relative_dir}")
    failed_checks = sorted(
        key for key, ok in report["aggregate_checks"].items() if not ok
    )
    if (
        not report["chain_head_ok"]
        or not report["manifest_self_digest_ok"]
        or failed_checks != ["totals"]
    ):
        raise RuntimeError(f"migration scope exceeded for {relative_dir}: {report}")

    frames = read_frames(frames_path)
    expected_cost = round(sum(float(row["cost_usd"]) for row in frames), 4)
    old_totals = dict(manifest["totals"])
    new_totals = {**old_totals, "total_cost_usd": expected_cost}
    if {k: v for k, v in old_totals.items() if k != "total_cost_usd"} != {
        k: v for k, v in new_totals.items() if k != "total_cost_usd"
    }:
        raise RuntimeError("non-cost totals would change")

    manifest["totals"] = new_totals
    manifest["release_normalization"] = {
        "schema": "gradia-wind-tunnel-manifest-normalization.v1",
        "source_manifest_sha256": expected_source_digest,
        "changed_field": "totals.total_cost_usd",
        "old_value": old_totals["total_cost_usd"],
        "new_value": expected_cost,
        "reason": (
            "Align the historical derivative cost total with the released verifier's "
            "exact IEEE-754 accumulation and four-decimal rounding. The frame bytes and "
            "frames_chain_head are unchanged."
        ),
    }
    manifest.pop("manifest_sha256", None)
    manifest["manifest_sha256"] = digest(manifest)
    write_canonical(manifest_path, manifest)

    final = verify_bundle(frames_path, load_json(manifest_path))
    if not final["ok"]:
        raise RuntimeError(f"normalized bundle still fails: {relative_dir}: {final}")
    print(f"normalized: {relative_dir}")


def main() -> int:
    for relative_dir, source_digest in ALLOWLIST.items():
        normalize(relative_dir, source_digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
