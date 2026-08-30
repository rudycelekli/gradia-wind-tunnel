"""The living Scorer Gameability Index -- one recomputable number per public
benchmark that anyone can cite and re-derive from the evidence frames.

For a benchmark's evidence bundle (frames.ndjson + manifest), the index is the
oracle-witnessed exploit density of its scorer under the canonical adversary, with
a 95% bootstrap CI, pinned to the dataset snapshot, the judge identity, and the git
SHA. Each card is content-addressed, so a third party recomputes the exact number
offline and verifies the digest. This is the 'paper -> infrastructure' artifact:
a standing, versioned gameability score the field can track as benchmarks and
judges evolve, and the anchor for responsible disclosure to benchmark maintainers.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .canonical import digest, load_json
from .capture import read_frames
from .stats import bootstrap_density_ci, wilson_ci

INDEX_SCHEMA = "gradia-wind-tunnel-gameability-index.v1"


def index_card(bundle_dir, *, label: str | None = None, boot_seed: int = 20260830, n_boot: int = 5000) -> dict[str, Any]:
    d = Path(bundle_dir)
    man = load_json(d / "manifest.json")
    frames = read_frames(d / "frames.ndjson")
    ci = bootstrap_density_ci(frames, n_boot=n_boot, seed=boot_seed)
    w = wilson_ci(ci["n_exploits"], ci["n_attempts"])
    card = {
        "schema": INDEX_SCHEMA,
        "label": label,
        "benchmark": man.get("benchmark_id"),
        "benchmark_real": man.get("benchmark_real"),
        "rung": man.get("rung"),
        "judge": man.get("judge"),
        "git_sha": man.get("git_sha"),
        "n_items": ci["n_items"], "n_attempts": ci["n_attempts"], "n_exploits": ci["n_exploits"],
        "gameability_index_per_1000": ci["point"],
        "ci95_bootstrap": [ci["ci95_low"], ci["ci95_high"]],
        "ci95_wilson": [w["ci95_low"], w["ci95_high"]],
        "bootstrap": {"n_boot": ci["n_boot"], "seed": ci["seed"], "method": ci["method"]},
        "frames_chain_head": man.get("frames_chain_head"),
        "manifest_sha256": man.get("manifest_sha256"),
        "source_bundle": str(d),
    }
    card["card_sha256"] = digest(card)
    return card


def build_index(bundles, *, boot_seed: int = 20260830, n_boot: int = 5000) -> dict[str, Any]:
    cards = []
    for label, bd in bundles:
        try:
            c = index_card(bd, label=label, boot_seed=boot_seed, n_boot=n_boot)
            cards.append(c)
        except Exception as e:
            cards.append({"label": label, "source_bundle": str(bd),
                          "error": f"{type(e).__name__}: {str(e)[:140]}"})
    body = {
        "schema": INDEX_SCHEMA + ".table",
        "n_cards": len([c for c in cards if "error" not in c]),
        "cards": cards,
        "note": ("Each card's gameability_index is the oracle-witnessed exploit density of the "
                 "benchmark's scorer under the canonical adversary, recomputable from the frames "
                 "(deterministic bootstrap seed). Pinned to dataset snapshot, judge, and git SHA."),
    }
    body["index_sha256"] = digest(body)
    return body


def verify_card(card: dict) -> bool:
    return card.get("card_sha256") == digest({k: v for k, v in card.items() if k != "card_sha256"})
