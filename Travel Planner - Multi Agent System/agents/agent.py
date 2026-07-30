import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from openai.types.responses import response
from tools.tavily_tool import tavily_search
from langchain_core.messages import AIMessage
from tools.flilght_tool import search_flights
from  agents.state import TravelState

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")


def flight_agent(state : TravelState):
    origin = state["origin"]
    destination = state["destination"]
    
    try:
        flight_data = search_flights(origin, destination)
    except Exception as e:
        flight_data = f"Error fetching flights: {e}"

    return{
        "flight_result": flight_data,
        "message":[
            AIMessage(content=f"Flight data fetched for {origin} to {destination}")
        ],
        "llm_calls":state.get("llm_calls", 0) + 1
    }
    
def hotel_agent(state : TravelState):

    destination = state["destination"]
    days = state["days"]
    user_comments = state.get("user_comments", "")
    search_query = f"Budget hotels in {destination} for {days} days"
    if user_comments:
        search_query += f" with preferences: {user_comments}"
    hotel_data = tavily_search(search_query)

    return{
        "hotel_result": hotel_data,
        "message":[
            AIMessage(content="Hotel data fetched")
        ],
        "llm_calls":state.get("llm_calls", 0) + 1
    }

def itinerary_agent(state : TravelState):
    user_query = state["user_query"]
    user_comments = state.get("user_comments", "")
    filgt_results = state["flight_result"]
    hotel_result = state["hotel_result"]
    days = state["days"]
    destination = state["destination"]

    full_user_input = user_query
    if user_comments:
        full_user_input += f" Preferences: {user_comments}"

    prompt = f"""
    Create a complete {days}-day travel itinerary for {destination} based on the following information:
    Flights: {filgt_results}
    Hotels: {hotel_result}
    User Input: {full_user_input}
    
    Make itinerary practical, budget friendly and easy to follow and time saving
    """

    response = llm.invoke(
        [SystemMessage(content="You are a expert travel agent"),
        HumanMessage(content=prompt)])

    return{
        "itinerary_result" : response.content,
        "message" :   [response],
        "llm_calls" : state.get("llm_calls",0) + 1  
    }
    
def response_agent(state : TravelState):
    user_query = state["user_query"]
    user_comments = state.get("user_comments", "")
    flight_result = state["flight_result"]
    hotel_result = state["hotel_result"]
    itinerary_result = state["itinerary_result"]
    
    prompt = f"""
    Analyze the response received from each agent as mentioned below.
    flight_result : {flight_result}
    hotel_result : {hotel_result}
    itinerary_result : {itinerary_result}
    User Input: {user_query}
    User Comments: {user_comments}

    Format a final response to the user using simple language including the below points:

    1. Trip Summary
    2. Flight Information
    3. Hotel Suggestions
    4. Day-by-day Itinerary
    5. Estimated Budget
    6. Final recommendations

    Important Note:
    - Be clear and practical
    - Mention that live flight API may not provide ticket prices and availabilities
    - Hotel suggestions should be budget friendly
    - Itinerary should be easy to follow and time saving
    - Estimated budget should be realistic
    - Final response should be engaging and helpful
    """

    response = llm.invoke([
        SystemMessage(content="You are a expert and professional travel agent"),
        HumanMessage(content=prompt)
    ])

    return{
        "message": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }


    

