"""Retrieval-augmented generation logic for chat answers."""

import logging
from typing import Any

from apps.core import chroma, ollama
from apps.chat.models import Conversation, Message

logger = logging.getLogger(__name__)

MAX_HISTORY_MESSAGES = 10
MAX_RETRIEVED_CHUNKS = 5
SYSTEM_PROMPT = """You are a grounded knowledge assistant. Answer the user's question using ONLY the retrieved context below. If the context does not contain enough information, clearly say so and do not invent facts. Cite the provided sources implicitly by referring to the context.

Retrieved context:
{context}

Respond in the requested language: {language}"""


def retrieve_chunks(question: str, n_results: int = MAX_RETRIEVED_CHUNKS) -> list[dict[str, Any]]:
    """Embed a question and return the most relevant chunks from ChromaDB."""
    if not question.strip():
        return []

    embeddings = ollama.get_embeddings([question])
    if not embeddings:
        return []

    results = chroma.query(embedding=embeddings[0], n_results=n_results)
    documents = results.get("documents") or [[]]
    metadatas = results.get("metadatas") or [[]]
    distances = results.get("distances") or [[]]

    chunks = []
    for text, metadata, distance in zip(
        documents[0], metadatas[0], distances[0], strict=False
    ):
        chunks.append(
            {
                "text": text,
                "source": metadata.get("title", "Unknown source"),
                "source_type": metadata.get("source_type", "unknown"),
                "source_id": metadata.get("source_id"),
                "chunk_index": metadata.get("chunk_index", 0),
                "distance": distance,
            }
        )

    return chunks


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
    return [
        {
            "source": chunk["source"],
            "source_type": chunk["source_type"],
            "source_id": chunk["source_id"],
            "chunk_index": chunk["chunk_index"],
            "text": chunk["text"],
        }
        for chunk in chunks
    ]


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
