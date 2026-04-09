"""RAG-specific runtime settings."""

from __future__ import annotations

from functools import lru_cache

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class RagSettings(BaseSettings):
    """Settings for local-first RAG workflows."""

    environment: str = "development"
    use_gemini_first: bool = False
    qdrant_prefer_embedded: bool = True
    qdrant_path: str = "data/qdrant_local"
    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_collection: str = "video_segments_v1"
    qdrant_knowledge_collection: str = "video_knowledge_units_v1"
    embedding_model_name: str = "text-embedding-3-large"
    hf_token: str | None = None
    hf_router_url: str = "https://router.huggingface.co/v1/chat/completions"
    hf_analysis_model: str = "openai/gpt-oss-120b"
    hf_answer_model: str = "Qwen/Qwen3-32B"
    hf_answer_model_balanced: str = "Qwen/Qwen3-32B"
    hf_answer_model_cheap: str = "Qwen/Qwen3-4B-Instruct-2507"
    hf_provider: str = "auto"
    hf_timeout_sec: int = 120
    hf_max_segments: int = 24
    answer_backend: str = "auto"
    ollama_base_url: str = "http://localhost:11434"
    ollama_answer_model: str = "qwen3:8b"
    ollama_timeout_sec: int = 180
    openai_api_key: str | None = Field(default=None, validation_alias=AliasChoices("OPENAI_API_KEY", "API_KEY_OPENAI"))
    openai_base_url: str = "https://api.openai.com/v1/chat/completions"
    openai_answer_model: str = "gpt-5-mini"
    openai_timeout_sec: int = 120
    segment_target_min_sec: int = 4
    segment_target_max_sec: int = 15
    segment_hard_max_sec: int = 20

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache(maxsize=1)
def get_rag_settings() -> RagSettings:
    """Return cached RAG settings instance."""
    return RagSettings()
