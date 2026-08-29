#!/usr/bin/env bash
# Gradia Wind Tunnel — the WHOLE pipeline, one command, hands-off.
#   caffeinate -i bash run_all.sh
# Stages (each fail-closed; one failure never aborts the rest; everything logged):
#   0  agent-env         agentic reward-hacking archetype (deterministic, $0)
#   1  L1 @200/bench      the preregistered run (run_wind_tunnel.sh)
#   2  L2 + localization  adaptive search + witnessed causal slice (run_wind_tunnel_L2.sh)
#   3  Regime-2           oracle-less audit on HLE + MATH (no answer key)
#   4  SWE-bench          readiness ladder (real execution needs a Docker host)
# Caps below are generous CEILINGS (fail-closed guards), not target spend; actual
# cost is whatever the work needs (~$300-400 total in practice).
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
STAMP="$(date +%Y%m%d-%H%M%S)"; ALL="results/ALL-$STAMP"; mkdir -p "$ALL"
say(){ echo "$@" | tee -a "$ALL/all.log"; }
CLI(){ python3 -m gradia_wind_tunnel.cli "$@"; }

say "################ FULL WIND TUNNEL PIPELINE @ $STAMP ################"
say "collector dir: $ALL   (sub-runners also write results/overnight-* and results/L2-*)"

say ""; say "===== [0/4] agent-env — agentic reward-hacking (\$0, deterministic) ====="
CLI agentenv --tasks 100 --out "$ALL/agentenv" 2>&1 | tee -a "$ALL/all.log" || say "  agent-env failed (skipped)"

say ""; say "===== [1/4] L1 @200/bench — the preregistered run ====="
LIMIT=200 CAP=150 bash run_wind_tunnel.sh 2>&1 | tee -a "$ALL/all.log" || say "  L1 stage returned nonzero (see log)"

say ""; say "===== [2/4] L2 adaptive search + witnessed causal localization ====="
LIMIT=200 CAP=200 LOC_LIMIT=40 LOC_CAP=80 bash run_wind_tunnel_L2.sh 2>&1 | tee -a "$ALL/all.log" || say "  L2 stage returned nonzero (see log)"

say ""; say "===== [3/4] Regime-2 — oracle-less audit (no answer key) ====="
for b in hle math; do
  say "  --- regime2: $b ---"
  CLI regime2 --benchmark "$b" --real --live --limit 40 --max-cost-usd 80 --out "$ALL/regime2-$b" 2>&1 | tee -a "$ALL/all.log" || say "  regime2 $b failed (skipped)"
done

say ""; say "===== [4/4] SWE-bench readiness ladder ====="
CLI swebench-check 2>&1 | tee -a "$ALL/all.log" || say "  (SWE-bench needs a Docker host / executor)"

say ""; say "################ PIPELINE COMPLETE @ $(date +%H:%M:%S) ################"
say "verify any bundle:  PYTHONPATH=src python3 -m gradia_wind_tunnel.cli verify-report <dir>/manifest.json"
say "collector: $ALL   L1: results/overnight-*   L2: results/L2-*"
