"""
Configuration for LLM model.
"""

import os
from typing import Dict
from constants import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS

# Friendly alias -> full Bedrock model ID
BEDROCK_MODELS: Dict[str, str] = {
    "nova-2-lite": "eu.amazon.nova-2-lite-v1:0",
    "nova-2-pro": "eu.amazon.nova-2-pro-v1:0",
}


def get_llm_config() -> Dict:
    """Get LLM config from environment."""
    model_alias = os.environ.get("LLM_MODEL", DEFAULT_LLM_MODEL)
    model_id = BEDROCK_MODELS.get(model_alias, model_alias)

    temperature_str = os.environ.get("LLM_TEMPERATURE", str(DEFAULT_TEMPERATURE))
    temperature = float(temperature_str)

    return {
        "model_id": model_id,
        "temperature": temperature,
        "max_tokens": DEFAULT_MAX_TOKENS,
    }
