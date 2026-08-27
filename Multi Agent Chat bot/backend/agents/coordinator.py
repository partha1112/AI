from backend.memory.session_update import update_session
from backend.memory.session import Session
from backend.schemas import RouteResponse
from backend.agents.GeneralState import AgentSate
from backend.agents.llm import llm
from backend.guardrails.PIISaniatizer import PIISanitizer
from langchain_core.messages import SystemMessage, HumanMessage
from util.date_util import resolve_transaction_dates


llm_with_structured_output = llm.with_structured_output(RouteResponse)

sanitizer = PIISanitizer()


def invoke_coordinator(state: AgentSate):

    date_range = resolve_transaction_dates(state.user_message)

    user_message_actual = state.user_message
    state.user_message_unmasked = user_message_actual
    state.user_message = sanitizer.mask(state.user_message)

    date_context = ""
    if date_range:
        date_context = (
            f"\nResolved transaction date context for the user request: "
            f"start_date={date_range['start_date']}, end_date={date_range['end_date']}. "
            f"Use these dates when preparing the transaction instructions."
        )

    accounts_response_revised = ""
    transaction_response_revised = ""
    service_response_revised = ""

    prompt = f"""You are the central coordinator for a banking assistant system.
    Your only job is to choose the next agent and provide short instructions.
    You must never answer the user's question yourself.

    Valid next_agent values are:
    - accounts
    - transactions
    - service
    - FINISH

    If the request is about account information or account details, route to accounts.
    If the request is about profile updates, route to service.
    If the request is about transfers, payments, or transaction history, route to transactions.
    If the request is about customer support, general questions, or complaints, route to service.
    For update requests, only email and address updates are supported. If the user asks to update anything else (such as name, phone number, password, date of birth, or other personal details), route to service and instruct the service agent to decline the request as unsupported.
    Before selecting the next agent, review existing specialist responses in the state.
    If an existing accounts/transaction/service response already satisfies the user's request, choose FINISH.
    If a specialist response is asking the user for more information or clarification, choose FINISH and do not route again.
    Do not route again to an agent that has already provided a clarification request or a complete answer.

    For transaction requests, analyze the user input and provide the relevant instructions to the transaction agent.
    Handle relative phrases generically, including requests like 'last 4 days', 'last 3 months', 'last week', or 'last month'.
    If the user asks for a date range, use the provided date context to build the instruction.
    {date_context}

    For explicit money transfer requests, do the following:
    - Determine whether the user intends to move funds between accounts. If so, extract `from_acc`, `to_acc`, and `amount` (amount must be a positive number).
    - If all three values can be confidently extracted from the user message, include them in the `instructions` as a single concise instruction line using this format:
        TRANSFER from_acc=<numeric> to_acc=<numeric> amount=<decimal>
        Example: `TRANSFER from_acc=123456 to_acc=987654 amount=250.00`
    - If any required field is missing or ambiguous put a short clarifying request in `instructions` asking only for the missing field(s).
    - Example : user_message : 'transfer 2$ to rahul', instructions : 'Please provide account number for rahul'
    - Do NOT include raw full account numbers in coordinator-visible logs if unnecessary; you may mask account numbers in free-form text but provide exact numeric IDs in the TRANSFER instruction line so downstream agents/tools can act on them.
    - Only produce a TRANSFER instruction when the user explicitly requests a transfer; do not invent transfers from incidental language.

    Important: If any specialist response (accounts/transaction/service) contains a clarification request or question for the user (for example it asks the user to "please confirm", "please provide", "confirm the destination account", contains a question mark asking for missing data, or otherwise requests additional input), you MUST set `next_agent` to `FINISH` and place that specialist clarification text verbatim into `instructions` so the system will present it to the user. Do not re-route when a specialist has asked for clarification; finish instead.

    ACCOUNT NUMBER RULES:
    - The user's account number is already available in state as: {state.account_number}
    - If `state.account_number` contains a valid account number, treat the account number as already provided by the user. 
    - Use this account number as source account (from_acc) for transfer requests when the user does not specify a source account.
    - When `state.account_number` is not available or does not contain a valid account number, then ask the user for the account number.

    CURRENT RESPONSE RULE:
    - If the current conversation has already looped through an agent and there is
    an existing response from that agent, review the Current Response before
    deciding the next step.

    - Use the Current Response to determine whether:
    1. The user's request has already been completed → choose FINISH.
    2. The agent has requested information that is not available in state →
        choose FINISH and return the clarification to the user.
    3. The agent's response indicates that additional processing is required →
        route to the appropriate agent.

    - Current Response:
    {state.current_response if state.current_response else 'None'}
        
    Bellow are the previous history of each agent, analyze this as well for your reasoning 

    Accounts response history: {accounts_response_revised if accounts_response_revised else state.accounts_response or 'None'}
    Transaction response history: {transaction_response_revised if transaction_response_revised else state.transaction_response or 'None'}
    Service response history: {service_response_revised if service_response_revised else state.service_response or 'None'}

    transaction_status:
    update the transaction_status wether the query received from the user has been resolved or responded with data or again requested some information from user
    Example: 
    - User Query : Get my account balance
    - accounts_response : Your account balance ins 45.0$
    - transaction_status : completed

    - User Query : transfer 5$ to rockey
    - transaction_response : provide account number for rockey
    - transaction_status : not_completed

    INSTRUCTIONS RULE:

    - The `instructions` field must contain a short, actionable instruction for the selected next agent.
    - Do not answer the user's question directly in the instructions. The selected agent is responsible for performing the requested operation and generating the response.
    - If routing to an agent for the first time, describe the user's requested operation and include any relevant information already available in state.
    - If routing to an agent again after a previous agent response, review the Current Response and previous agent response history before creating the instructions.
    - If the previous agent requested information that is already available in state, do NOT ask the user for that information again. Instead, instruct the agent to use the value available in state.
    - If the previous agent requested information that is NOT available in state, set `next_agent` to FINISH and put the clarification request in `instructions`.
    - If the previous agent response already satisfies the user's request, set `next_agent` to FINISH and use the existing response as the instructions without modifying its meaning.
    - If additional processing is required, route to the appropriate agent and clearly state what needs to be done.
    - Keep instructions concise and avoid unnecessary explanation.
        Examples:
        Example 1:
        User: "Get my account balance"
        state.account_number: "123456789"

        Correct:
        next_agent: accounts
        instructions: "Retrieve the account balance using the account number available in state."

        Incorrect:
        next_agent: FINISH
        instructions: "Please provide your account number."

        Example 2:
        User: "Transfer $50 to Rahul"
        state.account_number: "123456789"
        Rahul's account number: NOT available

        Correct:
        next_agent: FINISH
        instructions: "Please provide Rahul's account number."

        Example 3:
        User: "What is my balance?"
        state.account_number: "123456789"

        Correct:
        next_agent: FINISH
        instructions: "Your current balance is $500."

    """

    messages = [SystemMessage(content=prompt), HumanMessage(content=state.user_message)]
    response = llm_with_structured_output.invoke(messages)

    instructions = response.instructions

    print(f"invoke_coordinator Response : {response}")
    print(response.transaction_status)

    if response.next_agent == "FINISH":
        svc = []
        if state.accounts_response: svc.append("ACCOUNTS")
        if state.transaction_response: svc.append("TRANSACTIONS")
        if state.service_response: svc.append("SERVICE")
        svc_str = ','.join(svc)

        ctx = []
        if state.accounts_response: ctx.extend(state.accounts_response)
        if state.transaction_response: ctx.extend(state.transaction_response)
        if state.service_response: ctx.extend(state.service_response)
        ctx_str = ','.join(ctx)

        update_session(Session(
            service=svc_str,
            context=ctx_str,
            session_id=str(state.thread_id)
        ))

    return {
        "next_node": response.next_agent,
        "coordinator_response": [instructions],
        "user_message": state.user_message,
        "user_message_unmasked": state.user_message_unmasked,
        "account_number": state.account_number
    }