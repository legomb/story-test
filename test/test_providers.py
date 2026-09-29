from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from story_test import ProviderError
from story_test.prompts import parse_verdict
from story_test.providers.anthropic import AnthropicEvaluator
from story_test.providers.ollama import OllamaEvaluator
from story_test.providers.openai import OpenAIEvaluator


def test_parse_verdict_accepts_fenced_json() -> None:
    assert parse_verdict('```json\n{"supported": true}\n```') is True
    assert parse_verdict('{"supported": false}') is False


@pytest.mark.parametrize("text", ["not json", "{}", '{"supported": "yes"}'])
def test_parse_verdict_rejects_unexpected_answers(text: str) -> None:
    with pytest.raises(ProviderError):
        parse_verdict(text)


def test_anthropic_skips_thinking_blocks() -> None:
    client = Mock()
    client.messages.create.return_value = SimpleNamespace(
        stop_reason="end_turn",
        content=[
            SimpleNamespace(type="thinking"),
            SimpleNamespace(type="text", text='{"supported": true}'),
        ],
    )
    evaluator = AnthropicEvaluator("claude-opus-5-5", client=client)

    assert evaluator.evaluate("He confesses.", "Story text") is True
    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["output_config"]["format"]["type"] == "json_schema"
    assert kwargs["messages"][0]["content"].startswith("Assertion: He confesses.")


def test_anthropic_reports_truncated_response() -> None:
    client = Mock()
    client.messages.create.return_value = SimpleNamespace(
        stop_reason="max_tokens", content=[]
    )
    evaluator = AnthropicEvaluator("claude-opus-5-5", client=client)

    with pytest.raises(ProviderError, match="'max_tokens' before answering"):
        evaluator.evaluate("He confesses.", "Story text")


def test_anthropic_requires_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)

    with pytest.raises(ProviderError, match="ANTHROPIC_API_KEY"):
        AnthropicEvaluator("claude-opus-5-5")


def test_openai_reads_json_answer() -> None:
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content='{"supported": false}'))]
    )

    assert OpenAIEvaluator("gpt-4.1-mini", client=client).evaluate("A", "S") is False


def test_ollama_reads_structured_boolean() -> None:
    client = Mock()
    client.chat.return_value = SimpleNamespace(
        message=SimpleNamespace(content='{"supported": true}')
    )
    evaluator = OllamaEvaluator("qwen3:8b", context_length=65536, client=client)

    assert evaluator.evaluate("A", "S") is True
    kwargs = client.chat.call_args.kwargs
    assert kwargs["model"] == "qwen3:8b"
    assert kwargs["options"]["num_ctx"] == 65536
