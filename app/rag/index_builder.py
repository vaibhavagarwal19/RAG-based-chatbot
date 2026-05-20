import threading
from typing import List, Optional

from app.rag.loaders import find_pdfs_in_data, load_pdf
from app.rag.ingestion import ingest_docs
from app.rag.vector_store import (
    create_vector_store,
    load_vector_store,
    vector_store_exists,
    is_vector_store_ready,
)

_lock = threading.Lock()
_building = False
_error: Optional[str] = None


def get_index_status() -> dict:
    with _lock:
        return {
            "ready": is_vector_store_ready(),
            "building": _building,
            "error": _error,
        }


def _set_building(value: bool) -> None:
    global _building
    with _lock:
        _building = value


def _set_error(msg: Optional[str]) -> None:
    global _error
    with _lock:
        _error = msg


def build_index_from_pdfs(pdf_paths: List[str]) -> None:
    """Build and persist the FAISS index (CPU-heavy; run off the main thread)."""
    _set_building(True)
    _set_error(None)
    try:
        chunks = []
        for path in pdf_paths:
            print(f"📄 Loading {path}...")
            chunks.extend(ingest_docs(load_pdf(path)))
        print(f"🔢 Embedding {len(chunks)} chunks — first run may take several minutes...")
        create_vector_store(chunks)
        print(f"✅ FAISS index ready ({len(chunks)} chunks)")
    except Exception as exc:
        _set_error(str(exc))
        print(f"❌ Index build failed: {exc}")
        raise
    finally:
        _set_building(False)


def start_index_build(pdf_paths: List[str]) -> None:
    with _lock:
        if is_vector_store_ready() or _building:
            return
    threading.Thread(
        target=build_index_from_pdfs,
        args=(pdf_paths,),
        daemon=True,
        name="faiss-index-build",
    ).start()


def initialize_vector_index() -> None:
    """
    Load an existing index or start a background build from PDFs under data/.
    Returns immediately so the HTTP server can accept connections.
    """
    if vector_store_exists():
        load_vector_store()
        print("✅ FAISS index loaded from disk")
        return

    pdf_paths = find_pdfs_in_data()
    if not pdf_paths:
        print("⚠️  No vector index yet. Add a PDF under data/ or upload one in the chat UI.")
        return

    print(f"⏳ Building index in background from {len(pdf_paths)} PDF(s)...")
    for path in pdf_paths:
        print(f"   → {path}")
    start_index_build(pdf_paths)
