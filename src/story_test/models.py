"""Plain data types shared by the CLI, the runner and the providers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StoryTest:
    """One plain-English assertion to check against a story."""

    name: str
    assertion: str


@dataclass(frozen=True)
class StoryTestResult:
    """Whether the story supported a test's assertion."""

    name: str
    passed: bool
