from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm
from backend.schemas import SummarizeSchema
from datetime import date
from sentence_transformers import SentenceTransformer
from backend.memory.vector_store import get_index
from uuid import uuid4



embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

llm_with_episode_structure = llm.with_structured_output(SummarizeSchema, method="function_calling")

index = get_index()

def sumarize_episode(state : AgentSate):
    prompt = f"""You are a summarization agent. Your task is to summarize the following conversation history and state into a very simple 1 or 2 line summary. This summary will be stored in a vector database.

    State Details:
    User Message: {state.user_message}
    Account Number: {state.account_number}
    Accounts Response History: {state.accounts_response}
    Transaction Response History: {state.transaction_response}
    Service Response History: {state.service_response}
    Coordinator Response History: {state.coordinator_response}
    Current Response: {state.current_response}

    Create an episode summary using the provided details. 
    - Use the user's account number for 'user_id'.
    - Use state.thread_id for 'thread_id'.
    - Use date {date.today().isoformat()} for the 'date'.
    - 'event_type' should be the general category of the user's request (e.g., balance inquiry, transaction).
    - 'outcome' should indicate if the request was resolved or is pending.
    - meta data : add bellow deatils
        - amount: transaction amount/balance,
        - service_type : which service agent invoked based onthe response available in the state
        - other details : like email if it's updated, address of its updated. Need to add the entity which is updated. For balance check don't add this
    """

    response = llm_with_episode_structure.invoke(prompt)

    print(f"summarize_agent Response : {response.summary}")

    episode_data = response.summary
    vector = get_embedding(episode_data.summary)

    
    metadata_payload = {
        "thread_id": state.thread_id,
        "summary": episode_data.summary,
        "account_number": state.account_number,
        "date": date.today().isoformat(),
        "event_type": episode_data.event_type,
        "outcome": episode_data.outcome
    }
    if episode_data.metadata:
        metadata_payload.update(episode_data.metadata)

    res = index.upsert(
        vectors=[{
            "id": str(uuid4()),
            "values": vector,
            "metadata": metadata_payload
        }]
    )


    print(res)

    return res

    

def  get_embedding(text):
    response = embedding_model.encode(text)
    return response.tolist()

