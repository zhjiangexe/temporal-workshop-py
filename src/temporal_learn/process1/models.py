from dataclasses import dataclass


@dataclass
class RegisterRequest:
    user_id: str
    email: str
