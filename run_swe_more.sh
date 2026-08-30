#!/usr/bin/env bash
# Continue the SWE-bench live sweep: ADD fresh instances onto what you already have,
# then merge everything into ONE re-validated bundle (results/swe-merged) that
# run_research.sh reads. Safe to run repeatedly -- each run resumes, never redoes.
#
#   bash run_swe_more.sh                 # add up to 12 fresh instances, then merge
#   LIMIT=25 bash run_swe_more.sh        # aim to add 25 (disk permitting)
#   caffeinate -i bash run_swe_more.sh   # keep the Mac awake for a long batch
#
# THE ONE HARD LIMIT is disk: macOS never shrinks Docker.raw, so free host disk only
# falls as task images accumulate. If a batch stops on the disk floor, reclaim space
# (see the DISK note this script prints) and just run it again -- it picks up where it
# stopped. run_swe.sh must have proven the oracle at least once before you use this.
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"

LIMIT="${LIMIT:-12}"
MIN_FREE="${MIN_FREE_GB:-12}"
BASE="${SWE_BASE:-results/swe-live-20260830-132756/live}"   # the validated stratified baseline
STAMP="$(date +%Y%m%d-%H%M%S)"; OUT="results/swe-cont-$STAMP"; mkdir -p "$OUT"
say(){ echo "$@" | tee -a "$OUT/more.log"; }

[ -f .env ] && { set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a; }

ARCH="$(uname -m)"
if [ -z "${DOCKER_DEFAULT_PLATFORM:-}" ] && { [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; }; then
  export DOCKER_DEFAULT_PLATFORM=linux/amd64   # prebuilt SWE images are x86_64 (emulated on Apple Silicon)
fi

say "################ SWE CONTINUE @ $STAMP (add up to $LIMIT; disk floor ${MIN_FREE}GB) ################"

DONE=$(python3 -c "
from glob import glob
from gradia_wind_tunnel.swebench_live import collect_done_ids
d=['$BASE']+sorted(glob('results/swe-cont-*/live'))+['results/swe-merged']
print(len(collect_done_ids([x for x in d if x])))" 2>/dev/null || echo '?')
say "  instances already in hand: $DONE  (this batch skips them and adds NEW ones)"

# ---- readiness (Docker + swebench). run_swe.sh installs + proves the oracle first. ----
if ! python3 -c "import swebench" 2>/dev/null; then
  say "  swebench not importable -- run 'bash run_swe.sh' once first (installs it + proves the oracle). Aborting."; exit 1
fi
if ! python3 -c "from gradia_wind_tunnel.swebench_harness import harness_ready as h;import sys;sys.exit(0 if h()['ready'] else 1)"; then
  say "  HARNESS NOT READY -- the Docker daemon isn't answering. Start Docker Desktop, verify with 'docker run --rm hello-world', then re-run. Aborting."; exit 1
fi
say "  harness READY"

# ---- disk preflight ----
FREE_GB=$(df -g / 2>/dev/null | awk 'NR==2{print $4}'); [ -z "$FREE_GB" ] && FREE_GB=$(df -k / 2>/dev/null | awk 'NR==2{printf "%d",$4/1048576}')
say "  free disk: ${FREE_GB}GB (floor ${MIN_FREE}GB)"
if [ "${FREE_GB:-0}" -lt "$MIN_FREE" ] 2>/dev/null; then
  say ""
  say "  LOW DISK. IMPORTANT: on macOS, 'docker system prune' frees space INSIDE Docker.raw but"
  say "  does NOT return GBs to the host -- Docker.raw never shrinks on its own. To actually"
  say "  reclaim host disk you must SHRINK the Docker disk image:"
  say "    Docker Desktop -> Settings -> Resources -> Advanced -> lower 'Disk image size'  (fastest)"
  say "    or  Docker Desktop -> Troubleshoot -> 'Clean / Purge data'  (nukes all images)"
  say "  After either, run 'bash run_swe.sh' ONCE (re-pulls + re-proves the oracle), then this script again."
  say "  (Or just free space elsewhere until free disk > ${MIN_FREE}GB.)"
  exit 1
fi

# ---- resume: add fresh instances, skipping everything already measured ----
say ""; say "===== resume: add up to $LIMIT fresh instances -> $OUT/live ====="
python3 -m gradia_wind_tunnel.cli swebench-live --stratified --limit "$LIMIT" --min-free-gb "$MIN_FREE" \
  --skip-done "$BASE" --skip-done "results/swe-cont-*/live" --skip-done "results/swe-merged" \
  --out "$OUT/live" 2>&1 | tee -a "$OUT/more.log" | tail -60

# ---- merge the validated baseline + every continuation -> ONE re-validated bundle ----
say ""; say "===== merge baseline + all continuations -> results/swe-merged ====="
python3 -m gradia_wind_tunnel.cli swebench-merge \
  "$BASE" "results/swe-cont-*/live" \
  --out results/swe-merged 2>&1 | tee -a "$OUT/more.log" | tail -45

say ""
if grep -q '"VALID": true' "$OUT/more.log" 2>/dev/null; then
  say "################ DONE -- results/swe-merged is the combined, re-validated bundle ################"
  say "  fold it into every paper number:   bash run_research.sh"
else
  say "################ batch finished -- check $OUT/more.log for the merged VALID verdict ################"
fi
