from service.regx_processor import classify
from service.model_processor import classify_logs_with_model
from service.llm_processor import classify_logs_with_llm
from service.email_notifier import send_security_alert_email
import pandas as pd

def classify_logs(log_list:list)->list[str]:
    response=[]
    label = str()
    for log in log_list:
        label = (regx_classifier(log))
        print("Regx Label",label)

        if label == "UNKNOWN" :
            label = classify_logs_with_model(log)
            print("Model Label",label)

        if label == "UNKNOWN" :
            label = classify_logs_with_llm(log)
            print("LLM Label",label)

        response.append(label)

    return response


    

def regx_classifier(log_message: str) -> dict:
    label=  (classify(log_message))
    if label is None:
        return "UNKNOWN"
    return label

def csv_classifier(file):
    df = pd.read_csv(file)
    
    if "source" not in df.columns or "log_message" not in df.columns:
        raise ValueError("CSV must contain 'source' and 'log_message' columns")

    df["label_predcited"] = classify_logs(df["log_message"])
    
    security_logs = df[df["label_predcited"] == "SECURITY_ALERT"]["log_message"].tolist()
    
    if security_logs:
        send_security_alert_email(security_logs)
            
    return df
    

if __name__ == "__main__":
    results = csv_classifier("testdata.csv")
    print(results)