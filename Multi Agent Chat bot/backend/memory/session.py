from dataclasses import dataclass

@dataclass
class Session:
    session_id  : str
    service     : str
    context     : str
    