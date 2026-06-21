"""vLLM answer synthesis from retrieved context."""

from __future__ import annotations

import logging
import os
from typing import Optional

from dotenv import load_dotenv
from llama_index.core.llms import ChatMessage, MessageRole
from llama_index.core.schema import NodeWithScore
from llama_index.llms.openai_like import OpenAILike

from scholarsynth.rag.prompts import RAG_SYSTEM_PROMPT

load_dotenv()

logger = logging.getLogger(__name__)

VLLM_BASE_URL = (os.environ.get("SCHOLARSYNTH_VLLM_BASE_URL") or "http://localhost:8000/v1").strip()
VLLM_MODEL = (os.environ.get("SCHOLARSYNTH_VLLM_SERVED_MODEL") or "qwen-coder-7b").strip()
VLLM_API_KEY = (os.environ.get("SCHOLARSYNTH_VLLM_API_KEY") or "not-needed").strip()
VLLM_TIMEOUT = float(os.environ.get("SCHOLARSYNTH_VLLM_TIMEOUT", "120"))


def build_llm(
    *,
    api_base: str = VLLM_BASE_URL,
    model: str = VLLM_MODEL,
    api_key: str = VLLM_API_KEY,
    timeout: float = VLLM_TIMEOUT,
    temperature: float = 0.2,
    max_tokens: int = 2048,
) -> OpenAILike:
    return OpenAILike(
        model=model,
        api_base=api_base,
        api_key=api_key,
        is_chat_model=True,
        is_function_calling_model=False,
        timeout=timeout,
        temperature=temperature,
        max_tokens=max_tokens,
        additional_kwargs={"top_p": 0.9},
    )


def _format_context_header(node: NodeWithScore) -> str:
    meta = node.node.metadata
    doc = meta.get("document_name", "unknown")
    page = meta.get("page_label") or meta.get("page", "?")
    section = meta.get("section") or ""
    chunk_type = meta.get("chunk_type", "prose")
    header = f"[{doc}, p.{page}] ({chunk_type})"
    if section:
        header += f" — {section}"
    return header


def build_context_prompt(query: str, nodes: list[NodeWithScore]) -> str:
    blocks = [
        f"{_format_context_header(node)}\n{node.node.get_content()}"
        for node in nodes
    ]
    context_str = "\n\n".join(blocks)
    return (
        "Use only the excerpts below to answer the question.\n\n"
        f"{context_str}\n\n"
        f"Question: {query}"
    )


def generate_answer(
    query: str,
    nodes: list[NodeWithScore],
    llm: Optional[OpenAILike] = None,
) -> str:
    """Call Modal-hosted vLLM with retrieved context."""
    client = llm or build_llm()
    user_prompt = build_context_prompt(query, nodes)

    logger.info("Generating answer via vLLM at %s model=%s", VLLM_BASE_URL, VLLM_MODEL)
    try:
        response = client.chat(
            [
                ChatMessage(role=MessageRole.SYSTEM, content=RAG_SYSTEM_PROMPT),
                ChatMessage(role=MessageRole.USER, content=user_prompt),
            ]
        )
    except Exception as exc:
        err = str(exc).lower()
        if "404" in err or "not found" in err or "invalid function call" in err:
            raise RuntimeError(
                "vLLM endpoint unreachable. Check SCHOLARSYNTH_VLLM_BASE_URL in .env — "
                "Modal URLs must include your workspace prefix, e.g. "
                "https://<workspace>--scholarsynth-vllm-serve.modal.run/v1 "
                "(run `modal deploy model.py` to print the correct URL). "
                f"Current: {VLLM_BASE_URL}"
            ) from exc
        raise
    return str(response.message.content).strip()
