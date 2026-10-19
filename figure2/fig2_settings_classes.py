"""
Fig2_settings_classes — Figure 2 of the manuscript.

Modality coverage of the 60 reviewed methods, rendered as an UpSet plot.
For every method we encode the set of biological modalities the *original
publication* claims to address, drawn from Supporting Information S1 (methods table)'s
"Reprogramming modes (D/I/T/P)" column:

    D = Directed differentiation
    I = Pluripotency induction (indirect reprogramming → iPSC-like)
    T = Transdifferentiation
    P = Phenotype reprogramming

A 4-set Venn would have 15 regions and is hard to read; an UpSet plot is the
standard alternative for ≥4 sets. Each column is one modality combination
that *actually appears* among the reviewed methods, the column height is the
number of methods in that combination, and a dot matrix below the columns shows
which modalities the column represents. Each bar is split by publication-year
cohort, so the figure carries two pieces of information per column:
    - bar height           = methods in that modality combination
    - sub-segment heights  = how those methods are distributed across cohorts
                             (oldest at the bottom, newest at the top)
Method names are listed under each column for traceability. Class is colour
plus a marker, in regular Arial. The canvas is the print size (7.5 in wide),
so the point sizes are the sizes on the page. Reference numbers are drawn as
raised Arial digits, not as Unicode superscripts, so the EPS stays Type 42.
See fig2_bibliography.py.

Outputs:
    Fig2_settings_classes.png   (300 dpi, journal ready)
    Fig2_settings_classes.tiff  (600 dpi, submission raster)
    Fig2_settings_classes.pdf   (vector, for typesetting)
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _fonts import configure_sans, font_name
_FONT_PATH = configure_sans()
FONT = font_name()

import matplotlib.patches as patches
import matplotlib.pyplot as plt

# Embed TrueType outlines. Type 3 fonts are what journals reject as non-vector text.
plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42

from fig2_bibliography import (
    METHOD_NAME_TO_CITEKEY,
    load_citekey_to_ref_num,
    method_name_to_ref_num,
    superscript_number,
)


# ---------------------------------------------------------------------------
# 1. Reviewed methods: (method, year, level, modality string)
#    transcribed from Supporting Information S1 (methods table), kept in lock-step with the
#    classifications in Manuscript_blueprint_04-24-2026_v3.md and Table 1.
# ---------------------------------------------------------------------------

METHODS: list[tuple[str, int, int, str]] = [
    ("Crespo & Del Sol", 2013, 3, "T"),
    ("Cornelius",        2013, 3, "P"),
    ("FVS",              2013, 3, "DP"),
    ("DEPCs",            2013, 3, "DITP"),
    ("CellNet",          2014, 1, "DIT"),
    ("Hopfield",         2014, 3, "IT"),
    ("Stable Motifs",    2015, 3, "DP"),
    ("D'Alessio",        2015, 0, "T"),
    ("Mogrify",          2016, 1, "T"),
    ("Murrugarra",       2016, 3, "P"),
    ("Toggle/Okawa",     2016, 3, "D"),
    ("Del Vecchio",      2017, 3, "DIP"),
    ("Zañudo",           2017, 3, "DP"),
    ("DGC",              2017, 3, "IT"),
    ("PCK",              2018, 3, "P"),
    ("LDOI",             2018, 3, "P"),
    ("SeesawPred",       2018, 1, "D"),
    ("OncoTreat",        2018, 2, "P"),
    ("BRC",              2019, 3, "P"),
    ("Okawa & Del Sol",  2019, 0, "T"),
    ("BoolIFFNN",        2020, 3, "DP"),
    ("Sordo",            2020, 3, "P"),
    ("Aguilar",          2020, 3, "P"),
    ("TransSynW",        2020, 0, "DT"),
    ("OCSANA+",          2020, 4, "DP"),
    ("ANANSE",           2021, 1, "IT"),
    ("CABEAN",           2021, 3, "PT"),
    ("DECCODE",          2021, 2, "I"),
    ("IRENE",            2021, 3, "DIT"),
    ("Taiji-reprogram",  2021, 1, "IT"),
    ("CELLoGeNe",        2022, 3, "I"),
    ("cSTAR",            2022, 3, "P"),
    ("Tercan",           2022, 3, "T"),
    ("NETISCE",          2022, 3, "DP"),
    ("scREMOTE",         2022, 3, "D"),
    ("TRANSDIRE",        2022, 1, "T"),
    ("CellOracle",       2023, 3, "DP"),
    ("DCGS",             2023, 3, "P"),
    ("scANANSE",         2023, 1, "D"),
    ("PC3T",             2023, 2, "DIT"),
    ("SiPER",            2023, 2, "DITP"),
    ("Wytock-TL",        2024, 2, "IPT"),
    ("CAESAR",           2024, 3, "DPT"),
    ("DIRECTEUR",        2024, 2, "T"),
    ("pbn-STAC",         2025, 3, "P"),
    ("CellCartographer", 2025, 0, "D"),
    ("BoNesis+CABEAN",   2025, 3, "DT"),
    ("TFcomb",           2025, 3, "DIT"),
    ("REVERT",           2025, 3, "P"),
    ("DrugReflector",    2025, 2, "DP"),
    ("PDGrapher",        2026, 3, "P"),
    # --- 6 methods added in the Draft-1 supplement extension (refs 52–57) ---
    ("REVIVE",           2025, 2, "P"),
    ("CANDiT",           2025, 1, "P"),
    ("SwitchTFI",        2025, 1, "D"),
    ("Atlas-guided",     2026, 1, "P"),
    ("REPROcode",        2026, 0, "T"),
    ("Reprogram-Seq",    2019, 0, "T"),
    ("TF Atlas",         2023, 2, "D"),
    ("Iterative TF screening", 2025, 0, "D"),
    ("Briggs",           2026, 2, "D"),
]
assert len(METHODS) == 60
assert len({name for name, _, _, _ in METHODS}) == 60
assert all(name != "TRAPT" for name, _, _, _ in METHODS)

MODALITY_ORDER: list[tuple[str, str]] = [
    ("D", "Directed\ndifferentiation"),
    ("I", "Pluripotency\ninduction (iPSC)"),
    ("T", "Transdifferentiation"),
    ("P", "Phenotype\nreprogramming"),
]
MODALITY_KEYS = [k for k, _ in MODALITY_ORDER]


# ---------------------------------------------------------------------------
# 2. Encoding
# ---------------------------------------------------------------------------

# Year-cohort palette ("Palette B": cool sequential teal → near-black).
# Disjoint from Figure 1's modality palette (blue/green/orange/purple) and
# from the explicitness class palette below; colour-blind friendly via a
# wide lightness ramp so the temporal ordering reads even under
# protan/deutan/tritan deficits.
YEAR_BANDS: list[tuple[str, range, str]] = [
    ("2013–2017", range(2013, 2018), "#9DD9D2"),  # light teal
    ("2018–2022", range(2018, 2023), "#1F7F8C"),  # deep teal
    ("2023–2026", range(2023, 2027), "#0B2B33"),  # near-black teal
]


def cohort_index(year: int) -> int:
    for i, (_, yrs, _) in enumerate(YEAR_BANDS):
        if year in yrs:
            return i
    raise ValueError(f"year {year} not in any cohort")


# Colour plus a matplotlib marker. Weight stays regular. C1 uses the teal
# already used for the middle publication-year cohort; the marker, not the
# hue alone, separates a class from a bar.
LEVEL_STYLE: dict[int, dict[str, object]] = {
    0: dict(color="#6B7280", marker="o", mfc="white"),
    1: dict(color="#1F7F8C", marker="^", mfc="#1F7F8C"),
    2: dict(color="#9D174D", marker="s", mfc="#9D174D"),
    3: dict(color="#2A0010", marker="D", mfc="#2A0010"),
    # Two strategies (C1 and C3A), so the name is not given one class color.
    4: dict(color="#374151", marker=None, mfc="none"),
}


def _text_color_for_bg(hex_: str) -> str:
    h = hex_.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return "white" if (0.299 * r + 0.587 * g + 0.114 * b) < 130 else "#1F2937"


# Print size. One data unit is one inch, and figsize matches the axes, so a
# fontsize of 8 is 8 pt on the page. PLOS: width 2.63–7.5 in, height ≤ 8.75 in,
# Arial 8–12 pt.
PRINT_W = 7.5
MAX_H = 8.75
NAME_PT = 8.0
LABEL_PT = 8.0
TITLE_PT = 9.0
LINE_H = 0.148
SIDE_W = 1.48
ANNOT_COLOR = "#0F172A"
ARIAL_PATH = str(_FONT_PATH)


def _caps_label(text: str) -> str:
    return "\n".join(line.upper() for line in text.split("\n"))


def _annot_title_kwargs(fontsize: float) -> dict[str, object]:
    return dict(
        color=ANNOT_COLOR,
        fontfamily="sans-serif",
        fontweight="semibold",
        fontsize=fontsize,
    )


def _style_legend_title(text_artist: plt.Text) -> None:
    text_artist.set_color(ANNOT_COLOR)
    text_artist.set_fontfamily("sans-serif")
    text_artist.set_fontweight("semibold")


# Long method lists split into two side-by-side sub-columns under one UpSet column.
NAME_SPLIT_AT = 10

# Top-to-bottom display order for selected UpSet columns (default: alphabetical).
COLUMN_NAME_ORDER: dict[tuple[bool, bool, bool, bool], list[str]] = {
    (False, False, True, False): [  # T-only, column 2 (9 methods)
        "Mogrify",
        "DIRECTEUR",
        "D'Alessio",
        "Okawa & Del Sol",
        "REPROcode",
        "Reprogram-Seq",
        "Tercan",
        "TRANSDIRE",
        "Crespo & Del Sol",
    ],
}


def _ordered_members(
    combo: tuple[bool, bool, bool, bool],
    members: list[tuple[str, int, int]],
) -> list[tuple[str, int, int]]:
    order = COLUMN_NAME_ORDER.get(combo)
    if order is None:
        return sorted(members, key=lambda m: m[0])
    by_name = {m[0]: m for m in members}
    return [by_name[n] for n in order]


def _method_name_metrics(member_count: int) -> tuple[float, float, int]:
    """Font size, line height, and vertical rows needed for a column's name list."""
    rows = member_count if member_count <= NAME_SPLIT_AT else (member_count + 1) // 2
    if member_count <= 8:
        return 10.5, 0.42, rows
    if member_count <= 12:
        return 9.8, 0.38, rows
    if member_count <= NAME_SPLIT_AT:
        return 9.2, 0.34, rows
    return 8.8, 0.32, rows


