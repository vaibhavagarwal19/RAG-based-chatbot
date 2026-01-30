from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    user_query: str
    plan: List[str]
    retrieved_docs: List[str]
    reasoning: Optional[str]
    validation_status: Optional[str]
    final_answer: Optional[str]
    next_agent: str
