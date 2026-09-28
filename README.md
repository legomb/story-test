# Story test

**Run plain-English tests against your stories or texts.**

<div align="center">

[![Build](https://github.com/legomb/story-test/actions/workflows/build.yml/badge.svg)](https://github.com/legomb/story-test/actions/workflows/build.yml)
[![PyPI version](https://img.shields.io/pypi/v/story-test.svg)](https://pypi.org/project/story-test/)

</div>

CLI tool that runs natural language tests (e.g. "The hero wins in the end") against a markdown text.

Lets you define a list of checks you expect from your story and determines whether each one passes or fails.

It does not replace a human editor, but it's a great tool to aid in the editing phase, for both writers and editors:

- Make sure your story's main points are addressed while editing your story.
- Build and grow a repository with standard tests you want to run on manuscripts, and make specific tests for specific genres, etc.

Supports OpenAI, Anthropic, and local [Ollama](https://ollama.com/) models.

> [!warning] WARNING (first and foremost)
> This app does not replace writers or editors.
> This app does not write or edit for you.
> It just checks the things you ask it to check.
> Fuck AI, and fuck hacks that use AI to make reading and writing less fun.

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

## Development Setup

The repository uses **direnv**, **Devbox**, **Taskfile**, and **pre-commit** for
a reproducible development environment and automatic schema/YAML validation.

### Setup

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

## Features

- [x] JSON structure validation using `jq`
- [x] Schema validation using `check-jsonschema` (temporarily disabled)
- [x] CI/CD integration with GitHub Actions
- [x] Versioning schemas with directories like `schemas/v1`, `schemas/v2`
- [x] Documentation with inline schema descriptions
- [x] Code formatting using `prettier` or `jq`
- [ ] Documentation with `README` or extended docs folder (pending)
- [ ] Schema hosting via `$id` URLs or SchemaStore (pending)
