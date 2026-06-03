
"""Shared helpers for reproduction notebooks.

Author: Paola Vera-Licona (Vera-Licona Research Group,
University of Connecticut School of Medicine)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    path = (start or Path.cwd()).resolve()
    for candidate in [path, *path.parents]:
        if (candidate / "figure3" / "fig3_reproducibility.py").is_file():
            return candidate
    raise FileNotFoundError(
        "Could not locate repository root (expected figure3/fig3_reproducibility.py)."
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

