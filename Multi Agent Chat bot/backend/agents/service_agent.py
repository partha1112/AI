import asyncio
from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters, stdio_client
from langgraph.prebuilt import create_react_agent


server_params = StdioServerParameters(
    command="python",
    args=["mcp/service_server.py"]
)

server_params_transfer = StdioServerParameters(
    command="python",
    args=["mcp/transfer_server.py"]
)


async def invoke_service(state: AgentSate):
    user_message = state.user_message_unmasked or state.user_message

    prompt = f"""You are a helpful service specialist.
    Your job is to analyze the user input and respond with the service information requested by the coordinator.

    coordinator_response = {state.coordinator_response}
    user_message = {user_message}
    account_number = {state.account_number}

    Important instructions:
    - If the user explicitly requests moving money between accounts, call the MCP tool `transfer_amount(from_acc:int, to_acc:int, amount:float)`.
        Provide exact numeric account IDs and a positive amount when invoking the tool.
    - Only call `transfer_amount` when the user asks to perform a transfer; do not call it for balance inquiries or other service requests.
    - After calling the tool, return a brief confirmation summarizing the result (success or error). Do not display full account numbers in the final message—mask them (e.g., show last 4 digits) or summarize.
    - For non-transfer service requests, answer using available account/service information without invoking transfer tools.
    - If required details are missing (from/to account numbers or amount), ask a concise clarifying question instead of attempting a transfer.

    Follow these rules and produce a concise, user-facing response.
    """

    async with stdio_client(server_params) as (read1, write1):
        async with stdio_client(server_params_transfer) as (read2, write2):
            async with ClientSession(read1, write1) as session1:
                async with ClientSession(read2, write2) as session2:
                    await session1.initialize()
                    await session2.initialize()

                    tools1 = await load_mcp_tools(session1)
                    tools2 = await load_mcp_tools(session2)

                    tools = tools1 + tools2
                    agent = create_react_agent(llm, tools)
                    response = await agent.ainvoke({"messages": [("user", prompt)]})
                    final_message = response["messages"][-1].content

    print("service response : " + final_message)

    return {
        "service_response": [final_message],
        "current_response": {"service_response": final_message}
    }