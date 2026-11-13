from database.database import get_connection
from models.transaction import Transaction

_SELECT = """
    SELECT t.transaction_id, t.amount, t.transaction_date, t.description,
           t.user_id, t.category_id,
           u.username, c.name, c.type
    FROM transactions t
    JOIN users u ON u.user_id = t.user_id
    JOIN categories c ON c.category_id = t.category_id
"""


def _map(row) -> Transaction:
    return Transaction(*row)


def create(amount: float, date: str, description: str | None,
           user_id: int, category_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions(amount, transaction_date, description, user_id, category_id)
        VALUES (?, ?, ?, ?, ?)
    """, (amount, date, description, user_id, category_id))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_by_id(transaction_id: int) -> Transaction | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " WHERE t.transaction_id = ?", (transaction_id,))
    row = cur.fetchone()
    conn.close()
    return _map(row) if row else None


def get_all() -> list[Transaction]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " ORDER BY t.transaction_date DESC, t.transaction_id DESC")
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def get_by_user(user_id: int) -> list[Transaction]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        _SELECT + " WHERE t.user_id = ? ORDER BY t.transaction_date DESC, t.transaction_id DESC",
        (user_id,),
    )
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def update(transaction_id: int, amount: float, date: str,
           description: str | None, category_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE transactions
        SET amount = ?, transaction_date = ?, description = ?, category_id = ?
        WHERE transaction_id = ?
    """, (amount, date, description, category_id, transaction_id))
    conn.commit()
    conn.close()


def delete(transaction_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
    conn.commit()
    conn.close()


def get_totals_by_type() -> dict[str, float]:
    """Сумма по типам: {'Доход': ..., 'Расход': ...}."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.type, COALESCE(SUM(t.amount), 0)
        FROM transactions t
        JOIN categories c ON c.category_id = t.category_id
        GROUP BY c.type
    """)
    rows = cur.fetchall()
    conn.close()
    result = {"Доход": 0.0, "Расход": 0.0}
    result.update({t: s for t, s in rows})
    return result


def get_totals_by_category() -> list[tuple[str, str, float]]:
    """Список (тип, категория, сумма)."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.type, c.name, SUM(t.amount)
        FROM transactions t
        JOIN categories c ON c.category_id = t.category_id
        GROUP BY c.category_id
        ORDER BY c.type, SUM(t.amount) DESC
    """)
    rows = cur.fetchall()
    conn.close()
    return rows
