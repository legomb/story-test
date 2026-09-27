#!/bin/sh

set -eu

root_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
install_dir="${STORY_TEST_INSTALL_DIR:-$HOME/.local/share/story-test}"
venv_dir="$install_dir/venv"
bin_dir="${STORY_TEST_BIN_DIR:-$HOME/.local/bin}"
model="${STORY_TEST_MODEL:-qwen3:8b}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is required. Install it from https://ollama.com/ and rerun this script." >&2
  exit 1
fi

mkdir -p "$install_dir" "$bin_dir"
python3 -m venv "$venv_dir"
"$venv_dir/bin/python" -m pip install --upgrade pip
"$venv_dir/bin/python" -m pip install "$root_dir"
ln -sf "$venv_dir/bin/story-test" "$bin_dir/story-test"

echo "Pulling Ollama model: $model"
ollama pull "$model"
echo "Installed story-test at $bin_dir/story-test"
echo "Ensure $bin_dir is on your PATH."
