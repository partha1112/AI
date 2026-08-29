from typing import Annotated, Optional, Dict
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentSate(BaseModel):
    user_message: str
    account_number: int
    user_message_unmasked: Optional[str] = None
    messages: Annotated[list[BaseMessage], add_messages] = []
    next_node: Optional[str] = None 
    current_response: Optional[Dict[str, str]] = None
    thread_id: Optional[str] = None
    coordinator_response: Optional[str] = None

