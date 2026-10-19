"""
Main-text Figure 1 at print size.

Panel A is the assignment tree. Panel B is the input, selection step, and
output for each class. The canvas is the print size, Arial is 8–12 pt, and
the class colours match Figure 2 (UpSet map). EPS text is Type 42.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _fonts import configure_sans
ARIAL = str(configure_sans())
plt.rcParams["mathtext.fontset"] = "dejavusans"

# Same class colours as main-text Figure 2 (UpSet).
CLASS_COLOR = {
    "C0": "#6B7280",
    "C1": "#1F7F8C",
    "C2": "#9D174D",
    "C3": "#2A0010",
}

W = 7.5
# Laid out in inches from the top. Height is set after the table.
PT = 8.5


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
    print(f"Wrote {path}")


def wrap(text: str, width_in: float, pt: float = PT) -> str:
    from PIL import ImageFont

    font = ImageFont.truetype(ARIAL, pt)
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if font.getlength(trial) / 72 <= width_in:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def box(ax, x, y, w, h, text, *, face="white", edge="#111827", tcolor="#111827", pt=PT, weight="regular"):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.04",
        facecolor=face, edgecolor=edge, linewidth=0.8, zorder=2,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=pt, color=tcolor, fontweight=weight, zorder=3, linespacing=1.15)


def class_box(ax, x, y, w, h, label):
    key = label.split()[-1]
    face = CLASS_COLOR[key]
    box(ax, x, y, w, h, label, face=face, edge=face, tcolor="white", pt=9, weight="semibold")


def arrow(ax, x0, y0, x1, y1, label, side="above"):
    ax.add_patch(FancyArrowPatch(
        (x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=8,
        linewidth=0.8, color="#111827", zorder=1,
    ))
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    if side == "above":
        ax.text(mx, my + 0.04, label, ha="center", va="bottom", fontsize=8, color="#111827")
    elif side == "left":
        ax.text(mx - 0.04, my, label, ha="right", va="center", fontsize=8, color="#111827")
    else:
        ax.text(mx + 0.04, my, label, ha="left", va="center", fontsize=8, color="#111827")


def main() -> None:
    # y decreases downward in the plan; matplotlib y increases upward.
    # Content height, then flip.
    h_fig = 7.85
    fig, ax = plt.subplots(figsize=(W, h_fig))
    ax.set_xlim(0, W)
    ax.set_ylim(0, h_fig)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)

    def Y(top_offset: float) -> float:
        return h_fig - top_offset

    ax.text(0.08, Y(0.22), "A", fontsize=11, fontweight="bold", va="center")

    n1 = wrap(
        "1. Is selection a direct score of target features or of observed screen outcomes, "
        "with no predictive response and no network-influence model?",
        4.15,
    )
    box(ax, 0.28, Y(1.05), 4.35, 0.72, n1, weight="regular")
    class_box(ax, 5.35, Y(0.92), 1.55, 0.42, "Class C0")
    arrow(ax, 4.63, Y(0.69), 5.35, Y(0.71), "Yes")

    n2 = wrap(
        "2. Does selection use a predictive response, a learned inverse of one, "
        "or a certified control property of a stated model family?",
        3.75,
    )
    box(ax, 0.28, Y(1.95), 4.05, 0.68, n2)
    arrow(ax, 2.45, Y(1.05), 2.45, Y(1.27), "No", side="left")

    n2b = wrap(
        "2b. Network-influence score, with no response representation "
        "and no certified control property?",
        2.55,
    )
    box(ax, 4.85, Y(1.95), 2.45, 0.62, n2b)
    arrow(ax, 4.33, Y(1.61), 4.85, Y(1.64), "")
    ax.text(4.59, Y(1.50), "No", ha="center", va="bottom", fontsize=8, color="#111827")

    class_box(ax, 4.85, Y(2.90), 1.15, 0.38, "Class C1")
    box(ax, 6.15, Y(2.90), 1.15, 0.38, "Unresolved")
    arrow(ax, 5.42, Y(1.95), 5.42, Y(2.52), "Yes", side="left")
    arrow(ax, 6.40, Y(1.95), 6.40, Y(2.52), "", side="right")
    ax.text(6.48, Y(2.22), "No, or not\ndocumented", ha="left", va="center", fontsize=8, color="#111827")

    n3 = wrap(
        "3. Does selection use a proxy response or its learned inverse, without an "
        "explicit intervention-model evaluation or certified control property "
        "contributing to selection?",
        4.15,
    )
    box(ax, 0.28, Y(3.83), 4.35, 0.72, n3)
    arrow(ax, 2.45, Y(1.95), 2.45, Y(3.11), "Yes", side="left")

    class_box(ax, 5.35, Y(3.68), 1.55, 0.42, "Class C2")
    arrow(ax, 4.63, Y(3.47), 5.35, Y(3.47), "Yes")

    n4 = "4. Does $u$ enter the intervention model,\nor does the certified property select $u$?"
    box(ax, 0.28, Y(4.47), 4.35, 0.48, n4)
    arrow(ax, 2.45, Y(3.83), 2.45, Y(3.99), "No", side="left")

    class_box(ax, 5.35, Y(4.44), 1.55, 0.42, "Class C3")
    arrow(ax, 4.63, Y(4.23), 5.35, Y(4.23), "Yes")
    box(ax, 1.45, Y(5.32), 2.00, 0.36, "Unresolved")
    arrow(ax, 2.45, Y(4.62), 2.45, Y(4.96), "")
    ax.text(2.35, Y(4.58), "No, or not documented", ha="right", va="top", fontsize=8, color="#111827")

    ax.text(0.08, Y(5.40), "B", fontsize=11, fontweight="bold", va="center")

    # Table
    headers = ["Class", "Input", "Selection step", "Output", "Examples"]
    rows = [
        ["C0", "Target features, or observed screen outcomes",
         "Score against the target, or rank observed outcomes",
         "Ranked features or tested interventions", "D'Alessio; REPROcode"],
        ["C1", "Regulatory graph and source–target contrast",
         "Network-influence score", "Ranked interventions", "CellNet; ANANSE"],
        ["C2", "Proxy responses, or the pairs used to learn them",
         "Match the proxy to the target,\nor apply a learned inverse",
         "Ranked interventions", "OncoTreat; DrugReflector"],
        ["C3", "An intervention model, or a stated model family",
         "Modeled outcome, or a certified control property",
         "Ranked or certified intervention sets", "Stable Motifs; PDGrapher"],
    ]
    col_w = [0.46, 1.95, 1.92, 1.78, 1.31]
    x0 = 0.04
    row_h = 0.46
    header_h = 0.28
    table_top = 5.52
    # header
    x = x0
    for header, cw in zip(headers, col_w):
        ax.add_patch(plt.Rectangle((x, Y(table_top + header_h)), cw, header_h,
                                   facecolor="#F3F4F6", edgecolor="#111827", linewidth=0.4))
        ax.text(x + 0.04, Y(table_top + header_h / 2), header, ha="left", va="center",
                fontsize=8, fontweight="semibold")
        x += cw
    for ri, row in enumerate(rows):
        yb = Y(table_top + header_h + (ri + 1) * row_h)
        x = x0
        face = "white"
        for ci, (cell, cw) in enumerate(zip(row, col_w)):
            ax.add_patch(plt.Rectangle((x, yb), cw, row_h,
                                       facecolor=face, edgecolor="#111827", linewidth=0.4))
            if ci == 0:
                ax.add_patch(plt.Rectangle((x, yb), 0.08, row_h,
                                           facecolor=CLASS_COLOR[cell], edgecolor="none"))
            inset = 0.14 if ci == 0 else 0.08
            shown = cell if (ci == 0 or "\n" in cell) else wrap(cell, cw - inset - 0.10, 8)
            ax.text(x + inset, yb + row_h / 2, shown, ha="left", va="center", fontsize=8)
            x += cw

    out = Path(__file__).resolve().parent
    fig.patch.set_facecolor("white")
    _save_rgb(fig, out / "Fig1_assignment.png", 300)
    _save_rgb(fig, out / "Fig1_assignment.tiff", 600)
    fig.savefig(out / "Fig1_assignment.pdf", facecolor="white")
    fig.savefig(out / "Fig1_assignment.eps", format="eps", facecolor="white")
    print(f"Wrote {out / 'Fig1_assignment.pdf'}")
    plt.close(fig)
    print(f"Figure 1 canvas {W:.2f} x {h_fig:.2f} in")


if __name__ == "__main__":
    main()
