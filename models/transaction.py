from dataclasses import dataclass


@dataclass
class Transaction:
    transaction_id: int
    amount: float
    transaction_date: str
    description: str | None
    user_id: int
    category_id: int
    # служебные поля (в таблице transactions их нет, заполняются через JOIN)
    username: str | None = None
    category_name: str | None = None
    category_type: str | None = None
