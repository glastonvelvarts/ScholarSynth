"""LlamaIndex query engine: Milvus retrieval + vLLM synthesis."""

from __future__ import annotations

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.llms.openai_like import OpenAILike

from scholarsynth.rag.generator import build_llm
from scholarsynth.rag.milvus_retriever import MilvusRetriever
from scholarsynth.rag.pipeline import (
    RAGResponse,
    default_retrieval_config,
    run_rag,
)
from scholarsynth.rag.prompts import TEXT_QA_TEMPLATE
from scholarsynth.retrieval.retriever import RetrievalConfig


def build_query_engine(
    *,
    retrieval_config: RetrievalConfig | None = None,
    llm: OpenAILike | None = None,
) -> RetrieverQueryEngine:
    """LlamaIndex query engine wired to Milvus + vLLM."""
    retriever = MilvusRetriever(config=retrieval_config)
    synthesizer = get_response_synthesizer(
        llm=llm or build_llm(),
        text_qa_template=TEXT_QA_TEMPLATE,
        response_mode="compact",
    )
    return RetrieverQueryEngine(
        retriever=retriever,
        response_synthesizer=synthesizer,
        node_postprocessors=[],
    )


def ask(
    query: str,
    *,
    retrieval_config: RetrievalConfig | None = None,
    llm: OpenAILike | None = None,
    skip_generation_on_low_confidence: bool = True,
) -> RAGResponse:
    """Backward-compatible entrypoint; delegates to run_rag."""
    cfg = retrieval_config or default_retrieval_config()
    return run_rag(
        query,
        retrieval_config=cfg,
        llm=llm,
        skip_generation_on_low_confidence=skip_generation_on_low_confidence,
    )


if __name__ == "__main__":
    from scholarsynth.rag.pipeline import _print_response

    import logging
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

    question = " ".join(sys.argv[1:]).strip() or input("\nQuestion: ").strip()
    if not question:
        raise SystemExit("Empty query.")

    result = ask(question)
    _print_response(result)
