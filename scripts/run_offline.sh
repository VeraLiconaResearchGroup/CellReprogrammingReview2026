#!/usr/bin/env bash
# Regenerate main-text Figures 1 and 2, Supporting Information S3 Figure 1, and S4.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
export MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/matplotlib}"
mkdir -p "$MPLCONFIGDIR"

echo "==> Main-text Figure 1 (assignment tree)"
(cd figure1 && "$PYTHON" fig1_assignment.py)

echo "==> Main-text Figure 2 (settings and classes)"
(cd figure2 && "$PYTHON" preview_rows.py)

echo "==> Supporting Information S3, Figure 1 (resource audit)"
"$PYTHON" s3_figure1/render_s3_fig1.py

echo "==> Supporting Information S4 (dataset reuse xlsx)"
(cd dataset_reuse && "$PYTHON" build_si_4_xlsx.py)

echo ""
echo "Done. Outputs:"
echo "  figure1/Fig1_assignment.{pdf,png,tiff,eps}"
echo "  figure2/Fig2_settings_classes.{pdf,png,tiff,eps}"
echo "  s3_figure1/S3_Fig1.{pdf,png,tiff,eps}"
echo "  dataset_reuse/SI_4_DatasetReuse.xlsx"
