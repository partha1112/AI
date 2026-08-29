from transformers import pipeline
from backend.agents.llm import llm
from backend.schemas import ScopeModel

class PromptInjectionException(Exception):
    pass

class OutOfScopeExcepton(Exception):
    pass

import os
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

model_dir = r"C:\Users\Dell\AI_projects\Multi Agent Chat bot\deberta-prompt-injection"
model_name = "protectai/deberta-v3-base-prompt-injection-v2"

if os.path.exists(model_dir):
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    model = AutoModelForSequenceClassification.from_pretrained(model_dir)
    classifier = pipeline("text-classification", model=model, tokenizer=tokenizer)
else:
    classifier = pipeline("text-classification", model=model_name)
    classifier.model.save_pretrained(model_dir)
    classifier.tokenizer.save_pretrained(model_dir)

def validate_input(text: str):
    if "my account number" in text.lower():
        return "SAFE"
    res = classifier(text)[0]
    print(res)
    label = res['label']
    if label == "INJECTION":
        raise PromptInjectionException(
            "Prompt injection detected. Request blocked."
        )

llm = llm.with_structured_output(ScopeModel)

def scop_validation(text: str):
    prompt = f"""
    you are a useful agent who will validate the user message and find if the content is out of scopt of this project
    This project is a Banking Project which will do the bellow operations
    - Accounts information
    - Accounts Management/service
    - Transaction Management
    If you receive any queries related to the above mentioned topics then respond with the label as 'VALID_SCOPE'
    If you receive any queries out of this topics then mark it as 'OUT_OF_SCOPE'
    user prompt : {text}
    """

    response = llm.invoke(prompt)

    if response.label == "OUT_OF_SCOPE":
        raise OutOfScopeExcepton(
            "The request received from the user is OUT OF SCOPE"
        )