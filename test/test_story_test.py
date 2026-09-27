from pathlib import Path
from unittest.mock import Mock

from story_test import OllamaRunner, exit_code, run_tests
from story_test.cli import _anthropic_json

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "test/the-tell-tale-heart.tests.yml"
STORY = ROOT / "test/the-tell-tale-heart.md"


def test_tell_tale_heart_example() -> None:
    runner = Mock()
    completed = []
    runner.predict.side_effect = [
        {"answers": {"author": {"choice": "true"}}},
        {"answers": {"narrator-reliability": {"choice": "true"}}},
        {"answers": {"victim": {"choice": "true"}}},
        {"answers": {"motive": {"choice": "false"}}},
        {"answers": {"confession": {"choice": "true"}}},
        {"answers": {"location": {"choice": "false"}}},
    ]

    results = run_tests(TESTS, [STORY], runner=runner, on_result=completed.append)

    assert results == [
        {"name": "author", "passed": True},
        {"name": "narrator-reliability", "passed": True},
        {"name": "victim", "passed": True},
        {"name": "motive", "passed": False},
        {"name": "confession", "passed": True},
        {"name": "location", "passed": False},
    ]
    assert runner.predict.call_count == 6
    assert completed == results
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

    runner = OllamaRunner("qwen3:8b", "http://localhost:11434", 32768, client=Client())

    result = runner.predict("Story text", {"author": {"type": "boolean"}})

    assert result == {"answers": {"author": {"supported": True}}}


def test_anthropic_json_skips_thinking_blocks() -> None:
    class ThinkingBlock:
        type = "thinking"

    class TextBlock:
        type = "text"
        text = '```json\n{"supported": true}\n```'

    assert _anthropic_json([ThinkingBlock(), TextBlock()]) == {"supported": True}
