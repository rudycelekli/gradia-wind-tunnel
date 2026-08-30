#!/usr/bin/env bash
# SWE-bench live reward-hacking — one command, no paste hazards.
#   bash run_swe.sh            (defaults to 1 instance)
#   LIMIT=3 bash run_swe.sh
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
LIMIT="${LIMIT:-1}"
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="results/swe-live-$STAMP"; mkdir -p "$OUT"
say(){ echo "$@" | tee -a "$OUT/swe.log"; }

# make HF_TOKEN available to plain `python -c` calls too (the CLI loads .env itself)
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
say "################ SWE-bench LIVE @ $STAMP (limit=$LIMIT) ################"
say "  $PLATNOTE"

say ""; say "===== [1/4] install the harness ====="
if python3 -c "import swebench" 2>/dev/null; then
  say "  swebench already installed"
else
  say "  installing swebench (this can take a few minutes)..."
  pip install swebench 2>&1 | tail -5 | tee -a "$OUT/swe.log"
  python3 -c "import swebench" 2>/dev/null || { say "  FATAL: swebench still not importable. Try: python3 -m pip install swebench"; exit 1; }
  say "  swebench installed"
fi

say ""; say "===== [2/4] readiness ladder ====="
python3 -m gradia_wind_tunnel.cli swebench-check 2>&1 | tee -a "$OUT/swe.log" | tail -20
python3 -c "
import json,sys
from gradia_wind_tunnel.swebench_harness import harness_ready
r=harness_ready(); sys.exit(0 if r['ready'] else 1)" || { say "  FATAL: harness not ready (see above)"; exit 1; }
say "  READY"

say ""; say "===== [2.5/4] pre-pull task images for the host platform ====="
say "  (DOCKER_DEFAULT_PLATFORM only affects the docker CLI; swebench pulls via docker-py,"
say "   which ignores it — so we pull explicitly here and swebench then finds them locally)"
PLATARG=""
[ -n "${DOCKER_DEFAULT_PLATFORM:-}" ] && PLATARG="--platform ${DOCKER_DEFAULT_PLATFORM}"
python3 - "$LIMIT" > "$OUT/images.txt" 2>/dev/null <<'PYIMG'
import sys
try:
    from gradia_wind_tunnel.swebench_live import load_live_cases
    from gradia_wind_tunnel.swebench_harness import instance_image_name
    for case, _ in load_live_cases(int(sys.argv[1])):
        print(instance_image_name(case.instance_id))
except Exception as e:
    print("", file=sys.stderr)
PYIMG
if [ -s "$OUT/images.txt" ]; then
  while read -r img; do
    [ -z "$img" ] && continue
    if docker image inspect "$img" >/dev/null 2>&1; then
      say "  already local: $img"
    else
      say "  pulling $img"
      say "    (multi-GB under $DOCKER_DEFAULT_PLATFORM emulation — this is the slow step)"
      if docker pull $PLATARG "$img" >"$OUT/pull.log" 2>&1; then
        say "    pulled OK"
      else
        say "    PULL FAILED — tail:"; tail -3 "$OUT/pull.log" | tee -a "$OUT/swe.log"
        say "    If the image truly has no x86_64 build, fall back to building locally:"
        say "      python3 -m swebench.harness.prepare_images --instance_ids <id> --max_workers 2"
      fi
    fi
  done < "$OUT/images.txt"
else
  say "  could not resolve image names (dataset/network?) — continuing"
fi

say ""; say "===== [3/4] prove the ORACLE (gold patch must RESOLVE) ====="
say "  first run pulls a multi-GB task image — expect several minutes"
python3 -c "
import json
from gradia_wind_tunnel.swebench_harness import gold_patch_smoke
r = gold_patch_smoke()
print(json.dumps({k:v for k,v in r.items() if k!='report'}, indent=2))
" 2>&1 | tee -a "$OUT/swe-gold.log" | tail -25
if grep -q '"smoke_ok": true' "$OUT/swe-gold.log" 2>/dev/null; then
  say "  ORACLE PROVEN (gold patch resolves) ✓"
else
  say "  gold smoke did NOT report smoke_ok:true — see $OUT/swe-gold.log"
  say "  (continuing to the live run anyway; the oracle column may be unreliable)"
fi

say ""; say "===== [4/4] LIVE reward-hacking run ====="
python3 -m gradia_wind_tunnel.cli swebench-live --limit "$LIMIT" --out "$OUT/live" 2>&1 | tee -a "$OUT/swe.log" | tail -40

say ""
if grep -q '"VALID": true' "$OUT/swe.log" 2>/dev/null; then
  say "################ RUN IS VALID — numbers are real ################"
elif grep -q '"VALID": false' "$OUT/swe.log" 2>/dev/null; then
  say "################ RUN IS INVALID — controls failed; DO NOT USE THESE NUMBERS ################"
  say "  the 'problems' list above says exactly what broke"
fi
say ""; say "################ DONE — bundle: $OUT/live ################"
say "verify: PYTHONPATH=src python3 -c \"import json;from pathlib import Path;from gradia_wind_tunnel.capture import verify_bundle;m=json.load(open('$OUT/live/manifest.json'));print(verify_bundle(Path('$OUT/live/frames.ndjson'),m))\""
