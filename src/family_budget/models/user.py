from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    login: str
    password_hash: str
    username: str
    email: str | None
    role: str
    created_at: str
