# AGENTS

## Objective
- Build a reproducible pilot benchmark that has frontier and open-weight LLMs answer Autism Spectrum Quotient items through OpenRouter.
- Deliver a working `uv` project, experiments, logged outputs, figures, and a compiled LaTeX paper.

## Current State
- Local git repo initialized on `main`.
- Remote target is the existing empty public repo `BurnyCoder/llms-take-autism-test`.
- `uv` project scaffold exists.
- Python dependencies are installed through `uv`.
- The implementation baseline is committed and pushed to `origin/main`.
- `ruff` passes.
- `pytest` passes.
- Real-source ingestion succeeds for both AQ-10 and adult AQ.
- The pilot benchmark run `artifacts/runs/pilot` completed.
- The validation rerun `artifacts/runs/pilot-rerun` completed.
- Aggregate artifacts and the LaTeX paper were generated successfully.
- A second benchmark validation pass completed with a replacement OpenRouter API key.
- Official source URLs identified:
  - `AQ10.pdf` from the Autism Research Centre.
  - `AQ_Scoring_Key.doc` for the adult AQ.
- Practical extractor constraint:
  - `pdftotext` is available locally.
  - `antiword` is not available and cannot be installed via `apt-get` in this environment due permission errors.
  - Adult AQ extraction will therefore use `strings` plus parser cleanup, with scoring directions hand-encoded in `config.AQ_ADULT_AGREE_ITEMS`. A 2026-11-05 check against the official scoring key found item 1 mis-keyed as agree (now fixed); item 1 was not sampled, so the committed runs are unaffected.

## Locked Decisions
- Use English only.
- Use 8 representative OpenRouter model families:
  Claude, GPT, Gemini, Llama, DeepSeek, GLM, Qwen, Mistral.
- Run 2 prompting conditions:
  `ai_self_report` and `typical_human_roleplay`.
- Use 5 sampled items from `AQ-10` and 5 sampled items from adult `AQ`.
- Keep scoring hidden from models.
- Report exploratory subset scores only.
- Do not claim diagnosis or binary autism classification from the subset benchmark.

## Active Plan
1. Commit and push the rerun artifacts.
2. Keep both runs for comparison.

## Open Risks
- Adult AQ `.doc` formatting marks are not preserved by `strings`; scoring directions must be encoded from a verified reference list.
- Some OpenRouter model ids may disappear; the runner uses same-family fallback logic.
- Gemini and GLM produced substantial formatting or empty-output failures in the current pilot run.
- The replacement API key did not remove the Gemini or GLM failure modes.

## Immediate Next Steps
- Commit the rerun artifacts and updated paper.
- Push the comparison state to GitHub.

## Quality Checklist
- [x] Code runs end to end
- [x] Tests pass
- [x] Logging is informative
- [x] README matches reality
- [x] AGENTS matches reality
- [x] Results look coherent
- [x] Paper compiles
- [x] Commits are pushed

## Pilot Findings
- Mean combined normalized score:
  - `0.525` for `ai_self_report`
  - `0.19` for `typical_human_roleplay`
- Highest self-report score: `Qwen3 Max Thinking` at `0.90`.
- Highest human-roleplay score: `Qwen3 Max Thinking` at `0.50`.
- Major data-quality caveat:
  - `Gemini 3.1 Pro Preview` was mostly unparsable.
  - `GLM 5.1` has empty saved AQ-10 completions (cause not logged).

## Rerun Findings
- The rerun label is `pilot-rerun`.
- Invalid rows remained `25`, the same as the original pilot run.
- `Gemini 3.1 Pro Preview` remained mostly unparsable.
- `GLM 5.1` remained unstable, with invalid completions shifting from AQ-10-only to both instruments under `ai_self_report`.
- Top rerun scores:
  - `Qwen3 Max Thinking`: `0.80` self-report, `0.50` human roleplay
  - `GPT-5.4`: `0.70` self-report, `0.10` human roleplay
  - `DeepSeek V3.2`: `0.60` self-report, `0.10` human roleplay
