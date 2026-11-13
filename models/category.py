from dataclasses import dataclass


@dataclass
class Category:
    category_id: int
    name: str
    type: str  # 'Доход' или 'Расход'
