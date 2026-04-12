from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from llms_take_autism_test.config import PAPER_DIR, PAPER_GENERATED_DIR, RUNS_DIR
from llms_take_autism_test.utils import ensure_dir


def build_paper(run_label: str) -> Path:
    run_dir = RUNS_DIR / run_label
    ensure_dir(PAPER_GENERATED_DIR)

    source_figure = run_dir / "model_scores.png"
    if source_figure.exists():
        shutil.copy2(source_figure, PAPER_GENERATED_DIR / "model_scores.png")

    subprocess.run(
        ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "paper.tex"],
        cwd=PAPER_DIR,
        check=True,
    )
    return PAPER_DIR / "paper.pdf"
