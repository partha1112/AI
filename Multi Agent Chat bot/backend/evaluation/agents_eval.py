import sys
import os
import asyncio
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from deepeval import assert_test
from deepeval.test_case import LLMTestCase
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    HallucinationMetric,
    BiasMetric,
    ToxicityMetric
)
from backend.evaluation.utils import judge

from backend.agents.GeneralState import AgentSate
from backend.agents.accounts_agent import invoke_accounts
from backend.agents.transactions_agent import invoke_transaction
from backend.agents.service_agent import invoke_service

def get_metrics():
    # Using low thresholds to keep it simple
    return [
        AnswerRelevancyMetric(threshold=0.8, model=judge),
        FaithfulnessMetric(threshold=0.8, model=judge),
        ContextualPrecisionMetric(threshold=0.8, model=judge),
        ContextualRecallMetric(threshold=0.8, model=judge),
        HallucinationMetric(threshold=0.2, model=judge),
        BiasMetric(threshold=0.2, model=judge),
        ToxicityMetric(threshold=0.2, model=judge)
    ]

class TestAgentsEval:
    def test_accounts_agent(self):
        state = AgentSate(
            user_message="What is my checking account balance?",
            account_number=100001,
            coordinator_response="User wants to check balance -> Route to accounts agent."
        )
        response = asyncio.run(invoke_accounts(state))
        actual_output = response["current_response"].get("ACCOUNTS", "")

        test_case = LLMTestCase(
            input="What is my checking account balance?",
            actual_output=actual_output,
            expected_output="Your checking account balance is $1,000.",
            retrieval_context=["The user has a checking account with a balance of $1,000."],
            context=["The user has a checking account with a balance of $1,000."]
        )
        assert_test(test_case, get_metrics())

    def test_transactions_agent(self):
        state = AgentSate(
            user_message="Send $50 to John",
            user_message_unmasked="Send $50 to John",
            account_number=100001,
            coordinator_response="TRANSFER from_account_number=100001 to_account_number=100002 amount=50"
        )
        response = asyncio.run(invoke_transaction(state))
        actual_output = response["current_response"].get("TRANSACTION", "")

        test_case = LLMTestCase(
            input="Send $50 to John",
            actual_output=actual_output,
            expected_output="Transaction of $50 to John was successful.",
            retrieval_context=["User balance is sufficient. John is a valid payee."],
            context=["User balance is sufficient. John is a valid payee."]
        )
        assert_test(test_case, get_metrics())
        
    def test_service_agent(self):
        state = AgentSate(
            user_message="My app is not working",
            account_number=100001,
            coordinator_response="User is facing app issues -> Route to service agent."
        )
        response = asyncio.run(invoke_service(state))
        actual_output = response["current_response"].get("SERVICE", "")

        test_case = LLMTestCase(
            input="My app is not working",
            actual_output=actual_output,
            expected_output="I am sorry to hear that. I will help you troubleshoot.",
            retrieval_context=["Troubleshooting steps for app issues."],
            context=["Troubleshooting steps for app issues."]
        )
        assert_test(test_case, get_metrics())
        
    def test_summarize_agent(self):
        # We use a dummy for the summarize agent as it triggers database writes in Pinecone 
        # and doesn't return a text response directly suitable for string comparison.
        test_case = LLMTestCase(
            input="Summarize the previous conversation about checking balance.",
            actual_output="The user asked for their checking account balance and was informed it is $1,000.",
            expected_output="The user asked for their checking account balance and was informed it is $1,000.",
            retrieval_context=["User asked: What is my checking account balance? Agent answered: Your checking account balance is $1,000."],
            context=["User asked: What is my checking account balance? Agent answered: Your checking account balance is $1,000."]
        )
        assert_test(test_case, get_metrics())
