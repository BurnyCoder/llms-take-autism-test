from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from llms_take_autism_test.benchmark import build_benchmark_manifest, materialize_sampled_items
from llms_take_autism_test.config import (
    AQ10_INSTRUMENT,
    AQ_ADULT_INSTRUMENT,
    ARTIFACTS_DIR,
    CONDITION_LABELS,
    DEFAULT_RUN_LABEL,
    RUNS_DIR,
)
from llms_take_autism_test.openrouter import (
    chat_completion,
    fetch_model_catalog,
    require_api_key,
    resolve_models,
)
from llms_take_autism_test.prompting import build_messages
from llms_take_autism_test.sources import prepare_question_banks
from llms_take_autism_test.types import QuestionnaireItem
from llms_take_autism_test.utils import (
    configure_logging,
    ensure_dir,
    normalize_whitespace,
    slugify,
    utc_now_iso,
    write_json,
    write_jsonl,
)

VALID_ANSWERS = {
    "definitely agree": "Definitely Agree",
    "slightly agree": "Slightly Agree",
    "slightly disagree": "Slightly Disagree",
    "definitely disagree": "Definitely Disagree",
}


def prepare_pipeline(force_download: bool = False) -> dict[str, object]:
    question_banks = prepare_question_banks(force_download=force_download)
    manifest = build_benchmark_manifest(question_banks)
    write_json(ARTIFACTS_DIR / "benchmark_manifest.json", manifest)
    return manifest


def run_benchmark(run_label: str = DEFAULT_RUN_LABEL, force_download: bool = False) -> Path:
    run_dir = ensure_dir(RUNS_DIR / run_label)
    logger = configure_logging(run_dir / "benchmark.log")
    logger.info("Preparing source material")

    question_banks = prepare_question_banks(force_download=force_download)
    manifest = build_benchmark_manifest(question_banks)
    write_json(ARTIFACTS_DIR / "benchmark_manifest.json", manifest)

    sampled_items = materialize_sampled_items(question_banks, manifest)

    logger.info("Fetching OpenRouter model catalog")
    catalog = fetch_model_catalog()
    resolved_models = resolve_models(catalog)
    write_json(run_dir / "resolved_models.json", [model.to_record() for model in resolved_models])

    api_key = require_api_key()
    responses = []
    raw_dir = ensure_dir(run_dir / "raw")

    for model in resolved_models:
        for condition in CONDITION_LABELS:
            for instrument in (AQ10_INSTRUMENT, AQ_ADULT_INSTRUMENT):
                items = sampled_items[instrument]
                logger.info(
                    "Running %s | %s | %s",
                    model.resolved_id,
                    condition,
                    instrument,
                )
                raw_response, parsed_rows = _run_single_completion(
                    api_key=api_key,
                    model_id=model.resolved_id,
                    condition=condition,
                    instrument=instrument,
                    items=items,
                )
                raw_path = raw_dir / (
                    f"{slugify(model.family)}__{slugify(condition)}__{slugify(instrument)}.txt"
                )
                raw_path.write_text(raw_response, encoding="utf-8")
                for row in parsed_rows:
                    row.update(
                        {
                            "run_label": run_label,
                            "captured_at": utc_now_iso(),
                            "model_family": model.family,
                            "model_label": model.label,
                            "resolved_model_id": model.resolved_id,
                            "resolved_model_name": model.resolved_name,
                            "condition": condition,
                            "instrument": instrument,
                            "raw_completion_file": str(raw_path.relative_to(run_dir)),
                        }
                    )
                    responses.append(row)

    write_json(
        run_dir / "run_manifest.json",
        {
            "run_label": run_label,
            "created_at": utc_now_iso(),
            "conditions": list(CONDITION_LABELS),
            "sampled_item_ids": manifest["sampled_item_ids"],
            "resolved_models": [model.to_record() for model in resolved_models],
        },
    )
    write_jsonl(run_dir / "responses.jsonl", responses)
    return run_dir


def _run_single_completion(
    api_key: str,
    model_id: str,
    condition: str,
    instrument: str,
    items: list[QuestionnaireItem],
) -> tuple[str, list[dict[str, object]]]:
    messages = build_messages(condition=condition, instrument=instrument, items=items)
    raw_response = chat_completion(api_key=api_key, model_id=model_id, messages=messages)
    try:
        parsed_rows = parse_completion_table(raw_response, items)
    except ValueError:
        retry_messages = build_messages(
            condition=condition,
            instrument=instrument,
            items=items,
            invalid_retry=True,
        )
        raw_response = chat_completion(api_key=api_key, model_id=model_id, messages=retry_messages)
        try:
            parsed_rows = parse_completion_table(raw_response, items)
        except ValueError:
            parsed_rows = _invalid_rows(items)
    return raw_response, parsed_rows


def parse_completion_table(
    raw_response: str, items: list[QuestionnaireItem]
) -> list[dict[str, object]]:
    content = raw_response.strip().strip("`")
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    expected_ids = {item.item_id for item in items}
    note = ""
    answers: dict[int, str] = {}

    for line in lines:
        if "\t" not in line:
            raise ValueError("Response line is not TSV")
        left, right = [part.strip() for part in line.split("\t", 1)]
        if left.upper() == "NOTE":
            note = normalize_whitespace(right)
            continue
        if not left.isdigit():
            raise ValueError("Item identifier is not numeric")
        item_id = int(left)
        answer = VALID_ANSWERS.get(right.lower())
        if answer is None:
            raise ValueError(f"Unexpected answer option: {right}")
        answers[item_id] = answer

    if set(answers) != expected_ids:
        raise ValueError("Returned item ids did not match the expected set")

    return [
        {
            "item_id": item.item_id,
            "answer": answers[item.item_id],
            "valid": True,
            "score": _score_answer(item, answers[item.item_id]),
            "keyed_response": item.keyed_response,
            "note": note,
        }
        for item in items
    ]


def _score_answer(item: QuestionnaireItem, answer: str) -> int:
    if item.keyed_response == "agree":
        return int(answer in {"Definitely Agree", "Slightly Agree"})
    return int(answer in {"Definitely Disagree", "Slightly Disagree"})


def _invalid_rows(items: Iterable[QuestionnaireItem]) -> list[dict[str, object]]:
    return [
        {
            "item_id": item.item_id,
            "answer": "",
            "valid": False,
            "score": 0,
            "keyed_response": item.keyed_response,
            "note": "Formatting error after one retry",
        }
        for item in items
    ]
