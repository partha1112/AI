from backend import run_travel_planner

res= run_travel_planner("usa","india",7, "test_session_1")

print("\n")
print(res["message"][-1].content)