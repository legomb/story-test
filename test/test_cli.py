from pathlib import Path

import pytest

from story_test import StoryTestResult, cli

HERE = Path(__file__).resolve().parent
ARGS = [str(HERE / "the-tell-tale-heart.tests.yml"), str(HERE / "the-tell-tale-heart.md")]


class AlwaysFails:
    def evaluate(self, assertion: str, story: str) -> bool:
        return False


@pytest.fixture
def failing_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "create_evaluator", lambda *args, **kwargs: AlwaysFails())
    monkeypatch.setenv("NO_COLOR", "1")


@pytest.mark.usefixtures("failing_provider")
def test_failures_do_not_affect_exit_code_by_default(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(ARGS) == 0
    assert "Test [author]: FAIL" in capsys.readouterr().out


@pytest.mark.usefixtures("failing_provider")
def test_strict_mode_fails_on_failed_tests() -> None:
    assert cli.main([*ARGS, "--fail-on-test-failure"]) == 1


def test_expected_errors_are_reported_without_traceback(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    assert cli.main([*ARGS, "--provider", "openai"]) == 2
    assert "story-test: error: OPENAI_API_KEY is not set" in capsys.readouterr().err


def test_colorizes_test_statuses() -> None:
    assert cli.format_result(StoryTestResult("a", True), True) == "Test [a]: \033[32mPASS\033[0m"
    assert cli.format_result(StoryTestResult("a", False), True) == "Test [a]: \033[31mFAIL\033[0m"
    assert cli.format_result(StoryTestResult("a", True), False) == "Test [a]: PASS"
