"""Tests for documentation chunking."""

from src.ingestion.chunker import _split_with_overlap, chunk_documentation
from src.ingestion.loader import Document


def test_short_text_is_a_single_chunk():
    assert _split_with_overlap("hello", 1000, 100) == ["hello"]


def test_overlap_larger_than_chunk_still_terminates():
    """Regression: `start = end - overlap` could move backwards and loop forever."""
    text = "a\n" * 200
    chunks = _split_with_overlap(text, 50, 100)  # must return, not hang
    assert chunks
    # chunks are stripped, so compare the content that survives stripping
    assert "".join(chunks).count("a") == text.count("a")


def test_bambda_examples_are_never_chunked():
    doc = Document(id="b1", content="x" * 5000, metadata={"source_type": "bambda_example"})
    assert chunk_documentation([doc], max_chunk_size=100) == [doc]


def test_large_documentation_is_split():
    doc = Document(id="d1", content="word " * 2000, metadata={"source_type": "documentation"})
    chunks = chunk_documentation([doc], max_chunk_size=1000, overlap=100)
    assert len(chunks) > 1
    assert all(c.metadata["total_chunks"] == len(chunks) for c in chunks)
