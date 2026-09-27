"""Evaluate story assertions with a local Ollama model."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Iterable

from ollama import Client, ResponseError
import yaml
from jsonschema import validate

SOURCE_SCHEMA_PATH = (
    Path(__file__).resolve().parent.parent / "schemas/v1/tests.schema.json"
)
INSTALLED_SCHEMA_PATH = (
    Path(sys.prefix) / "share/story-test/schemas/v1/tests.schema.json"
)
DEFAULT_MODEL = "qwen3:8b"
DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_CONTEXT_LENGTH = 32768


class OllamaRunner:
    def __init__(self, model: str, host: str, context_length: int) -> None:
        self.model = model
        self.context_length = context_length
        self.client = Client(host=host)

    def predict(
        self, state: str, questions: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        answers = {}
        for question_id in questions:
            try:
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Evaluate the assertion against the story. "
                                "Return true only when the story supports it."
                            ),
                        },
                        {"role": "user", "content": state},
                    ],
                    format={
                        "type": "object",
                        "properties": {"supported": {"type": "boolean"}},
                        "required": ["supported"],
                    },
                    options={"num_ctx": self.context_length, "temperature": 0},
                )
            except ResponseError as error:
                if error.status_code == 404:
                    raise RuntimeError(
                        f"Ollama model {self.model!r} is not installed. "
                        f"Run `OLLAMA_MODEL={self.model} task environment:ollama:install`."
                    ) from error
                raise
            content = response.message.content
            parsed = json.loads(content)
            answers[question_id] = {"supported": parsed["supported"]}
        return {"answers": answers}


def load_tests(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as file:
        document = yaml.safe_load(file)

    schema_path = (
        SOURCE_SCHEMA_PATH if SOURCE_SCHEMA_PATH.exists() else INSTALLED_SCHEMA_PATH
    )
    with schema_path.open(encoding="utf-8") as file:
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
        raise ValueError(f"Ollama did not return an answer for {question_id!r}")

    answer = answers[question_id]
    if isinstance(answer, dict) and "supported" in answer:
        return answer["supported"] is True
    if isinstance(answer, dict) and "choice" in answer:
        return answer["choice"] == "true"
    if isinstance(answer, dict) and "noul" in answer:
        answer = answer["noul"]
    if isinstance(answer, bool):
        return answer
    if isinstance(answer, (int, float)):
        return answer >= 0.5
    raise ValueError(f"Unexpected Ollama answer for {question_id!r}: {answer!r}")


def run_tests(
    tests_path: Path,
    story_paths: Iterable[Path],
    runner: Any | None = None,
    model: str = DEFAULT_MODEL,
    ollama_host: str = DEFAULT_OLLAMA_HOST,
    context_length: int = DEFAULT_CONTEXT_LENGTH,
) -> list[dict[str, Any]]:
    tests = load_tests(tests_path)
    story = load_story(story_paths)
    runner = runner or OllamaRunner(model, ollama_host, context_length)
    results = []
    for test in tests:
        questions = {
            test["name"]: {
                "type": "boolean",
            }
        }
        state = f"Assertion: {test['assertion']}\n\nStory:\n{story}"
        result = runner.predict(state, questions)
        results.append(
            {
                "name": test["name"],
                "passed": _answer_is_true(result, test["name"]),
            }
        )
    return results


def exit_code(results: list[dict[str, Any]], fail_on_test_failure: bool) -> int:
    if fail_on_test_failure and any(not result["passed"] for result in results):
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Ollama assertions against Markdown stories."
    )
    parser.add_argument(
        "tests", type=Path, help="YAML file matching the story tests schema"
    )
    parser.add_argument(
        "stories", type=Path, nargs="+", help="One or more Markdown story files"
    )
    parser.add_argument(
        "--fail-on-test-failure",
        action="store_true",
        help="Exit with status 1 when any story test fails",
    )
    parser.add_argument("--model", default=os.getenv("STORY_TEST_MODEL", DEFAULT_MODEL))
    parser.add_argument(
        "--ollama-host",
        default=os.getenv("OLLAMA_HOST", DEFAULT_OLLAMA_HOST),
    )
    parser.add_argument(
        "--context-length",
        type=int,
        default=int(os.getenv("STORY_TEST_CONTEXT_LENGTH", DEFAULT_CONTEXT_LENGTH)),
    )
    args = parser.parse_args()

    results = run_tests(
        args.tests,
        args.stories,
        model=args.model,
        ollama_host=args.ollama_host,
        context_length=args.context_length,
    )
    for result in results:
        status = "PASS" if result["passed"] else "FAIL"
        print(f"Test [{result['name']}]: {status}")
    return exit_code(results, args.fail_on_test_failure)


if __name__ == "__main__":
    raise SystemExit(main())
