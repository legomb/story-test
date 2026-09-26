# Story test

[![Build](https://github.com/legomb/story-test/actions/workflows/validation-schemas.yml/badge.svg)](https://github.com/legomb/story-test/actions/workflows/validation-schemas.yml) - [![Build](https://github.com/legomb/story-test/actions/workflows/validation-examples.yml/badge.svg)](https://github.com/legomb/story-test/actions/workflows/validation-examples.yml)

Runs tests against a story.

Uses [laya](https://github.com/NandhaKishorM/laya) to determine whether a test case passes or not.

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

Run `tasks` to see a list of available tasks.

## Features

- [x] JSON structure validation using `jq`
- [x] Schema validation using `check-jsonschema` (temporarily disabled)
- [x] CI/CD integration with GitHub Actions
- [x] Versioning schemas with directories like `schemas/v1`, `schemas/v2`
- [x] Documentation with inline schema descriptions
- [x] Code formatting using `prettier` or `jq`
- [ ] Documentation with `README` or extended docs folder (pending)
- [ ] Schema hosting via `$id` URLs or SchemaStore (pending)
