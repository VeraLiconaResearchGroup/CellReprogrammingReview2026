# Computational Cell Reprogramming Review — Reproduction Materials

**Author:** Paola Vera-Licona (veralicona@uchc.edu)  
**Affiliation:** University of Connecticut School of Medicine, Farmington, CT, USA

Public reproduction package for the PLOS Computational Biology submission  
*Computational Cell Reprogramming: A Systematic Review of Cellular Intervention Design* (Vera-Licona Research Group, 2026).

This repository contains the scripts and data needed to regenerate the figures and tables named in the Data Availability statement. The bibliometric analysis is not part of this submission.

| Manuscript artifact | Folder | Output |
| --- | --- | --- |
| Main-text Figure 1 (assignment of Classes C0 to C3) | [`figure1/`](figure1/) | `Fig1_assignment.{pdf,png,tiff,eps}` |
| Main-text Figure 2 (settings and classes) | [`figure2/`](figure2/) | `Fig2_settings_classes.{pdf,png,tiff,eps}` |
| Supporting Information S1, Figure 1 (Waddington landscape) | [`s1_figure1/`](s1_figure1/) | `Fig1.tiff` from the PowerPoint source |
| S4 Fig (resource audit) | [`s4_fig/`](s4_fig/) | `S4_fig.{pdf,png,tiff,eps}` |
| SI_3 table (resource audit) | [`data/`](data/) | `SI_3_ResourceAudit.xlsx` |
| SI_5 table (dataset reuse) | [`dataset_reuse/`](dataset_reuse/) | `SI_5_DatasetReuse.xlsx` |
| Frozen workbook copies | [`supporting_information/`](supporting_information/) | SI_2 table, SI_3 table, and SI_5 table |

S1, Figure 1 is exported from the slide in `s1_figure1/` with PowerPoint. The Docker workflow regenerates Figures 1 and 2, S4 Fig, and SI_5 table. SI_3 table is the resource-audit workbook; S4 Fig is drawn from the same audit (`data/audit_source.csv`). SI_2 table is included as a frozen copy of the methods catalogue and is not rebuilt by these scripts.

## Quick start (Docker — recommended)

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose plugin).

```bash
# Build the image once
docker compose build

# Regenerate Figures 1 and 2, S4 Fig, and SI_5 table (offline, ~1–2 minutes)
docker compose run --rm run-offline

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
| [`notebooks/00_Run_All_Offline.ipynb`](notebooks/00_Run_All_Offline.ipynb) | Figure 1 → Figure 2 → S4 Fig → SI_5 table |
| [`notebooks/01_Figure1_Assignment.ipynb`](notebooks/01_Figure1_Assignment.ipynb) | Figure 1 only |
| [`notebooks/02_Figure2_SettingsClasses.ipynb`](notebooks/02_Figure2_SettingsClasses.ipynb) | Figure 2 only |
| [`notebooks/03_S4_Fig_ResourceAudit.ipynb`](notebooks/03_S4_Fig_ResourceAudit.ipynb) | S4 Fig only |
| [`notebooks/04_DatasetReuse_Table.ipynb`](notebooks/04_DatasetReuse_Table.ipynb) | SI_5 table only |

Notebooks call the same Python scripts as the command-line workflow.

## Quick start (command line)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
bash scripts/run_offline.sh
```

### Individual scripts

**Figure 1**

```bash
cd figure1 && python fig1_assignment.py
```

**Figure 2**

```bash
cd figure2 && python preview_rows.py
```

Reference numbers on Figure 2 are frozen in `figure2/citekey_to_ref_num.json` (PLOS citeproc order from the compiled manuscript).

**S4 Fig**

```bash
python s4_fig/render_s4_fig.py
```

Reads `data/audit_source.csv` (aligned with `data/SI_3_ResourceAudit.xlsx`). Trip-wire asserts check the Section 5 counts drawn on S4 Fig: 59 single-class methods, 45 of them with code, 26 of those bars at 4 of 4, and 15 of 45 with a FAIR4RS-based score of 3 or higher. With OCSANA+ included, SI_3 table counts 46 methods with downloadable code and 27 with all four resources.

**SI_5 table**

```bash
cd dataset_reuse && python build_si_4_xlsx.py
```

**Supporting Information S1, Figure 1**

See [`s1_figure1/README.md`](s1_figure1/README.md). This step needs PowerPoint or LibreOffice and is not run inside Docker.

## Repository layout

```
CellReprogrammingReview2026/
├── data/                         # SI_3 table + audit CSV for S4 Fig
├── supporting_information/       # Frozen SI_2, SI_3, and SI_5 workbooks
├── notebooks/                    # Guided Jupyter notebooks
├── scripts/                      # run_offline.sh
├── figure1/                      # Main-text Figure 1
├── figure2/                      # Main-text Figure 2 + reference map
├── s1_figure1/                   # Supporting Information S1, Figure 1
├── s4_fig/                       # S4 Fig
├── dataset_reuse/                # SI_5 table builder + input CSVs
├── Dockerfile
├── docker-compose.yml
├── requirements.txt              # figures + SI_5 table
├── requirements-all.txt          # core + Jupyter
└── LICENSE                       # MIT (code)
```

## Licenses

- **Code** (Python scripts, notebooks, Docker files): [MIT License](LICENSE)
- **Data** (CSV/xlsx tables in `data/`, `dataset_reuse/data/`, and `supporting_information/`, and the S1 Figure 1 slide): CC BY 4.0

## Citation

If you use these materials, please cite the PLOS Computational Biology article
(DOI to be added upon acceptance) and this repository:

> Vera-Licona, P. (2026). *Computational Cell Reprogramming Review —
> Reproduction Materials*. GitHub: VeraLiconaResearchGroup/CellReprogrammingReview2026.
