from repositories import account_repository, transaction_repository
from models.user import User
from services.constants import ROLE_HEAD, TYPE_INCOME, TYPE_EXPENSE


def get_report(actor: User) -> dict:
    """Глава получает отчёт по всей семье, член семьи — только по своим данным."""
    scope = None if actor.role == ROLE_HEAD else actor.user_id
    totals = transaction_repository.get_totals_by_type(scope)
    income, expense = totals[TYPE_INCOME], totals[TYPE_EXPENSE]
    return {
        "scope": "семья" if scope is None else actor.username,
        "income": income,
        "expense": expense,
        "balance": income - expense,
        "accounts_total": account_repository.get_total_balance(scope),
        "by_category": transaction_repository.get_totals_by_category(scope),
    }
