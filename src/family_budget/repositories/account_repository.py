from database.database import get_connection
from models.account import Account

_SELECT = """
    SELECT a.account_id, a.user_id, a.name, a.balance, a.currency, u.username
    FROM accounts a
    JOIN users u ON u.user_id = a.user_id
"""


def _map(row) -> Account:
    return Account(*row)


def create(user_id: int, name: str, balance: float, currency: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO accounts(user_id, name, balance, currency) VALUES (?, ?, ?, ?)",
        (user_id, name, balance, currency),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_by_id(account_id: int) -> Account | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " WHERE a.account_id = ?", (account_id,))
    row = cur.fetchone()
    conn.close()
    return _map(row) if row else None


def get_all() -> list[Account]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " ORDER BY a.account_id")
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def get_by_user(user_id: int) -> list[Account]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " WHERE a.user_id = ? ORDER BY a.account_id", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def update(account_id: int, name: str, currency: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE accounts SET name = ?, currency = ? WHERE account_id = ?",
        (name, currency, account_id),
    )
    conn.commit()
    conn.close()


def change_balance(account_id: int, delta: float):
    """Изменяет баланс счёта на delta (может быть отрицательным)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE accounts SET balance = balance + ? WHERE account_id = ?",
        (delta, account_id),
    )
    conn.commit()
    conn.close()


def delete(account_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM accounts WHERE account_id = ?", (account_id,))
    conn.commit()
    conn.close()


def count_transactions(account_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions WHERE account_id = ?", (account_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count


def get_total_balance(user_id: int | None = None) -> float:
    conn = get_connection()
    cur = conn.cursor()
    if user_id is None:
        cur.execute("SELECT COALESCE(SUM(balance), 0) FROM accounts")
    else:
        cur.execute(
            "SELECT COALESCE(SUM(balance), 0) FROM accounts WHERE user_id = ?",
            (user_id,),
        )
    total = cur.fetchone()[0]
    conn.close()
    return total
