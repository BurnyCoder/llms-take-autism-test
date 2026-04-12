from llms_take_autism_test.benchmark import build_benchmark_manifest
from llms_take_autism_test.config import AQ10_INSTRUMENT, AQ_ADULT_INSTRUMENT
from llms_take_autism_test.types import QuestionnaireItem


def _items(instrument: str, count: int) -> list[QuestionnaireItem]:
    return [
        QuestionnaireItem(
            instrument=instrument,
            item_id=item_id,
            text=f"{instrument} item {item_id}",
            keyed_response="agree" if item_id % 2 else "disagree",
        )
        for item_id in range(1, count + 1)
    ]


def test_benchmark_sampling_is_deterministic() -> None:
    question_banks = {
        AQ10_INSTRUMENT: _items(AQ10_INSTRUMENT, 10),
        AQ_ADULT_INSTRUMENT: _items(AQ_ADULT_INSTRUMENT, 50),
    }

    first = build_benchmark_manifest(question_banks)
    second = build_benchmark_manifest(question_banks)

    assert first["sampled_item_ids"] == second["sampled_item_ids"]
    assert len(first["sampled_item_ids"][AQ10_INSTRUMENT]) == 5
    assert len(first["sampled_item_ids"][AQ_ADULT_INSTRUMENT]) == 5
