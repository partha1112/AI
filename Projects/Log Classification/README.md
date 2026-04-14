# Log Classification Pipeline

## Summary
The Log Classification Pipeline is an automated machine-learning and heuristic-driven system designed to classify unstructured log messages from various sources. It processes batches of logs provided via CSV uploads and evaluates them to apply predefined labels. Critically, it acts as a security monitor, automatically identifying logs flagged as `SECURITY_ALERT` and dispatching immediate email notifications to administrators.

## High-Level Design (HLD)

The system exposes a FastAPI web service that accepts an uploaded CSV file. The CSV file must contain at a minimum `source` and `log_message` columns.

At the core of the system is a three-tiered classification architecture:

1. **Tier 1: Regular Expression Processor (`regx_processor.py`)** 
   - A fast, heuristic-based initial pass. It scans logs against known, rigid patterns to assign labels instantly. If a log matches strongly with a known structure, it returns a label. If it doesn't match any known pattern, it returns `"UNKNOWN"`.

2. **Tier 2: Machine Learning Model (`model_processor.py`)**
   - If Tier 1 returns `"UNKNOWN"`, the system falls back to a trained ML model (Logistic Regression).
   - The log text is converted into dense vector embeddings using `fastembed` (`BAAI/bge-small-en`).
   - The model predicts the probability of various labels. If the maximum probability exceeds a 50% confidence threshold, that label is returned. Otherwise, it again falls back, returning `"UNKNOWN"`.

3. **Tier 3: Large Language Model (`llm_processor.py`)**
   - As a final catch-all for logs that are highly unstructured or anomalous, the system uses an LLM (via LangChain). The LLM reads the log text and semantic context to intelligently deduce the most appropriate log classification.

**Alerting System (`email_notifier.py`)**
Once all logs in the file have been processed through the pipeline and assigned a `label_predicted`, the system scans the results specifically for logs classified as `SECURITY_ALERT`. If any exist, it formats them and triggers an email using SMTP to notify stakeholders immediately.

Finally, the original data frame, now appended with the `label_predicted` column, is saved to disk as a CSV and streamed directly back to the API client as a file download.

## Complete Workflow Step-by-Step

1. **User Request**: Client sends a `POST` request to the `/classify` endpoint via FastAPI (`main.py`) containing a CSV file upload.
2. **Data Extraction**: The `UploadFile` is passed natively to Pandas (`service/clasify_logs.py`) which validates that the required headers (`source`, `log_message`) exist.
3. **Classification Loop**: The system iterates over every log message in the file:
   - Evaluates via **Regex Processor**.
   - If `UNKNOWN`, evaluates via **ML Processor** (creates text embeddings, applies logistic regression model).
   - If still `UNKNOWN`, evaluates via **LLM Processor**.
   - Appends the final predicted label to a list.
4. **Data Aggregation**: The list of predictions is attached to the Pandas DataFrame as a new column named `label_predicted`.
5. **Security Scanning**: The DataFrame is filtered to find any rows where the prediction equals `SECURITY_ALERT`.
6. **Notification Delivery**: If security alerts are present, `send_security_alert_email()` is invoked to batch the alerts into an HTML email.
7. **Response Generation**: The updated DataFrame is saved locally as `classified_logs.csv`. The FastAPI controller then serves this physical file back to the requester as a `FileResponse` to complete the transaction.

## Workflow Diagram

```text
+---------------------+
| Client Uploads CSV  |
+---------+-----------+
          |
          v
+---------------------+
| FastAPI Endpoint    |
|     '/classify'     |
+---------+-----------+
          |
          v
+---------------------+
| Pandas Data         |
| Validation          |
+---------+-----------+
          |
          v
+---------------------+
| Iterate over Logs   |<-------------------------+
+---------+-----------+                          |
          |                                      |
          v                                      |
+---------------------+                          |
| Tier 1: Regex       |                          |
| Match?              |-- (No) -->+              |
+---------+-----------+           |              |
          | (Yes)                 |              |
          v                       v              |
+---------------------+   +--------------------+ |
|    Assign Label     |   | Tier 2: ML Model   | |
|                     |   | Confidence > 50%?  | |
+---------+-----------+   +-------+------------+ |
          |                       | (No)         |
          |               (Yes)   v              |
          |<----------------------+              |
          |               +--------------------+ |
          |               | Tier 3: LLM        | |
          |<--------------| Processor          | |
          |               +--------------------+ |
          v                                      |
+---------------------+                          |
|     More logs?      |-- (Yes) -----------------+
+---------+-----------+
          | (No)
          v
+-----------------------+
| Aggregate Predictions |
|    into DataFrame     |
+---------+-------------+
          |
          v
+-----------------------+      +------------------------+
| Are there any         |      | Send Security Alert    |
| SECURITY_ALERT logs?  |-(Yes)| Email to Administrator |
+---------+-------------+      +----------+-------------+
          | (No)                          |
          v                               |
+-----------------------+                 |
| Save DataFrame as     |<----------------+
| 'classified_logs.csv' |
+---------+-------------+
          |
          v
+-----------------------+
| Return FileResponse   |
| (Stream CSV to Client)|
+-----------------------+
```
