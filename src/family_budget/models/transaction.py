from dataclasses import dataclass


@dataclass
class Transaction:
    transaction_id: int
    user_id: int
    account_id: int
    category_id: int
    amount: float
    transaction_date: str
    payment_method: str
    description: str | None
    # служебные поля (в таблице transactions их нет, заполняются через JOIN)
    username: str | None = None
    account_name: str | None = None
    category_name: str | None = None
    category_type: str | None = None
