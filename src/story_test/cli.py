"""Command-line interface: argument parsing and terminal output only."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Sequence

from .errors import StoryTestError
from .loading import load_story, load_tests
from .models import StoryTestResult
from .providers import DEFAULT_MODELS, DEFAULT_PROVIDER, create_evaluator
from .runner import run_tests


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="story-test", description="Run AI assertions against Markdown stories."
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
        help=f"AI provider to use (default: {DEFAULT_PROVIDER})",
    )
    parser.add_argument(
        "--model",
        default=os.getenv("STORY_TEST_MODEL"),
        help="Model name for the selected provider",
    )
    parser.add_argument("--ollama-host", default=os.getenv("OLLAMA_HOST"))
    parser.add_argument(
        "--context-length",
        type=int,
        default=os.getenv("STORY_TEST_CONTEXT_LENGTH"),
        help="Ollama context window in tokens",
    )
    return parser


def color_enabled() -> bool:
    if os.getenv("NO_COLOR"):
        return False
    return bool(os.getenv("FORCE_COLOR")) or sys.stdout.isatty()


def format_result(result: StoryTestResult, color: bool) -> str:
    status = "PASS" if result.passed else "FAIL"
    if color:
        status = f"\033[{'32' if result.passed else '31'}m{status}\033[0m"
    return f"Test [{result.name}]: {status}"


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    color = color_enabled()
    try:
        tests = load_tests(args.tests)
        story = load_story(args.stories)
        evaluator = create_evaluator(
            args.provider,
            args.model,
            ollama_host=args.ollama_host,
            context_length=args.context_length,
        )
        all_passed = True
        for result in run_tests(tests, story, evaluator):
            print(format_result(result, color), flush=True)
            all_passed = all_passed and result.passed
    except StoryTestError as error:
        print(f"story-test: error: {error}", file=sys.stderr)
        return 2
    return 1 if args.fail_on_test_failure and not all_passed else 0


if __name__ == "__main__":
    raise SystemExit(main())
