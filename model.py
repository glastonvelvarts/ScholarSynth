"""
Modal deployment: vLLM OpenAI-compatible server on L40S (port 8000).

Stack: Python 3.10 + CUDA 12.4 devel + vLLM 0.8.5 + Qwen2.5-7B-Instruct.
Qwen2.5-7B is a good model for RAG summarization and loads without tokenizer hacks.

Deploy:
    modal deploy model.py

Logs:
    modal app logs scholarsynth-vllm
"""

from __future__ import annotations

import os
import subprocess

import modal

APP_NAME = "scholarsynth-vllm"
VLLM_PORT = 8000
GPU = "L40S"
MINUTES = 60

MODEL_NAME = os.environ.get(
    "SCHOLARSYNTH_VLLM_HF_MODEL",
    "Qwen/Qwen2.5-7B-Instruct",
)
SERVED_MODEL_NAME = os.environ.get(
    "SCHOLARSYNTH_VLLM_SERVED_MODEL",
    "qwen2.5-7b-instruct",
)

VLLM_VERSION = os.environ.get("SCHOLARSYNTH_VLLM_VERSION", "0.8.5")

hf_cache_vol = modal.Volume.from_name("scholarsynth-hf-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("scholarsynth-vllm-cache", create_if_missing=True)

vllm_image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.4.0-devel-ubuntu22.04",
        add_python="3.10",
    )
    .entrypoint([])
    .pip_install(
        f"vllm=={VLLM_VERSION}",
        # vLLM 0.8.x breaks on transformers 5.x (all_special_tokens_extended removed).
        "transformers>=4.51.0,<5.0.0",
    )
    .env(
        {
            "HF_XET_HIGH_PERFORMANCE": "1",
            "VLLM_USE_V1": "0",
            "VLLM_WORKER_MULTIPROC_METHOD": "spawn",
        }
    )
)

app = modal.App(APP_NAME)


@app.function(
    image=vllm_image,
    gpu=f"{GPU}:1",
    timeout=15 * MINUTES,
    scaledown_window=15 * MINUTES,
    volumes={
        "/root/.cache/huggingface": hf_cache_vol,
        "/root/.cache/vllm": vllm_cache_vol,
    },
)
@modal.concurrent(max_inputs=16)
@modal.web_server(port=VLLM_PORT, startup_timeout=15 * MINUTES)
def serve():
    cmd = [
        "python",
        "-m",
        "vllm.entrypoints.openai.api_server",
        "--model",
        MODEL_NAME,
        "--served-model-name",
        SERVED_MODEL_NAME,
        "--host",
        "0.0.0.0",
        "--port",
        str(VLLM_PORT),
        "--tensor-parallel-size",
        "1",
        "--gpu-memory-utilization",
        "0.90",
        "--max-model-len",
        "8192",
        "--enforce-eager",
        "--disable-log-requests",
    ]

    print("Starting vLLM:", " ".join(cmd), flush=True)
    subprocess.Popen(cmd)
