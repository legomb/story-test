"""Evaluate story assertions with a local Ollama model."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any, Callable, Iterable

from anthropic import Anthropic
from openai import OpenAI
import yaml
from jsonschema import validate

SOURCE_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "schemas/v1/tests.schema.json"
)
INSTALLED_SCHEMA_PATH = (
    Path(sys.prefix) / "share/story-test/schemas/v1/tests.schema.json"
)
DEFAULT_PROVIDER = "ollama"
DEFAULT_MODELS = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-3-5-haiku-latest",
    "ollama": "qwen3:8b",
}
DEFAULT_OLLAMA_HOST = "http://127.0.0.1:11434"
DEFAULT_CONTEXT_LENGTH = 32768
SYSTEM_PROMPT = (
    "Evaluate the assertion against the story. Return only JSON in the form "
    '{"supported": true} or {"supported": false}.'
)


def _anthropic_json(content: list[Any]) -> dict[str, Any]:
    text = next(
        (
            block.text
            for block in content
            if getattr(block, "type", None) == "text" and getattr(block, "text", None)
        ),
        None,
    )
    if text is None:
        raise ValueError("Anthropic returned no text content block")
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    return json.loads(text)


class OpenAIRunner:
    def __init__(self, model: str) -> None:
        self.model = model
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Export it before using the openai provider."
            )
        self.client = OpenAI()

    def predict(
        self, state: str, questions: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        answers = {}
        for question_id in questions:
            response = self.client.chat.completions.create(
                model=self.model,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": state},
                ],
            )
            answers[question_id] = {
                "supported": json.loads(response.choices[0].message.content)[
                    "supported"
                ]
            }
        return {"answers": answers}


class AnthropicRunner:
    def __init__(self, model: str) -> None:
        self.model = model
        if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")):
            raise RuntimeError(
                "Set ANTHROPIC_API_KEY or ANTHROPIC_AUTH_TOKEN before using the anthropic provider."
            )
        self.client = Anthropic()

    def predict(
        self, state: str, questions: dict[str, dict[str, Any]]
    ) -> dict[str, Any]:
        answers = {}
        for question_id in questions:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=64,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": state}],
            )
            answers[question_id] = {
                "supported": _anthropic_json(response.content)["supported"]
            }
        return {"answers": answers}


class OllamaRunner:
    def __init__(
        self, model: str, host: str, context_length: int, client: Any | None = None
    ) -> None:
        self.model = model
        self.context_length = context_length
        if client is None:
            import ollama

            self.client = ollama.Client(host=host)
            self.response_error = ollama.ResponseError
        else:
            self.client = client
            self.response_error = Exception

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
                            "content": SYSTEM_PROMPT,
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
            except self.response_error as error:
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
        raise ValueError(f"AI provider did not return an answer for {question_id!r}")

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
    raise ValueError(f"Unexpected AI answer for {question_id!r}: {answer!r}")


def create_runner(
    provider: str, model: str, ollama_host: str, context_length: int
) -> Any:
    if provider == "openai":
        return OpenAIRunner(model)
    if provider == "anthropic":
        return AnthropicRunner(model)
    if provider == "ollama":
        return OllamaRunner(model, ollama_host, context_length)
    raise ValueError(f"Unsupported provider: {provider}")


def run_tests(
    tests_path: Path,
    story_paths: Iterable[Path],
    runner: Any | None = None,
    provider: str = DEFAULT_PROVIDER,
    model: str | None = None,
    ollama_host: str = DEFAULT_OLLAMA_HOST,
    context_length: int = DEFAULT_CONTEXT_LENGTH,
    on_result: Callable[[dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    tests = load_tests(tests_path)
    story = load_story(story_paths)
    model = model or DEFAULT_MODELS[provider]
    runner = runner or create_runner(provider, model, ollama_host, context_length)
    results = []
    for test in tests:
        questions = {
            test["name"]: {
                "type": "boolean",
            }
        }
        state = f"Assertion: {test['assertion']}\n\nStory:\n{story}"
        result = runner.predict(state, questions)
        test_result = {
            "name": test["name"],
            "passed": _answer_is_true(result, test["name"]),
        }
        results.append(test_result)
        if on_result is not None:
            on_result(test_result)
    return results


def exit_code(results: list[dict[str, Any]], fail_on_test_failure: bool) -> int:
    if fail_on_test_failure and any(not result["passed"] for result in results):
        return 1
    return 0


def _colorize_status(status: str, enabled: bool) -> str:
    if not enabled:
        return status
    color = "32" if status == "PASS" else "31"
    return f"\033[{color}m{status}\033[0m"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run AI assertions against Markdown stories."
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
    parser.add_argument(
        "--provider",
        choices=DEFAULT_MODELS,
        default=os.getenv("STORY_TEST_PROVIDER", DEFAULT_PROVIDER),
        help="AI provider to use (default: ollama)",
    )
    parser.add_argument("--model", help="Model name for the selected provider")
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
    color_enabled = bool(os.getenv("FORCE_COLOR")) and not os.getenv("NO_COLOR")
    color_enabled = (sys.stdout.isatty() or color_enabled) and not os.getenv("NO_COLOR")

    def print_result(result: dict[str, Any]) -> None:
        status = "PASS" if result["passed"] else "FAIL"
        print(
            f"Test [{result['name']}]: {_colorize_status(status, color_enabled)}",
            flush=True,
        )

    results = run_tests(
        args.tests,
        args.stories,
        provider=args.provider,
        model=args.model or os.getenv("STORY_TEST_MODEL"),
        ollama_host=args.ollama_host,
        context_length=args.context_length,
        on_result=print_result,
    )
    return exit_code(results, args.fail_on_test_failure)


if __name__ == "__main__":
    raise SystemExit(main())
