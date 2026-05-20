import os
from typing import Any, Dict, List, Optional

from langchain_core.documents import Document


def _page_number(meta: dict) -> Optional[int]:
    page = meta.get("page")
    if page is None:
        return None
    return int(page) + 1


def document_to_chunk(doc: Document) -> Dict[str, Any]:
    """Structured chunk with citation fields for the graph state."""
    meta = doc.metadata or {}
    source_path = str(meta.get("source", "unknown"))
    return {
        "content": doc.page_content,
        "source": os.path.basename(source_path),
        "page": _page_number(meta),
    }


def format_source_citation(chunk: Dict[str, Any], index: int) -> Dict[str, Any]:
    """API-facing citation object."""
    excerpt = chunk["content"][:280].strip()
    if len(chunk["content"]) > 280:
        excerpt += "…"
    return {
        "id": index,
        "source": chunk.get("source", "unknown"),
        "page": chunk.get("page"),
        "excerpt": excerpt,
    }
