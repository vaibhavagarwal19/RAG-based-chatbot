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

        # Retrieve top-k relevant chunks (docs may carry similarity scores)
        docs = vector_store.similarity_search(
            query=query,
            k=6  # slightly larger pool for ranking
        )

        # docs is a list of Document objects; some stores include a ‘score’ attribute
        retrieved_docs = []
        retrieved_scores = []
        for doc in docs:
            retrieved_docs.append(doc.page_content)
            # attempt to grab score metadata if available
            score = getattr(doc, "score", None) or doc.metadata.get("score") if hasattr(doc, "metadata") else None
            retrieved_scores.append(score)

        # log for debugging
        print(f"🔍 Retrieved {len(retrieved_docs)} chunks (scores: {retrieved_scores})")

        return {
            "retrieved_docs": retrieved_docs,
            "retrieved_scores": retrieved_scores,
            "next_agent": "reasoning"
        }

    except Exception as e:
        # Fail safely — downstream agents can handle empty retrieval
        return {
            "retrieved_docs": [],
            "error": str(e),
            "next_agent": "reasoning"
        }
