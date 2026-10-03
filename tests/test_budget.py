import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "src", "family_budget")))

from budget import Budget


def test_add_income():
    b = Budget()
    b.add_income("Зарплата", 50000)
    assert b.total_income() == 50000


def test_add_expense():
    b = Budget()
    b.add_expense("Продукты", 3000)
    assert b.total_expense() == 3000


def test_balance():
    b = Budget()
    b.add_income("Зарплата", 50000)
    b.add_expense("Продукты", 3000)
    assert b.balance() == 47000