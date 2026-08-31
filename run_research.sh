#!/usr/bin/env bash
# Regenerate every research number + the living gameability index from the LATEST
# evidence bundles, in one command. Re-run any time new L1/L2/SWE/HLE runs land.
set -uo pipefail
cd "$(cd "$(dirname "$0")" && pwd)"
export PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}"
[ -f .env ] && { set -a; . <(grep -E '^[A-Za-z_][A-Za-z0-9_]*=' .env | sed 's/[[:space:]]*$//'); set +a; }
OUT="${OUT:-results/research-v1}"
echo "### regenerating research bundle -> $OUT"
python3 -m gradia_wind_tunnel.cli research --out "$OUT" --transfer-limit "${TLIMIT:-100}"
echo ""; echo "### living scorer gameability index"
python3 -m gradia_wind_tunnel.cli index --out "$OUT/index"
echo ""; echo "### markdown tables written:"; ls "$OUT"/*.md 2>/dev/null
echo ""; echo "### public anchoring (OpenTimestamps) -- timestamped, non-equivocating evidence"
command -v ots >/dev/null 2>&1 || pip install --quiet opentimestamps-client >/dev/null 2>&1 || true
python3 -m gradia_wind_tunnel.cli anchor || echo "  (anchoring is best-effort; the receipt records whether a stamp happened)"
