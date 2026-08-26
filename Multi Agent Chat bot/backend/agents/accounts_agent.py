import asyncio
from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters, stdio_client
from langgraph.prebuilt import create_react_agent


server_params = StdioServerParameters(
    command="python",
    args=["mcp/accounts_server.py"]
)


async def invoke_accounts(state: AgentSate):
    prompt = f"""You are a helpful accounts specialist.
    Your job is to analyze the user input and provide the requested accounts information.
    Use the coordinator instructions and the user message to decide the best response.

    coordinator_response = {state.coordinator_response}
    user_message = {state.user_message_unmasked}
    account_number ={state.account_number}

    If you cannot access actual account data, do not ask the coordinator for the current balance.
    Instead, provide a safe answer or ask the user for the missing detail directly.
    """

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm, tools)
            response = await agent.ainvoke({"messages": [("user", prompt)]})
            final_message = response["messages"][-1].content

    return {
        "accounts_response": [final_message],
        "current_response": {"accounts_response": final_message}
    }