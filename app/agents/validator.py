from app.schemas.state import AgentState


def validator_agent(state: AgentState) -> dict:
    """
    Validates whether the generated reasoning is grounded,
    non-empty, and safe to present to the user.
    """
    retrieved_docs = state.get("retrieved_docs", [])
    reasoning = state.get("reasoning")
    error = state.get("error")

    # Case 1: Upstream error (LLM or retrieval failure)
    if error:
        return {
            "validation_status": "failed",
            "final_answer": (
                "❌ An internal error occurred while processing your request. "
                "Please try again."
            ),
            "next_agent": "end"
        }

    # Case 2: No documents retrieved
    if not retrieved_docs:
        return {
            "validation_status": "failed",
            "final_answer": (
                "❌ I couldn’t find relevant information in the document "
                "to answer this question."
            ),
            "next_agent": "end"
        }

    # Case 3: No reasoning generated
    if not reasoning:
        return {
            "validation_status": "failed",
            "final_answer": (
                "❌ The document does not contain enough information "
                "to answer this question confidently."
            ),
            "next_agent": "end"
        }

    # Case 4: Weak or suspicious reasoning (too short)
    if len(reasoning.strip()) < 30:
        return {
            "validation_status": "failed",
            "final_answer": (
                "❌ The retrieved information was insufficient to generate "
                "a reliable answer."
            ),
            "next_agent": "end"
        }

    # Passed all checks
    return {
        "validation_status": "passed",
        "next_agent": "executor"
    }
