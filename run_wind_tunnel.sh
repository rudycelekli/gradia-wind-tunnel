#!/usr/bin/env bash
# Gradia Wind Tunnel — overnight run (the machine-checkable benchmarks).
# Runs in YOUR terminal: needs your network + the Anthropic key already in .env.
# Safe by design: smoke-tests each benchmark first (tiny), per-benchmark fail-closed
# cost cap, SKIPS (never aborts the night) on any single failure, logs everything.
#
#   bash run_wind_tunnel.sh                 # defaults: 50 items/bench, $40 cap/bench
#   LIMIT=200 CAP=60 bash run_wind_tunnel.sh   # fuller run (matches prereg 200/cell)
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

PREREG="preregistrations/gradia-wind-tunnel-phase0-20260829-03.json"
BENCHES=(gsm8k math gpqa_diamond humaneval hle)
LIMIT="${LIMIT:-50}"; CAP="${CAP:-40}"; SMOKE=2
STAMP="$(date +%Y%m%d-%H%M%S)"; LOG="results/overnight-$STAMP"; mkdir -p "$LOG"
CLI() { python3 -m gradia_wind_tunnel.cli "$@"; }
say() { echo "$@" | tee -a "$LOG/run.log"; }

say "=== Gradia Wind Tunnel overnight run @ $STAMP ==="
say "log dir: $LOG   LIMIT=$LIMIT items/bench   CAP=\$$CAP/bench (fail-closed)"

python3 -c "import datasets" 2>/dev/null || { say "FATAL: 'datasets' missing -> run:  pip install -e \".[real]\""; exit 1; }
CLI prereg-verify "$PREREG" >/dev/null 2>&1 || { say "FATAL: prereg-verify failed for $PREREG"; exit 1; }
say "preflight OK (datasets present; prereg $PREREG verified)"

ok=(); skipped=()
for b in "${BENCHES[@]}"; do
  say ""; say "### $b — smoke ($SMOKE items) ###"
  if CLI suite --benchmark "$b" --real --live --limit "$SMOKE" --max-cost-usd 5 --out "$LOG/smoke-$b" >"$LOG/smoke-$b.log" 2>&1; then
    say "  smoke OK -> full run ($LIMIT items, cap \$$CAP)"
    if CLI suite --benchmark "$b" --real --live --limit "$LIMIT" --max-cost-usd "$CAP" --out "$LOG/$b" >"$LOG/$b.log" 2>&1; then
      spent=$(python3 -c "import json;print(json.load(open('$LOG/$b/manifest.json'))['spend']['spent_usd'])" 2>/dev/null || echo '?')
      say "  DONE $b — spent \$$spent — bundle: $LOG/$b/manifest.json"; ok+=("$b")
    else
      say "  FULL RUN FAILED ($b) — see $LOG/$b.log:"; tail -4 "$LOG/$b.log" | tee -a "$LOG/run.log"; skipped+=("$b")
    fi
  else
    say "  SMOKE FAILED ($b) — skipping — see $LOG/smoke-$b.log:"; tail -4 "$LOG/smoke-$b.log" | tee -a "$LOG/run.log"; skipped+=("$b")
  fi
done

say ""; say "=== SUMMARY ==="
say "completed: ${ok[*]:-none}"
say "skipped:   ${skipped[*]:-none}"
say "verify any bundle:  PYTHONPATH=src python3 -m gradia_wind_tunnel.cli verify-report $LOG/<bench>/manifest.json"
[ ${#ok[@]} -eq 0 ] && say "NOTHING COMPLETED — most likely GRADIA_WT_MODEL=claude-opus-5 isn't a valid id for your account, or the key/gateway. Check $LOG/smoke-gsm8k.log."
