from __future__ import annotations

from presidio_analyzer import AnalyzerEngine

from backend.agents.GeneralState import AgentSate
from backend.guardrailsAI.AccountNumberRecognizer import RecognizeAccountNumber


class PIISanitizer:

    def __init__(self):
        self.analyzer = AnalyzerEngine()

        self.analyzer.registry.add_recognizer(
            RecognizeAccountNumber()
        )

        self.entities = [
            "EMAIL_ADDRESS",
            "CREDIT_CARD",
            "PHONE_NUMBER",
            "ACCOUNT_NUMBER"
        ]

    def mask(self, user_message: str) -> dict:

        text = user_message
        results = self.analyzer.analyze(
            text=text,
            entities=self.entities,
            language="en"
        )

        if not results:
            return {}

        pii_mapping = {}
        token_by_value = {}
        counters = {}

        replacements = []

        for result in results:
            entity_type = result.entity_type
            raw_value = text[ result.start:result.end ]
            if raw_value in token_by_value:
                token = token_by_value[raw_value]
            else:
                counters[entity_type] = ( counters.get(entity_type, 0) + 1 )
                token = ( f"{entity_type}_{counters[entity_type]}")
                token_by_value[raw_value] = token
                pii_mapping[token] = raw_value

            replacements.append(
                (
                    result.start,
                    result.end,
                    token
                )
            )

        masked_text = text

        for start, end, token in reversed(replacements):

            masked_text = (
                masked_text[:start]
                + token
                + masked_text[end:]
            )

        return {
            "user_message_masked": masked_text,
            "pii_mapping": pii_mapping
            }


