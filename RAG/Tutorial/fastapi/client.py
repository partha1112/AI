import requests
import streamlit as st

def get_funny_response(input_text):
    url = "http://localhost:8000/funny/invoke"
    response = requests.post(url, json={ "input": { "topic": input_text}})
    return response

def get_serious_response(input_text):
    url = "http://localhost:8000/serious/invoke"
    response = requests.post(url, json={ "input": { "topic": input_text}})
    return response

st.title("Rag with FastAPI")
input_text1 = st.text_input("Enter the topic for Funny Response")
input_text2 = st.text_input("Enter the topic for Serious Response")

if input_text1:
    response = get_funny_response(input_text=input_text1)
    st.write(response.json()["output"] ["content"])
    

if input_text2:
    response = get_serious_response(input_text=input_text2)
    st.write(response.json()["output"] ["content"])