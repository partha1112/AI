import asyncio
import sys
from backend.schemas import ChatResponse
from backend.schemas import ChatRequest
from fastapi import FastAPI
from backend.agents.graphBuilder import workflow
# from backend.guardrails.input_validator import validate_input, scop_validation
import random
from util.ainvoke import resolve_ainvoke


app = FastAPI()

@app.post("/chatbot")
async def chat(request: ChatRequest):
    thread_id = request.thread_id

    if not thread_id:
        thread_id = str(random.randint(1000, 9999))


    try:
        inputs = {"user_message": request.message}
        # validate_input(request.message)
        # scop_validation(request.message)

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        # Build initial workflow state matching `AgentSate` (expects `user_message`).
        inputs = {"user_message": request.message,
                  "account_number": request.account_number,
                  "current_response":{},
                  "thread_id": thread_id}

        # Run sync workflow in a                        thread so MCP agents can create their own event loops
        res = await workflow.ainvoke(inputs, config)
 
        # Choose the first available specialist response.
        response_text = res.get("coordinator_response")[-1]

        return ChatResponse(response=response_text, thread_id=thread_id)
    except Exception as e:
        import traceback
        return ChatResponse(
            response=traceback.format_exc(),
            thread_id=thread_id
        )
