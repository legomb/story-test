"""Local Ollama provider."""

from __future__ import annotations

from typing import Any

import ollama

from ..errors import ProviderError
from ..prompts import SYSTEM_PROMPT, VERDICT_SCHEMA, build_prompt, parse_verdict

DEFAULT_HOST = "http://127.0.0.1:11434"
DEFAULT_CONTEXT_LENGTH = 32768


class OllamaEvaluator:
    def __init__(
        self,
        model: str,
        host: str | None = None,
        context_length: int | None = None,
        client: Any | None = None,
    ) -> None:
        self.model = model
        self.context_length = context_length or DEFAULT_CONTEXT_LENGTH
        self.client = client or ollama.Client(host=host or DEFAULT_HOST)

    def evaluate(self, assertion: str, story: str) -> bool:
        try:
            response = self.client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": build_prompt(assertion, story)},
                ],
                format=VERDICT_SCHEMA,
                options={"num_ctx": self.context_length, "temperature": 0},
            )
        except ollama.ResponseError as error:
            if error.status_code == 404:
                raise ProviderError(
                    f"Ollama model {self.model!r} is not installed. "
                    f"Run `OLLAMA_MODEL={self.model} task environment:ollama:install`."
                ) from error
            raise
        return parse_verdict(response.message.content)
