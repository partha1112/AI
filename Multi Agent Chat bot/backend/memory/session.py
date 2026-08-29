from dataclasses import dataclass

@dataclass
class Session:
    session_id  : str
    account_id  : str
    service     : str
    context     : str
    