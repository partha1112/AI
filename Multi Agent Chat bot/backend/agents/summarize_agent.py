from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm
from backend.schemas import SummarizeSchema
from datetime import date
from sentence_transformers import SentenceTransformer
from backend.memory.vector_store import get_index
from uuid import uuid4
from backend.memory.Session import Session
import os


model_name = "all-MiniLM-L6-v2"
model_dir = r"C:\Users\Dell\AI_projects\Multi Agent Chat bot\all-MiniLM-L6-v2"

if os.path.exists(model_dir):
    embedding_model = SentenceTransformer(model_dir)
else:
    embedding_model = SentenceTransformer(model_name)
    embedding_model.save(model_dir)

llm_with_episode_structure = llm.with_structured_output(SummarizeSchema, method="function_calling")

index = get_index()

def get_embedding(text):
    response = embedding_model.encode(text)
    return response.tolist()

def sumarize_episode( state : AgentSate):
    prompt = f"""You are a summarization agent. Your task is to summarize the following conversation history and state into a very simple 1 or 2 line summary. This summary will be stored in a vector database.

    State Details:
    session details : {state.messages}

    Create an episode summary using the provided details. 
    - Use the user's account number for 'user_id'.
    - Use {state.thread_id} for 'thread_id'.
    - Use date {date.today().isoformat()} for the 'date'.
    - 'event_type' should be the general category of the user's request (e.g., balance inquiry, transaction).
    - 'outcome' should indicate if the request was resolved or is pending.
    - meta data : add bellow deatils
        - amount: transaction amount/balance,
        - service_type : which service agent invoked based onthe response available in the state
        - other_updates : like email if it's updated, address of its updated. Need to add the entity which is updated. For balance check don't add this
    """

    response = llm_with_episode_structure.invoke(prompt)

    print(f"summarize_agent Response : {response.summary}")

    episode_data = response
    vector = get_embedding(episode_data.summary.summary)

    metadata_payload = {
        "thread_id": state.thread_id,
        "summary": episode_data.summary.summary,
        "account_number": state.account_number,
        "date": date.today().isoformat(),
        "event_type": episode_data.summary.event_type,
        "outcome": episode_data.summary.outcome
    }

    res = index.upsert(
        vectors=[{
            "id": str(uuid4()),
            "values": vector,
            "metadata": metadata_payload
        }]
    )

    print(res)

    return res