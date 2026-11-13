from database.database import get_connection
from models.user import User

_COLUMNS = "user_id, login, password_hash, username, email, role, created_at"


def _map(row) -> User:
    return User(*row)


def create(login: str, password_hash: str, username: str,
           email: str | None, role: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO users(login, password_hash, username, email, role)
        VALUES (?, ?, ?, ?, ?)
    """, (login, password_hash, username, email, role))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_by_id(user_id: int) -> User | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLUMNS} FROM users WHERE user_id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return _map(row) if row else None


def get_by_login(login: str) -> User | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLUMNS} FROM users WHERE login = ?", (login,))
    row = cur.fetchone()
    conn.close()
    return _map(row) if row else None


def get_all() -> list[User]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"SELECT {_COLUMNS} FROM users ORDER BY user_id")
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def update(user_id: int, username: str, email: str | None, role: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users SET username = ?, email = ?, role = ?
        WHERE user_id = ?
    """, (username, email, role, user_id))
    conn.commit()
    conn.close()


def delete(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def has_related_data(user_id: int) -> bool:
    """Есть ли у пользователя счета, транзакции или регулярные платежи."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT (SELECT COUNT(*) FROM accounts WHERE user_id = ?)
             + (SELECT COUNT(*) FROM transactions WHERE user_id = ?)
             + (SELECT COUNT(*) FROM regular_payments WHERE user_id = ?)
    """, (user_id, user_id, user_id))
    count = cur.fetchone()[0]
    conn.close()
    return count > 0
