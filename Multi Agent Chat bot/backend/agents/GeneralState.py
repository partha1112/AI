from operator import add
from typing import Annotated, List, Optional, Dict
from pydantic import BaseModel, Field

class AgentSate(BaseModel):
    user_message: str
    account_number: int
    user_message_unmasked: Optional[str] = None
    accounts_response: Annotated[List[str], add] = []
    transaction_response: Annotated[List[str], add] = []
    service_response: Annotated[List[str], add] = []
    coordinator_response: Annotated[List[str], add] = []
    next_node: Optional[str] = None 
    current_response: Optional[Dict[str, str]] = None
    thread_id: Optional[str] = None
