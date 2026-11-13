from datetime import datetime

from repositories import category_repository, transaction_repository, user_repository
from models.transaction import Transaction
from models.user import User
from services.constants import ROLE_HEAD, TYPE_INCOME, TYPE_EXPENSE
from services.errors import ServiceError


def _validate(amount: float, date: str, category_id: int):
    if amount <= 0:
        raise ServiceError("Сумма должна быть больше нуля")
    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        raise ServiceError("Дата должна быть в формате ГГГГ-ММ-ДД")
    if not category_repository.get_by_id(category_id):
        raise ServiceError("Категория не найдена")


def _get_editable(actor: User, transaction_id: int) -> Transaction:
    tr = transaction_repository.get_by_id(transaction_id)
    if not tr:
        raise ServiceError("Транзакция не найдена")
    if actor.role != ROLE_HEAD and tr.user_id != actor.user_id:
        raise ServiceError("Можно изменять только свои транзакции")
    return tr


def add_transaction(actor: User, amount: float, date: str,
                    description: str | None, category_id: int) -> int:
    if not user_repository.get_by_id(actor.user_id):
        raise ServiceError("Пользователь не найден")
    _validate(amount, date, category_id)
    desc = (description or "").strip() or None
    return transaction_repository.create(amount, date, desc, actor.user_id, category_id)


def get_transactions(actor: User) -> list[Transaction]:
    """Глава видит все транзакции семьи, член семьи — только свои."""
    if actor.role == ROLE_HEAD:
        return transaction_repository.get_all()
    return transaction_repository.get_by_user(actor.user_id)


def update_transaction(actor: User, transaction_id: int, amount: float,
                       date: str, description: str | None, category_id: int):
    _get_editable(actor, transaction_id)
    _validate(amount, date, category_id)
    desc = (description or "").strip() or None
    transaction_repository.update(transaction_id, amount, date, desc, category_id)


def delete_transaction(actor: User, transaction_id: int):
    _get_editable(actor, transaction_id)
    transaction_repository.delete(transaction_id)


def get_report() -> dict:
    """Общий отчёт по семье: доходы, расходы, баланс и суммы по категориям."""
    totals = transaction_repository.get_totals_by_type()
    income, expense = totals[TYPE_INCOME], totals[TYPE_EXPENSE]
    return {
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "by_category": transaction_repository.get_totals_by_category(),
    }
