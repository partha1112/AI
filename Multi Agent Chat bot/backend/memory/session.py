from dataclasses import dataclass
from datetime import date

@dataclass
class Session:
    session_id  : str
    account_id  : str
    status     : str
    crearted_at : date
    last_activity : date
    