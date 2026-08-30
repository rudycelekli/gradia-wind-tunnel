#!/usr/bin/env bash
# Re-run HumanEval under the CORRECTED code-attack family (real semantic mutations that
# still parse; judge-favored phrasing injected as a comment). Replaces the superseded
# syntax-artifact numbers. Run AFTER run_rest.sh finishes so the judge isn't contended.
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"; export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
[ -f .env ] && { set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a; }
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="results/HUMANEVAL-FIX-$STAMP"; mkdir -p "$OUT"
say(){ echo "$@" | tee -a "$OUT/run.log"; }
say "################ HumanEval re-run (corrected attack family) @ $STAMP ################"

say ""; say "===== preflight: every attack must PARSE and be oracle-wrong ====="
python3 -c "
import ast, random
from gradia_wind_tunnel.benchmark_suite import build_benchmark
b=build_benchmark('humaneval'); items=b.items(seed=20260830, limit=40); rng=random.Random(0)
bad=0
for it in items:
    for a in b.attacks(it, rng):
        try: ast.parse(a.answer_text)
        except SyntaxError: bad+=1; continue
        if b.oracle(a.answer_text, it): bad+=1
print('invalid attacks:', bad)
raise SystemExit(1 if bad else 0)
" 2>&1 | tail -3 | tee -a "$OUT/run.log"
if [ "${PIPESTATUS[0]}" != "0" ]; then say "  PREFLIGHT FAILED - not spending on a bad attack family"; exit 1; fi
say "  preflight OK (all attacks parse and are oracle-wrong)"

say ""; say "===== L1 (200 items) ====="
python3 -m gradia_wind_tunnel.cli suite --benchmark humaneval --rung L1 --real --live \
  --limit 200 --max-cost-usd 150 --out "$OUT/humaneval-L1" 2>&1 | tail -25 | tee -a "$OUT/run.log"

say ""; say "===== L2 (200 items, adaptive) ====="
python3 -m gradia_wind_tunnel.cli suite --benchmark humaneval --rung L2 --real --live \
  --limit 200 --max-cost-usd 200 --out "$OUT/humaneval-L2" 2>&1 | tail -25 | tee -a "$OUT/run.log"

say ""; say "===== witnessed localization (40 items) ====="
python3 -m gradia_wind_tunnel.cli localize --benchmark humaneval --real --live \
  --limit 40 --max-cost-usd 80 --out "$OUT/humaneval-localize.json" 2>&1 | tail -20 | tee -a "$OUT/run.log"

say ""; say "===== refresh the index + all research tables ====="
bash run_research.sh 2>&1 | tail -20 | tee -a "$OUT/run.log"
say ""; say "################ DONE -> $OUT ################"
