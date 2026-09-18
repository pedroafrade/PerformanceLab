"""Private, athlete-controlled recovery history."""

from dataclasses import dataclass, field
from datetime import date
from uuid import uuid4


@dataclass(frozen=True, slots=True)
class RecoveryLogEntry:
    day: date
    category: str
    body_area: str
    severity: int
    notes: str = ""
    entry_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        if self.category not in {"Pain", "Injury", "Condition", "Other"}:
            raise ValueError("Unsupported recovery-log category.")
        if not 1 <= self.severity <= 10:
            raise ValueError("Severity must be between 1 and 10.")
