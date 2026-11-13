from dataclasses import dataclass


@dataclass
class User:
    user_id: int
    username: str
    role: str
    login: str
    password_hash: str
