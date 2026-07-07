from typing import TypedDict, Annotated
from langchain_core.messages import AnyMessage
import operator

class TravelState(TypedDict):
    message : Annotated[list[AnyMessage], operator.add]
    user_query: str
    origin: str
    destination: str
    days: int
    flight_result: str
    hotel_result: str
    itinerary_result: str
    llm_calls: int