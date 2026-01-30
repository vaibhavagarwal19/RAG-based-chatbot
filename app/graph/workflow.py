from langgraph.graph import StateGraph, END
from app.schemas.state import AgentState
from app.agents.planner import planner_agent
from app.agents.researcher import research_agent
from app.agents.reasoner import reasoning_agent
from app.agents.validator import validator_agent
from app.agents.executor import executor_agent

graph = StateGraph(AgentState)

graph.add_node("planner", planner_agent)
graph.add_node("research", research_agent)
graph.add_node("reasoning", reasoning_agent)
graph.add_node("validator", validator_agent)
graph.add_node("executor", executor_agent)

graph.set_entry_point("planner")
graph.add_edge("planner", "research")
graph.add_edge("research", "reasoning")
graph.add_edge("reasoning", "validator")
graph.add_edge("validator", "executor")
graph.add_edge("executor", END)

app_graph = graph.compile()
