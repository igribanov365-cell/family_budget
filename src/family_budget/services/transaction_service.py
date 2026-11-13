from datetime import datetime

from repositories import account_repository, category_repository, transaction_repository
from models.transaction import Transaction
from models.user import User
from services.constants import (
    DATE_FORMAT, PAYMENT_METHODS, ROLE_HEAD, TYPE_INCOME,
)
from services.errors import ServiceError


def _effect(type_: str, amount: float) -> float:
    """Как транзакция меняет баланс счёта: доход увеличивает, расход уменьшает."""
    return amount if type_ == TYPE_INCOME else -amount


def _validate(amount: float, date: str, category_id: int, payment_method: str):
    """Проверяет данные и возвращает категорию."""
    if amount <= 0:
        raise ServiceError("Сумма должна быть больше нуля")
    try:
        datetime.strptime(date, DATE_FORMAT)
    except ValueError:
        raise ServiceError("Дата должна быть в формате ГГГГ-ММ-ДД")
    if payment_method not in PAYMENT_METHODS:
        raise ServiceError("Способ оплаты: 'Наличные' или 'Карта'")
    category = category_repository.get_by_id(category_id)
    if not category:
        raise ServiceError("Категория не найдена")
    return category


def _get_editable(actor: User, transaction_id: int) -> Transaction:
    tr = transaction_repository.get_by_id(transaction_id)
    if not tr:
        raise ServiceError("Транзакция не найдена")
    if actor.role != ROLE_HEAD and tr.user_id != actor.user_id:
        raise ServiceError("Можно изменять только свои транзакции")
    return tr


def add_transaction(actor: User, account_id: int, category_id: int, amount: float,
                    date: str, payment_method: str, description: str | None) -> int:
    account = account_repository.get_by_id(account_id)
    if not account:
        raise ServiceError("Счёт не найден")
    if account.user_id != actor.user_id:
        raise ServiceError("Транзакцию можно провести только по своему счёту")
    category = _validate(amount, date, category_id, payment_method)
    delta = _effect(category.type, amount)
    if account.balance + delta < 0:
        raise ServiceError("Недостаточно средств на счёте")
    desc = (description or "").strip() or None
    new_id = transaction_repository.create(
        actor.user_id, account_id, category_id, amount, date, payment_method, desc
    )
    account_repository.change_balance(account_id, delta)
    return new_id


def get_transactions(actor: User) -> list[Transaction]:
    """Глава видит все транзакции семьи, член семьи — только свои."""
    if actor.role == ROLE_HEAD:
        return transaction_repository.get_all()
    return transaction_repository.get_by_user(actor.user_id)


def update_transaction(actor: User, transaction_id: int, category_id: int, amount: float,
                       date: str, payment_method: str, description: str | None):
    old = _get_editable(actor, transaction_id)
    new_category = _validate(amount, date, category_id, payment_method)
    account = account_repository.get_by_id(old.account_id)
    delta = _effect(new_category.type, amount) - _effect(old.category_type, old.amount)
    if account.balance + delta < 0:
        raise ServiceError("Недостаточно средств на счёте для такого изменения")
    desc = (description or "").strip() or None
    transaction_repository.update(transaction_id, category_id, amount, date, payment_method, desc)
    if delta:
        account_repository.change_balance(old.account_id, delta)


def delete_transaction(actor: User, transaction_id: int):
    old = _get_editable(actor, transaction_id)
    account = account_repository.get_by_id(old.account_id)
    delta = -_effect(old.category_type, old.amount)  # откат влияния на баланс
    if account.balance + delta < 0:
        raise ServiceError("Нельзя удалить: баланс счёта станет отрицательным")
    transaction_repository.delete(transaction_id)
    account_repository.change_balance(old.account_id, delta)
