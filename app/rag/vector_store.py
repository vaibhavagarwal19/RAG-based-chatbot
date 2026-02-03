import os
from langchain_community.vectorstores import FAISS
from app.tools.embeddings import get_embeddings

# Where FAISS will be stored
FAISS_PATH = "data/faiss_index"

_vector_store = None


def create_vector_store(docs):
    """
    Create FAISS index and persist it to disk.
    """
    global _vector_store

    embeddings = get_embeddings()
    _vector_store = FAISS.from_documents(docs, embeddings)

    # Persist to disk
    _vector_store.save_local(FAISS_PATH)

    return _vector_store


def load_vector_store():
    global _vector_store
    _vector_store = FAISS.load_local(
        FAISS_PATH,
        get_embeddings(),  # embeddings load once, reused
        allow_dangerous_deserialization=True
    )
    return _vector_store


def get_vector_store():
    """
    Return the active vector store.
    """
    if _vector_store is None:
        raise RuntimeError("Vector store not initialized")
    return _vector_store


def vector_store_exists():
    return os.path.exists(FAISS_PATH)

def add_documents(docs):
    """
    Add new documents to existing FAISS index and persist.
    """
    global _vector_store

    if _vector_store is None:
        raise RuntimeError("Vector store not initialized")

    _vector_store.add_documents(docs)
    _vector_store.save_local(FAISS_PATH)
