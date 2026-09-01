#!/usr/bin/env bash
# ============================================================================
# POWERED real-LLM-judge convergence sweep  —  the #1 bulletproofing item for
# the Wind Tunnel's central claim (C2): repair *relocates* the flaw, and even
# structural self-commitment does NOT cure gaming on a real frontier judge.
#
# The R2 pilot that ships in the paper is deliberately thin: 2 benchmarks
# (MATH, HLE), n=100/cycle, K=4, ONE judge model. That is the most-attackable
# plank under the heaviest weight ("underpowered, one judge"). This sweep
# widens all three axes so the result cannot be dismissed as noise.
#
# Requires a filled .env with GRADIA_GUARD_GATEWAY_URL (+ creds). REAL API SPEND.
#
#   Launch (default: 4 benchmarks x 1 judge, n=200, K=6):
#       bash run_realjudge_powered.sh
#
#   Widen to a multi-judge measurement (turns "paradigm, not checkpoint" from
#   an argument into a measurement — item #2):
#       MODELS="claude-opus-5 gemini-3.1-pro-preview gpt-5.6-sol grok-4.6" \
#       bash run_realjudge_powered.sh
#
#   Gauge spend first with ONE cell:
#       BENCHES="math" MODELS="claude-opus-5" LIMIT=200 K=6 bash run_realjudge_powered.sh
#
# COST scales ~ (#benches x #models x LIMIT x K x ~2 arms) judge calls.
# The default below (4 x 1 x 200 x 6) is ~12x the R2 pilot; each extra judge
# model multiplies the whole sweep. Start with one model, read the spend the
# gateway reports, then decide whether to add judges. GSM8K is included as the
# resist-control: it should stay ~0 and prove the sweep isn't manufacturing
# exploits.
# ============================================================================
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"; export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
[ -f .env ] && { set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a; }

BENCHES="${BENCHES:-math hle gpqa_diamond gsm8k}"
MODELS="${MODELS:-claude-opus-5}"
LIMIT="${LIMIT:-200}"; K="${K:-6}"
REAL="${REAL:-1}"; REALFLAG=""; [ "$REAL" = "1" ] && REALFLAG="--real"

STAMP="$(date +%Y%m%d-%H%M%S)"; ROOT="results/realjudge-powered-$STAMP"; mkdir -p "$ROOT"
echo "### powered real-judge sweep: benches=[$BENCHES] models=[$MODELS] n=$LIMIT K=$K real=$REAL"
echo "### -> $ROOT"
fail=0
for M in $MODELS; do
  for B in $BENCHES; do
    OUT="$ROOT/${B}--${M}"; mkdir -p "$OUT"
    echo "--- $B x $M -> $OUT"
    if ! python3 -m gradia_wind_tunnel.cli realjudge --benchmark "$B" $REALFLAG --model "$M" \
           --limit "$LIMIT" --K "$K" --out "$OUT" 2>&1 | tee "$OUT/run.log"; then
      echo "!! $B x $M FAILED (continuing the sweep)"; fail=$((fail+1))
    fi
  done
done
echo "### done -> $ROOT  (each cell: <bench>--<model>/realjudge_convergence.json)"
[ "$fail" -gt 0 ] && echo "### $fail cell(s) failed — see the per-cell run.log"
echo "### next: point the realjudge table/figure at \$ROOT and re-run the fold"
echo "###       (run_research.sh regenerates the paper numbers; make_paper_figures.py the charts)"
