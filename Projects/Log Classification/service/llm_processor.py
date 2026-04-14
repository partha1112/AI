import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

llm_groq = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def classify_logs_with_llm(logs):
    
    prompt = f"""
    You are a log classification expert. Your task is to classify the given log message into one of the following categories:
    - HTTP_STATUS
    - USER_ACTION
    - SECURITY_ALERT
    - ERROR
    - CRITICAL_ERROR
    - RESOURCE_USAGE
    - SYSTEM_NOTIFICATION
    - DEPRECATION_WARNING
    - WORKFLOW_ERROR
    
    If you are unable to classify the log message, return "UNKNOWN".

    Log message: {logs}

    Note : Return only the category name. No preambele. No explanation. No extra text.
    """

    response = llm_groq.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response.choices[0].message.content.strip()
