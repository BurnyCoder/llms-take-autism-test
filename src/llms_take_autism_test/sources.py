from __future__ import annotations

import logging
import re
import subprocess
from pathlib import Path

import httpx

from llms_take_autism_test.config import (
    AQ10_INSTRUMENT,
    AQ10_ITEM_TEXT,
    AQ10_SOURCE_URL,
    AQ_ADULT_AGREE_ITEMS,
    AQ_ADULT_INSTRUMENT,
    AQ_ADULT_SCORING_URL,
    AQ_ADULT_TEXT_OVERRIDES,
    EXTRACTED_SOURCE_DIR,
    PARSED_SOURCE_DIR,
    RAW_SOURCE_DIR,
)
from llms_take_autism_test.types import QuestionnaireItem
from llms_take_autism_test.utils import ensure_dir, normalize_whitespace, read_json, write_json

LOGGER = logging.getLogger("llms_take_autism_test")


def download_sources(force: bool = False) -> dict[str, Path]:
    ensure_dir(RAW_SOURCE_DIR)
    targets = {
        AQ10_INSTRUMENT: (AQ10_SOURCE_URL, RAW_SOURCE_DIR / "AQ10.pdf"),
        AQ_ADULT_INSTRUMENT: (AQ_ADULT_SCORING_URL, RAW_SOURCE_DIR / "AQ_Scoring_Key.doc"),
    }

    with httpx.Client(timeout=60.0, follow_redirects=True) as client:
        for instrument, (url, destination) in targets.items():
            if destination.exists() and not force:
                continue
            LOGGER.info("Downloading %s source from %s", instrument, url)
            response = client.get(url)
            response.raise_for_status()
            destination.write_bytes(response.content)

    return {instrument: destination for instrument, (_, destination) in targets.items()}


def _extract_pdf_text(pdf_path: Path) -> str:
    extracted = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return extracted.stdout


def _extract_doc_text(doc_path: Path) -> str:
    extracted = subprocess.run(
        ["strings", "-n", "6", str(doc_path)],
        check=True,
        capture_output=True,
        text=True,
    )
    return extracted.stdout


def parse_aq10_text(text: str, expected_count: int | None = None) -> list[QuestionnaireItem]:
    lines = [line.rstrip() for line in text.splitlines()]
    item_ids: set[int] = set()
    current_id: int | None = None
    in_questions = False

    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Please tick one option"):
            in_questions = True
            continue
        if line.startswith("SCORING:"):
            break
        if not in_questions:
            continue
        if line in {"Definitely", "Agree", "Slightly", "Disagree"}:
            continue

        numbered = re.match(r"^(\d{1,2})\s+(.*)$", line)
        if numbered:
            current_id = int(numbered.group(1))
            item_ids.add(current_id)
            continue
        if re.fullmatch(r"\d{1,2}", line):
            current_id = int(line)
            item_ids.add(current_id)
            continue

    agree_match = re.search(
        r"Score 1 point for Definitely\s+or\s+Slightly\s+Agree on each of items (.+?)\.",
        text,
        re.DOTALL,
    )
    disagree_match = re.search(
        r"Score 1 point for Definitely\s+or\s+Slightly\s+Disagree on each of items (.+?)\.",
        text,
        re.DOTALL,
    )
    if agree_match is None or disagree_match is None:
        raise ValueError("Could not parse AQ-10 scoring rules")

    agree_items = _parse_number_list(agree_match.group(1))
    disagree_items = _parse_number_list(disagree_match.group(1))

    parsed_items = []
    for item_id in sorted(item_ids):
        if item_id in agree_items:
            keyed = "agree"
        elif item_id in disagree_items:
            keyed = "disagree"
        else:
            raise ValueError(f"AQ-10 item {item_id} missing from scoring rules")
        parsed_items.append(
            QuestionnaireItem(
                instrument=AQ10_INSTRUMENT,
                item_id=item_id,
                text=AQ10_ITEM_TEXT[item_id],
                keyed_response=keyed,
            )
        )

    if expected_count is not None and len(parsed_items) != expected_count:
        raise ValueError(f"Expected {expected_count} AQ-10 items, found {len(parsed_items)}")

    return parsed_items


