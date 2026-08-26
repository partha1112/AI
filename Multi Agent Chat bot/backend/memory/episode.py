from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Episode:
    user_id     : str
    thread_id   : str
    event_type  : str
    summary     : str
    outcome     : str
    date        : date
    metadata    : Optional[dict] = None