from langchain_core.messages import AIMessage
from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm

from langchain_mcp_adapters.tools import load_mcp_tools
from mcp import ClientSession, StdioServerParameters, stdio_client
from langgraph.prebuilt import create_react_agent
import os



async def invoke_service(state: AgentSate):

    env1 = {
        **os.environ,
        "CUSTOMER_ACCOUNT_NUMBER": str(state.account_number),
    }

    env2 = {}
    if state.pii_mapping:
        for key, value in state.pii_mapping.items():
            env2[str(key)] = str(value)

    env1.update(env2)

    if "EMAIL_ADDRESS_1" in env1:
        print( "EMAIL_ADDRESS_1 : " + env1["EMAIL_ADDRESS_1"])

    server_params = StdioServerParameters(
        command="python",
        args=["mcp/service_server.py"],
        env=env1
    )

    server_params_transfer = StdioServerParameters(
        command="python",
        args=["mcp/transfer_server.py"],
        env=env1
    )   

    user_message = state.user_message_masked or state.user_message

    prompt = f"""You are a helpful service specialist.
    Your job is to analyze the user input and respond with the service information requested by the coordinator.

    coordinator_response = {state.coordinator_response}
    
    Use CUSTOMER_ACCOUNT_NUMBER to refer to the user's account number.
    Use CUSTOMER_EMAIL_1 to refer to the user's email.
    

    Important instructions:
    - If the coordinator explicitly requests moving money between accounts, call the MCP tool `guarded_transfer(from_acc:CUSTOMER_ACCOUNT_NUMBER, to_acc: ACCOUNT_NUMBER_1, amount:float, approved:bool)`.
        Provide exact numeric account IDs and a positive amount when invoking the tool. Set approved=True to bypass approval, or False if approval is needed.
    - Only call `guarded_transfer` when the coordinator asks to perform a transfer; do not call it for balance inquiries or other service requests.
    - After calling the tool, return a brief confirmation summarizing the result (success or error).
    - For non-transfer service requests, answer using available account/service information without invoking transfer tools.   

    The customer's account information is available through the tool.
    Do not ask the customer for an account number. 
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
        "messages": [AIMessage(content=final_message, name="SERVICE")],
        "current_response": {"SERVICE": final_message}
    }