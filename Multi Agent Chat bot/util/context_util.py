from langsmith._internal._embedding_distance import cosine_similarity
from backend.agents.GeneralState import AgentSate
from typing import List
from sentence_transformers import SentenceTransformer
import os


model_dir = r"C:\Users\Dell\AI_projects\Multi Agent Chat bot\all-MiniLM-L6-v2"

if os.path.exists(model_dir):
    model = SentenceTransformer(model_dir)
else:
    model = SentenceTransformer("all-MiniLM-L6-v2")
    model.save(model_dir)

CONTEXT_MAX_TOKEN_SIZE = 1000


def check_context_size(context : str) -> str:
    if len(context) < 1:
        return False
    token_count = sum(len(text.split()) for text in context)
    if token_count > CONTEXT_MAX_TOKEN_SIZE:
        return True
    return False

    
def context_score(context : List[str], state : AgentSate) -> str:
    revised_context = []
    user_message = state.user_message
    user_message_encoded = model.encode(user_message)
    for index, text in enumerate(context):
        text_encoded = model.encode(text)
        relevence_score = cosine_similarity([user_message_encoded], [text_encoded])[0][0]
        recency_score = 1 / (index + 1)
        total_score = relevence_score + recency_score
        if total_score > 0.5:
            revised_context.append(text)

    return revised_context

        
    
        