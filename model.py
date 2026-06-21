"""
Modal deployment: vLLM OpenAI-compatible server on L40S (port 8000).

Deploy:
    modal deploy model.py

Dev (ephemeral URL):
    modal serve model.py

Then point ScholarSynth at the URL:
    export SCHOLARSYNTH_VLLM_BASE_URL=https://<workspace>--scholarsynth-vllm-serve.modal.run/v1
"""

from __future__ import annotations

import os
import subprocess

import modal

APP_NAME = "scholarsynth-vllm"
VLLM_PORT = 8000
GPU = "L40S"
MINUTES = 60

# Qwen3 has no 7B Coder checkpoint; Qwen2.5-Coder-7B is the best 7B coder fit for L40S.
# For pure research Q&A you can override with Qwen/Qwen3-8B via SCHOLARSYNTH_VLLM_HF_MODEL.
MODEL_NAME = os.environ.get(
    "SCHOLARSYNTH_VLLM_HF_MODEL",
    "Qwen/Qwen2.5-Coder-7B-Instruct",
)
SERVED_MODEL_NAME = os.environ.get(
    "SCHOLARSYNTH_VLLM_SERVED_MODEL",
    "qwen-coder-7b",
)

hf_cache_vol = modal.Volume.from_name("scholarsynth-hf-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("scholarsynth-vllm-cache", create_if_missing=True)

vllm_image = (
    modal.Image.debian_slim(python_version="3.12")
    .pip_install(
        "vllm==0.22.0",
        "huggingface_hub[hf_transfer]==0.36.0",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
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
        "vllm",
        "serve",
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
        "32768",
        "--enable-prefix-caching",
        "--uvicorn-log-level",
        "info",
    ]

    if "Qwen3" in MODEL_NAME:
        cmd.extend(
            [
                "--reasoning-parser",
                "qwen3",
                "--default-chat-template-kwargs",
                '{"enable_thinking": false}',
            ]
        )

    print("Starting vLLM:", " ".join(cmd), flush=True)
    subprocess.Popen(cmd)
