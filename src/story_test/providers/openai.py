"""OpenAI provider."""

from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from ..errors import ProviderError
from ..prompts import SYSTEM_PROMPT, build_prompt, parse_verdict


class OpenAIEvaluator:
    def __init__(self, model: str, client: Any | None = None) -> None:
        if client is None:
            if not os.getenv("OPENAI_API_KEY"):
                raise ProviderError(
                    "OPENAI_API_KEY is not set. Export it before using the openai provider."
                )
            client = OpenAI()
        self.model = model
        self.client = client

    def evaluate(self, assertion: str, story: str) -> bool:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_prompt(assertion, story)},
            ],
        )
        return parse_verdict(response.choices[0].message.content)
