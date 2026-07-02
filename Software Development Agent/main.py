import streamlit as st
from graph.builder import build_graph

if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "config" not in st.session_state:
    st.session_state.config = {"configurable": {"thread_id": "1"}}
if "plan_generated" not in st.session_state:
    st.session_state.plan_generated = False

st.title("Software Development Agent")

user_request = st.text_area(
    "Enter your request:", 
    value="Example : Build a java application to find the square root of a number"
)

if st.button("Generate Plan"):
    initial_state = {"user_request": user_request}
    with st.spinner("Analyzing request and generating plan..."):
        current_state = st.session_state.graph.invoke(initial_state, st.session_state.config)
        
    st.session_state.plan_generated = True
    st.session_state.plan = current_state.get("execution_plan", "No plan generated.")

if st.session_state.plan_generated:
    st.subheader("Generated Plan")
    st.markdown(st.session_state.plan)
    
    st.warning("The plan has been generated. Do you want to proceed with execution?")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, Proceed"):
            with st.spinner("Executing plan..."):
                final_state = st.session_state.graph.invoke(None, st.session_state.config)
            
            st.success("Execution Complete!")
            st.subheader("Final Result")
            st.markdown(final_state.get("generated_response", "No response generated."))
            
            # Reset state for next request
            st.session_state.plan_generated = False
            
    with col2:
        if st.button("No, Abort"):
            st.error("Execution aborted for security reasons.")
            # Reset state
            st.session_state.plan_generated = False