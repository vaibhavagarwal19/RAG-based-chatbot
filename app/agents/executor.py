from app.schemas.state import AgentState


def executor_agent(state: AgentState) -> dict:
    """
    Formats and returns the final user-facing response.
    """
    # If validator already produced a final answer, respect it
    if state.get("final_answer"):
        return {
            "final_answer": state["final_answer"],
            "next_agent": "end"
        }

    reasoning = state.get("reasoning")

    # Safety fallback (should rarely happen)
    if not reasoning:
        return {
            "final_answer": (
                "❌ I couldn't generate a reliable answer from the document."
            ),
            "next_agent": "end"
        }

    final_answer = (
        "✅ Final Answer\n\n"
        f"{reasoning.strip()}"
    )

    return {
        "final_answer": final_answer,
        "next_agent": "end"
    }
