"""Read and validate test files and stories."""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import ValidationError, validate

from .errors import StoryTestError
from .models import StoryTest

SOURCE_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "schemas/v1/tests.schema.json"
)
INSTALLED_SCHEMA_PATH = (
    Path(sys.prefix) / "share/story-test/schemas/v1/tests.schema.json"
)


@cache
def _schema() -> dict[str, Any]:
    schema_path = (
        SOURCE_SCHEMA_PATH if SOURCE_SCHEMA_PATH.exists() else INSTALLED_SCHEMA_PATH
    )
    with schema_path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def parse_tests(document: Any) -> list[StoryTest]:
    """Validate a parsed tests document (from YAML, JSON, a request body...)."""
    try:
        validate(document, _schema())
    except ValidationError as error:
        raise StoryTestError(f"Invalid tests document: {error.message}") from error
    return [StoryTest(test["name"], test["assertion"]) for test in document["tests"]]


def load_tests(path: Path) -> list[StoryTest]:
    with path.open(encoding="utf-8") as file:
        return parse_tests(yaml.safe_load(file))


def load_story(paths: Iterable[Path]) -> str:
    return "\n\n".join(path.read_text(encoding="utf-8") for path in paths)
