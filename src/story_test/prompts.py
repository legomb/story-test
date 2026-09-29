"""Prompt and answer format shared by every LLM provider."""

from __future__ import annotations

import json
from typing import Any

from .errors import ProviderError

SYSTEM_PROMPT = (
    "Evaluate the assertion against the story. Return only JSON in the form "
    '{"supported": true} or {"supported": false}.'
)

VERDICT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"supported": {"type": "boolean"}},
    "required": ["supported"],
    "additionalProperties": False,
}


def build_prompt(assertion: str, story: str) -> str:
    return f"Assertion: {assertion}\n\nStory:\n{story}"


def parse_verdict(text: str) -> bool:
    """Read the `supported` flag from a model's JSON answer."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        supported = json.loads(text)["supported"]
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise ProviderError(f"Unexpected answer from the model: {text!r}") from error
    if not isinstance(supported, bool):
        raise ProviderError(f"Unexpected answer from the model: {text!r}")
    return supported
