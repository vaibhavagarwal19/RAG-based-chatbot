from langgraph.graph import StateGraph, END
from app.schemas.state import AgentState
from app.agents.researcher import research_agent
from app.agents.reasoner import reasoning_agent
from app.agents.validator import validator_agent

graph = StateGraph(AgentState)

graph.add_node("research", research_agent)
graph.add_node("reasoning", reasoning_agent)
graph.add_node("validator", validator_agent)

graph.set_entry_point("research")
graph.add_edge("research", "reasoning")
graph.add_edge("reasoning", "validator")
graph.add_edge("validator", END)

app_graph = graph.compile()
