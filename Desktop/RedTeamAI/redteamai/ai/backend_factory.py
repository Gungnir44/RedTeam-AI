"""Instantiate AI backend from application settings."""
from __future__ import annotations
from redteamai.ai.base import AIBackend
from redteamai.config.settings import AppSettings


def create_backend(settings: AppSettings) -> AIBackend:
    backend = settings.ai_backend

    if backend == "ollama":
        from redteamai.ai.ollama_backend import OllamaBackend
        return OllamaBackend(
            host=settings.ollama.host,
            model=settings.ollama.model,
            timeout=settings.ollama.timeout,
            use_xml_fallback=settings.ollama.use_xml_fallback,
        )
    elif backend == "groq":
        from redteamai.ai.groq_backend import GroqBackend
        return GroqBackend(
            api_key=settings.groq.api_key,
            model=settings.groq.model,
            timeout=settings.groq.timeout,
        )
    elif backend == "anthropic":
        from redteamai.ai.anthropic_backend import AnthropicBackend
        return AnthropicBackend(
            api_key=settings.anthropic.api_key,
            model=settings.anthropic.model,
            timeout=settings.anthropic.timeout,
            max_tokens=settings.anthropic.max_tokens,
        )
    elif backend == "openai_compat":
        from redteamai.ai.openai_compat_backend import OpenAICompatBackend
        return OpenAICompatBackend(
            api_key=settings.openai_compat.api_key,
            base_url=settings.openai_compat.base_url,
            model=settings.openai_compat.model,
            timeout=settings.openai_compat.timeout,
        )
    else:
        raise ValueError(f"Unknown AI backend: {backend!r}")
