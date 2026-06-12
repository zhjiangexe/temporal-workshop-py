from dataclasses import dataclass


@dataclass
class RegisterRequest:
    user_id: str
    email: str


TEMPORAL_URL = "localhost:7233"
TASK_QUEUE = "registration-tq"
