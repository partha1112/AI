import os
from typing import Dict, Any
from guardrails import Guard
from guardrails.validators import (
    Validator,
    register_validator,
    ValidationResult,
    PassResult,
    FailResult,
)
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from backend.agents.llm import llm
from backend.schemas import ScopeModel


class PromptInjectionException(Exception):
    pass


class OutOfScopeExcepton(Exception):
    pass


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


@register_validator(name="prompt_injection_validator", data_type="string")
class PromptInjectionValidator(Validator):
    def validate(self, value: str, metadata: Dict[str, Any] = {}) -> ValidationResult:
        if "my account number" in value.lower():
            return PassResult()

        res = classifier(value)[0]
        if res["label"] == "INJECTION":
            return FailResult(
                error_message="Prompt injection detected. Request blocked."
            )

        return PassResult()


@register_validator(name="scope_validator", data_type="string")
class ScopeValidator(Validator):
    def validate(self, value: str, metadata: Dict[str, Any] = {}) -> ValidationResult:
        structured_llm = llm.with_structured_output(ScopeModel)
        prompt = f"""
        You are a scope validation agent for a Banking project.
        Your task is to determine whether the user's request is related to the supported banking operations.

        Supported operations:

        1. Accounts Information
            * Check account details
            * Check account balance
            * View account information

        2. Accounts Management / Service
            * Update email address
            * Update mailing/home address
            * Manage customer account/profile information
            * Other account-related service requests

        3. Transaction Management
            * View transaction history
            * Check transactions
            * Transfer money
            * Make payments
            * Other banking transaction-related requests

        Important:
            * Requests to update the customer's email address are VALID_SCOPE.
            * Requests to update the customer's address are VALID_SCOPE.
            * Do not mark a request as OUT_OF_SCOPE just because it contains an email address, phone number, or other personal information.
            * Evaluate the user's intent, not just individual words or entities.

        If the user's request is related to any of the supported banking operations, respond ONLY with:

        VALID_SCOPE

        If the user's request is unrelated to all of the supported banking operations, respond ONLY with:

        OUT_OF_SCOPE

        User prompt:
        {value}
        """
        response = structured_llm.invoke(prompt)
        if response.label == "OUT_OF_SCOPE":
            return FailResult(
                error_message="The request received from the user is OUT OF SCOPE"
            )

        return PassResult()


def handle_injection_failure(value: str, fail_result: FailResult):
    raise PromptInjectionException(fail_result.error_message)


def handle_scope_failure(value: str, fail_result: FailResult):
    raise OutOfScopeExcepton(fail_result.error_message)


guard = Guard().use(
    PromptInjectionValidator(on_fail=handle_injection_failure),
    ScopeValidator(on_fail=handle_scope_failure),
)


def validate_input(text: str) -> Dict[str, Any]:
    try:
        guard.validate(text)
        return {
            "is_valid": True,
            "status": "VALID_SCOPE",
            "message": text,
            "error": None
        }
    except PromptInjectionException as e:
        return {
            "is_valid": False,
            "status": "PROMPT_INJECTION",
            "message": text,
            "error": str(e)
        }
    except OutOfScopeExcepton as e:
        return {
            "is_valid": False,
            "status": "OUT_OF_SCOPE",
            "message": text,
            "error": str(e)
        }
    except Exception as e:
        return {
            "is_valid": False,
            "status": "ERROR",
            "message": text,
            "error": str(e)
        }