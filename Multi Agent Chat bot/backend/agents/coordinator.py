from backend.agents.summarize_agent import sumarize_episode
from backend.schemas import RouteResponse
from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm
from backend.guardrails.PIISaniatizer import PIISanitizer
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from util.date_util import resolve_transaction_dates


llm_with_structured_output = llm.with_structured_output(RouteResponse)

sanitizer = PIISanitizer()


async def invoke_coordinator(state: AgentSate):

    if any(word in state.user_message.lower() for word in ["exit", "bye", "quit", "done", "thank you", "thanks"]):
        sumarize_episode(state)
        return {
            "next_node": "FINISH",
            "messages": [AIMessage(content="Thank you for reaching out! Have a great day.", name="coordinator")]
        }
    
    date_range = resolve_transaction_dates(state.user_message)

    user_message_actual = state.user_message
    state.user_message_unmasked = user_message_actual

    date_context = ""
    if date_range:
        date_context = (
            f"\nResolved transaction date context for the user request: "
            f"start_date={date_range['start_date']}, end_date={date_range['end_date']}. "
            f"Use these dates when preparing the transaction instructions."
        )
        
    

    

    messages_history = []

    for msg in state.messages:

        if isinstance(msg, HumanMessage):
            role = "USER"

        elif getattr(msg, "name", None):
            role = msg.name.upper()

        else:
            role = msg.type.upper()

        messages_history.append(f"{role}: {msg.content}")

    messages_history_str = "\n".join(messages_history)


    prompt = f""" 
    You are the Coordinator Agent for a banking assistant.

    Your responsibilities:

    1. Review the current user message, current response, and message history.
    2. Decide which agent should handle the request.
    3. Generate short instructions for the selected agent.
    4. If a specialist has already answered the user's request, return that response and finish.

    Valid next_agent values:

    * accounts
    * transactions
    * service
    * FINISH

    ---

    ## ROUTING RULES

    * Account balance, account details, account information -> accounts
    * Transaction history -> transactions
    * Transfers, payments, profile updates, support requests -> service
    * Only email and address updates are supported.
    * Any other profile update request must be routed to service with instructions to decline.

    ---

    ## CURRENT RESPONSE PRIORITY

    CURRENT_RESPONSE:
    {state.current_response}

    Always evaluate CURRENT_RESPONSE first.

    If CURRENT_RESPONSE:

    * Answers the user's request
    * Provides requested information
    * Confirms a successful operation
    * Requests missing information from the user

    Then:

    * next_agent = FINISH
    * instructions = CURRENT_RESPONSE content (verbatim)

    Do not generate a new response.

    ---

    ## MESSAGE HISTORY EVALUATION

    Message History:
    {messages_history_str}

    Review history from newest to oldest.

    If the latest specialist response:

    * Answers the user's request -> FINISH
    * Requests clarification -> FINISH
    * If user ask for transactin details then dont check the history route it to 

    Return the specialist response verbatim.

    Never replace a valid specialist response with a coordinator-generated response.

    ---

    ## TRANSFER HANDLING

    For transfer requests:

    From Account:
    {state.account_number}

    Extract:

    * from_account_number
    * to_account_number
    * amount

    Rules:

    * Use {state.account_number} as the source account unless the user specifies another account.
    * Remove currency symbols from amount.
    * Amount must be numeric.

    If all values are available:

    next_agent = service

    instructions:

    TRANSFER from_account_number=<number> to_account_number=<number> amount=<amount>

    If amount or destination account is missing:

    next_agent = FINISH

    Ask only for the missing information.

    Examples:

    User:
    Transfer $500

    Response:
    'next_node':FINISH
    'instructions':Please provide the destination account number.

    User:
    Transfer money to account 123456

    Response:
    'next_node':service
    'instructions':TRANSFER from_account_number=123456 to_account_number=123456 amount=500

    ---

    ## TRANSACTION STATUS

    completed:

    * Requested information was provided
    * Transfer completed successfully
    * Requested operation completed successfully

    not_completed:

    * Missing user input
    * Clarification required
    * Operation pending
    * Operation failed

    ---
    ## TRANSACTION REQUESTS RULES

    If the user requests transaction information:

    * Extract date range using resolve_transaction_dates()
    * Format as yyyy-MM-dd
    * If the user does not specify dates, use the resolved date range
    * If the user specifies only one date, use it as both start_date and end_date
    * If the user does not specify any dates, ask for clarification

    ---

    ## DO YOU NEED ANYTHING ELSE RULE

    Append:

    "Do you need anything else?"

    ONLY when ALL conditions are true:

    1. A specialist agent generated the response.
    2. The response explicitly confirms successful completion.
    3. The request involved a completed action or transaction.

    Examples:

    "The transfer of $500 has been successfully completed."

    Return:
    "The transfer of $500 has been successfully completed. Do you need anything else?"

    "Please provide the destination account number."

    Return:
    "Please provide the destination account number."

    "Which account would you like to transfer from?"

    Return:
    "Which account would you like to transfer from?"

    ---

    ## OUTPUT RULES

    * Never generate banking answers yourself.
    * Never summarize specialist responses.
    * Never modify specialist responses.
    * Always return specialist responses verbatim.
    * FINISH means no further agent processing is required.


    """

    messages = [SystemMessage(content=prompt), HumanMessage(content=state.user_message)]
    response = llm_with_structured_output.invoke(messages)

    instructions = response.instructions

    print(f"invoke_coordinator Response : {response}")
    print(response.transaction_status)

    return {
        "next_node": response.next_agent,
        "coordinator_response": instructions,
        "messages": [AIMessage(content=instructions, name="COORDINATOR")],
        "user_message": state.user_message,
        "user_message_unmasked": state.user_message_unmasked,
        "account_number": state.account_number
    }