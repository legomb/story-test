"""Provider registry.

Provider modules are imported only when selected, so the CLI starts fast and
one provider's SDK never has to be importable to use another.
"""

from __future__ import annotations

from .base import Evaluator

DEFAULT_PROVIDER = "ollama"
DEFAULT_MODELS = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-opus-5-5",
    "ollama": "qwen3:8b",
}


def create_evaluator(
    provider: str,
    model: str | None = None,
    *,
    ollama_host: str | None = None,
    context_length: int | None = None,
) -> Evaluator:
    if provider not in DEFAULT_MODELS:
        raise ValueError(f"Unsupported provider: {provider}")
    model = model or DEFAULT_MODELS[provider]
    if provider == "openai":
        from .openai import OpenAIEvaluator

        return OpenAIEvaluator(model)
    if provider == "anthropic":
        from .anthropic import AnthropicEvaluator

        return AnthropicEvaluator(model)
    from .ollama import OllamaEvaluator

    return OllamaEvaluator(model, host=ollama_host, context_length=context_length)


__all__ = ["DEFAULT_MODELS", "DEFAULT_PROVIDER", "Evaluator", "create_evaluator"]
