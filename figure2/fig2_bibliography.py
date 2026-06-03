"""Bibliography indices for Figure 2 method labels.

Superscript numbers match the numbered References list in the submitted
manuscript (PLOS numeric citeproc order). The mapping is frozen in
``citekey_to_ref_num.json`` so Figure 2 can be regenerated without pandoc.
"""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REF_MAP = HERE / "citekey_to_ref_num.json"

# Figure label (fig2_modality_upset.METHODS[0]) -> BibTeX citekey
METHOD_NAME_TO_CITEKEY: dict[str, str] = {
    "Crespo & Del Sol": "crespo2013",
    "Cornelius": "cornelius2013",
    "FVS": "mochizuki2013",
    "DEPCs": "crespo2013depcs",
    "CellNet": "cellnet2014",
    "Hopfield": "hopfield2014",
    "Stable Motifs": "stablemotifs2015",
    "D'Alessio": "dalessio2015",
    "Mogrify": "mogrify2016",
    "Murrugarra": "murrugarra2016",
    "Toggle/Okawa": "okawa2016",
    "Del Vecchio": "delvecchio2017",
    "Zañudo": "zanudofvs2017",
    "DGC": "dgc2017",
    "PCK": "choo2018",
    "LDOI": "ldoi2018",
    "SeesawPred": "seesawpred2018",
    "OncoTreat": "oncotreat2018",
    "BRC": "choo2019",
    "Okawa & Del Sol": "okawa2019",
    "BoolIFFNN": "choo2020",
    "Sordo": "sordovieira2019",
    "Aguilar": "aguilar2020",
    "TransSynW": "transsynw2020",
    "OCSANA+": "marazzi2020ocsana",
    "ANANSE": "ananse2021",
    "CABEAN": "cabean2021",
    "DECCODE": "deccode2021",
    "IRENE": "irene2021",
    "Taiji-reprogram": "taiji2021",
    "CELLoGeNe": "cellogene2022",
    "cSTAR": "cstar2022",
    "Tercan": "pbns2022",
    "NETISCE": "netisce2022",
    "scREMOTE": "scremote2022",
    "TRANSDIRE": "transdire2022",
    "CellOracle": "celloracle2023",
    "DCGS": "dcgs2023",
    "scANANSE": "scananse2023",
    "PC3T": "pc3t2023",
    "SiPER": "siper2023",
    "Wytock-TL": "transferlearning2024",
    "CAESAR": "caesar2024",
    "DIRECTEUR": "directeur2024",
    "pbn-STAC": "pbnstac2025",
    "CellCartographer": "cellcartographer2025",
    "BoNesis+CABEAN": "bonesiscabean2025",
    "TFcomb": "tfcomb2025",
    "REVERT": "revert2025",
    "DrugReflector": "drugreflector2025",
    "PDGrapher": "pdgrapher2025",
    "REVIVE": "revive2025",
    "CANDiT": "candit2025",
    "SwitchTFI": "switchtfi2025",
    "TRAPT": "trapt2025",
    "Atlas-guided": "atlasguided2026",
    "REPROcode": "reprocode2026",
}


def load_citekey_to_ref_num(ref_map: Path = DEFAULT_REF_MAP) -> dict[str, int]:
    """Return citekey -> numbered reference index (PLOS citeproc order)."""
    if not ref_map.is_file():
        raise FileNotFoundError(
            f"Reference map not found: {ref_map}. "
            "This file ships with the repository and maps BibTeX keys to "
            "numbered references in the submitted manuscript."
        )
    raw = json.loads(ref_map.read_text(encoding="utf-8"))
    key_to_num = {str(k): int(v) for k, v in raw.items()}
    if len(key_to_num) < 50:
        raise RuntimeError(
            f"Expected a full bibliography map, got {len(key_to_num)} entries"
        )
    return key_to_num


def method_name_to_ref_num(
    name: str,
    citekey_to_num: dict[str, int],
) -> int:
    citekey = METHOD_NAME_TO_CITEKEY.get(name)
    if citekey is None:
        raise KeyError(f"No BibTeX mapping for Figure 2 method label {name!r}")
    num = citekey_to_num.get(citekey)
    if num is None:
        raise KeyError(
            f"Citekey {citekey!r} for {name!r} not in reference map "
            "(regenerate citekey_to_ref_num.json if citation order changed)"
        )
    return num


def superscript_number(n: int) -> str:
    """Render a positive integer as Unicode superscript digits."""
    trans = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
    return str(n).translate(trans)
