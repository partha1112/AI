from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from os import getenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=getenv("OPENAI_API_KEY")
)

def invoke_llm(context,query):
    prompt = f"""
You are a customer support assistant.

Based on the provided Context (which contains similar past tickets), extract and provide the most appropriate resolution for the given Question. 
Output ONLY the recommended resolution and nothing else.

Context:
{context}

Question:
{query}

Recommended Resolution:
"""
    response = llm.invoke(prompt)

    print(response.content)

    return response.content    