from typing import Literal
from backend.agents.llm import llm
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI


class ModelRoute(BaseModel):
    model_tier: Literal["low", "high"] = Field(
        description="Model tier required to handle the user query"
    )


structured_router = llm.with_structured_output(ModelRoute)


def invoke_model_router(state):
    user_query = state["user_message"]

    prompt = f"""
    You are a model-routing classifier for a banking chatbot.

    Select LOW for:
    - Account balance inquiries
    - Simple transaction lookups
    - Banking FAQs
    - Straightforward service requests

    Select HIGH for:
    - Multi-step financial analysis
    - Comparing transactions or spending trends
    - Complex troubleshooting
    - Requests requiring substantial reasoning across multiple steps

    Select the least expensive model tier capable of handling
    the request.

    Security-sensitive operations must always follow the required
    authentication, authorization, and confirmation procedures,
    regardless of the selected model.

    User query: {user_query}

    Return the model tier using the required structured output.
    """

    decision = structured_router.invoke(prompt)

    return {
        "model_tier": decision.model_tier
    }