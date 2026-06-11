from service.llm import invoke_llm
from service.hybridsearch import hybrid_search, reranke_context
from fastapi import FastAPI
from pydantic import BaseModel

class TicketQuery(BaseModel):
    product: str
    category: str
    issue_description: str

app = FastAPI()

@app.post("/search")
def process_query(query: TicketQuery):
    # Construct the search string just like how it is stored in the vector DB
    search_query = f"Product: {query.product}\n\nCategory: {query.category}\n\nIssue Description:\n{query.issue_description}"

    context = hybrid_search(search_query)
    top_docs = reranke_context(search_query, context)
    
    response = invoke_llm(top_docs, search_query)

    return response