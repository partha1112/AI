from pinecone import Pinecone, ServerlessSpec
import os
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()


model_name = "all-MiniLM-L6-v2"
model_dir = r"C:\Users\Dell\AI_projects\Multi Agent Chat bot\all-MiniLM-L6-v2"

if os.path.exists(model_dir):
    embedding_model = SentenceTransformer(model_dir)
else:
    embedding_model = SentenceTransformer(model_name)
    embedding_model.save(model_dir)


def get_embedding(text):
    response = embedding_model.encode(text)
    return response.tolist()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "banking-episodic-memory"

if not pc.has_index(index_name):
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )

vector_store = pc.Index(index_name)

def get_index():
    return vector_store

def get_summary(query: str, user_id: str):
    res = vector_store.query(
        vector=get_embedding(query),
        top_k=20,
        include_metadata=True,
        filter={
            "account_number": {"$eq": user_id}
        }
    )

    documents = []

    if not res["matches"]:
        return None
    
    for match in res["matches"]:
        documents.append({
            "id": match["id"],
            "text": match["metadata"]["summary"]
        })

    reranked = pc.inference.rerank(
        model="bge-reranker-v2-m3",
        query=query,
        documents=documents,
        top_n=3,
        return_documents=True
    )
    

    return reranked.data