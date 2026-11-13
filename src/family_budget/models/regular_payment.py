from dataclasses import dataclass


@dataclass
class RegularPayment:
    payment_id: int
    user_id: int
    category_id: int
    amount: float
    frequency: str  # 'месяц' или 'неделя'
    next_date: str
    # служебные поля (заполняются через JOIN)
    username: str | None = None
    category_name: str | None = None
    category_type: str | None = None
