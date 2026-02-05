"""
Configuration for LLM backends and models.
Supports Bedrock (production) and LM Studio (local dev).
"""

import os
from functools import lru_cache
from typing import Literal, Optional, Dict, Set
from pydantic import BaseModel, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from constants import DEFAULT_LLM_MODEL, DEFAULT_TEMPERATURE, DEFAULT_MAX_TOKENS, DEFAULT_AWS_REGION
from utils.logging import get_logger

logger = get_logger(__name__)

LLMBackend = Literal["bedrock", "lm_studio"]
EmbeddingBackend = Literal["bedrock"]

# Which regions each model is available in (for validation warnings)
MODEL_REGION_MAP: Dict[str, Set[str]] = {
    "eu.meta.llama3-2-1b-instruct-v1:0": {"eu-west-1", "eu-west-3", "eu-central-1"},
    "eu.meta.llama3-2-3b-instruct-v1:0": {"eu-west-1", "eu-west-3", "eu-central-1"},
    "us.meta.llama3-2-8b-instruct-v1:0": {"us-east-1", "us-west-2"},
    "mistral.mixtral-8x7b-instruct-v0:1": {"us-east-1", "us-west-2", "eu-west-1", "eu-west-3", "ap-northeast-1"},
    "mistral.mistral-7b-instruct-v0:2": {"us-east-1", "us-west-2", "eu-west-1", "eu-west-3"},
    "amazon.titan-text-lite-v1": {"us-east-1", "us-west-2", "eu-west-1", "eu-west-3", "ap-northeast-1"},
    "amazon.titan-text-express-v1": {"us-east-1", "us-west-2", "eu-west-1", "eu-west-3", "ap-northeast-1"},
}

# Friendly alias -> full Bedrock model ID
BEDROCK_MODELS: Dict[str, str] = {
    # Nova 2
    "nova-2-lite": "eu.amazon.nova-2-lite-v1:0",
    "nova-2-pro": "eu.amazon.nova-2-pro-v1:0",
    # Llama
    "llama-3.2-1b": "eu.meta.llama3-2-1b-instruct-v1:0",
    "llama-3.2-3b": "eu.meta.llama3-2-3b-instruct-v1:0",
    "llama-3.2-8b": "us.meta.llama3-2-8b-instruct-v1:0",
    "llama-3.1-8b": "meta.llama3-1-8b-instruct-v1:0",
    "llama-3.1-70b": "meta.llama3-1-70b-instruct-v1:0",
    # Claude
    "claude-3-haiku": "anthropic.claude-3-haiku-20240307-v1:0",
    "claude-3-sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
    "claude-3.5-sonnet": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    # Mistral
    "mistral-7b": "mistral.mistral-7b-instruct-v0:2",
    "mixtral-8x7b": "mistral.mixtral-8x7b-instruct-v0:1",
    # Titan
    "titan-text-lite": "amazon.titan-text-lite-v1",
    "titan-text-express": "amazon.titan-text-express-v1",
}

BEDROCK_EMBEDDING_MODELS: Dict[str, str] = {
    "titan-embed-text-v1": "amazon.titan-embed-text-v1",
    "titan-embed-text-v2": "amazon.titan-embed-text-v2:0",
    "cohere-embed-english": "cohere.embed-english-v3",
    "cohere-embed-multilingual": "cohere.embed-multilingual-v3",
}


class ModelConfig(BaseModel):
    """LLM model configuration."""
    backend: LLMBackend
    model_id: str
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: Optional[int] = DEFAULT_MAX_TOKENS
    aws_region: str = DEFAULT_AWS_REGION
    lm_studio_base_url: str = "http://localhost:1234/v1"

    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"Temperature must be between 0.0 and 1.0, got {v}")
        return v

    @model_validator(mode='after')
    def validate_model_region(self) -> 'ModelConfig':
        """Warn if model may not be available in selected region."""
        if self.backend == "bedrock" and self.model_id in MODEL_REGION_MAP:
            available_regions = MODEL_REGION_MAP[self.model_id]
            if self.aws_region not in available_regions:
                logger.warning(
                    "Model %s may not be available in region %s. Available: %s",
                    self.model_id, self.aws_region, ", ".join(sorted(available_regions))
                )
        return self


class EmbeddingConfig(BaseModel):
    """Embedding model configuration."""
    backend: EmbeddingBackend
    model_id: str
    aws_region: str = DEFAULT_AWS_REGION


class Settings(BaseSettings):
    """Settings loaded from environment variables."""
    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore"
    )

    llm_backend: LLMBackend = "bedrock"
    llm_model: str = DEFAULT_LLM_MODEL
    llm_temperature: float = DEFAULT_TEMPERATURE

    aws_default_region: str = DEFAULT_AWS_REGION
    aws_region: Optional[str] = None

    lm_studio_base_url: str = "http://localhost:1234/v1"

    embedding_backend: EmbeddingBackend = "bedrock"
    embedding_model: str = "titan-embed-text-v2"

    @property
    def effective_region(self) -> str:
        return self.aws_default_region or self.aws_region or DEFAULT_AWS_REGION


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get or create settings instance (cached)."""
    return Settings()


def _resolve_model_id(alias: str, model_map: Dict[str, str], is_bedrock: bool) -> str:
    """Convert friendly alias to full model ID."""
    if is_bedrock:
        return model_map.get(alias, alias)
    return alias


def get_model_config() -> ModelConfig:
    """Get LLM config from environment."""
    settings = get_settings()
    model_id = _resolve_model_id(
        settings.llm_model,
        BEDROCK_MODELS,
        settings.llm_backend == "bedrock"
    )

    return ModelConfig(
        backend=settings.llm_backend,
        model_id=model_id,
        temperature=settings.llm_temperature,
        aws_region=settings.effective_region,
        lm_studio_base_url=settings.lm_studio_base_url
    )


def get_embedding_config() -> Dict[str, str]:
    """Get embedding config from environment."""
    settings = get_settings()
    model_id = _resolve_model_id(
        settings.embedding_model,
        BEDROCK_EMBEDDING_MODELS,
        settings.embedding_backend == "bedrock"
    )

    return {
        "backend": settings.embedding_backend,
        "model_id": model_id,
        "aws_region": settings.effective_region
    }


def list_available_models(backend: LLMBackend = "bedrock") -> Dict[str, str]:
    """List available models for a backend."""
    if backend == "bedrock":
        return BEDROCK_MODELS.copy()
    elif backend == "lm_studio":
        return {"local-model": "Check LM Studio UI"}
    return {}


def reset_settings() -> None:
    """Reset settings cache (for testing)."""
    get_settings.cache_clear()
