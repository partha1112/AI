from backend.agents.transactions_agent import invoke_transaction
from backend.agents.GeneralState import AgentSate
from backend.agents.service_agent import invoke_service
from backend.agents.accounts_agent import invoke_accounts
from backend.agents.coordinator import invoke_coordinator
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver
import os
from dotenv import load_dotenv
from psycopg_pool import ConnectionPool

load_dotenv()

DB_URI = os.getenv("DB_URI")

graph = StateGraph(AgentSate)

graph.add_node("coordinator", invoke_coordinator)
graph.add_node("accounts", invoke_accounts)
graph.add_node("transaction", invoke_transaction)
graph.add_node("service", invoke_service)

graph.add_edge(START, "coordinator")

graph.add_conditional_edges("coordinator", lambda state: state.next_node,
    {
        "accounts": "accounts",
        "transactions": "transaction",
        "service": "service",
        "FINISH": END
    }
)

graph.add_edge("accounts", "coordinator")
graph.add_edge("transaction", "coordinator")
graph.add_edge("service", "coordinator")

pool = ConnectionPool(DB_URI)
checkpointer = PostgresSaver(pool)
checkpointer.setup()
workflow = graph.compile(checkpointer=checkpointer)