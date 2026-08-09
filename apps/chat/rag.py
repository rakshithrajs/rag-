"""Retrieval-augmented generation logic for chat answers."""

import logging
from typing import Any

from apps.core import chroma, ollama
from apps.core.reranker import Reranker
from apps.chat.models import Conversation, Message

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 10
MAX_RETRIEVED_CHUNKS = 5
MAX_CHUNK_DISTANCE = 0.85
PER_SOURCE_RESULTS = 12
PER_SOURCE_KEEP = 4
RERANK_TOP_N = 5
SYSTEM_PROMPT = """You are a grounded knowledge assistant. Answer the user's question using ONLY the retrieved context below. If the context does not contain enough information, clearly say so and do not invent facts. Cite the provided sources implicitly by referring to the context.

Retrieved context:
{context}

Respond in the requested language: {language}"""


_reranker: Reranker | None = None


def _get_reranker() -> Reranker:
    global _reranker
    if _reranker is None:
        _reranker = Reranker()
    return _reranker


def retrieve_chunks(question: str) -> list[dict[str, Any]]:
    """Return up to RERANK_TOP_N chunks ranked by the cross-encoder reranker.

    Pipeline: per-source top-K -> reranker top-N.

    Note: the reranker is authoritative on the final ordering. The embedding
    distance is only used to pick the top PER_SOURCE_KEEP from each source;
    no distance threshold is applied. When two sources cover overlapping
    vocabulary (e.g. a LangChain scraping guide and a RAG evaluation guide),
    the reranker can favor the noisier source for ambiguous queries. Removing
    the noisier source restores the expected answer. Tune the module-level
    constants below (PER_SOURCE_KEEP, RERANK_TOP_N) to experiment.
    """
    if not question.strip():
        return []

    embeddings = ollama.get_embeddings([question])
    if not embeddings:
        return []

    source_ids = chroma.list_ready_source_ids()
    if not source_ids:
        return []

    per_source: list[dict[str, Any]] = []
    for sid in source_ids:
        try:
            results = chroma.query_by_source(
                source_id=sid,
                embedding=embeddings[0],
                n_results=PER_SOURCE_RESULTS,
            )
        except Exception:
            logger.exception("query_by_source failed for source %s; skipping", sid)
            continue
        docs = (results.get("documents") or [[]])[0]
        metas = (results.get("metadatas") or [[]])[0]
        dists = (results.get("distances") or [[]])[0]
        combined = sorted(
            zip(docs, metas, dists, strict=False), key=lambda t: t[2]
        )[:PER_SOURCE_KEEP]
        for text, meta, dist in combined:
            per_source.append(
                {
                    "text": text,
                    "source": meta.get("title", "Unknown source"),
                    "source_type": meta.get("source_type", "unknown"),
                    "source_id": meta.get("source_id"),
                    "chunk_index": meta.get("chunk_index", 0),
                    "distance": dist,
                }
            )

    if not per_source:
        return []

    return _get_reranker().rerank(question, per_source, top_n=RERANK_TOP_N)


def format_context(chunks: list[dict[str, Any]]) -> str:
    """Format retrieved chunks into a single context string for the prompt."""
    parts = []
    for index, chunk in enumerate(chunks, start=1):
        parts.append(
            f"[{index}] Source: {chunk['source']}\n{chunk['text']}"
        )
    return "\n\n".join(parts)


def format_sources(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Format retrieved chunks for storage alongside an assistant message."""
    out: list[dict[str, Any]] = []
    for chunk in chunks:
        if not chunk:
            continue
        entry: dict[str, Any] = {
            "source": chunk.get("source", "Unknown source"),
            "source_type": chunk.get("source_type", "unknown"),
            "source_id": chunk.get("source_id"),
            "chunk_index": chunk.get("chunk_index", 0),
            "text": chunk.get("text", ""),
        }
        if "rerank_score" in chunk:
            entry["rerank_score"] = chunk["rerank_score"]
        out.append(entry)
    return out


def build_messages(
    question: str,
    chunks: list[dict[str, Any]],
    history: list[Message],
    language: str,
) -> list[dict[str, str]]:
    """Build the message list for the chat model."""
    messages: list[dict[str, str]] = []

    context = format_context(chunks) if chunks else "No relevant context was found."
    messages.append(
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(context=context, language=language),
        }
    )

    for message in history[-MAX_HISTORY_MESSAGES:]:
        role = message.role
        if role == Message.ROLE_ASSISTANT:
            role = "assistant"
        messages.append({"role": role, "content": message.content})

    messages.append({"role": "user", "content": question})
    return messages


def generate_answer(
    conversation: Conversation,
    question: str,
    language: str = "English",
) -> tuple[str, list[dict[str, Any]]]:
    """Retrieve context and generate an answer for a question."""
    chunks = retrieve_chunks(question)
    messages = build_messages(question, chunks, list(conversation.messages.all()), language)

    try:
        answer = ollama.get_chat_response(messages)
    except ollama.ChatError as exc:
        logger.exception("Answer generation failed for conversation %s", conversation.id)
        answer = "Sorry, I couldn't generate an answer right now. Please try again later."

    return answer, format_sources(chunks)
