# Customer Support System

## Project Summary

A Retrieval-Augmented Generation (RAG) system that resolves customer support tickets by finding similar past tickets and generating solutions using AI.

## Use Case

When a customer submits a support ticket with product, category, and issue description, the system:
1. Searches a database of 200K historical tickets using hybrid search (vector + keyword)
2. Reranks results by relevance using a cross-encoder
3. Generates a solution recommendation using GPT-4 mini based on similar past resolutions

## Architecture

Components:
- Frontend: Streamlit UI (streamlit_app.py)
- Backend API: FastAPI (controller.py)
- Retrieval: Hybrid search combining Pinecone vectors and BM25 (service/hybridsearch.py)
- LLM: OpenAI GPT-4 mini for resolution generation (service/llm.py)
- Evaluation: Metrics for retrieval time and accuracy (service/evaluation.py)

Data Flow:
User Query -> Hybrid Search (Pinecone + BM25) -> Reranking (Cross-encoder) -> LLM Response

System Flow Diagram:

```
                          User Input
                              |
                              v
                    Streamlit UI / FastAPI
                              |
                              v
                     Query Construction
               (Product, Category, Description)
                              |
                              v
                    Hybrid Search Module
                              |
                    __________|__________
                   |                      |
                   v                      v
            Pinecone Vectors          BM25 Keyword
            (Dense Search)            (Sparse Search)
                   |                      |
                   |______________________|
                              |
                              v
                      Combine & Deduplicate
                       Retrieved Documents
                              |
                              v
                    Cross-Encoder Reranking
                   (Relevance Scoring)
                              |
                              v
                    Top 3 Ranked Documents
                              |
                              v
                   OpenAI GPT-4 Mini LLM
                 (Generate Resolution)
                              |
                              v
                    Final Response to User
```

## Setup

1. Install dependencies:
   pip install -r requirements.txt

2. Create .env file with:
   OPENAI_API_KEY=your_key
   PINECONE_API_KEY=your_key

3. Run API:
   uvicorn controller:app --reload

4. Run Streamlit:
   streamlit run streamlit_app.py

5. Run evaluation:
   python evaluate.py

## Performance Metrics

- Average Retrieval Time: 330-400ms
- Relevance Score: 6.7-8.2 (normalized)
- System handles 200K customer support tickets

## Files

- controller.py - FastAPI endpoints
- streamlit_app.py - User interface
- service/llm.py - LLM integration
- service/hybridsearch.py - Retrieval logic
- service/evaluation.py - Performance metrics
- evaluate.py - Batch evaluation script
