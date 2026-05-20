from langchain_core.documents import Document

from app.rag.citations import document_to_chunk, format_source_citation


def test_document_to_chunk():
    doc = Document(
        page_content="Sample passage about presence.",
        metadata={"source": "data/uploads/book.pdf", "page": 4},
    )
    chunk = document_to_chunk(doc)
    assert chunk["source"] == "book.pdf"
    assert chunk["page"] == 5
    assert "presence" in chunk["content"]


def test_format_source_citation():
    chunk = {"content": "x" * 300, "source": "book.pdf", "page": 2}
    cite = format_source_citation(chunk, 1)
    assert cite["id"] == 1
    assert cite["source"] == "book.pdf"
    assert cite["page"] == 2
    assert cite["excerpt"].endswith("…")
