import os
import sys

# Add parent directory to standard path so 'service' module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import HTTPException
import fastapi
from fastapi import UploadFile
from fastapi.responses import FileResponse
from service.clasify_logs import csv_classifier

app = fastapi.FastAPI()

@app.post("/classify")
def classify_logs(file: UploadFile):

    try:    
        dataframe = csv_classifier(file.file)
        file_path = "classified_logs.csv"
        dataframe.to_csv(file_path, index=False)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return FileResponse(path=file_path, filename="classified_logs.csv", media_type="text/csv")