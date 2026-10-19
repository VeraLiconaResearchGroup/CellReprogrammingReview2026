"""Resolve a sans-serif font for figure scripts (macOS Arial or Linux Liberation/DejaVu)."""
from __future__ import annotations

from pathlib import Path

from matplotlib import font_manager
import matplotlib.pyplot as plt

CANDIDATES = [
    Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
    Path("/Library/Fonts/Arial.ttf"),
    Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/freefont/FreeSans.ttf"),
]

FONT_PATH: Path | None = None
FONT_NAME: str | None = None


def configure_sans() -> Path:
    global FONT_PATH, FONT_NAME
    if FONT_PATH is not None:
        return FONT_PATH
    for path in CANDIDATES:
        if not path.is_file():
            continue
        font_manager.fontManager.addfont(str(path))
        for sibling_name in (
            "Arial Italic.ttf",
            "Arial Bold.ttf",
            "LiberationSans-Italic.ttf",
            "LiberationSans-Bold.ttf",
            "DejaVuSans-Oblique.ttf",
            "DejaVuSans-Bold.ttf",
        ):
            sibling = path.parent / sibling_name
            if sibling.is_file():
                font_manager.fontManager.addfont(str(sibling))
        prop = font_manager.FontProperties(fname=str(path))
        FONT_NAME = prop.get_name()
        FONT_PATH = path
        plt.rcParams["font.family"] = FONT_NAME
        plt.rcParams["font.sans-serif"] = [FONT_NAME, "DejaVu Sans", "sans-serif"]
        plt.rcParams["pdf.fonttype"] = 42
        plt.rcParams["ps.fonttype"] = 42
        return FONT_PATH
    raise FileNotFoundError(
        "No suitable sans-serif font found. Install Arial, Liberation Sans, or DejaVu Sans."
    )


def font_name() -> str:
    configure_sans()
    assert FONT_NAME is not None
    return FONT_NAME
