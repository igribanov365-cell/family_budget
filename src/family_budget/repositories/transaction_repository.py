from database.database import get_connection
from models.transaction import Transaction

_SELECT = """
    SELECT t.transaction_id, t.user_id, t.account_id, t.category_id, t.amount,
           t.transaction_date, t.payment_method, t.description,
           u.username, a.name, c.name, c.type
    FROM transactions t
    JOIN users u ON u.user_id = t.user_id
    JOIN accounts a ON a.account_id = t.account_id
    JOIN categories c ON c.category_id = t.category_id
"""
_ORDER = " ORDER BY t.transaction_date DESC, t.transaction_id DESC"


def _map(row) -> Transaction:
    return Transaction(*row)


def create(user_id: int, account_id: int, category_id: int, amount: float,
           date: str, payment_method: str, description: str | None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transactions(user_id, account_id, category_id, amount,
                                 transaction_date, payment_method, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, account_id, category_id, amount, date, payment_method, description))
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
    cur.execute(_SELECT + _ORDER)
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def get_by_user(user_id: int) -> list[Transaction]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " WHERE t.user_id = ?" + _ORDER, (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def update(transaction_id: int, category_id: int, amount: float, date: str,
           payment_method: str, description: str | None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE transactions
        SET category_id = ?, amount = ?, transaction_date = ?,
            payment_method = ?, description = ?
        WHERE transaction_id = ?
    """, (category_id, amount, date, payment_method, description, transaction_id))
    conn.commit()
    conn.close()


def delete(transaction_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM transactions WHERE transaction_id = ?", (transaction_id,))
    conn.commit()
    conn.close()


def get_totals_by_type(user_id: int | None = None) -> dict[str, float]:
    """Суммы по типам: {'Доход': ..., 'Расход': ...}. user_id=None — вся семья."""
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT c.type, COALESCE(SUM(t.amount), 0)
        FROM transactions t
        JOIN categories c ON c.category_id = t.category_id
    """
    params: tuple = ()
    if user_id is not None:
        sql += " WHERE t.user_id = ?"
        params = (user_id,)
    cur.execute(sql + " GROUP BY c.type", params)
    rows = cur.fetchall()
    conn.close()
    result = {"Доход": 0.0, "Расход": 0.0}
    result.update({t: s for t, s in rows})
    return result


def get_totals_by_category(user_id: int | None = None) -> list[tuple[str, str, float]]:
    """Список (тип, категория, сумма). Подкатегории показываются как 'Родитель / Имя'."""
    conn = get_connection()
    cur = conn.cursor()
    sql = """
        SELECT c.type,
               CASE WHEN p.name IS NULL THEN c.name ELSE p.name || ' / ' || c.name END,
               SUM(t.amount)
        FROM transactions t
        JOIN categories c ON c.category_id = t.category_id
        LEFT JOIN categories p ON p.category_id = c.parent_id
    """
    params: tuple = ()
    if user_id is not None:
        sql += " WHERE t.user_id = ?"
        params = (user_id,)
    cur.execute(sql + " GROUP BY c.category_id ORDER BY c.type, SUM(t.amount) DESC", params)
    rows = cur.fetchall()
    conn.close()
    return rows
