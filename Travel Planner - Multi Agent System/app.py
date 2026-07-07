import streamlit as st
import uuid
from backend import run_travel_planner, get_travel_state, resume_travel_planner

st.set_page_config(page_title="AI Travel Planner", page_icon="✈️", layout="centered")

st.title("🌍 AI Travel Planner")
st.markdown("Plan your next trip with the power of Multi-Agent AI!")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

# Fetch current graph state
try:
    current_state = get_travel_state(st.session_state.session_id)
except Exception:
    current_state = None

# Determine if we are waiting for human approval
is_paused = current_state and current_state.next and "response_agent" in current_state.next

if is_paused:
    st.info("The agent has drafted an itinerary for you. Please review and confirm it below.")
    itinerary = current_state.values.get("itinerary_result", "No itinerary found.")
    st.markdown("### Draft Itinerary")
    st.markdown(itinerary)
    
    if st.button("Confirm & Generate Final Plan ✅"):
        with st.spinner("Generating final polished plan..."):
            resume_travel_planner(st.session_state.session_id)
            st.rerun()
            
elif current_state and not current_state.next and current_state.values.get("itinerary_result") and len(current_state.values.get("message", [])) >= 2:
    # The graph is finished
    st.success("Your trip is ready!")
    final_message = current_state.values.get("message", [])[-1].content
    st.markdown("---")
    st.markdown(final_message)
    
    if st.button("Plan a New Trip"):
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()

else:
    # Initial state
    with st.form("travel_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            origin = st.text_input("Origin Country", placeholder="e.g. USA, UK, India")
        
        with col2:
            destination = st.text_input("Destination Country", placeholder="e.g. France, Japan")
            
        days = st.number_input("Number of Days", min_value=1, max_value=30, value=7, step=1)
        
        submit_button = st.form_submit_button("Plan My Trip 🚀")

    if submit_button:
        if not origin or not destination:
            st.error("Please provide both an origin and a destination!")
        else:
            with st.spinner("Our AI agents are building your itinerary. This may take a moment..."):
                try:
                    run_travel_planner(origin, destination, days, st.session_state.session_id)
                    st.rerun()
                except Exception as e:
                    st.error(f"An error occurred: {e}")
