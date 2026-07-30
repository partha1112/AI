import asyncio
import nest_asyncio
from pathlib import Path
from nemoguardrails import LLMRails, RailsConfig

nest_asyncio.apply()

_rails = LLMRails(RailsConfig.from_path(str(Path(__file__).parent)))

_REFUSAL_PHRASES = [
    "I'm sorry, I'm only able to help with travel planning",
    "I can't do that",
]

class GuardrailsBlocked(Exception):
    pass

async def check_input_async(user_message: str) -> None:
    """
    Validate user input using NemoGuardrails with LLM as judge.
    The system prompt instructs the LLM to refuse off-topic queries.
    """
    messages = [{"role": "user", "content": user_message}]
    
    # Call generate_async - the LLM will apply the system prompt
    response = await _rails.generate_async(messages=messages)
    
    print(f"DEBUG - Response from generate_async: {response}")
    print(f"DEBUG - Response type: {type(response)}")
    
    # Extract text from response
    text = ""
    if isinstance(response, str):
        text = response
    elif isinstance(response, dict):
        text = response.get("content", "")
    else:
        text = str(response)
    
    print(f"DEBUG - Extracted text: '{text}'")
    print(f"DEBUG - Text length: {len(text)}")
    
    # Check if the LLM's response contains a refusal phrase
    # This means the input was rejected by the system prompt
    if text and any(phrase.lower() in text.lower() for phrase in _REFUSAL_PHRASES):
        print(f"DEBUG - Refusal phrase detected: input blocked by guardrails")
        raise GuardrailsBlocked(text)

def check_input(user_message: str) -> None:
    """Synchronous wrapper for input validation."""
    asyncio.get_event_loop().run_until_complete(check_input_async(user_message))

async def check_output_async(bot_response: str) -> str:
    """
    Validate bot output using NemoGuardrails with LLM as judge.
    """
    messages = [
        {"role": "user", "content": "Plan my trip"},
        {"role": "assistant", "content": bot_response},
    ]
    
    response = await _rails.generate_async(messages=messages)
    
    print(f"DEBUG - Output response: {response}")
    
    # Extract text from response
    text = ""
    if isinstance(response, str):
        text = response
    elif isinstance(response, dict):
        text = response.get("content", "")
    else:
        text = str(response)
    
    print(f"DEBUG - Output extracted text: '{text}'")
    
    # Check if unsafe content was detected
    if text and any(phrase.lower() in text.lower() for phrase in _REFUSAL_PHRASES):
        print(f"DEBUG - Safety issue detected in output")
        raise GuardrailsBlocked(text)
    
    return bot_response

def check_output(bot_response: str) -> str:
    """Synchronous wrapper for output validation."""
    return asyncio.get_event_loop().run_until_complete(check_output_async(bot_response))
