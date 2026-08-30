#!/usr/bin/env bash
# SWE-bench reward-hacking -- offline catalog (ALWAYS, Docker-free) + live Docker run (best-effort).
#   bash run_swe.sh                 # offline catalog + 1 live instance
#   LIMIT=3 bash run_swe.sh         # churn more live instances (may not finish overnight)
#   caffeinate -i bash run_swe.sh   # keep the Mac awake for the whole run
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
LIMIT="${LIMIT:-1}"
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="results/swe-live-$STAMP"; mkdir -p "$OUT"
say(){ echo "$@" | tee -a "$OUT/swe.log"; }

if [ -f .env ]; then
  set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a
fi

ARCH="$(uname -m)"
if [ -z "${DOCKER_DEFAULT_PLATFORM:-}" ] && { [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; }; then
  export DOCKER_DEFAULT_PLATFORM=linux/amd64
  PLATNOTE="host is $ARCH; prebuilt SWE-bench images are x86_64 -> DOCKER_DEFAULT_PLATFORM=linux/amd64 (emulated, slower)"
else
  PLATNOTE="host arch $ARCH; DOCKER_DEFAULT_PLATFORM=${DOCKER_DEFAULT_PLATFORM:-<unset>}"
fi
say "################ SWE-bench @ $STAMP (limit=$LIMIT) ################"
say "  $PLATNOTE"

# ---- [0/5] OFFLINE catalog: Docker-free, deterministic, ALWAYS produces real numbers ----
say ""; say "===== [0/5] offline test-gaming catalog (no Docker, guaranteed) ====="
if python3 -m gradia_wind_tunnel.cli swebench-attacks --cases ${OFFLINE_CASES:-200} --out "$OUT/offline" 2>&1 | tee -a "$OUT/swe.log" | tail -30; then
  say "  offline catalog OK -> $OUT/offline"
else
  say "  offline catalog reported an error (see log above)"
fi

# ---- [1/5] install harness (live path only) ----
say ""; say "===== [1/5] install the harness (live path) ====="
python3 -c "import swebench" 2>/dev/null || { say "  installing swebench..."; pip install swebench 2>&1 | tail -5 | tee -a "$OUT/swe.log"; }
if ! python3 -c "import swebench" 2>/dev/null; then
  say "  swebench not importable -- SKIPPING live run. Offline numbers above stand."
  say "################ DONE (offline only) -- bundle: $OUT ################"; exit 0
fi
say "  swebench ready"

# ---- [2/5] readiness ----
say ""; say "===== [2/5] readiness ladder ====="
python3 -m gradia_wind_tunnel.cli swebench-check 2>&1 | tee -a "$OUT/swe.log" | tail -20
if ! python3 -c "from gradia_wind_tunnel.swebench_harness import harness_ready as h;import sys;sys.exit(0 if h()['ready'] else 1)"; then
  say "  HARNESS NOT READY -- skipping the live run (offline numbers above still stand)."
  python3 -c "
import json
from gradia_wind_tunnel.swebench_harness import docker_status
d = docker_status()
print('  docker:', json.dumps(d))
if d.get('cli') and not d.get('daemon'):
    print('  -> The Docker DAEMON is not answering. Fix it, then re-run:')
    print('     1) Quit Docker Desktop completely (whale menu -> Quit)')
    print('     2) Reopen it; if it says \'unable to start\', click the troubleshoot/bug icon')
    print('        -> Reset to factory defaults (this also reclaims its virtual disk image)')
    print('     3) Verify with:  docker run --rm hello-world')
" 2>&1 | tee -a "$OUT/swe.log"
  say "################ DONE (offline only) -- bundle: $OUT ################"; exit 0
fi
say "  READY"

# ---- [2.5/5] disk preflight (images are pulled lazily, one at a time) ----
say ""; say "===== [2.5/5] disk preflight ====="
FREE_GB=$(df -g / 2>/dev/null | awk 'NR==2{print $4}')
[ -z "$FREE_GB" ] && FREE_GB=$(df -k / 2>/dev/null | awk 'NR==2{printf "%d", $4/1048576}')
MIN_FREE="${MIN_FREE_GB:-20}"
say "  free disk: ${FREE_GB}GB (floor ${MIN_FREE}GB)"
say "  task images are pulled ONE AT A TIME and deleted after each instance, so peak"
say "  disk stays ~one image regardless of LIMIT (the old mass pre-pull filled the disk)."
if [ "${FREE_GB:-0}" -lt "$MIN_FREE" ] 2>/dev/null; then
  say "  LOW DISK -- reclaim space before the live run:"
  say "    docker system prune -af --volumes"
  say "  (skipping the live run; the offline catalog above is still valid)"
  say "################ DONE (offline only) -- bundle: $OUT ################"; exit 0
fi

# ---- [3/5] prove the ORACLE (gold patch must resolve) ----
say ""; say "===== [3/5] prove the ORACLE (gold patch must RESOLVE) ====="
python3 -c "
import json
from gradia_wind_tunnel.swebench_harness import gold_patch_smoke
r = gold_patch_smoke()
print(json.dumps({k:v for k,v in r.items() if k!='report'}, indent=2))
" 2>&1 | tee -a "$OUT/swe-gold.log" | tail -30
if grep -q '"smoke_ok": true' "$OUT/swe-gold.log" 2>/dev/null; then say "  ORACLE PROVEN (gold resolves) OK";
else say "  gold smoke did not report smoke_ok:true -- see $OUT/swe-gold.log (continuing; self-validation refuses to report if the oracle is unreliable)"; fi

# ---- [4/5] LIVE run ----
if [ "${STRATIFIED:-0}" = "1" ]; then
  say ""; say "===== [4/5] LIVE: validate 1 instance, then stratified $LIMIT (checkpoints each instance) ====="
  python3 -m gradia_wind_tunnel.cli swebench-live --limit 1 --min-free-gb "${MIN_FREE_GB:-20}" --out "$OUT/validate" 2>&1 | tee "$OUT/validate.log" | tail -30
  if grep -q '"VALID": true' "$OUT/validate.log" 2>/dev/null; then
    say "  1-instance validation VALID -> launching stratified $LIMIT (long run; safe to sleep, checkpoints to $OUT/live each instance)"
    python3 -m gradia_wind_tunnel.cli swebench-live --stratified --limit "$LIMIT" --min-free-gb "${MIN_FREE_GB:-20}" --out "$OUT/live" 2>&1 | tee -a "$OUT/swe.log" | tail -60
  else
    say "  1-instance validation did NOT report VALID:true -> NOT launching the long run (see $OUT/validate.log)"
    cat "$OUT/validate.log" >> "$OUT/swe.log"
  fi
else
  say ""; say "===== [4/5] LIVE reward-hacking run (limit=$LIMIT) ====="
  python3 -m gradia_wind_tunnel.cli swebench-live --limit "$LIMIT" --min-free-gb "${MIN_FREE_GB:-20}" --out "$OUT/live" 2>&1 | tee -a "$OUT/swe.log" | tail -50
fi

say ""
if grep -q '"VALID": true' "$OUT/swe.log" 2>/dev/null; then
  say "################ LIVE RUN IS VALID -- numbers are real ################"
elif grep -q '"VALID": false' "$OUT/swe.log" 2>/dev/null; then
  say "################ LIVE RUN INVALID -- controls failed; offline catalog still valid ################"
  say "  (self-validation refused to report exploit numbers; the 'problems' list above says why)"
else
  say "################ LIVE RUN produced no validity verdict -- see $OUT/swe.log ################"
fi
say ""; say "################ DONE -- offline: $OUT/offline | live: $OUT/live ################"
