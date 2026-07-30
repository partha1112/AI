from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from psycopg.rows import dict_row
import psycopg

from agents.state import TravelState
from agents.agent import (
    flight_agent,
    hotel_agent,
    itinerary_agent,
    response_agent,
)

load_dotenv()

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("response_agent", response_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "response_agent")
graph.add_edge("response_agent", END)

db_url = os.getenv("DATABASE_URL")

connection_pool = psycopg.connect(
    db_url,
    autocommit=True,
    row_factory=dict_row,
)

checkpointer = PostgresSaver(connection_pool)
checkpointer.setup()

travel_graph = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["response_agent"],
)


def invoke_travel_graph(
    origin: str,
    destination: str,
    days: int,
    comments: str,
    session_id: str,
):

    config = RunnableConfig(
        configurable={
            "thread_id": f"thread_{session_id}"
        }
    )

    base_query = (
        f"I want to go to {destination} "
        f"from {origin} "
        f"for {days} days."
    )

    input_query = (
        f"{base_query} {comments}"
        if comments
        else base_query
    )

    return travel_graph.invoke(
        {
            "message": [
                HumanMessage(content=input_query)
            ],
            "user_query": input_query,
            "user_comments": comments,
            "origin": origin,
            "destination": destination,
            "days": days,
            "llm_calls": 0,
            "flight_result": "",
            "hotel_result": "",
            "itinerary_result": "",
        },
        config=config,
    )


def get_travel_state(session_id: str):

    config = RunnableConfig(
        configurable={
            "thread_id": f"thread_{session_id}"
        }
    )

    return travel_graph.get_state(config)


def resume_travel_planner(session_id: str):

    config = RunnableConfig(
        configurable={
            "thread_id": f"thread_{session_id}"
        }
    )

    return travel_graph.invoke(
        None,
        config=config,
    )