def _name_panel_height() -> float:
    return max(
        _method_name_metrics(len(groups[c]))[2]
        * _method_name_metrics(len(groups[c]))[1]
        + 0.22
        for c in combos
    )


DEFAULT_COL_W = 1.55
SPLIT_COL_W = 2.2   # extra width when a column carries two name sub-columns
SPLIT_NAME_GAP = 0.08  # gutter between the two name lists, centered on the bar
SPLIT_COL_INWARD = 0.012  # pull each sub-column slightly toward the bar center


def _column_widths() -> list[float]:
    return [
        SPLIT_COL_W if len(groups[c]) > NAME_SPLIT_AT else DEFAULT_COL_W
        for c in combos
    ]


def _column_layout(
    side_w: float, widths: list[float],
) -> tuple[list[float], float]:
    """X-center per UpSet column and total width of the column block."""
    centers: list[float] = []
    cursor = side_w
    for w in widths:
        centers.append(cursor + w / 2)
        cursor += w
    return centers, cursor


# ---------------------------------------------------------------------------
# 3. Aggregate — methods grouped by exact modality combination
# ---------------------------------------------------------------------------

def combo_key(modes: str) -> tuple[bool, bool, bool, bool]:
    return tuple(k in modes for k in MODALITY_KEYS)  # type: ignore[return-value]


