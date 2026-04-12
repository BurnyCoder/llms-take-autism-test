from llms_take_autism_test.openrouter import resolve_models


def test_resolve_models_prefers_exact_matches() -> None:
    catalog = [
        {
            "id": "anthropic/claude-opus-4.6",
            "name": "Claude Opus 4.6",
            "created": 2,
            "context_length": 1000,
        },
        {
            "id": "openai/gpt-5.4",
            "name": "GPT-5.4",
            "created": 2,
            "context_length": 1000,
        },
        {
            "id": "google/gemini-3.1-pro-preview",
            "name": "Gemini 3.1 Pro Preview",
            "created": 2,
            "context_length": 1000,
        },
        {
            "id": "meta-llama/llama-4-maverick",
            "name": "Llama 4 Maverick",
            "created": 2,
            "context_length": 1000,
        },
        {
            "id": "deepseek/deepseek-v3.2",
            "name": "DeepSeek V3.2",
            "created": 2,
            "context_length": 1000,
        },
        {
            "id": "z-ai/glm-5.1",
            "name": "GLM 5.1",
            "created": 2,
            "context_length": 1000,
        },
        {
            "id": "qwen/qwen3-max-thinking",
            "name": "Qwen3 Max Thinking",
            "created": 2,
            "context_length": 1000,
        },
        {
            "id": "mistralai/mistral-large-2512",
            "name": "Mistral Large 3 2512",
            "created": 2,
            "context_length": 1000,
        },
    ]

    resolved = resolve_models(catalog)

    assert len(resolved) == 8
    assert resolved[0].resolved_id == "anthropic/claude-opus-4.6"
    assert resolved[-1].resolved_id == "mistralai/mistral-large-2512"
