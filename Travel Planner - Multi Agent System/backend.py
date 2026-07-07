
from langchain_core.messages import HumanMessage
import uuid
import os
from dotenv import load_dotenv

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.postgres import PostgresSaver

from agents.state import TravelState
from agents.agent import  flight_agent, hotel_agent, itinerary_agent, response_agent

from psycopg.rows import dict_row
import psycopg

load_dotenv()

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent",hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("response_agent", response_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent","hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "response_agent")
graph.add_edge("response_agent", END)


db_url = os.getenv("DATABASE_URL")

connection_pool = psycopg.connect(db_url, autocommit = True, row_factory = dict_row)
checkpointer = PostgresSaver(connection_pool)
checkpointer.setup()

travel_graph = graph.compile(checkpointer=checkpointer, interrupt_before=["response_agent"])

def run_travel_planner(origin: str, destination: str, days: int, session_id: str):
    config = {"configurable": {"thread_id" : f"thread_{session_id}"}}

    input_query = f"I want to go to {destination} from {origin} for {days} days."
    
    result = travel_graph.invoke(
        {
            "message" :[
                HumanMessage(content=input_query)
            ],
            "user_query" : input_query,
            "origin": origin,
            "destination": destination,
            "days": days,
            "llm_calls" : 0,
            "flight_result" : "",
            "hotel_result" : "",
            "itinerary_result" : "",
            }, 
            config = config
        )

    return result

def get_travel_state(session_id: str):
    config = {"configurable": {"thread_id" : f"thread_{session_id}"}}
    return travel_graph.get_state(config)

def resume_travel_planner(session_id: str):
    config = {"configurable": {"thread_id" : f"thread_{session_id}"}}
    return travel_graph.invoke(None, config=config)
