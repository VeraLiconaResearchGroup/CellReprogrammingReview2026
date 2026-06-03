#!/usr/bin/env bash
# Regenerate all offline artifacts: Figure 2, Figure 3, Supporting Information S4.
# Author: Paola Vera-Licona (Vera-Licona Research Group)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"

echo "==> Figure 3 (reproducibility audit)"
"$PYTHON" figure3/fig3_reproducibility.py

echo "==> Figure 2 (modality UpSet)"
"$PYTHON" figure2/fig2_modality_upset.py

echo "==> Supporting Information S4 (dataset reuse xlsx)"
"$PYTHON" dataset_reuse/build_si_4_xlsx.py

echo ""
echo "Done. Outputs:"
echo "  figure3/Fig3_reproducibility.{pdf,png,tiff}"
echo "  figure2/Fig2_modality_upset.{pdf,png,tiff}"
echo "  dataset_reuse/SI_4_DatasetReuse.xlsx"
