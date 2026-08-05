"""LangChain-based clients for Ollama embeddings and chat."""

import logging

from django.conf import settings
from langchain_ollama import ChatOllama, OllamaEmbeddings

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Raised when an embedding request fails."""


class ChatError(Exception):
    """Raised when a chat completion request fails."""


def _auth_headers() -> dict[str, str]:
    """Return authorization headers when an API key is configured."""
    if settings.OLLAMA_API_KEY:
        return {"Authorization": f"Bearer {settings.OLLAMA_API_KEY}"}
    return {}


def _embedding_client() -> OllamaEmbeddings:
    """Return a configured OllamaEmbeddings instance."""
    return OllamaEmbeddings(
        model=settings.OLLAMA_EMBED_MODEL,
        base_url=settings.OLLAMA_EMBED_HOST.rstrip("/"),
        client_kwargs={"headers": _auth_headers()},
    )


def _chat_client() -> ChatOllama:
    """Return a configured ChatOllama instance."""
    return ChatOllama(
        model=settings.OLLAMA_LANG_MODEL,
        base_url=settings.OLLAMA_HOST.rstrip("/"),
        client_kwargs={"headers": _auth_headers()},
        temperature=0.3,
        timeout=300,
    )


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Return one embedding vector for each input text."""
    if not texts:
        return []

    client = _embedding_client()
    try:
        return client.embed_documents(texts)
    except Exception as exc:
        logger.error("Embedding request failed for model %s: %s", settings.OLLAMA_EMBED_MODEL, exc)
        raise EmbeddingError(f"Embedding request failed: {exc}") from exc


def get_chat_response(messages: list[dict[str, str]]) -> str:
    """Send messages to the chat model and return the assistant's text."""
    client = _chat_client()
    try:
        response = client.invoke(messages)
        return response.content
    except Exception as exc:
        logger.error("Chat request failed for model %s: %s", settings.OLLAMA_LANG_MODEL, exc)
        raise ChatError(f"Chat request failed: {exc}") from exc
