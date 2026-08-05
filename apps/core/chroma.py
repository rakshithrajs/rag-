"""Thin wrapper around a local persistent ChromaDB client."""

import logging
from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection
from django.conf import settings

logger = logging.getLogger(__name__)

_COLLECTION_NAME = "knowledge"


def _get_client() -> chromadb.ClientAPI:
    """Return a persistent ChromaDB client using the configured directory."""
    path = Path(settings.CHROMA_DB_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(path))


def _get_collection() -> Collection:
    """Return the shared knowledge collection."""
    client = _get_client()
    return client.get_or_create_collection(name=_COLLECTION_NAME)


def add_chunks(
    source_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
    metadata: list[dict[str, Any]],
) -> None:
    """Upsert text chunks for a single knowledge source."""
    if not chunks:
        return

    if len(chunks) != len(embeddings) or len(chunks) != len(metadata):
        raise ValueError("chunks, embeddings, and metadata must have the same length")

    ids = [f"source-{source_id}-{index}" for index in range(len(chunks))]
    collection = _get_collection()
    collection.upsert(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadata,
    )
    logger.info("Added %d chunks for source %d", len(chunks), source_id)


def query(
    embedding: list[float],
    n_results: int = 5,
) -> dict[str, Any]:
    """Query the knowledge collection by a single embedding vector."""
    collection = _get_collection()
    return collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )


def delete_source(source_id: int) -> None:
    """Remove all chunks belonging to a knowledge source."""
    collection = _get_collection()
    collection.delete(where={"source_id": source_id})
    logger.info("Deleted chunks for source %d", source_id)
