import pytest
import sys
import os
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
from backend.agents.coordinator import invoke_coordinator
from backend.agents.GeneralState import AgentSate
import asyncio

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

class TestCoordinatorEval:
    def test_coordinator_routing(self):
        # Create a mock state with minimal required fields
        state = AgentSate(
            user_message="I want to check my account balance",
            account_number=100001
        )
        
        # Invoke the actual coordinator to get its dynamic output
        response = asyncio.run(invoke_coordinator(state))
        actual_output = response.get("coordinator_response", "")

        test_case = LLMTestCase(
            input="I want to check my account balance",
            actual_output=actual_output,
            expected_output="a short description of the requested account operation.",
            retrieval_context=["User wants to check balance -> Route to accounts agent."],
            context=["User wants to check balance -> Route to accounts agent."]
        )
        assert_test(test_case, get_metrics())
