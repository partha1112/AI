from graph.state import AgentState
from graph.llm import llm


def planer_agent(state : AgentState):
    prompt = f"""
    You are a Senior Architect. Your goal is to analyze the user's request and create a structured, high-level implementation plan.

    Requirements: {state["analyzed_request"]}

    Please provide the plan in the following JSON format:
    {{
        "plan_name" : "A short descriptive name for the plan",
        "description" : "A brief overview of the implementation approach",
        "steps" : [
        ]
    }}"""

    response = llm.invoke(prompt)

    # print(f"planner_agent resp : {response.content}")

    return {
        "execution_plan" : response.content
    }