import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src" / "family_budget"))

from database.database import init_db  # noqa: E402
from repositories import user_repository  # noqa: E402
from services import auth_service, category_service, transaction_service, user_service  # noqa: E402
from services.errors import ServiceError  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setenv("FAMILY_BUDGET_DB", str(tmp_path / "test.db"))
    init_db(force=True)


def head():
    return auth_service.authenticate("papa", "1234")


def member():
    return auth_service.authenticate("mama", "1234")


def test_authentication():
    assert head().role == "Глава"
    assert auth_service.authenticate("papa", "wrong") is None


def test_register_duplicate_login():
    auth_service.register("Дочь", "daughter", "pass1")
    with pytest.raises(ServiceError):
        auth_service.register("Другая", "daughter", "pass2")


def test_report_balance():
    r = transaction_service.get_report()
    assert r["income"] == 157000 and r["expense"] == 38000 and r["balance"] == 119000


def test_member_sees_only_own_transactions():
    mine = transaction_service.get_transactions(member())
    assert mine and all(t.user_id == member().user_id for t in mine)


def test_member_cannot_edit_foreign_transaction():
    with pytest.raises(ServiceError):
        transaction_service.delete_transaction(member(), 1)  # транзакция папы


def test_add_transaction_validation():
    with pytest.raises(ServiceError):
        transaction_service.add_transaction(member(), -5, "2026-01-01", "", 3)
    with pytest.raises(ServiceError):
        transaction_service.add_transaction(member(), 5, "01.01.2026", "", 3)
    with pytest.raises(ServiceError):
        transaction_service.add_transaction(member(), 5, "2026-01-01", "", 999)


def test_only_head_manages_categories():
    with pytest.raises(ServiceError):
        category_service.create_category(member(), "Спорт", "Расход")
    category_service.create_category(head(), "Спорт", "Расход")
    with pytest.raises(ServiceError):
        category_service.create_category(head(), "спорт", "Расход")


def test_cannot_delete_used_category_or_user():
    with pytest.raises(ServiceError):
        category_service.delete_category(head(), 1)
    with pytest.raises(ServiceError):
        user_service.delete_user(head(), 2)


def test_crud_transaction():
    tid = transaction_service.add_transaction(member(), 100, "2026-01-01", "тест", 3)
    transaction_service.update_transaction(member(), tid, 150, "2026-01-02", "новое", 4)
    t = [x for x in transaction_service.get_transactions(member()) if x.transaction_id == tid][0]
    assert t.amount == 150 and t.category_name == "Коммунальные услуги"
    transaction_service.delete_transaction(member(), tid)
    assert all(x.transaction_id != tid for x in transaction_service.get_transactions(member()))
