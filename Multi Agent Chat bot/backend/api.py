
from datetime import datetime
from backend.memory.Session import Session
from backend.memory.session_update import get_session, create_session, update_session
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import random
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

from backend.schemas import ChatResponse, ChatRequest
from backend.agents.graphBuilder import get_workflow
from langchain_core.messages import HumanMessage

workflow_app = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global workflow_app
    workflow_app = await get_workflow()
    yield

app = FastAPI(lifespan=lifespan)

@app.post("/chatbot")
async def chat(request: ChatRequest):
    thread_id = request.thread_id
    if not thread_id:
        thread_id = str(random.randint(1000, 9999))

    session = get_session(thread_id)
    
    if session and session.last_activity:
        last_activity_time = (datetime.now() - session.last_activity).total_seconds() 
        if last_activity_time > 3600:
            session.status = "INACTIVE"
            thread_id = str(random.randint(1000, 9999))
            update_session(session.status, datetime.now(), thread_id)
    
    if not session or session.status == "INACTIVE":
        session = create_session(Session(session_id=thread_id, account_id=request.account_number, status="ACTIVE", crearted_at=datetime.now(), last_activity=datetime.now()))

    try:
        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        input_state = {
            "user_message": request.message,
            "account_number": request.account_number,
            "current_response": {},
            "thread_id": thread_id,
            "messages": [HumanMessage(content=request.message, name="USER")]
        }

        result = await workflow_app.ainvoke(input_state, config=config)

        messages = result["coordinator_response"]

        return ChatResponse(response=messages, thread_id=thread_id)
    except Exception as e:
        import traceback
        return ChatResponse(
            response=traceback.format_exc(),
            thread_id=thread_id
        )

if __name__ == "__main__":
    uvicorn.run("backend.api:app", host="0.0.0.0", port=8000, reload=True, loop="asyncio")