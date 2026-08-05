"""Text chunking using langchain's recursive splitter."""

from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """Split long text into overlapping chunks by character count."""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ) -> None:
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )

    def split(self, text: str) -> list[str]:
        """Return a list of text chunks."""
        text = text.strip()
        if not text:
            return []

        return self._splitter.split_text(text)
