from __future__ import annotations

from llms_take_autism_test.config import CONDITION_LABELS, RESPONSE_OPTIONS
from llms_take_autism_test.types import ConditionName, QuestionnaireItem


def build_messages(
    condition: ConditionName,
    instrument: str,
    items: list[QuestionnaireItem],
    invalid_retry: bool = False,
) -> list[dict[str, str]]:
    system_prompt = (
        "You are completing an autism questionnaire benchmark. Follow the format exactly. "
        "Return plain TSV only and never use Markdown tables or code fences."
    )

    retry_note = ""
    if invalid_retry:
        retry_note = (
            "\nYour previous response did not match the required TSV schema. "
            "Return only the corrected TSV rows and the NOTE row."
        )

    item_block = "\n".join(f"{item.item_id}. {item.text}" for item in items)
    user_prompt = (
        f"Questionnaire: {instrument}\n"
        f"Condition: {condition}\n"
        f"Instruction: {CONDITION_LABELS[condition]}\n\n"
        f"Allowed answers: {' | '.join(RESPONSE_OPTIONS)}\n"
        "Return exactly one line per questionnaire item in this format:\n"
        "item_id<TAB>answer\n"
        "After the item rows, add one final line in this format:\n"
        "NOTE<TAB>one short sentence\n"
        "Do not add any extra text before or after the TSV.\n"
        f"{retry_note}\n\n"
        "Items:\n"
        f"{item_block}\n"
    )

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
