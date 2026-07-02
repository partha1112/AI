from graph.state import AgentState
from graph.llm import llm

def developer_agent(state : AgentState):
    prompt = f"""
    You are a Senior Java Engineer.
    Provide code for the requirements given bellow.
    
    Requirements: {state["execution_plan"]}
    
    Provide code in string so that it will be extracted eassyly and added to any IDE

    """

    response = llm.invoke(prompt)

    print(f"developer_agent resp : {response.content}")

    return {
        "generated_response" : response.content
    }