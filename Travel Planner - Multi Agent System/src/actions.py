from nemoguardrails.actions import action

from backend import invoke_travel_graph


@action(name="run_travel_planner")
async def run_travel_planner_action(
    origin: str,
    destination: str,
    days: int,
    comments: str,
    session_id: str,
):
    return invoke_travel_graph(
        origin,
        destination,
        days,
        comments,
        session_id,
    )