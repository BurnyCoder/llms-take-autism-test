from __future__ import annotations

import random

from llms_take_autism_test.config import (
    AQ10_INSTRUMENT,
    AQ_ADULT_INSTRUMENT,
    CONDITION_LABELS,
    SAMPLE_SEED,
    SAMPLE_SIZE,
)
from llms_take_autism_test.types import QuestionnaireItem
from llms_take_autism_test.utils import utc_now_iso


def build_benchmark_manifest(
    question_banks: dict[str, list[QuestionnaireItem]],
) -> dict[str, object]:
    sampler = random.Random(SAMPLE_SEED)
    sampled = {}
    for instrument in (AQ10_INSTRUMENT, AQ_ADULT_INSTRUMENT):
        item_ids = [item.item_id for item in question_banks[instrument]]
        sampled[instrument] = sorted(sampler.sample(item_ids, SAMPLE_SIZE))

    return {
        "created_at": utc_now_iso(),
        "seed": SAMPLE_SEED,
        "sample_size": SAMPLE_SIZE,
        "conditions": list(CONDITION_LABELS),
        "sampled_item_ids": sampled,
    }


def materialize_sampled_items(
    question_banks: dict[str, list[QuestionnaireItem]], manifest: dict[str, object]
) -> dict[str, list[QuestionnaireItem]]:
    sampled_ids = manifest["sampled_item_ids"]
    materialized = {}
    for instrument, items in question_banks.items():
        wanted_ids = set(sampled_ids[instrument])
        materialized[instrument] = [item for item in items if item.item_id in wanted_ids]
    return materialized