def parse_adult_aq_text(text: str, expected_count: int | None = None) -> list[QuestionnaireItem]:
    cleaned_text = _normalize_doc_text(text)
    lines = [line.strip() for line in cleaned_text.splitlines()]
    filtered: list[str] = []
    seen_marker = False
    for line in lines:
        if not line:
            continue
        if "Responses that score 1 point are marked" in line:
            seen_marker = True
            continue
        if not seen_marker and expected_count is not None:
            continue
        if line.startswith("(") or line.startswith("@HP"):
            break
        if line in {
            "The Adult Autism Spectrum Quotient (AQ)",
            "Ages 16+: Scoring Key",
            "For full details, please see:",
            "Journal of Autism and Developmental Disorders",
            (
                "Responses that score 1 point are marked. Other responses score 0. "
                "For total score, sum all items."
            ),
            "definitely",
            "agree",
            "slightly",
            "disagree",
        }:
            continue
        if re.fullmatch(r"[A-Za-z0-9./:-]{1,12}", line) and not line.endswith("."):
            continue
        filtered.append(line)

    questions: list[str] = []
    buffer = ""
    for line in filtered:
        if not buffer:
            buffer = line
        else:
            joiner = "" if _needs_tight_join(buffer, line) else " "
            buffer = f"{buffer}{joiner}{line}"
        if buffer.endswith((".", "?", ").")):
            questions.append(_cleanup_question_text(buffer))
            buffer = ""

    if buffer:
        questions.append(_cleanup_question_text(buffer))

    parsed_items = []
    for index, question in enumerate(questions, start=1):
        canonical_text = AQ_ADULT_TEXT_OVERRIDES.get(index, question)
        parsed_items.append(
            QuestionnaireItem(
                instrument=AQ_ADULT_INSTRUMENT,
                item_id=index,
                text=canonical_text,
                keyed_response="agree" if index in AQ_ADULT_AGREE_ITEMS else "disagree",
            )
        )

    if expected_count is not None and len(parsed_items) != expected_count:
        raise ValueError(f"Expected {expected_count} adult AQ items, found {len(parsed_items)}")

    return parsed_items


def prepare_question_banks(force_download: bool = False) -> dict[str, list[QuestionnaireItem]]:
    ensure_dir(EXTRACTED_SOURCE_DIR)
    ensure_dir(PARSED_SOURCE_DIR)
    source_paths = download_sources(force=force_download)

    aq10_text_path = EXTRACTED_SOURCE_DIR / "AQ10.txt"
    aq_adult_text_path = EXTRACTED_SOURCE_DIR / "AQ_Scoring_Key.txt"

    aq10_text = _extract_pdf_text(source_paths[AQ10_INSTRUMENT])
    aq10_text_path.write_text(aq10_text, encoding="utf-8")

    aq_adult_text = _extract_doc_text(source_paths[AQ_ADULT_INSTRUMENT])
    aq_adult_text_path.write_text(aq_adult_text, encoding="utf-8")

    aq10_items = parse_aq10_text(aq10_text, expected_count=10)
    aq_adult_items = parse_adult_aq_text(aq_adult_text, expected_count=50)

    write_json(PARSED_SOURCE_DIR / "aq10.json", [item.to_record() for item in aq10_items])
    write_json(PARSED_SOURCE_DIR / "aq_adult.json", [item.to_record() for item in aq_adult_items])

    return {
        AQ10_INSTRUMENT: aq10_items,
        AQ_ADULT_INSTRUMENT: aq_adult_items,
    }


def load_question_banks() -> dict[str, list[QuestionnaireItem]]:
    aq10_records = read_json(PARSED_SOURCE_DIR / "aq10.json")
    aq_adult_records = read_json(PARSED_SOURCE_DIR / "aq_adult.json")
    return {
        AQ10_INSTRUMENT: [QuestionnaireItem(**record) for record in aq10_records],
        AQ_ADULT_INSTRUMENT: [QuestionnaireItem(**record) for record in aq_adult_records],
    }


def _parse_number_list(segment: str) -> set[int]:
    return {int(match) for match in re.findall(r"\d+", segment)}


def _needs_tight_join(buffer: str, line: str) -> bool:
    return buffer.endswith(("I", "can", "don", "isn", "it", "people", "character"))


def _normalize_doc_text(text: str) -> str:
    replacements = {
        "I\nm": "I'm",
        "I\nve": "I've",
        "can\nt": "can't",
        "don\nt": "don't",
        "isn\nt": "isn't",
        "it\ns": "it's",
        "people\ns": "people's",
        "characters\n intentions": "characters' intentions",
        "person\ns": "person's",
    }
    normalized = text.replace("\r", "")
    for old, new in replacements.items():
        normalized = normalized.replace(old, new)
    return normalized


def _cleanup_question_text(text: str) -> str:
    cleaned = normalize_whitespace(text)
    replacements = {
        "Im ": "I'm ",
        "Ive ": "I've ",
        "cant ": "can't ",
        "dont ": "don't ",
        "isnt ": "isn't ",
        "its ": "it's ",
        "peoples ": "people's ",
        "characters intentions": "characters' intentions",
    }
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    return cleaned
