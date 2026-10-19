"""Figure 2 of the manuscript: one UpSet with combinations in rows.

Names stay at 8 pt inside each row. The canvas is the print size, so the
point sizes are the sizes on the page. Reference numbers come from the
compiled bibliography. Regenerate this file after any change that alters
citation order in the main-text draft.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _fonts import configure_sans, font_name
_FONT_PATH = configure_sans()
FONT = font_name()

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath

import fig2_settings_classes as src
from fig2_bibliography import (
    METHOD_NAME_TO_CITEKEY,
    load_citekey_to_ref_num,
    method_name_to_ref_num,
)

PRINT_W = 7.5
NAME_PT = 8.0
LABEL_PT = 8.0
SUP_PT = 6.0
# Author-surname labels are citations. Tool names stay as the method name.
AUTHOR_ET_AL = {
    "Aguilar",
    "Cornelius",
    "D'Alessio",
    "Del Vecchio",
    "Murrugarra",
    "Sordo",
    "Tercan",
    "Zañudo",
}
ARIAL = str(_FONT_PATH)
INK = "#0F172A"
KEYS = src.MODALITY_KEYS

# Five fixed name subcolumns. The bar is shorter so those subcolumns
# have room for the longest method name at 8 pt.
N_NAME_COLS = 5
DOT_X = [0.20, 0.40, 0.60, 0.80]
BAR_X = 0.96
BAR_LANE = 0.50
COUNT_X = 1.62
NAME_X = 1.82
NAME_RIGHT = 7.42
NAME_GAP = 0.06
LINE_H = 0.20


def width(text: str, pt: float) -> float:
    path = TextPath((0, 0), text, prop=FontProperties(family=FONT, size=pt))
    return path.get_extents().width / 72.0


def display_name(name: str) -> str:
    if name in AUTHOR_ET_AL:
        return f"{name} et al."
    return name


def ocsana_layout(ref: str) -> dict[str, float]:
    """Inch positions for OCSANA+ (C1 symbol, C3 symbol)*, from the name start.

    The triangle is centered far enough past the opening parenthesis that its
    left edge does not sit inside the parenthesis.
    """
    name_w = width("OCSANA+", NAME_PT)
    ref_w = width(ref, SUP_PT)
    open_w = width("(", NAME_PT)
    close_w = width(")*", NAME_PT)
    ref_x = name_w + 0.02
    open_x = ref_x + ref_w + 0.04
    # Marker radius is about 0.04 in; keep a clear gap after "(".
    tri_x = open_x + open_w + 0.09
    dia_x = tri_x + 0.16
    close_x = dia_x + 0.09
    end = close_x + close_w
    return {
        "ref_x": ref_x,
        "open_x": open_x,
        "tri_x": tri_x,
        "dia_x": dia_x,
        "close_x": close_x,
        "end": end,
    }


def name_span(name: str, ref: str, level: int) -> float:
    if name == "OCSANA+":
        return ocsana_layout(ref)["end"]
    span = width(display_name(name), NAME_PT) + 0.02 + width(ref, SUP_PT)
    if src.LEVEL_STYLE[level]["marker"] is not None:
        span += 0.13
    return span


def class_rank(item: dict) -> int:
    """C0–C3 from the left. OCSANA+ (level 4) follows C3."""
    return 4 if item["level"] >= 4 else item["level"]


def order_items(items: list[dict], mode: str) -> list[dict]:
    if mode == "length":
        return sorted(items, key=lambda it: (it["span"], display_name(it["name"]).casefold()))
    if mode == "class":
        return sorted(items, key=lambda it: (class_rank(it), display_name(it["name"]).casefold()))
    if mode == "both":
        return sorted(items, key=lambda it: (
            class_rank(it), it["span"], display_name(it["name"]).casefold(),
        ))
    raise ValueError(mode)


def grid(items: list[dict]) -> tuple[list[list], list[float]]:
    """Fill five subcolumns from top to bottom, then left to right.

    `items` is already in the order that should occupy successive columns,
    so a contiguous group stays inside one subcolumn or spills into the next.
    """
    n = len(items)
    heights = [n // N_NAME_COLS] * N_NAME_COLS
    for i in range(n % N_NAME_COLS):
        heights[i] += 1
    bands: list[list] = []
    idx = 0
    for h in heights:
        bands.append(items[idx:idx + h])
        idx += h
    n_lines = max(heights) if n else 1
    lines = [
        [band[r] if r < len(band) else None for band in bands]
        for r in range(n_lines)
    ]
    col_w = [max((it["span"] for it in band), default=0.0) for band in bands]
    return lines, col_w


def grid_both(items: list[dict]) -> tuple[list[list], list[float]]:
    """OCSANA+ at the top of subcolumn 1, with DrugReflector directly below.

    The Class C3 names then fill three subcolumns, so this row has four.
    """
    dual = [it for it in items if it["name"] == "OCSANA+"]
    rest = [it for it in items if it["name"] != "OCSANA+"]
    if not dual:
        return grid(order_items(items, "both"))
    reflector = [it for it in rest if it["name"] == "DrugReflector"]
    others = order_items(
        [it for it in rest if it["name"] != "DrugReflector"], "both",
    )
    first = dual + reflector
    k = 3
    n = len(others)
    heights = [n // k] * k if n else []
    for i in range(n % k):
        heights[i] += 1
    bands: list[list] = [first]
    idx = 0
    for h in heights:
        bands.append(others[idx:idx + h])
        idx += h
    n_lines = max(len(band) for band in bands)
    lines = [
        [band[r] if r < len(band) else None for band in bands]
        for r in range(n_lines)
    ]
    col_w = [max((it["span"] for it in band), default=0.0) for band in bands]
    return lines, col_w


def used_width(col_w: list[float]) -> float:
    active = [w for w in col_w if w > 0]
    if not active:
        return 0.0
    return sum(active) + NAME_GAP * (len(active) - 1)


def render(mode: str) -> None:
    citekey_to_num = load_citekey_to_ref_num()
    groups: dict[tuple, list] = defaultdict(list)
    for name, year, level, modes in src.METHODS:
        groups[tuple(k in modes for k in KEYS)].append((name, year, level))
    combos = sorted(groups, key=lambda c: (-len(groups[c]), sum(c)))
    field = NAME_RIGHT - NAME_X
    max_count = max(len(groups[c]) for c in combos)

    rows = []
    for combo in combos:
        members = list(groups[combo])
        items = []
        for name, year, level in members:
            ref = str(method_name_to_ref_num(name, citekey_to_num))
            items.append({
                "name": name,
                "year": year,
                "level": level,
                "ref": ref,
                "span": name_span(name, ref, level),
            })
        if mode == "both":
            lines, col_w = grid_both(items)
        else:
            items = order_items(items, mode)
            lines, col_w = grid(items)
        used = used_width(col_w)
        key = "".join(k for k, bit in zip(KEYS, combo) if bit)
        if used > field + 0.02:
            raise SystemExit(
                f"{mode} {key}: name grid is {used:.2f} in; field is {field:.2f}"
            )
        row_h = max(0.34, len(lines) * LINE_H + 0.10)
        rows.append({
            "combo": combo, "items": items, "lines": lines,
            "col_w": col_w, "h": row_h,
        })

    legend_h = 0.92
    header_h = 0.28
    footnote_h = 0.32 if mode == "both" else 0.0
    fig_h = legend_h + header_h + sum(r["h"] for r in rows) + 0.12 + footnote_h
    if fig_h > 8.75:
        raise SystemExit(f"sample is {fig_h:.2f} in tall; limit is 8.75")

    # font family set by configure_sans()

    fig, ax = plt.subplots(figsize=(PRINT_W, fig_h))
    ax.set_xlim(0, PRINT_W)
    ax.set_ylim(0, fig_h)
    ax.axis("off")
    fig.subplots_adjust(0, 0, 1, 1)
    fig.patch.set_facecolor("white")

    y = fig_h - 0.08
    ax.text(PRINT_W / 2, y, "Bar fill is the publication-year cohort",
            ha="center", va="top", fontsize=9, color=INK)
    y -= 0.22
    cohort_labels = []
    for label, yrs, col in src.YEAR_BANDS:
        n = sum(1 for m in src.METHODS if m[1] in yrs)
        cohort_labels.append((f"{label}  (n={n})", col))
    gap = 0.16
    cw = [width(lab, LABEL_PT) + 0.24 for lab, _ in cohort_labels]
    x = PRINT_W / 2 - (sum(cw) + gap * (len(cw) - 1)) / 2
    for (lab, col), w in zip(cohort_labels, cw):
        ax.add_patch(patches.Rectangle((x, y - 0.12), 0.16, 0.11,
                                       facecolor=col, edgecolor="white", lw=0.4))
        ax.text(x + 0.20, y - 0.065, lab, ha="left", va="center",
                fontsize=LABEL_PT, color="#1F2937")
        x += w + gap

    y -= 0.30
    ax.text(PRINT_W / 2, y, "Explicitness class",
            ha="center", va="top", fontsize=9, color=INK)
    y -= 0.22
    class_labels = [("Class C0", 0), ("Class C1", 1), ("Class C2", 2), ("Class C3", 3)]
    class_w = [width(lab, LABEL_PT) + 0.28 for lab, _ in class_labels]
    x = PRINT_W / 2 - (sum(class_w) + 0.22 * 3) / 2
    for (lab, lvl), w in zip(class_labels, class_w):
        style = src.LEVEL_STYLE[lvl]
        ax.scatter([x + 0.06], [y], s=22, marker=style["marker"],
                   facecolor=style["mfc"], edgecolor=style["color"],
                   linewidths=0.7, clip_on=False, zorder=5)
        ax.text(x + 0.16, y, lab, ha="left", va="center",
                fontsize=LABEL_PT, color=style["color"])
        x += w + 0.22

    y -= 0.28
    for i, key in enumerate(KEYS):
        ax.text(DOT_X[i], y, key, ha="center", va="center",
                fontsize=LABEL_PT, color=INK)
    ax.text(COUNT_X, y, "n", ha="center", va="center",
            fontsize=LABEL_PT, color=INK)
    y -= 0.10

    for ri, row in enumerate(rows):
        y -= row["h"]
        mid = y + row["h"] / 2
        if ri % 2 == 0:
            ax.add_patch(patches.Rectangle(
                (0.08, y + 0.02), PRINT_W - 0.16, row["h"] - 0.04,
                facecolor="#F4F6F8", edgecolor="none", zorder=0,
            ))
        active = [i for i, bit in enumerate(row["combo"]) if bit]
        if len(active) >= 2:
            ax.plot([DOT_X[min(active)], DOT_X[max(active)]], [mid, mid],
                    color="#1F2937", lw=1.1, zorder=2, solid_capstyle="round")
        for i in range(4):
            if i in active:
                ax.add_patch(plt.Circle((DOT_X[i], mid), 0.055,
                                        facecolor="#1F2937", edgecolor="white",
                                        lw=0.4, zorder=3))
            else:
                ax.add_patch(plt.Circle((DOT_X[i], mid), 0.038,
                                        facecolor="#D1D5DB", edgecolor="none", zorder=2))

        counts = [0, 0, 0]
        for item in row["items"]:
            counts[src.cohort_index(item["year"])] += 1
        unit = BAR_LANE / max_count
        bx = BAR_X
        for pi, sub in enumerate(counts):
            if sub == 0:
                continue
            seg = unit * sub
            ax.add_patch(patches.Rectangle(
                (bx, mid - 0.055), seg, 0.11,
                facecolor=src.YEAR_BANDS[pi][2], edgecolor="white", lw=0.3, zorder=3,
            ))
            bx += seg
        ax.text(COUNT_X, mid, str(len(row["items"])), ha="center", va="center",
                fontsize=LABEL_PT, color=INK)

        block_h = len(row["lines"]) * LINE_H
        text_top = mid + block_h / 2 - 0.02
        col_x = []
        cursor = NAME_X
        for w in row["col_w"]:
            col_x.append(cursor)
            cursor += w + NAME_GAP
        for li, line in enumerate(row["lines"]):
            ty = text_top - li * LINE_H
            for c, item in enumerate(line):
                if item is None:
                    continue
                tx = col_x[c]
                if item["name"] == "OCSANA+":
                    color = "#374151"
                    lay = ocsana_layout(item["ref"])
                    ax.text(tx, ty, "OCSANA+", ha="left", va="center",
                            fontsize=NAME_PT, color=color, zorder=4)
                    ax.text(tx + lay["ref_x"], ty + 0.055, item["ref"], ha="left", va="center",
                            fontsize=SUP_PT, color=color, zorder=4)
                    ax.text(tx + lay["open_x"], ty, "(", ha="left", va="center",
                            fontsize=NAME_PT, color=color, zorder=4)
                    c1 = src.LEVEL_STYLE[1]
                    c3 = src.LEVEL_STYLE[3]
                    ax.scatter([tx + lay["tri_x"]], [ty], s=16, marker=c1["marker"],
                               facecolor=c1["mfc"], edgecolor=c1["color"],
                               linewidths=0.5, clip_on=False, zorder=5)
                    ax.scatter([tx + lay["dia_x"]], [ty], s=14, marker=c3["marker"],
                               facecolor=c3["mfc"], edgecolor=c3["color"],
                               linewidths=0.5, clip_on=False, zorder=5)
                    ax.text(tx + lay["close_x"], ty, ")*", ha="left", va="center",
                            fontsize=NAME_PT, color=color, zorder=4)
                    continue
                label = display_name(item["name"])
                style = src.LEVEL_STYLE[item["level"]]
                color = style["color"]
                ax.text(tx, ty, label, ha="left", va="center",
                        fontsize=NAME_PT, color=color, zorder=4)
                rx = tx + width(label, NAME_PT) + 0.015
                ax.text(rx, ty + 0.055, item["ref"], ha="left", va="center",
                        fontsize=SUP_PT, color=color, zorder=4)
                if style["marker"] is not None:
                    mx = rx + width(item["ref"], SUP_PT) + 0.07
                    ax.scatter([mx], [ty], s=14, marker=style["marker"],
                               facecolor=style["mfc"], edgecolor=color,
                               linewidths=0.5, clip_on=False, zorder=5)

    if mode == "both":
        ax.text(
            0.12, 0.08,
            "* OCSANA+ comprises two workflows, assigned to Class C1 and Class C3.",
            ha="left", va="bottom", fontsize=LABEL_PT, color=INK,
        )

    out_dir = Path(__file__).resolve().parent
    stem = out_dir / "Fig2_settings_classes"
    fig.savefig(stem.with_suffix(".pdf"), facecolor="white")
    fig.savefig(stem.with_suffix(".eps"), format="eps", facecolor="white")
    src._save_figure(fig, stem.with_suffix(".png"), 300)
    src._save_figure(fig, stem.with_suffix(".tiff"), 600)
    plt.close(fig)
    print(f"{PRINT_W:.2f} x {fig_h:.2f} in")
    print(stem)


if __name__ == "__main__":
    render("both")
