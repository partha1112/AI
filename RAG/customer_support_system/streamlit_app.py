import streamlit as st
import requests

st.set_page_config(page_title="Customer Support Assistant", layout="centered")

st.title("🛡️ Customer Support Resolution Finder")
st.write("Enter the details of the support ticket below to find a recommended resolution based on past tickets.")

with st.form("ticket_form"):
    product = st.text_input("Product", placeholder="e.g., Web Portal, Mobile App")
    category = st.text_input("Category", placeholder="e.g., Account Suspension, Performance Issue")
    issue_description = st.text_area("Issue Description", placeholder="Describe the issue the customer is facing...")
    
    submitted = st.form_submit_button("Find Resolution")

if submitted:
    if not product or not category or not issue_description:
        st.warning("Please fill in all the fields before searching.")
    else:
        with st.spinner("Searching knowledge base for similar tickets..."):
            try:
                # Send the POST request to the FastAPI backend
                response = requests.post(
                    "http://localhost:8000/search",
                    json={
                        "product": product,
                        "category": category,
                        "issue_description": issue_description
                    }
                )
                
                if response.status_code == 200:
                    st.success("Resolution found!")
                    st.write("### Recommended Resolution")
                    
                    # The backend currently returns the raw string response from LLM
                    resolution = response.json()
                    st.info(resolution)
                else:
                    st.error(f"Error from server: {response.status_code}")
                    st.write(response.text)
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend server. Make sure your FastAPI server is running on localhost:8000!")
