from app.schemas.state import AgentState

def planner_agent(state: AgentState) -> dict:
    """
    Creates an execution plan based on the user query.
    """
    query = state.get("user_query", "").lower()

    # Basic adaptive planning (can be expanded later)
    plan = [
        "Analyze user intent",
        "Search the document corpus using vector similarity",
        "Extract relevant context passages",
        "Generate a grounded answer using retrieved context",
        "Validate the answer against retrieved information",
        "Format and return the final response"
    ]

    return {
        "plan": plan,
        "next_agent": "research"
    }
