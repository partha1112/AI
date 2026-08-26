from backend.memory.episode import Episode
from langchain_protocol import Literal
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    thread_id: str = None
    account_number : str

class ChatResponse(BaseModel):
    response: str
    thread_id: str

class RouteResponse(BaseModel):
    next_agent: Literal["accounts","transactions","service","FINISH"]
    instructions:str
    transaction_status: Literal["completed","not_completed"]

class ScopeModel(BaseModel):
    label: Literal['VALID_SCOPE','OUT_OF_SCOPE']

class SummarizeSchema(BaseModel):
    summary: Episode
