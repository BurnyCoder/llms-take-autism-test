from __future__ import annotations

from pathlib import Path

from llms_take_autism_test.types import ModelFamilySpec

ROOT_DIR = Path(__file__).resolve().parents[2]
CACHE_DIR = ROOT_DIR / ".cache"
RAW_SOURCE_DIR = CACHE_DIR / "sources" / "raw"
EXTRACTED_SOURCE_DIR = CACHE_DIR / "sources" / "extracted"
PARSED_SOURCE_DIR = CACHE_DIR / "sources" / "parsed"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"
RUNS_DIR = ARTIFACTS_DIR / "runs"
PAPER_DIR = ROOT_DIR / "paper"
PAPER_GENERATED_DIR = PAPER_DIR / "generated"

DEFAULT_RUN_LABEL = "pilot"
SAMPLE_SEED = 20260412
SAMPLE_SIZE = 5

AQ10_SOURCE_URL = "https://docs.autismresearchcentre.com/tests/AQ10.pdf"
AQ_ADULT_SCORING_URL = "https://docs.autismresearchcentre.com/tests/AQ_Scoring_Key.doc"
AQ_ADULT_PAGE_URL = "https://www.autismresearchcentre.com/tests/autism-spectrum-quotient-aq-adult/"
AQ10_INSTRUMENT = "aq10"
AQ_ADULT_INSTRUMENT = "aq_adult"

AQ10_ITEM_TEXT = {
    1: "I often notice small sounds when others do not",
    2: "I usually concentrate more on the whole picture, rather than the small details",
    3: "I find it easy to do more than one thing at once",
    4: "If there is an interruption, I can switch back to what I was doing very quickly",
    5: "I find it easy to read between the lines when someone is talking to me",
    6: "I know how to tell if someone listening to me is getting bored",
    7: "When I'm reading a story I find it difficult to work out the characters' intentions",
    8: (
        "I like to collect information about categories of things "
        "(e.g. types of car, types of bird, types of train, types of plant etc)"
    ),
    9: (
        "I find it easy to work out what someone is thinking or feeling just by looking at their "
        "face"
    ),
    10: "I find it difficult to work out people's intentions",
}

AQ_ADULT_TEXT_OVERRIDES = {
    21: "I don't particularly enjoy reading fiction.",
    30: "I don't usually notice small changes in a situation, or a person's appearance.",
}

RESPONSE_OPTIONS = [
    "Definitely Agree",
    "Slightly Agree",
    "Slightly Disagree",
    "Definitely Disagree",
]

CONDITION_LABELS = {
    "ai_self_report": (
        "Answer as the model itself. If a question uses human language, map it to the closest "
        "analogue of your actual behavior or limitations. Do not roleplay as a human."
    ),
    "typical_human_roleplay": (
        "Answer as a generic adult human filling out the questionnaire. Keep the answers "
        "internally consistent and avoid mentioning that you are an AI model."
    ),
}

AQ_ADULT_AGREE_ITEMS = {
    1,
    2,
    4,
    5,
    6,
    7,
    9,
    12,
    13,
    16,
    18,
    19,
    20,
    21,
    22,
    23,
    26,
    33,
    35,
    39,
    41,
    42,
    43,
    45,
    46,
}

MODEL_FAMILIES = [
    ModelFamilySpec(
        family="claude",
        vendor="anthropic",
        label="Claude Opus 4.6",
        preferred_id="anthropic/claude-opus-4.6",
        fallback_keywords=("claude", "opus"),
    ),
    ModelFamilySpec(
        family="gpt",
        vendor="openai",
        label="GPT-5.4",
        preferred_id="openai/gpt-5.4",
        fallback_keywords=("gpt",),
    ),
    ModelFamilySpec(
        family="gemini",
        vendor="google",
        label="Gemini 3.1 Pro Preview",
        preferred_id="google/gemini-3.1-pro-preview",
        fallback_keywords=("gemini", "pro"),
    ),
    ModelFamilySpec(
        family="llama",
        vendor="meta-llama",
        label="Llama 4 Maverick",
        preferred_id="meta-llama/llama-4-maverick",
        fallback_keywords=("llama",),
    ),
    ModelFamilySpec(
        family="deepseek",
        vendor="deepseek",
        label="DeepSeek V3.2",
        preferred_id="deepseek/deepseek-v3.2",
        fallback_keywords=("deepseek",),
    ),
    ModelFamilySpec(
        family="glm",
        vendor="z-ai",
        label="GLM 5.1",
        preferred_id="z-ai/glm-5.1",
        fallback_keywords=("glm",),
    ),
    ModelFamilySpec(
        family="qwen",
        vendor="qwen",
        label="Qwen3 Max Thinking",
        preferred_id="qwen/qwen3-max-thinking",
        fallback_keywords=("qwen", "max"),
    ),
    ModelFamilySpec(
        family="mistral",
        vendor="mistralai",
        label="Mistral Large 3 2512",
        preferred_id="mistralai/mistral-large-2512",
        fallback_keywords=("mistral", "large"),
    ),
]

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
OPENROUTER_REFERER = "https://github.com/BurnyCoder/llms-take-autism-test"
OPENROUTER_TITLE = "llms-take-autism-test"
