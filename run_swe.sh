#!/usr/bin/env bash
# SWE-bench reward-hacking — offline catalog (ALWAYS, Docker-free) + live Docker run (best-effort).
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
if python3 -m gradia_wind_tunnel.cli swebench-attacks --cases 20 --out "$OUT/offline" 2>&1 | tee -a "$OUT/swe.log" | tail -30; then
  say "  offline catalog OK -> $OUT/offline"
else
  say "  offline catalog reported an error (see log above)"
fi

# ---- [1/5] install harness (live path only) ----
say ""; say "===== [1/5] install the harness (live path) ====="
python3 -c "import swebench" 2>/dev/null || { say "  installing swebench..."; pip install swebench 2>&1 | tail -5 | tee -a "$OUT/swe.log"; }
if ! python3 -c "import swebench" 2>/dev/null; then
  say "  swebench not importable — SKIPPING live run. Offline numbers above stand."
  say "################ DONE (offline only) — bundle: $OUT ################"; exit 0
fi
say "  swebench ready"

# ---- [2/5] readiness ----
say ""; say "===== [2/5] readiness ladder ====="
python3 -m gradia_wind_tunnel.cli swebench-check 2>&1 | tee -a "$OUT/swe.log" | tail -20
if ! python3 -c "from gradia_wind_tunnel.swebench_harness import harness_ready as h;import sys;sys.exit(0 if h()['ready'] else 1)"; then
  say "  harness not ready (is Docker running?) — SKIPPING live run. Offline numbers stand."
  say "################ DONE (offline only) — bundle: $OUT ################"; exit 0
fi
say "  READY"

# ---- [2.5/5] pre-pull task images (namespaced, pullable) ----
say ""; say "===== [2.5/5] pre-pull task images ====="
PLATARG=""; [ -n "${DOCKER_DEFAULT_PLATFORM:-}" ] && PLATARG="--platform ${DOCKER_DEFAULT_PLATFORM}"
python3 - "$LIMIT" > "$OUT/images.txt" 2>/dev/null <<'PYIMG'
import sys
try:
    from gradia_wind_tunnel.swebench_live import load_live_cases
    from gradia_wind_tunnel.swebench_harness import instance_image_name
    for case, _ in load_live_cases(int(sys.argv[1])):
        print(instance_image_name(case.instance_id))
except Exception:
    pass
PYIMG
if [ -s "$OUT/images.txt" ]; then
  while read -r img; do
    [ -z "$img" ] && continue
    if docker image inspect "$img" >/dev/null 2>&1; then say "  already local: $img";
    else
      say "  pulling $img (multi-GB, slow under emulation)"
      if docker pull $PLATARG "$img" >"$OUT/pull.log" 2>&1; then say "    pulled OK";
      else say "    pull failed (harness will try to build during the run); tail:"; tail -3 "$OUT/pull.log" | tee -a "$OUT/swe.log"; fi
    fi
  done < "$OUT/images.txt"
else
  say "  could not resolve image names — harness will build/pull during the run"
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
else say "  gold smoke did not report smoke_ok:true — see $OUT/swe-gold.log (continuing; self-validation refuses to report if the oracle is unreliable)"; fi

# ---- [4/5] LIVE run ----
say ""; say "===== [4/5] LIVE reward-hacking run (limit=$LIMIT) ====="
python3 -m gradia_wind_tunnel.cli swebench-live --limit "$LIMIT" --out "$OUT/live" 2>&1 | tee -a "$OUT/swe.log" | tail -50

say ""
if grep -q '"VALID": true' "$OUT/swe.log" 2>/dev/null; then
  say "################ LIVE RUN IS VALID — numbers are real ################"
elif grep -q '"VALID": false' "$OUT/swe.log" 2>/dev/null; then
  say "################ LIVE RUN INVALID — controls failed; offline catalog still valid ################"
  say "  (self-validation refused to report exploit numbers; the 'problems' list above says why)"
else
  say "################ LIVE RUN produced no validity verdict — see $OUT/swe.log ################"
fi
say ""; say "################ DONE — offline: $OUT/offline | live: $OUT/live ################"
