"""Run story tests with any evaluator."""

from __future__ import annotations

from typing import Iterable, Iterator

from .models import StoryTest, StoryTestResult
from .providers import Evaluator


def run_tests(
    tests: Iterable[StoryTest], story: str, evaluator: Evaluator
) -> Iterator[StoryTestResult]:
    """Yield each result as soon as it is ready, so callers can stream them."""
    for test in tests:
        yield StoryTestResult(test.name, evaluator.evaluate(test.assertion, story))
