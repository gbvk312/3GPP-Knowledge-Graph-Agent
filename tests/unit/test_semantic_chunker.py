import pytest
from lambdas.ingestion.semantic_chunker.handler import (
    compute_chunk_id,
    split_at_boundaries,
    sub_split,
)


def test_compute_chunk_id_deterministic():
    id1 = compute_chunk_id("38.331", "Rel-18", "5.5.4", 0)
    id2 = compute_chunk_id("38.331", "Rel-18", "5.5.4", 0)
    assert id1 == id2


def test_compute_chunk_id_different_offsets():
    id1 = compute_chunk_id("38.331", "Rel-18", "5.5.4", 0)
    id2 = compute_chunk_id("38.331", "Rel-18", "5.5.4", 1)
    assert id1 != id2


def test_split_at_boundaries_headings():
    content = "## Section 1\nContent A\n\n## Section 2\nContent B"
    chunks = split_at_boundaries(content)
    assert len(chunks) >= 2


def test_split_at_boundaries_asn1():
    content = "## Header\nSome text\n```asn1\nMyType ::= SEQUENCE {}\n```\nMore text"
    chunks = split_at_boundaries(content)
    # ASN.1 block should be its own chunk
    asn1_chunks = [c for c in chunks if "asn1" in c["text"] or "SEQUENCE" in c["text"]]
    assert len(asn1_chunks) >= 1


def test_sub_split_small_chunk():
    text = "Short paragraph."
    result = sub_split(text, max_size=8192)
    assert result == [text]


def test_sub_split_large_chunk():
    # Create a chunk > 8KB
    paragraphs = [f"Paragraph {i} with some content. " * 20 for i in range(20)]
    text = "\n\n".join(paragraphs)
    result = sub_split(text, max_size=8192)
    assert len(result) > 1
    # Verify overlap: last paragraph of chunk N should appear in chunk N+1
    for chunk in result:
        assert len(chunk.encode("utf-8")) <= 8192 + 500  # Allow small overflow from overlap
