"""Anthropic (Claude) provider."""

from __future__ import annotations

import os
from typing import Any

from anthropic import Anthropic

from ..errors import ProviderError
from ..prompts import SYSTEM_PROMPT, VERDICT_SCHEMA, build_prompt, parse_verdict

# Thinking tokens count toward max_tokens, and newer models always think
# before answering, so leave room beyond the tiny JSON answer.
MAX_TOKENS = 16000


class AnthropicEvaluator:
    def __init__(self, model: str, client: Any | None = None) -> None:
        if client is None:
            if not (
                os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")
            ):
                raise ProviderError(
                    "Set ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN before using the anthropic provider."
                )
            client = Anthropic()
        self.model = model
        self.client = client

    def evaluate(self, assertion: str, story: str) -> bool:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": build_prompt(assertion, story)}],
            output_config={"format": {"type": "json_schema", "schema": VERDICT_SCHEMA}},
        )
        if response.stop_reason in ("max_tokens", "refusal"):
            raise ProviderError(
                f"Anthropic stopped with {response.stop_reason!r} before answering"
            )
        text = next(
            (block.text for block in response.content if block.type == "text"), None
        )
        if text is None:
            raise ProviderError("Anthropic returned no text content block")
        return parse_verdict(text)
