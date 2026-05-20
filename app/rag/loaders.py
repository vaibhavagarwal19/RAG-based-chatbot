import os
import re
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

DATA_DIR = "data"


def find_pdfs_in_data() -> List[str]:
    """Return PDF paths under data/, excluding the FAISS index directory."""
    if not os.path.isdir(DATA_DIR):
        return []

    paths: List[str] = []
    for root, dirs, files in os.walk(DATA_DIR):
        if "faiss_index" in dirs:
            dirs.remove("faiss_index")
        if os.path.basename(root) == "faiss_index":
            continue
        for name in sorted(files):
            if name.lower().endswith(".pdf"):
                paths.append(os.path.join(root, name))
    return sorted(paths)


def _normalize_extracted_text(text: str) -> str:
    """
    Fix PDFs where each character was extracted on its own line (unusable for RAG).
    """
    if not text or not text.strip():
        return text

    lines = [line.strip() for line in text.splitlines()]
    non_empty = [ln for ln in lines if ln]
    if not non_empty:
        return text

    single_char = sum(1 for ln in non_empty if len(ln) == 1)
    if single_char > len(non_empty) * 0.4:
        return " ".join(non_empty)

    collapsed = re.sub(r"\s+", " ", text).strip()
    # PDF layout often repeats each word 2–4 times in a row
    collapsed = re.sub(r"\b(\w+)(?:\s+\1\b)+", r"\1", collapsed, flags=re.IGNORECASE)
    return collapsed


def _load_with_pymupdf(path: str) -> List[Document]:
    from langchain_community.document_loaders import PyMuPDFLoader

    docs = PyMuPDFLoader(path).load()
    for doc in docs:
        doc.page_content = _normalize_extracted_text(doc.page_content)
    return docs


def load_pdf(path: str) -> List[Document]:
    """Load a PDF; prefer PyMuPDF for readable text extraction."""
    docs: List[Document]

    try:
        docs = _load_with_pymupdf(path)
    except Exception as exc:
        print(f"⚠️  PyMuPDF failed for {path} ({exc}); falling back to PyPDFLoader")
        docs = PyPDFLoader(path).load()
        for doc in docs:
            doc.page_content = _normalize_extracted_text(doc.page_content)

    for doc in docs:
        doc.metadata["source"] = path

    return docs
