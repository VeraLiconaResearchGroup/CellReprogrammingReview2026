"""Shared helpers for reproduction notebooks."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    path = (start or Path.cwd()).resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "s3_figure1" / "render_s3_fig1.py").is_file():
            return candidate
    raise FileNotFoundError(
        "Could not locate repository root (expected s3_figure1/render_s3_fig1.py)."
    )


def run_script(relative_path: str) -> None:
    root = repo_root()
    script = root / relative_path
    print(f"Running: {script}")
    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="")
        raise RuntimeError(f"{relative_path} failed (exit {result.returncode})")
