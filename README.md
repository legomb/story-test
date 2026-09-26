# Story test

[![Build](https://github.com/legomb/story-test/actions/workflows/validation-schemas.yml/badge.svg)](https://github.com/legomb/story-test/actions/workflows/validation-schemas.yml) - [![Build](https://github.com/legomb/story-test/actions/workflows/validation-examples.yml/badge.svg)](https://github.com/legomb/story-test/actions/workflows/validation-examples.yml)

Runs tests against a story using a local [Ollama](https://ollama.com/) model.

## 🚀 Getting Started

This repo uses **direnv**, **Devbox**, **Taskfile**, and **pre-commit** for a reproducible dev environment and automatic schema/YAML validation.

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

Install Ollama separately, then download the default model through Task:

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

The local model is `qwen3:8b` by default. Set `STORY_TEST_MODEL` to use another
model already installed in Ollama.

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

The GitHub Actions workflow installs Ollama and pulls `qwen3:8b` automatically.
Qwen open-weight models are Apache 2.0 licensed and Ollama is MIT licensed;
always review the license for the exact model tag you deploy.

Run formatting and pre-commit checks with:

```bash
task format:check
task pre-commit:run
```

## Features

- [x] JSON structure validation using `jq`
- [x] Schema validation using `check-jsonschema` (temporarily disabled)
- [x] CI/CD integration with GitHub Actions
- [x] Versioning schemas with directories like `schemas/v1`, `schemas/v2`
- [x] Documentation with inline schema descriptions
- [x] Code formatting using `prettier` or `jq`
- [ ] Documentation with `README` or extended docs folder (pending)
- [ ] Schema hosting via `$id` URLs or SchemaStore (pending)
