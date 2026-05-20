from app.schemas.state import AgentState


def validator_agent(state: AgentState) -> dict:
    """Validate the answer and set the final user-facing response."""
    retrieved_chunks = state.get("retrieved_chunks", [])
    reasoning = state.get("reasoning")
    error = state.get("error")
    sources = state.get("sources", [])

    if not retrieved_chunks:
        return {
            "final_answer": (
                "I couldn't find relevant information in the document to answer this question."
            ),
            "sources": [],
        }

    if not reasoning:
        if error:
            msg = str(error)
            if "401" in msg or "invalid_api_key" in msg.lower() or "authentication" in msg.lower():
                answer = (
                    "Groq API key is invalid or missing. "
                    "Set a valid GROQ_API_KEY in your .env file and restart the server."
                )
            else:
                answer = f"Could not generate an answer: {msg}"
        else:
            answer = (
                "The document does not contain enough information to answer this question confidently."
            )
        return {"final_answer": answer, "sources": []}

    if len(reasoning.strip()) < 30:
        return {
            "final_answer": (
                "The retrieved information was insufficient to generate a reliable answer."
            ),
            "sources": sources,
        }

    return {"final_answer": reasoning.strip(), "sources": sources}
