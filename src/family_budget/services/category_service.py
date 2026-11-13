from repositories import category_repository
from models.category import Category
from models.user import User
from services.constants import TYPES, ROLE_HEAD
from services.errors import ServiceError


def _require_head(actor: User):
    if actor.role != ROLE_HEAD:
        raise ServiceError("Недостаточно прав: категориями управляет Глава семьи")


def _check(name: str, type_: str):
    if not name.strip():
        raise ServiceError("Название категории не может быть пустым")
    if type_ not in TYPES:
        raise ServiceError("Тип категории должен быть 'Доход' или 'Расход'")


def _exists(name: str, type_: str, exclude_id: int | None = None) -> bool:
    return any(
        c.name.lower() == name.strip().lower() and c.type == type_
        and c.category_id != exclude_id
        for c in category_repository.get_all()
    )


def get_all_categories() -> list[Category]:
    return category_repository.get_all()


def create_category(actor: User, name: str, type_: str) -> int:
    _require_head(actor)
    _check(name, type_)
    if _exists(name, type_):
        raise ServiceError("Такая категория уже существует")
    return category_repository.create(name.strip(), type_)


def update_category(actor: User, category_id: int, name: str, type_: str):
    _require_head(actor)
    _check(name, type_)
    if not category_repository.get_by_id(category_id):
        raise ServiceError("Категория не найдена")
    if _exists(name, type_, exclude_id=category_id):
        raise ServiceError("Такая категория уже существует")
    category_repository.update(category_id, name.strip(), type_)


def delete_category(actor: User, category_id: int):
    _require_head(actor)
    if not category_repository.get_by_id(category_id):
        raise ServiceError("Категория не найдена")
    if category_repository.count_transactions(category_id) > 0:
        raise ServiceError("Нельзя удалить категорию, по которой есть транзакции")
    category_repository.delete(category_id)
