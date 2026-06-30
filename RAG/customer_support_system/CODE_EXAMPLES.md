# Code Examples - Customer Support RAG System

## 1. Hybrid Search Implementation

**File: service/hybridsearch.py**

```python
def hybrid_search(query, top_k=5):
    # Dense search using vector embeddings
    query_vector = embeddings.embed_query(query)
    dense_result = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True
    )
    dense_docs = [match['metadata']['text'] for match in dense_result['matches']]
    
    # Sparse search using BM25
    sparse_docs = bm25.get_top_n(
        query.lower().split(),
        documents,
        n=5
    )
    
    # Combine results, removing duplicates
    combined_docs = list(dict.fromkeys(dense_docs + sparse_docs))
    return combined_docs[:top_k]
```

## 2. LLM Integration

**File: service/llm.py**

```python
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    api_key=getenv("OPENAI_API_KEY")
)

def invoke_llm(context, query):
    prompt = f"""You are a customer support assistant.
    
Based on the provided Context, extract and provide the most appropriate resolution.
Output ONLY the recommended resolution.

Context:
{context}

Question:
{query}

Recommended Resolution:"""
    
    response = llm.invoke(prompt)
    return response.content
```

## 3. FastAPI Controller

**File: controller.py**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from service.llm import invoke_llm
from service.hybridsearch import hybrid_search, reranke_context

class TicketQuery(BaseModel):
    product: str
    category: str
    issue_description: str

app = FastAPI()

@app.post("/search")
def process_query(query: TicketQuery):
    search_query = f"Product: {query.product}\n\nCategory: {query.category}\n\nIssue Description:\n{query.issue_description}"
    
    context = hybrid_search(search_query)
    top_docs = reranke_context(search_query, context)
    response = invoke_llm(top_docs, search_query)
    
    return response
```

## 4. Reranking with Cross-Encoder

**File: service/hybridsearch.py**

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

def reranke_context(query, documents, top_k=3):
    pairs = [(query, doc) for doc in documents]
    
    scores = reranker.predict(pairs)
    scored_docs = list(zip(documents, scores))
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    
    return scored_docs[:top_k]
```

## 5. Performance Evaluation

**File: service/evaluation.py**

```python
import time

class RetrievalEvaluator:
    def measure_retrieval_time(self, query, top_k=5):
        start_time = time.time()
        
        retrieved_docs = hybrid_search(query, top_k=top_k)
        reranked_docs = reranke_context(query, retrieved_docs, top_k=3)
        
        total_time = (time.time() - start_time) * 1000  # Convert to ms
        
        # Calculate relevance scores
        relevance_scores = {}
        if reranked_docs:
            scores = [doc[1] for doc in reranked_docs]
            relevance_scores = {
                'avg_relevance': round(sum(scores) / len(scores), 4),
                'max_relevance': round(max(scores), 4),
                'min_relevance': round(min(scores), 4)
            }
        
        return {
            'reranked_docs': reranked_docs,
            'total_time_ms': round(total_time, 2),
            'relevance_scores': relevance_scores
        }
```

## 6. Streamlit UI

**File: streamlit_app.py**

```python
import streamlit as st
import requests

st.set_page_config(page_title="Customer Support Assistant")
st.title("Customer Support Resolution Finder")

with st.form("ticket_form"):
    product = st.text_input("Product")
    category = st.text_input("Category")
    issue_description = st.text_area("Issue Description")
    submitted = st.form_submit_button("Find Resolution")

if submitted and all([product, category, issue_description]):
    with st.spinner("Searching knowledge base..."):
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
            st.info(response.json())
```

## 7. Evaluation Script

**File: evaluate.py**

```python
from service.evaluation import evaluator

def run_evaluation():
    test_queries = [
        "Product: Web Portal\n\nCategory: Account Suspension\n\nIssue Description: User account was suspended",
        "Product: Mobile App\n\nCategory: Performance Issue\n\nIssue Description: App is slow",
    ]
    
    for i, query in enumerate(test_queries, 1):
        result = evaluator.measure_retrieval_time(query)
        print(f"Query {i}: {result['total_time_ms']} ms")
        print(f"Avg Relevance: {result['relevance_scores'].get('avg_relevance')}")

if __name__ == "__main__":
    run_evaluation()
```

## Key Concepts Demonstrated

1. **Hybrid Search**: Combining dense (vector) and sparse (keyword) approaches
2. **Reranking**: Using cross-encoders for relevance scoring
3. **LLM Integration**: Leveraging GPT-4 for resolution generation
4. **API Design**: Clean FastAPI endpoints with type validation
5. **Evaluation**: Measuring retrieval time and accuracy metrics
6. **Frontend**: User-friendly Streamlit interface
