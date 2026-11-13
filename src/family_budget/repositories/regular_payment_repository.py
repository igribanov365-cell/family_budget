from database.database import get_connection
from models.regular_payment import RegularPayment

_SELECT = """
    SELECT r.payment_id, r.user_id, r.category_id, r.amount, r.frequency,
           r.next_date, u.username, c.name, c.type
    FROM regular_payments r
    JOIN users u ON u.user_id = r.user_id
    JOIN categories c ON c.category_id = r.category_id
"""


def _map(row) -> RegularPayment:
    return RegularPayment(*row)


def create(user_id: int, category_id: int, amount: float,
           frequency: str, next_date: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO regular_payments(user_id, category_id, amount, frequency, next_date)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, category_id, amount, frequency, next_date))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_by_id(payment_id: int) -> RegularPayment | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " WHERE r.payment_id = ?", (payment_id,))
    row = cur.fetchone()
    conn.close()
    return _map(row) if row else None


def get_all() -> list[RegularPayment]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " ORDER BY r.next_date, r.payment_id")
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def get_by_user(user_id: int) -> list[RegularPayment]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(_SELECT + " WHERE r.user_id = ? ORDER BY r.next_date, r.payment_id", (user_id,))
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def update(payment_id: int, category_id: int, amount: float,
           frequency: str, next_date: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE regular_payments
        SET category_id = ?, amount = ?, frequency = ?, next_date = ?
        WHERE payment_id = ?
    """, (category_id, amount, frequency, next_date, payment_id))
    conn.commit()
    conn.close()


def set_next_date(payment_id: int, next_date: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE regular_payments SET next_date = ? WHERE payment_id = ?",
        (next_date, payment_id),
    )
    conn.commit()
    conn.close()


def delete(payment_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM regular_payments WHERE payment_id = ?", (payment_id,))
    conn.commit()
    conn.close()
