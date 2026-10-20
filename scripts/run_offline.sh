#!/usr/bin/env bash
# Regenerate main-text Figures 1 and 2, S4 Fig, and SI_5 table.
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

echo "==> S4 Fig (resource audit)"
"$PYTHON" s4_fig/render_s4_fig.py

echo "==> SI_5 table (dataset reuse)"
(cd dataset_reuse && "$PYTHON" build_si_4_xlsx.py)

echo ""
echo "Done. Outputs:"
echo "  figure1/Fig1_assignment.{pdf,png,tiff,eps}"
echo "  figure2/Fig2_settings_classes.{pdf,png,tiff,eps}"
echo "  s4_fig/S4_fig.{pdf,png,tiff,eps}"
echo "  dataset_reuse/SI_5_DatasetReuse.xlsx"
