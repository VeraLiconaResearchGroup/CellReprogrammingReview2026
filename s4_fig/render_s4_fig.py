"""Render S4 Fig, the resource-audit figure.

Two panels:
  A. Downloadable code and the four-item resource score, by explicitness class.
  B. FAIR4RS-based score, by explicitness class, for methods with public
     code that have one class. OCSANA+ publishes code and is outside the bars.

Design choices for the figure:
  - palette: a single cool slate sequential ramp (off-white → mid slate-grey →
    near-black). It is colour-blind safe (sequential luminance ramp, not
    red/green-dependent), legible in greyscale, and disjoint from main-text Figure 2's
    saturated modality palette (blue/green/orange/purple) and from Figure 2's
    cohort palette (teal) and level palette (rose/magenta/wine). Slate is a
    desaturated blue-grey, so it cannot be confused with main-text Figure 2's saturated
    modality blue.
  - notation: every ratio is spelled out as "x of y" or "x (of y)" so a reader
    cannot mistake "x/y" for a fractional comparison (e.g. "0/3 ≥ 3/5").
  - inline annotations on bars spell counts as "x of y" and never appear
    inside the bar's coloured area. Panel B reports how many deposits have
    three or more indicators. It does not draw a pass or fail line.

The script is the single source of truth for the figure. It computes every
number it draws from the audit spreadsheet
(``data/audit_source.csv``, aligned with SI_3 table). Trip-wire asserts at the
bottom of ``compute_*`` functions match the headline numbers quoted in the
Section 5 prose so the figure cannot silently drift away from the manuscript.

The catalogued-resource count (125 of 135 dataset and resource identifiers
linked to exactly one method) is intentionally not drawn here. It lives in
Section 5 prose so the figure stays focused on per-class method counts. A
score of 4 of 4 means four public resources are present. It does not mean an
example workflow was run to completion.

Outputs (written in this folder):
  - S4_fig.pdf
  - S4_fig.png
  - S4_fig.tiff  (600 dpi, submission raster)
  - S4_fig.eps
"""

from __future__ import annotations

import csv
from pathlib import Path

import sys

import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _fonts import configure_sans

configure_sans()

# Bundled audit CSV matches SI_3 table (v3, 60 methods).
# col 0 = '#'  (row index 1..60)
# col 1 = Method Name
# col 4 = Tool Avail   ('Yes', 'No', '⚠️OFFLINE')
# col 8 = Repro Score  ('0/4' .. '4/4' or 'N/A')
# col 14 = FAIR4RS Score ('0/5' .. '5/5' or 'N/A')
REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_CSV = REPO_ROOT / "data" / "audit_source.csv"
OUT_DIR = Path(__file__).resolve().parent

LEVEL_ORDER = ["C0", "C1", "C2_sig", "C2_net", "C3"]
LEVEL_LABEL = {
    "C0": "Class C0\ntarget feature\ndiscovery",
    "C1": "Class C1\nnetwork\nprioritization",
    "C2_sig": "Class C2, proxy\n(signature)",
    "C2_net": "Class C2, proxy\n(network)",
    "C3": "Class C3, explicit\nintervention model",
}
LEVEL_MEMBERS_S2 = {
    "C0": [8, 21, 25, 46, 56, 57, 59],
    "C1": [5, 9, 18, 26, 30, 36, 39, 53, 54, 55],
    "C2_sig": [19, 28, 40, 42, 44, 50, 52, 58, 60],
    # OCSANA+ (row 17) has two strategies and is outside these single-class bars.
    # Row 44 is DIRECTEUR (signature). Row 41 is SiPER, the one network method.
    "C2_net": [41],
    "C3": [
        1, 2, 3, 4, 6, 7, 10, 11, 12, 13, 14, 15, 16, 20, 22, 23, 24, 27, 29, 31,
        32, 33, 34, 35, 37, 38, 43, 45, 47, 48, 49, 51,
    ],
}

# Sequential cool-slate ramp. Six steps; lightest = "absent / least rigorous",
# darkest = "fully present / most rigorous". Both panels draw from this ramp
# so the visual scale reads identically across the figure. The colours are
# tuned versions of Tailwind's slate scale: a desaturated blue-grey that is
# neutral enough to look editorial, but distinct from saturated blues used
# in main-text Figure 2 (UpSet map).
SLATE_RAMP = [
    "#F1F5F9",  # off-white slate
    "#CBD5E1",  # light slate
    "#94A3B8",  # mid slate
    "#475569",  # dark slate
    "#1E293B",  # near-black slate
    "#0F172A",  # ink
]

# Panel-A categorical mapping uses three steps from the ramp so that
# "more rigorous" is consistently darker in greyscale.
AVAILABILITY_PALETTE = {
    "All four resources": SLATE_RAMP[5],
    "Public code, under four":  SLATE_RAMP[3],
    "No code or offline": SLATE_RAMP[1],
}

