import json
import os
from pathlib import Path
from typing import Any

from backend import get_travel_state, resume_travel_planner, run_travel_planner


EVAL_CASES = [
    {
        "name": "budget_goa_trip",
        "origin": "India",
        "destination": "Goa",
        "days": 3,
    },
    {
        "name": "family_paris_trip",
        "origin": "India",
        "destination": "Paris",
        "days": 5,
    },
]


def _extract_text(result: dict[str, Any]) -> str:
    messages = result.get("message", []) or result.get("messages", [])
    if not messages:
        return ""

    last_message = messages[-1]
    if hasattr(last_message, "content"):
        return str(last_message.content)
    return str(last_message)


def run_evaluation(output_path: str | None = None) -> list[dict[str, Any]]:
    results = []

    for case in EVAL_CASES:
        session_id = f"eval-{case['name']}"
        initial_result = run_travel_planner(
            case["origin"],
            case["destination"],
            case["days"],
            session_id,
        )

        current_state = get_travel_state(session_id)
        final_result = initial_result
        if current_state and current_state.next and "response_agent" in current_state.next:
            final_result = resume_travel_planner(session_id)

        final_text = _extract_text(final_result)
        score = {
            "has_destination": case["destination"].lower() in final_text.lower(),
            "has_itinerary": "itinerary" in final_text.lower() or "day" in final_text.lower(),
            "has_hotel": "hotel" in final_text.lower() or "stay" in final_text.lower(),
            "has_flight": "flight" in final_text.lower() or "travel" in final_text.lower(),
            "llm_calls": final_result.get("llm_calls", 0),
        }

        result_entry = {
            "name": case["name"],
            "origin": case["origin"],
            "destination": case["destination"],
            "days": case["days"],
            "score": score,
            "preview": final_text[:1200],
        }
        results.append(result_entry)

    if output_path:
        Path(output_path).write_text(json.dumps(results, indent=2), encoding="utf-8")

    return results


if __name__ == "__main__":
    output_path = os.getenv("EVAL_OUTPUT", "eval_results.json")
    results = run_evaluation(output_path)
    print(json.dumps(results, indent=2))
