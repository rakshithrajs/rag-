"""Background tasks for processing knowledge sources."""

import logging
from pathlib import Path

from django_tasks import task

from apps.core import chroma, ollama
from apps.core.chunker import TextChunker
from apps.sources.extractors import ExtractionError, extract
from apps.sources.models import KnowledgeSource

logger = logging.getLogger(__name__)

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_BATCH_SIZE = 32


@task()
def process_source(source_id: int) -> None:
    """Extract, chunk, embed, and store a knowledge source."""
    try:
        source = KnowledgeSource.objects.get(pk=source_id)
    except KnowledgeSource.DoesNotExist:
        logger.error("KnowledgeSource %d not found", source_id)
        return

    source.status = KnowledgeSource.STATUS_PROCESSING
    source.save(update_fields=["status", "updated_at"])

    try:
        file_path = None
        if source.source_type in (KnowledgeSource.SOURCE_TYPE_PDF, KnowledgeSource.SOURCE_TYPE_TXT):
            if not source.file:
                raise ExtractionError("Source is missing a file")
            file_path = Path(source.file.path)

        text = extract(
            source_type=source.source_type,
            file_path=file_path,
            url=source.url,
        )

        if not text.strip():
            raise ExtractionError("No text could be extracted from the source")

        chunker = TextChunker(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
        chunks = chunker.split(text)

        embeddings = _embed_in_batches(chunks)

        metadata = [
            {
                "source_id": source.id,
                "source_type": source.source_type,
                "title": source.title,
                "chunk_index": index,
            }
            for index in range(len(chunks))
        ]

        chroma.add_chunks(
            source_id=source.id,
            chunks=chunks,
            embeddings=embeddings,
            metadata=metadata,
        )

        source.status = KnowledgeSource.STATUS_READY
        source.metadata["chunks"] = len(chunks)
        source.save(update_fields=["status", "metadata", "updated_at"])
        logger.info("Processed KnowledgeSource %d into %d chunks", source.id, len(chunks))

    except Exception as exc:
        logger.exception("Failed to process KnowledgeSource %d", source_id)
        source.status = KnowledgeSource.STATUS_ERROR
        source.metadata["error"] = str(exc)
        source.save(update_fields=["status", "metadata", "updated_at"])


def _embed_in_batches(chunks: list[str]) -> list[list[float]]:
    """Generate embeddings for chunks in small batches."""
    embeddings: list[list[float]] = []
    for start in range(0, len(chunks), EMBEDDING_BATCH_SIZE):
        batch = chunks[start : start + EMBEDDING_BATCH_SIZE]
        batch_embeddings = ollama.get_embeddings(batch)
        embeddings.extend(batch_embeddings)
    return embeddings
