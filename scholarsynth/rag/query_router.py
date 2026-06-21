"""Classify queries that need broad / vectorless retrieval."""

from __future__ import annotations

import re

_GENERAL_PATTERNS = re.compile(
    r"\b("
    r"summarize|summarise|summary|overview|recap|"
    r"compare|comparison|contrast|"
    r"all papers|all documents|all uploaded|each paper|across papers|"
    r"main themes|key themes|common themes|"
    r"what are the|list the|give me an overview|"
    r"high.?level|big picture|"
    r"methodolog(y|ies)|findings|contributions|limitations"
    r")\b",
    re.IGNORECASE,
)


def is_general_query(query: str) -> bool:
    """True when the user wants synthesis across documents, not a pinpoint fact."""
    text = query.strip()
    if len(text) < 8:
        return False
    if _GENERAL_PATTERNS.search(text):
        return True
    # Short open-ended prompts common in the UI
    if text.lower().startswith(("summarize", "summarise", "compare", "list", "overview")):
        return True
    return False
