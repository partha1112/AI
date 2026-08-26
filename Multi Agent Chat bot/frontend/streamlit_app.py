import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bank Agentic Chatbot",
    page_icon="🏦",
    layout="centered",
)

st.title("🏦 Bank Agentic Chatbot")
st.caption("Powered by the Coordinator Agent")

# ── Session state ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of {"role": "user"|"assistant", "content": str}

# ── Render existing chat history ──────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Chat input ────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Type your message…"):
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call the FastAPI server
    try:
        api_response = requests.post(
            "http://127.0.0.1:8000/chatbot",
            json={"message": prompt}
        )
        api_response.raise_for_status()
        data = api_response.json()
        
        # FastAPI returns a ChatResponse schema where "response" contains the workflow output
        res_data = data.get("response", "")
        # Since the workflow state might be returned as a dict/string, format it nicely
        if isinstance(res_data, dict):
            # Try to get one of the agent responses if available
            response = (
                res_data.get("service_response") or 
                res_data.get("accounts_response") or 
                res_data.get("transaction_response") or 
                str(res_data)
            )
        else:
            response = str(res_data)
            
    except Exception as e:
        response = f"**Error reaching backend API:** `{e}`"

    # 3. Show assistant message
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
