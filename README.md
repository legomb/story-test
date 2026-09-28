# Story test

<!-- **Run plain-English tests against your stories or texts.** -->

<div align="center">

[![Build](https://github.com/legomb/story-test/actions/workflows/build.yml/badge.svg)](https://github.com/legomb/story-test/actions/workflows/build.yml)
[![PyPI version](https://img.shields.io/pypi/v/story-test.svg)](https://pypi.org/project/story-test/)

</div>

This CLI uses AI and large language models (LLMs) to evaluate plain-English
tests (e.g., "The hero wins in the end") against Markdown stories or other text.
It reports whether each test passes or fails.

Supports OpenAI, Anthropic, and local [Ollama](https://ollama.com/) models.

> [!WARNING]
> This app does not replace writers or editors.
>
> This app does not write or edit for you.
>
> It just checks the things you ask it to check.
>
> This is not for hacks that use AI to make reading and writing less fun. Go home and get yourself an honest hobby.

## Use cases

For a one-time check, you can always upload your doc to an AI agent and ask it questions. But if you want to build a list of tests and run them anytime you want against any text, this tool enables you to:

- Writing: Make sure your story's main points are addressed while editing your story.
- Editing: Build and grow a repository with standard tests you want to run on manuscripts, and make specific tests for specific genres, etc.
- White papers / notes: Run tests against your notes or papers. Does my paper convey X point clearly after my latest changes?
- Contracts: Run tests against your contracts. Is X case covered?

## The problem (a.k.a. how this started)

Always good to start with the problem we want to solve.

As a writer, I keep:

- Notes
- To-do lists
- Checklists
- Character sheets/descriptions
- Plot summaries
- Notes for myself before I send manuscripts to an editor, that I have to re-check with every new draft
- Notes and snippets from books on writing, with advice I’d love to think I'm sticking to, but can’t keep track of.

But I'm also a software engineer 💅, and testing is part of my job.

And I noticed that all of these can be expressed as natural language tests (in plain English, or Spanish, or any language).

And now, with AI and LLMs, natural-language tests can be automated.

## 🚀 Getting Started

Install the CLI from PyPI with `pipx` so it is available from any directory in
an isolated Python environment:

```bash
pipx install story-test
```

Alternatively, install it into the active Python environment:

```bash
python -m pip install --upgrade story-test
```

The default provider is Ollama. Install Ollama separately and pull the default
model if you use it:

```bash
ollama pull qwen3:8b
```

For OpenAI or Anthropic, no local model runtime is needed; provide
`OPENAI_API_KEY` or `ANTHROPIC_API_KEY` and select the provider as shown above.

## Usage

Create a test file containing assertions about a story:

```yaml
tests:
  - name: author
    assertion: The story was written by Edgar Allan Poe.
  - name: ending
    assertion: The narrator confesses at the end of the story.
```

Run the tests against one or more Markdown files:

```bash
story-test story.tests.yml story.md
story-test story.tests.yml chapter-1.md chapter-2.md
```

Failed assertions are reported without failing the process by default. For CI, use strict mode:

```bash
story-test story.tests.yml story.md --fail-on-test-failure
```

The default provider is Ollama. For hosted OpenAI usage, set the API key and
select the provider explicitly:

```bash
export OPENAI_API_KEY=your-key
story-test story.tests.yml story.md --provider openai --model gpt-4.1-mini
```

For Anthropic:

```bash
export ANTHROPIC_API_KEY=your-key
story-test story.tests.yml story.md \
  --provider anthropic --model claude-opus-5-5
```

If you are using a Claude Code authorization token, Anthropic's SDK also accepts:

```bash
export ANTHROPIC_AUTH_TOKEN=your-token
```

Ollama remains available as an optional local provider:

```bash
STORY_TEST_PROVIDER=ollama sh install.sh
story-test story.tests.yml story.md --provider ollama --model qwen3:8b
```

## Advanced uses

### Test-driven writing

You could even use this for test-driven writing, which I'm hereby inventing I believe.
Pantsers: skip this section.

Some of you are plotters. Some of you are technical writers who start with
requirements before you have a document. Just for you, this app lets you apply
the basic TDD cycle to writing: define what you want the text to do, draft, run
the checks, and revise based on what they reveal.

Start by turning your outline, character notes, or revision checklist into
plain-English assertions. For example:

```yaml
tests:
  - name: protagonist-goal
    assertion: The protagonist's goal is clear by the end of the first chapter.
  - name: planted-clue
    assertion: The brass key is introduced before it is used to open the cellar.
  - name: ending-resolves-conflict
    assertion: The ending resolves the central conflict between the sisters.
```

Then run the tests against your draft:

```bash
story-test story.tests.yml story.md
```

An assertion failing does not mean the story is bad. It means either the draft
has not met that intention yet, or the assertion needs to be clarified. And a
passing assertion is not a grade for literary quality: these checks are prompts
for your judgment, not a substitute for it.

How to apply it to writing:

1. Start with your notes, outline, or requirements. Write a handful of checks for things you want the story to establish, include, or resolve.
2. Create a draft and run the checks. Early failures are expected; use them to spot intentions that are not yet showing up in the text.
3. After a writing session or major revision, run the same checks again. Add, remove, or refine checks as your plans change.

### CI for writing

If your manuscript lives in Git, you can run the checks on every push or pull
request. That gives you a repeatable reminder when a revision changes something
you were trying to preserve. Keep subjective checks advisory, and reserve strict
CI failure for assertions you genuinely want to enforce.

## Maintaining this repo

### Development Setup

The repository uses **direnv**, **Devbox**, **Taskfile**, and **pre-commit** for
a reproducible development environment and automatic schema/YAML validation.

```bash
# Automatically enter devbox via direnv (if available)
direnv allow

# Enter dev environment
devbox shell

# Install pre-commit hooks
task pre-commit:install
```

### Tasks

Run `task` to see a list of available tasks.

Install the development dependencies with:

```bash
task environment:dev:install
```

For a local user installation, run the bootstrap script from this repository:

```bash
sh install.sh
```

This creates an isolated Python environment and installs the `story-test`
command. The installed command can then be used from any directory:

```bash
story-test path/to/story.tests.yml path/to/story.md
```

For an Ollama installation, set `STORY_TEST_PROVIDER` before running the
installer to pull a local model:

```bash
STORY_TEST_PROVIDER=ollama STORY_TEST_MODEL=qwen3:30b-a3b sh install.sh
```

Install Ollama separately only when using the local provider, then download the model through Task:

```bash
task environment:ollama:install
```

To use a model already installed locally:

```bash
OLLAMA_MODEL=qwen3:30b-a3b task environment:ollama:install
```

Run the sample story tests. Failed story assertions are reported but do not
fail the task by default:

```bash
task test:example-story
```

The OpenAI and Anthropic providers use their standard `OPENAI_API_KEY` and
`ANTHROPIC_API_KEY` environment variables. The Ollama provider uses
`STORY_TEST_MODEL` and `STORY_TEST_CONTEXT_LENGTH` and is the default.

The model can be changed with `STORY_TEST_MODEL`, and the context window can be
changed with `STORY_TEST_CONTEXT_LENGTH`.

To make failed story assertions fail the task, use the strict variant:

```bash
task test:example-story:strict
```

Run the complete local validation suite:

```bash
task test:all
```

This runs schema validation, Python unit tests, and the sample story tests.

The GitHub Actions workflow validates and builds the package without running an
AI provider. Qwen open-weight models are Apache 2.0 licensed and Ollama is MIT
licensed; always review the license for the exact model tag you deploy.

Run formatting and pre-commit checks with:

```bash
task format:check
task pre-commit:run
```

Before publishing a release, build and validate both distribution formats:

```bash
task package:check
```

This creates the wheel and source archive under `dist/` and validates them with
Twine. Increment the version in `pyproject.toml` before building a new release.
