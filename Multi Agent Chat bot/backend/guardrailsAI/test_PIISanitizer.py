from backend.agents.GeneralState import AgentSate
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

import pytest
from backend.guardrailsAI.PIISaniatizer import PIISanitizer

@pytest.fixture
def sanitizer():
    return PIISanitizer()

class TestMask:

    def test_email_is_masked(self, sanitizer):
        state = AgentSate(user_message="Send 1$ to 100002.", account_number=100001)
        state = PIISanitizer().mask(state)
        state = PIISanitizer().mask(state.account_number)
        print(state.user_message_masked)
    