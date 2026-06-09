#!/usr/bin/env bash
# Run inside WSL2 (Ubuntu): bash scripts/wsl-setup.sh
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "==> scholarsynth WSL setup"
echo "    Project: $PROJECT_ROOT"

if ! command -v nvidia-smi &>/dev/null; then
  echo ""
  echo "WARNING: nvidia-smi not found in WSL."
  echo "  1. Install the latest NVIDIA driver on Windows (WSL2/CUDA support)."
  echo "  2. Reboot, then open WSL again and re-run this script."
  echo "  https://docs.nvidia.com/cuda/wsl-user-guide/"
  echo ""
else
  echo "==> GPU"
  nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
fi

if ! command -v uv &>/dev/null; then
  echo "==> Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

echo "==> $(uv --version)"
echo "==> Syncing project + vllm extra..."
uv sync --extra vllm

echo "==> Verifying vllm import..."
uv run python -c "import vllm; print('vllm', vllm.__version__)"

echo ""
echo "==> Done."
echo "    PDF:  uv run read.py Automating_Customer_Service_Using_Langchain.pdf"
echo "    vLLM: uv run python -m vllm.entrypoints.openai.api_server --help"
