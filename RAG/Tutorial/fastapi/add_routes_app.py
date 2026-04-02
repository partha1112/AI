from fastapi  import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langserve import add_routes
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in environment variables")
else:
    print("OPENAI_API_KEY found")
    

app = FastAPI(
    title="LangChain Demo",
    version="1.0",
    description="LangChain Demo"
)

model = ChatOpenAI(api_key=api_key)

funny_chain = ChatPromptTemplate.from_template("tell me a joke about {topic}") | model

serious_chain = ChatPromptTemplate.from_template("tell me something serious about {topic}") | model

add_routes(
    app,
    funny_chain,
    path="/funny"
)

add_routes(
    app,
    serious_chain,
    path="/serious"
)



if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)

