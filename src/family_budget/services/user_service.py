from repositories import user_repository
from models.user import User
from services.auth_service import check_email
from services.constants import ROLES, ROLE_HEAD
from services.errors import ServiceError


def _require_head(actor: User):
    if actor.role != ROLE_HEAD:
        raise ServiceError("Недостаточно прав: действие доступно только Главе семьи")


def get_all_users(actor: User) -> list[User]:
    _require_head(actor)
    return user_repository.get_all()


def update_user(actor: User, user_id: int, username: str, email: str | None, role: str):
    _require_head(actor)
    if not username.strip():
        raise ServiceError("Имя не может быть пустым")
    if role not in ROLES:
        raise ServiceError("Недопустимая роль")
    email = check_email(email)
    target = user_repository.get_by_id(user_id)
    if not target:
        raise ServiceError("Пользователь не найден")
    if target.role == ROLE_HEAD and role != ROLE_HEAD:
        heads = [u for u in user_repository.get_all() if u.role == ROLE_HEAD]
        if len(heads) <= 1:
            raise ServiceError("Нельзя убрать роль у последнего Главы семьи")
    user_repository.update(user_id, username.strip(), email, role)


def delete_user(actor: User, user_id: int):
    _require_head(actor)
    target = user_repository.get_by_id(user_id)
    if not target:
        raise ServiceError("Пользователь не найден")
    if target.user_id == actor.user_id:
        raise ServiceError("Нельзя удалить самого себя")
    if user_repository.has_related_data(user_id):
        raise ServiceError("Нельзя удалить пользователя: у него есть счета, транзакции или платежи")
    user_repository.delete(user_id)
