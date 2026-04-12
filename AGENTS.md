# AGENTS

## Objective
- Build a reproducible pilot benchmark that has frontier and open-weight LLMs answer Autism Spectrum Quotient items through OpenRouter.
- Deliver a working `uv` project, experiments, logged outputs, figures, and a compiled LaTeX paper.

## Current State
- Local git repo initialized on `main`.
- Remote target is the existing empty public repo `BurnyCoder/llms-take-autism-test`.
- `uv` project scaffold exists.
- Python dependencies are installed through `uv`.
- Official source URLs identified:
  - `AQ10.pdf` from the Autism Research Centre.
  - `AQ_Scoring_Key.doc` for the adult AQ.
- Practical extractor constraint:
  - `pdftotext` is available locally.
  - `antiword` is not available and cannot be installed via `apt-get` in this environment due permission errors.
  - Adult AQ extraction will therefore use `strings` plus parser cleanup, with scoring direction cross-checked against public scoring references.

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
1. Finish repository scaffolding and baseline docs.
2. Implement source download, extraction, parsing, and deterministic item sampling.
3. Implement OpenRouter model resolution, prompting, response parsing, scoring, logging, and CLI.
4. Add tests for parsing, sampling, model resolution, and output parsing.
5. Run tests and fix failures.
6. Commit and push the scaffold/implementation milestone.
7. Run the pilot benchmark with the provided OpenRouter key.
8. Generate aggregate artifacts, figures, LaTeX snippets, and compile the paper.
9. Update docs to match actual behavior, then commit and push final results.

## Open Risks
- Adult AQ `.doc` formatting marks are not preserved by `strings`; scoring directions must be encoded from a verified reference list.
- Some OpenRouter model ids may disappear; the runner needs same-family fallback logic.
- A few models may ignore the TSV output contract; one formatting-only retry is required.

## Immediate Next Steps
- Write the implementation files and tests.
- Run `pytest`.
- Push the first meaningful milestone before spending tokens on the live benchmark.

## Quality Checklist
- [ ] Code runs end to end
- [ ] Tests pass
- [ ] Logging is informative
- [ ] README matches reality
- [ ] AGENTS matches reality
- [ ] Results look coherent
- [ ] Paper compiles
- [ ] Commits are pushed
