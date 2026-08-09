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
) -> Any:
    """Query the knowledge collection by a single embedding vector."""
    collection = _get_collection()
    return collection.query(
        query_embeddings=[embedding],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )


def query_by_source(
    source_id: int,
    embedding: list[float],
    n_results: int = 5,
) -> Any:
    """Query the collection limited to a single source_id.

    Chroma's KNN panics if n_results exceeds the size of the candidate set
    for a `where` filter, so we clamp.
    """
    collection = _get_collection()
    available = collection.get(
        where={"source_id": source_id},
        include=[],
    )
    available_count = len(available.get("ids") or [])
    if available_count == 0:
        empty: dict[str, Any] = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        return empty
    effective_n = min(n_results, available_count)
    return collection.query(
        query_embeddings=[embedding],
        n_results=effective_n,
        where={"source_id": source_id},
        include=["documents", "metadatas", "distances"],
    )


def list_ready_source_ids() -> list[int]:
    """Return distinct source_ids that currently have at least one chunk."""
    collection = _get_collection()
    data = collection.get(include=["metadatas"])
    ids: set[int] = set()
    for md in data.get("metadatas", []) or []:
        if not md:
            continue
        sid = md.get("source_id")
        if isinstance(sid, int):
            ids.add(sid)
    return sorted(ids)


def _reset_collection() -> None:
    """Drop and recreate the knowledge collection to rebuild the HNSW index.

    Used when the collection becomes empty: dropping the collection and
    letting it be recreated sheds any residual index fragmentation or
    inconsistency left by prior deletes, rather than accumulating it.
    """
    client = _get_client()
    client.delete_collection(name=_COLLECTION_NAME)
    client.get_or_create_collection(name=_COLLECTION_NAME)
    logger.info("Reset knowledge collection (fresh HNSW index)")


def delete_source(source_id: int) -> None:
    """Remove all chunks belonging to a knowledge source.

    Deletes by explicit chunk IDs rather than a ``where`` metadata filter.
    ChromaDB 1.x's ``where``-filter delete does not always reconcile the HNSW
    graph cleanly, which leaves the vector index inconsistent and makes
    subsequent ``query`` calls fail with internal errors (e.g.
    "Error finding id"). Deleting by IDs uses the well-exercised per-vector
    path. The IDs are first looked up via ``get``, a metadata scan that does
    not touch the HNSW index.

    If the delete empties the collection, drop and recreate it so the HNSW
    segment starts fresh. This is a safety net for any residual corruption
    and only triggers when there is nothing left to lose.
    """
    collection = _get_collection()
    existing = collection.get(where={"source_id": source_id}, include=[])
    ids = existing.get("ids") or []
    if ids:
        collection.delete(ids=ids)
    logger.info("Deleted %d chunks for source %d", len(ids), source_id)

    if collection.count() == 0:
        _reset_collection()
