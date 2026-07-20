from agents.agent import guardrail_middleware


def test_guardrail_blocks_invalid_state():
    def fake_node(state):
        return {"flight_result": "ok"}

    guarded = guardrail_middleware(fake_node)
    result = guarded(
        {
            "user_query": "",
            "origin": "",
            "destination": "",
            "days": 0,
            "flight_result": "",
            "hotel_result": "",
            "itinerary_result": "",
            "llm_calls": 0,
        }
    )

    assert result["guardrail_status"] == "blocked"
    assert "Guardrail blocked" in result["guardrail_message"]


def test_guardrail_allows_valid_state():
    def fake_node(state):
        return {"flight_result": "ok"}

    guarded = guardrail_middleware(fake_node)
    result = guarded(
        {
            "user_query": "Plan a trip to Paris from London for 3 days",
            "origin": "London",
            "destination": "Paris",
            "days": 3,
            "flight_result": "",
            "hotel_result": "",
            "itinerary_result": "",
            "llm_calls": 0,
        }
    )

    assert result["guardrail_status"] == "passed"
    assert result["flight_result"] == "ok"
