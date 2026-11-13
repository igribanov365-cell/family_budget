from database.database import get_connection
from models.user import User

_COLUMNS = "user_id, username, role, login, password_hash"


def _map(row) -> User:
    return User(*row)


def create(username: str, role: str, login: str, password_hash: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users(username, role, login, password_hash) VALUES (?, ?, ?, ?)",
        (username, role, login, password_hash),
    )
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


def update(user_id: int, username: str, role: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE users SET username = ?, role = ? WHERE user_id = ?",
        (username, role, user_id),
    )
    conn.commit()
    conn.close()


def delete(user_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()


def count_transactions(user_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions WHERE user_id = ?", (user_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count
