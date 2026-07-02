from graph.llm import llm
from graph.state import AgentState

def analyze_request(state : AgentState):
    prompt = f""" you are an experienced software Architect
    Analyze the following request

    Request: {state["user_request"]}

    Then rewrite the request clearly.
    """

    response = llm.invoke(prompt)

    # print(f"analyze_request resp : {response.content}")

    return{
        "analyzed_request" : response.content
    }

