"""The interface every AI provider implements."""

from __future__ import annotations

from typing import Protocol


class Evaluator(Protocol):
    def evaluate(self, assertion: str, story: str) -> bool:
        """Return whether the story supports the assertion."""
        ...
