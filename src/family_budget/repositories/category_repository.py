from database.database import get_connection
from models.category import Category


def _map(row) -> Category:
    return Category(*row)


def create(name: str, type_: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO categories(name, type) VALUES (?, ?)", (name, type_))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def get_by_id(category_id: int) -> Category | None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT category_id, name, type FROM categories WHERE category_id = ?",
        (category_id,),
    )
    row = cur.fetchone()
    conn.close()
    return _map(row) if row else None


def get_all() -> list[Category]:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT category_id, name, type FROM categories ORDER BY type, name")
    rows = cur.fetchall()
    conn.close()
    return [_map(r) for r in rows]


def update(category_id: int, name: str, type_: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE categories SET name = ?, type = ? WHERE category_id = ?",
        (name, type_, category_id),
    )
    conn.commit()
    conn.close()


def delete(category_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM categories WHERE category_id = ?", (category_id,))
    conn.commit()
    conn.close()


def count_transactions(category_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions WHERE category_id = ?", (category_id,))
    count = cur.fetchone()[0]
    conn.close()
    return count
