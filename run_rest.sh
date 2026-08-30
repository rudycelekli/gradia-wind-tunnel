#!/usr/bin/env bash
# Finish the study, resilient to a flaky connection. Keeps every L1 bundle already on
# disk, re-runs only missing ones, then L2 + witnessed localization, Regime-2, agent-env,
# SWE readiness. WAITS for the network before each stage and retries once on failure, so a
# dropped connection pauses the run instead of skipping benchmarks.
#   caffeinate -i bash run_rest.sh
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
STAMP="$(date +%Y%m%d-%H%M%S)"; R="results/REST-$STAMP"; mkdir -p "$R"
say(){ echo "$@" | tee -a "$R/rest.log"; }
CLI(){ python3 -m gradia_wind_tunnel.cli "$@"; }

_net_up(){ python3 -c "import urllib.request as u,urllib.error as e,sys
try: u.urlopen('https://api.anthropic.com/v1/messages',timeout=8); sys.exit(0)
except e.HTTPError: sys.exit(0)
except Exception: sys.exit(1)" 2>/dev/null; }
wait_for_net(){ local max=${1:-1800} w=0
  _net_up && return 0
  say "  network down — waiting (up to $((max/60)) min)..."
  while ! _net_up; do [ "$w" -ge "$max" ] && { say "  network still down after ${w}s"; return 1; }; sleep 15; w=$((w+15)); done
  say "  network back after ${w}s"; return 0; }
# run a CLI stage with a net-wait + one retry; args: <label> <outlog> <cli args...>
stage(){ local label="$1" outlog="$2"; shift 2
  wait_for_net || { say "  SKIP $label (no network)"; return 1; }
  if CLI "$@" >"$outlog" 2>&1; then say "  DONE $label"; return 0; fi
  say "  $label failed once — waiting for network + retrying"; wait_for_net || return 1
  if CLI "$@" >"$outlog" 2>&1; then say "  DONE $label (retry)"; return 0; fi
  say "  FAILED $label — see $outlog:"; tail -3 "$outlog" | tee -a "$R/rest.log"; return 1; }

say "################ FINISH THE STUDY @ $STAMP ################"
wait_for_net 1800 || { say "FATAL: no network after 30 min. Re-run when back online."; exit 1; }

# 1) fill L1 gaps (keep completed bundles)
LATEST=$(ls -dt results/overnight-* 2>/dev/null | head -1); say "L1 completeness vs ${LATEST:-<none>}"
for b in gsm8k math gpqa_diamond humaneval hle; do
  if [ -n "$LATEST" ] && [ -f "$LATEST/$b/manifest.json" ]; then say "  L1 $b: already done"; else
    say "  L1 $b: MISSING -> re-run 200"
    stage "L1-$b" "$R/$b-L1.log" suite --benchmark "$b" --rung L1 --real --live --limit 200 --max-cost-usd 150 --out "$R/$b-L1" || true
  fi
done

# 2) L2 adaptive search + witnessed localization (all five, net-guarded)
say ""; say "===== L2 + witnessed localization ====="
for b in gsm8k math gpqa_diamond humaneval hle; do
  say "### $b — L2 ###"
  stage "L2-$b" "$R/$b-L2.log" suite --benchmark "$b" --rung L2 --real --live --limit 200 --max-cost-usd 200 --out "$R/$b-L2" || true
  stage "localize-$b" "$R/$b-localize.out" localize --benchmark "$b" --real --live --limit 40 --max-cost-usd 80 --out "$R/$b-localize.json" || true
done

# 3) Regime-2 oracle-less audit
say ""; say "===== Regime-2 ====="
for b in hle math; do stage "regime2-$b" "$R/regime2-$b.out" regime2 --benchmark "$b" --real --live --limit 40 --max-cost-usd 80 --out "$R/regime2-$b" || true; done

# 4) agent-env (offline, always works) + SWE readiness
say ""; say "===== agent-env + SWE ====="
CLI agentenv --tasks 100 --out "$R/agentenv" >"$R/agentenv.out" 2>&1 && say "  DONE agent-env" || true
CLI swebench-attacks --cases 40 --out "$R/swebench-attacks" >"$R/swebench-attacks.out" 2>&1 && say "  DONE swebench-attacks (offline)" || true
CLI swebench-check >"$R/swebench-check.out" 2>&1 || true

say ""; say "################ DONE @ $(date +%H:%M:%S) — bundles under $R ################"
