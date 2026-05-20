from typing import TypedDict, List, Optional, Dict, Any


class RetrievedChunk(TypedDict, total=False):
    content: str
    source: str
    page: Optional[int]


class AgentState(TypedDict, total=False):
    user_query: str
    retrieved_chunks: List[RetrievedChunk]
    reasoning: Optional[str]
    final_answer: Optional[str]
    sources: List[Dict[str, Any]]
    error: Optional[str]
    conversation: List[Dict[str, str]]
