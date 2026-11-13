from dataclasses import dataclass


@dataclass
class Category:
    category_id: int
    parent_id: int | None
    name: str
    type: str  # 'Доход' или 'Расход'
    color: str | None
    # служебное поле: название родительской категории (для подкатегорий)
    parent_name: str | None = None

    @property
    def full_name(self) -> str:
        return f"{self.parent_name} / {self.name}" if self.parent_name else self.name
