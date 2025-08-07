from openai import OpenAI
from typing import Any, Optional, List, Dict, Union

# Individual model IDs
MODEL_GPT_4O = "gpt-4o"
MODEL_GPT_4_TURBO = "gpt-4-turbo"
MODEL_GPT_35_TURBO = "gpt-3.5-turbo"

# List of available models
AVAILABLE_GPT_MODELS = [
    MODEL_GPT_4O,
    MODEL_GPT_4_TURBO,
    MODEL_GPT_35_TURBO,
]

# Default GPT model
DEFAULT_GPT_MODEL = MODEL_GPT_4O

# Optionally, a mapping for model families
MODEL_FAMILIES_GPT = {
    "gpt-4": [MODEL_GPT_4O, MODEL_GPT_4_TURBO],
    "gpt-3.5": [MODEL_GPT_35_TURBO],
}

def validate_gpt_model(model_name: str) -> bool:
    return model_name in AVAILABLE_GPT_MODELS

def get_best_gpt_model(preferred: Optional[str] = None) -> str:
    if preferred and preferred in AVAILABLE_GPT_MODELS:
        return preferred
    return DEFAULT_GPT_MODEL

def get_openai_models(client : OpenAI) -> list:
    return [m.id for m in client.models.list().data if m.id in AVAILABLE_GPT_MODELS]
