# LLMs Take an Autism Test

This repo runs a pilot benchmark in which current LLMs answer sampled items from the Autism Spectrum Quotient through OpenRouter, then aggregates the results into reproducible artifacts and a LaTeX paper.

The project is intentionally narrow:

- `AQ-10`: 5 sampled items
- adult `AQ`: 5 sampled items
- 8 model families
- 2 prompting conditions: `ai_self_report` and `typical_human_roleplay`

The outputs are exploratory subset scores. They are not diagnostic labels and should not be read as evidence that a model is literally autistic or non-autistic.

## Sources

- AQ-10 PDF: <https://docs.autismresearchcentre.com/tests/AQ10.pdf>
- Adult AQ scoring key: <https://docs.autismresearchcentre.com/tests/AQ_Scoring_Key.doc>
- Adult AQ page: <https://www.autismresearchcentre.com/tests/autism-spectrum-quotient-aq-adult/>
- NICE guideline: <https://www.nice.org.uk/guidance/cg142>
- OpenRouter model catalog: <https://openrouter.ai/api/v1/models>

## Requirements

- Python 3.12+
- `uv`
- `pdftotext`
- `latexmk` / `pdflatex`
- `OPENROUTER_API_KEY` in the environment

## Usage

Run the full pipeline:

```bash
OPENROUTER_API_KEY=... uv run llms-take-autism-test all --run-label pilot
```

Run individual stages:

```bash
uv run llms-take-autism-test prepare
OPENROUTER_API_KEY=... uv run llms-take-autism-test run --run-label pilot
uv run llms-take-autism-test analyze --run-label pilot
uv run llms-take-autism-test build-paper --run-label pilot
```

## Layout

- `src/llms_take_autism_test/`: benchmark code
- `tests/`: parser and pipeline tests
- `.cache/`: downloaded sources and extracted text, not committed
- `artifacts/`: benchmark manifests, responses, summaries, figures
- `paper/`: LaTeX manuscript and generated snippets