# Panel-B uses one step per FAIR4RS bin (0..5).
FAIR_PALETTE = {score: SLATE_RAMP[score] for score in range(6)}

FAIR_THREE_OR_MORE = 3  # reported count only; not a pass or fail rule

# Type is sized for a double-column figure. Titles are regular weight: the
# editor asked for larger type and far less bold.
TITLE_FONT = dict(fontsize=10, fontweight="regular", color="#0F172A")
SHORT_LABEL = {
    "C0": "C0",
    "C1": "C1",
    "C2_sig": "C2 signature",
    "C2_net": "C2 network",
    "C3": "C3",
}


def set_panel_title(ax: plt.Axes, text: str) -> None:
    """Center a panel title over the bar plot (inside the spines)."""
    fig = ax.figure
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    left = ax.spines["left"].get_window_extent(renderer).x1
    right = ax.spines["right"].get_window_extent(renderer).x0
    x_center_fig = fig.transFigure.inverted().transform(((left + right) / 2, 0))[0]
    pos = ax.get_position()
    x_in_axes = (x_center_fig - pos.x0) / pos.width
    ax.set_title(text, loc="center", x=x_in_axes, **TITLE_FONT)


def _parse_score(cell: object) -> int | None:
    if cell in (None, "N/A", "-", ""):
        return None
    head = str(cell).split("/", 1)[0].strip()
    try:
        return int(head)
    except ValueError:
        return None


def load_audit() -> dict[int, dict[str, object]]:
    """Load the 60-method audit from the v3 CSV.

    Only rows whose first column parses cleanly as an integer in 1..60 are
    treated as data; this skips the title/comment/header/footnote/statistics
    lines that surround the data block in the file.
    """
    rows: dict[int, dict[str, object]] = {}
    with open(AUDIT_CSV, encoding="utf-8") as f:
        reader = csv.reader(f)
        for record in reader:
            if not record:
                continue
            try:
                idx = int(record[0])
            except (ValueError, IndexError):
                continue
            if not (1 <= idx <= 60):
                continue
            rows[idx] = {
                "name": record[1],
                "tool_avail": record[4],
                "repro": _parse_score(record[8]),
                "fair": _parse_score(record[14]),
            }
    return rows


