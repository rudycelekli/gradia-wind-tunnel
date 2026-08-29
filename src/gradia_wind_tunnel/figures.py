"""Generate the paper's figures from a study report.

Matplotlib only (matches the program's make_figures.py convention). Figures are
drawn from the OFFLINE study; until Phase-0 runs against real models they
illustrate the machinery, not empirical findings — every figure caption says so.

    python -m gradia_wind_tunnel.figures --out paper/figures
"""

from __future__ import annotations

import sys
from pathlib import Path

from .experiment import run_study

_ILLUSTRATIVE = "Illustrative (offline scorer) — machinery, not an empirical finding."


def make_figures(out_dir: Path, seed: int = 20260829) -> list[Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_dir.mkdir(parents=True, exist_ok=True)
    report = run_study("figures", per_cell=8, K=6)
    paths: list[Path] = []

    # Fig 1 — rung densities (L0 -> L1 -> L2)
    rungs = report["rungs"]
    labels = ["L0\nnatural", "L1\nmetamorphic", "L2\nadaptive"]
    vals = [rungs["L0_natural_incidence"]["density_per_1000"],
            rungs["L1_metamorphic"]["density_per_1000"],
            rungs["L2_adaptive_search"]["density_per_1000"]]
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.bar(labels, vals, color=["#9aa7b2", "#3b7dd8", "#d8663b"])
    ax.set_ylabel("exploit density / 1000")
    ax.set_title("Exploit density by threat rung")
    fig.text(0.5, -0.02, _ILLUSTRATIVE, ha="center", fontsize=7, style="italic")
    p = out_dir / "fig1_rungs.png"; fig.savefig(p, bbox_inches="tight", dpi=150); plt.close(fig); paths.append(p)

    # Fig 2 — causal slice: prospective vs baselines
    cs = report["causal_slice"]
    if cs:
        fig, ax = plt.subplots(figsize=(5, 3.2))
        ax.bar(["named slice\n" + str(cs["conjunction"]), "broad\nbaseline", "random\ncontrol"],
               [cs["prospective_density"], cs["broad_baseline_density"], cs["random_baseline_density"]],
               color=["#2a9d6f", "#9aa7b2", "#c7ccd1"])
        ax.set_ylabel("prospective exploit density / 1000")
        ax.set_title("Causal slice validates above baselines")
        fig.text(0.5, -0.02, _ILLUSTRATIVE, ha="center", fontsize=7, style="italic")
        p = out_dir / "fig2_causal_slice.png"; fig.savefig(p, bbox_inches="tight", dpi=150); plt.close(fig); paths.append(p)

    # Fig 3 — convergence curve
    conv = report["convergence"]
    fig, ax = plt.subplots(figsize=(5, 3.2))
    ax.plot(range(1, len(conv["heldout_curve"]) + 1), conv["heldout_curve"],
            marker="o", color="#3b7dd8")
    ax.set_xlabel("patch cycle")
    ax.set_ylabel("held-out exploit density / 1000")
    ax.set_title(f"Convergence: {conv['classification']} (mean gamma {conv['mean_gamma']})")
    fig.text(0.5, -0.02, _ILLUSTRATIVE, ha="center", fontsize=7, style="italic")
    p = out_dir / "fig3_convergence.png"; fig.savefig(p, bbox_inches="tight", dpi=150); plt.close(fig); paths.append(p)

    return paths


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    out = Path("paper/figures")
    if "--out" in argv:
        out = Path(argv[argv.index("--out") + 1])
    paths = make_figures(out)
    for p in paths:
        print(f"wrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
