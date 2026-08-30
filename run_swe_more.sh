#!/usr/bin/env bash
# Grow the SWE-bench live sweep toward a TARGET total (default 60), resuming across runs
# and merging everything into ONE re-validated bundle (results/swe-merged). It never
# redoes an instance. Run it; when it stops short, reclaim disk and run it again.
#
#   caffeinate -i bash run_swe_more.sh              # aim for 60 clean total
#   TARGET=30 caffeinate -i bash run_swe_more.sh    # aim for a smaller total
#   LIMIT=8   caffeinate -i bash run_swe_more.sh    # cap THIS batch at 8 new instances
#
# macOS never shrinks Docker.raw on its own, so this prunes Docker aggressively between
# instances (--prune-all) and prints free disk before/after. If your Docker Desktop TRIMs
# its disk image you may reach the target in one long run; if not, a batch stops on the
# disk floor -- reclaim space (instructions printed) and re-run. run_swe.sh must have
# proven the oracle at least once first.
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

TARGET="${TARGET:-60}"
MIN_FREE="${MIN_FREE_GB:-10}"
BASE="${SWE_BASE:-results/swe-live-20260830-132756/live}"   # validated stratified baseline
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="results/swe-cont-$STAMP"; mkdir -p "$OUT"
say(){ echo "$@" | tee -a "$OUT/more.log"; }
freeg(){ df -g / 2>/dev/null | awk 'NR==2{print $4}'; }

[ -f .env ] && { set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a; }
ARCH="$(uname -m)"
if [ -z "${DOCKER_DEFAULT_PLATFORM:-}" ] && { [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; }; then
  export DOCKER_DEFAULT_PLATFORM=linux/amd64
fi

CLEAN=$(python3 -c "import json;print(json.load(open('results/swe-merged/manifest.json'))['n_instances'])" 2>/dev/null || echo 0)
REMAIN=$(( TARGET - CLEAN )); [ "$REMAIN" -lt 0 ] && REMAIN=0
BATCH="${LIMIT:-$REMAIN}"

say "################ SWE -> TARGET $TARGET  (have $CLEAN clean, need $REMAIN more) @ $STAMP ################"
if [ "$REMAIN" -le 0 ]; then
  say "  TARGET ALREADY REACHED ($CLEAN >= $TARGET). Fold into the paper:  bash run_research.sh"; exit 0
fi

# ---- readiness ----
if ! python3 -c "import swebench" 2>/dev/null; then say "  swebench missing -- run 'bash run_swe.sh' once first. Aborting."; exit 1; fi
if ! python3 -c "from gradia_wind_tunnel.swebench_harness import harness_ready as h;import sys;sys.exit(0 if h()['ready'] else 1)"; then
  say "  HARNESS NOT READY -- start Docker Desktop, verify 'docker run --rm hello-world', re-run. Aborting."; exit 1; fi
say "  harness READY"

# ---- disk preflight ----
FREE0=$(freeg); [ -z "$FREE0" ] && FREE0=999
say "  free disk before: ${FREE0}GB (floor ${MIN_FREE}GB)"
if [ "${FREE0:-0}" -lt "$MIN_FREE" ] 2>/dev/null; then
  say ""; say "  LOW DISK before we start. Reclaim first:"
  say "    fastest: Docker Desktop -> Settings -> Resources -> Advanced -> lower 'Disk image size' -> Apply & Restart"
  say "    or:      Docker Desktop -> Troubleshoot -> 'Clean / Purge data'  (nukes all images)"
  say "    then 'bash run_swe.sh' once (re-proves the oracle), then this script again."
  exit 1
fi

# ---- resume: add up to BATCH fresh instances, pruning Docker between each ----
say ""; say "===== adding up to $BATCH fresh instance(s) toward $TARGET (prune-all between each) -> $OUT/live ====="
python3 -m gradia_wind_tunnel.cli swebench-live --stratified --limit "$BATCH" --min-free-gb "$MIN_FREE" --prune-all \
  --skip-done "$BASE" --skip-done "results/swe-cont-*/live" --skip-done "results/swe-merged" \
  --out "$OUT/live" 2>&1 | tee -a "$OUT/more.log" | tail -60
[ -f "$OUT/live/progress.txt" ] && { say ""; say "  last checkpoint: $(tail -1 "$OUT/live/progress.txt")"; }

# ---- merge baseline + all continuations -> ONE re-validated bundle ----
say ""; say "===== merge baseline + all continuations -> results/swe-merged ====="
python3 -m gradia_wind_tunnel.cli swebench-merge "$BASE" "results/swe-cont-*/live" --out results/swe-merged 2>&1 | tee -a "$OUT/more.log" | tail -30

# ---- recount + report ----
CLEAN=$(python3 -c "import json;print(json.load(open('results/swe-merged/manifest.json'))['n_instances'])" 2>/dev/null || echo '?')
FREE1=$(freeg); [ -z "$FREE1" ] && FREE1=999
say ""; say "  merged bundle now: $CLEAN clean instance(s)  |  free disk ${FREE0}GB -> ${FREE1}GB (after run, before prune)"
if [ "${CLEAN:-0}" -ge "$TARGET" ] 2>/dev/null; then
  say "################ TARGET $TARGET REACHED ($CLEAN clean). Now:  bash run_research.sh ################"
  exit 0
fi
say "  reclaiming docker space (system prune)..."
docker system prune -af --volumes >/dev/null 2>&1 && say "  pruned -> free disk now: $(freeg)GB"
if [ "$(freeg 2>/dev/null || echo 999)" -lt "$MIN_FREE" ] 2>/dev/null; then
  say ""; say "  Host disk did NOT recover from prune -> your Docker doesn't auto-trim Docker.raw."
  say "  Shrink the Docker disk image ONCE, then keep going:"
  say "    Docker Desktop -> Settings -> Resources -> Advanced -> lower 'Disk image size' -> Apply & Restart"
  say "    then 'bash run_swe.sh' once, then 'bash run_swe_more.sh' again."
else
  say "################ at $CLEAN / $TARGET -- disk healthy, just run 'bash run_swe_more.sh' again ################"
fi