def compute_panelA(audit: dict[int, dict[str, object]]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    totals = {"All four resources": 0, "Public code, under four": 0, "No code or offline": 0}
    for level, ids in LEVEL_MEMBERS_S2.items():
        bucket = {"All four resources": 0, "Public code, under four": 0, "No code or offline": 0}
        for i in ids:
            row = audit[i]
            avail = str(row["tool_avail"] or "")
            repro = row["repro"]
            if avail == "Yes" and repro == 4:
                bucket["All four resources"] += 1
            elif avail == "Yes":
                bucket["Public code, under four"] += 1
            else:
                bucket["No code or offline"] += 1
        out[level] = bucket
        for k in totals:
            totals[k] += bucket[k]
    assert sum(totals.values()) == 59, totals
    assert totals["All four resources"] == 26, totals
    assert totals["All four resources"] + totals["Public code, under four"] == 45, totals
    return out


def compute_panelB(audit: dict[int, dict[str, object]]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    total_with_code = 0
    total_three_plus = 0
    for level, ids in LEVEL_MEMBERS_S2.items():
        bins = [0] * 6
        for i in ids:
            row = audit[i]
            if str(row["tool_avail"] or "") != "Yes":
                continue
            score = row["fair"]
            if score is None:
                continue
            bins[score] += 1
            total_with_code += 1
            if score >= FAIR_THREE_OR_MORE:
                total_three_plus += 1
        out[level] = bins
    assert total_with_code == 45, total_with_code
    assert total_three_plus == 15, total_three_plus
    return out


def draw_panelA(ax: plt.Axes, panelA: dict[str, dict[str, int]]) -> None:
    levels = LEVEL_ORDER[::-1]
    cats = ["All four resources", "Public code, under four", "No code or offline"]
    y = list(range(len(levels)))
    left = [0] * len(levels)
    for cat in cats:
        widths = [panelA[lvl][cat] for lvl in levels]
        ax.barh(y, widths, left=left, color=AVAILABILITY_PALETTE[cat],
                label=cat, edgecolor="white", linewidth=0.8)
        left = [a + b for a, b in zip(left, widths)]

    ax.set_yticks(y)
    ax.set_xlabel("Number of methods", fontsize=8)

    labels = []
    for lvl in levels:
        n = sum(panelA[lvl].values())
        runnable = panelA[lvl]["All four resources"]
        public = runnable + panelA[lvl]["Public code, under four"]
        labels.append(f"{SHORT_LABEL[lvl]}\n{public} of {n} with code\n{runnable} at 4 of 4")
    ax.set_yticklabels(labels, fontsize=8)
    max_n = max(sum(panelA[lvl].values()) for lvl in levels)
    ax.set_xlim(0, max_n + 1)
    ax.spines[["right", "top"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", left=False)


def draw_panelB(ax: plt.Axes, panelB: dict[str, list[int]]) -> None:
    levels = LEVEL_ORDER[::-1]
    y = list(range(len(levels)))
    left = [0] * len(levels)
    for score in range(6):
        widths = [panelB[lvl][score] for lvl in levels]
        ax.barh(y, widths, left=left, color=FAIR_PALETTE[score],
                edgecolor="white", linewidth=0.8)
        left = [a + b for a, b in zip(left, widths)]

    ax.set_yticks(y)
    ax.set_xlabel("Methods with public code", fontsize=8)

    labels = []
    max_with_code = 1
    for lvl in levels:
        bins = panelB[lvl]
        n_code = sum(bins)
        three_plus = sum(bins[FAIR_THREE_OR_MORE:])
        max_with_code = max(max_with_code, n_code)
        if n_code == 0:
            labels.append(f"{SHORT_LABEL[lvl]}\nno public code")
        else:
            labels.append(f"{SHORT_LABEL[lvl]}\n{three_plus} of {n_code}\nwith 3 or more")
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_xlim(0, max_with_code + 1)
    ax.spines[["right", "top"]].set_visible(False)
    ax.tick_params(axis="x", labelsize=8)
    ax.tick_params(axis="y", left=False)


def draw_shared_legend(fig: plt.Figure, ax_a: plt.Axes, ax_b: plt.Axes) -> None:
    avail_handles = [
        Patch(facecolor=AVAILABILITY_PALETTE[k], edgecolor="white", label=k)
        for k in ("All four resources", "Public code, under four", "No code or offline")
    ]
    fair_handles = [
        Patch(facecolor=FAIR_PALETTE[score], edgecolor="white",
              label=f"{score} of 5")
        for score in range(6)
    ]
    fig.legend(handles=avail_handles,
               loc="lower left",
               bbox_to_anchor=(0.22, 0.08),
               fontsize=8, frameon=False, ncol=3,
               title="A. Code availability",
               title_fontsize=8)
    fig.legend(handles=fair_handles,
               loc="lower left",
               bbox_to_anchor=(0.22, 0.01),
               fontsize=8, frameon=False, ncol=6,
               title="B. FAIR4RS-based score",
               title_fontsize=8)


def _save_rgb(fig, path: Path, dpi: int) -> None:
    """Write a flattened RGB raster. PLOS rejects RGBA and transparency."""
    from PIL import Image
    fig.savefig(path, dpi=dpi, facecolor="white", transparent=False)
    image = Image.open(path)
    rgb = Image.new("RGB", image.size, (255, 255, 255))
    rgb.paste(image.convert("RGBA"), mask=image.convert("RGBA").split()[-1])
    kwargs = {"dpi": (dpi, dpi)}
    if path.suffix.lower() in {".tif", ".tiff"}:
        kwargs["compression"] = "tiff_lzw"
    rgb.save(path, **kwargs)
    print(f"wrote {path}")


def main() -> None:
    audit = load_audit()
    panelA = compute_panelA(audit)
    panelB = compute_panelB(audit)

    fig = plt.figure(figsize=(7.5, 7.6))
    fig.patch.set_facecolor("white")
    gs = GridSpec(2, 1, height_ratios=[1, 1], hspace=0.42, figure=fig,
                  left=0.24, right=0.98, top=0.95, bottom=0.20)
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[1, 0])

    draw_panelA(ax_a, panelA)
    draw_panelB(ax_b, panelB)

    # Re-center titles after both panels are drawn so spine positions are final.
    set_panel_title(ax_a, "A.  Code and four-item resource score")
    set_panel_title(ax_b, "B.  FAIR4RS-based score")

    # Figure title and headline audit numbers live in the manuscript caption.
    draw_shared_legend(fig, ax_a, ax_b)

    pdf_path = OUT_DIR / "S4_fig.pdf"
    png_path = OUT_DIR / "S4_fig.png"
    tiff_path = OUT_DIR / "S4_fig.tiff"
    eps_path = OUT_DIR / "S4_fig.eps"
    _save_rgb(fig, png_path, 300)
    _save_rgb(fig, tiff_path, 600)
    fig.savefig(pdf_path, facecolor="white")
    fig.savefig(eps_path, format="eps", facecolor="white")
    print(f"wrote {pdf_path}")
    print(f"wrote {eps_path}")
    print(f"canvas {fig.get_size_inches()}")


if __name__ == "__main__":
    main()
