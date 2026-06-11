import pickle
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from sentence_transformers import CrossEncoder

load_dotenv()

reranker = CrossEncoder(
    "cross-encoder/ms-marco-MiniLM-L-6-v2"
)

current_dir = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(current_dir, 'embeddings.pkl'), 'rb') as f:
    embeddings = pickle.load(f)

with open(os.path.join(current_dir, 'bm25.pkl'), 'rb') as f:
    bm25 = pickle.load(f)

with open(os.path.join(current_dir, 'documents.pkl'), 'rb') as f:
    documents = pickle.load(f)

pc = Pinecone(
    api_key=os.getenv('PINECONE_API_KEY')
)

index = pc.Index('support-rag-openai')


def hybrid_search(query, top_k=5, alpha=0.5):
    
    # Dense search
    query_vector=embeddings.embed_query(query)

    dense_result = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True
    )
    dense_docs = [match['metadata']['text'] for match in dense_result['matches']]
    # Sparse search BM25 
    sparse_docs = bm25.get_top_n(
        query.lower().split(),
        documents,
        n=5
    )

    # combine both results
    combined_docs = list(
        dict.fromkeys(dense_docs + sparse_docs)
    )

    return combined_docs[:top_k]

    
def reranke_context(query, documents, top_k=3):
    pairs = []

    for doc in documents:
        pairs.append(
            (query, doc)
        )

    scores = reranker.predict(pairs)
    scored_docs = list(zip(documents, scores))
    scored_docs.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return scored_docs[:top_k]
    
    
        
        
    

    

   