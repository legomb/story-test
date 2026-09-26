from pathlib import Path
from unittest.mock import Mock

from story_test import run_tests


ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "examples/the-tell-tale-heart/the-tell-tale-heart.tests.yml"
STORY = ROOT / "examples/the-tell-tale-heart/the-tell-tale-heart.md"


def test_tell_tale_heart_example() -> None:
    runner = Mock()
    runner.predict.return_value = {
        "answers": {
            "author": True,
            "narrator-reliability": True,
            "victim": True,
            "motive": False,
            "confession": True,
        }
    }

    results = run_tests(TESTS, [STORY], runner=runner)

    assert results == [
        {"name": "author", "passed": True},
        {"name": "narrator-reliability", "passed": True},
        {"name": "victim", "passed": True},
        {"name": "motive", "passed": False},
        {"name": "confession", "passed": True},
    ]
    runner.predict.assert_called_once()
    state, questions = runner.predict.call_args.args
    assert "The Tell-Tale Heart" in state
    assert questions["author"]["type"] == "noul"
