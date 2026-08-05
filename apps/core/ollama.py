"""Thin client for Ollama embedding endpoints."""

import logging
from typing import Any

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Raised when an embedding request fails."""


class EmbeddingClient:
    """Client that generates embeddings via Ollama's /api/embed endpoint."""

    def __init__(
        self,
        host: str | None = None,
        model: str | None = None,
        timeout_seconds: int = 300,
    ) -> None:
        self.host = (host or settings.OLLAMA_EMBED_HOST).rstrip("/")
        self.model = model or settings.OLLAMA_EMBED_MODEL
        self.timeout_seconds = timeout_seconds

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one embedding vector for each input text."""
        if not texts:
            return []

        url = f"{self.host}/api/embed"
        payload: dict[str, Any] = {
            "model": self.model,
            "input": texts,
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.exceptions.Timeout as exc:
            logger.error("Embedding request timed out for model %s", self.model)
            raise EmbeddingError("Embedding request timed out") from exc
        except requests.exceptions.RequestException as exc:
            logger.error("Embedding request failed for model %s: %s", self.model, exc)
            raise EmbeddingError(f"Embedding request failed: {exc}") from exc

        data = response.json()
        embeddings = data.get("embeddings")
        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise EmbeddingError("Embedding response did not contain expected vectors")

        return embeddings


def get_embeddings(texts: list[str]) -> list[list[float]]:
    """Convenience function using configured Ollama embedding settings."""
    return EmbeddingClient().embed(texts)
