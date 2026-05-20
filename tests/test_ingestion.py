from langchain_core.documents import Document

from app.rag.ingestion import ingest_docs


def test_ingest_preserves_metadata():
    docs = [
        Document(
            page_content="A" * 1200,
            metadata={"source": "data/test.pdf", "page": 3},
        )
    ]
    chunks = ingest_docs(docs)
    assert len(chunks) >= 2
    assert chunks[0].metadata["source"] == "data/test.pdf"
    assert chunks[0].metadata["page"] == 3
