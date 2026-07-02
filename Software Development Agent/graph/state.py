from typing import TypedDict

class AgentState(TypedDict):
    user_request: str
    analyzed_request: str
    execution_plan: str
    generated_response: str

    