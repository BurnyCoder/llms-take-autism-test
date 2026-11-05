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
- Adult AQ paper: Baron-Cohen et al. (2001), J Autism Dev Disord 31(1):5-17, <https://doi.org/10.1023/A:1005653411471>
- AQ-10 paper: Allison, Auyeung and Baron-Cohen (2012), J Am Acad Child Adolesc Psychiatry 51(2):202-212, <https://doi.org/10.1016/j.jaac.2011.11.003>
- OpenRouter model catalog: <https://openrouter.ai/api/v1/models>

## Requirements

- Python 3.12+
- `uv`
- `pdftotext`
- `strings` (GNU binutils)
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
uv run llms-take-autism-test repair-run --run-label pilot
uv run llms-take-autism-test analyze --run-label pilot
uv run llms-take-autism-test build-paper --run-label pilot
```

`repair-run` reparses saved raw completions without spending more API calls. It exists because some providers returned valid-looking output with literal `<TAB>` tokens instead of real tab characters.

## Pilot Results

The current committed pilot run is `artifacts/runs/pilot` (summaries in `summary_by_model_condition.csv`). The paper is built from the second run, `artifacts/runs/pilot-rerun`, whose scores differ for DeepSeek, GLM, GPT and Qwen.

Scores are the share of the 10 sampled items answered in the scored direction. Invalid or unparsable items count as 0, so models with invalid items score lower for formatting reasons as well as for their answers. Each score is from a single temperature-0 run.

Top combined normalized scores:

- `Qwen3 Max Thinking`: `0.90` self-report, `0.50` human roleplay
- `DeepSeek V3.2`: `0.80` self-report, `0.40` human roleplay
- `GPT-5.4`: `0.70` self-report, `0.20` human roleplay

Notable data-quality issue:

- `Gemini 3.1 Pro Preview` produced truncated or unparsable outputs on most sampled items (15 of 20 item responses invalid).
- `GLM 5.1`'s saved AQ-10 completions are empty in both conditions (10 of 20 item responses invalid). The runner also saves an empty completion after an API error, and the cause was not logged.

## Layout

- `src/llms_take_autism_test/`: benchmark code
- `tests/`: parser and pipeline tests
- `.cache/`: downloaded sources and extracted text, not committed
- `artifacts/`: benchmark manifests, responses, summaries, figures
- `paper/`: LaTeX manuscript and generated snippets
