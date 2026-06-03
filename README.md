# Computational Cell Reprogramming Review — Reproduction Materials

**Authors:** Martha Vera Licona; Paola Vera-Licona (corresponding author, veralicona@uchc.edu)  
**Affiliation:** Vera-Licona Research Group, University of Connecticut School of Medicine, Farmington, CT, USA

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

## Quick start (Docker — recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose plugin).

```bash
# Build the image once
docker compose build

# Regenerate Figure 2, Figure 3, and SI_4 (offline, ~1 minute)
docker compose run --rm run-offline

# Bibliometric analysis (network + your NCBI email; ~10–20 minutes)
NCBI_EMAIL=you@institution.edu docker compose run --rm run-bibliometric

# JupyterLab with guided notebooks
docker compose up jupyter
# Open http://localhost:8888 and open notebooks/00_Run_All_Offline.ipynb
```

Outputs are written into this repository folder (mounted as a volume), so they persist after the container exits.

## Quick start (Jupyter notebooks)

From the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-all.txt
jupyter lab notebooks/
```

| Notebook | What it runs |
| --- | --- |
| [`notebooks/00_Run_All_Offline.ipynb`](notebooks/00_Run_All_Offline.ipynb) | Figure 3 → Figure 2 → SI_4 |
| [`notebooks/01_Figure3_Reproducibility.ipynb`](notebooks/01_Figure3_Reproducibility.ipynb) | Figure 3 only |
| [`notebooks/02_Figure2_ModalityUpSet.ipynb`](notebooks/02_Figure2_ModalityUpSet.ipynb) | Figure 2 only |
| [`notebooks/03_DatasetReuse_Table.ipynb`](notebooks/03_DatasetReuse_Table.ipynb) | SI_4 xlsx only |
| [`notebooks/04_Bibliometric_Analysis.ipynb`](notebooks/04_Bibliometric_Analysis.ipynb) | SI_5 (set email first; needs network) |

Notebooks call the same Python scripts as the command-line workflow — they are thin wrappers, not duplicate logic.

## Quick start (command line)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_offline.sh
```

For bibliometrics, also `pip install -r bibliometric/requirements_bibliometric.txt`, then:

```bash
NCBI_EMAIL=you@institution.edu bash scripts/run_bibliometric.sh
```

### Individual scripts

**Figure 2**

```bash
cd figure2 && python fig2_modality_upset.py
```

**Figure 3**

```bash
cd figure3 && python fig3_reproducibility.py
```

Reads `data/SI_3_ReproducibilityAudit.xlsx`. Trip-wire asserts verify headline Section 5 counts (27 runnable, 43 with code, 14 FAIR4RS ≥ 3).

**Supporting Information S4**

```bash
cd dataset_reuse && python build_si_4_xlsx.py
```

**Supporting Information S5**

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
├── notebooks/                    # Guided Jupyter notebooks
├── scripts/                      # run_offline.sh, run_bibliometric.sh
├── reproducibility_audit/        # audit notes + optional xlsx legend patch
├── figure2/                      # Figure 2 scripts + reference map
├── figure3/                      # Figure 3 script
├── dataset_reuse/                # SI_4 builder + input CSVs
├── bibliometric/                 # SI_5 PubMed/PMC queries
├── Dockerfile
├── docker-compose.yml
├── requirements.txt              # core deps (figures + SI_4)
├── requirements-all.txt          # core + bibliometric + Jupyter
└── LICENSE                       # MIT (code)
```

## Licenses

- **Code** (Python scripts, notebooks, Docker files): [MIT License](LICENSE)
- **Data** (CSV/xlsx tables in `data/` and `dataset_reuse/data/`): CC BY 4.0

## Citation

If you use these materials, please cite the PLOS Computational Biology article
(DOI to be added upon acceptance) and this repository:

> Vera Licona, M.; Vera-Licona, P. (2026). *Computational Cell Reprogramming Review —
> Reproduction Materials*. GitHub: VeraLiconaResearchGroup/CellReprogrammingReview2026.
