# RAG with Hybrid Search

This project demonstrates how to implement **Hybrid Search** using Pinecone vector database and HuggingFace embeddings.

## What is Hybrid Search?

Hybrid search is a retrieval technique that combines two powerful search methods to deliver the best possible results:

1. **Dense Vector Search (Semantic Search)**
   - Uses machine learning models (like sentence-transformers) to understand the *meaning* and *context* of a query.
   - Good for: Finding relevant information even if the exact keywords are not used (e.g., matching "vacation" with "holiday").
   - In this project, we use the `all-MiniLM-L6-v2` model from HuggingFace to generate 384-dimensional dense vectors.

2. **Sparse Vector Search (Keyword Search)**
   - Uses traditional information retrieval algorithms (like BM25) to match exact keywords and their frequencies.
   - Good for: Finding specific terms, names, IDs, or domain-specific jargon that semantic models might gloss over.
   - In this project, we use Pinecone's `BM25Encoder` to generate sparse vectors.

By combining both, Hybrid Search ensures that results are both contextually relevant and highly precise.

## How it Works in Pinecone

Pinecone allows you to store both dense and sparse vectors in the same index record. When querying, you provide both a dense query vector and a sparse query vector.

The combination is controlled by an **`alpha`** parameter (ranging from 0.0 to 1.0) which weights the importance of each search type:

- `alpha = 1.0`: Pure semantic search (dense vectors only).
- `alpha = 0.0`: Pure keyword search (sparse vectors only).
- `alpha = 0.5`: A balanced hybrid search, giving equal weight to semantic meaning and exact keyword matches.

### The Pipeline

1. **Embedding Generation**: We fit a BM25 encoder on our text corpus to learn term frequencies. Then, we generate dense vectors using our HuggingFace model and sparse vectors using our fitted BM25 encoder.
2. **Upsertion**: We package the text ID, dense vector, sparse vector, and original text (as metadata) together and upsert them into Pinecone using keyword arguments (required for Pinecone SDK v5+).
3. **Querying**: When a user asks a question, we encode the question into both dense and sparse vectors, scale them according to the `alpha` parameter, and send them to Pinecone to retrieve the top matching documents.

## Setup and Installation

1. Create a virtual environment and install the dependencies:
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```
   *Note: Ensure you have installed the required packages like `pinecone-client`, `pinecone-text`, `langchain-huggingface`, and `python-dotenv`.*

2. Create a `.env` file in this directory and add your Pinecone API key:
   ```env
   PINECONE_API_KEY=your_pinecone_api_key_here
   ```

3. Open and run the `1.2_RAG_Hybrid_Search.ipynb` Jupyter Notebook to see the hybrid search in action.
