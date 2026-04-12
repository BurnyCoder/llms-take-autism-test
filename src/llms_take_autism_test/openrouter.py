from __future__ import annotations

import os
from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from llms_take_autism_test.config import (
    MODEL_FAMILIES,
    OPENROUTER_BASE_URL,
    OPENROUTER_REFERER,
    OPENROUTER_TITLE,
)
from llms_take_autism_test.types import ModelFamilySpec, ResolvedModel

SKIP_MODEL_TOKENS = ("image", "audio", "guard", "coder", "vision", "lyria", ":free")


def require_api_key() -> str:
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is not set")
    return api_key


def fetch_model_catalog() -> list[dict[str, Any]]:
    response = httpx.get(f"{OPENROUTER_BASE_URL}/models", timeout=60.0)
    response.raise_for_status()
    payload = response.json()
    return payload["data"]


def resolve_models(catalog: list[dict[str, Any]]) -> list[ResolvedModel]:
    resolved = []
    by_id = {entry["id"]: entry for entry in catalog}
    for spec in MODEL_FAMILIES:
        exact = by_id.get(spec.preferred_id)
        if exact is not None:
            resolved.append(_resolved_model(spec, exact))
            continue
        fallback = _resolve_fallback(spec, catalog)
        if fallback is None:
            raise RuntimeError(f"Could not resolve any model for family {spec.family}")
        resolved.append(_resolved_model(spec, fallback))
    return resolved


def _resolve_fallback(
    spec: ModelFamilySpec, catalog: list[dict[str, Any]]
) -> dict[str, Any] | None:
    candidates = []
    for entry in catalog:
        model_id = entry["id"].lower()
        if not model_id.startswith(f"{spec.vendor}/"):
            continue
        if any(token in model_id for token in SKIP_MODEL_TOKENS):
            continue
        if not all(keyword in model_id for keyword in spec.fallback_keywords):
            continue
        candidates.append(entry)

    if not candidates:
        for entry in catalog:
            model_id = entry["id"].lower()
            if model_id.startswith(f"{spec.vendor}/") and not any(
                token in model_id for token in SKIP_MODEL_TOKENS
            ):
                candidates.append(entry)

    if not candidates:
        return None

    return sorted(candidates, key=lambda entry: entry.get("created", 0), reverse=True)[0]


def _resolved_model(spec: ModelFamilySpec, entry: dict[str, Any]) -> ResolvedModel:
    return ResolvedModel(
        family=spec.family,
        vendor=spec.vendor,
        label=spec.label,
        preferred_id=spec.preferred_id,
        resolved_id=entry["id"],
        resolved_name=entry.get("name", entry["id"]),
        context_length=entry.get("context_length"),
    )


@retry(
    reraise=True,
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    retry=retry_if_exception_type(httpx.HTTPError),
)
def chat_completion(api_key: str, model_id: str, messages: list[dict[str, str]]) -> str:
    response = httpx.post(
        f"{OPENROUTER_BASE_URL}/chat/completions",
        timeout=120.0,
        headers={
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": OPENROUTER_REFERER,
            "X-Title": OPENROUTER_TITLE,
        },
        json={
            "model": model_id,
            "messages": messages,
            "temperature": 0,
            "max_tokens": 500,
        },
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"].get("content")
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            chunk.get("text", "")
            for chunk in content
            if isinstance(chunk, dict) and chunk.get("type") == "text"
        )
    raise TypeError(f"Unsupported content payload: {type(content)!r}")
