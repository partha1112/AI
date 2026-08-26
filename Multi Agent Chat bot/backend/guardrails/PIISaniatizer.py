from __future__ import annotations

from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from backend.guardrails.AccountNumberRecognizer import RecognizeAccountNumber

class PIISanitizer:
    def __init__(self):
        self.analyzer = AnalyzerEngine()
        self.anonymizer = AnonymizerEngine()
        self.analyzer.registry.add_recognizer(
            RecognizeAccountNumber()
        )
        self.entities = ["EMAIL_ADDRESS", "CREDIT_CARD", "PHONE_NUMBER","ACCOUNT_NUMBER"]
        self.vault = {}
        self.counter = {}
        self._initialized = True

    def mask(self, text: str) -> str:
        result = self.analyzer.analyze(
            text=text,
            entities=self.entities,
            language="en"
        )

        if not result:
            return text

        operators = {}
        for res in result:
            entity_type = res.entity_type
            raw_value = text[res.start:res.end]

            existing_token = next((k for k, v in self.vault.items() if v == raw_value), None)
            if existing_token:
                token = existing_token
            else:
                self.counter[entity_type] = self.counter.get(entity_type, 0) + 1
                token = f"<{entity_type}_{self.counter[entity_type]}>"
                self.vault[token] = raw_value

            operators[entity_type] = OperatorConfig("replace", {"new_value": token})

        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=result,
            operators=operators
        )

        return anonymized_result.text

    def unmask(self, data):
        if isinstance(data, str):
            unmasked = data
            for token, real_val in self.vault.items():
                if token in unmasked:
                    unmasked = unmasked.replace(token, real_val)
            return unmasked
        elif isinstance(data, dict):
            return {k: self.unmask(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.unmask(v) for v in data]
        return data