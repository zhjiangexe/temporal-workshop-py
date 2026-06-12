from dataclasses import dataclass
from enum import StrEnum, auto

TEMPORAL_URL = "localhost:7233"
TASK_QUEUE = "price-change-tq"


class ReviewOutcome(StrEnum):
    APPROVE = auto()
    REJECT = auto()


@dataclass
class ProductChangeSpec:
    request_id: str
    product_id: str
    new_price: float


@dataclass
class ReviewDecision:
    outcome: ReviewOutcome
    approver_id: str
    reason: str = ""
