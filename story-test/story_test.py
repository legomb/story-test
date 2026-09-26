"""Evaluate story assertions with Laya."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import validate
from laya import load

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "schemas/v1/tests.schema.json"


def load_tests(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as file:
        document = yaml.safe_load(file)

    with SCHEMA_PATH.open(encoding="utf-8") as file:
        schema = yaml.safe_load(file)
    validate(document, schema)
    return document["tests"]


def load_story(paths: Iterable[Path]) -> str:
    sections = []
    for path in paths:
        sections.append(path.read_text(encoding="utf-8"))
    return "\n\n".join(sections)


def _answer_is_true(result: Any, question_id: str) -> bool:
    answers = result.get("answers") if isinstance(result, dict) else None
    if not isinstance(answers, dict) or question_id not in answers:
        raise ValueError(f"Laya did not return an answer for {question_id!r}")

    answer = answers[question_id]
    if isinstance(answer, dict) and "noul" in answer:
        answer = answer["noul"]
    if isinstance(answer, bool):
        return answer
    if isinstance(answer, (int, float)):
        return answer >= 0.5
    raise ValueError(f"Unexpected Laya answer for {question_id!r}: {answer!r}")


def run_tests(
    tests_path: Path,
    story_paths: Iterable[Path],
    runner: Any | None = None,
) -> list[dict[str, Any]]:
    tests = load_tests(tests_path)
    story = load_story(story_paths)
    runner = runner or load()
    questions = {
        test["name"]: {
            "type": "noul",
            "instructions": (
                "Decide whether this assertion is true according to the story:\n"
                f"{test['assertion']}"
            ),
            "criteria": {
                "false": "The assertion is false or contradicted by the story.",
                "true": "The assertion is supported by the story.",
            },
        }
        for test in tests
    }
    result = runner.predict(story, questions)
    return [
        {
            "name": test["name"],
            "passed": _answer_is_true(result, test["name"]),
        }
        for test in tests
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Laya assertions against Markdown stories."
    )
    parser.add_argument(
        "tests", type=Path, help="YAML file matching the story tests schema"
    )
    parser.add_argument(
        "stories", type=Path, nargs="+", help="One or more Markdown story files"
    )
    args = parser.parse_args()

    results = run_tests(args.tests, args.stories)
    failed = 0
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"Test [{result['name']}]: {status}")
        failed += not result["passed"]
    return int(failed > 0)


if __name__ == "__main__":
    raise SystemExit(main())
