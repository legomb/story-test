from pathlib import Path
from unittest.mock import Mock

from story_test import OllamaRunner, exit_code, run_tests

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "examples/the-tell-tale-heart/the-tell-tale-heart.tests.yml"
STORY = ROOT / "examples/the-tell-tale-heart/the-tell-tale-heart.md"


def test_tell_tale_heart_example() -> None:
    runner = Mock()
    runner.predict.side_effect = [
        {"answers": {"author": {"choice": "true"}}},
        {"answers": {"narrator-reliability": {"choice": "true"}}},
        {"answers": {"victim": {"choice": "true"}}},
        {"answers": {"motive": {"choice": "false"}}},
        {"answers": {"confession": {"choice": "true"}}},
        {"answers": {"location": {"choice": "false"}}},
    ]

    results = run_tests(TESTS, [STORY], runner=runner)

    assert results == [
        {"name": "author", "passed": True},
        {"name": "narrator-reliability", "passed": True},
        {"name": "victim", "passed": True},
        {"name": "motive", "passed": False},
        {"name": "confession", "passed": True},
        {"name": "location", "passed": False},
    ]
    assert runner.predict.call_count == 6
    state, questions = runner.predict.call_args_list[0].args
    assert "The Tell-Tale Heart" in state
    assert state.startswith("Assertion: The story was written by Edgar Allan Poe.")
    assert questions["author"]["type"] == "boolean"


def test_failures_do_not_affect_exit_code_by_default() -> None:
    results = [{"name": "location", "passed": False}]

    assert exit_code(results, fail_on_test_failure=False) == 0
    assert exit_code(results, fail_on_test_failure=True) == 1


def test_ollama_runner_reads_structured_boolean() -> None:
    class Message:
        content = '{"supported": true}'

    class Response:
        message = Message()

    class Client:
        def chat(self, **kwargs):
            assert kwargs["model"] == "qwen3:8b"
            assert kwargs["options"]["num_ctx"] == 32768
            return Response()

    runner = OllamaRunner("qwen3:8b", "http://localhost:11434", 32768)
    runner.client = Client()

    result = runner.predict("Story text", {"author": {"type": "boolean"}})

    assert result == {"answers": {"author": {"supported": True}}}
