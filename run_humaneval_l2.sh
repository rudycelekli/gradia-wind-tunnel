#!/usr/bin/env bash
# Re-run ONLY HumanEval L2 + witnessed localization. L1 already landed (0.0 exploits);
# L2 + localize died on a transient HTTP 529 (Anthropic overloaded). This resumes just
# those two, then folds. Safe to re-run if 529 recurs.
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"; export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
[ -f .env ] && { set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a; }
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="results/HUMANEVAL-L2-$STAMP"; mkdir -p "$OUT"
echo "################ HumanEval L2 + localize (resume) @ $STAMP ################"
echo "===== L2 (200 items, adaptive) ====="
python3 -m gradia_wind_tunnel.cli suite --benchmark humaneval --rung L2 --real --live \
  --limit 200 --max-cost-usd 200 --out "$OUT/humaneval-L2" 2>&1 | tail -25
echo ""; echo "===== witnessed localization (40 items) ====="
python3 -m gradia_wind_tunnel.cli localize --benchmark humaneval --real --live \
  --limit 40 --max-cost-usd 80 --out "$OUT/humaneval-localize.json" 2>&1 | tail -20
echo ""; echo "===== fold: refresh index + tables + anchor ====="
bash run_research.sh
echo "################ DONE -> $OUT ################"
