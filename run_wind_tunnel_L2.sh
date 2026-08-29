#!/usr/bin/env bash
# Gradia Wind Tunnel — L2 adaptive search + witnessed causal localization.
# The "find in all" wave: run AFTER (or alongside) the L1 run. Separate log dir,
# same fail-closed design (smoke first, per-item budget, cost caps, skip-on-fail).
#
#   LIMIT=200 CAP=80 bash run_wind_tunnel_L2.sh          # full L2 across all five
#   LOC_LIMIT=40 LOC_CAP=40 ...                          # localization cohort/caps
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

PREREG="preregistrations/gradia-wind-tunnel-phase0-20260829-03.json"
BENCHES=(gsm8k math gpqa_diamond humaneval hle)
LIMIT="${LIMIT:-200}"; CAP="${CAP:-80}"; SMOKE=2
LOC_LIMIT="${LOC_LIMIT:-40}"; LOC_CAP="${LOC_CAP:-40}"
STAMP="$(date +%Y%m%d-%H%M%S)"; LOG="results/L2-$STAMP"; mkdir -p "$LOG"
CLI(){ python3 -m gradia_wind_tunnel.cli "$@"; }
say(){ echo "$@" | tee -a "$LOG/run.log"; }

say "=== L2 adaptive search + witnessed localization @ $STAMP ==="
say "log dir: $LOG   L2 LIMIT=$LIMIT CAP=\$$CAP/bench   localize cohort=$LOC_LIMIT cap=\$$LOC_CAP"
python3 -c "import datasets" 2>/dev/null || { say "FATAL: 'datasets' missing -> pip install -e \".[real]\""; exit 1; }
CLI prereg-verify "$PREREG" >/dev/null 2>&1 || { say "FATAL: prereg-verify failed for $PREREG"; exit 1; }
say "preflight OK"

okL2=(); okLOC=(); skipped=()
for b in "${BENCHES[@]}"; do
  say ""; say "### $b — L2 smoke ($SMOKE items) ###"
  if CLI suite --benchmark "$b" --rung L2 --real --live --limit "$SMOKE" --max-cost-usd 5 --out "$LOG/smoke-$b" >"$LOG/smoke-$b.log" 2>&1; then
    say "  smoke OK -> L2 full ($LIMIT items, cap \$$CAP)"
    if CLI suite --benchmark "$b" --rung L2 --real --live --limit "$LIMIT" --max-cost-usd "$CAP" --out "$LOG/$b-L2" >"$LOG/$b-L2.log" 2>&1; then
      spent=$(python3 -c "import json;print(json.load(open('$LOG/$b-L2/manifest.json'))['spend']['spent_usd'])" 2>/dev/null || echo '?')
      exps=$(python3 -c "import json;print(json.load(open('$LOG/$b-L2/manifest.json'))['totals']['exploits'])" 2>/dev/null || echo '?')
      say "  DONE L2 $b — exploits=$exps spent=\$$spent — $LOG/$b-L2/manifest.json"; okL2+=("$b")
    else say "  L2 FULL FAILED ($b):"; tail -4 "$LOG/$b-L2.log" | tee -a "$LOG/run.log"; skipped+=("$b-L2"); fi
    say "  ### $b — witnessed causal localization (cohort $LOC_LIMIT) ###"
    if CLI localize --benchmark "$b" --real --live --limit "$LOC_LIMIT" --max-cost-usd "$LOC_CAP" --out "$LOG/$b-localize.json" >"$LOG/$b-localize.out" 2>&1; then
      loc=$(python3 -c "import json;d=json.load(open('$LOG/$b-localize.out'));p=d.get('prospective') or {};print(d['localized_variable'],'| validated:',p.get('validated'),'| engine:',d['witness_engine'])" 2>/dev/null || echo '?')
      say "  DONE localize $b -> $loc"; okLOC+=("$b")
    else say "  LOCALIZE FAILED ($b):"; tail -4 "$LOG/$b-localize.out" | tee -a "$LOG/run.log"; skipped+=("$b-loc"); fi
  else say "  SMOKE FAILED ($b) — skipping:"; tail -4 "$LOG/smoke-$b.log" | tee -a "$LOG/run.log"; skipped+=("$b"); fi
done

say ""; say "=== SUMMARY ==="
say "L2 completed:       ${okL2[*]:-none}"
say "localization done:  ${okLOC[*]:-none}"
say "skipped:            ${skipped[*]:-none}"
say "verify an L2 bundle:  PYTHONPATH=src python3 -m gradia_wind_tunnel.cli verify-report $LOG/<bench>-L2/manifest.json"
