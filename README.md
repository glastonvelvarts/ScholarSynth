# PaperContext

Read PDFs and run LLM tooling. **vLLM is Linux-only** — use WSL2 on Windows.

## Windows (PDF only)

```powershell
uv run read.py Automating_Customer_Service_Using_Langchain.pdf
```

## WSL2 + vLLM

### 1. One-time: enable WSL2

In **PowerShell (Admin)**:

```powershell
wsl --install -d Ubuntu
```

Reboot if prompted. Set your Ubuntu username/password on first launch.

### 2. One-time: NVIDIA GPU in WSL

1. Install the latest [NVIDIA driver for Windows](https://www.nvidia.com/Download/index.aspx) (must support WSL2).
2. Reboot.
3. In Ubuntu:

```bash
nvidia-smi
```

If that works, the GPU is available in WSL.

### 3. Install project + vLLM (inside Ubuntu)

From Windows, open Ubuntu, then:

```bash
cd /mnt/c/Users/glast/OneDrive/Desktop/PaperContext
bash scripts/wsl-setup.sh
```

> **Tip:** OneDrive under `/mnt/c` can be slow. For heavy vLLM use, copy the repo to `~/PaperContext` and run the script there.

### 4. Daily use (WSL)

```bash
cd /mnt/c/Users/glast/OneDrive/Desktop/PaperContext   # or ~/PaperContext

uv run read.py Automating_Customer_Service_Using_Langchain.pdf

# Example: start OpenAI-compatible server (adjust model name)
uv run python -m vllm.entrypoints.openai.api_server \
  --model meta-llama/Llama-3.2-3B-Instruct \
  --host 0.0.0.0 --port 8000
```

From Windows, call `http://localhost:8000` while the server runs in WSL.

### Optional: run setup from PowerShell

```powershell
wsl -d Ubuntu -- bash -lc "cd '/mnt/c/Users/glast/OneDrive/Desktop/PaperContext' && bash scripts/wsl-setup.sh"
```

Replace `Ubuntu` with your distro name from `wsl -l -v`.

'''
reader.py
    ↓
chunker.py
    ↓
embedder.py
    ↓
milvus.py
'''