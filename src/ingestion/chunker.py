"""Chunking strategies for different document types."""

from typing import List

from .loader import Document


def chunk_documentation(
    documents: List[Document],
    max_chunk_size: int = 1000,
    overlap: int = 100,
) -> List[Document]:
    """Further chunk documentation if needed.

    Bambda examples are kept intact (no chunking).
    Documentation is chunked if sections are too large.

    Args:
        documents: List of documents to potentially chunk
        max_chunk_size: Maximum chunk size in characters
        overlap: Overlap between chunks

    Returns:
        List of chunked documents
    """
    chunked = []

    for doc in documents:
        # Don't chunk bambda examples - they should stay complete
        if doc.metadata.get("source_type") == "bambda_example":
            chunked.append(doc)
            continue

        # Chunk documentation if too large
        if len(doc.content) > max_chunk_size:
            chunks = _split_with_overlap(doc.content, max_chunk_size, overlap)
            for i, chunk in enumerate(chunks):
                new_doc = Document(
                    id=f"{doc.id}_chunk_{i}",
                    content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    }
                )
                chunked.append(new_doc)
        else:
            chunked.append(doc)

    return chunked


def _split_with_overlap(text: str, max_size: int, overlap: int) -> List[str]:
    """Split text into chunks with overlap."""
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_size

        # Try to break at a natural boundary
        if end < len(text):
            # Look for newline near the end
            newline_pos = text.rfind('\n', start + max_size - 200, end)
            if newline_pos > start:
                end = newline_pos + 1

        chunks.append(text[start:end].strip())

        # Always move forward. With a small max_size (or a newline found right
        # after `start`) `end - overlap` can land at or before `start`, which
        # would loop forever.
        next_start = end - overlap
        start = next_start if next_start > start else end

    return chunks
