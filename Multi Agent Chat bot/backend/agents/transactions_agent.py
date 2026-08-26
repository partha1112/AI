from email import message
from backend.agents.GeneralState import AgentSate
from langgraph.graph import StateGraph, END
from backend.agents.llm import llm


from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters, stdio_client
from langgraph.prebuilt import create_react_agent
from util.ainvoke import resolve_ainvoke


server_params = StdioServerParameters(
    command="python",
    args=["mcp/transactions_server.py"]
)


async def invoke_transaction(state:AgentSate):
    prompt = f"""You are a helpful transactions specialist.
    Your job is to analyze the user input and respond with transaction history.

    Use the provided tool if transaction data is needed.
    Available tool:
    - fetch_transactions(acc_number: int, start_date: str | None = None, end_date: str | None = None)
      returns transaction history for the account and optional date range.

    coordinator_response = {state.coordinator_response}
    user_message = {state.user_message_unmasked}
    user account_number = {state.account_number}

    If the coordinator instructions or user request imply a date range, call the tool with the exact
    ISO dates from the request or instructions. Do not invent date values.
    If the request is specifically about transactions, do not answer without calling the tool.
    If the tool returns data, present the transactions clearly.
    If there are no matching transactions, state that the date range returned no records.
    """

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = create_react_agent(llm, tools)

            response = await agent.ainvoke({"messages": [("user", prompt)]})

            final_message = response["messages"][-1].content

            print("transactions response : " + final_message)
            return {
                "transaction_response": [final_message],
                "current_response": {'transaction_response': final_message}
            }
    

    
    
    
    