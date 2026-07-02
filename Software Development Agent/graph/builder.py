from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from graph.state import AgentState


from agents.analyzer import analyze_request
from agents.developer import developer_agent
from agents.planer import planer_agent


def build_graph():

    builder = StateGraph(AgentState)

    builder.add_node("analyze_request", analyze_request)
    builder.add_node("developer_agent", developer_agent)
    builder.add_node("planer_agent", planer_agent)

    builder.add_edge(START, "analyze_request")
    builder.add_edge("analyze_request", "planer_agent")
    builder.add_edge("planer_agent","developer_agent")
    builder.add_edge("developer_agent", END)

    memory = MemorySaver()
    graph = builder.compile(checkpointer=memory, interrupt_before=["developer_agent"])

    return graph

