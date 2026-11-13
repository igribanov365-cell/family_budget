from dataclasses import dataclass


@dataclass
class Account:
    account_id: int
    user_id: int
    name: str
    balance: float
    currency: str
    # служебное поле (заполняется через JOIN)
    owner_name: str | None = None
