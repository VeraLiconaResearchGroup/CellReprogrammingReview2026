#!/usr/bin/env python3
"""Export Figure 1 PPTX to a 600 dpi submission TIFF.

Pipeline:
  1. Re-export slide 1 from Figure1_v4_unified.pptx via Microsoft PowerPoint (PDF).
  2. Rasterize the PDF at 2× target pixels with PyMuPDF.
  3. Crop to the slide content bounding box (drops unused slide margins).
  4. Downscale to 600 dpi at PLOS full-page width (4500 px).

Outputs (next to this script):
  - Fig1_export.pdf   (intermediate)
  - Fig1.tiff         (600 dpi, LZW-compressed RGB; Fig1.tif alias)
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
PPTX_CANDIDATES = [
    HERE / "Figure1_v4_unified.pptx",
    HERE.parents[1] / "Figures&Tables" / "Figure1" / "Figure1_v4_unified.pptx",
]
PDF = HERE / "Fig1_export.pdf"
OUT = HERE / "Fig1.tiff"

DPI = 600
TARGET_W = 4500  # 7.5 in × 600 dpi (PLOS full page width)
SUPERSAMPLE = 2
# Padding around the PPTX shape bounding box (inches).
CROP_PAD_IN = 0.12
EMU_PER_INCH = 914400


@dataclass(frozen=True)
class CropBox:
    """Content region on the slide, in inches from the top-left corner."""

    left: float
    top: float
    right: float
    bottom: float

    @property
    def width(self) -> float:
        return self.right - self.left

    @property
    def height(self) -> float:
        return self.bottom - self.top

    @property
    def aspect(self) -> float:
        return self.width / self.height


def find_pptx() -> Path:
    for path in PPTX_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError(
        "Figure1_v4_unified.pptx not found. Save your edited deck as:\n"
        f"  {PPTX_CANDIDATES[0]}"
    )


def slide_size_inches(pptx: Path) -> tuple[float, float]:
    from pptx import Presentation

    prs = Presentation(pptx)
    return prs.slide_width / EMU_PER_INCH, prs.slide_height / EMU_PER_INCH


def content_crop_box(pptx: Path) -> CropBox:
    """Bounding box of all shapes on slide 1, padded slightly."""
    from pptx import Presentation

    prs = Presentation(pptx)
    slide = prs.slides[0]
    slide_w, slide_h = slide_size_inches(pptx)

    tops: list[float] = []
    bottoms: list[float] = []
    lefts: list[float] = []
    rights: list[float] = []
    for shape in slide.shapes:
        if not hasattr(shape, "top"):
            continue
        tops.append(shape.top / EMU_PER_INCH)
        bottoms.append((shape.top + shape.height) / EMU_PER_INCH)
        lefts.append(shape.left / EMU_PER_INCH)
        rights.append((shape.left + shape.width) / EMU_PER_INCH)

    if not tops:
        raise RuntimeError(f"No shapes found on slide 1 of {pptx}")

    box = CropBox(
        left=max(0.0, min(lefts) - CROP_PAD_IN),
        top=max(0.0, min(tops) - CROP_PAD_IN),
        right=min(slide_w, max(rights) + CROP_PAD_IN),
        bottom=min(slide_h, max(bottoms) + CROP_PAD_IN),
    )
    return box


def export_pdf_via_powerpoint(pptx: Path, pdf: Path) -> None:
    # Use active presentation after open (not "set pres to open …") — avoids
    # AppleScript -2753 on recent PowerPoint builds.
    script = f'''
set pptxPath to POSIX file "{pptx.resolve()}"
set pdfPath to POSIX file "{pdf.resolve()}"

tell application "Microsoft PowerPoint"
    activate
    open pptxPath
    delay 4
    tell active presentation
        save in pdfPath as save as PDF
        close saving no
    end tell
end tell
'''
    subprocess.run(["osascript", "-e", script], check=True, timeout=120)
    if not pdf.exists():
        raise RuntimeError(f"PowerPoint did not create {pdf}")


def export_pdf_via_libreoffice(pptx: Path, pdf: Path) -> None:
    soffice = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
    if not soffice.exists():
        raise RuntimeError("LibreOffice not found; install it or export PDF manually.")
    out_dir = pdf.parent
    subprocess.run(
        [
            str(soffice),
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(out_dir),
            str(pptx.resolve()),
        ],
        check=True,
    )
    generated = out_dir / f"{pptx.stem}.pdf"
    if not generated.exists():
        raise RuntimeError(f"LibreOffice did not create {generated}")
    if generated != pdf:
        generated.replace(pdf)


def export_pdf(pptx: Path, pdf: Path) -> str:
    try:
        export_pdf_via_powerpoint(pptx, pdf)
        return "Microsoft PowerPoint"
    except (subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"PowerPoint export failed ({exc}); trying LibreOffice…")
        export_pdf_via_libreoffice(pptx, pdf)
        return "LibreOffice"


def pdf_to_tiff(pdf: Path, out: Path, crop: CropBox, slide_w: float, slide_h: float) -> tuple[int, int]:
    try:
        import fitz
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "pymupdf", "-q"], check=True)
        import fitz

    from PIL import Image

    target_h = round(TARGET_W / crop.aspect)

    doc = fitz.open(pdf)
    page = doc[0]
    zoom = (TARGET_W * SUPERSAMPLE) / page.rect.width
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False, colorspace=fitz.csRGB)
    doc.close()

    Image.MAX_IMAGE_PIXELS = None
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)

    # Map slide inches → raster pixels (PDF page matches full slide).
    sx = im.width / slide_w
    sy = im.height / slide_h
    box = (
        int(round(crop.left * sx)),
        int(round(crop.top * sy)),
        int(round(crop.right * sx)),
        int(round(crop.bottom * sy)),
    )
    im = im.crop(box)
    im = im.resize((TARGET_W, target_h), Image.Resampling.LANCZOS)
    im.save(out, format="TIFF", compression="tiff_lzw", dpi=(DPI, DPI))
    return TARGET_W, target_h


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pdf",
        type=Path,
        help="Use a PowerPoint-exported PDF (e.g. Figure1_v4_unified.pdf) instead of LibreOffice",
    )
    args = parser.parse_args()

    pptx = find_pptx()
    slide_w, slide_h = slide_size_inches(pptx)
    crop = content_crop_box(pptx)
    target_h = round(TARGET_W / crop.aspect)
    print(f"PPTX: {pptx}")
    print(
        f"Crop box (in): L={crop.left:.2f} T={crop.top:.2f} "
        f"R={crop.right:.2f} B={crop.bottom:.2f} "
        f"({crop.width:.2f}×{crop.height:.2f})"
    )

    if args.pdf:
        pdf_path = args.pdf.resolve()
        if not pdf_path.exists():
            raise SystemExit(f"PDF not found: {pdf_path}")
        print(f"PDF: {pdf_path} (manual export)")
    else:
        print("Exporting PDF…")
        backend = export_pdf(pptx, PDF)
        pdf_path = PDF
        print(f"Wrote {PDF} ({backend})")

    print(f"Rasterizing to {TARGET_W}×{target_h} px @ {DPI} dpi (content-cropped)…")
    pdf_to_tiff(pdf_path, OUT, crop, slide_w, slide_h)
    if args.pdf and pdf_path != PDF:
        PDF.write_bytes(pdf_path.read_bytes())
    # Keep .tif alias for older submission bundles.
    alias = HERE / "Fig1.tif"
    alias.write_bytes(OUT.read_bytes())
    size_mb = OUT.stat().st_size / (1024 * 1024)
    print(f"Wrote {OUT} ({size_mb:.2f} MB)")
    print(f"Wrote {alias}")


if __name__ == "__main__":
    main()
