from repositories import account_repository, user_repository
from models.account import Account
from models.user import User
from services.constants import ROLE_HEAD
from services.errors import ServiceError


def _check_fields(name: str, currency: str) -> tuple[str, str]:
    name, currency = name.strip(), currency.strip().upper()
    if not name:
        raise ServiceError("Название счёта не может быть пустым")
    if len(currency) != 3 or not currency.isalpha():
        raise ServiceError("Валюта задаётся трёхбуквенным кодом, например RUB")
    return name, currency


def _get_accessible(actor: User, account_id: int) -> Account:
    account = account_repository.get_by_id(account_id)
    if not account:
        raise ServiceError("Счёт не найден")
    if actor.role != ROLE_HEAD and account.user_id != actor.user_id:
        raise ServiceError("Можно работать только со своими счетами")
    return account


def get_accounts(actor: User) -> list[Account]:
    """Глава видит все счета семьи, член семьи — только свои."""
    if actor.role == ROLE_HEAD:
        return account_repository.get_all()
    return account_repository.get_by_user(actor.user_id)


def create_account(actor: User, name: str, balance: float,
                   currency: str = "RUB", owner_id: int | None = None) -> int:
    name, currency = _check_fields(name, currency)
    if balance < 0:
        raise ServiceError("Начальный баланс не может быть отрицательным")
    owner_id = owner_id if owner_id is not None else actor.user_id
    if owner_id != actor.user_id and actor.role != ROLE_HEAD:
        raise ServiceError("Создавать счета другим пользователям может только Глава семьи")
    if not user_repository.get_by_id(owner_id):
        raise ServiceError("Владелец счёта не найден")
    if any(a.name.lower() == name.lower() for a in account_repository.get_by_user(owner_id)):
        raise ServiceError("У владельца уже есть счёт с таким названием")
    return account_repository.create(owner_id, name, balance, currency)


def update_account(actor: User, account_id: int, name: str, currency: str):
    account = _get_accessible(actor, account_id)
    name, currency = _check_fields(name, currency)
    if any(a.name.lower() == name.lower() and a.account_id != account_id
           for a in account_repository.get_by_user(account.user_id)):
        raise ServiceError("У владельца уже есть счёт с таким названием")
    account_repository.update(account_id, name, currency)


def delete_account(actor: User, account_id: int):
    _get_accessible(actor, account_id)
    if account_repository.count_transactions(account_id) > 0:
        raise ServiceError("Нельзя удалить счёт, по которому есть транзакции")
    account_repository.delete(account_id)
