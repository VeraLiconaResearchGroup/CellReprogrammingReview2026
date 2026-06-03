#!/usr/bin/env bash
# Regenerate Supporting Information S5 bibliometric CSVs and plot.
# Author: Paola Vera-Licona (Vera-Licona Research Group)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

EMAIL="${NCBI_EMAIL:-}"
if [[ -z "$EMAIL" || "$EMAIL" == "your.email@institution.edu" ]]; then
  echo "Set NCBI_EMAIL to your institutional email, e.g.:"
  echo "  NCBI_EMAIL=you@uni.edu docker compose run --rm run-bibliometric"
  exit 1
fi

PYTHON="${PYTHON:-python3}"

mkdir -p bibliometric/results
"$PYTHON" bibliometric/bibliometric_analysis.py \
  --email "$EMAIL" \
  --start-year 2014 \
  --end-year 2026 \
  --output-dir bibliometric/results

echo ""
echo "Done. Outputs in bibliometric/results/"
