# Computational Cell Reprogramming Review — Reproduction Materials

Public reproduction package for the PLOS Computational Biology submission  
*Computational Cell Reprogramming: A Cross-Modality Framework for Cellular Intervention Design* (Vera-Licona Research Group, 2026).

This repository contains the minimal scripts and data needed to regenerate:

| Manuscript artifact | Folder | Output |
| --- | --- | --- |
| Supporting Information S3 (reproducibility audit) | [`data/`](data/) | `SI_3_ReproducibilityAudit.xlsx` |
| Figure 3 | [`figure3/`](figure3/) | `Fig3_reproducibility.{pdf,png,tiff}` |
| Figure 2 | [`figure2/`](figure2/) | `Fig2_modality_upset.{pdf,png,tiff}` |
| Supporting Information S4 (dataset reuse) | [`dataset_reuse/`](dataset_reuse/) | `SI_4_DatasetReuse.xlsx` |
| Supporting Information S5 (bibliometric analysis) | [`bibliometric/`](bibliometric/) | trend CSVs + summary plot |

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For the bibliometric script only, also install:

```bash
pip install -r bibliometric/requirements_bibliometric.txt
```

## Regenerate each artifact

### Figure 2 — modality UpSet plot

```bash
cd figure2
python fig2_modality_upset.py
```

Reference superscripts use the frozen map in `figure2/citekey_to_ref_num.json`
(matching the submitted manuscript's numbered References list).

### Figure 3 — reproducibility audit figure

```bash
cd figure3
python fig3_reproducibility.py
```

Reads scores from `data/SI_3_ReproducibilityAudit.xlsx`. Trip-wire asserts verify
the headline counts quoted in Section 5 (27 runnable, 43 with code, 14 FAIR4RS ≥ 3).

### Supporting Information S4 — dataset reuse table

```bash
cd dataset_reuse
python build_si_4_xlsx.py
```

Builds the styled xlsx from the bundled CSVs in `dataset_reuse/data/`.

### Supporting Information S5 — bibliometric analysis

Requires network access and a valid email for NCBI E-utilities.

```bash
cd bibliometric
python bibliometric_analysis.py \
  --email YOUR_EMAIL@institution.edu \
  --start-year 2014 \
  --end-year 2026 \
  --output-dir results
```

PubMed/PMC counts may drift slightly as new papers are indexed.

## Repository layout

```
CellReprogrammingReview2026/
├── data/                         # Supporting Information S3 spreadsheet
├── reproducibility_audit/        # audit notes + optional xlsx legend patch
├── figure2/                      # Figure 2 scripts + reference map
├── figure3/                      # Figure 3 script
├── dataset_reuse/                # SI_4 builder + input CSVs
├── bibliometric/                 # SI_5 PubMed/PMC queries
├── requirements.txt
└── LICENSE                       # MIT (code)
```

## Licenses

- **Code** (Python scripts): [MIT License](LICENSE)
- **Data** (CSV/xlsx tables in `data/` and `dataset_reuse/data/`): CC BY 4.0

## Citation

If you use these materials, please cite the PLOS Computational Biology article
( DOI to be added upon acceptance ) and this repository.
