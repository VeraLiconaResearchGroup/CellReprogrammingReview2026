#!/usr/bin/env python3
"""Export Figure 1 PPTX to high-resolution PNG via LibreOffice UNO."""

from __future__ import annotations

import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

HERE = Path(__file__).resolve().parent
PPTX = HERE / "Figure1_v4_unified.pptx"
OUT_PNG = HERE / "Fig1_render.png"
PORT = 2002
WIDTH = 9000  # 2x final; downsampled to 4500 in finalize step


def prop(name, value):
    from com.sun.star.beans import PropertyValue

    p = PropertyValue()
    p.Name = name
    p.Value = value
    return p


def file_url(path: Path) -> str:
    return "file://" + urllib.parse.quote(str(path.resolve()))


def main() -> None:
    soffice = "/Applications/LibreOffice.app/Contents/MacOS/soffice"
    proc = subprocess.Popen(
        [
            soffice,
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            f"--accept=socket,host=127.0.0.1,port={PORT};urp;StarOffice.ComponentContext",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(3)

    try:
        import uno
        from com.sun.star.beans import PropertyValue

        local_ctx = uno.getComponentContext()
        resolver = local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", local_ctx
        )
        ctx = resolver.resolve(
            f"uno:socket,host=127.0.0.1,port={PORT};urp;StarOffice.ComponentContext"
        )
        sm = ctx.ServiceManager
        desktop = sm.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

        doc = desktop.loadComponentFromURL(
            file_url(PPTX),
            "_blank",
            0,
            (prop("Hidden", True),),
        )

        filter_data = (
            PropertyValue("PixelWidth", 0, WIDTH, 0),
        )
        export_props = (
            prop("FilterName", "impress_png_Export"),
            prop("FilterData", filter_data),
        )
        doc.storeToURL(file_url(OUT_PNG), export_props)
        doc.close(True)
        print(f"Exported {OUT_PNG}")
    finally:
        proc.terminate()
        proc.wait(timeout=10)


if __name__ == "__main__":
    # UNO must run under LibreOffice's bundled Python with correct PYTHONPATH.
    main()
