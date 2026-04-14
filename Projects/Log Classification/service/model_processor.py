import joblib
import pandas as pd
import os
import numpy as np
from fastembed import TextEmbedding

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "training", "log_classifier.joblib")

if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}. Ensure the file exists.")

classifier = joblib.load(model_path)

# Initialize the embedding model used during training
embed_model = TextEmbedding(model_name="BAAI/bge-small-en")

def classify_logs_with_model(logs):   
    is_scalar = isinstance(logs, str)
    if is_scalar:
        logs = [logs]
        
    # Convert text to embeddings (2D array) required by the logistic regression model
    embeddings = np.array(list(embed_model.embed(logs)))
    
    probabilities = classifier.predict_proba(embeddings)
    #print("probabilities",probabilities)

    max_probs = np.max(probabilities, axis=1)
    print("max_probs",max_probs)

    if max_probs > 0.5:
        predictions = classifier.predict(embeddings)[0]
    else:
        predictions = "UNKNOWN"
    
    print("predictions",predictions)
    return predictions
