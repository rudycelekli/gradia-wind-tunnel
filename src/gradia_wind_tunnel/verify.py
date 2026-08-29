"""
`wind-tunnel-verify`: recompute exploit density and the run-log chain head from
a saved episode log, so a third party confirms the headline numbers offline
(the CA / Guard trust move, in miniature).

    python -m pilot.verify run.json

Exits 0 and prints a canonical JSON summary; exits 1 if the file's stored
chain head disagrees with the recomputed one (tamper / drift detection).
"""

from __future__ import annotations

import json
import sys

from .windtunnel import Episode, exploit_density, run_log_chain_head


def load_episodes(path: str) -> tuple[list[Episode], str | None]:
    with open(path) as f:
        blob = json.load(f)
    eps = [Episode(**e) for e in blob["episodes"]]
    return eps, blob.get("chain_head")


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        sys.stderr.write("usage: python -m pilot.verify RUN.json\n")
        return 2
    eps, stored = load_episodes(argv[0])
    recomputed = run_log_chain_head(eps)
    ok = (stored is None) or (stored == recomputed)
    summary = {
        "episodes": len(eps),
        "exploits": sum(1 for e in eps if e.is_exploit),
        "exploit_density_per_1000": round(exploit_density(eps), 2),
        "chain_head_stored": stored,
        "chain_head_recomputed": recomputed,
        "chain_head_ok": ok,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
