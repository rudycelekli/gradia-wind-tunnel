#!/usr/bin/env bash
# Finish the study — run AFTER the L1 overnight (run_wind_tunnel.sh) completes.
# Keeps every L1 bundle already produced, re-runs ONLY the missing ones (e.g. a
# benchmark that dropped on a network blip), then does L2 + witnessed
# localization, Regime-2, agent-env, and the SWE readiness check. One command,
# hardened grader, fail-closed, zero waste.
#   caffeinate -i bash run_rest.sh
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
STAMP="$(date +%Y%m%d-%H%M%S)"; R="results/REST-$STAMP"; mkdir -p "$R"
say(){ echo "$@" | tee -a "$R/rest.log"; }
CLI(){ python3 -m gradia_wind_tunnel.cli "$@"; }

say "################ FINISH THE STUDY @ $STAMP ################"

# 1) fill L1 gaps: re-run only benchmarks whose L1 bundle is missing from the latest overnight run
LATEST=$(ls -dt results/overnight-* 2>/dev/null | head -1)
say "L1 completeness vs: ${LATEST:-<none>}"
for b in gsm8k math gpqa_diamond humaneval hle; do
  if [ -n "$LATEST" ] && [ -f "$LATEST/$b/manifest.json" ]; then
    say "  L1 $b: already done (keeping it)"
  else
    say "  L1 $b: MISSING -> re-running 200 items"
    CLI suite --benchmark "$b" --rung L1 --real --live --limit 200 --max-cost-usd 150 --out "$R/$b-L1" 2>&1 | tee -a "$R/rest.log" || say "    $b L1 failed (skipped)"
  fi
done

# 2) L2 adaptive search + witnessed causal localization (all five)
say ""; say "===== L2 adaptive search + witnessed localization ====="
LIMIT=200 CAP=200 LOC_LIMIT=40 LOC_CAP=80 bash run_wind_tunnel_L2.sh 2>&1 | tee -a "$R/rest.log" || say "  L2 stage returned nonzero"

# 3) Regime-2 oracle-less audit (hle + math)
say ""; say "===== Regime-2 oracle-less audit ====="
for b in hle math; do
  CLI regime2 --benchmark "$b" --real --live --limit 40 --max-cost-usd 80 --out "$R/regime2-$b" 2>&1 | tee -a "$R/rest.log" || say "  regime2 $b failed (skipped)"
done

# 4) agent-env + SWE readiness
say ""; say "===== agent-env + SWE readiness ====="
CLI agentenv --tasks 100 --out "$R/agentenv" 2>&1 | tee -a "$R/rest.log" || true
CLI swebench-check 2>&1 | tee -a "$R/rest.log" || true

say ""; say "################ DONE @ $(date +%H:%M:%S) — bundles under $R, results/L2-*, and the overnight dir ################"