groups: dict[tuple[bool, bool, bool, bool], list[tuple[str, int, int]]] = defaultdict(list)
for _name, _year, _lvl, _modes in METHODS:
    groups[combo_key(_modes)].append((_name, _year, _lvl))

# Sort columns by total count descending, breaking ties by combo size ascending
# so single-modality columns come before multi-modality columns within ties.
combos = sorted(
    groups.keys(),
    key=lambda c: (-len(groups[c]), sum(c)),
)
N_COMBOS = len(combos)

modality_totals = {
    k: sum(1 for _n, _y, _l, m in METHODS if k in m) for k in MODALITY_KEYS
}


# ---------------------------------------------------------------------------
# 4. Render
# ---------------------------------------------------------------------------

def _save_figure(fig, path: Path, dpi: int) -> None:
    """Write a flattened RGB raster. PLOS rejects RGBA and transparency."""
    from PIL import Image
    fig.savefig(path, dpi=dpi, facecolor="white", transparent=False)
    image = Image.open(path)
    rgb = Image.new("RGB", image.size, (255, 255, 255))
    rgb.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
    save_kwargs = {"dpi": (dpi, dpi)}
    if path.suffix.lower() in {".tif", ".tiff"}:
        save_kwargs["compression"] = "tiff_lzw"
    rgb.save(path, **save_kwargs)


