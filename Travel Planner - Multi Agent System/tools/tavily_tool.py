from tavily import TavilyClient
from dotenv import load_dotenv
import os
load_dotenv()


tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search(query):
    response = tavily_client.search(query=query,max_results=5)
    result = []


    for r in response["results"]:
        result.append(f"""
        Title: {r["title"]}
        Content: {r["content"]}
        URL: {r["url"]}
        
        """)

    return result
    



