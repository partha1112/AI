from langsmith import traceable
import asyncio
from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters, stdio_client
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AIMessage
import os

async def invoke_accounts(state: AgentSate):

    server_params = StdioServerParameters(
    command="python",
        args=["mcp/accounts_server.py"],
        env={
        **os.environ,
        "CUSTOMER_ACCOUNT_NUMBER": str(state.account_number)
        }   
    )

    prompt = f"""You are a helpful accounts specialist.
    Your job is to analyze the user input and provide the requested accounts information.
    Use the coordinator instructions and the user message to decide the best response.

    coordinator_response = {state.coordinator_response}
    account_number = CUSTOMER_ACCOUNT_NUMBER

    Use CUSTOMER_ACCOUNT_NUMBER to refer to the user's account number.

    The customer's account information is available through the accounts tool.
    Do not ask the customer for an account number.
    """

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm, tools)
            response = await agent.ainvoke({"messages": [("user", prompt)]})
            final_message = response["messages"][-1].content

    return {
        "messages": [AIMessage(content=final_message, name="ACCOUNTS")],
        "current_response": {"ACCOUNTS": final_message}
    }