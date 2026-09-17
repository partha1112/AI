from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer
)


class RecognizeAccountNumber(PatternRecognizer):

    def __init__(self):
        patterns = [
            Pattern(
                name="account_number",
                regex=r"\b\d{6}\b",
                score=0.8
            )
        ]

        super().__init__(
            supported_entity="ACCOUNT_NUMBER",
            patterns=patterns
        )