from __future__ import annotations

from typing import Annotated

import typer

from llms_take_autism_test.analysis import analyze_run
from llms_take_autism_test.config import DEFAULT_RUN_LABEL
from llms_take_autism_test.paper import build_paper
from llms_take_autism_test.runner import prepare_pipeline, run_benchmark

app = typer.Typer(add_completion=False, pretty_exceptions_show_locals=False)


@app.command()
def prepare(
    force_download: Annotated[bool, typer.Option("--force-download")] = False,
) -> None:
    prepare_pipeline(force_download=force_download)


@app.command()
def run(
    run_label: Annotated[str, typer.Option("--run-label")] = DEFAULT_RUN_LABEL,
    force_download: Annotated[bool, typer.Option("--force-download")] = False,
) -> None:
    run_benchmark(run_label=run_label, force_download=force_download)


@app.command("analyze")
def analyze_command(
    run_label: Annotated[str, typer.Option("--run-label")] = DEFAULT_RUN_LABEL,
) -> None:
    analyze_run(run_label=run_label)


@app.command("build-paper")
def build_paper_command(
    run_label: Annotated[str, typer.Option("--run-label")] = DEFAULT_RUN_LABEL,
) -> None:
    build_paper(run_label=run_label)


@app.command()
def all(
    run_label: Annotated[str, typer.Option("--run-label")] = DEFAULT_RUN_LABEL,
    force_download: Annotated[bool, typer.Option("--force-download")] = False,
) -> None:
    run_benchmark(run_label=run_label, force_download=force_download)
    analyze_run(run_label=run_label)
    build_paper(run_label=run_label)


def main() -> None:
    app()