def _arial_inches(text: str, pt: float) -> float:
    """Width in inches of an Arial string at `pt` points, from the font matplotlib draws."""
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath
    path = TextPath((0, 0), text, prop=FontProperties(family=FONT, size=pt))
    return path.get_extents().width / 72.0


def _label_span(name: str, ref: str, level: int) -> float:
    """Width of name + raised reference digits + marker, in inches."""
    span = _arial_inches(name, NAME_PT) + 0.08 + _arial_inches(ref, NAME_PT)
    if LEVEL_STYLE[level]["marker"] is not None:
        span += 0.13
    return span


def _column_spec(combo: tuple[bool, bool, bool, bool]) -> dict:
    members = _ordered_members(combo, groups[combo])
    # Filled in render once reference numbers are known. Placeholder widths
    # are replaced there; this helper only groups the names.
    return {"combo": combo, "members": members}


def render(out_dir: Path) -> None:
    from matplotlib import font_manager
    # font family set by configure_sans()
    plt.rcParams["pdf.fonttype"] = 42
    plt.rcParams["ps.fonttype"] = 42

    citekey_to_num = load_citekey_to_ref_num()
    missing_map = [name for name, _, _, _ in METHODS if name not in METHOD_NAME_TO_CITEKEY]
    if missing_map:
        raise RuntimeError(f"Missing BibTeX mapping for: {missing_map}")

    content_w = PRINT_W - SIDE_W - 0.12

    columns = []
    for combo in combos:
        members = _ordered_members(combo, groups[combo])
        enriched = []
        for name, year, lvl in members:
            ref = str(method_name_to_ref_num(name, citekey_to_num))
            enriched.append((name, year, lvl, ref, _label_span(name, ref, lvl)))
        n = len(enriched)
        if n > 6:
            mid = (n + 1) // 2
            stacks = [enriched[:mid], enriched[mid:]]
        else:
            stacks = [enriched]
        width = 0.08 + sum(max(item[4] for item in stack) for stack in stacks)
        width += 0.06 * (len(stacks) - 1)
        columns.append({
            "combo": combo,
            "stacks": stacks,
            "width": width,
            "nlines": max(len(stack) for stack in stacks),
            "count": n,
        })

    bands: list[list[dict]] = []
    current: list[dict] = []
    used = 0.0
    for col in columns:
        if current and used + col["width"] > content_w:
            bands.append(current)
            current = []
            used = 0.0
        current.append(col)
        used += col["width"]
    if current:
        bands.append(current)

    def band_height(band: list[dict], first: bool) -> float:
        max_count = max(col["count"] for col in band)
        max_lines = max(col["nlines"] for col in band)
        bar_h = max(0.42, 0.058 * max_count + 0.14)
        matrix_h = 0.46
        names_h = max_lines * LINE_H
        return bar_h + 0.02 + matrix_h + 0.04 + names_h + 0.08

    legend_h = 0.94
    heights = [band_height(band, i == 0) for i, band in enumerate(bands)]
    fig_h = legend_h + sum(heights) + 0.08
    if fig_h > MAX_H:
        raise RuntimeError(f"Figure 2 is {fig_h:.2f} in tall; PLOS maximum is {MAX_H}")

    fig, ax = plt.subplots(figsize=(PRINT_W, fig_h))
    ax.set_xlim(0, PRINT_W)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    # ----- legends, top -----
    y_cursor = fig_h - 0.08
    ax.text(PRINT_W / 2, y_cursor, "Bar fill is the publication-year cohort",
            ha="center", va="top", fontsize=TITLE_PT, fontweight="regular",
            color=ANNOT_COLOR)
    y_cursor -= 0.20
    cohort_labels = []
    for label, yrs, col in YEAR_BANDS:
        n = sum(1 for m in METHODS if m[1] in yrs)
        cohort_labels.append((f"{label}  (n={n})", col))
    gap = 0.18
    widths = [_arial_inches(lab, LABEL_PT) + 0.22 for lab, _ in cohort_labels]
    x = PRINT_W / 2 - (sum(widths) + gap * (len(widths) - 1)) / 2
    for (lab, col), w in zip(cohort_labels, widths):
        ax.add_patch(patches.Rectangle((x, y_cursor - 0.12), 0.16, 0.12,
                                       facecolor=col, edgecolor="white", linewidth=0.4))
        ax.text(x + 0.20, y_cursor - 0.06, lab, ha="left", va="center",
                fontsize=LABEL_PT, color="#1F2937")
        x += w + gap
    y_cursor -= 0.28
    ax.text(PRINT_W / 2, y_cursor, "Explicitness class",
            ha="center", va="top", fontsize=TITLE_PT, fontweight="regular",
            color=ANNOT_COLOR)
    y_cursor -= 0.22
    class_labels = [("Class C0", 0), ("Class C1", 1), ("Class C2", 2), ("Class C3", 3)]
    class_w = []
    for lab, lvl in class_labels:
        class_w.append(_arial_inches(lab, LABEL_PT) + 0.22)
    x = PRINT_W / 2 - (sum(class_w) + 0.28 * 3) / 2
    for (lab, lvl), w in zip(class_labels, class_w):
        style = LEVEL_STYLE[lvl]
        ax.scatter([x + 0.06], [y_cursor], s=28, marker=style["marker"],
                   facecolor=style["mfc"], edgecolor=style["color"],
                   linewidths=0.8, clip_on=False, zorder=5)
        ax.text(x + 0.16, y_cursor, lab, ha="left", va="center",
                fontsize=LABEL_PT, color=style["color"])
        x += w + 0.28

    y_top = y_cursor - 0.16

    def draw_name(x_left: float, y: float, name: str, ref: str, lvl: int) -> None:
        style = LEVEL_STYLE.get(lvl, LEVEL_STYLE[4])
        color = style["color"]
        ax.text(x_left, y, name, ha="left", va="top", fontsize=NAME_PT,
                color=color, fontweight="regular", zorder=5)
        ref_x = x_left + _arial_inches(name, NAME_PT) + 0.08
        ax.text(ref_x, y, ref, ha="left", va="top", fontsize=NAME_PT,
                color=color, zorder=5)
        if style["marker"] is not None:
            mark_x = ref_x + _arial_inches(ref, NAME_PT) + 0.08
            ax.scatter([mark_x], [y - 0.055], s=16, marker=style["marker"],
                       facecolor=style["mfc"], edgecolor=color, linewidths=0.6,
                       clip_on=False, zorder=6)

    for bi, band in enumerate(bands):
        band_w = sum(col["width"] for col in band)
        # Center the columns in the content area.
        x0 = SIDE_W + (content_w - band_w) / 2
        centers = []
        cursor = x0
        for col in band:
            centers.append(cursor + col["width"] / 2)
            cursor += col["width"]
        max_count = max(col["count"] for col in band)
        bar_h = max(0.42, 0.058 * max_count + 0.14)
        matrix_h = 0.46
        bar_top = y_top
        bar_bottom = bar_top - bar_h
        unit = (bar_h - 0.16) / max_count
        bar_w = 0.28
        for col, xc in zip(band, centers):
            cohort_counts = [0, 0, 0]
            for _name, year, _lvl, _ref, _span in col["stacks"][0] + (
                col["stacks"][1] if len(col["stacks"]) > 1 else []
            ):
                cohort_counts[cohort_index(year)] += 1
            y = bar_bottom
            x = xc - bar_w / 2
            for pi, sub in enumerate(cohort_counts):
                if sub == 0:
                    continue
                seg_h = unit * sub
                seg_color = YEAR_BANDS[pi][2]
                ax.add_patch(patches.Rectangle(
                    (x, y), bar_w, seg_h, facecolor=seg_color,
                    edgecolor="white", linewidth=0.4, zorder=3,
                ))
                y += seg_h
            ax.text(xc, y + 0.02, str(col["count"]), ha="center", va="bottom",
                    fontsize=LABEL_PT, fontweight="semibold", color=ANNOT_COLOR,
                    zorder=4)

        matrix_top = bar_bottom - 0.02
        row_h = matrix_h / len(MODALITY_ORDER)
        row_ys = [matrix_top - (ri + 0.5) * row_h for ri in range(len(MODALITY_ORDER))]
        for ri, y in enumerate(row_ys):
            ax.add_patch(patches.Rectangle(
                (SIDE_W - 0.04, y - row_h * 0.46),
                band_w + (content_w - band_w) / 2 + 0.08, row_h * 0.92,
                facecolor=("#f3f4f6" if ri % 2 == 0 else "#ffffff"),
                edgecolor="none", zorder=1,
            ))
        short = {"D": "Directed", "I": "Pluripotency", "T": "Transdiff.", "P": "Phenotype"}
        max_mod = max(modality_totals.values())
        for ri, (key, _label) in enumerate(MODALITY_ORDER):
            y = row_ys[ri]
            bw = 0.34 * modality_totals[key] / max_mod
            ax.add_patch(patches.Rectangle(
                (0.04, y - 0.04), bw, 0.08,
                facecolor="#9CA3AF", edgecolor="none", zorder=2,
            ))
            ax.text(0.42, y, str(modality_totals[key]), ha="left", va="center",
                    fontsize=LABEL_PT, color=ANNOT_COLOR)
            ax.text(SIDE_W - 0.06, y, f"{key}  {short[key]}",
                    ha="right", va="center", fontsize=LABEL_PT,
                    color=ANNOT_COLOR)
        for col, xc in zip(band, centers):
            active = [ri for ri, bit in enumerate(col["combo"]) if bit]
            for ri in range(len(MODALITY_ORDER)):
                if ri in active:
                    continue
                ax.add_patch(plt.Circle((xc, row_ys[ri]), 0.035,
                                        facecolor="#dadada", edgecolor="none", zorder=2))
            if len(active) >= 2:
                ax.plot([xc, xc], [row_ys[max(active)], row_ys[min(active)]],
                        color="#1F2937", linewidth=1.2, zorder=3, solid_capstyle="round")
            for ri in active:
                ax.add_patch(plt.Circle((xc, row_ys[ri]), 0.055,
                                        facecolor="#1F2937", edgecolor="white",
                                        linewidth=0.4, zorder=4))

        name_top = matrix_top - matrix_h - 0.04
        for col, xc in zip(band, centers):
            n_stacks = len(col["stacks"])
            stack_widths = [max(item[4] for item in stack) for stack in col["stacks"]]
            total = sum(stack_widths) + 0.06 * (n_stacks - 1)
            left = xc - total / 2
            for stack, sw in zip(col["stacks"], stack_widths):
                for i, (name, _year, lvl, ref, _span) in enumerate(stack):
                    draw_name(left, name_top - i * LINE_H, name, ref, lvl)
                left += sw + 0.06
        y_top = name_top - max(col["nlines"] for col in band) * LINE_H - 0.08

    out_png = out_dir / "Fig2_settings_classes.png"
    out_tiff = out_dir / "Fig2_settings_classes.tiff"
    out_pdf = out_dir / "Fig2_settings_classes.pdf"
    out_eps = out_dir / "Fig2_settings_classes.eps"
    fig.patch.set_facecolor("white")
    _save_figure(fig, out_png, dpi=300)
    _save_figure(fig, out_tiff, dpi=600)
    fig.savefig(out_pdf, facecolor="white")
    fig.savefig(out_eps, format="eps", facecolor="white")
    plt.close(fig)
    print(f"Figure 2 canvas {PRINT_W:.2f} x {fig_h:.2f} in, {len(bands)} rows")
    print(f"Wrote {out_png}")
    print(f"Wrote {out_tiff}")
    print(f"Wrote {out_pdf}")
    print(f"Wrote {out_eps}")


def report() -> None:
    print(f"\nReviewed methods = {len(METHODS)}")
    print("Per-modality coverage:")
    for k, label in MODALITY_ORDER:
        flat_label = label.replace(chr(10), " ")
        print(f"  {k}  {modality_totals[k]:>3}   {flat_label}")
    print("\nUnique combinations (size, count, members):")
    for combo in combos:
        key = "".join(k for k, b in zip(MODALITY_KEYS, combo) if b)
        names = ", ".join(n for n, _y, _l in sorted(groups[combo]))
        print(f"  {key:<5}  n={len(groups[combo]):>2}   {names}")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    report()
    render(out_dir)
