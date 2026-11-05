from __future__ import annotations

from pathlib import Path

import matplotlib
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from llms_take_autism_test.config import PAPER_GENERATED_DIR, RUNS_DIR
from llms_take_autism_test.utils import ensure_dir, read_json, read_jsonl


def analyze_run(run_label: str) -> Path:
    run_dir = RUNS_DIR / run_label
    responses = read_jsonl(run_dir / "responses.jsonl")
    manifest = read_json(run_dir / "run_manifest.json")

    df = pd.DataFrame(responses)
    if df.empty:
        raise RuntimeError("No responses found to analyze")

    summary = (
        df.groupby(["model_label", "model_family", "condition"], as_index=False)
        .agg(
            combined_raw_score=("score", "sum"),
            combined_normalized_score=("score", "mean"),
            invalid_items=("valid", lambda values: int((~pd.Series(values)).sum())),
        )
        .sort_values(["model_family", "model_label", "condition"])
    )
    pivot = (
        summary.pivot(
            index=["model_label", "model_family"],
            columns="condition",
            values="combined_normalized_score",
        )
        .reset_index()
        .rename_axis(columns=None)
    )
    pivot["delta_roleplay_minus_self"] = (
        pivot["typical_human_roleplay"] - pivot["ai_self_report"]
    )
    instrument_summary = (
        df.groupby(["instrument", "condition"], as_index=False)
        .agg(
            mean_score=("score", "mean"),
            invalid_items=("valid", lambda values: int((~pd.Series(values)).sum())),
        )
        .sort_values(["instrument", "condition"])
    )

    summary.to_csv(run_dir / "summary_by_model_condition.csv", index=False)
    pivot.to_csv(run_dir / "summary_by_model.csv", index=False)
    instrument_summary.to_csv(run_dir / "summary_by_instrument.csv", index=False)

    _plot_model_scores(summary, run_dir / "model_scores.png")

    generated_dir = ensure_dir(PAPER_GENERATED_DIR)
    _write_paper_snippets(
        generated_dir=generated_dir,
        manifest=manifest,
        summary=summary,
        pivot=pivot,
        instrument_summary=instrument_summary,
        run_label=run_label,
        item_total=len(df),
    )

    return run_dir


def _plot_model_scores(summary: pd.DataFrame, destination: Path) -> None:
    ordered = summary["model_label"].drop_duplicates().tolist()
    fig, ax = plt.subplots(figsize=(12, 6))
    width = 0.35
    x_positions = range(len(ordered))

    self_scores = [
        float(
            summary.loc[
                (summary["model_label"] == label) & (summary["condition"] == "ai_self_report"),
                "combined_normalized_score",
            ].iloc[0]
        )
        for label in ordered
    ]
    roleplay_scores = [
        float(
            summary.loc[
                (summary["model_label"] == label)
                & (summary["condition"] == "typical_human_roleplay"),
                "combined_normalized_score",
            ].iloc[0]
        )
        for label in ordered
    ]

    left_positions = [index - width / 2 for index in x_positions]
    right_positions = [index + width / 2 for index in x_positions]
    ax.bar(left_positions, self_scores, width=width, label="AI self-report")
    ax.bar(right_positions, roleplay_scores, width=width, label="Typical human roleplay")
    ax.set_xticks(list(x_positions))
    ax.set_xticklabels(ordered, rotation=30, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Combined normalized score")
    ax.set_title("AQ subset score by model and prompting condition")
    ax.legend()
    fig.tight_layout()
    fig.savefig(destination, dpi=200)
    plt.close(fig)


def _write_paper_snippets(
    generated_dir: Path,
    manifest: dict[str, object],
    summary: pd.DataFrame,
    pivot: pd.DataFrame,
    instrument_summary: pd.DataFrame,
    run_label: str,
    item_total: int,
) -> None:
    top_self = summary.loc[summary["condition"] == "ai_self_report"].sort_values(
        "combined_normalized_score", ascending=False
    )
    top_roleplay = summary.loc[summary["condition"] == "typical_human_roleplay"].sort_values(
        "combined_normalized_score", ascending=False
    )
    abstract = (
        f"This pilot benchmark evaluated {len(pivot)} LLMs through OpenRouter on 10 sampled "
        "Autism Spectrum Quotient items, split across AQ-10 and the adult AQ. "
        f"The strongest AI self-report score came from {top_self.iloc[0]['model_label']} "
        f"({top_self.iloc[0]['combined_normalized_score']:.2f}), while the strongest typical "
        f"human roleplay score came from {top_roleplay.iloc[0]['model_label']} "
        f"({top_roleplay.iloc[0]['combined_normalized_score']:.2f}). "
        "Results should be interpreted as exploratory questionnaire behavior, not diagnosis."
    )
    methods = (
        "The benchmark used official Autism Research Centre source documents, deterministic "
        "sampling with seed 20260412, hidden scoring, English-only prompts, and two conditions: "
        "AI self-report and generic human roleplay."
    )
    self_mean = summary.loc[
        summary["condition"] == "ai_self_report", "combined_normalized_score"
    ].mean()
    roleplay_mean = summary.loc[
        summary["condition"] == "typical_human_roleplay", "combined_normalized_score"
    ].mean()
    invalid_total = int(summary["invalid_items"].sum())
    results = (
        f"The run label was {run_label}. Mean combined normalized score was "
        f"{self_mean:.2f} "
        "for AI self-report and "
        f"{roleplay_mean:.2f} "
        "for generic human roleplay. "
        "Invalid or unparsable items were scored 0 and kept in the denominator; "
        f"{invalid_total} of {item_total} item responses were invalid, so scores for models "
        "with invalid items reflect formatting failures as well as answers."
    )
    limitations = (
        "This study uses only 5 sampled items from each questionnaire, so it cannot justify "
        "binary thresholding or diagnostic claims. The adult AQ scoring directions were encoded "
        "by hand because the strings-based DOC extractor did not preserve the original score "
        "markers. Each run makes one temperature-0 request per model, condition and instrument "
        "(plus one retry after a formatting error), so the scores are single-run observations."
    )

    (generated_dir / "abstract.tex").write_text(_tex_escape(abstract) + "\n", encoding="utf-8")
    (generated_dir / "methods.tex").write_text(_tex_escape(methods) + "\n", encoding="utf-8")
    (generated_dir / "results.tex").write_text(_tex_escape(results) + "\n", encoding="utf-8")
    (generated_dir / "limitations.tex").write_text(
        _tex_escape(limitations) + "\n",
        encoding="utf-8",
    )
    pivot.to_latex(generated_dir / "model_table.tex", index=False, float_format="%.2f", escape=True)
    instrument_summary.to_latex(
        generated_dir / "instrument_table.tex",
        index=False,
        float_format="%.2f",
        escape=True,
    )


def _tex_escape(text: str) -> str:
    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
    }
    escaped = text
    for old, new in replacements.items():
        escaped = escaped.replace(old, new)
    return escaped
