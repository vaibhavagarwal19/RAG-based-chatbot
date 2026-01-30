from app.rag.vector_store import get_vector_store
from app.schemas.state import AgentState


def research_agent(state: AgentState) -> dict:
    """
    Retrieves relevant document chunks using vector similarity search.
    """
    query = state.get("user_query")

    if not query:
        return {
            "retrieved_docs": [],
            "next_agent": "reasoning"
        }

    try:
        vector_store = get_vector_store()

        # Retrieve top-k relevant chunks
        docs = vector_store.similarity_search(
            query=query,
            k=4
        )

        retrieved_docs = [doc.page_content for doc in docs]

        return {
            "retrieved_docs": retrieved_docs,
            "next_agent": "reasoning"
        }

    except Exception as e:
        # Fail safely — downstream agents can handle empty retrieval
        return {
            "retrieved_docs": [],
            "error": str(e),
            "next_agent": "reasoning"
        }
