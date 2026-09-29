from pathlib import Path

import pytest

from story_test import (
    StoryTest,
    StoryTestError,
    StoryTestResult,
    load_story,
    load_tests,
    parse_tests,
    run_tests,
)

HERE = Path(__file__).resolve().parent
TESTS = HERE / "the-tell-tale-heart.tests.yml"
STORY = HERE / "the-tell-tale-heart.md"


class FakeEvaluator:
    def __init__(self, verdicts: dict[str, bool]) -> None:
        self.verdicts = verdicts
        self.calls: list[tuple[str, str]] = []

    def evaluate(self, assertion: str, story: str) -> bool:
        self.calls.append((assertion, story))
        return self.verdicts[assertion]


def test_tell_tale_heart_example() -> None:
    tests = load_tests(TESTS)
    story = load_story([STORY])
    verdicts = {test.assertion: test.name not in ("motive", "location") for test in tests}
    evaluator = FakeEvaluator(verdicts)

    results = list(run_tests(tests, story, evaluator))

    assert results == [
        StoryTestResult("author", True),
        StoryTestResult("narrator-reliability", True),
        StoryTestResult("victim", True),
        StoryTestResult("motive", False),
        StoryTestResult("confession", True),
        StoryTestResult("location", False),
    ]
    assertion, passed_story = evaluator.calls[0]
    assert assertion == "The story was written by Edgar Allan Poe."
    assert "The Tell-Tale Heart" in passed_story


def test_run_tests_streams_results_lazily() -> None:
    evaluator = FakeEvaluator({"a": True, "b": False})
    results = run_tests([StoryTest("one", "a"), StoryTest("two", "b")], "story", evaluator)

    assert next(results) == StoryTestResult("one", True)
    assert len(evaluator.calls) == 1


def test_load_story_joins_files(tmp_path: Path) -> None:
    first, second = tmp_path / "1.md", tmp_path / "2.md"
    first.write_text("One", encoding="utf-8")
    second.write_text("Two", encoding="utf-8")

    assert load_story([first, second]) == "One\n\nTwo"


def test_parse_tests_rejects_invalid_documents() -> None:
    with pytest.raises(StoryTestError, match="Invalid tests document"):
        parse_tests({"tests": [{"name": "missing-assertion"}]})
