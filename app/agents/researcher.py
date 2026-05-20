from app.rag.citations import document_to_chunk
from app.rag.vector_store import get_vector_store
from app.schemas.state import AgentState


def research_agent(state: AgentState) -> dict:
    """Retrieve relevant document chunks using vector similarity search."""
    query = state.get("user_query")

    if not query:
        return {"retrieved_chunks": []}

    try:
        vector_store = get_vector_store()
        docs = vector_store.similarity_search(query=query, k=6)
        chunks = [document_to_chunk(doc) for doc in docs]
        print(f"🔍 Retrieved {len(chunks)} chunks")
        return {"retrieved_chunks": chunks}

    except Exception as e:
        return {"retrieved_chunks": [], "error": str(e)}
