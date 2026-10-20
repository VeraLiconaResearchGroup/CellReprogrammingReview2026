# Supporting Information S1, Figure 1

Waddington landscape of the four reprogramming settings, one application
example each. Panel D is cancer reversion with the lineage held. This is not
a main-text figure.

The editable slide is `Figure1_v4_unified.pptx`. Export uses Microsoft
PowerPoint (or LibreOffice) and is not part of `scripts/run_offline.sh` or
the Docker image.

## Regenerate

1. Edit `Figure1_v4_unified.pptx` if the landscape changes.
2. Export a PDF from PowerPoint, which keeps the curved arrows, then:

```bash
pip install pymupdf pillow
python3 export_fig1_tiff.py --pdf Figure1_v4_unified.pdf
```

`export_fig1_tiff.py` can also open the slide in PowerPoint and write
`Fig1.tiff` (600 dpi, LZW, content-cropped). LibreOffice can shorten freeform
arrows, so the PowerPoint PDF export is the one that matches the submission.
