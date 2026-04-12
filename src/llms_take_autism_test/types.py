from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

ResponseOption = Literal[
    "Definitely Agree",
    "Slightly Agree",
    "Slightly Disagree",
    "Definitely Disagree",
]
KeyedResponse = Literal["agree", "disagree"]
ConditionName = Literal["ai_self_report", "typical_human_roleplay"]


@dataclass(slots=True)
class QuestionnaireItem:
    instrument: str
    item_id: int
    text: str
    keyed_response: KeyedResponse

    def to_record(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ModelFamilySpec:
    family: str
    vendor: str
    label: str
    preferred_id: str
    fallback_keywords: tuple[str, ...]


@dataclass(slots=True)
class ResolvedModel:
    family: str
    vendor: str
    label: str
    preferred_id: str
    resolved_id: str
    resolved_name: str
    context_length: int | None

    def to_record(self) -> dict[str, object]:
        return asdict(self)
