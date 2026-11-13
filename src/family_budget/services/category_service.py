from repositories import category_repository
from models.category import Category
from models.user import User
from services.constants import TYPES, ROLE_HEAD
from services.errors import ServiceError


def _require_head(actor: User):
    if actor.role != ROLE_HEAD:
        raise ServiceError("Недостаточно прав: категориями управляет Глава семьи")


def _check(name: str, type_: str, parent_id: int | None, own_id: int | None = None):
    if not name.strip():
        raise ServiceError("Название категории не может быть пустым")
    if type_ not in TYPES:
        raise ServiceError("Тип категории должен быть 'Доход' или 'Расход'")
    if parent_id is not None:
        if parent_id == own_id:
            raise ServiceError("Категория не может быть родителем самой себя")
        parent = category_repository.get_by_id(parent_id)
        if not parent:
            raise ServiceError("Родительская категория не найдена")
        if parent.parent_id is not None:
            raise ServiceError("Допускается только один уровень подкатегорий")
        if parent.type != type_:
            raise ServiceError("Тип подкатегории должен совпадать с типом родительской категории")
    duplicate = any(
        c.name.lower() == name.strip().lower()
        and c.parent_id == parent_id
        and c.category_id != own_id
        for c in category_repository.get_all()
    )
    if duplicate:
        raise ServiceError("Такая категория уже существует")


def get_all_categories() -> list[Category]:
    return category_repository.get_all()


def create_category(actor: User, name: str, type_: str,
                    parent_id: int | None = None, color: str | None = None) -> int:
    _require_head(actor)
    _check(name, type_, parent_id)
    return category_repository.create(parent_id, name.strip(), type_, (color or "").strip() or None)


def update_category(actor: User, category_id: int, name: str, type_: str,
                    parent_id: int | None = None, color: str | None = None):
    _require_head(actor)
    existing = category_repository.get_by_id(category_id)
    if not existing:
        raise ServiceError("Категория не найдена")
    _check(name, type_, parent_id, own_id=category_id)
    has_children = any(c.parent_id == category_id for c in category_repository.get_all())
    if has_children and parent_id is not None:
        raise ServiceError("У категории есть подкатегории, её нельзя сделать подкатегорией")
    if has_children and type_ != existing.type:
        raise ServiceError("Нельзя менять тип категории, у которой есть подкатегории")
    category_repository.update(category_id, parent_id, name.strip(), type_,
                               (color or "").strip() or None)


def delete_category(actor: User, category_id: int):
    _require_head(actor)
    if not category_repository.get_by_id(category_id):
        raise ServiceError("Категория не найдена")
    if category_repository.count_usage(category_id) > 0:
        raise ServiceError(
            "Нельзя удалить категорию: она используется в транзакциях, "
            "регулярных платежах или имеет подкатегории"
        )
    category_repository.delete(category_id)
