from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ActivityEvent:

    timestamp: datetime
    action: str
    details: str