#!/usr/bin/env bash
# Real-LLM-judge convergence (rubric-edit loop) against the Guard-routed frontier judge.
# Offline rubric-aware sim by default; REAL=1 routes to the live judge (needs Guard creds).
#   BENCH=math REAL=1 MODEL=claude-opus-5 LIMIT=100 bash run_realjudge.sh
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"; export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
[ -f .env ] && { set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a; }
BENCH="${BENCH:-math}"; MODEL="${MODEL:-claude-opus-5}"; LIMIT="${LIMIT:-100}"; K="${K:-4}"
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="results/realjudge-$STAMP"
REALFLAG=""; [ "${REAL:-0}" = "1" ] && REALFLAG="--real"
echo "### real-judge convergence: bench=$BENCH model=$MODEL real=${REAL:-0} -> $OUT"
python3 -m gradia_wind_tunnel.cli realjudge --benchmark "$BENCH" $REALFLAG --model "$MODEL" --limit "$LIMIT" --K "$K" --out "$OUT"
echo "### bundle: $OUT/realjudge_convergence.json"
